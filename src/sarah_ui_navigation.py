"""
SARAH'S UI NAVIGATION SYSTEM
Advanced mouse and keyboard interactions for YouTube and complex UIs

This adds human-like UI navigation:
- Mouse hover
- Smooth mouse movement
- Double click
- Right click
- Drag and drop
- Scroll to element
- Wait and interact patterns

Works with Sarah's vision to navigate ANY UI like a human!
"""

import asyncio
import random
from playwright.async_api import Page
from typing import Optional, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class UINavigator:
    """
    Sarah's advanced UI navigation - mouse, keyboard, and human-like patterns

    This gives Sarah the ability to:
    - Hover over elements (YouTube thumbnails, buttons)
    - Move mouse smoothly (looks human, not robotic)
    - Double click, right click
    - Drag and drop
    - Scroll to make elements visible
    - Wait for elements before interacting
    """

    async def hover(self, page: Page, selector: str = None, x: int = None, y: int = None,
                   smooth: bool = True, duration: float = 0.5) -> Dict[str, Any]:
        """
        Hover over an element or coordinates

        Args:
            page: Playwright page
            selector: CSS selector to hover over (e.g., "video", ".thumbnail")
            x, y: Coordinates to hover over (if no selector)
            smooth: Use smooth human-like movement
            duration: How long to take moving (seconds)

        Returns:
            Result dict

        Examples:
            # Hover over a video thumbnail
            await hover(page, selector="ytd-thumbnail")

            # Hover at specific coordinates
            await hover(page, x=500, y=300)
        """
        if not page:
            return {'success': False, 'message': 'No page available'}

        try:
            # Get target coordinates
            if selector:
                # Find element and get its center
                element = page.locator(selector).first
                box = await element.bounding_box()
                if not box:
                    return {'success': False, 'message': f'Element not found: {selector}'}
                target_x = box['x'] + box['width'] / 2
                target_y = box['y'] + box['height'] / 2
            elif x is not None and y is not None:
                target_x = x
                target_y = y
            else:
                return {'success': False, 'message': 'Must provide selector or coordinates'}

            if smooth:
                # Smooth human-like mouse movement
                await self._smooth_mouse_move(page, target_x, target_y, duration)
            else:
                # Direct move
                await page.mouse.move(target_x, target_y)

            # Hover for a moment (humans pause when hovering)
            hover_time = random.uniform(0.3, 0.8)
            await asyncio.sleep(hover_time)

            return {
                'success': True,
                'message': f'Hovered at ({int(target_x)}, {int(target_y)})',
                'coordinates': (int(target_x), int(target_y))
            }

        except Exception as e:
            logger.error(f"Hover failed: {e}")
            return {'success': False, 'message': str(e)}

    async def _smooth_mouse_move(self, page: Page, target_x: float, target_y: float,
                                 duration: float = 0.5) -> None:
        """
        Move mouse smoothly from current position to target
        Looks more human than instant jumps

        Args:
            page: Playwright page
            target_x: Target X coordinate
            target_y: Target Y coordinate
            duration: Time to take (seconds)
        """
        # Get current mouse position (approximate)
        # We'll move in steps to create smooth motion
        steps = int(duration * 60)  # 60fps
        if steps < 5:
            steps = 5

        # Simple linear interpolation for smooth movement
        # In future could add bezier curves for even more human-like movement
        current_pos = await page.evaluate('''() => {
            return {x: window.innerWidth / 2, y: window.innerHeight / 2};
        }''')

        start_x = current_pos['x']
        start_y = current_pos['y']

        for i in range(steps + 1):
            progress = i / steps
            # Add slight randomness to path (humans don't move perfectly straight)
            jitter_x = random.uniform(-2, 2) if i > 0 and i < steps else 0
            jitter_y = random.uniform(-2, 2) if i > 0 and i < steps else 0

            current_x = start_x + (target_x - start_x) * progress + jitter_x
            current_y = start_y + (target_y - start_y) * progress + jitter_y

            await page.mouse.move(current_x, current_y)
            await asyncio.sleep(duration / steps)

    async def double_click(self, page: Page, selector: str = None, x: int = None, y: int = None) -> Dict[str, Any]:
        """
        Double click an element or coordinates

        Args:
            page: Playwright page
            selector: CSS selector to double click
            x, y: Coordinates to double click

        Examples:
            # Double click a video to fullscreen
            await double_click(page, selector="video")
        """
        if not page:
            return {'success': False, 'message': 'No page available'}

        try:
            if selector:
                element = page.locator(selector).first
                await element.dblclick()
                return {'success': True, 'message': f'Double clicked {selector}'}
            elif x is not None and y is not None:
                await page.mouse.dblclick(x, y)
                return {'success': True, 'message': f'Double clicked ({x}, {y})'}
            else:
                return {'success': False, 'message': 'Must provide selector or coordinates'}

        except Exception as e:
            logger.error(f"Double click failed: {e}")
            return {'success': False, 'message': str(e)}

    async def right_click(self, page: Page, selector: str = None, x: int = None, y: int = None) -> Dict[str, Any]:
        """
        Right click (context menu)

        Args:
            page: Playwright page
            selector: CSS selector to right click
            x, y: Coordinates to right click

        Examples:
            # Right click a video
            await right_click(page, selector="video")
        """
        if not page:
            return {'success': False, 'message': 'No page available'}

        try:
            if selector:
                element = page.locator(selector).first
                await element.click(button='right')
                return {'success': True, 'message': f'Right clicked {selector}'}
            elif x is not None and y is not None:
                await page.mouse.click(x, y, button='right')
                return {'success': True, 'message': f'Right clicked ({x}, {y})'}
            else:
                return {'success': False, 'message': 'Must provide selector or coordinates'}

        except Exception as e:
            logger.error(f"Right click failed: {e}")
            return {'success': False, 'message': str(e)}

    async def drag_and_drop(self, page: Page, source_selector: str, target_selector: str) -> Dict[str, Any]:
        """
        Drag element from source to target

        Args:
            page: Playwright page
            source_selector: Element to drag
            target_selector: Where to drop it

        Examples:
            # Drag a video to a playlist
            await drag_and_drop(page, "#video1", "#playlist")
        """
        if not page:
            return {'success': False, 'message': 'No page available'}

        try:
            source = page.locator(source_selector).first
            target = page.locator(target_selector).first

            await source.drag_to(target)

            return {
                'success': True,
                'message': f'Dragged {source_selector} to {target_selector}'
            }

        except Exception as e:
            logger.error(f"Drag and drop failed: {e}")
            return {'success': False, 'message': str(e)}

    async def scroll_to_element(self, page: Page, selector: str, smooth: bool = True) -> Dict[str, Any]:
        """
        Scroll until element is visible

        Args:
            page: Playwright page
            selector: Element to scroll to
            smooth: Use smooth scrolling

        Examples:
            # Scroll to a specific video
            await scroll_to_element(page, "#video-title")
        """
        if not page:
            return {'success': False, 'message': 'No page available'}

        try:
            element = page.locator(selector).first

            # Scroll element into view
            await element.scroll_into_view_if_needed(timeout=5000)

            if smooth:
                # Add slight delay for smooth appearance
                await asyncio.sleep(random.uniform(0.2, 0.5))

            return {
                'success': True,
                'message': f'Scrolled to {selector}'
            }

        except Exception as e:
            logger.error(f"Scroll to element failed: {e}")
            return {'success': False, 'message': str(e)}

    async def wait_and_click(self, page: Page, selector: str, timeout: int = 10000,
                            hover_first: bool = True) -> Dict[str, Any]:
        """
        Wait for element to be visible, optionally hover, then click
        Very human-like pattern

        Args:
            page: Playwright page
            selector: Element to click
            timeout: How long to wait (milliseconds)
            hover_first: Hover before clicking (more human-like)

        Examples:
            # Wait for video and click it
            await wait_and_click(page, "ytd-thumbnail", hover_first=True)
        """
        if not page:
            return {'success': False, 'message': 'No page available'}

        try:
            # Wait for element to be visible
            element = page.locator(selector).first
            await element.wait_for(state='visible', timeout=timeout)

            if hover_first:
                # Hover over element first (humans do this)
                await self.hover(page, selector=selector, smooth=True)
                # Brief pause (humans think before clicking)
                await asyncio.sleep(random.uniform(0.2, 0.5))

            # Click the element
            await element.click()

            return {
                'success': True,
                'message': f'Waited and clicked {selector}',
                'hovered': hover_first
            }

        except Exception as e:
            logger.error(f"Wait and click failed: {e}")
            return {'success': False, 'message': str(e)}

    async def keyboard_shortcut(self, page: Page, keys: str) -> Dict[str, Any]:
        """
        Press keyboard shortcut (e.g., Ctrl+F, Space for play/pause)

        Args:
            page: Playwright page
            keys: Shortcut like "Control+F", "Space", "k" (YouTube play/pause)

        Examples:
            # YouTube shortcuts
            await keyboard_shortcut(page, "k")  # Play/pause
            await keyboard_shortcut(page, "f")  # Fullscreen
            await keyboard_shortcut(page, "ArrowRight")  # Skip forward
            await keyboard_shortcut(page, "ArrowLeft")  # Skip back
        """
        if not page:
            return {'success': False, 'message': 'No page available'}

        try:
            await page.keyboard.press(keys)
            return {
                'success': True,
                'message': f'Pressed {keys}'
            }

        except Exception as e:
            logger.error(f"Keyboard shortcut failed: {e}")
            return {'success': False, 'message': str(e)}

    async def scroll_smooth(self, page: Page, direction: str = 'down', pixels: int = 300,
                           speed: float = 0.5) -> Dict[str, Any]:
        """
        Smooth scrolling (more human-like than instant jumps)

        Args:
            page: Playwright page
            direction: 'up' or 'down'
            pixels: How many pixels to scroll
            speed: Speed of scroll (seconds)

        Examples:
            # Scroll down YouTube feed smoothly
            await scroll_smooth(page, 'down', pixels=500, speed=1.0)
        """
        if not page:
            return {'success': False, 'message': 'No page available'}

        try:
            steps = int(speed * 30)  # 30 steps per second
            if steps < 5:
                steps = 5

            pixel_per_step = pixels / steps
            direction_multiplier = 1 if direction == 'down' else -1

            for i in range(steps):
                await page.evaluate(f'window.scrollBy(0, {pixel_per_step * direction_multiplier})')
                await asyncio.sleep(speed / steps)

            return {
                'success': True,
                'message': f'Smoothly scrolled {direction} {pixels}px'
            }

        except Exception as e:
            logger.error(f"Smooth scroll failed: {e}")
            return {'success': False, 'message': str(e)}


