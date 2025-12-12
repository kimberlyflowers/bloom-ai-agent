"""
Foundation Capabilities (11 total)

Core utilities that all other capabilities depend on:
1. database_query - SQLite operations
2. http_request - Generic HTTP client
3. file_upload_multipart - Upload files to APIs
4. file_download - Download assets
5. oauth_authentication - OAuth 2.0 flow
6. subprocess_execute - Run system commands
7. webhook_handler - Process webhooks
8. batch_processing - Process tasks in parallel
9. queue_management - Task queue system
10. storage_management - File storage (S3/local)
11. metadata_extraction - Extract metadata from media files
"""

import asyncio
import aiohttp
import sqlite3
import subprocess
import json
import os
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from urllib.parse import urlencode
import mimetypes

logger = logging.getLogger(__name__)


# ============================================================================
# 1. DATABASE_QUERY
# ============================================================================

class DatabaseManager:
    """SQLite database operations"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '../../data/sarah.db')

        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    async def database_query(
        self,
        query: str,
        params: tuple = None,
        fetch_one: bool = False
    ) -> Any:
        """
        Execute SQL query on SQLite database

        Args:
            query: SQL query string
            params: Query parameters (prevents SQL injection)
            fetch_one: Return single row vs all rows

        Returns:
            Query results (list of dicts or single dict)
        """
        try:
            def _execute():
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                if query.strip().upper().startswith('SELECT'):
                    if fetch_one:
                        result = cursor.fetchone()
                        return dict(result) if result else None
                    else:
                        results = cursor.fetchall()
                        return [dict(row) for row in results]
                else:
                    conn.commit()
                    return {"affected_rows": cursor.rowcount, "last_id": cursor.lastrowid}

                conn.close()

            result = await asyncio.to_thread(_execute)
            logger.info(f"✅ Database query executed: {query[:50]}...")
            return result

        except Exception as e:
            logger.error(f"❌ Database query failed: {e}")
            raise


# ============================================================================
# 2. HTTP_REQUEST
# ============================================================================

async def http_request(
    method: str,
    url: str,
    headers: Dict[str, str] = None,
    json_data: Dict = None,
    data: Any = None,
    params: Dict = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Generic HTTP client for API calls

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        url: Target URL
        headers: Request headers
        json_data: JSON body
        data: Form data or raw body
        params: Query parameters
        timeout: Request timeout in seconds

    Returns:
        {
            "status": 200,
            "headers": {...},
            "body": {...},
            "success": true
        }
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                data=data,
                params=params,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:

                # Try to parse JSON, fall back to text
                try:
                    body = await response.json()
                except:
                    body = await response.text()

                result = {
                    "status": response.status,
                    "headers": dict(response.headers),
                    "body": body,
                    "success": 200 <= response.status < 300
                }

                logger.info(f"✅ HTTP {method} {url}: {response.status}")
                return result

    except Exception as e:
        logger.error(f"❌ HTTP request failed: {e}")
        return {
            "status": 0,
            "headers": {},
            "body": str(e),
            "success": False
        }


# ============================================================================
# 3. FILE_UPLOAD_MULTIPART
# ============================================================================

async def file_upload_multipart(
    url: str,
    file_path: str,
    field_name: str = "file",
    additional_fields: Dict[str, str] = None,
    headers: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    Upload file using multipart/form-data

    Args:
        url: Upload endpoint URL
        file_path: Path to file to upload
        field_name: Form field name for file
        additional_fields: Extra form fields
        headers: Request headers

    Returns:
        API response
    """
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()

        form_data = aiohttp.FormData()

        # Add file
        filename = os.path.basename(file_path)
        content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        form_data.add_field(field_name, file_data, filename=filename, content_type=content_type)

        # Add additional fields
        if additional_fields:
            for key, value in additional_fields.items():
                form_data.add_field(key, value)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=form_data, headers=headers) as response:
                try:
                    body = await response.json()
                except:
                    body = await response.text()

                logger.info(f"✅ File uploaded: {filename} to {url}")
                return {
                    "status": response.status,
                    "body": body,
                    "success": 200 <= response.status < 300
                }

    except Exception as e:
        logger.error(f"❌ File upload failed: {e}")
        return {"status": 0, "body": str(e), "success": False}


