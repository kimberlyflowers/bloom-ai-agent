"""
PLATFORM-AWARE CLICKING SYSTEM
Intelligent router that uses the right method for each platform

For YouTube: Direct navigation instead of clicking
For other sites: Reliable DOM-based clicking
"""

import asyncio
import logging
import re
from typing import Optional, Dict
from playwright.async_api import Page

logger = logging.getLogger(__name__)


class YouTubeNavigator:
    """
    YouTube-specific navigation - NO MORE COORDINATE CLICKING!
    Uses direct URL navigation for 100% reliability
    """

    @staticmethod
    async def navigate_to_video(page: Page, description: str) -> Dict:
        """
        Extract video title from description and navigate directly

        Args:
            page: Playwright page object
            description: User's intent (e.g., "click first video", "play TikTok Algorithm video")

        Returns:
            dict with success status and method used
        """
        try:
            current_url = page.url

            # STRATEGY 1: If we're on YouTube search results, extract video URL from DOM
            if 'youtube.com/results' in current_url or 'youtube.com' in current_url:
                logger.info(f"🎬 YouTube detected - Using direct navigation for: {description}")

                # Extract video links from search results
                video_selector = 'a#video-title'
                videos = await page.query_selector_all(video_selector)

                if not videos:
                    # Try alternate selector
                    video_selector = 'ytd-video-renderer a#thumbnail'
                    videos = await page.query_selector_all(video_selector)

                if videos:
                    # Determine which video to click based on description
                    video_index = YouTubeNavigator._parse_video_index(description)

                    if video_index < len(videos):
                        video_element = videos[video_index]
                        video_url = await video_element.get_attribute('href')

                        if video_url:
                            # Make absolute URL
                            if video_url.startswith('/'):
                                video_url = f"https://www.youtube.com{video_url}"

                            logger.info(f"✅ Navigating directly to video: {video_url}")
                            await page.goto(video_url, wait_until='networkidle', timeout=30000)

                            return {
                                'success': True,
                                'method': 'youtube_direct_navigation',
                                'message': f'Navigated to video #{video_index + 1}',
                                'url': video_url
                            }

                # STRATEGY 2: Search YouTube directly if we couldn't find videos
                video_title = YouTubeNavigator._extract_video_title(description)
                if video_title:
                    search_url = f"https://www.youtube.com/results?search_query={video_title.replace(' ', '+')}"
                    logger.info(f"🔍 Searching YouTube for: {video_title}")
                    await page.goto(search_url, wait_until='networkidle', timeout=30000)

                    # Wait for results and click first video
                    await page.wait_for_selector('a#video-title', timeout=10000)
                    videos = await page.query_selector_all('a#video-title')

                    if videos:
                        video_url = await videos[0].get_attribute('href')
                        if video_url:
                            if video_url.startswith('/'):
                                video_url = f"https://www.youtube.com{video_url}"

                            logger.info(f"✅ Found video, navigating to: {video_url}")
                            await page.goto(video_url, wait_until='networkidle', timeout=30000)

                            return {
                                'success': True,
                                'method': 'youtube_search_navigation',
                                'message': f'Searched and navigated to: {video_title}',
                                'url': video_url
                            }

            return {
                'success': False,
                'message': 'Could not extract video URL from YouTube page'
            }

        except Exception as e:
            logger.error(f"❌ YouTube navigation failed: {e}")
            return {
                'success': False,
                'message': f'YouTube navigation error: {str(e)}'
            }

    @staticmethod
    def _parse_video_index(description: str) -> int:
        """
        Parse video index from description

        "first video" -> 0
        "second video" -> 1
        "third video" -> 2
        "click video 3" -> 2
        Default: 0 (first video)
        """
        description_lower = description.lower()

        # Check for ordinal numbers
        ordinals = {
            'first': 0, '1st': 0,
            'second': 1, '2nd': 1,
            'third': 2, '3rd': 2,
            'fourth': 3, '4th': 3,
            'fifth': 4, '5th': 4
        }

        for ordinal, index in ordinals.items():
            if ordinal in description_lower:
                return index

        # Check for numeric patterns (e.g., "video 3", "click 2")
        number_match = re.search(r'\b(\d+)\b', description)
        if number_match:
            num = int(number_match.group(1))
            return num - 1  # Convert to 0-indexed

        # Default to first video
        return 0

    @staticmethod
    def _extract_video_title(description: str) -> Optional[str]:
        """
        Extract video title from description

        "click TikTok Algorithm video" -> "TikTok Algorithm"
        "play video about python" -> "python"
        """
        # Remove common action words
        clean_desc = description.lower()
        for word in ['click', 'play', 'open', 'watch', 'video', 'the', 'a', 'first', 'second', 'third']:
            clean_desc = clean_desc.replace(word, ' ')

        clean_desc = ' '.join(clean_desc.split())  # Remove extra spaces
        return clean_desc if clean_desc else None


