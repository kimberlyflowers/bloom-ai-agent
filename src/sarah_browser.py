"""
Sarah's Browser Controller with Live Screen Streaming

This integrates:
- Async Playwright browser automation
- Live screen streaming to dashboard
- Command interface for chat server
- Advanced vision-guided interactions
- Multi-step workflow execution

When Sarah browses the web, you can watch her screen in real-time!
She can interact with ANY website like a human using vision!
"""

import asyncio
import logging
import os
from typing import Optional, Dict, List, Any
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from src.live_screen_stream import PlaywrightScreenStreamer
from src.advanced_browser_control import AdvancedBrowserController

# Sarah's improved clicking system - helps her hands work better!
try:
    from src.sarah_improved_clicking import ImprovedClicking
    IMPROVED_CLICKING_AVAILABLE = True
except ImportError:
    IMPROVED_CLICKING_AVAILABLE = False

# Sarah's UI navigation - mouse hover, smooth movement, YouTube controls
try:
    from src.sarah_ui_navigation import UINavigator, YouTubeNavigator
    UI_NAVIGATION_AVAILABLE = True
except ImportError:
    UI_NAVIGATION_AVAILABLE = False

logger = logging.getLogger(__name__)

if not IMPROVED_CLICKING_AVAILABLE:
    logger.warning("⚠️  ImprovedClicking not available - using basic clicking only")
