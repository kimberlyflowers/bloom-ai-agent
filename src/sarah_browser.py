"""
Sarah's Browser Controller with GLOBAL CLICKING FIX + Tutorial Learning Support
Complete replacement - fixes Intent vs Execution Gap
"""

import asyncio
import logging
import os
from typing import Optional, Dict, List, Any
from pathlib import Path
from PIL import Image
from io import BytesIO
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

# Try to import optional dependencies with better error handling
try:
    from src.live_screen_stream import PlaywrightScreenStreamer
    STREAMER_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️  Live screen streamer not available: {e}")
    STREAMER_AVAILABLE = False
    PlaywrightScreenStreamer = None

try:
    from src.advanced_browser_control import AdvancedBrowserController
    ADVANCED_CONTROL_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️  Advanced browser control not available: {e}")
    ADVANCED_CONTROL_AVAILABLE = False
    AdvancedBrowserController = None

# Sarah's improved clicking system - GLOBAL FIX
try:
    from src.sarah_improved_clicking import ImprovedClicking, SafeClicking
    IMPROVED_CLICKING_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️  Improved clicking not available: {e}")
    IMPROVED_CLICKING_AVAILABLE = False
    ImprovedClicking = None
    SafeClicking = None

# Sarah's UI navigation
try:
    from src.sarah_ui_navigation import UINavigator, YouTubeNavigator
    UI_NAVIGATION_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️  UI navigation not available: {e}")
    UI_NAVIGATION_AVAILABLE = False
    UINavigator = None
    YouTubeNavigator = None

logger = logging.getLogger(__name__)

