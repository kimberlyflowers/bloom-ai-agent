"""
Tool Registry for Sarah's Agents

Provides tool definitions to spawned agents so they can call capabilities.
Each agent gets a tool list based on their specialization.
"""

from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# TOOL DEFINITIONS (Claude API format)
# ============================================================================

def get_video_creation_tools() -> List[Dict[str, Any]]:
    """
    Get all tools available to VideoCreationAgent

    VideoCreationAgent can:
    - Query persona data
    - Generate avatar images/videos
    - Generate voice
    - Write scripts
    - Edit videos
    - Create thumbnails
    - Publish to platforms
    """
    return [
        # PERSONA TOOLS
        {
            "name": "persona_database_query",
            "description": "Query persona database for reference images, voice ID, and brand info",
            "input_schema": {
                "type": "object",
                "properties": {
                    "persona_id": {
                        "type": "string",
                        "description": "Persona identifier (e.g., 'sarah_001')"
                    }
                },
                "required": ["persona_id"]
            }
        },
        {
            "name": "load_persona_assets",
            "description": "Load all persona assets (images, voice, personality)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "persona_id": {"type": "string"}
                },
                "required": ["persona_id"]
            }
        },

        # SCRIPTWRITING TOOLS
        {
            "name": "write_video_script",
            "description": "Generate complete UGC-style video script",
            "input_schema": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Video topic"},
                    "duration": {"type": "integer", "description": "Target duration in seconds (default 30)"},
                    "platform": {"type": "string", "enum": ["tiktok", "youtube", "instagram"]},
                    "product_name": {"type": "string", "description": "Product to feature (optional)"}
                },
                "required": ["topic"]
            }
        },
        {
            "name": "create_hook",
            "description": "Generate attention-grabbing hook (first 3 seconds)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "hook_type": {"type": "string", "enum": ["question", "shock", "promise", "relatable"]}
                },
                "required": ["topic"]
            }
        },

        # AVATAR GENERATION TOOLS
        {
            "name": "nanobanna_generate_character_image",
            "description": "Generate photo-realistic character image using AI",
            "input_schema": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Scene description"},
                    "reference_images": {"type": "array", "items": {"type": "string"}},
                    "style": {"type": "string", "enum": ["realistic_photography", "cinematic", "portrait"]},
                    "aspect_ratio": {"type": "string", "enum": ["9:16", "16:9", "1:1"]}
                },
                "required": ["prompt"]
            }
        },
        {
            "name": "nanobanna_batch_generate_poses",
            "description": "Generate 3 character images with different poses for video (45sec total)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "base_prompt": {"type": "string"},
                    "poses": {"type": "array", "items": {"type": "string"}},
                    "reference_images": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["base_prompt", "poses"]
            }
        },
        {
            "name": "elevenlabs_generate_voice",
            "description": "Generate voice audio from script text",
            "input_schema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Script text to synthesize"},
                    "voice_id": {"type": "string", "description": "ElevenLabs voice ID"}
                },
                "required": ["text", "voice_id"]
            }
        },
        {
            "name": "seaweed_image_to_video",
            "description": "Convert character image + audio to talking head video",
            "input_schema": {
                "type": "object",
                "properties": {
                    "image_path": {"type": "string"},
                    "audio_path": {"type": "string"}
                },
                "required": ["image_path", "audio_path"]
            }
        },

        # VIDEO EDITING TOOLS
        {
            "name": "moviepy_composite_video",
            "description": "Combine multiple avatar clips into complete video",
            "input_schema": {
                "type": "object",
                "properties": {
                    "scenes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "video_path": {"type": "string"},
                                "duration": {"type": "number"}
                            }
                        }
                    },
                    "output_path": {"type": "string"},
                    "transitions": {"type": "boolean"}
                },
                "required": ["scenes", "output_path"]
            }
        },
        {
            "name": "whisper_generate_captions",
            "description": "Auto-generate captions from audio using Whisper AI",
            "input_schema": {
                "type": "object",
                "properties": {
                    "audio_path": {"type": "string"},
                    "model": {"type": "string", "enum": ["tiny", "base", "small", "medium"]}
                },
                "required": ["audio_path"]
            }
        },
        {
            "name": "moviepy_add_hardcoded_captions",
            "description": "Burn captions into video",
            "input_schema": {
                "type": "object",
                "properties": {
                    "video_path": {"type": "string"},
                    "captions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "start": {"type": "number"},
                                "end": {"type": "number"},
                                "text": {"type": "string"}
                            }
                        }
                    },
                    "output_path": {"type": "string"}
                },
                "required": ["video_path", "captions"]
            }
        },
        {
            "name": "ffmpeg_optimize_for_tiktok",
            "description": "Optimize video for TikTok (1080x1920, 30fps)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "video_path": {"type": "string"},
                    "output_path": {"type": "string"}
                },
                "required": ["video_path"]
            }
        },
        {
            "name": "ffmpeg_add_background_music",
            "description": "Add background music to video",
            "input_schema": {
                "type": "object",
                "properties": {
                    "video_path": {"type": "string"},
                    "music_path": {"type": "string"},
                    "music_volume": {"type": "number", "description": "0.0-1.0"}
                },
                "required": ["video_path", "music_path"]
            }
        },

        # PUBLISHING TOOLS
        {
            "name": "tiktok_api_upload_video",
            "description": "Upload video to TikTok",
            "input_schema": {
                "type": "object",
                "properties": {
                    "video_path": {"type": "string"},
                    "caption": {"type": "string"},
                    "access_token": {"type": "string"}
                },
                "required": ["video_path", "caption", "access_token"]
            }
        },
        {
            "name": "tiktok_generate_ugc_caption",
            "description": "Generate TikTok-style caption with hashtags",
            "input_schema": {
                "type": "object",
                "properties": {
                    "video_topic": {"type": "string"},
                    "product_name": {"type": "string"}
                },
                "required": ["video_topic"]
            }
        },
        {
            "name": "update_persona_content_library",
            "description": "Save video metadata to persona's content library",
            "input_schema": {
                "type": "object",
                "properties": {
                    "persona_id": {"type": "string"},
                    "video_url": {"type": "string"},
                    "title": {"type": "string"},
                    "platform": {"type": "string"}
                },
                "required": ["persona_id", "video_url"]
            }
        }
    ]