# ============================================================================
# 4. FILE_DOWNLOAD
# ============================================================================

async def file_download(
    url: str,
    save_path: str,
    headers: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    Download file from URL

    Args:
        url: File URL
        save_path: Where to save file
        headers: Request headers

    Returns:
        {"success": bool, "file_path": str, "size_bytes": int}
    """
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Download failed: HTTP {response.status}")

                with open(save_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)

        size = os.path.getsize(save_path)
        logger.info(f"✅ File downloaded: {save_path} ({size} bytes)")

        return {
            "success": True,
            "file_path": save_path,
            "size_bytes": size
        }

    except Exception as e:
        logger.error(f"❌ File download failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 5. OAUTH_AUTHENTICATION
# ============================================================================

async def oauth_authentication(
    auth_url: str,
    token_url: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    scope: str,
    code: str = None
) -> Dict[str, Any]:
    """
    OAuth 2.0 authentication flow

    Args:
        auth_url: Authorization URL
        token_url: Token exchange URL
        client_id: OAuth client ID
        client_secret: OAuth client secret
        redirect_uri: Callback URL
        scope: Requested scopes
        code: Authorization code (if exchanging)

    Returns:
        {"access_token": str, "refresh_token": str, "expires_in": int}
    """
    try:
        if not code:
            # Step 1: Generate authorization URL
            params = {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "scope": scope,
                "response_type": "code"
            }
            auth_link = f"{auth_url}?{urlencode(params)}"

            logger.info(f"🔗 OAuth authorization URL generated")
            return {
                "step": "authorize",
                "auth_url": auth_link,
                "message": "User must visit this URL and authorize"
            }
        else:
            # Step 2: Exchange code for tokens
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": client_id,
                "client_secret": client_secret
            }

            result = await http_request("POST", token_url, data=data)

            if result["success"]:
                logger.info(f"✅ OAuth tokens obtained")
                return result["body"]
            else:
                raise Exception(f"Token exchange failed: {result['body']}")

    except Exception as e:
        logger.error(f"❌ OAuth authentication failed: {e}")
        return {"error": str(e)}


# ============================================================================
# 6. SUBPROCESS_EXECUTE
# ============================================================================

async def subprocess_execute(
    command: str,
    shell: bool = True,
    timeout: int = 300,
    cwd: str = None
) -> Dict[str, Any]:
    """
    Execute system command (e.g., ffmpeg, whisper)

    Args:
        command: Command to execute
        shell: Run in shell
        timeout: Command timeout in seconds
        cwd: Working directory

    Returns:
        {"returncode": int, "stdout": str, "stderr": str, "success": bool}
    """
    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )

        stdout, stderr = await asyncio.wait_for(
            proc.communicate(),
            timeout=timeout
        )

        result = {
            "returncode": proc.returncode,
            "stdout": stdout.decode('utf-8', errors='replace'),
            "stderr": stderr.decode('utf-8', errors='replace'),
            "success": proc.returncode == 0
        }

        if result["success"]:
            logger.info(f"✅ Subprocess executed: {command[:50]}...")
        else:
            logger.warning(f"⚠️ Subprocess failed: {command[:50]}...")

        return result

    except asyncio.TimeoutError:
        logger.error(f"❌ Subprocess timeout: {command[:50]}...")
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": "Command timed out",
            "success": False
        }
    except Exception as e:
        logger.error(f"❌ Subprocess error: {e}")
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "success": False
        }


# ============================================================================
# 7. WEBHOOK_HANDLER
# ============================================================================

class WebhookManager:
    """Handle incoming webhooks"""

    def __init__(self):
        self.handlers = {}

    def register_handler(self, webhook_type: str, handler_func):
        """Register a webhook handler function"""
        self.handlers[webhook_type] = handler_func
        logger.info(f"✅ Webhook handler registered: {webhook_type}")

    async def webhook_handler(
        self,
        webhook_type: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process incoming webhook

        Args:
            webhook_type: Type of webhook (e.g., "tiktok_comment", "youtube_upload")
            payload: Webhook payload

        Returns:
            Handler response
        """
        try:
            if webhook_type not in self.handlers:
                logger.warning(f"⚠️ No handler for webhook type: {webhook_type}")
                return {"success": False, "error": "No handler registered"}

            handler = self.handlers[webhook_type]
            result = await handler(payload)

            logger.info(f"✅ Webhook processed: {webhook_type}")
            return {"success": True, "result": result}

        except Exception as e:
            logger.error(f"❌ Webhook handler error: {e}")
            return {"success": False, "error": str(e)}


# ============================================================================
# 8. BATCH_PROCESSING
# ============================================================================

async def batch_processing(
    items: List[Any],
    process_func,
    batch_size: int = 10,
    max_concurrent: int = 5
) -> List[Dict[str, Any]]:
    """
    Process items in parallel batches

    Args:
        items: List of items to process
        process_func: Async function to apply to each item
        batch_size: Items per batch
        max_concurrent: Max concurrent batches

    Returns:
        List of results
    """
    try:
        results = []
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_with_semaphore(item):
            async with semaphore:
                return await process_func(item)

        # Process in batches
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[process_with_semaphore(item) for item in batch],
                return_exceptions=True
            )
            results.extend(batch_results)

            logger.info(f"✅ Batch processed: {i+1}-{i+len(batch)} of {len(items)}")

        return results

    except Exception as e:
        logger.error(f"❌ Batch processing error: {e}")
        return []


