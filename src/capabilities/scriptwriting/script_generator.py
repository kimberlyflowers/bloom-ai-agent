"""
Scriptwriting Capabilities (5 total)

UGC-style script generation for viral videos:
1. write_video_script - Generate complete video script (ALREADY EXISTS - will integrate)
2. create_hook - Generate attention-grabbing first 3 seconds
3. add_timestamps - Add timing markers for editing
4. optimize_for_platform - Adapt script for TikTok/YouTube/Instagram
5. generate_captions - Create hardcoded captions from script
"""

import anthropic
import asyncio
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


# ============================================================================
# 1. WRITE_VIDEO_SCRIPT
# ============================================================================

async def write_video_script(
    topic: str,
    duration: int = 30,
    style: str = "ugc",
    platform: str = "tiktok",
    product_name: str = None,
    key_points: List[str] = None,
    anthropic_api_key: str = None
) -> Dict[str, Any]:
    """
    Generate complete video script

    Args:
        topic: Video topic/theme
        duration: Target duration in seconds
        style: "ugc", "educational", "testimonial", "trending"
        platform: "tiktok", "youtube", "instagram"
        product_name: Product to feature
        key_points: Key messages to include
        anthropic_api_key: Anthropic API key

    Returns:
        {
            "success": true,
            "script": "Full script text",
            "word_count": 120,
            "estimated_duration": 28.5,
            "scenes": [{"text": "...", "duration": 10}, ...]
        }
    """
    try:
        client = anthropic.Anthropic(api_key=anthropic_api_key)

        # Build prompt
        prompt = f"""Write a {duration}-second {style} video script for {platform}.

Topic: {topic}
{"Product: " + product_name if product_name else ""}
{"Key points: " + ", ".join(key_points) if key_points else ""}

Requirements:
- Natural, conversational tone (UGC style)
- Strong hook in first 3 seconds
- Clear call-to-action at end
- {duration} seconds when spoken (~{int(duration * 2.5)} words)
- Platform-optimized for {platform}

Return script in this format:
[0-3s] Hook text here
[3-10s] Body text here
[10-20s] More body text
[20-{duration}s] Call to action

Write ONLY the script, no explanations."""

        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-sonnet-4-5-20250929",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        script = response.content[0].text.strip()

        # Parse scenes
        scenes = []
        for line in script.split('\n'):
            if line.strip() and '[' in line:
                # Extract timestamp and text
                import re
                match = re.match(r'\[(\d+-\d+)s\]\s*(.*)', line)
                if match:
                    time_range = match.group(1)
                    text = match.group(2)
                    start, end = time_range.split('-')
                    scenes.append({
                        "start": int(start),
                        "end": int(end),
                        "duration": int(end) - int(start),
                        "text": text
                    })

        word_count = len(script.split())
        estimated_duration = word_count / 2.5  # ~150 words per minute

        logger.info(f"✅ Script generated: {word_count} words, {len(scenes)} scenes")
        return {
            "success": True,
            "script": script,
            "word_count": word_count,
            "estimated_duration": estimated_duration,
            "scenes": scenes
        }

    except Exception as e:
        logger.error(f"❌ Script generation failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 2. CREATE_HOOK
# ============================================================================

async def create_hook(
    topic: str,
    hook_type: str = "question",
    anthropic_api_key: str = None
) -> Dict[str, Any]:
    """
    Generate attention-grabbing hook (first 3 seconds)

    Args:
        topic: Video topic
        hook_type: "question", "shock", "promise", "relatable"
        anthropic_api_key: Anthropic API key

    Returns:
        {
            "success": true,
            "hook": "Wait... you're telling me this is FREE?!",
            "hook_type": "shock",
            "word_count": 7
        }
    """
    try:
        client = anthropic.Anthropic(api_key=anthropic_api_key)

        hook_templates = {
            "question": "Ask a provocative question that makes viewers curious",
            "shock": "Make a surprising statement that contradicts common belief",
            "promise": "Promise a specific benefit or result",
            "relatable": "Start with a common pain point viewers experience"
        }

        prompt = f"""Generate a 3-second hook for a video about: {topic}

Hook type: {hook_type} - {hook_templates[hook_type]}

Requirements:
- 5-10 words maximum
- Immediately attention-grabbing
- Makes viewer want to keep watching
- Conversational tone

Return ONLY the hook text, nothing else."""

        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-3-5-haiku-20241022",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )

        hook = response.content[0].text.strip().strip('"')

        logger.info(f"✅ Hook generated: {hook}")
        return {
            "success": True,
            "hook": hook,
            "hook_type": hook_type,
            "word_count": len(hook.split())
        }

    except Exception as e:
        logger.error(f"❌ Hook generation failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 3. ADD_TIMESTAMPS
# ============================================================================

async def add_timestamps(
    script: str,
    scene_duration: int = 5
) -> Dict[str, Any]:
    """
    Add timing markers to script for editing

    Args:
        script: Raw script text
        scene_duration: Default seconds per scene

    Returns:
        {
            "success": true,
            "timestamped_script": "[0-3s] Hook...\n[3-8s] Scene 2...",
            "scenes": [{"start": 0, "end": 3, "text": "..."}]
        }
    """
    try:
        # Split script into sentences
        sentences = [s.strip() for s in script.split('.') if s.strip()]

        timestamped_lines = []
        scenes = []
        current_time = 0

        for sentence in sentences:
            # Estimate duration based on word count
            word_count = len(sentence.split())
            duration = max(3, min(10, int(word_count / 2.5)))  # 3-10 seconds per scene

            end_time = current_time + duration

            line = f"[{current_time}-{end_time}s] {sentence}."
            timestamped_lines.append(line)

            scenes.append({
                "start": current_time,
                "end": end_time,
                "duration": duration,
                "text": sentence + "."
            })

            current_time = end_time

        timestamped_script = "\n".join(timestamped_lines)

        logger.info(f"✅ Timestamps added: {len(scenes)} scenes")
        return {
            "success": True,
            "timestamped_script": timestamped_script,
            "scenes": scenes,
            "total_duration": current_time
        }

    except Exception as e:
        logger.error(f"❌ Add timestamps failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 4. OPTIMIZE_FOR_PLATFORM
# ============================================================================

async def optimize_for_platform(
    script: str,
    target_platform: str,
    anthropic_api_key: str = None
) -> Dict[str, Any]:
    """
    Adapt script for specific platform (TikTok/YouTube/Instagram)

    Args:
        script: Original script
        target_platform: "tiktok", "youtube", "instagram"
        anthropic_api_key: Anthropic API key

    Returns:
        {
            "success": true,
            "optimized_script": "...",
            "changes_made": ["Added trending phrase", "Shortened for TikTok"]
        }
    """
    try:
        client = anthropic.Anthropic(api_key=anthropic_api_key)

        platform_requirements = {
            "tiktok": "Fast-paced, trending phrases, vertical format (9:16), 15-60s",
            "youtube": "Educational, SEO keywords, horizontal (16:9), 60-180s",
            "instagram": "Visual-first, aesthetic, square (1:1) or vertical, 30-90s"
        }

        prompt = f"""Optimize this video script for {target_platform}.

Original script:
{script}

Platform requirements: {platform_requirements[target_platform]}

Changes to make:
- Adjust pacing for platform
- Add platform-appropriate language/phrases
- Optimize length
- Include platform-specific CTAs

Return:
1. Optimized script
2. List of changes made

Format:
SCRIPT:
[optimized script here]

CHANGES:
- Change 1
- Change 2"""

        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-3-5-haiku-20241022",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        output = response.content[0].text.strip()

        # Parse response
        parts = output.split("CHANGES:")
        optimized_script = parts[0].replace("SCRIPT:", "").strip()
        changes = [c.strip().strip('-').strip() for c in parts[1].split('\n') if c.strip()]

        logger.info(f"✅ Script optimized for {target_platform}: {len(changes)} changes")
        return {
            "success": True,
            "optimized_script": optimized_script,
            "target_platform": target_platform,
            "changes_made": changes
        }

    except Exception as e:
        logger.error(f"❌ Platform optimization failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 5. GENERATE_CAPTIONS
# ============================================================================

async def generate_captions(
    script: str,
    max_chars_per_line: int = 40,
    max_lines: int = 2
) -> Dict[str, Any]:
    """
    Generate hardcoded captions from script (for video overlay)

    Args:
        script: Video script
        max_chars_per_line: Max characters per caption line
        max_lines: Max lines per caption

    Returns:
        {
            "success": true,
            "captions": [
                {"start": 0, "end": 3, "text": "Wait... you're telling me"},
                {"start": 3, "end": 6, "text": "this is FREE?!"}
            ]
        }
    """
    try:
        # Parse timestamped script if available
        import re
        captions = []

        # Check if script has timestamps
        if '[' in script and 's]' in script:
            # Parse timestamped format
            for line in script.split('\n'):
                match = re.match(r'\[(\d+)-(\d+)s\]\s*(.*)', line.strip())
                if match:
                    start = int(match.group(1))
                    end = int(match.group(2))
                    text = match.group(3)

                    # Split long text into multiple captions
                    words = text.split()
                    current_caption = []
                    current_length = 0

                    for word in words:
                        if current_length + len(word) + 1 > max_chars_per_line:
                            captions.append({
                                "start": start,
                                "end": end,
                                "text": " ".join(current_caption)
                            })
                            current_caption = [word]
                            current_length = len(word)
                        else:
                            current_caption.append(word)
                            current_length += len(word) + 1

                    if current_caption:
                        captions.append({
                            "start": start,
                            "end": end,
                            "text": " ".join(current_caption)
                        })
        else:
            # No timestamps - split by sentences
            sentences = [s.strip() for s in script.split('.') if s.strip()]
            duration_per_sentence = 3  # Default 3 seconds
            current_time = 0

            for sentence in sentences:
                captions.append({
                    "start": current_time,
                    "end": current_time + duration_per_sentence,
                    "text": sentence + "."
                })
                current_time += duration_per_sentence

        logger.info(f"✅ Captions generated: {len(captions)} segments")
        return {
            "success": True,
            "captions": captions,
            "count": len(captions)
        }

    except Exception as e:
        logger.error(f"❌ Caption generation failed: {e}")
        return {"success": False, "error": str(e)}
