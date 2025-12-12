"""
Platform Publishing Capabilities (11 total)

Post videos to social platforms via APIs:
1. youtube_api_upload - Upload video to YouTube
2. youtube_set_metadata - Set title, description, tags
3. youtube_upload_thumbnail - Upload custom thumbnail
4. youtube_schedule_publish - Schedule video publication
5. tiktok_api_upload_video - Upload video to TikTok
6. tiktok_generate_ugc_caption - Generate TikTok-style caption
7. tiktok_select_trending_hashtags - Select trending hashtags
8. tiktok_get_persona_credentials - Get persona's TikTok credentials
9. instagram_api_upload_reel - Upload Reel to Instagram
10. instagram_set_caption - Set caption with hashtags
11. cross_platform_scheduler - Schedule posts across platforms
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from ..foundation.core_utilities import http_request, file_upload_multipart, oauth_authentication
from ..persona.persona_manager import persona_database_query

logger = logging.getLogger(__name__)


# ============================================================================
# 1-4. YOUTUBE APIs
# ============================================================================

async def youtube_api_upload(
    video_path: str,
    title: str,
    access_token: str,
    privacy_status: str = "private"
) -> Dict[str, Any]:
    """
    Upload video to YouTube

    Args:
        video_path: Path to video file
        title: Video title
        access_token: YouTube OAuth access token
        privacy_status: "private", "unlisted", or "public"

    Returns:
        {
            "success": true,
            "video_id": "dQw4w9WgXcQ",
            "video_url": "https://youtu.be/dQw4w9WgXcQ"
        }
    """
    try:
        api_endpoint = "https://www.googleapis.com/upload/youtube/v3/videos"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }

        params = {
            "part": "snippet,status",
            "uploadType": "multipart"
        }

        # Prepare metadata
        metadata = {
            "snippet": {
                "title": title,
                "categoryId": "22"  # People & Blogs
            },
            "status": {
                "privacyStatus": privacy_status
            }
        }

        # Upload video
        result = await file_upload_multipart(
            url=f"{api_endpoint}?{'&'.join([f'{k}={v}' for k,v in params.items()])}",
            file_path=video_path,
            field_name="media",
            additional_fields={"metadata": str(metadata)},
            headers=headers
        )

        if not result["success"]:
            raise Exception(f"YouTube upload failed: {result['body']}")

        video_id = result["body"].get("id")
        video_url = f"https://youtu.be/{video_id}"

        logger.info(f"✅ YouTube video uploaded: {video_url}")
        return {
            "success": True,
            "video_id": video_id,
            "video_url": video_url,
            "privacy_status": privacy_status
        }

    except Exception as e:
        logger.error(f"❌ YouTube upload failed: {e}")
        return {"success": False, "error": str(e)}


async def youtube_set_metadata(
    video_id: str,
    title: str = None,
    description: str = None,
    tags: List[str] = None,
    access_token: str = None
) -> Dict[str, Any]:
    """Set YouTube video metadata"""
    try:
        api_endpoint = f"https://www.googleapis.com/youtube/v3/videos?part=snippet"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        data = {
            "id": video_id,
            "snippet": {}
        }

        if title:
            data["snippet"]["title"] = title
        if description:
            data["snippet"]["description"] = description
        if tags:
            data["snippet"]["tags"] = tags

        result = await http_request("PUT", api_endpoint, headers=headers, json_data=data)

        logger.info(f"✅ YouTube metadata updated: {video_id}")
        return {"success": True, "video_id": video_id}

    except Exception as e:
        logger.error(f"❌ YouTube metadata update failed: {e}")
        return {"success": False, "error": str(e)}


async def youtube_upload_thumbnail(
    video_id: str,
    thumbnail_path: str,
    access_token: str
) -> Dict[str, Any]:
    """Upload custom thumbnail"""
    try:
        api_endpoint = f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={video_id}"

        headers = {"Authorization": f"Bearer {access_token}"}

        result = await file_upload_multipart(
            url=api_endpoint,
            file_path=thumbnail_path,
            field_name="media",
            headers=headers
        )

        logger.info(f"✅ YouTube thumbnail uploaded: {video_id}")
        return {"success": True, "video_id": video_id}

    except Exception as e:
        logger.error(f"❌ YouTube thumbnail upload failed: {e}")
        return {"success": False, "error": str(e)}


async def youtube_schedule_publish(
    video_id: str,
    publish_at: str,
    access_token: str
) -> Dict[str, Any]:
    """Schedule video publication"""
    try:
        # Update video status with publishAt timestamp
        api_endpoint = f"https://www.googleapis.com/youtube/v3/videos?part=status"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        data = {
            "id": video_id,
            "status": {
                "privacyStatus": "private",
                "publishAt": publish_at  # RFC 3339 format
            }
        }

        result = await http_request("PUT", api_endpoint, headers=headers, json_data=data)

        logger.info(f"✅ YouTube video scheduled: {video_id} at {publish_at}")
        return {"success": True, "video_id": video_id, "publish_at": publish_at}

    except Exception as e:
        logger.error(f"❌ YouTube scheduling failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 5-8. TIKTOK APIs
# ============================================================================

async def tiktok_api_upload_video(
    video_path: str,
    caption: str,
    access_token: str,
    privacy_level: str = "PUBLIC_TO_EVERYONE"
) -> Dict[str, Any]:
    """
    Upload video to TikTok

    Args:
        video_path: Path to video file
        caption: Video caption (with hashtags)
        access_token: TikTok access token
        privacy_level: "PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS", "SELF_ONLY"

    Returns:
        {
            "success": true,
            "share_id": "...",
            "video_url": "https://www.tiktok.com/@username/video/..."
        }
    """
    try:
        # TikTok Content Posting API
        api_endpoint = "https://open.tiktokapis.com/v2/post/publish/video/init/"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        data = {
            "post_info": {
                "title": caption,
                "privacy_level": privacy_level,
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
                "video_cover_timestamp_ms": 1000
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": os.path.getsize(video_path),
                "chunk_size": 10000000,
                "total_chunk_count": 1
            }
        }

        # Initialize upload
        result = await http_request("POST", api_endpoint, headers=headers, json_data=data)

        if not result["success"]:
            raise Exception(f"TikTok upload init failed: {result['body']}")

        publish_id = result["body"]["data"]["publish_id"]
        upload_url = result["body"]["data"]["upload_url"]

        # Upload video
        upload_result = await file_upload_multipart(
            url=upload_url,
            file_path=video_path,
            field_name="video"
        )

        if not upload_result["success"]:
            raise Exception("TikTok video upload failed")

        logger.info(f"✅ TikTok video uploaded: {publish_id}")
        return {
            "success": True,
            "publish_id": publish_id,
            "message": "Video uploaded successfully"
        }

    except Exception as e:
        logger.error(f"❌ TikTok upload failed: {e}")
        return {"success": False, "error": str(e)}


async def tiktok_generate_ugc_caption(
    video_topic: str,
    product_name: str = None,
    anthropic_api_key: str = None
) -> Dict[str, Any]:
    """Generate TikTok-style caption with hashtags"""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=anthropic_api_key)

        prompt = f"""Generate a viral TikTok caption for a video about: {video_topic}
{"Product: " + product_name if product_name else ""}

