"""
File Upload Handler - Supabase Storage, Vision API, Document Parsing
Handles all file uploads for Sarah to analyze
"""

import os
import logging
import base64
from pathlib import Path
from typing import Dict, Optional
import mimetypes

logger = logging.getLogger(__name__)

# Supabase Storage
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("⚠️ Supabase not installed - files will be stored locally")

# Document parsing
try:
    from pypdf import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Claude Vision (using same Anthropic client)
from anthropic import Anthropic


class FileHandler:
    """Handles file uploads, storage, and analysis"""

    def __init__(self):
        """Initialize file handler with Supabase and Anthropic"""

        # Supabase setup
        self.supabase: Optional[Client] = None
        self.bucket_name = "bloom-files"

        if SUPABASE_AVAILABLE:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

            if supabase_url and supabase_key:
                try:
                    self.supabase = create_client(supabase_url, supabase_key)
                    logger.info("✅ Supabase Storage initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize Supabase: {e}")
            else:
                logger.warning("⚠️ SUPABASE_URL or SUPABASE_SERVICE_KEY not set")

        # Anthropic for Vision API
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.anthropic = Anthropic(api_key=anthropic_key) if anthropic_key else None

        # Local storage fallback
        self.local_upload_dir = Path("uploads")
        self.local_upload_dir.mkdir(exist_ok=True)

    async def upload_file(self, file_path: Path, filename: str, content_type: str, conversation_id: str) -> Dict:
        """
        Upload file to Supabase Storage (or local fallback)

        Returns:
            Dict with file URL, metadata, and analysis
        """
        try:
            # Determine file category
            file_category = self._get_file_category(content_type)

            # Upload to Supabase or save locally
            if self.supabase:
                file_url = await self._upload_to_supabase(file_path, filename, content_type, conversation_id)
            else:
                file_url = f"/uploads/{filename}"  # Local fallback
                logger.info(f"📁 Stored locally: {filename}")

            # Analyze the file based on type
            analysis = await self._analyze_file(file_path, content_type, filename)

            return {
                "success": True,
                "url": file_url,
                "filename": filename,
                "content_type": content_type,
                "category": file_category,
                "size": file_path.stat().st_size,
                "analysis": analysis,
                "conversation_id": conversation_id
            }

        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _upload_to_supabase(self, file_path: Path, filename: str, content_type: str, conversation_id: str) -> str:
        """Upload file to Supabase Storage"""
        try:
            # Generate storage path: conversation_id/filename
            storage_path = f"{conversation_id}/{filename}"

            # Read file data
            with open(file_path, "rb") as f:
                file_data = f.read()

            # Upload to Supabase
            response = self.supabase.storage.from_(self.bucket_name).upload(
                storage_path,
                file_data,
                {"content-type": content_type}
            )

            # Get public URL
            url_response = self.supabase.storage.from_(self.bucket_name).get_public_url(storage_path)

            logger.info(f"☁️ Uploaded to Supabase: {storage_path}")
            return url_response

        except Exception as e:
            logger.error(f"Supabase upload failed: {e}")
            # Fallback to local
            return f"/uploads/{filename}"

    async def _analyze_file(self, file_path: Path, content_type: str, filename: str) -> Dict:
        """Analyze file content based on type"""

        # Images - use Claude Vision
        if content_type.startswith("image/"):
            return await self._analyze_image(file_path, content_type)

        # PDFs - extract text
        elif content_type == "application/pdf":
            return await self._parse_pdf(file_path)

        # Word docs - extract text
        elif content_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            return await self._parse_docx(file_path)

        # Text files
        elif content_type.startswith("text/"):
            return await self._read_text_file(file_path)

        # Videos - not analyzed yet
        elif content_type.startswith("video/"):
            return {
                "type": "video",
                "description": f"Video file: {filename}",
                "note": "Video analysis coming soon!"
            }

        else:
            return {
                "type": "unknown",
                "description": f"File: {filename}"
            }

    async def _analyze_image(self, file_path: Path, content_type: str) -> Dict:
        """Analyze image using Claude Vision API"""
        if not self.anthropic:
            return {"type": "image", "description": "Image uploaded (analysis unavailable)"}

        try:
            # Read and encode image
            with open(file_path, "rb") as f:
                image_data = base64.standard_b64encode(f.read()).decode("utf-8")

            # Determine media type
            media_type_map = {
                "image/jpeg": "image/jpeg",
                "image/jpg": "image/jpeg",
                "image/png": "image/png",
                "image/gif": "image/gif",
                "image/webp": "image/webp"
            }
            media_type = media_type_map.get(content_type, "image/jpeg")

            # Call Claude Vision API
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=512,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data
                            }
                        },
                        {
                            "type": "text",
                            "text": "Describe this image in detail. What do you see? What's the context?"
                        }
                    ]
                }]
            )

            description = response.content[0].text
            logger.info(f"🖼️ Image analyzed: {description[:100]}...")

            return {
                "type": "image",
                "description": description,
                "analyzed": True
            }

        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return {
                "type": "image",
                "description": "Image uploaded (analysis failed)",
                "error": str(e)
            }

    async def _parse_pdf(self, file_path: Path) -> Dict:
        """Extract text from PDF"""
        if not PDF_AVAILABLE:
            return {"type": "pdf", "description": "PDF uploaded (parsing unavailable)"}

        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            # Truncate if too long
            if len(text) > 5000:
                text = text[:5000] + "...(truncated)"

            logger.info(f"📄 PDF parsed: {len(text)} characters")

            return {
                "type": "pdf",
                "description": f"PDF document with {len(reader.pages)} pages",
                "text": text,
                "pages": len(reader.pages),
                "analyzed": True
            }

        except Exception as e:
            logger.error(f"PDF parsing failed: {e}")
            return {
                "type": "pdf",
                "description": "PDF uploaded (parsing failed)",
                "error": str(e)
            }

    async def _parse_docx(self, file_path: Path) -> Dict:
        """Extract text from Word document"""
        if not DOCX_AVAILABLE:
            return {"type": "docx", "description": "Word document uploaded (parsing unavailable)"}

        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])

            # Truncate if too long
            if len(text) > 5000:
                text = text[:5000] + "...(truncated)"

            logger.info(f"📝 Word doc parsed: {len(text)} characters")

            return {
                "type": "docx",
                "description": f"Word document with {len(doc.paragraphs)} paragraphs",
                "text": text,
                "paragraphs": len(doc.paragraphs),
                "analyzed": True
            }

        except Exception as e:
            logger.error(f"Word doc parsing failed: {e}")
            return {
                "type": "docx",
                "description": "Word document uploaded (parsing failed)",
                "error": str(e)
            }

    async def _read_text_file(self, file_path: Path) -> Dict:
        """Read plain text file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            # Truncate if too long
            if len(text) > 5000:
                text = text[:5000] + "...(truncated)"

            return {
                "type": "text",
                "description": "Text file",
                "text": text,
                "analyzed": True
            }

        except Exception as e:
            logger.error(f"Text file read failed: {e}")
            return {
                "type": "text",
                "description": "Text file (read failed)",
                "error": str(e)
            }

    def _get_file_category(self, content_type: str) -> str:
        """Categorize file by MIME type"""
        if content_type.startswith("image/"):
            return "image"
        elif content_type.startswith("video/"):
            return "video"
        elif content_type == "application/pdf":
            return "pdf"
        elif "word" in content_type or "document" in content_type:
            return "document"
        elif content_type.startswith("text/"):
            return "text"
        else:
            return "other"
