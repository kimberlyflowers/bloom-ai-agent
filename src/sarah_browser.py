"""
Sarah's Browser Controller with Live Screen Streaming

This integrates:
- Async Playwright browser automation
- Live screen streaming to dashboard
- Command interface for chat server

When Sarah browses the web, you can watch her screen in real-time!
"""

import asyncio
import logging
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from src.live_screen_stream import PlaywrightScreenStreamer

logger = logging.getLogger(__name__)


class SarahBrowser:
    """
    Sarah's browser with live screen streaming capabilities

    This class provides:
    - Async Playwright browser control
    - Live screen streaming to dashboard
    - Human-like browsing behavior
    - Command interface for automation
    """

    def __init__(self, headless: bool = True, stream_port: int = 8765):
        """
        Initialize Sarah's browser

        Args:
            headless: Run in headless mode (True for Railway/production)
            stream_port: WebSocket port for screen streaming
        """
        self.headless = headless
        self.stream_port = stream_port

        # Playwright objects
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        # Screen streamer
        self.streamer = PlaywrightScreenStreamer(port=stream_port, fps=2)

        # State
        self.is_running = False
        self.current_url = None

    async def start(self):
        """Start browser and screen streaming server"""
        logger.info("🌸 Starting Sarah's browser...")

        try:
            # Start Playwright
            self.playwright = await async_playwright().start()

            # Launch browser (Chromium)
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )

            # Create context (separate session)
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            # Create page
            self.page = await self.context.new_page()

            # Connect page to screen streamer
            self.streamer.set_browser_page(self.page)

            # NOTE: Don't start screen streaming server here!
            # The unified WebSocket server will handle connections
            # We only start the streaming loop

            self.is_running = True

            logger.info("✅ Sarah's browser is ready!")
            logger.info(f"📺 Screen streaming will be available via unified server")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to start browser: {e}")
            logger.exception(e)
            return False

    async def navigate(self, url: str) -> dict:
        """
        Navigate to a URL

        Args:
            url: URL to visit

        Returns:
            dict with status and message
        """
        if not self.is_running or not self.page:
            return {
                'success': False,
                'message': 'Browser not running'
            }

        try:
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = f'https://{url}'

            logger.info(f"🌐 Navigating to: {url}")

            # Navigate with timeout
            await self.page.goto(url, wait_until='networkidle', timeout=30000)

            self.current_url = self.page.url
            title = await self.page.title()

            logger.info(f"✅ Loaded: {title}")

            return {
                'success': True,
                'url': self.current_url,
                'title': title,
                'message': f'Successfully loaded {title}'
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Navigation failed: {error_msg}")

            return {
                'success': False,
                'url': url,
                'message': f'Failed to load page: {error_msg}'
            }

    async def get_page_info(self) -> dict:
        """Get current page information"""
        if not self.page:
            return {
                'url': None,
                'title': None,
                'message': 'No page loaded'
            }

        try:
            return {
                'url': self.page.url,
                'title': await self.page.title(),
                'message': 'Page info retrieved'
            }
        except:
            return {
                'url': self.current_url,
                'title': None,
                'message': 'Could not retrieve page info'
            }

    async def click(self, selector: str) -> dict:
        """Click an element"""
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        try:
            await self.page.click(selector, timeout=10000)
            return {'success': True, 'message': f'Clicked {selector}'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    async def type_text(self, selector: str, text: str, human_like: bool = True) -> dict:
        """
        Type text into an input field

        Args:
            selector: CSS selector for input field
            text: Text to type
            human_like: Add delays between keystrokes
        """
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        try:
            if human_like:
                # Type with human-like delays
                await self.page.type(selector, text, delay=50)
            else:
                await self.page.fill(selector, text)

            return {'success': True, 'message': f'Typed into {selector}'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    async def screenshot(self, full_page: bool = False) -> Optional[bytes]:
        """Take a screenshot"""
        if not self.page:
            return None

        try:
            return await self.page.screenshot(
                type='jpeg',
                quality=80,
                full_page=full_page
            )
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None

    async def scroll(self, direction: str = 'down', amount: int = 500) -> dict:
        """Scroll the page"""
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        try:
            if direction == 'down':
                await self.page.evaluate(f'window.scrollBy(0, {amount})')
            elif direction == 'up':
                await self.page.evaluate(f'window.scrollBy(0, -{amount})')
            elif direction == 'top':
                await self.page.evaluate('window.scrollTo(0, 0)')
            elif direction == 'bottom':
                await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')

            return {'success': True, 'message': f'Scrolled {direction}'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    async def search_google(self, query: str) -> dict:
        """
        Search on Google (convenience method)

        Args:
            query: Search query

        Returns:
            dict with status
        """
        try:
            # Navigate to Google
            result = await self.navigate('https://www.google.com')
            if not result['success']:
                return result

            await asyncio.sleep(1)

            # Wait for search box and type query
            await self.page.wait_for_selector('textarea[name="q"], input[name="q"]', timeout=5000)
            await self.type_text('textarea[name="q"], input[name="q"]', query)

            # Press Enter
            await self.page.keyboard.press('Enter')

            # Wait for results
            await self.page.wait_for_load_state('networkidle', timeout=10000)

            return {
                'success': True,
                'query': query,
                'message': f'Searched for "{query}"'
            }

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                'success': False,
                'query': query,
                'message': f'Search failed: {str(e)}'
            }

    async def wait(self, seconds: float):
        """Wait for specified seconds"""
        await asyncio.sleep(seconds)

    async def close(self):
        """Close browser and stop streaming"""
        logger.info("🔴 Closing Sarah's browser...")

        self.streamer.stop_streaming()

        if self.context:
            await self.context.close()

        if self.browser:
            await self.browser.close()

        if self.playwright:
            await self.playwright.stop()

        self.is_running = False
        logger.info("✅ Browser closed")


# Demo/testing
async def demo():
    """Test Sarah's browser"""
    browser = SarahBrowser(headless=False)

    await browser.start()

    print("\n✅ Sarah's browser is running!")
    print("📺 Open dashboard to see her screen")
    print("\nTesting navigation...\n")

    # Test navigation
    result = await browser.navigate('https://www.google.com')
    print(f"Navigation result: {result}")

    await browser.wait(3)

    # Test search
    result = await browser.search_google('TikTok growth strategies')
    print(f"Search result: {result}")

    await browser.wait(5)

    print("\n🎉 Demo complete! Check the dashboard to see Sarah's screen.")
    print("Press Ctrl+C to close...")

    try:
        await asyncio.Future()  # Keep running
    except KeyboardInterrupt:
        await browser.close()


if __name__ == '__main__':
    asyncio.run(demo())