# YouTube-specific helper functions
class YouTubeNavigator:
    """
    YouTube-specific navigation helpers
    Uses UINavigator under the hood
    """

    def __init__(self):
        self.ui_nav = UINavigator()

    async def hover_video(self, page: Page, video_index: int = 0) -> Dict[str, Any]:
        """
        Hover over a video thumbnail

        Args:
            page: Playwright page
            video_index: Which video (0 = first, 1 = second, etc.)
        """
        try:
            # YouTube video thumbnails
            selector = f"ytd-rich-item-renderer:nth-of-type({video_index + 1}) ytd-thumbnail"
            result = await self.ui_nav.hover(page, selector=selector, smooth=True)
            return result
        except Exception as e:
            return {'success': False, 'message': str(e)}

    async def click_video(self, page: Page, video_index: int = 0) -> Dict[str, Any]:
        """
        Click a video (with human-like hover first)

        Args:
            page: Playwright page
            video_index: Which video to click
        """
        try:
            selector = f"ytd-rich-item-renderer:nth-of-type({video_index + 1}) ytd-thumbnail"
            result = await self.ui_nav.wait_and_click(page, selector=selector, hover_first=True)
            return result
        except Exception as e:
            return {'success': False, 'message': str(e)}

    async def play_pause(self, page: Page) -> Dict[str, Any]:
        """Press 'k' to play/pause video"""
        return await self.ui_nav.keyboard_shortcut(page, "k")

    async def fullscreen(self, page: Page) -> Dict[str, Any]:
        """Press 'f' to toggle fullscreen"""
        return await self.ui_nav.keyboard_shortcut(page, "f")

    async def skip_forward(self, page: Page, seconds: int = 5) -> Dict[str, Any]:
        """Skip forward (arrow right = 5 seconds, 'l' = 10 seconds)"""
        key = "l" if seconds >= 10 else "ArrowRight"
        return await self.ui_nav.keyboard_shortcut(page, key)

    async def skip_back(self, page: Page, seconds: int = 5) -> Dict[str, Any]:
        """Skip backward (arrow left = 5 seconds, 'j' = 10 seconds)"""
        key = "j" if seconds >= 10 else "ArrowLeft"
        return await self.ui_nav.keyboard_shortcut(page, key)