Requirements:
- UGC style (conversational, authentic)
- 2-3 sentences max
- Include call-to-action
- Add 5-7 trending hashtags
- Use emojis naturally

Return caption only, no explanations."""

        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-3-5-haiku-20241022",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        caption = response.content[0].text.strip()

        logger.info(f"✅ TikTok caption generated")
        return {"success": True, "caption": caption}

    except Exception as e:
        logger.error(f"❌ TikTok caption generation failed: {e}")
        return {"success": False, "error": str(e)}


async def tiktok_select_trending_hashtags(
    topic: str,
    count: int = 5
) -> Dict[str, Any]:
    """Select trending hashtags for TikTok"""
    # Placeholder - would integrate with TikTok trending API
    trending_hashtags = [
        "#fyp", "#foryou", "#viral", "#trending", f"#{topic.replace(' ', '')}"
    ]

    logger.info(f"✅ Trending hashtags selected")
    return {
        "success": True,
        "hashtags": trending_hashtags[:count]
    }


async def tiktok_get_persona_credentials(
    persona_id: str
) -> Dict[str, Any]:
    """Get persona's TikTok credentials from database"""
    try:
        result = await persona_database_query(persona_id, include_social=True)

        if not result["success"]:
            return result

        social_accounts = result["persona"].get("social_accounts", [])
        tiktok_account = next((acc for acc in social_accounts if acc["platform"] == "tiktok"), None)

        if not tiktok_account:
            return {"success": False, "error": "No TikTok account linked"}

        logger.info(f"✅ TikTok credentials retrieved for {persona_id}")
        return {
            "success": True,
            "access_token": tiktok_account.get("access_token"),
            "refresh_token": tiktok_account.get("refresh_token"),
            "username": tiktok_account.get("username")
        }

    except Exception as e:
        logger.error(f"❌ TikTok credential retrieval failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 9-10. INSTAGRAM APIs
# ============================================================================

async def instagram_api_upload_reel(
    video_path: str,
    caption: str,
    access_token: str,
    instagram_account_id: str
) -> Dict[str, Any]:
    """Upload Reel to Instagram"""
    try:
        # Instagram Graph API - Create media container
        api_endpoint = f"https://graph.facebook.com/v18.0/{instagram_account_id}/media"

        data = {
            "media_type": "REELS",
            "video_url": video_path,  # Must be publicly accessible URL
            "caption": caption,
            "access_token": access_token
        }

        result = await http_request("POST", api_endpoint, data=data)

        if not result["success"]:
            raise Exception(f"Instagram container creation failed: {result['body']}")

        creation_id = result["body"]["id"]

        # Publish media
        publish_endpoint = f"https://graph.facebook.com/v18.0/{instagram_account_id}/media_publish"

        publish_data = {
            "creation_id": creation_id,
            "access_token": access_token
        }

        publish_result = await http_request("POST", publish_endpoint, data=publish_data)

        media_id = publish_result["body"]["id"]

        logger.info(f"✅ Instagram Reel uploaded: {media_id}")
        return {
            "success": True,
            "media_id": media_id
        }

    except Exception as e:
        logger.error(f"❌ Instagram upload failed: {e}")
        return {"success": False, "error": str(e)}


async def instagram_set_caption(
    video_topic: str,
    hashtags: List[str] = None,
    anthropic_api_key: str = None
) -> Dict[str, Any]:
    """Generate Instagram caption with hashtags"""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=anthropic_api_key)

        hashtags_str = " ".join(hashtags) if hashtags else ""

        prompt = f"""Generate an Instagram Reel caption for: {video_topic}

Requirements:
- Authentic, engaging tone
- 2-3 sentences
- Call-to-action
- Emojis
- End with hashtags: {hashtags_str or "trending hashtags"}

Return caption only."""

        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-3-5-haiku-20241022",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        caption = response.content[0].text.strip()

        logger.info(f"✅ Instagram caption generated")
        return {"success": True, "caption": caption}

    except Exception as e:
        logger.error(f"❌ Instagram caption generation failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 11. CROSS-PLATFORM SCHEDULER
# ============================================================================

async def cross_platform_scheduler(
    video_path: str,
    caption: str,
    platforms: List[str],
    persona_id: str,
    schedule_times: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    Schedule video posts across multiple platforms

    Args:
        video_path: Path to video
        caption: Base caption
        platforms: ["tiktok", "youtube", "instagram"]
        persona_id: Persona ID for credentials
        schedule_times: {"tiktok": "2025-01-15T10:00:00Z", ...}

    Returns:
        {
            "success": true,
            "scheduled": {
                "tiktok": {"video_id": "...", "scheduled_at": "..."},
                "youtube": {...},
                ...
            }
        }
    """
    try:
        scheduled = {}

        for platform in platforms:
            # Get credentials
            creds_result = await tiktok_get_persona_credentials(persona_id)  # Would generalize this
            if not creds_result["success"]:
                scheduled[platform] = {"error": "No credentials"}
                continue

            access_token = creds_result["access_token"]

            # Upload to platform
            if platform == "tiktok":
                result = await tiktok_api_upload_video(video_path, caption, access_token)
            elif platform == "youtube":
                result = await youtube_api_upload(video_path, caption, access_token)
            elif platform == "instagram":
                instagram_id = "placeholder"  # Would get from DB
                result = await instagram_api_upload_reel(video_path, caption, access_token, instagram_id)
            else:
                result = {"success": False, "error": "Unknown platform"}

            scheduled[platform] = result

        logger.info(f"✅ Cross-platform scheduling complete: {len(scheduled)} platforms")
        return {
            "success": True,
            "scheduled": scheduled,
            "platform_count": len(scheduled)
        }

    except Exception as e:
        logger.error(f"❌ Cross-platform scheduling failed: {e}")
        return {"success": False, "error": str(e)}
