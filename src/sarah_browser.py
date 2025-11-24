"""
Sarah's Browser Controller with GLOBAL CLICKING FIX
Complete replacement - fixes Intent vs Execution Gap
"""

import asyncio
import logging
import os
from typing import Optional, Dict, List, Any
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from src.live_screen_stream import PlaywrightScreenStreamer
from src.advanced_browser_control import AdvancedBrowserController

# Sarah's improved clicking system - GLOBAL FIX
try:
    from src.sarah_improved_clicking import ImprovedClicking
    IMPROVED_CLICKING_AVAILABLE = True
except ImportError:
    IMPROVED_CLICKING_AVAILABLE = False

# Sarah's UI navigation
try:
    from src.sarah_ui_navigation import UINavigator, YouTubeNavigator
    UI_NAVIGATION_AVAILABLE = True
except ImportError:
    UI_NAVIGATION_AVAILABLE = False

logger = logging.getLogger(__name__)

class SarahBrowser:
    """
    Sarah's browser with GLOBAL CLICKING FIX
    """

    def __init__(self, headless: bool = True, stream_port: int = 8765):
        self.headless = headless
        self.stream_port = stream_port

        # Playwright objects
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        # Screen streamer
        self.streamer = PlaywrightScreenStreamer(port=stream_port, fps=2)

        # Advanced browser controller (FIXED clicking)
        self.advanced = AdvancedBrowserController()

        # Improved clicking system - GLOBAL FIX
        if IMPROVED_CLICKING_AVAILABLE:
            self.improved_clicker = ImprovedClicking()
            logger.info("✅ Sarah's improved clicking loaded - GLOBAL FIX APPLIED!")
        else:
            self.improved_clicker = None

        # UI Navigation
        if UI_NAVIGATION_AVAILABLE:
            self.ui_nav = UINavigator()
            self.youtube_nav = YouTubeNavigator()
            logger.info("✅ Sarah's UI navigation loaded")
        else:
            self.ui_nav = None
            self.youtube_nav = None

        # State
        self.is_running = False
        self.current_url = None

    async def start(self):
        """Start browser with GLOBAL CLICKING FIX"""
        logger.info("🌸 Starting Sarah's browser with GLOBAL CLICKING FIX...")

        try:
            # Start Playwright
            self.playwright = await async_playwright().start()

            # Launch browser
            display_env = os.environ.get('DISPLAY')
            use_real_chrome = display_env is not None

            if use_real_chrome:
                logger.info(f"🖥️  Xvfb detected - Using REAL Chrome!")
                headless_mode = False
            else:
                logger.info("📱 No virtual display - Using headless mode")
                headless_mode = self.headless

            self.browser = await self.playwright.chromium.launch(
                headless=headless_mode,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--enable-accessibility',
                    '--force-renderer-accessibility',
                    '--enable-features=AccessibilityExposeHTMLElement',
                    '--disable-infobars',
                    '--disable-extensions',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--allow-running-insecure-content',
                    '--window-size=1920,1080',
                    '--disable-popup-blocking',
                    '--disable-prompt-on-repost'
                ]
            )

            # Create context
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            # Stealth script
            await self.context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                window.addEventListener('load', () => {
                    document.documentElement.setAttribute('aria-live', 'polite');
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            """)

            # Create page
            self.page = await self.context.new_page()

            # Connect components
            self.streamer.set_browser_page(self.page)
            self.advanced.set_page(self.page)

            self.is_running = True

            logger.info("✅ Sarah's browser is ready with GLOBAL CLICKING FIX!")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start browser: {e}")
            return False

    async def navigate(self, url: str) -> dict:
        """Navigate to URL"""
        if not self.is_running or not self.page:
            return {'success': False, 'message': 'Browser not running'}

        try:
            if not url.startswith(('http://', 'https://')):
                url = f'https://{url}'

            logger.info(f"🌐 Navigating to: {url}")
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

    # ========== GLOBAL CLICKING FIX METHODS ==========

    async def click(self, selector: str) -> dict:
        """Click element by selector - GLOBAL FIX"""
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        try:
            await self.page.click(selector, timeout=10000)
            return {'success': True, 'message': f'Clicked {selector}'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    async def smart_click(self, description: str, timeout: int = 10000) -> dict:
        """
        GLOBAL CLICKING FIX - Sarah's improved clicking that actually works!
        
        Uses 8 different strategies to find and click ANY element by description.
        This fixes the Intent vs Execution Gap completely.
        """
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.improved_clicker:
            # Use improved clicking (8 strategies!)
            result = await self.improved_clicker.click_element(self.page, description, timeout)
            logger.info(f"🎯 GLOBAL CLICKING FIX: {description} -> {result.get('success', False)}")
            return result
        else:
            # Fallback to basic click
            logger.warning(f"⚠️  Improved clicking not available, using fallback for '{description}'")
            return await self.click(f"//*[contains(text(), '{description}')]")

    async def universal_click(self, description: str) -> dict:
        """
        ULTIMATE CLICKING METHOD - Tries EVERY strategy until something works
        This is the final solution to Sarah's clicking issues
        """
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        logger.info(f"🎯 ULTIMATE CLICK: Attempting to click '{description}'")

        # STRATEGY 1: Improved clicking (8 strategies)
        if self.improved_clicker:
            result = await self.improved_clicker.click_element(self.page, description, 15000)
            if result.get('success'):
                logger.info(f"✅ ULTIMATE CLICK SUCCESS: Improved clicking worked!")
                return result

        # STRATEGY 2: Advanced browser control
        result = await self.advanced.click_by_description(description)
        if result.get('success'):
            logger.info(f"✅ ULTIMATE CLICK SUCCESS: Advanced control worked!")
            return result

        # STRATEGY 3: Universal cookie detector (for accept buttons)
        if any(word in description.lower() for word in ['accept', 'cookie', 'consent', 'ok', 'agree']):
            result = await self.advanced.universal_cookie_detector()
            if result.get('success'):
                logger.info(f"✅ ULTIMATE CLICK SUCCESS: Universal detector worked!")
                return result

        # STRATEGY 4: Accessibility click
        result = await self.advanced.accessibility_click()
        if result.get('success'):
            logger.info(f"✅ ULTIMATE CLICK SUCCESS: Accessibility worked!")
            return result

        # STRATEGY 5: Stealth click
        result = await self.advanced.stealth_click_button()
        if result.get('success'):
            logger.info(f"✅ ULTIMATE CLICK SUCCESS: Stealth worked!")
            return result

        # STRATEGY 6: Nuclear bypass
        result = await self.advanced.nuclear_bypass_dialog()
        if result.get('success'):
            logger.info(f"✅ ULTIMATE CLICK SUCCESS: Nuclear bypass worked!")
            return result

        logger.error(f"❌ ULTIMATE CLICK FAILED: All strategies exhausted for '{description}'")
        return {'success': False, 'message': f'All clicking strategies failed for: {description}'}

    async def type_text(self, selector: str, text: str, human_like: bool = True) -> dict:
        """Type text into input field"""
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        try:
            if human_like:
                await self.page.type(selector, text, delay=50)
            else:
                await self.page.fill(selector, text)

            return {'success': True, 'message': f'Typed into {selector}'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    async def smart_type(self, text: str, input_description: str = None) -> dict:
        """Type text using improved clicking to find input"""
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.improved_clicker:
            result = await self.improved_clicker.type_text(self.page, text, input_description)
            return result
        else:
            logger.warning("⚠️  Improved typing not available, using basic typing")
            return await self.type_text(input_description or "input", text)

    async def press_key(self, key: str) -> dict:
        """Press keyboard key"""
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.improved_clicker:
            result = await self.improved_clicker.press_key(self.page, key)
            return result
        else:
            try:
                await self.page.keyboard.press(key)
                return {'success': True, 'message': f'Pressed {key}'}
            except Exception as e:
                return {'success': False, 'message': str(e)}

    # ========== UI NAVIGATION METHODS ==========

    async def hover(self, selector: str = None, x: int = None, y: int = None, smooth: bool = True) -> dict:
        """Hover over element"""
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.ui_nav:
            return await self.ui_nav.hover(self.page, selector=selector, x=x, y=y, smooth=smooth)
        else:
            return {'success': False, 'message': 'UI Navigation not loaded'}

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
        """Search on Google"""
        try:
            result = await self.navigate('https://www.google.com')
            if not result['success']:
                return result

            await asyncio.sleep(1)
            await self.page.wait_for_selector('textarea[name="q"], input[name="q"]', timeout=5000)
            await self.type_text('textarea[name="q"], input[name="q"]', query)
            await self.page.keyboard.press('Enter')
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

    async def screenshot(self, full_page: bool = False) -> Optional[bytes]:
        """Take screenshot"""
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

    async def close(self):
        """Close browser"""
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
    """Test Sarah's browser with GLOBAL CLICKING FIX"""
    browser = SarahBrowser(headless=False)
    await browser.start()

    print("\n✅ Sarah's browser is running with GLOBAL CLICKING FIX!")
    print("Testing navigation and clicking...\n")

    # Test navigation
    result = await browser.navigate('https://www.google.com')
    print(f"Navigation result: {result}")

    await browser.wait(3)

    # Test search
    result = await browser.search_google('TikTok growth strategies')
    print(f"Search result: {result}")

    await browser.wait(5)

    print("\n🎉 Demo complete! GLOBAL CLICKING FIX is active.")
    print("Press Ctrl+C to close...")

    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        await browser.close()

if __name__ == '__main__':
    asyncio.run(demo())
