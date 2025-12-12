"""
Content Research Capabilities (5 total)

Research capabilities for viral content creation:
1. trending_topics_research - Discover trending topics in niche
2. competitor_analysis - Analyze top-performing competitor content
3. keyword_research - Find high-performing keywords/hashtags
4. content_gap_analysis - Identify untapped content opportunities
5. generate_video_ideas - Generate 10+ video ideas from trends
"""

import anthropic
import asyncio
import logging
from typing import Dict, List, Any, Optional
from ..foundation.core_utilities import http_request

logger = logging.getLogger(__name__)


# ============================================================================
# 1. TRENDING_TOPICS_RESEARCH
# ============================================================================

async def trending_topics_research(
    niche: str,
    platform: str = "tiktok",
    time_range: str = "7d",
    anthropic_api_key: str = None
) -> Dict[str, Any]:
    """
    Research trending topics in a specific niche

    Args:
        niche: Content niche (e.g., "creator economy", "AI tools", "beauty")
        platform: "tiktok", "youtube", "instagram"
        time_range: "24h", "7d", "30d"
        anthropic_api_key: Anthropic API key

    Returns:
        {
            "success": true,
            "trending_topics": [
                {"topic": "AI content tools", "trend_score": 95, "volume": "1.2M"},
                {"topic": "Creator burnout", "trend_score": 82, "volume": "500K"},
                ...
            ],
            "recommendations": ["Focus on AI automation", ...]
        }
    """
    try:
        client = anthropic.Anthropic(api_key=anthropic_api_key)

        prompt = f"""Research trending topics in the {niche} niche on {platform} over the past {time_range}.

Analyze:
- What topics are gaining traction?
- What questions are people asking?
- What problems need solving?
- What content gaps exist?

Return JSON format:
{{
  "trending_topics": [
    {{
      "topic": "Topic name",
      "trend_score": 0-100,
      "estimated_volume": "Volume estimate",
      "why_trending": "Brief explanation",
      "content_angles": ["Angle 1", "Angle 2"]
    }}
  ],
  "recommendations": ["Strategic recommendation 1", ...]
}}

Research comprehensively and return ONLY valid JSON."""

        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        result_text = response.content[0].text.strip()

        # Clean JSON
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
            result_text = result_text.strip()

        data = json.loads(result_text)

        logger.info(f"✅ Trending topics researched: {len(data.get('trending_topics', []))} topics")
        return {
            "success": True,
            "niche": niche,
            "platform": platform,
            **data
        }

    except Exception as e:
        logger.error(f"❌ Trending topics research failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 2. COMPETITOR_ANALYSIS
# ============================================================================

async def competitor_analysis(
    competitor_accounts: List[str],
    platform: str = "tiktok",
    anthropic_api_key: str = None
) -> Dict[str, Any]:
    """
    Analyze top-performing competitor content

    Args:
        competitor_accounts: List of competitor usernames
        platform: "tiktok", "youtube", "instagram"
        anthropic_api_key: Anthropic API key

    Returns:
        {
            "success": true,
            "insights": {
                "content_themes": [...],
                "posting_frequency": "3-5x/day",
                "engagement_patterns": {...},
                "winning_formats": [...]
            },
            "opportunities": [...]
        }
    """
    try:
        client = anthropic.Anthropic(api_key=anthropic_api_key)

        competitors_str = ", ".join(competitor_accounts)

        prompt = f"""Analyze these {platform} competitor accounts: {competitors_str}

Analyze:
1. Content themes and topics they cover
2. Posting frequency and timing
3. Video formats (length, style, structure)
4. Engagement patterns (what gets most views/likes)
5. Content gaps they're NOT covering
6. What we can do better

Return JSON format:
{{
  "insights": {{
    "content_themes": ["Theme 1", "Theme 2", ...],
    "posting_frequency": "Description",
    "video_lengths": "Average length",
    "winning_formats": ["Format 1", ...],
    "engagement_drivers": ["Driver 1", ...]
  }},
  "opportunities": [
    {{
      "opportunity": "Description",
      "why": "Reasoning",
      "estimated_impact": "high|medium|low"
    }}
  ],
  "recommendations": ["Actionable recommendation 1", ...]
}}

Analyze strategically and return ONLY valid JSON."""

        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-sonnet-4-5-20250929",
            max_tokens=2500,
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        result_text = response.content[0].text.strip()

        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
            result_text = result_text.strip()

        data = json.loads(result_text)

        logger.info(f"✅ Competitor analysis complete: {len(competitor_accounts)} accounts")
        return {
            "success": True,
            "competitors": competitor_accounts,
            "platform": platform,
            **data
        }

    except Exception as e:
        logger.error(f"❌ Competitor analysis failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 3. KEYWORD_RESEARCH
# ============================================================================

async def keyword_research(
    seed_keywords: List[str],
    platform: str = "tiktok",
    anthropic_api_key: str = None
) -> Dict[str, Any]:
    """
    Research high-performing keywords and hashtags

    Args:
        seed_keywords: Starting keywords (e.g., ["AI tools", "creator tips"])
        platform: Target platform
        anthropic_api_key: Anthropic API key

    Returns:
        {
            "success": true,
            "keywords": [
                {"keyword": "#AItools", "volume": "high", "competition": "medium"},
                ...
            ],
            "hashtag_strategy": {...}
        }
    """
    try:
        client = anthropic.Anthropic(api_key=anthropic_api_key)

        keywords_str = ", ".join(seed_keywords)

        prompt = f"""Research keywords and hashtags for {platform} based on: {keywords_str}

Find:
1. High-volume, low-competition keywords
2. Trending hashtags related to these topics
3. Long-tail keyword opportunities
4. Semantic variations people actually search

Return JSON format:
{{
  "keywords": [
    {{
      "keyword": "Keyword/hashtag",
      "volume_estimate": "high|medium|low",
      "competition": "high|medium|low",
      "opportunity_score": 0-100,
      "why_use": "Reason"
    }}
  ],
  "hashtag_strategy": {{
    "primary_hashtags": ["#hashtag1", "#hashtag2"],
    "secondary_hashtags": ["#hashtag3", ...],
    "niche_hashtags": ["#niche1", ...]
  }},
  "keyword_clusters": [
    {{
      "cluster_theme": "Theme name",
      "keywords": ["kw1", "kw2", ...]
    }}
  ]
}}

Research comprehensively and return ONLY valid JSON."""

        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        result_text = response.content[0].text.strip()

        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
            result_text = result_text.strip()

        data = json.loads(result_text)

        logger.info(f"✅ Keyword research complete: {len(data.get('keywords', []))} keywords")
        return {
            "success": True,
            "seed_keywords": seed_keywords,
            "platform": platform,
            **data
        }

    except Exception as e:
        logger.error(f"❌ Keyword research failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 4. CONTENT_GAP_ANALYSIS
# ============================================================================

async def content_gap_analysis(
    niche: str,
    our_content_themes: List[str],
    anthropic_api_key: str = None
) -> Dict[str, Any]:
    """
    Identify untapped content opportunities

    Args:
        niche: Content niche
        our_content_themes: Themes we've already covered
        anthropic_api_key: Anthropic API key

    Returns:
        {
            "success": true,
            "content_gaps": [
                {
                    "gap": "Tutorial content",
                    "opportunity_size": "large",
                    "difficulty": "medium",
                    "suggested_videos": [...]
                }
            ]
        }
    """
    try:
        client = anthropic.Anthropic(api_key=anthropic_api_key)

        themes_str = ", ".join(our_content_themes)

        prompt = f"""Identify content gaps in the {niche} niche.

We've covered: {themes_str}

Find gaps:
1. Topics competitors cover but we don't
2. Questions audience asks but aren't answered
3. Underserved sub-niches
4. Format opportunities (tutorials, behind-scenes, etc.)
5. Trending topics we haven't addressed

Return JSON format:
{{
  "content_gaps": [
    {{
      "gap_category": "Category name",
      "gap_description": "Detailed description",
      "opportunity_size": "large|medium|small",
      "difficulty": "easy|medium|hard",
      "audience_demand": "high|medium|low",
      "suggested_videos": [
        {{
          "title": "Video title",
          "angle": "Content angle",
          "estimated_views": "Estimate"
        }}
      ]
    }}
  ],
  "priority_gaps": ["Gap 1 to tackle first", "Gap 2", ...],
  "quick_wins": ["Easy gap to fill quickly", ...]
}}

Analyze strategically and return ONLY valid JSON."""

        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-sonnet-4-5-20250929",
            max_tokens=2500,
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        result_text = response.content[0].text.strip()

        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
            result_text = result_text.strip()

        data = json.loads(result_text)

        logger.info(f"✅ Content gap analysis complete: {len(data.get('content_gaps', []))} gaps identified")
        return {
            "success": True,
            "niche": niche,
            **data
        }

    except Exception as e:
        logger.error(f"❌ Content gap analysis failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 5. GENERATE_VIDEO_IDEAS
# ============================================================================

async def generate_video_ideas(
    topic: str = None,
    trending_topics: List[str] = None,
    count: int = 10,
    platform: str = "tiktok",
    anthropic_api_key: str = None
) -> Dict[str, Any]:
    """
    Generate video ideas from trends and topics

    Args:
        topic: Specific topic (optional)
        trending_topics: List of trending topics (optional)
        count: Number of ideas to generate
        platform: Target platform
        anthropic_api_key: Anthropic API key

    Returns:
        {
            "success": true,
            "video_ideas": [
                {
                    "title": "Video title",
                    "hook": "First 3 seconds",
                    "angle": "Content angle",
                    "estimated_performance": "high|medium|low",
                    "reasoning": "Why this will work"
                }
            ]
        }
    """
    try:
        client = anthropic.Anthropic(api_key=anthropic_api_key)

        context = ""
        if topic:
            context = f"Main topic: {topic}\n"
        if trending_topics:
            context += f"Trending topics: {', '.join(trending_topics)}\n"

        prompt = f"""Generate {count} viral video ideas for {platform}.

{context}

Each idea should:
- Have strong viral potential
- Be unique and attention-grabbing
- Fit {platform}'s algorithm
- Be actionable and specific
- Include a proven content angle

Return JSON format:
{{
  "video_ideas": [
    {{
      "title": "Compelling video title",
      "hook": "First 3 seconds that grab attention",
      "content_angle": "Educational|Testimonial|Behind-scenes|Trending|etc",
      "key_points": ["Point 1", "Point 2", "Point 3"],
      "estimated_duration": "15s|30s|60s",
      "estimated_performance": "high|medium",
      "reasoning": "Why this will perform well",
      "cta": "Call to action",
      "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"]
    }}
  ]
}}

Generate {count} diverse, high-potential ideas and return ONLY valid JSON."""

        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-sonnet-4-5-20250929",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        result_text = response.content[0].text.strip()

        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
            result_text = result_text.strip()

        data = json.loads(result_text)

        logger.info(f"✅ Video ideas generated: {len(data.get('video_ideas', []))} ideas")
        return {
            "success": True,
            "count": len(data.get('video_ideas', [])),
            "platform": platform,
            **data
        }

    except Exception as e:
        logger.error(f"❌ Video idea generation failed: {e}")
        return {"success": False, "error": str(e)}
