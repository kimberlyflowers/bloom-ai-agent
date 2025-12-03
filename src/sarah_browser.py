"""
Sarah's Browser - Async wrapper around Playwright for browser automation

Provides clean interface for browser operations needed for tutorial learning.
"""

import asyncio
import logging
from typing import Optional
from pathlib import Path
from PIL import Image
from io import BytesIO
from playwright.async_api import async_playwright, Page, Browser, BrowserContext


class SarahBrowser:
    """
    Async browser automation wrapper for Sarah

    Features:
    - Async/await API
    - Screenshot capture as PIL Images
    - Navigation and interaction
    - Cookie banner dismissal
    - YouTube search helper

    Usage:
        browser = SarahBrowser()
        await browser.start()
        await browser.navigate("https://example.com")
        screenshot = await browser.take_screenshot()  # Returns PIL Image
        await browser.click(x=100, y=200)
        await browser.close()
    """

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.logger = logging.getLogger(__name__)

    async def start(self):
        """Initialize browser"""
        self.logger.info("🚀 Starting browser...")

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )

        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        self.page = await self.context.new_page()
        self.logger.info("✅ Browser started")

    async def close(self):
        """Clean shutdown"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.logger.info("🛑 Browser closed")

    async def navigate(self, url: str, wait_until: str = "networkidle"):
        """
        Navigate to URL

        Args:
            url: URL to visit
            wait_until: When to consider navigation complete
                       ("load", "domcontentloaded", "networkidle")
        """
        self.logger.info(f"🔗 Navigating to: {url}")
        await self.page.goto(url, wait_until=wait_until, timeout=30000)
        await asyncio.sleep(1)  # Extra settling time

    async def take_screenshot(self) -> Image.Image:
        """
        Take screenshot and return as PIL Image

        Returns:
            PIL Image object
        """
        screenshot_bytes = await self.page.screenshot(type="png", full_page=False)
        return Image.open(BytesIO(screenshot_bytes))

    async def screenshot(self) -> bytes:
        """
        Take screenshot and return as bytes

        Returns:
            PNG screenshot as bytes
        """
        return await self.page.screenshot(type="png", full_page=False)

    async def click(self, x: int, y: int):
        """
        Click at specific coordinates

        Args:
            x: X coordinate (pixels from left)
            y: Y coordinate (pixels from top)
        """
        self.logger.info(f"🖱️  Clicking at ({x}, {y})")
        await self.page.mouse.click(x, y)
        await asyncio.sleep(0.5)

    async def type_text(self, text: str, delay: int = 50):
        """
        Type text using keyboard

        Args:
            text: Text to type
            delay: Milliseconds between keystrokes
        """
        self.logger.info(f"⌨️  Typing: {text}")
        await self.page.keyboard.type(text, delay=delay)

    async def press_key(self, key: str):
        """Press a single key (e.g., "Enter", "Escape")"""
        await self.page.keyboard.press(key)

    async def search_youtube(self, query: str):
        """
        Helper: Search YouTube

        Args:
            query: Search query
        """
        self.logger.info(f"🔍 Searching YouTube for: {query}")

        # Find search box
        search_input = await self.page.wait_for_selector(
            'input#search',
            timeout=10000
        )

        # Type query
        await search_input.click()
        await search_input.fill(query)
        await asyncio.sleep(0.5)

        # Press Enter or click search button
        await self.page.keyboard.press("Enter")
        await asyncio.sleep(2)

        self.logger.info("✅ Search complete")

    async def search_google(self, query: str):
        """
        Helper: Search Google

        Args:
            query: Search query
        """
        self.logger.info(f"🔍 Searching Google for: {query}")

        # Navigate to Google
        await self.navigate("https://www.google.com")

        # Find search box
        search_input = await self.page.wait_for_selector(
            'textarea[name="q"], input[name="q"]',
            timeout=10000
        )

        # Type and search
        await search_input.click()
        await search_input.fill(query)
        await self.page.keyboard.press("Enter")
        await asyncio.sleep(2)

        self.logger.info("✅ Search complete")

    async def dismiss_cookie_banner(self) -> bool:
        """
        Try to dismiss cookie consent banners

        Returns:
            True if banner was found and dismissed, False otherwise
        """
        self.logger.info("🍪 Looking for cookie banner...")

        # Common cookie banner button texts
        button_texts = [
            "Accept", "Accept all", "I agree", "OK", "Agree",
            "Accepteren", "Alles accepteren",  # Dutch
            "Tout accepter",  # French
            "Akzeptieren", "Alle akzeptieren"  # German
        ]

        for text in button_texts:
            try:
                # Try to find button with this text
                button = await self.page.query_selector(
                    f'button:has-text("{text}"), a:has-text("{text}")'
                )

                if button:
                    await button.click()
                    await asyncio.sleep(1)
                    self.logger.info(f"✅ Dismissed cookie banner (clicked '{text}')")
                    return True
            except:
                continue

        self.logger.info("ℹ️  No cookie banner found")
        return False

    async def scroll_down(self, pixels: int = 500):
        """Scroll down by specified pixels"""
        await self.page.evaluate(f"window.scrollBy(0, {pixels})")
        await asyncio.sleep(0.5)

    async def scroll_to_top(self):
        """Scroll to top of page"""
        await self.page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.5)

    async def wait_for_element(self, selector: str, timeout: int = 10000):
        """Wait for element to appear"""
        return await self.page.wait_for_selector(selector, timeout=timeout)

    async def get_current_url(self) -> str:
        """Get current page URL"""
        return self.page.url

    async def go_back(self):
        """Navigate back"""
        await self.page.go_back()
        await asyncio.sleep(1)

    async def go_forward(self):
        """Navigate forward"""
        await self.page.go_forward()
        await asyncio.sleep(1)

    async def reload(self):
        """Reload page"""
        await self.page.reload()
        await asyncio.sleep(1)


# Example usage
if __name__ == "__main__":
    async def test():
        browser = SarahBrowser(headless=False)
        await browser.start()

        # Test navigation
        await browser.navigate("https://www.google.com")

        # Test screenshot
        screenshot = await browser.take_screenshot()
        print(f"Screenshot size: {screenshot.size}")

        # Test cookie dismissal
        await browser.dismiss_cookie_banner()

        await browser.close()
        print("✅ Test complete!")

    asyncio.run(test())