class IntelligentClickRouter:
    """
    Platform-aware click router that chooses the right method for each situation
    """

    def __init__(self, page: Page):
        self.page = page
        self.youtube_navigator = YouTubeNavigator()

    async def click(self, description: str, safe_clicker=None, universal_locator=None) -> Dict:
        """
        Intelligent routing based on platform and intent

        Args:
            description: What to click
            safe_clicker: SafeClicking instance (optional)
            universal_locator: UniversalElementLocator instance (optional)

        Returns:
            dict with success status and method used
        """
        current_url = self.page.url
        description_lower = description.lower()

        # ROUTE 1: YouTube video navigation
        if self._is_youtube_video_intent(current_url, description_lower):
            logger.info(f"🎬 INTELLIGENT ROUTER: Detected YouTube video click -> Using direct navigation")
            return await self.youtube_navigator.navigate_to_video(self.page, description)

        # ROUTE 2: Search box / form inputs (already works reliably)
        if self._is_search_intent(description_lower):
            logger.info(f"🔍 INTELLIGENT ROUTER: Search intent detected -> Using DOM method")
            if safe_clicker:
                result = await safe_clicker.click_element(self.page, description, timeout=8000)
                if result.get('success'):
                    return {**result, 'router': 'search_dom'}

        # ROUTE 3: Regular DOM clicking (for buttons, links, etc.)
        if safe_clicker:
            logger.info(f"🎯 INTELLIGENT ROUTER: Regular click -> Using SafeClicking")
            result = await safe_clicker.click_element(self.page, description, timeout=8000)
            if result.get('success'):
                return {**result, 'router': 'safe_clicker'}

        # ROUTE 4: Fallback to universal locator (vision-based) - last resort
        # NOTE: This may still have coordinate issues until viewport fix is tested
        logger.info(f"👁️ INTELLIGENT ROUTER: DOM failed -> Falling back to vision-based locator")
        return {
            'success': False,
            'message': 'DOM methods failed, vision-based clicking may have coordinate issues',
            'router': 'fallback_needed'
        }

    @staticmethod
    def _is_youtube_video_intent(url: str, description: str) -> bool:
        """
        Check if this is a YouTube video click intent (navigating TO a video)
        NOT clicking elements WITHIN a video (like skip button, play button, etc.)
        """
        is_youtube = 'youtube.com' in url

        # Exclude if clicking buttons/elements WITHIN a video
        within_video_patterns = [
            'skip', 'button', 'ad', 'play button', 'pause', 'settings',
            'quality', 'speed', 'caption', 'fullscreen', 'volume'
        ]
        if any(pattern in description for pattern in within_video_patterns):
            return False

        # Only match if it's clearly clicking ON/AT a video (to navigate)
        video_click_patterns = [
            'first video', 'second video', 'third video', 'fourth video', 'fifth video',
            'video 1', 'video 2', 'video 3', 'video 4', 'video 5',
            'video titled', 'video about', 'click video', 'play video',
            'watch video', 'thumbnail', 'click thumbnail'
        ]
        is_video_click = any(pattern in description for pattern in video_click_patterns)

        return is_youtube and is_video_click

    @staticmethod
    def _is_search_intent(description: str) -> bool:
        """Check if this is a search box click intent"""
        return any(word in description for word in [
            'search', 'search box', 'search bar', 'input', 'type in'
        ])
