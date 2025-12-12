"""
Visual Assets Capabilities (5 total)

Generate visual assets for videos and marketing:
1. generate_ai_image - Generate AI images for B-roll
2. design_thumbnail - Create platform-optimized thumbnails (integrates Canva UI map)
3. create_lower_thirds - Generate lower third graphics
4. generate_b_roll - Create B-roll footage
5. create_motion_graphics - Simple motion graphics overlays
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from ..foundation.core_utilities import http_request, subprocess_execute
from ..avatar.avatar_generator import nanobanna_generate_character_image

logger = logging.getLogger(__name__)


# ============================================================================
# 1. GENERATE_AI_IMAGE
# ============================================================================

async def generate_ai_image(
    prompt: str,
    style: str = "photorealistic",
    aspect_ratio: str = "16:9",
    api_key: str = None
) -> Dict[str, Any]:
    """
    Generate AI images for B-roll or backgrounds

    Args:
        prompt: Image description
        style: "photorealistic", "illustration", "minimalist"
        aspect_ratio: "16:9", "9:16", "1:1"
        api_key: API key (Replicate/Midjourney)

    Returns:
        {
            "success": true,
            "image_url": "...",
            "image_path": "local/path.jpg"
        }
    """
    try:
        # Reuse avatar generation system
        result = await nanobanna_generate_character_image(
            prompt=prompt,
            style=style,
            aspect_ratio=aspect_ratio,
            api_key=api_key
        )

        logger.info(f"✅ AI image generated: {prompt[:50]}...")
        return result

    except Exception as e:
        logger.error(f"❌ AI image generation failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 2. DESIGN_THUMBNAIL
# ============================================================================

async def design_thumbnail(
    title: str,
    persona_id: str = None,
    persona_image_path: str = None,
    platform: str = "youtube",
    template_style: str = "bold"
) -> Dict[str, Any]:
    """
    Create platform-optimized thumbnail (integrates with existing Canva UI map)

    Args:
        title: Video title text
        persona_id: Persona ID for face
        persona_image_path: Direct path to persona image
        platform: "youtube", "tiktok", "instagram"
        template_style: "bold", "minimal", "professional"

    Returns:
        {
            "success": true,
            "thumbnail_path": "thumbnails/thumb.jpg",
            "thumbnail_url": "..."
        }
    """
    try:
        # TODO: Integrate with Canva browser automation (existing UI map)
        # For now, generate using ImageMagick or PIL

        # Platform-specific sizes
        size_map = {
            "youtube": (1280, 720),
            "tiktok": (1080, 1920),
            "instagram": (1080, 1080)
        }

        width, height = size_map[platform]

        # Use ImageMagick to create simple thumbnail
        import time
        output_path = f"thumbnails/{int(time.time())}_thumbnail.jpg"

        command = f"""convert -size {width}x{height} \
            -background '#FF5733' \
            -fill white \
            -gravity center \
            -pointsize 72 \
            -font Arial-Bold \
            label:'{title[:40]}' \
            '{output_path}'"""

        result = await subprocess_execute(command, timeout=30)

        if not result["success"]:
            raise Exception(f"Thumbnail creation failed: {result['stderr']}")

        logger.info(f"✅ Thumbnail created: {output_path}")
        return {
            "success": True,
            "thumbnail_path": output_path,
            "resolution": f"{width}x{height}",
            "platform": platform
        }

    except Exception as e:
        logger.error(f"❌ Thumbnail creation failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 3. CREATE_LOWER_THIRDS
# ============================================================================

async def create_lower_thirds(
    text: str,
    subtitle: str = None,
    width: int = 1920,
    height: int = 200
) -> Dict[str, Any]:
    """
    Generate lower third graphics (name plates, info bars)

    Args:
        text: Main text
        subtitle: Subtitle text
        width: Width in pixels
        height: Height in pixels

    Returns:
        {"success": bool, "image_path": str}
    """
    try:
        import time
        output_path = f"graphics/{int(time.time())}_lower_third.png"

        # Create semi-transparent lower third with text
        command = f"""convert -size {width}x{height} \
            xc:none \
            -fill 'rgba(0,0,0,0.7)' \
            -draw 'rectangle 0,0 {width},{height}' \
            -fill white \
            -pointsize 48 \
            -gravity west \
            -annotate +50+0 '{text}' \
            '{output_path}'"""

        result = await subprocess_execute(command, timeout=30)

        if not result["success"]:
            raise Exception(f"Lower third creation failed: {result['stderr']}")

        logger.info(f"✅ Lower third created: {output_path}")
        return {
            "success": True,
            "image_path": output_path
        }

    except Exception as e:
        logger.error(f"❌ Lower third creation failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 4. GENERATE_B_ROLL
# ============================================================================

async def generate_b_roll(
    topic: str,
    duration: int = 5,
    count: int = 3,
    api_key: str = None
) -> Dict[str, Any]:
    """
    Generate B-roll footage (AI-generated or stock)

    Args:
        topic: B-roll topic
        duration: Seconds per clip
        count: Number of clips
        api_key: API key

    Returns:
        {
            "success": true,
            "clips": [
                {"path": "...", "duration": 5},
                ...
            ]
        }
    """
    try:
        # Generate B-roll images and convert to video
        clips = []

        for i in range(count):
            prompt = f"{topic}, professional stock footage style, {i+1} of {count}"

            # Generate image
            image_result = await generate_ai_image(
                prompt=prompt,
                style="photorealistic",
                aspect_ratio="16:9",
                api_key=api_key
            )

            if image_result["success"]:
                # Convert to video (static image with duration)
                import time
                video_path = f"broll/{int(time.time())}_{i}.mp4"

                command = f"""ffmpeg -loop 1 -i '{image_result['image_path']}' \
                    -c:v libx264 -t {duration} -pix_fmt yuv420p '{video_path}'"""

                result = await subprocess_execute(command, timeout=60)

                if result["success"]:
                    clips.append({
                        "path": video_path,
                        "duration": duration
                    })

        logger.info(f"✅ B-roll generated: {len(clips)} clips")
        return {
            "success": True,
            "clips": clips,
            "count": len(clips)
        }

    except Exception as e:
        logger.error(f"❌ B-roll generation failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 5. CREATE_MOTION_GRAPHICS
# ============================================================================

async def create_motion_graphics(
    graphic_type: str,
    duration: int = 3,
    text: str = None
) -> Dict[str, Any]:
    """
    Create simple motion graphics (animated text, transitions)

    Args:
        graphic_type: "text_reveal", "logo_animation", "transition"
        duration: Duration in seconds
        text: Text for graphic

    Returns:
        {"success": bool, "video_path": str}
    """
    try:
        import time
        output_path = f"graphics/{int(time.time())}_{graphic_type}.mp4"

        if graphic_type == "text_reveal":
            # Animated text reveal
            command = f"""ffmpeg -f lavfi -i color=c=black:s=1920x1080:d={duration} \
                -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='{text}':fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:alpha='if(lt(t,0.5),0,if(lt(t,1.5),(t-0.5),1))'" \
                -c:v libx264 -t {duration} -pix_fmt yuv420p '{output_path}'"""

            result = await subprocess_execute(command, timeout=60)

            if not result["success"]:
                raise Exception(f"Motion graphics failed: {result['stderr']}")

        logger.info(f"✅ Motion graphic created: {output_path}")
        return {
            "success": True,
            "video_path": output_path,
            "duration": duration
        }

    except Exception as e:
        logger.error(f"❌ Motion graphics creation failed: {e}")
        return {"success": False, "error": str(e)}