if not UI_NAVIGATION_AVAILABLE:
    logger.warning("⚠️  UI Navigation not available - hover/smooth movement disabled")


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

        # Advanced browser controller (vision-guided interactions)
        self.advanced = AdvancedBrowserController()

        # Improved clicking system - helps Sarah's hands work better!
        if IMPROVED_CLICKING_AVAILABLE:
            self.improved_clicker = ImprovedClicking()
            logger.info("✅ Sarah's improved clicking loaded - hands upgraded!")
        else:
            self.improved_clicker = None

        # UI Navigation - mouse hover, smooth movement, YouTube controls
        if UI_NAVIGATION_AVAILABLE:
            self.ui_nav = UINavigator()
            self.youtube_nav = YouTubeNavigator()
            logger.info("✅ Sarah's UI navigation loaded - can hover, drag, smooth scroll!")
        else:
            self.ui_nav = None
            self.youtube_nav = None

        # State
        self.is_running = False
        self.current_url = None

    async def start(self):
        """Start browser and screen streaming server"""
        logger.info("🌸 Starting Sarah's browser...")

        try:
            # Start Playwright
            self.playwright = await async_playwright().start()

            # XVFB DETECTION: Check if virtual display is available
            # If DISPLAY is set (e.g., :99), we can run REAL Chrome (not headless)!
            display_env = os.environ.get('DISPLAY')
            use_real_chrome = display_env is not None

            if use_real_chrome:
                logger.info(f"🖥️  Xvfb detected (DISPLAY={display_env}) - Using REAL Chrome!")
                logger.info("🎯 Browser fingerprint will look 100% authentic!")
                headless_mode = False  # Run real Chrome on virtual display
            else:
                logger.info("📱 No virtual display - Using headless mode")
                headless_mode = self.headless

            # Launch browser (Chromium)
            # With Xvfb: Real Chrome with perfect fingerprint
            # Without Xvfb: Headless mode (fallback)
            self.browser = await self.playwright.chromium.launch(
                headless=headless_mode,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    # ACCESSIBILITY FLAGS - Makes CAPTCHA bypass easier!
                    '--enable-accessibility',  # Enable accessibility tree
                    '--force-renderer-accessibility',  # Force accessibility support
                    '--enable-features=AccessibilityExposeHTMLElement',  # Expose HTML elements to accessibility API
                    # Additional anti-detection args for real Chrome
                    '--disable-infobars',
                    '--disable-extensions',
                    '--disable-web-security',  # Reduces detection surface
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--allow-running-insecure-content',
                    # Make window look like a normal user's Chrome
                    '--window-size=1920,1080',
                    '--disable-popup-blocking',
                    '--disable-prompt-on-repost'
                ]
            )

            # Create context (separate session)
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            # STEALTH SCRIPT: Hide automation markers and indicate assistive technology
            await self.context.add_init_script("""
                // Remove webdriver flag (makes us look like a real user)
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                // Indicate screen reader/assistive technology presence
                // This makes accessibility-based interactions look natural!
                window.addEventListener('load', () => {
                    document.documentElement.setAttribute('aria-live', 'polite');
                });

                // Override plugins to look more real
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            """)

            # Create page
            self.page = await self.context.new_page()

            # Connect page to screen streamer
            self.streamer.set_browser_page(self.page)

            # Connect page to advanced controller (vision-guided interactions)
            self.advanced.set_page(self.page)

            # NOTE: Don't start screen streaming server here!
            # The unified WebSocket server will handle connections
            # We only start the streaming loop

            self.is_running = True

            logger.info("✅ Sarah's browser is ready!")
            logger.info(f"📺 Screen streaming will be available via unified server")
            logger.info(f"🎯 Advanced vision-guided interactions enabled")

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

    async def smart_click(self, description: str, timeout: int = 10000) -> dict:
        """
        Sarah's improved clicking - finds and clicks elements by description!

        This helps Sarah's hands work better by trying 8 different strategies
        to find and click elements. She can just describe what she sees instead
        of needing exact CSS selectors.

        Args:
            description: What Sarah sees (e.g., "Accept all", "Search", "Login button")
            timeout: Timeout in milliseconds

        Returns:
            dict with success status and method used

        Examples:
            await sarah.smart_click("Accept all")  # Finds cookie button
            await sarah.smart_click("Search")      # Finds search box
            await sarah.smart_click("Sign in")     # Finds login link/button
        """
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.improved_clicker:
            # Use improved clicking (8 strategies!)
            result = await self.improved_clicker.click_element(self.page, description, timeout)
            return result
        else:
            # Fallback to basic click if improved clicker not available
            logger.warning(f"⚠️  Improved clicking not available, using fallback for '{description}'")
            return await self.click(f"//*[contains(text(), '{description}')]")

    async def smart_type(self, text: str, input_description: str = None) -> dict:
        """
        Type text into an input field using improved clicking to find it

        Args:
            text: Text to type
            input_description: Description of input (e.g., "Search", "Email", "Password")

        Examples:
            await sarah.smart_type("hello world", "Search")
            await sarah.smart_type("test@example.com", "Email")
        """
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.improved_clicker:
            result = await self.improved_clicker.type_text(self.page, text, input_description)
            return result
        else:
            # Fallback
            logger.warning("⚠️  Improved typing not available, using basic typing")
            return await self.type_text(input_description or "input", text)

    async def press_key(self, key: str) -> dict:
        """
        Press a keyboard key

        Args:
            key: Key name (e.g., "Enter", "Escape", "Tab", "ArrowDown")

        Examples:
            await sarah.press_key("Enter")    # Submit form
            await sarah.press_key("Escape")   # Close dialog
            await sarah.press_key("Tab")      # Next field
        """
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.improved_clicker:
            result = await self.improved_clicker.press_key(self.page, key)
            return result
        else:
            # Fallback
            try:
                await self.page.keyboard.press(key)
                return {'success': True, 'message': f'Pressed {key}'}
            except Exception as e:
                return {'success': False, 'message': str(e)}

    # ========== UI NAVIGATION METHODS ==========

    async def hover(self, selector: str = None, x: int = None, y: int = None, smooth: bool = True) -> dict:
        """
        Hover over an element - perfect for YouTube thumbnails, buttons

        Args:
            selector: CSS selector to hover over
            x, y: Coordinates to hover (if no selector)
            smooth: Use smooth human-like mouse movement

        Examples:
            await sarah.hover("ytd-thumbnail")  # Hover video thumbnail
            await sarah.hover(x=500, y=300)     # Hover at coordinates
        """
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.ui_nav:
            return await self.ui_nav.hover(self.page, selector=selector, x=x, y=y, smooth=smooth)
        else:
            logger.warning("⚠️  UI Navigation not available")
            return {'success': False, 'message': 'UI Navigation not loaded'}

    async def double_click(self, selector: str = None, x: int = None, y: int = None) -> dict:
        """
        Double click an element (e.g., fullscreen video)

        Examples:
            await sarah.double_click("video")  # Double click video to fullscreen
        """
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.ui_nav:
            return await self.ui_nav.double_click(self.page, selector=selector, x=x, y=y)
        else:
            try:
                if selector:
                    await self.page.dblclick(selector)
                    return {'success': True}
                return {'success': False, 'message': 'UI Navigation not loaded'}
            except Exception as e:
                return {'success': False, 'message': str(e)}

    async def right_click(self, selector: str = None, x: int = None, y: int = None) -> dict:
        """
        Right click for context menu

        Examples:
            await sarah.right_click("video")  # Right click video
        """
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.ui_nav:
            return await self.ui_nav.right_click(self.page, selector=selector, x=x, y=y)
        else:
            return {'success': False, 'message': 'UI Navigation not loaded'}

    async def drag_and_drop(self, source_selector: str, target_selector: str) -> dict:
        """
        Drag element from source to target

        Examples:
            await sarah.drag_and_drop("#video1", "#playlist")
        """
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.ui_nav:
            return await self.ui_nav.drag_and_drop(self.page, source_selector, target_selector)
        else:
            return {'success': False, 'message': 'UI Navigation not loaded'}

    async def scroll_to_element(self, selector: str, smooth: bool = True) -> dict:
        """
        Scroll until element is visible

        Examples:
            await sarah.scroll_to_element("#video-title")
        """
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.ui_nav:
            return await self.ui_nav.scroll_to_element(self.page, selector, smooth=smooth)
        else:
            try:
                await self.page.locator(selector).first.scroll_into_view_if_needed()
                return {'success': True}
            except Exception as e:
                return {'success': False, 'message': str(e)}

    async def smooth_scroll(self, direction: str = 'down', pixels: int = 300, speed: float = 0.5) -> dict:
        """
        Smooth scrolling (more human-like)

        Examples:
            await sarah.smooth_scroll('down', pixels=500, speed=1.0)
        """
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.ui_nav:
            return await self.ui_nav.scroll_smooth(self.page, direction=direction, pixels=pixels, speed=speed)
        else:
            return await self.scroll(direction=direction, amount=pixels)

    async def wait_and_click(self, selector: str, timeout: int = 10000, hover_first: bool = True) -> dict:
        """
        Wait for element, optionally hover, then click (very human-like)

        Examples:
            await sarah.wait_and_click("ytd-thumbnail", hover_first=True)
        """
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.ui_nav:
            return await self.ui_nav.wait_and_click(self.page, selector, timeout=timeout, hover_first=hover_first)
        else:
            try:
                await self.page.wait_for_selector(selector, timeout=timeout)
                await self.page.click(selector)
                return {'success': True}
            except Exception as e:
                return {'success': False, 'message': str(e)}

    async def keyboard_shortcut(self, keys: str) -> dict:
        """
        Press keyboard shortcut (YouTube controls, etc.)

        Examples:
            await sarah.keyboard_shortcut("k")  # YouTube play/pause
            await sarah.keyboard_shortcut("f")  # YouTube fullscreen
            await sarah.keyboard_shortcut("ArrowRight")  # Skip forward
        """
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.ui_nav:
            return await self.ui_nav.keyboard_shortcut(self.page, keys)
        else:
            try:
                await self.page.keyboard.press(keys)
                return {'success': True}
            except Exception as e:
                return {'success': False, 'message': str(e)}

    # ========== YOUTUBE-SPECIFIC NAVIGATION ==========

    async def youtube_hover_video(self, video_index: int = 0) -> dict:
        """Hover over YouTube video thumbnail"""
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.youtube_nav:
            return await self.youtube_nav.hover_video(self.page, video_index)
        else:
            return {'success': False, 'message': 'YouTube navigator not loaded'}

    async def youtube_click_video(self, video_index: int = 0) -> dict:
        """Click YouTube video (with hover first)"""
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.youtube_nav:
            return await self.youtube_nav.click_video(self.page, video_index)
        else:
            return {'success': False, 'message': 'YouTube navigator not loaded'}

    async def youtube_play_pause(self) -> dict:
        """Toggle YouTube video play/pause (k key)"""
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.youtube_nav:
            return await self.youtube_nav.play_pause(self.page)
        else:
            return await self.keyboard_shortcut("k")

    async def youtube_fullscreen(self) -> dict:
        """Toggle YouTube fullscreen (f key)"""
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.youtube_nav:
            return await self.youtube_nav.fullscreen(self.page)
        else:
            return await self.keyboard_shortcut("f")

    async def youtube_skip_forward(self, seconds: int = 5) -> dict:
        """Skip forward in YouTube video"""
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.youtube_nav:
            return await self.youtube_nav.skip_forward(self.page, seconds)
        else:
            key = "l" if seconds >= 10 else "ArrowRight"
            return await self.keyboard_shortcut(key)

    async def youtube_skip_back(self, seconds: int = 5) -> dict:
        """Skip backward in YouTube video"""
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.youtube_nav:
            return await self.youtube_nav.skip_back(self.page, seconds)
        else:
            key = "j" if seconds >= 10 else "ArrowLeft"
            return await self.keyboard_shortcut(key)

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
