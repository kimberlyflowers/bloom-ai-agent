"""
SARAH'S FIXED CLICKING SYSTEM
This fixes Sarah's vision → clicking disconnect.

She can SEE elements but couldn't CLICK them. This bridges that gap using Playwright's locators.

SAFE TO INTEGRATE: This doesn't change her existing code, just adds better clicking capability.
"""

import asyncio
from playwright.async_api import Page, TimeoutError as PlaywrightTimeout


class ImprovedClicking:
    """
    Sarah's enhanced clicking that actually works

    Uses multiple strategies to find and click elements:
    1. Exact text match
    2. Partial text match
    3. Button with text
    4. Link with text
    5. Placeholder text (for inputs)
    6. ARIA labels
    7. Visible text anywhere
    """

    async def click_element(self, page: Page, description: str, timeout: int = 10000) -> dict:
        """
        Smart clicking that tries multiple strategies

        Args:
            page: Playwright page object
            description: What Sarah sees/wants to click (e.g., "Accept all", "Search", "Change to English")
            timeout: How long to wait (milliseconds)

        Returns:
            dict with success status and message
        """

        strategies = [
            self._click_by_exact_text,
            self._click_by_partial_text,
            self._click_button_with_text,
            self._click_link_with_text,
            self._click_by_placeholder,
            self._click_by_aria_label,
            self._click_by_role,
            self._click_visible_text
        ]

        # Divide timeout among strategies for faster failure
        # Each strategy gets at most 2 seconds to avoid long waits
        per_strategy_timeout = min(2000, timeout // len(strategies))

        for strategy in strategies:
            try:
                result = await strategy(page, description, per_strategy_timeout)
                if result['success']:
                    return result
            except Exception as e:
                continue

        # Nothing worked
        return {
            'success': False,
            'message': f"Could not find clickable element: '{description}'",
            'tried_strategies': len(strategies)
        }

    async def _click_by_exact_text(self, page: Page, text: str, timeout: int) -> dict:
        """Strategy 1: Click element with exact text match"""
        try:
            element = page.get_by_text(text, exact=True)
            await element.click(timeout=timeout)
            return {'success': True, 'method': 'exact_text', 'message': f"Clicked '{text}' (exact match)"}
        except:
            raise

    async def _click_by_partial_text(self, page: Page, text: str, timeout: int) -> dict:
        """Strategy 2: Click first element containing text"""
        try:
            element = page.get_by_text(text).first
            await element.click(timeout=timeout)
            return {'success': True, 'method': 'partial_text', 'message': f"Clicked element containing '{text}'"}
        except:
            raise

    async def _click_button_with_text(self, page: Page, text: str, timeout: int) -> dict:
        """Strategy 3: Click button containing text"""
        try:
            element = page.locator(f"button:has-text('{text}')").first
            await element.click(timeout=timeout)
            return {'success': True, 'method': 'button_text', 'message': f"Clicked button '{text}'"}
        except:
            raise

    async def _click_link_with_text(self, page: Page, text: str, timeout: int) -> dict:
        """Strategy 4: Click link containing text"""
        try:
            element = page.locator(f"a:has-text('{text}')").first
            await element.click(timeout=timeout)
            return {'success': True, 'method': 'link_text', 'message': f"Clicked link '{text}'"}
        except:
            raise

    async def _click_by_placeholder(self, page: Page, text: str, timeout: int) -> dict:
        """Strategy 5: Click input with placeholder text"""
        try:
            element = page.get_by_placeholder(text)
            await element.click(timeout=timeout)
            return {'success': True, 'method': 'placeholder', 'message': f"Clicked input with placeholder '{text}'"}
        except:
            raise

    async def _click_by_aria_label(self, page: Page, text: str, timeout: int) -> dict:
        """Strategy 6: Click element with aria-label"""
        try:
            element = page.get_by_label(text)
            await element.click(timeout=timeout)
            return {'success': True, 'method': 'aria_label', 'message': f"Clicked element with label '{text}'"}
        except:
            raise

    async def _click_by_role(self, page: Page, text: str, timeout: int) -> dict:
        """Strategy 7: Click by role and name"""
        try:
            # Try as button role
            element = page.get_by_role("button", name=text)
            await element.click(timeout=timeout)
            return {'success': True, 'method': 'role_button', 'message': f"Clicked button role '{text}'"}
        except:
            pass

        try:
            # Try as link role
            element = page.get_by_role("link", name=text)
            await element.click(timeout=timeout)
            return {'success': True, 'method': 'role_link', 'message': f"Clicked link role '{text}'"}
        except:
            raise

    async def _click_visible_text(self, page: Page, text: str, timeout: int) -> dict:
        """Strategy 8: Click any visible element with text (last resort)"""
        try:
            # Use XPath to find any visible element containing text
            element = page.locator(f"//*[contains(text(), '{text}') and not(ancestor::*[contains(@style, 'display: none')])]").first
            await element.click(timeout=timeout)
            return {'success': True, 'method': 'visible_text', 'message': f"Clicked visible element with '{text}'"}
        except:
            raise

    async def type_text(self, page: Page, text: str, input_description: str = None) -> dict:
        """
        Type text into an input field

        Args:
            page: Playwright page
            text: Text to type
            input_description: Description of input (e.g., "Search", "Email")
        """

        try:
            if input_description:
                # First click the input to focus it
                click_result = await self.click_element(page, input_description)
                if not click_result['success']:
                    return click_result

            # Type the text
            await page.keyboard.type(text)

            return {
                'success': True,
                'message': f"Typed '{text}'" + (f" into {input_description}" if input_description else "")
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to type: {str(e)}"
            }

    async def press_key(self, page: Page, key: str) -> dict:
        """
        Press a keyboard key

        Args:
            page: Playwright page
            key: Key to press (e.g., "Enter", "Escape", "Tab")
        """
        try:
            await page.keyboard.press(key)
            return {
                'success': True,
                'message': f"Pressed {key}"
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to press key: {str(e)}"
            }

    async def wait_for_element(self, page: Page, description: str, timeout: int = 10000) -> dict:
        """
        Wait for element to appear

        Useful for checking if click worked or waiting for page load
        """
        try:
            # Try multiple selectors
            selectors = [
                page.get_by_text(description),
                page.locator(f"button:has-text('{description}')"),
                page.locator(f"a:has-text('{description}')"),
            ]

            for selector in selectors:
                try:
                    await selector.first.wait_for(state="visible", timeout=timeout)
                    return {
                        'success': True,
                        'message': f"Found '{description}'"
                    }
                except:
                    continue

            return {
                'success': False,
                'message': f"Element '{description}' not found within {timeout}ms"
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error waiting for element: {str(e)}"
            }


# ============================================================================
# STANDALONE TESTING
# ============================================================================
async def test_clicking():
    """Test the clicking system works"""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        clicker = ImprovedClicking()

        # Test 1: Navigate to Google
        print("\n🧪 TEST 1: Google")
        await page.goto("https://google.com")
        await asyncio.sleep(1)

        # Try to accept cookies
        result = await clicker.click_element(page, "Accept all", timeout=5000)
        print(f"   {result['message']}")

        # Test 2: Click search box
        print("\n🧪 TEST 2: Search")
        result = await clicker.click_element(page, "Search")
        print(f"   {result['message']}")

        if result['success']:
            # Type something
            result = await clicker.type_text(page, "playwright automation")
            print(f"   {result['message']}")

            # Press Enter
            result = await clicker.press_key(page, "Enter")
            print(f"   {result['message']}")

        await asyncio.sleep(3)

        # Test 3: YouTube
        print("\n🧪 TEST 3: YouTube")
        await page.goto("https://youtube.com")
        await asyncio.sleep(2)

        # Accept cookies
        result = await clicker.click_element(page, "Accept all", timeout=5000)
        print(f"   {result['message']}")

        # Search
        result = await clicker.click_element(page, "Search", timeout=5000)
        if result['success']:
            await clicker.type_text(page, "viral content")
            await clicker.press_key(page, "Enter")
            print("   ✅ Searched for videos")

        await asyncio.sleep(5)
        await browser.close()

        print("\n✅ All tests complete!")


if __name__ == "__main__":
    # Run standalone test
    asyncio.run(test_clicking())
