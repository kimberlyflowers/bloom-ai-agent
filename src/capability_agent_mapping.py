"""
Capability-to-Agent Type Mapping

This maps each of Sarah's 71 capabilities to agent types.
When Sarah needs help with a complex task, she analyzes which capabilities are needed,
then spawns the appropriate specialized agents dynamically.

Agent Types:
- script: Script writing for videos
- video_editing: Video editing and post-production
- analytics: Performance tracking and insights
- engagement: Comment moderation and community management
- publishing: Cross-platform content distribution
- avatar: Character generation and voice synthesis
- design: Visual assets and graphics
- research: Trending topics and competitor analysis
- persona: Persona management and asset loading
- strategy: Content strategy and optimization
"""

CAPABILITY_AGENT_MAP = {
    # ========== SCRIPT WRITING ==========
    # Script Agent handles all video script creation
    'write_video_script': 'script',
    'create_hook': 'script',
    'add_timestamps': 'script',
    'optimize_for_platform': 'script',
    'generate_captions': 'script',

    # ========== VIDEO EDITING ==========
    # Video Editing Agent handles all video production
    'moviepy_composite_video': 'video_editing',
    'moviepy_add_product_overlay': 'video_editing',
    'moviepy_add_hardcoded_captions': 'video_editing',
    'whisper_generate_captions': 'video_editing',
    'ffmpeg_add_transitions': 'video_editing',
    'ffmpeg_add_background_music': 'video_editing',
    'ffmpeg_adjust_audio_levels': 'video_editing',
    'ffmpeg_apply_effects': 'video_editing',
    'ffmpeg_optimize_for_tiktok': 'video_editing',
    'ffmpeg_optimize_for_youtube': 'video_editing',
    'ffmpeg_optimize_for_instagram': 'video_editing',

    # ========== ANALYTICS ==========
    # Analytics Agent handles all performance tracking
    'youtube_analytics_fetch': 'analytics',
    'tiktok_analytics_fetch': 'analytics',
    'instagram_insights_fetch': 'analytics',
    'track_engagement_metrics': 'analytics',
    'generate_performance_report': 'analytics',
    'identify_top_performing_content': 'analytics',

    # ========== ENGAGEMENT ==========
    # Engagement Agent handles community interaction
    'comment_moderation': 'engagement',
    'auto_reply_comments': 'engagement',
    'dm_response': 'engagement',

    # ========== PUBLISHING ==========
    # Publishing Agent handles content distribution
    'youtube_api_upload': 'publishing',
    'youtube_set_metadata': 'publishing',
    'youtube_upload_thumbnail': 'publishing',
    'youtube_schedule_publish': 'publishing',
    'tiktok_api_upload_video': 'publishing',
    'tiktok_generate_ugc_caption': 'publishing',
    'tiktok_select_trending_hashtags': 'publishing',
    'tiktok_get_persona_credentials': 'publishing',
    'instagram_api_upload_reel': 'publishing',
    'instagram_set_caption': 'publishing',
    'cross_platform_scheduler': 'publishing',

    # ========== AVATAR/CHARACTER ==========
    # Avatar Agent handles character generation and voice
    'nanobanna_generate_character_image': 'avatar',
    'nanobanna_batch_generate_poses': 'avatar',
    'elevenlabs_clone_voice': 'avatar',
    'elevenlabs_generate_voice': 'avatar',
    'seaweed_image_to_video': 'avatar',
    'seaweed_audio_lipsync': 'avatar',
    'character_sheet_generation': 'avatar',
    'lora_training_automation': 'avatar',

    # ========== DESIGN ==========
    # Design Agent handles visual assets
    'generate_ai_image': 'design',
    'design_thumbnail': 'design',
    'create_lower_thirds': 'design',
    'generate_b_roll': 'design',
    'create_motion_graphics': 'design',

    # ========== RESEARCH ==========
    # Research Agent handles market research and trends
    'trending_topics_research': 'research',
    'competitor_analysis': 'research',
    'keyword_research': 'research',
    'content_gap_analysis': 'research',
    'generate_video_ideas': 'research',

    # ========== PERSONA MANAGEMENT ==========
    # Persona Agent handles persona data and assets
    'persona_database_query': 'persona',
    'load_persona_assets': 'persona',
    'validate_persona_completeness': 'persona',
    'get_persona_reference_images': 'persona',
    'get_persona_voice_id': 'persona',
    'update_persona_content_library': 'persona',

    # ========== FOUNDATION CAPABILITIES ==========
    # These are low-level capabilities that Sarah uses directly
    # No dedicated agent needed - Sarah handles these herself
    'database_query': None,
    'http_request': None,
    'file_upload_multipart': None,
    'file_download': None,
    'oauth_authentication': None,
    'subprocess_execute': None,
    'webhook_handler': None,
    'batch_processing': None,
    'queue_management': None,
    'storage_management': None,
    'metadata_extraction': None,
}