class SarahBrowser:
    """
    Sarah's browser with GLOBAL CLICKING FIX + Tutorial Learning Support
    """

    def __init__(self, headless: bool = True, stream_port: int = 8765):
        self.headless = headless
        self.stream_port = stream_port

        # Playwright objects
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        # Screen streamer (optional)
        if STREAMER_AVAILABLE:
            self.streamer = PlaywrightScreenStreamer(port=stream_port, fps=2)
        else:
            self.streamer = None
            logger.warning("⚠️  Screen streaming disabled (module not available)")

        # Advanced browser controller (FIXED clicking) - optional
        if ADVANCED_CONTROL_AVAILABLE:
            self.advanced = AdvancedBrowserController()
        else:
            self.advanced = None
            logger.warning("⚠️  Advanced browser control disabled (module not available)")

        # Improved clicking system - GLOBAL FIX (optional)
        if IMPROVED_CLICKING_AVAILABLE:
            self.improved_clicker = ImprovedClicking()  # For captcha/popups ONLY
            self.safe_clicker = SafeClicking()  # For regular page clicks (filters voice/mic)
            logger.info("✅ Sarah's clicking loaded: ImprovedClicking (captcha) + SafeClicking (regular)")
        else:
            self.improved_clicker = None
            self.safe_clicker = None
            logger.warning("⚠️  Improved clicking disabled (module not available)")

        # UI Navigation (optional)
        if UI_NAVIGATION_AVAILABLE:
            self.ui_nav = UINavigator()
            self.youtube_nav = YouTubeNavigator()
            logger.info("✅ Sarah's UI navigation loaded")
        else:
            self.ui_nav = None
            self.youtube_nav = None
            logger.warning("⚠️  UI navigation disabled (module not available)")

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
                    '--disable-popup-blocking',
                    '--disable-prompt-on-repost'
                ],
                timeout=30000  # Add timeout
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

            # Connect components if available
            if self.streamer:
                self.streamer.set_browser_page(self.page)
            
            if self.advanced:
                self.advanced.set_page(self.page)

            self.is_running = True

            logger.info("✅ Sarah's browser is ready with GLOBAL CLICKING FIX!")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start browser: {e}", exc_info=True)
            return False

    async def navigate(self, url: str, wait_until: str = "networkidle") -> dict:
        """Navigate to URL"""
        if not self.is_running or not self.page:
            return {'success': False, 'message': 'Browser not running'}

        try:
            if not url.startswith(('http://', 'https://')):
                url = f'https://{url}'

            logger.info(f"🌐 Navigating to: {url}")
            await self.page.goto(url, wait_until=wait_until, timeout=30000)
            await asyncio.sleep(1)  # Extra settling time

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
            title = await self.page.title()
            return {
                'url': self.page.url,
                'title': title,
                'message': 'Page info retrieved'
            }
        except Exception as e:
            logger.error(f"❌ Failed to get page info: {e}")
            return {
                'url': self.current_url,
                'title': None,
                'message': 'Could not retrieve page info'
            }

    # ========== TUTORIAL LEARNING METHODS ==========
    
    async def take_screenshot(self) -> Image.Image:
        """Take screenshot and return as PIL Image - For Tutorial Learning"""
        if not self.page:
            raise RuntimeError("Browser page not available")
        
        screenshot_bytes = await self.page.screenshot(type="png", full_page=False)
        return Image.open(BytesIO(screenshot_bytes))

    async def click_coordinates(self, x: int, y: int):
        """Click at specific coordinates - For Tutorial Learning"""
        logger.info(f"🖱️  Clicking at ({x}, {y})")
        await self.page.mouse.click(x, y)
        await asyncio.sleep(0.5)

    async def type_with_delay(self, text: str, delay: int = 50):
        """Type text with delay - For Tutorial Learning"""
        logger.info(f"⌨️  Typing: {text}")
        await self.page.keyboard.type(text, delay=delay)

    async def dismiss_cookie_banner(self) -> bool:
        """Try to dismiss cookie consent banners"""
        logger.info("🍪 Looking for cookie banner...")

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
                    logger.info(f"✅ Dismissed cookie banner (clicked '{text}')")
                    return True
            except Exception:
                continue

        logger.info("ℹ️  No cookie banner found")
        return False

    # ========== GLOBAL CLICKING FIX METHODS ==========

    async def click(self, selector: str) -> dict:
        """Click element by selector - GLOBAL FIX"""
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        try:
            await self.page.click(selector, timeout=10000)
            return {'success': True, 'message': f'Clicked {selector}'}
        except Exception as e:
            logger.error(f"❌ Click failed for selector '{selector}': {e}")
            return {'success': False, 'message': str(e)}

    async def smart_click(self, description: str, timeout: int = 10000) -> dict:
        """
        GLOBAL CLICKING FIX - Sarah's improved clicking that actually works!
        
        Uses 8 different strategies to find and click ANY element by description.
        This fixes the Intent vs Execution Gap completely.
        """
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.safe_clicker:
            # Use SAFE clicking (filters voice/mic/camera) for regular page clicks
            result = await self.safe_clicker.click_element(self.page, description, timeout)
            logger.info(f"🎯 SAFE CLICK: {description} -> {result.get('success', False)}")
            return result
        else:
            # Fallback to basic click
            logger.warning(f"⚠️  Safe clicking not available, using fallback for '{description}'")
            try:
                # Try to find element by text
                element = await self.page.query_selector(f"text={description}")
                if element:
                    await element.click()
                    return {'success': True, 'message': f'Clicked element with text: {description}'}
                else:
                    return {'success': False, 'message': f'Element not found: {description}'}
            except Exception as e:
                return {'success': False, 'message': str(e)}

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
        if self.advanced:
            result = await self.advanced.click_by_description(description)
            if result.get('success'):
                logger.info(f"✅ ULTIMATE CLICK SUCCESS: Advanced control worked!")
                return result

        # STRATEGY 3: Universal cookie detector (for accept buttons)
        if any(word in description.lower() for word in ['accept', 'cookie', 'consent', 'ok', 'agree']):
            if self.advanced:
                result = await self.advanced.universal_cookie_detector()
                if result.get('success'):
                    logger.info(f"✅ ULTIMATE CLICK SUCCESS: Universal detector worked!")
                    return result
            else:
                # Try our own cookie banner detection
                success = await self.dismiss_cookie_banner()
                if success:
                    return {'success': True, 'message': 'Cookie banner dismissed'}

        # STRATEGY 4: Accessibility click
        if self.advanced:
            result = await self.advanced.accessibility_click()
            if result.get('success'):
                logger.info(f"✅ ULTIMATE CLICK SUCCESS: Accessibility worked!")
                return result

        # STRATEGY 5: Try basic selector patterns
        selector_patterns = [
            f"button:has-text('{description}')",
            f"a:has-text('{description}')",
            f"[aria-label*='{description}' i]",
            f"[title*='{description}' i]",
            f"//*[contains(text(), '{description}')]"
        ]

        for selector in selector_patterns:
            try:
                element = await self.page.query_selector(selector)
                if element:
                    await element.click()
                    logger.info(f"✅ ULTIMATE CLICK SUCCESS: Selector '{selector}' worked!")
                    return {'success': True, 'message': f'Clicked using selector: {selector}'}
            except Exception:
                continue

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
            logger.error(f"❌ Type failed for selector '{selector}': {e}")
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
            # Try to find input field
            if input_description:
                # Try common input selectors
                input_selectors = [
                    f"input[placeholder*='{input_description}']",
                    f"textarea[placeholder*='{input_description}']",
                    f"input[aria-label*='{input_description}']",
                    f"input[name*='{input_description.lower().replace(' ', '_')}']"
                ]
                
                for selector in input_selectors:
                    try:
                        element = await self.page.query_selector(selector)
                        if element:
                            await element.click()
                            await self.page.type(text, delay=50)
                            return {'success': True, 'message': f'Typed into {selector}'}
                    except Exception:
                        continue
            
            # Fallback: try to click first input field and type
            try:
                await self.page.click('input, textarea')
                await self.page.keyboard.type(text, delay=50)
                return {'success': True, 'message': 'Typed into first input field'}
            except Exception as e:
                return {'success': False, 'message': str(e)}

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
                logger.error(f"❌ Press key failed: {e}")
                return {'success': False, 'message': str(e)}

    # ========== UI NAVIGATION METHODS ==========

    async def hover(self, selector: str = None, x: int = None, y: int = None, smooth: bool = True) -> dict:
        """Hover over element"""
        if not self.page:
            return {'success': False, 'message': 'Browser not running'}

        if self.ui_nav:
            return await self.ui_nav.hover(self.page, selector=selector, x=x, y=y, smooth=smooth)
        else:
            try:
                if selector:
                    await self.page.hover(selector)
                elif x is not None and y is not None:
                    await self.page.mouse.move(x, y)
                else:
                    return {'success': False, 'message': 'No selector or coordinates provided'}
                
                return {'success': True, 'message': 'Hover successful'}
            except Exception as e:
                return {'success': False, 'message': str(e)}

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
            else:
                return {'success': False, 'message': f'Invalid direction: {direction}'}

            return {'success': True, 'message': f'Scrolled {direction}'}
        except Exception as e:
            logger.error(f"❌ Scroll failed: {e}")
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
            logger.error(f"❌ Google search failed: {e}")
            return {
                'success': False,
                'query': query,
                'message': f'Search failed: {str(e)}'
            }

    async def search_youtube(self, query: str) -> dict:
        """Search on YouTube"""
        try:
            # Navigate directly to YouTube search
            import urllib.parse
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
            logger.info(f"🔍 Searching YouTube for: {query}")

            result = await self.navigate(search_url)
            if not result['success']:
                return result

            # Wait for search results to load
            await asyncio.sleep(2)
            try:
                await self.page.wait_for_selector('a#video-title', timeout=10000)
            except Exception:
                logger.warning("Video titles not found, but page loaded")

            return {
                'success': True,
                'query': query,
                'platform': 'youtube',
                'message': f'Searched YouTube for "{query}"'
            }

        except Exception as e:
            logger.error(f"❌ YouTube search failed: {e}")
            return {
                'success': False,
                'query': query,
                'platform': 'youtube',
                'message': f'YouTube search failed: {str(e)}'
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
            logger.error(f"❌ Screenshot failed: {e}")
            return None

    async def close(self):
        """Close browser"""
        logger.info("🔴 Closing Sarah's browser...")

        if self.streamer:
            self.streamer.stop_streaming()

        if self.context:
            try:
                await self.context.close()
            except Exception as e:
                logger.error(f"❌ Error closing context: {e}")

        if self.browser:
            try:
                await self.browser.close()
            except Exception as e:
                logger.error(f"❌ Error closing browser: {e}")

        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception as e:
                logger.error(f"❌ Error stopping playwright: {e}")

        self.is_running = False
        logger.info("✅ Browser closed")

# Demo/testing
async def demo():
    """Test Sarah's browser with GLOBAL CLICKING FIX"""
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    browser = SarahBrowser(headless=True)  # Use headless for demo
    success = await browser.start()
    
    if not success:
        print("❌ Failed to start browser")
        return
    
    print("\n✅ Sarah's browser is running with GLOBAL CLICKING FIX!")
    print("Testing navigation...\n")

    try:
        # Test navigation
        result = await browser.navigate('https://www.google.com')
        print(f"Navigation result: {result}")

        await browser.wait(2)

        # Test search
        result = await browser.search_google('test search')
        print(f"Search result: {result}")

        await browser.wait(2)

        print("\n🎉 Demo complete! GLOBAL CLICKING FIX is active.")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await browser.close()
        print("\n✅ Browser closed cleanly")

if __name__ == '__main__':
    asyncio.run(demo())