def get_research_agent_tools() -> List[Dict[str, Any]]:
    """Tools for ResearchAgent"""
    return [
        {
            "name": "trending_topics_research",
            "description": "Research trending topics in a niche",
            "input_schema": {
                "type": "object",
                "properties": {
                    "niche": {"type": "string"},
                    "platform": {"type": "string", "enum": ["tiktok", "youtube", "instagram"]},
                    "time_range": {"type": "string", "enum": ["24h", "7d", "30d"]}
                },
                "required": ["niche"]
            }
        },
        {
            "name": "competitor_analysis",
            "description": "Analyze competitor content",
            "input_schema": {
                "type": "object",
                "properties": {
                    "competitor_accounts": {"type": "array", "items": {"type": "string"}},
                    "platform": {"type": "string"}
                },
                "required": ["competitor_accounts"]
            }
        },
        {
            "name": "generate_video_ideas",
            "description": "Generate video ideas from trends",
            "input_schema": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "count": {"type": "integer"},
                    "platform": {"type": "string"}
                },
                "required": []
            }
        }
    ]


def get_content_agent_tools() -> List[Dict[str, Any]]:
    """Tools for ContentPostingAgent"""
    return [
        {
            "name": "tiktok_api_upload_video",
            "description": "Upload video to TikTok",
            "input_schema": {
                "type": "object",
                "properties": {
                    "video_path": {"type": "string"},
                    "caption": {"type": "string"},
                    "access_token": {"type": "string"}
                },
                "required": ["video_path", "caption", "access_token"]
            }
        },
        {
            "name": "instagram_api_upload_reel",
            "description": "Upload Reel to Instagram",
            "input_schema": {
                "type": "object",
                "properties": {
                    "video_path": {"type": "string"},
                    "caption": {"type": "string"},
                    "access_token": {"type": "string"},
                    "instagram_account_id": {"type": "string"}
                },
                "required": ["video_path", "caption", "access_token", "instagram_account_id"]
            }
        }
    ]


# ============================================================================
# TOOL EXECUTION ROUTER
# ============================================================================

