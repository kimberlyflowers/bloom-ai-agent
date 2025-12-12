"""
Persona Management Capabilities (6 total)

Multi-persona system for managing AI influencers:
1. persona_database_query - Query persona data
2. load_persona_assets - Load reference images, voice, content library
3. validate_persona_completeness - Check if persona has all required assets
4. get_persona_reference_images - Get 3-5 reference photos for character generation
5. get_persona_voice_id - Get ElevenLabs voice ID
6. update_persona_content_library - Add new videos to persona's library
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from ..foundation.core_utilities import get_database_manager, get_storage_manager

logger = logging.getLogger(__name__)


# ============================================================================
# DATABASE SCHEMA
# ============================================================================

PERSONAS_SCHEMA = """
CREATE TABLE IF NOT EXISTS personas (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    full_name TEXT,
    age INTEGER,
    ethnicity TEXT,
    personality TEXT,
    voice_id TEXT,
    voice_provider TEXT DEFAULT 'elevenlabs',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS persona_reference_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    persona_id TEXT NOT NULL,
    image_path TEXT NOT NULL,
    image_type TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persona_id) REFERENCES personas(id)
);

CREATE TABLE IF NOT EXISTS persona_content_library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    persona_id TEXT NOT NULL,
    video_url TEXT,
    video_path TEXT,
    title TEXT,
    description TEXT,
    platform TEXT,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persona_id) REFERENCES personas(id)
);