# Agent type metadata
AGENT_METADATA = {
    'script': {
        'name': 'Script Agent',
        'icon': '✍️',
        'description': 'Writes video scripts with hooks and timestamps'
    },
    'video_editing': {
        'name': 'Video Editing Agent',
        'icon': '🎬',
        'description': 'Edits videos with transitions, music, and effects'
    },
    'analytics': {
        'name': 'Analytics Agent',
        'icon': '📊',
        'description': 'Tracks performance and generates insights'
    },
    'engagement': {
        'name': 'Engagement Agent',
        'icon': '💬',
        'description': 'Manages comments and community interaction'
    },
    'publishing': {
        'name': 'Publishing Agent',
        'icon': '🚀',
        'description': 'Publishes content across platforms'
    },
    'avatar': {
        'name': 'Avatar Agent',
        'icon': '🎭',
        'description': 'Generates characters and voice synthesis'
    },
    'design': {
        'name': 'Design Agent',
        'icon': '🎨',
        'description': 'Creates thumbnails and visual assets'
    },
    'research': {
        'name': 'Research Agent',
        'icon': '🔍',
        'description': 'Researches trends and competitor strategies'
    },
    'persona': {
        'name': 'Persona Agent',
        'icon': '👤',
        'description': 'Manages persona data and assets'
    },
    'strategy': {
        'name': 'Strategy Agent',
        'icon': '🎯',
        'description': 'Optimizes content strategy and planning'
    }
}


def get_agent_type_for_capability(capability_name: str) -> str:
    """
    Return which agent type should handle this capability

    Args:
        capability_name: Name of the capability (e.g., 'write_video_script')

    Returns:
        Agent type (e.g., 'script') or None if Sarah handles it directly
    """
    return CAPABILITY_AGENT_MAP.get(capability_name)


def get_capabilities_for_agent_type(agent_type: str) -> list:
    """
    Return all capabilities that belong to this agent type

    Args:
        agent_type: Type of agent (e.g., 'script', 'video_editing')

    Returns:
        List of capability names for this agent type
    """
    return [
        cap for cap, atype in CAPABILITY_AGENT_MAP.items()
        if atype == agent_type
    ]


def get_agent_metadata(agent_type: str) -> dict:
    """
    Get metadata for an agent type (name, icon, description)

    Args:
        agent_type: Type of agent (e.g., 'script')

    Returns:
        Dictionary with name, icon, description
    """
    return AGENT_METADATA.get(agent_type, {
        'name': f'{agent_type.title()} Agent',
        'icon': '🤖',
        'description': f'Handles {agent_type} tasks'
    })


def get_all_agent_types() -> list:
    """
    Get list of all possible agent types

    Returns:
        List of agent type strings
    """
    return list(AGENT_METADATA.keys())


# Example usage
if __name__ == "__main__":
    print("🤖 Agent Capability Mapping\n")

    # Show what each agent type can do
    for agent_type in get_all_agent_types():
        metadata = get_agent_metadata(agent_type)
        caps = get_capabilities_for_agent_type(agent_type)

        print(f"{metadata['icon']} {metadata['name']}")
        print(f"   {metadata['description']}")
        print(f"   Capabilities: {len(caps)}")
        print(f"   Examples: {', '.join(caps[:3])}")
        print()

    # Test reverse lookup
    print("\n🔍 Reverse Lookup Test:")
    test_caps = ['write_video_script', 'moviepy_composite_video', 'youtube_analytics_fetch']
    for cap in test_caps:
        agent = get_agent_type_for_capability(cap)
        print(f"   {cap} → {agent}")