# ============================================================================
# 9. QUEUE_MANAGEMENT
# ============================================================================

class TaskQueue:
    """Simple task queue for async jobs"""

    def __init__(self):
        self.queue = asyncio.Queue()
        self.results = {}

    async def queue_management(
        self,
        operation: str,
        task_id: str = None,
        task_data: Any = None
    ) -> Dict[str, Any]:
        """
        Manage task queue

        Args:
            operation: "enqueue", "dequeue", "get_result", "size"
            task_id: Task identifier
            task_data: Task payload

        Returns:
            Operation result
        """
        try:
            if operation == "enqueue":
                await self.queue.put({"id": task_id, "data": task_data})
                logger.info(f"✅ Task enqueued: {task_id}")
                return {"success": True, "task_id": task_id}

            elif operation == "dequeue":
                if self.queue.empty():
                    return {"success": False, "message": "Queue is empty"}
                task = await self.queue.get()
                return {"success": True, "task": task}

            elif operation == "get_result":
                result = self.results.get(task_id)
                return {"success": result is not None, "result": result}

            elif operation == "size":
                return {"success": True, "size": self.queue.qsize()}

            else:
                return {"success": False, "error": "Unknown operation"}

        except Exception as e:
            logger.error(f"❌ Queue management error: {e}")
            return {"success": False, "error": str(e)}


# ============================================================================
# 10. STORAGE_MANAGEMENT
# ============================================================================

