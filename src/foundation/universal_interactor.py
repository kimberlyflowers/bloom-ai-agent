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
        """Click element at specific coordinates (percentage of viewport)"""
        try:
            x_percent = target.get('x_percent')
            y_percent = target.get('y_percent')

            if x_percent is None or y_percent is None:
                logger.error("❌ Missing coordinates")
                return False

            # ✅ VALIDATE coordinates are within visible viewport (0-100%)
            if not (0 <= x_percent <= 100) or not (0 <= y_percent <= 100):
                logger.error(
                    f"❌ INVALID COORDINATES: ({x_percent}%, {y_percent}%) - "
                    f"Element is OUTSIDE visible viewport! "
                    f"Coordinates must be 0-100% for visible elements only. "
                    f"If element is below fold, you cannot click it without scrolling first."
                )
                return False

            # Get viewport size
            viewport_size = self.page.viewport_size
            if not viewport_size:
                viewport_size = {'width': 1920, 'height': 1080}  # Default

            # Calculate pixel coordinates
            x = int(viewport_size['width'] * x_percent / 100)
            y = int(viewport_size['height'] * y_percent / 100)

            logger.info(f"🖱️  Clicking coordinates: ({x_percent}%, {y_percent}%) → ({x}px, {y}px) [viewport: {viewport_size['width']}x{viewport_size['height']}]")

            # Click at coordinates
            await self.page.mouse.click(x, y)
            await asyncio.sleep(0.5)

            return True

        except Exception as e:
            logger.error(f"❌ Coordinate click error: {e}")
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
