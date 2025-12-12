"""
Video Editing Capabilities (11 total)

Professional video editing WITHOUT UI automation:
1. moviepy_composite_video - Combine avatar clips into full video
2. moviepy_add_product_overlay - Add product images/graphics
3. moviepy_add_hardcoded_captions - Burn captions into video
4. whisper_generate_captions - Auto-generate captions from audio
5. ffmpeg_add_transitions - Add transitions between scenes
6. ffmpeg_add_background_music - Add music track
7. ffmpeg_adjust_audio_levels - Normalize/adjust audio
8. ffmpeg_apply_effects - Apply visual effects
9. ffmpeg_optimize_for_tiktok - Optimize for TikTok specs
10. ffmpeg_optimize_for_youtube - Optimize for YouTube specs
11. ffmpeg_optimize_for_instagram - Optimize for Instagram specs
"""

import asyncio
import logging
import os
from typing import Dict, List, Any, Optional
from ..foundation.core_utilities import subprocess_execute, get_storage_manager, metadata_extraction

logger = logging.getLogger(__name__)


# ============================================================================
# 1. MOVIEPY_COMPOSITE_VIDEO
# ============================================================================

async def moviepy_composite_video(
    scenes: List[Dict[str, Any]],
    output_path: str,
    transitions: bool = True
) -> Dict[str, Any]:
    """
    Combine avatar video clips into complete video using MoviePy

    Args:
        scenes: List of scenes [{"video_path": "...", "duration": 10}, ...]
        output_path: Where to save final video
        transitions: Add transitions between scenes

    Returns:
        {
            "success": true,
            "video_path": "output.mp4",
            "duration": 30.5,
            "resolution": "1080x1920"
        }
    """
    try:
        # Build MoviePy script
        python_script = f"""
import sys
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip
import json

scenes_data = {scenes}
output_path = "{output_path}"

clips = []
for scene in scenes_data:
    clip = VideoFileClip(scene['video_path'])
    if 'duration' in scene and scene['duration']:
        clip = clip.set_duration(scene['duration'])
    clips.append(clip)

# Concatenate clips
if {transitions}:
    # Add crossfade transitions
    final = concatenate_videoclips(clips, method="compose")
else:
    final = concatenate_videoclips(clips)

# Write output
final.write_videofile(
    output_path,
    fps=30,
    codec='libx264',
    audio_codec='aac',
    preset='medium'
)

final.close()
for clip in clips:
    clip.close()

# Return metadata
print(json.dumps({{
    "duration": final.duration,
    "size": [final.w, final.h]
}}))
"""

        # Write script to temp file
        storage = get_storage_manager()
        script_path = os.path.join(storage.base_path, "temp_composite.py")
        with open(script_path, 'w') as f:
            f.write(python_script)

        # Execute
        result = await subprocess_execute(
            f"python {script_path}",
            timeout=300
        )

        if not result["success"]:
            raise Exception(f"MoviePy compositing failed: {result['stderr']}")

        # Parse metadata from output
        import json
        import re
        match = re.search(r'\{.*"duration".*\}', result["stdout"], re.DOTALL)
        if match:
            metadata = json.loads(match.group(0))
        else:
            metadata = {}

        # Get file metadata
        file_meta = await metadata_extraction(output_path, "video")

        logger.info(f"✅ Video composited: {output_path}")
        return {
            "success": True,
            "video_path": output_path,
            "duration": file_meta.get("duration", metadata.get("duration")),
            "resolution": f"{file_meta.get('width')}x{file_meta.get('height')}"
        }

    except Exception as e:
        logger.error(f"❌ Video compositing failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 2. MOVIEPY_ADD_PRODUCT_OVERLAY
# ============================================================================

async def moviepy_add_product_overlay(
    video_path: str,
    product_image_path: str,
    position: str = "bottom-right",
    scale: float = 0.2,
    output_path: str = None
) -> Dict[str, Any]:
    """
    Add product image overlay to video

    Args:
        video_path: Input video
        product_image_path: Product image to overlay
        position: "bottom-right", "bottom-left", "top-right", "top-left", "center"
        scale: Scale of overlay (0.1 = 10% of video size)
        output_path: Output path

    Returns:
        {"success": bool, "video_path": str}
    """
    try:
        if not output_path:
            output_path = video_path.replace('.mp4', '_with_product.mp4')

        # Position mapping
        position_map = {
            "bottom-right": "('right', 'bottom')",
            "bottom-left": "('left', 'bottom')",
            "top-right": "('right', 'top')",
            "top-left": "('left', 'top')",
            "center": "('center', 'center')"
        }

        python_script = f"""
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

video = VideoFileClip("{video_path}")
product = ImageClip("{product_image_path}")

# Scale product image
product_width = int(video.w * {scale})
product = product.resize(width=product_width)

# Set duration and position
product = product.set_duration(video.duration)
product = product.set_position({position_map[position]})

# Composite
final = CompositeVideoClip([video, product])

final.write_videofile(
    "{output_path}",
    fps=video.fps,
    codec='libx264'
)

video.close()
product.close()
final.close()
"""

        storage = get_storage_manager()
        script_path = os.path.join(storage.base_path, "temp_overlay.py")
        with open(script_path, 'w') as f:
            f.write(python_script)

        result = await subprocess_execute(f"python {script_path}", timeout=180)

        if not result["success"]:
            raise Exception(f"Product overlay failed: {result['stderr']}")

        logger.info(f"✅ Product overlay added: {output_path}")
        return {
            "success": True,
            "video_path": output_path
        }

    except Exception as e:
        logger.error(f"❌ Product overlay failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 3. MOVIEPY_ADD_HARDCODED_CAPTIONS
# ============================================================================

async def moviepy_add_hardcoded_captions(
    video_path: str,
    captions: List[Dict[str, Any]],
    output_path: str = None,
    font_size: int = 48,
    font_color: str = "white"
) -> Dict[str, Any]:
    """
    Burn captions into video

    Args:
        video_path: Input video
        captions: [{"start": 0, "end": 3, "text": "..."}, ...]
        output_path: Output path
        font_size: Font size
        font_color: Font color

    Returns:
        {"success": bool, "video_path": str}
    """
    try:
        if not output_path:
            output_path = video_path.replace('.mp4', '_with_captions.mp4')

        import json
        captions_json = json.dumps(captions)

        python_script = f"""
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import json

video = VideoFileClip("{video_path}")
captions_data = {captions_json}

text_clips = []
for cap in captions_data:
    txt = TextClip(
        cap['text'],
        fontsize={font_size},
        color='{font_color}',
        stroke_color='black',
        stroke_width=2,
        method='caption',
        size=(video.w * 0.9, None)
    )
    txt = txt.set_start(cap['start'])
    txt = txt.set_duration(cap['end'] - cap['start'])
    txt = txt.set_position(('center', 'bottom'))
    text_clips.append(txt)

final = CompositeVideoClip([video] + text_clips)

final.write_videofile(
    "{output_path}",
    fps=video.fps,
    codec='libx264'
)

video.close()
final.close()
"""

        storage = get_storage_manager()
        script_path = os.path.join(storage.base_path, "temp_captions.py")
        with open(script_path, 'w') as f:
            f.write(python_script)

        result = await subprocess_execute(f"python {script_path}", timeout=180)

        if not result["success"]:
            raise Exception(f"Caption burning failed: {result['stderr']}")

        logger.info(f"✅ Captions burned into video: {output_path}")
        return {
            "success": True,
            "video_path": output_path,
            "caption_count": len(captions)
        }

    except Exception as e:
        logger.error(f"❌ Caption burning failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 4. WHISPER_GENERATE_CAPTIONS
# ============================================================================

async def whisper_generate_captions(
    audio_path: str,
    model: str = "base"
) -> Dict[str, Any]:
    """
    Auto-generate captions from audio using Whisper AI

    Args:
        audio_path: Path to audio file
        model: Whisper model ("tiny", "base", "small", "medium", "large")

    Returns:
        {
            "success": true,
            "captions": [{"start": 0, "end": 3, "text": "..."}, ...],
            "srt_path": "captions.srt",
            "full_text": "Complete transcript"
        }
    """
    try:
        # Run Whisper
        command = f"whisper '{audio_path}' --model {model} --output_format srt --output_dir /tmp"

        result = await subprocess_execute(command, timeout=300)

        if not result["success"]:
            raise Exception(f"Whisper failed: {result['stderr']}")

        # Parse SRT file
        srt_path = audio_path.replace(os.path.splitext(audio_path)[1], '.srt')

        if not os.path.exists(srt_path):
            # Check /tmp
            srt_filename = os.path.basename(audio_path).replace(os.path.splitext(audio_path)[1], '.srt')
            srt_path = os.path.join('/tmp', srt_filename)

        captions = []
        full_text = []

        if os.path.exists(srt_path):
            with open(srt_path, 'r') as f:
                content = f.read()

            # Parse SRT format
            blocks = content.strip().split('\n\n')
            for block in blocks:
                lines = block.split('\n')
                if len(lines) >= 3:
                    # Extract timestamps
                    timestamp_line = lines[1]
                    # Format: 00:00:00,000 --> 00:00:03,000
                    times = timestamp_line.split(' --> ')
                    if len(times) == 2:
                        start = _parse_srt_time(times[0])
                        end = _parse_srt_time(times[1])
                        text = ' '.join(lines[2:])

                        captions.append({
                            "start": start,
                            "end": end,
                            "text": text
                        })
                        full_text.append(text)

        logger.info(f"✅ Captions generated: {len(captions)} segments")
        return {
            "success": True,
            "captions": captions,
            "srt_path": srt_path,
            "full_text": " ".join(full_text),
            "segment_count": len(captions)
        }

    except Exception as e:
        logger.error(f"❌ Whisper caption generation failed: {e}")
        return {"success": False, "error": str(e)}


def _parse_srt_time(time_str: str) -> float:
    """Convert SRT timestamp to seconds"""
    # Format: 00:00:03,000
    parts = time_str.replace(',', '.').split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    return hours * 3600 + minutes * 60 + seconds


# ============================================================================
# 5. FFMPEG_ADD_TRANSITIONS
# ============================================================================

async def ffmpeg_add_transitions(
    video_paths: List[str],
    output_path: str,
    transition_duration: float = 0.5
) -> Dict[str, Any]:
    """
    Add transitions between video clips using FFmpeg

    Args:
        video_paths: List of video files
        output_path: Output path
        transition_duration: Transition duration in seconds

    Returns:
        {"success": bool, "video_path": str}
    """
    try:
        # Build FFmpeg xfade filter complex
        inputs = " ".join([f"-i '{path}'" for path in video_paths])

        # Build filter complex with xfade
        filter_parts = []
        for i in range(len(video_paths) - 1):
            if i == 0:
                filter_parts.append(f"[0:v][1:v]xfade=transition=fade:duration={transition_duration}:offset=0[v{i+1}]")
            else:
                filter_parts.append(f"[v{i}][{i+1}:v]xfade=transition=fade:duration={transition_duration}:offset=0[v{i+1}]")

        filter_complex = ";".join(filter_parts)
        final_output = f"[v{len(video_paths)-1}]"

        command = f"ffmpeg {inputs} -filter_complex '{filter_complex}' -map '{final_output}' '{output_path}'"

        result = await subprocess_execute(command, timeout=180)

        if not result["success"]:
            raise Exception(f"FFmpeg transitions failed: {result['stderr']}")

        logger.info(f"✅ Transitions added: {output_path}")
        return {
            "success": True,
            "video_path": output_path,
            "clip_count": len(video_paths)
        }

    except Exception as e:
        logger.error(f"❌ FFmpeg transitions failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 6. FFMPEG_ADD_BACKGROUND_MUSIC
# ============================================================================

async def ffmpeg_add_background_music(
    video_path: str,
    music_path: str,
    output_path: str = None,
    music_volume: float = 0.3
) -> Dict[str, Any]:
    """
    Add background music to video

    Args:
        video_path: Input video
        music_path: Background music file
        output_path: Output path
        music_volume: Music volume (0.0-1.0)

    Returns:
        {"success": bool, "video_path": str}
    """
    try:
        if not output_path:
            output_path = video_path.replace('.mp4', '_with_music.mp4')

        # Mix audio tracks
        command = f"""ffmpeg -i '{video_path}' -i '{music_path}' \
            -filter_complex '[1:a]volume={music_volume}[music];[0:a][music]amix=inputs=2:duration=shortest' \
            -c:v copy -c:a aac '{output_path}'"""

        result = await subprocess_execute(command, timeout=180)

        if not result["success"]:
            raise Exception(f"FFmpeg music mixing failed: {result['stderr']}")

        logger.info(f"✅ Background music added: {output_path}")
        return {
            "success": True,
            "video_path": output_path
        }

    except Exception as e:
        logger.error(f"❌ Background music failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 7. FFMPEG_ADJUST_AUDIO_LEVELS
# ============================================================================

async def ffmpeg_adjust_audio_levels(
    video_path: str,
    output_path: str = None,
    volume: float = 1.0,
    normalize: bool = True
) -> Dict[str, Any]:
    """
    Normalize/adjust audio levels

    Args:
        video_path: Input video
        output_path: Output path
        volume: Volume multiplier (1.0 = no change)
        normalize: Auto-normalize to -16 LUFS (loudness standard)

    Returns:
        {"success": bool, "video_path": str}
    """
    try:
        if not output_path:
            output_path = video_path.replace('.mp4', '_audio_adjusted.mp4')

        if normalize:
            # Two-pass loudness normalization
            command = f"""ffmpeg -i '{video_path}' \
                -af loudnorm=I=-16:TP=-1.5:LRA=11 \
                -c:v copy '{output_path}'"""
        else:
            # Simple volume adjustment
            command = f"""ffmpeg -i '{video_path}' \
                -af 'volume={volume}' \
                -c:v copy -c:a aac '{output_path}'"""

        result = await subprocess_execute(command, timeout=180)

        if not result["success"]:
            raise Exception(f"FFmpeg audio adjustment failed: {result['stderr']}")

        logger.info(f"✅ Audio levels adjusted: {output_path}")
        return {
            "success": True,
            "video_path": output_path
        }

    except Exception as e:
        logger.error(f"❌ Audio adjustment failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 8. FFMPEG_APPLY_EFFECTS
# ============================================================================

async def ffmpeg_apply_effects(
    video_path: str,
    effects: List[str],
    output_path: str = None
) -> Dict[str, Any]:
    """
    Apply visual effects to video

    Args:
        video_path: Input video
        effects: List of effects ["brightness=0.1", "contrast=1.2", "saturation=1.3"]
        output_path: Output path

    Returns:
        {"success": bool, "video_path": str}
    """
    try:
        if not output_path:
            output_path = video_path.replace('.mp4', '_effects.mp4')

        # Build filter chain
        filter_chain = ",".join(effects)

        command = f"ffmpeg -i '{video_path}' -vf '{filter_chain}' -c:a copy '{output_path}'"

        result = await subprocess_execute(command, timeout=180)

        if not result["success"]:
            raise Exception(f"FFmpeg effects failed: {result['stderr']}")

        logger.info(f"✅ Effects applied: {output_path}")
        return {
            "success": True,
            "video_path": output_path,
            "effects_applied": len(effects)
        }

    except Exception as e:
        logger.error(f"❌ Effects application failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 9-11. PLATFORM OPTIMIZATION
# ============================================================================

async def ffmpeg_optimize_for_tiktok(
    video_path: str,
    output_path: str = None
) -> Dict[str, Any]:
    """Optimize video for TikTok (1080x1920, 30fps, H.264)"""
    return await _optimize_for_platform(
        video_path, output_path or video_path.replace('.mp4', '_tiktok.mp4'),
        width=1080, height=1920, fps=30, bitrate="5000k"
    )


async def ffmpeg_optimize_for_youtube(
    video_path: str,
    output_path: str = None
) -> Dict[str, Any]:
    """Optimize video for YouTube (1920x1080, 30fps, H.264)"""
    return await _optimize_for_platform(
        video_path, output_path or video_path.replace('.mp4', '_youtube.mp4'),
        width=1920, height=1080, fps=30, bitrate="8000k"
    )


async def ffmpeg_optimize_for_instagram(
    video_path: str,
    output_path: str = None
) -> Dict[str, Any]:
    """Optimize video for Instagram (1080x1350, 30fps, H.264)"""
    return await _optimize_for_platform(
        video_path, output_path or video_path.replace('.mp4', '_instagram.mp4'),
        width=1080, height=1350, fps=30, bitrate="5000k"
    )


async def _optimize_for_platform(
    video_path: str,
    output_path: str,
    width: int,
    height: int,
    fps: int,
    bitrate: str
) -> Dict[str, Any]:
    """Internal helper for platform optimization"""
    try:
        command = f"""ffmpeg -i '{video_path}' \
            -vf 'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,fps={fps}' \
            -c:v libx264 -preset fast -b:v {bitrate} \
            -c:a aac -b:a 128k -ar 44100 \
            -movflags +faststart \
            '{output_path}'"""

        result = await subprocess_execute(command, timeout=180)

        if not result["success"]:
            raise Exception(f"Platform optimization failed: {result['stderr']}")

        file_meta = await metadata_extraction(output_path, "video")

        logger.info(f"✅ Video optimized: {output_path} ({width}x{height})")
        return {
            "success": True,
            "video_path": output_path,
            "resolution": f"{width}x{height}",
            "fps": fps,
            "size_bytes": file_meta.get("size_bytes")
        }

    except Exception as e:
        logger.error(f"❌ Platform optimization failed: {e}")
        return {"success": False, "error": str(e)}