async def execute_tool(tool_name: str, tool_input: Dict[str, Any]) -> Any:
    """
    Execute a tool call from an agent

    Routes tool calls to the appropriate capability function.
    This is called by agents when they use tools.
    """
    import os

    # Set API keys from environment
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    api_key = os.getenv("REPLICATE_API_KEY") or os.getenv("ELEVENLABS_API_KEY")

    try:
        # PERSONA TOOLS
        if tool_name == "persona_database_query":
            from .persona.persona_manager import persona_database_query
            return await persona_database_query(**tool_input)

        elif tool_name == "load_persona_assets":
            from .persona.persona_manager import load_persona_assets
            return await load_persona_assets(**tool_input)

        # SCRIPTWRITING TOOLS
        elif tool_name == "write_video_script":
            from .scriptwriting.script_generator import write_video_script
            return await write_video_script(**tool_input, anthropic_api_key=anthropic_api_key)

        elif tool_name == "create_hook":
            from .scriptwriting.script_generator import create_hook
            return await create_hook(**tool_input, anthropic_api_key=anthropic_api_key)

        # AVATAR TOOLS
        elif tool_name == "nanobanna_generate_character_image":
            from .avatar.avatar_generator import nanobanna_generate_character_image
            return await nanobanna_generate_character_image(**tool_input, api_key=api_key)

        elif tool_name == "nanobanna_batch_generate_poses":
            from .avatar.avatar_generator import nanobanna_batch_generate_poses
            return await nanobanna_batch_generate_poses(**tool_input, api_key=api_key)

        elif tool_name == "elevenlabs_generate_voice":
            from .avatar.avatar_generator import elevenlabs_generate_voice
            return await elevenlabs_generate_voice(**tool_input, api_key=api_key)

        elif tool_name == "seaweed_image_to_video":
            from .avatar.avatar_generator import seaweed_image_to_video
            return await seaweed_image_to_video(**tool_input, api_key=api_key)

        # VIDEO EDITING TOOLS
        elif tool_name == "moviepy_composite_video":
            from .editing.video_editor import moviepy_composite_video
            return await moviepy_composite_video(**tool_input)

        elif tool_name == "whisper_generate_captions":
            from .editing.video_editor import whisper_generate_captions
            return await whisper_generate_captions(**tool_input)

        elif tool_name == "moviepy_add_hardcoded_captions":
            from .editing.video_editor import moviepy_add_hardcoded_captions
            return await moviepy_add_hardcoded_captions(**tool_input)

        elif tool_name == "ffmpeg_optimize_for_tiktok":
            from .editing.video_editor import ffmpeg_optimize_for_tiktok
            return await ffmpeg_optimize_for_tiktok(**tool_input)

        elif tool_name == "ffmpeg_add_background_music":
            from .editing.video_editor import ffmpeg_add_background_music
            return await ffmpeg_add_background_music(**tool_input)

        # PUBLISHING TOOLS
        elif tool_name == "tiktok_api_upload_video":
            from .publishing.platform_publisher import tiktok_api_upload_video
            return await tiktok_api_upload_video(**tool_input)

        elif tool_name == "tiktok_generate_ugc_caption":
            from .publishing.platform_publisher import tiktok_generate_ugc_caption
            return await tiktok_generate_ugc_caption(**tool_input, anthropic_api_key=anthropic_api_key)

        elif tool_name == "update_persona_content_library":
            from .persona.persona_manager import update_persona_content_library
            return await update_persona_content_library(**tool_input)

        # RESEARCH TOOLS
        elif tool_name == "trending_topics_research":
            from .content.content_research import trending_topics_research
            return await trending_topics_research(**tool_input, anthropic_api_key=anthropic_api_key)

        elif tool_name == "competitor_analysis":
            from .content.content_research import competitor_analysis
            return await competitor_analysis(**tool_input, anthropic_api_key=anthropic_api_key)

        elif tool_name == "generate_video_ideas":
            from .content.content_research import generate_video_ideas
            return await generate_video_ideas(**tool_input, anthropic_api_key=anthropic_api_key)

        # PUBLISHING (CONTENT AGENT)
        elif tool_name == "instagram_api_upload_reel":
            from .publishing.platform_publisher import instagram_api_upload_reel
            return await instagram_api_upload_reel(**tool_input)

        else:
            logger.warning(f"⚠️ Unknown tool: {tool_name}")
            return {"error": f"Unknown tool: {tool_name}"}

    except Exception as e:
        logger.error(f"❌ Tool execution failed ({tool_name}): {e}")
        return {"error": str(e)}