class StorageManager:
    """File storage management (local or S3)"""

    def __init__(self, storage_type: str = "local", base_path: str = None):
        self.storage_type = storage_type
        if base_path is None:
            base_path = os.path.join(os.path.dirname(__file__), '../../data/storage')
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    async def storage_management(
        self,
        operation: str,
        file_path: str = None,
        file_data: bytes = None,
        metadata: Dict = None
    ) -> Dict[str, Any]:
        """
        Manage file storage

        Args:
            operation: "save", "load", "delete", "list", "exists"
            file_path: Relative file path
            file_data: File bytes (for save)
            metadata: File metadata

        Returns:
            Operation result
        """
        try:
            full_path = os.path.join(self.base_path, file_path) if file_path else None

            if operation == "save":
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                if isinstance(file_data, bytes):
                    with open(full_path, 'wb') as f:
                        f.write(file_data)
                else:
                    with open(full_path, 'w') as f:
                        f.write(str(file_data))

                # Save metadata
                if metadata:
                    meta_path = full_path + ".meta.json"
                    with open(meta_path, 'w') as f:
                        json.dump(metadata, f)

                logger.info(f"✅ File saved: {file_path}")
                return {"success": True, "path": full_path}

            elif operation == "load":
                if not os.path.exists(full_path):
                    return {"success": False, "error": "File not found"}

                with open(full_path, 'rb') as f:
                    data = f.read()

                # Load metadata
                meta_path = full_path + ".meta.json"
                meta = None
                if os.path.exists(meta_path):
                    with open(meta_path, 'r') as f:
                        meta = json.load(f)

                return {"success": True, "data": data, "metadata": meta}

            elif operation == "delete":
                if os.path.exists(full_path):
                    os.remove(full_path)
                    # Delete metadata
                    meta_path = full_path + ".meta.json"
                    if os.path.exists(meta_path):
                        os.remove(meta_path)
                    logger.info(f"✅ File deleted: {file_path}")
                return {"success": True}

            elif operation == "exists":
                exists = os.path.exists(full_path)
                return {"success": True, "exists": exists}

            elif operation == "list":
                pattern = file_path or "*"
                files = list(Path(self.base_path).glob(pattern))
                file_list = [str(f.relative_to(self.base_path)) for f in files if f.is_file()]
                return {"success": True, "files": file_list}

            else:
                return {"success": False, "error": "Unknown operation"}

        except Exception as e:
            logger.error(f"❌ Storage management error: {e}")
            return {"success": False, "error": str(e)}


# ============================================================================
# 11. METADATA_EXTRACTION
# ============================================================================

async def metadata_extraction(
    file_path: str,
    media_type: str = "auto"
) -> Dict[str, Any]:
    """
    Extract metadata from media files

    Args:
        file_path: Path to media file
        media_type: "video", "audio", "image", or "auto"

    Returns:
        File metadata
    """
    try:
        # Auto-detect media type
        if media_type == "auto":
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.mp4', '.mov', '.avi', '.mkv']:
                media_type = "video"
            elif ext in ['.mp3', '.wav', '.m4a', '.flac']:
                media_type = "audio"
            elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                media_type = "image"

        # Basic metadata
        stat = os.stat(file_path)
        metadata = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "size_bytes": stat.st_size,
            "created_at": stat.st_ctime,
            "modified_at": stat.st_mtime,
            "media_type": media_type
        }

        # Use ffprobe for video/audio
        if media_type in ["video", "audio"]:
            command = f"ffprobe -v quiet -print_format json -show_format -show_streams '{file_path}'"
            result = await subprocess_execute(command)

            if result["success"]:
                ffprobe_data = json.loads(result["stdout"])
                metadata["format"] = ffprobe_data.get("format", {})
                metadata["streams"] = ffprobe_data.get("streams", [])

                if media_type == "video":
                    # Extract video-specific metadata
                    video_stream = next((s for s in metadata["streams"] if s["codec_type"] == "video"), None)
                    if video_stream:
                        metadata["width"] = video_stream.get("width")
                        metadata["height"] = video_stream.get("height")
                        metadata["duration"] = float(video_stream.get("duration", 0))
                        metadata["fps"] = eval(video_stream.get("r_frame_rate", "0/1"))

        logger.info(f"✅ Metadata extracted: {file_path}")
        return metadata

    except Exception as e:
        logger.error(f"❌ Metadata extraction error: {e}")
        return {"error": str(e)}


# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

# Singleton instances
_db_manager = None
_webhook_manager = None
_task_queue = None
_storage_manager = None


def get_database_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def get_webhook_manager() -> WebhookManager:
    """Get global webhook manager instance"""
    global _webhook_manager
    if _webhook_manager is None:
        _webhook_manager = WebhookManager()
    return _webhook_manager


def get_task_queue() -> TaskQueue:
    """Get global task queue instance"""
    global _task_queue
    if _task_queue is None:
        _task_queue = TaskQueue()
    return _task_queue


def get_storage_manager() -> StorageManager:
    """Get global storage manager instance"""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = StorageManager()
    return _storage_manager
