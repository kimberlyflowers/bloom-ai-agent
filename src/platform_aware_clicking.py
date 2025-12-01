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
    async def skip_ad_if_present(page: Page) -> Dict:
        """
        Automatically skip YouTube ads (human behavior!)

        Detects if an ad is playing and clicks "Skip Ad" as soon as available.
        Waits out unskippable ads gracefully.

        Args:
            page: Playwright page object

        Returns:
            dict with status and actions taken
        """
        try:
            logger.info("🎬 Checking for YouTube ads...")

            # Wait a moment for page to load
            await asyncio.sleep(1)

            # DETECTION: Check if an ad is playing
            ad_indicators = [
                '.ytp-ad-player-overlay',  # Ad overlay
                '.ytp-ad-text',            # "Ad" text in player
                '.video-ads.ytp-ad-module', # Ad container
                '.ytp-ad-preview-container' # Ad preview
            ]

            ad_detected = False
            for indicator in ad_indicators:
                ad_element = await page.query_selector(indicator)
                if ad_element:
                    # Check if it's visible
                    is_visible = await ad_element.is_visible()
                    if is_visible:
                        ad_detected = True
                        logger.info(f"📺 Ad detected via: {indicator}")
                        break

            if not ad_detected:
                logger.info("✅ No ad detected - video playing")
                return {
                    'success': True,
                    'ad_detected': False,
                    'message': 'No ad present, video is playing'
                }

            # AD DETECTED - Try to skip it
            logger.info("⏳ Ad is playing - waiting for skip button...")

            # Skip button selectors (YouTube uses different ones)
            skip_button_selectors = [
                '.ytp-ad-skip-button',
                '.ytp-skip-ad-button',
                'button.ytp-ad-skip-button-modern',
                '.ytp-ad-skip-button-container button',
                'button[class*="skip"]'
            ]

            # Wait up to 6 seconds for skip button to appear
            skip_button_found = False
            skip_button = None
            skip_selector_used = None

            for attempt in range(12):  # 12 attempts × 0.5s = 6 seconds
                for selector in skip_button_selectors:
                    skip_button = await page.query_selector(selector)
                    if skip_button:
                        # Check if visible and enabled
                        is_visible = await skip_button.is_visible()
                        is_enabled = await skip_button.is_enabled()

                        if is_visible and is_enabled:
                            skip_button_found = True
                            skip_selector_used = selector
                            logger.info(f"✅ Skip button found: {selector}")
                            break

                if skip_button_found:
                    break

                # Wait 0.5 seconds before next check
                await asyncio.sleep(0.5)

            if skip_button_found and skip_button:
                # CLICK SKIP BUTTON IMMEDIATELY (human behavior!)
                logger.info("🖱️ Clicking 'Skip Ad' button NOW...")
                await skip_button.click()

                # Wait for ad to disappear
                await asyncio.sleep(1)

                # Verify ad is gone
                ad_still_present = False
                for indicator in ad_indicators:
                    ad_element = await page.query_selector(indicator)
                    if ad_element:
                        is_visible = await ad_element.is_visible()
                        if is_visible:
                            ad_still_present = True
                            break

                if not ad_still_present:
                    logger.info("✅ Ad skipped successfully! Video is now playing")
                    return {
                        'success': True,
                        'ad_detected': True,
                        'ad_skipped': True,
                        'message': 'Ad skipped successfully',
                        'skip_button_selector': skip_selector_used
                    }
                else:
                    logger.warning("⚠️ Skip button clicked but ad still present (possibly second ad)")
                    return {
                        'success': True,
                        'ad_detected': True,
                        'ad_skipped': 'partial',
                        'message': 'Skip button clicked, but another ad may be playing'
                    }

            else:
                # No skip button found after 6 seconds - unskippable ad
                logger.info("⏰ No skip button found - This is an UNSKIPPABLE ad")
                logger.info("⏳ Waiting for ad to finish (max 20 seconds)...")

                # Wait for ad to finish (check every 2 seconds, max 20 seconds)
                for wait_attempt in range(10):  # 10 × 2s = 20 seconds max
                    await asyncio.sleep(2)

                    # Check if ad is still playing
                    ad_still_playing = False
                    for indicator in ad_indicators:
                        ad_element = await page.query_selector(indicator)
                        if ad_element:
                            is_visible = await ad_element.is_visible()
                            if is_visible:
                                ad_still_playing = True
                                break

                    if not ad_still_playing:
                        logger.info(f"✅ Unskippable ad finished after ~{(wait_attempt + 1) * 2} seconds")
                        return {
                            'success': True,
                            'ad_detected': True,
                            'ad_skipped': False,
                            'ad_type': 'unskippable',
                            'wait_time': (wait_attempt + 1) * 2,
                            'message': 'Waited for unskippable ad to finish'
                        }

                # Ad still playing after 20 seconds - give up and return
                logger.warning("⚠️ Ad still playing after 20 seconds - continuing anyway")
                return {
                    'success': True,
                    'ad_detected': True,
                    'ad_skipped': False,
                    'ad_type': 'long_unskippable',
                    'message': 'Ad still playing after 20s timeout'
                }

        except Exception as e:
            logger.error(f"❌ Ad skip error: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Ad skip failed: {e}'
            }

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

                            # AUTOMATICALLY SKIP ADS (human behavior!)
                            ad_result = await YouTubeNavigator.skip_ad_if_present(page)

                            return {
                                'success': True,
                                'method': 'youtube_direct_navigation',
                                'message': f'Navigated to video #{video_index + 1}',
                                'url': video_url,
                                'ad_handling': ad_result
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

                            # AUTOMATICALLY SKIP ADS (human behavior!)
                            ad_result = await YouTubeNavigator.skip_ad_if_present(page)

                            return {
                                'success': True,
                                'method': 'youtube_search_navigation',
                                'message': f'Searched and navigated to: {video_title}',
                                'url': video_url,
                                'ad_handling': ad_result
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