CREATE TABLE IF NOT EXISTS persona_social_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    persona_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    username TEXT,
    account_id TEXT,
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persona_id) REFERENCES personas(id)
);
"""


async def initialize_persona_database():
    """Initialize persona database tables"""
    db = get_database_manager()

    for statement in PERSONAS_SCHEMA.split(';'):
        if statement.strip():
            await db.database_query(statement.strip())

    logger.info("✅ Persona database initialized")


# ============================================================================
# 1. PERSONA_DATABASE_QUERY
# ============================================================================

async def persona_database_query(
    persona_id: str = None,
    include_images: bool = True,
    include_social: bool = True,
    include_stats: bool = True
) -> Dict[str, Any]:
    """
    Query persona data from database

    Args:
        persona_id: Persona identifier (e.g., "sarah_001"). If None, returns all personas
        include_images: Include reference images
        include_social: Include social account data
        include_stats: Include content performance stats

    Returns:
        Complete persona data
    """
    try:
        db = get_database_manager()

        if persona_id:
            # Get specific persona
            query = "SELECT * FROM personas WHERE id = ?"
            persona = await db.database_query(query, (persona_id,), fetch_one=True)

            if not persona:
                return {"success": False, "error": f"Persona {persona_id} not found"}

        else:
            # Get all active personas
            query = "SELECT * FROM personas WHERE is_active = 1"
            personas = await db.database_query(query)
            return {"success": True, "personas": personas}

        # Enrich with additional data
        if include_images:
            query = "SELECT * FROM persona_reference_images WHERE persona_id = ?"
            images = await db.database_query(query, (persona_id,))
            persona["reference_images"] = images

        if include_social:
            query = "SELECT platform, username, account_id FROM persona_social_accounts WHERE persona_id = ?"
            social = await db.database_query(query, (persona_id,))
            persona["social_accounts"] = social

        if include_stats:
            query = """
                SELECT
                    COUNT(*) as total_videos,
                    SUM(views) as total_views,
                    SUM(likes) as total_likes,
                    SUM(comments) as total_comments
                FROM persona_content_library
                WHERE persona_id = ?
            """
            stats = await db.database_query(query, (persona_id,), fetch_one=True)
            persona["stats"] = stats

        logger.info(f"✅ Persona queried: {persona_id}")
        return {"success": True, "persona": persona}

    except Exception as e:
        logger.error(f"❌ Persona query failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 2. LOAD_PERSONA_ASSETS
# ============================================================================

async def load_persona_assets(
    persona_id: str
) -> Dict[str, Any]:
    """
    Load all persona assets (images, voice, brand info)

    Args:
        persona_id: Persona identifier

    Returns:
        {
            "reference_images": ["path1.jpg", "path2.jpg", ...],
            "voice_id": "elevenlabs_voice_id",
            "personality": "Warm, authentic, tech-savvy...",
            "brand_colors": ["#FF5733", "#33FF57"],
            "ready": true/false
        }
    """
    try:
        # Get persona data
        result = await persona_database_query(
            persona_id=persona_id,
            include_images=True,
            include_social=False,
            include_stats=False
        )

        if not result["success"]:
            return result

        persona = result["persona"]

        # Extract image paths
        reference_images = [
            img["image_path"]
            for img in persona.get("reference_images", [])
        ]

        # Check if all assets are ready
        ready = (
            len(reference_images) >= 3 and
            persona.get("voice_id") is not None
        )

        assets = {
            "success": True,
            "persona_id": persona_id,
            "name": persona["name"],
            "reference_images": reference_images,
            "voice_id": persona.get("voice_id"),
            "voice_provider": persona.get("voice_provider", "elevenlabs"),
            "personality": persona.get("personality"),
            "age": persona.get("age"),
            "ethnicity": persona.get("ethnicity"),
            "ready": ready
        }

        logger.info(f"✅ Persona assets loaded: {persona_id} (ready={ready})")
        return assets

    except Exception as e:
        logger.error(f"❌ Load persona assets failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 3. VALIDATE_PERSONA_COMPLETENESS
# ============================================================================

async def validate_persona_completeness(
    persona_id: str
) -> Dict[str, Any]:
    """
    Validate that persona has all required assets

    Args:
        persona_id: Persona identifier

    Returns:
        {
            "valid": true/false,
            "missing": ["voice_id", "reference_images"],
            "warnings": ["Only 2 reference images, need 3+"]
        }
    """
    try:
        assets = await load_persona_assets(persona_id)

        if not assets["success"]:
            return assets

        missing = []
        warnings = []

        # Check voice
        if not assets.get("voice_id"):
            missing.append("voice_id")

        # Check reference images
        image_count = len(assets.get("reference_images", []))
        if image_count == 0:
            missing.append("reference_images")
        elif image_count < 3:
            warnings.append(f"Only {image_count} reference images, recommended 3+")

        # Check personality
        if not assets.get("personality"):
            warnings.append("No personality description")

        valid = len(missing) == 0

        result = {
            "success": True,
            "persona_id": persona_id,
            "valid": valid,
            "missing": missing,
            "warnings": warnings,
            "completeness_score": (5 - len(missing) - len(warnings)) / 5.0
        }

        logger.info(f"✅ Persona validated: {persona_id} (valid={valid})")
        return result

    except Exception as e:
        logger.error(f"❌ Persona validation failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 4. GET_PERSONA_REFERENCE_IMAGES
# ============================================================================

async def get_persona_reference_images(
    persona_id: str,
    load_image_data: bool = False
) -> Dict[str, Any]:
    """
    Get persona's reference images for character generation

    Args:
        persona_id: Persona identifier
        load_image_data: Load actual image bytes (vs just paths)

    Returns:
        {
            "images": [
                {"path": "...", "type": "portrait", "data": bytes},
                {"path": "...", "type": "full_body", "data": bytes},
                ...
            ]
        }
    """
    try:
        db = get_database_manager()
        storage = get_storage_manager()

        # Query reference images
        query = "SELECT * FROM persona_reference_images WHERE persona_id = ? ORDER BY created_at"
        images_data = await db.database_query(query, (persona_id,))

        if not images_data:
            return {
                "success": False,
                "error": f"No reference images for persona {persona_id}"
            }

        images = []
        for img in images_data:
            image_info = {
                "path": img["image_path"],
                "type": img.get("image_type", "portrait"),
                "description": img.get("description")
            }

            # Load image bytes if requested
            if load_image_data:
                result = await storage.storage_management("load", img["image_path"])
                if result["success"]:
                    image_info["data"] = result["data"]

            images.append(image_info)

        logger.info(f"✅ Reference images retrieved: {persona_id} ({len(images)} images)")
        return {
            "success": True,
            "persona_id": persona_id,
            "images": images,
            "count": len(images)
        }

    except Exception as e:
        logger.error(f"❌ Get reference images failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 5. GET_PERSONA_VOICE_ID
# ============================================================================

async def get_persona_voice_id(
    persona_id: str
) -> Dict[str, Any]:
    """
    Get persona's voice ID for TTS generation

    Args:
        persona_id: Persona identifier

    Returns:
        {
            "voice_id": "elevenlabs_voice_id",
            "voice_provider": "elevenlabs",
            "voice_name": "Sarah's Voice"
        }
    """
    try:
        db = get_database_manager()

        query = "SELECT voice_id, voice_provider, name FROM personas WHERE id = ?"
        persona = await db.database_query(query, (persona_id,), fetch_one=True)

        if not persona:
            return {"success": False, "error": f"Persona {persona_id} not found"}

        if not persona.get("voice_id"):
            return {
                "success": False,
                "error": f"No voice ID configured for persona {persona_id}"
            }

        logger.info(f"✅ Voice ID retrieved: {persona_id}")
        return {
            "success": True,
            "persona_id": persona_id,
            "voice_id": persona["voice_id"],
            "voice_provider": persona.get("voice_provider", "elevenlabs"),
            "voice_name": f"{persona['name']}'s Voice"
        }

    except Exception as e:
        logger.error(f"❌ Get voice ID failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 6. UPDATE_PERSONA_CONTENT_LIBRARY
# ============================================================================

async def update_persona_content_library(
    persona_id: str,
    video_url: str = None,
    video_path: str = None,
    title: str = None,
    description: str = None,
    platform: str = None,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Add new video to persona's content library

    Args:
        persona_id: Persona identifier
        video_url: Public video URL (YouTube, TikTok, etc.)
        video_path: Local storage path
        title: Video title
        description: Video description
        platform: "tiktok", "youtube", "instagram"
        metadata: Additional metadata (views, likes, etc.)

    Returns:
        {"success": bool, "video_id": int}
    """
    try:
        db = get_database_manager()

        # Build insert query
        query = """
            INSERT INTO persona_content_library
            (persona_id, video_url, video_path, title, description, platform, views, likes, comments)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        views = metadata.get("views", 0) if metadata else 0
        likes = metadata.get("likes", 0) if metadata else 0
        comments = metadata.get("comments", 0) if metadata else 0

        result = await db.database_query(
            query,
            (persona_id, video_url, video_path, title, description, platform, views, likes, comments)
        )

        video_id = result["last_id"]

        logger.info(f"✅ Content library updated: {persona_id} (video_id={video_id})")
        return {
            "success": True,
            "persona_id": persona_id,
            "video_id": video_id,
            "video_url": video_url
        }

    except Exception as e:
        logger.error(f"❌ Update content library failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# HELPER: CREATE PERSONA
# ============================================================================

async def create_persona(
    persona_id: str,
    name: str,
    full_name: str = None,
    age: int = None,
    ethnicity: str = None,
    personality: str = None,
    voice_id: str = None,
    reference_images: List[str] = None
) -> Dict[str, Any]:
    """
    Helper: Create new persona in database

    Args:
        persona_id: Unique persona ID (e.g., "sarah_001")
        name: Display name
        full_name: Full name
        age: Age
        ethnicity: Ethnicity description
        personality: Personality traits
        voice_id: ElevenLabs voice ID
        reference_images: List of image paths

    Returns:
        {"success": bool, "persona_id": str}
    """
    try:
        db = get_database_manager()

        # Insert persona
        query = """
            INSERT INTO personas
            (id, name, full_name, age, ethnicity, personality, voice_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        await db.database_query(query, (persona_id, name, full_name, age, ethnicity, personality, voice_id))

        # Add reference images
        if reference_images:
            for img_path in reference_images:
                query = """
                    INSERT INTO persona_reference_images
                    (persona_id, image_path, image_type)
                    VALUES (?, ?, 'portrait')
                """
                await db.database_query(query, (persona_id, img_path))

        logger.info(f"✅ Persona created: {persona_id}")
        return {"success": True, "persona_id": persona_id}

    except Exception as e:
        logger.error(f"❌ Create persona failed: {e}")
        return {"success": False, "error": str(e)}
