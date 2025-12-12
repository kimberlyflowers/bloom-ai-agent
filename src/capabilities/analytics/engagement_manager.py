"""
Engagement & Analytics Capabilities (9 total)

Track performance and engage with audience:
1. youtube_analytics_fetch - Get YouTube video analytics
2. tiktok_analytics_fetch - Get TikTok video analytics
3. instagram_insights_fetch - Get Instagram Reel insights
4. comment_moderation - Moderate comments (delete spam)
5. auto_reply_comments - Auto-reply to comments
6. dm_response - Respond to DMs
7. track_engagement_metrics - Track aggregate metrics
8. generate_performance_report - Weekly/monthly reports
9. identify_top_performing_content - Find best videos
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from ..foundation.core_utilities import http_request, get_database_manager

logger = logging.getLogger(__name__)


# ============================================================================
# 1-3. ANALYTICS APIs
# ============================================================================

async def youtube_analytics_fetch(
    video_id: str,
    access_token: str
) -> Dict[str, Any]:
    """Fetch YouTube video analytics"""
    try:
        api_endpoint = f"https://youtubeanalytics.googleapis.com/v2/reports"

        headers = {"Authorization": f"Bearer {access_token}"}

        params = {
            "ids": f"channel==MINE",
            "startDate": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "endDate": datetime.now().strftime("%Y-%m-%d"),
            "metrics": "views,likes,comments,shares,estimatedMinutesWatched,averageViewDuration",
            "filters": f"video=={video_id}"
        }

        result = await http_request("GET", api_endpoint, headers=headers, params=params)

        if not result["success"]:
            raise Exception(f"YouTube analytics failed: {result['body']}")

        rows = result["body"].get("rows", [[]])[0]
        columns = result["body"].get("columnHeaders", [])

        analytics = {col["name"]: rows[i] for i, col in enumerate(columns)}

        logger.info(f"✅ YouTube analytics fetched: {video_id}")
        return {"success": True, "video_id": video_id, **analytics}

    except Exception as e:
        logger.error(f"❌ YouTube analytics failed: {e}")
        return {"success": False, "error": str(e)}


async def tiktok_analytics_fetch(
    video_id: str,
    access_token: str
) -> Dict[str, Any]:
    """Fetch TikTok video analytics"""
    try:
        api_endpoint = f"https://open.tiktokapis.com/v2/research/video/query/"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        data = {
            "query": {
                "and": [{"field_name": "video_id", "field_values": [video_id]}]
            },
            "fields": ["like_count", "comment_count", "share_count", "view_count"]
        }

        result = await http_request("POST", api_endpoint, headers=headers, json_data=data)

        if not result["success"]:
            raise Exception(f"TikTok analytics failed: {result['body']}")

        video_data = result["body"]["data"]["videos"][0]

        logger.info(f"✅ TikTok analytics fetched: {video_id}")
        return {
            "success": True,
            "video_id": video_id,
            "views": video_data.get("view_count", 0),
            "likes": video_data.get("like_count", 0),
            "comments": video_data.get("comment_count", 0),
            "shares": video_data.get("share_count", 0)
        }

    except Exception as e:
        logger.error(f"❌ TikTok analytics failed: {e}")
        return {"success": False, "error": str(e)}


async def instagram_insights_fetch(
    media_id: str,
    access_token: str
) -> Dict[str, Any]:
    """Fetch Instagram Reel insights"""
    try:
        api_endpoint = f"https://graph.facebook.com/v18.0/{media_id}/insights"

        params = {
            "metric": "plays,likes,comments,shares,saved,reach",
            "access_token": access_token
        }

        result = await http_request("GET", api_endpoint, params=params)

        if not result["success"]:
            raise Exception(f"Instagram insights failed: {result['body']}")

        data = result["body"]["data"]
        insights = {item["name"]: item["values"][0]["value"] for item in data}

        logger.info(f"✅ Instagram insights fetched: {media_id}")
        return {"success": True, "media_id": media_id, **insights}

    except Exception as e:
        logger.error(f"❌ Instagram insights failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 4-6. ENGAGEMENT
# ============================================================================

async def comment_moderation(
    platform: str,
    video_id: str,
    action: str = "filter_spam",
    access_token: str = None
) -> Dict[str, Any]:
    """Moderate comments (delete spam)"""
    try:
        # Fetch comments
        if platform == "youtube":
            api_endpoint = "https://www.googleapis.com/youtube/v3/commentThreads"
            params = {"part": "snippet", "videoId": video_id, "access_token": access_token}
            result = await http_request("GET", api_endpoint, params=params)

            comments = result["body"].get("items", [])
            spam_count = 0

            for comment in comments:
                text = comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                # Simple spam detection
                if _is_spam(text):
                    comment_id = comment["id"]
                    # Delete spam
                    delete_endpoint = f"https://www.googleapis.com/youtube/v3/comments?id={comment_id}"
                    await http_request("DELETE", delete_endpoint, headers={"Authorization": f"Bearer {access_token}"})
                    spam_count += 1

            logger.info(f"✅ Comment moderation complete: {spam_count} spam removed")
            return {"success": True, "spam_removed": spam_count}

    except Exception as e:
        logger.error(f"❌ Comment moderation failed: {e}")
        return {"success": False, "error": str(e)}


def _is_spam(text: str) -> bool:
    """Simple spam detection"""
    spam_keywords = ["check out my", "click here", "free money", "subscribe to me", "dm for"]
    return any(keyword in text.lower() for keyword in spam_keywords)


async def auto_reply_comments(
    platform: str,
    video_id: str,
    access_token: str,
    anthropic_api_key: str
) -> Dict[str, Any]:
    """Auto-reply to comments"""
    try:
        # Fetch recent comments
        if platform == "youtube":
            api_endpoint = "https://www.googleapis.com/youtube/v3/commentThreads"
            params = {"part": "snippet", "videoId": video_id, "maxResults": 20}
            headers = {"Authorization": f"Bearer {access_token}"}
            result = await http_request("GET", api_endpoint, params=params, headers=headers)

            comments = result["body"].get("items", [])
            replied_count = 0

            for comment in comments:
                comment_text = comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comment_id = comment["snippet"]["topLevelComment"]["id"]

                # Generate reply
                import anthropic
                client = anthropic.Anthropic(api_key=anthropic_api_key)

                response = await asyncio.to_thread(
                    client.messages.create,
                    model="claude-3-5-haiku-20241022",
                    max_tokens=100,
                    messages=[{
                        "role": "user",
                        "content": f"Generate a friendly, helpful reply to this comment: '{comment_text}'. Be authentic and conversational. 1-2 sentences max."
                    }]
                )

                reply = response.content[0].text.strip()

                # Post reply
                reply_endpoint = "https://www.googleapis.com/youtube/v3/comments?part=snippet"
                reply_data = {
                    "snippet": {
                        "parentId": comment_id,
                        "textOriginal": reply
                    }
                }

                await http_request("POST", reply_endpoint, headers=headers, json_data=reply_data)
                replied_count += 1

            logger.info(f"✅ Auto-replied to {replied_count} comments")
            return {"success": True, "replies_sent": replied_count}

    except Exception as e:
        logger.error(f"❌ Auto-reply failed: {e}")
        return {"success": False, "error": str(e)}


async def dm_response(
    platform: str,
    message_id: str,
    message_text: str,
    access_token: str,
    anthropic_api_key: str
) -> Dict[str, Any]:
    """Respond to DMs"""
    try:
        # Generate response
        import anthropic
        client = anthropic.Anthropic(api_key=anthropic_api_key)

        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-sonnet-4-5-20250929",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": f"Generate a helpful, friendly DM response to: '{message_text}'. Be professional but warm. Answer questions about BLOOM if relevant."
            }]
        )

        reply = response.content[0].text.strip()

        logger.info(f"✅ DM response generated")
        return {"success": True, "reply": reply}

    except Exception as e:
        logger.error(f"❌ DM response failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# 7-9. REPORTING
# ============================================================================

async def track_engagement_metrics(
    persona_id: str,
    time_range: str = "7d"
) -> Dict[str, Any]:
    """Track aggregate engagement metrics"""
    try:
        db = get_database_manager()

        # Query content library for recent videos
        days = int(time_range.replace('d', ''))
        query = """
            SELECT SUM(views) as total_views, SUM(likes) as total_likes,
                   SUM(comments) as total_comments, COUNT(*) as video_count
            FROM persona_content_library
            WHERE persona_id = ? AND created_at >= datetime('now', '-{} days')
        """.format(days)

        result = await db.database_query(query, (persona_id,), fetch_one=True)

        logger.info(f"✅ Engagement metrics tracked: {persona_id}")
        return {
            "success": True,
            "persona_id": persona_id,
            "time_range": time_range,
            **result
        }

    except Exception as e:
        logger.error(f"❌ Engagement tracking failed: {e}")
        return {"success": False, "error": str(e)}


async def generate_performance_report(
    persona_id: str,
    report_type: str = "weekly"
) -> Dict[str, Any]:
    """Generate performance report"""
    try:
        days = 7 if report_type == "weekly" else 30

        # Get metrics
        metrics = await track_engagement_metrics(persona_id, f"{days}d")

        if not metrics["success"]:
            return metrics

        # Calculate growth
        prev_metrics = await track_engagement_metrics(persona_id, f"{days*2}d")

        growth = {}
        for key in ["total_views", "total_likes", "total_comments"]:
            current = metrics.get(key, 0)
            previous = prev_metrics.get(key, 0)
            if previous > 0:
                growth[key] = ((current - previous) / previous) * 100

        report = {
            "success": True,
            "persona_id": persona_id,
            "report_type": report_type,
            "period": f"Last {days} days",
            "metrics": metrics,
            "growth": growth,
            "generated_at": datetime.now().isoformat()
        }

        logger.info(f"✅ Performance report generated: {persona_id}")
        return report

    except Exception as e:
        logger.error(f"❌ Performance report failed: {e}")
        return {"success": False, "error": str(e)}


async def identify_top_performing_content(
    persona_id: str,
    metric: str = "views",
    limit: int = 10
) -> Dict[str, Any]:
    """Find best performing videos"""
    try:
        db = get_database_manager()

        query = f"""
            SELECT video_url, title, {metric}, created_at, platform
            FROM persona_content_library
            WHERE persona_id = ?
            ORDER BY {metric} DESC
            LIMIT ?
        """

        result = await db.database_query(query, (persona_id, limit))

        logger.info(f"✅ Top content identified: {len(result)} videos")
        return {
            "success": True,
            "persona_id": persona_id,
            "metric": metric,
            "top_content": result
        }

    except Exception as e:
        logger.error(f"❌ Top content identification failed: {e}")
        return {"success": False, "error": str(e)}
