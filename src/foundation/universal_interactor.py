"""
Universal Interactor - Executes interactions based on Universal Element Locator results
Works on ANY site, ANY layout, ANY language
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from playwright.async_api import Page, ElementHandle

logger = logging.getLogger(__name__)


class UniversalInteractor:
    """
    Executes interactions using results from Universal Element Locator
    Handles: coordinates, aria_label, text_content, visual_description
    """

    def __init__(self, page: Page):
        self.page = page

    async def click_element(self, locator_result: Dict[str, Any]) -> bool:
        """
        Click element using locator result

        Args:
            locator_result: Output from UniversalElementLocator.locate_element()

        Returns:
            bool: True if click succeeded
        """
        if not locator_result.get('success'):
            logger.warning(f"❌ Cannot click - element not found: {locator_result.get('reasoning')}")
            return False

        strategy = locator_result.get('strategy')
        target = locator_result.get('target', {})

        try:
            if strategy == 'coordinates':
                return await self._click_by_coordinates(target)
            elif strategy == 'aria_label':
                return await self._click_by_aria_label(target)
            elif strategy == 'text_content':
                return await self._click_by_text(target)
            elif strategy == 'visual_description':
                # Fallback: Try multiple strategies based on description
                return await self._click_by_description(target, locator_result.get('element_type'))
            else:
                logger.error(f"❌ Unknown strategy: {strategy}")
                return False

        except Exception as e:
            logger.error(f"❌ Click error: {e}")
            return False

    async def _click_by_coordinates(self, target: Dict[str, Any]) -> bool:
        """Click element at specific coordinates (percentage of page - handles scrolling for elements below fold)"""
        try:
            x_percent = target.get('x_percent')
            y_percent = target.get('y_percent')

            if x_percent is None or y_percent is None:
                logger.error("❌ Missing coordinates")
                return False

            # Check if coordinates are reasonable (basic sanity check)
            if not (0 <= x_percent <= 100) or y_percent < 0:
                logger.error(f"❌ INVALID COORDINATES: ({x_percent}%, {y_percent}%) - Out of bounds!")
                return False

            # 🔄 NEW: Detect if element requires scrolling (below fold)
            if y_percent > 100:
                logger.info(f"🔄 Element below fold at ({x_percent}%, {y_percent}%) - scrolling to bring into view")
                scroll_success = await self._scroll_to_element(x_percent, y_percent)
                if not scroll_success:
                    logger.error("❌ Failed to scroll element into view")
                    return False

                # After scrolling, element should be in viewport - adjust coordinates to viewport-relative
                # Assume element is now centered in viewport
                x_percent_viewport = x_percent
                y_percent_viewport = 50  # Center of viewport after scroll
            else:
                # Element already in viewport
                x_percent_viewport = x_percent
                y_percent_viewport = y_percent

            # Get viewport size
            viewport_size = self.page.viewport_size
            if not viewport_size:
                viewport_size = {'width': 1920, 'height': 1080}  # Default

            # Calculate pixel coordinates (viewport-relative)
            x = int(viewport_size['width'] * x_percent_viewport / 100)
            y = int(viewport_size['height'] * y_percent_viewport / 100)

            logger.info(f"🖱️  Clicking coordinates: ({x_percent_viewport}%, {y_percent_viewport}%) → ({x}px, {y}px) [viewport: {viewport_size['width']}x{viewport_size['height']}]")

            # Click at coordinates
            await self.page.mouse.click(x, y)
            await asyncio.sleep(0.5)

            return True

        except Exception as e:
            logger.error(f"❌ Coordinate click error: {e}")
            return False

    async def _scroll_to_element(self, x_percent: float, y_percent: float) -> bool:
        """
        Scroll page to bring element into visible viewport

        Args:
            x_percent: Horizontal position (0-100% of page width)
            y_percent: Vertical position (0-100%+ of page height)

        Returns:
            bool: True if scroll succeeded
        """
        try:
            # Calculate scroll position to center element in viewport
            # If element is at 534% down the page, we need to scroll to show that area
            # Strategy: Scroll to position where element will be at 50% of viewport (centered)

            # y_percent is percentage of FULL page height
            # To center element at y_percent in viewport, scroll to (y_percent - 50)% of page
            target_scroll_percent = max(0, y_percent - 50)  # Don't scroll negative

            # Get page height to calculate scroll position
            page_height = await self.page.evaluate("document.body.scrollHeight")
            viewport_height = await self.page.evaluate("window.innerHeight")

            # Calculate scroll position in pixels
            scroll_y = int(page_height * target_scroll_percent / 100)

            # Ensure we don't scroll past the bottom
            max_scroll = page_height - viewport_height
            scroll_y = min(scroll_y, max_scroll)

            logger.info(f"📜 Scrolling to Y: {scroll_y}px (target: {target_scroll_percent:.1f}% of page height {page_height}px)")

            # Perform scroll
            await self.page.evaluate(f"window.scrollTo(0, {scroll_y});")
            await asyncio.sleep(0.8)  # Allow scroll animation and content to load

            logger.info(f"✅ Scrolled successfully - element should now be visible")
            return True

        except Exception as e:
            logger.error(f"❌ Scroll failed: {e}")
            return False

    async def _click_by_aria_label(self, target: Dict[str, Any]) -> bool:
        """Click element by ARIA label"""
        try:
            aria_label = target.get('aria_label')
            if not aria_label:
                logger.error("❌ Missing aria_label")
                return False

            logger.info(f"🎯 Clicking by ARIA label: {aria_label}")

            # Try multiple ARIA selector variations
            selectors = [
                f'[aria-label="{aria_label}"]',
                f'[aria-label*="{aria_label}" i]',  # Case-insensitive partial match
                f'[aria-labelledby*="{aria_label}" i]'
            ]

            for selector in selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=2000, state='visible')
                    if element:
                        await element.click()
                        await asyncio.sleep(0.5)
                        logger.info(f"✅ Clicked via ARIA label: {selector}")
                        return True
                except:
                    continue

            logger.warning(f"⚠️  ARIA label not found: {aria_label}")
            return False

        except Exception as e:
            logger.error(f"❌ ARIA label click error: {e}")
            return False

    async def _click_by_text(self, target: Dict[str, Any]) -> bool:
        """Click element by visible text content"""
        try:
            text = target.get('text')
            partial = target.get('partial', False)

            if not text:
                logger.error("❌ Missing text")
                return False

            logger.info(f"📝 Clicking by text: '{text}' (partial={partial})")

            # Try to find element with matching text
            if partial:
                # Partial match - more forgiving
                selector = f'text=/{text}/i'  # Case-insensitive regex
            else:
                # Exact match
                selector = f'text="{text}"'

            try:
                element = await self.page.wait_for_selector(selector, timeout=2000, state='visible')
                if element:
                    await element.click()
                    await asyncio.sleep(0.5)
                    logger.info(f"✅ Clicked via text: {text}")
                    return True
            except:
                # Try alternative: find by inner text
                elements = await self.page.query_selector_all('button, a, [role="button"], [role="link"]')
                for elem in elements:
                    inner_text = await elem.inner_text()
                    if inner_text and (text.lower() in inner_text.lower() if partial else text == inner_text):
                        is_visible = await elem.is_visible()
                        if is_visible:
                            await elem.click()
                            await asyncio.sleep(0.5)
                            logger.info(f"✅ Clicked via text match: {inner_text}")
                            return True

            logger.warning(f"⚠️  Text not found: {text}")
            return False

        except Exception as e:
            logger.error(f"❌ Text click error: {e}")
            return False

    async def _click_by_description(self, target: Dict[str, Any], element_type: Optional[str] = None) -> bool:
        """
        Fallback: Try to find element based on visual description
        Uses multiple heuristics and common patterns
        """
        try:
            description = target.get('description', '')
            logger.info(f"🔍 Attempting click by description: {description}")

            # Parse description for keywords
            desc_lower = description.lower()

            # Try to extract position hints
            if 'top' in desc_lower and 'right' in desc_lower:
                # Top-right area
                viewport_size = self.page.viewport_size or {'width': 1920, 'height': 1080}
                x = int(viewport_size['width'] * 0.85)
                y = int(viewport_size['height'] * 0.1)
                logger.info(f"🎯 Description suggests top-right: ({x}px, {y}px)")
                await self.page.mouse.click(x, y)
                await asyncio.sleep(0.5)
                return True

            elif 'top' in desc_lower and 'left' in desc_lower:
                viewport_size = self.page.viewport_size or {'width': 1920, 'height': 1080}
                x = int(viewport_size['width'] * 0.15)
                y = int(viewport_size['height'] * 0.1)
                logger.info(f"🎯 Description suggests top-left: ({x}px, {y}px)")
                await self.page.mouse.click(x, y)
                await asyncio.sleep(0.5)
                return True

            # Try to find by element type + position
            if element_type:
                type_selectors = {
                    'button': 'button, [role="button"]',
                    'input': 'input, [role="textbox"]',
                    'link': 'a, [role="link"]',
                    'icon': 'svg, i, [class*="icon"]'
                }
                selector = type_selectors.get(element_type, element_type)

                elements = await self.page.query_selector_all(selector)
                if elements:
                    # Click first visible element (LLM said it's the target)
                    for elem in elements:
                        is_visible = await elem.is_visible()
                        if is_visible:
                            await elem.click()
                            await asyncio.sleep(0.5)
                            logger.info(f"✅ Clicked first visible {element_type}")
                            return True

            logger.warning(f"⚠️  Could not interpret description: {description}")
            return False

        except Exception as e:
            logger.error(f"❌ Description click error: {e}")
            return False

    async def type_text(self, locator_result: Dict[str, Any], text: str) -> bool:
        """
        Type text into element using locator result

        Args:
            locator_result: Output from UniversalElementLocator.locate_element()
            text: Text to type

        Returns:
            bool: True if typing succeeded
        """
        if not locator_result.get('success'):
            logger.warning(f"❌ Cannot type - element not found: {locator_result.get('reasoning')}")
            return False

        strategy = locator_result.get('strategy')
        target = locator_result.get('target', {})

        try:
            # First click to focus
            clicked = await self.click_element(locator_result)
            if not clicked:
                return False

            # Then type
            logger.info(f"⌨️  Typing text: {text[:50]}...")
            await self.page.keyboard.type(text, delay=50)  # 50ms between keystrokes
            await asyncio.sleep(0.3)

            return True

        except Exception as e:
            logger.error(f"❌ Type text error: {e}")
            return False

    async def press_key(self, key: str) -> bool:
        """Press a keyboard key (e.g., 'Enter', 'Escape', 'Tab')"""
        try:
            logger.info(f"⌨️  Pressing key: {key}")
            await self.page.keyboard.press(key)
            await asyncio.sleep(0.3)
            return True
        except Exception as e:
            logger.error(f"❌ Key press error: {e}")
            return False
