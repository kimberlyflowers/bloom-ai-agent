"""
Advanced Browser Control - Vision-Guided Interactions

Sarah can interact with ANY web interface like a human:
- Click elements based on visual descriptions
- Fill complex multi-step forms
- Scroll and observe changes
- Handle popups, modals, auth flows
- Upload files and media
- Interact with videos, canvases, embeds
- Test workflows and verify results

This enables Sarah to use:
- TikTok, Instagram, YouTube (browse, post, engage)
- Canva, Adobe (create graphics, videos)
- Email platforms (campaigns, automation)
- Code platforms (Replit, CodeSandbox)
- ANYTHING a human can do in a browser
"""

import asyncio
import logging
from typing import Optional, Dict, List, Any
from playwright.async_api import Page, ElementHandle

logger = logging.getLogger(__name__)


class AdvancedBrowserController:
    """
    Advanced browser interactions using vision and AI

    This enables Sarah to work with ANY web interface autonomously
    """

    def __init__(self, page: Optional[Page] = None):
        self.page = page

    def set_page(self, page: Page):
        """Set the browser page to control"""
        self.page = page

    async def click_by_description(self, description: str) -> Dict[str, Any]:
        """
        Click an element based on visual/text description
        Supports: main page, iframes, and coordinate-based clicking

        Args:
            description: What to click (e.g., "blue Login button", "search icon")

        Returns:
            Result dict with success status
        """
        if not self.page:
            return {'success': False, 'message': 'No page available'}

        try:
            # Strategy: Try multiple selectors based on description
            desc_lower = description.lower()
            selectors = []

            # Cookie dialog detection (high priority)
            if any(word in desc_lower for word in ['cookie', 'accept', 'consent', 'alles', 'tout', 'alle', 'gdpr']):
                # International cookie consent buttons
                selectors.extend([
                    # English
                    'button:has-text("Accept")',
                    'button:has-text("Accept all")',
                    'button:has-text("Accept All")',
                    'button:has-text("I Accept")',
                    'button:has-text("OK")',
                    '[aria-label*="Accept"]',
                    # Dutch
                    'button:has-text("Accepteren")',
                    'button:has-text("Alles accepteren")',
                    'button:has-text("Akkoord")',
                    # French
                    'button:has-text("Accepter")',
                    'button:has-text("Tout accepter")',
                    "button:has-text(\"J'accepte\")",
                    # German
                    'button:has-text("Akzeptieren")',
                    'button:has-text("Alle akzeptieren")',
                    'button:has-text("Einverstanden")',
                    # Spanish
                    'button:has-text("Aceptar")',
                    'button:has-text("Aceptar todo")',
                    # Common selectors
                    '[class*="accept"]',
                    '[class*="consent"]',
                    '[id*="accept"]',
                    '[data-testid*="accept"]',
                    'button[class*="cookie"]',
                    'a:has-text("Accept")',
                    'div[role="button"]:has-text("Accept")'
                ])

            # Extract key terms
            elif 'button' in desc_lower:
                # Try button selectors
                if 'login' in desc_lower or 'sign in' in desc_lower:
                    selectors = [
                        'button:has-text("Login")',
                        'button:has-text("Sign in")',
                        'button:has-text("Log in")',
                        '[type="submit"]',
                        'a:has-text("Login")'
                    ]
                elif 'signup' in desc_lower or 'sign up' in desc_lower or 'register' in desc_lower:
                    selectors = [
                        'button:has-text("Sign up")',
                        'button:has-text("Register")',
                        'button:has-text("Create account")',
                        'a:has-text("Sign up")'
                    ]
                elif 'submit' in desc_lower or 'send' in desc_lower:
                    selectors = [
                        'button:has-text("Submit")',
                        'button:has-text("Send")',
                        '[type="submit"]'
                    ]
                else:
                    # Generic button search
                    selectors = ['button', '[role="button"]']

            elif 'link' in desc_lower or 'menu' in desc_lower:
                selectors = ['a', '[role="link"]', 'nav a']

            elif 'icon' in desc_lower or 'image' in desc_lower:
                selectors = ['svg', 'img', '[role="img"]']

            else:
                # Generic clickable elements
                selectors = ['button', 'a', '[role="button"]', '[onclick]']

            # PHASE 1: Try main page selectors
            for selector in selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=3000)
                    if element:
                        await element.click()
                        logger.info(f"✅ Clicked element matching: {selector}")
                        return {
                            'success': True,
                            'message': f'Clicked {description}',
                            'selector': selector
                        }
                except Exception:
                    continue

            # PHASE 2: Try iframes (Google uses iframes for consent!)
            logger.info("🔍 Main page failed, checking iframes...")
            try:
                frames = self.page.frames
                for frame in frames:
                    for selector in selectors:
                        try:
                            element = await frame.wait_for_selector(selector, timeout=2000)
                            if element:
                                await element.click()
                                logger.info(f"✅ Clicked in iframe - selector: {selector}")
                                return {
                                    'success': True,
                                    'message': f'Clicked {description} in iframe',
                                    'selector': selector,
                                    'location': 'iframe'
                                }
                        except Exception:
                            continue
            except Exception as e:
                logger.warning(f"Iframe search failed: {e}")

            # PHASE 3: Fallback - scan visible buttons by text
            if 'cookie' in desc_lower or 'accept' in desc_lower:
                logger.info("🔍 Trying text-based button scan...")
                try:
                    # Try main page
                    all_buttons = await self.page.query_selector_all('button')
                    for button in all_buttons:
                        is_visible = await button.is_visible()
                        if is_visible:
                            text = await button.inner_text()
                            if any(word in text.lower() for word in ['accept', 'ok', 'akkoord', 'accepter', 'akzeptieren', 'aceptar']):
                                await button.click()
                                logger.info(f"✅ Clicked button with text: {text}")
                                return {
                                    'success': True,
                                    'message': f'Clicked button: {text}',
                                    'selector': 'button (text match)'
                                }

                    # Try iframes
                    for frame in self.page.frames:
                        frame_buttons = await frame.query_selector_all('button')
                        for button in frame_buttons:
                            is_visible = await button.is_visible()
                            if is_visible:
                                text = await button.inner_text()
                                if any(word in text.lower() for word in ['accept', 'ok', 'akkoord', 'accepter', 'akzeptieren', 'aceptar']):
                                    await button.click()
                                    logger.info(f"✅ Clicked iframe button with text: {text}")
                                    return {
                                        'success': True,
                                        'message': f'Clicked button: {text}',
                                        'selector': 'iframe button (text match)'
                                    }
                except Exception as e:
                    logger.warning(f"Text-based scan failed: {e}")

            # PHASE 4: Coordinate-based clicking (last resort)
            if 'cookie' in desc_lower or 'accept' in desc_lower:
                logger.info("🔍 Trying coordinate-based clicking...")
                try:
                    # Find any visible button and click its center
                    result = await self.page.evaluate('''() => {
                        const buttons = Array.from(document.querySelectorAll('button'));
                        for (const btn of buttons) {
                            const text = btn.innerText.toLowerCase();
                            if (text.includes('accept') || text.includes('ok') ||
                                text.includes('akkoord') || text.includes('accepter')) {
                                const rect = btn.getBoundingClientRect();
                                if (rect.width > 0 && rect.height > 0) {
                                    return {
                                        x: rect.left + rect.width / 2,
                                        y: rect.top + rect.height / 2,
                                        text: btn.innerText
                                    };
                                }
                            }
                        }
                        return null;
                    }''')

                    if result:
                        await self.page.mouse.click(result['x'], result['y'])
                        logger.info(f"✅ Coordinate click at ({result['x']}, {result['y']}) - {result['text']}")
                        return {
                            'success': True,
                            'message': f'Coordinate-clicked button: {result["text"]}',
                            'method': 'coordinate-based'
                        }
                except Exception as e:
                    logger.warning(f"Coordinate click failed: {e}")

            return {
                'success': False,
                'message': f'Could not find element: {description}'
            }

        except Exception as e:
            logger.error(f"Click failed: {e}")
            return {'success': False, 'message': str(e)}

    async def fill_form_field(self, field_description: str, value: str) -> Dict[str, Any]:
        """
        Fill a form field based on description

        Args:
            field_description: What field to fill (e.g., "email", "password", "username")
            value: Value to enter

        Returns:
            Result dict
        """
        if not self.page:
            return {'success': False, 'message': 'No page available'}

        try:
            desc_lower = field_description.lower()

            # Build selectors based on field type
            if 'email' in desc_lower:
                selectors = [
                    'input[type="email"]',
                    'input[name*="email"]',
                    'input[id*="email"]',
                    'input[placeholder*="email"]'
                ]
            elif 'password' in desc_lower:
                selectors = [
                    'input[type="password"]',
                    'input[name*="password"]',
                    'input[id*="password"]'
                ]
            elif 'username' in desc_lower or 'user' in desc_lower:
                selectors = [
                    'input[name*="username"]',
                    'input[name*="user"]',
                    'input[id*="username"]',
                    'input[placeholder*="username"]'
                ]
            elif 'search' in desc_lower:
                selectors = [
                    'input[type="search"]',
                    'input[name*="search"]',
                    'input[placeholder*="search"]',
                    'input[role="searchbox"]'
                ]
            else:
                # Generic text input
                selectors = [
                    'input[type="text"]',
                    'input:not([type])',
                    'textarea'
                ]

            # Try each selector
            for selector in selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=3000)
                    if element:
                        await element.fill(value)
                        logger.info(f"✅ Filled field '{field_description}' with value")
                        return {
                            'success': True,
                            'message': f'Filled {field_description}',
                            'selector': selector
                        }
                except Exception:
                    continue

            return {
                'success': False,
                'message': f'Could not find field: {field_description}'
            }

        except Exception as e:
            logger.error(f"Fill field failed: {e}")
            return {'success': False, 'message': str(e)}

    async def scroll_and_observe(self, direction: str = "down", distance: int = 500) -> Dict[str, Any]:
        """
        Scroll and capture what changes

        Args:
            direction: 'up', 'down', 'top', 'bottom'
            distance: Pixels to scroll

        Returns:
            Result with observation
        """
        if not self.page:
            return {'success': False, 'message': 'No page available'}

        try:
            # Scroll
            if direction == 'down':
                await self.page.evaluate(f'window.scrollBy(0, {distance})')
            elif direction == 'up':
                await self.page.evaluate(f'window.scrollBy(0, -{distance})')
            elif direction == 'top':
                await self.page.evaluate('window.scrollTo(0, 0)')
            elif direction == 'bottom':
                await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')

            # Wait for content to load
            await asyncio.sleep(1)

            # Get scroll position
            scroll_pos = await self.page.evaluate('''() => {
                return {
                    x: window.pageXOffset,
                    y: window.pageYOffset,
                    maxY: document.body.scrollHeight - window.innerHeight
                }
            }''')

            logger.info(f"📜 Scrolled {direction}, position: {scroll_pos['y']}")

            return {
                'success': True,
                'message': f'Scrolled {direction}',
                'scroll_position': scroll_pos
            }

        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return {'success': False, 'message': str(e)}

    async def upload_file(self, file_path: str, input_selector: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a file to a file input

        Args:
            file_path: Path to file to upload
            input_selector: Optional specific input selector

        Returns:
            Result dict
        """
        if not self.page:
            return {'success': False, 'message': 'No page available'}

        try:
            # Find file input
            selector = input_selector or 'input[type="file"]'

            file_input = await self.page.wait_for_selector(selector, timeout=5000)
            if file_input:
                await file_input.set_input_files(file_path)
                logger.info(f"✅ Uploaded file: {file_path}")
                return {
                    'success': True,
                    'message': f'Uploaded {file_path}'
                }
            else:
                return {
                    'success': False,
                    'message': 'No file input found'
                }

        except Exception as e:
            logger.error(f"File upload failed: {e}")
            return {'success': False, 'message': str(e)}

    async def wait_for_element(self, description: str, timeout: int = 10000) -> Dict[str, Any]:
        """
        Wait for an element to appear

        Args:
            description: What to wait for
            timeout: Max wait time in ms

        Returns:
            Result dict
        """
        if not self.page:
            return {'success': False, 'message': 'No page available'}

        try:
            # Build selector based on description
            desc_lower = description.lower()

            # Try to match common patterns
            if 'loading' in desc_lower or 'spinner' in desc_lower:
                # Wait for loading to disappear
                await self.page.wait_for_load_state('networkidle', timeout=timeout)
                return {
                    'success': True,
                    'message': 'Page finished loading'
                }
            else:
                # Wait for page to be generally ready
                await self.page.wait_for_load_state('domcontentloaded', timeout=timeout)
                return {
                    'success': True,
                    'message': 'Page content loaded'
                }

        except Exception as e:
            logger.error(f"Wait failed: {e}")
            return {'success': False, 'message': str(e)}

    async def extract_text(self, selector: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract text from page or element

        Args:
            selector: Optional selector to extract from

        Returns:
            Extracted text
        """
        if not self.page:
            return {'success': False, 'message': 'No page available'}

        try:
            if selector:
                element = await self.page.query_selector(selector)
                if element:
                    text = await element.inner_text()
                else:
                    return {'success': False, 'message': f'Element not found: {selector}'}
            else:
                # Get all visible text
                text = await self.page.evaluate('''() => {
                    return document.body.innerText;
                }''')

            return {
                'success': True,
                'text': text,
                'length': len(text)
            }

        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return {'success': False, 'message': str(e)}

    async def execute_workflow(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute a multi-step workflow

        Args:
            steps: List of steps, each with 'action' and params

        Example:
            steps = [
                {'action': 'navigate', 'url': 'gmail.com'},
                {'action': 'fill_field', 'field': 'email', 'value': 'sarah@bloom.ai'},
                {'action': 'click', 'description': 'Next button'},
                {'action': 'fill_field', 'field': 'password', 'value': 'secure123'},
                {'action': 'click', 'description': 'Sign in button'}
            ]

        Returns:
            Results from each step
        """
        if not self.page:
            return {'success': False, 'message': 'No page available'}

        results = []

        for i, step in enumerate(steps):
            action = step.get('action')
            logger.info(f"📋 Step {i+1}/{len(steps)}: {action}")

            try:
                if action == 'fill_field':
                    result = await self.fill_form_field(
                        step.get('field', ''),
                        step.get('value', '')
                    )
                elif action == 'click':
                    result = await self.click_by_description(step.get('description', ''))
                elif action == 'scroll':
                    result = await self.scroll_and_observe(
                        step.get('direction', 'down'),
                        step.get('distance', 500)
                    )
                elif action == 'wait':
                    await asyncio.sleep(step.get('seconds', 1))
                    result = {'success': True, 'message': f'Waited {step.get("seconds", 1)}s'}
                elif action == 'upload':
                    result = await self.upload_file(step.get('file_path', ''))
                else:
                    result = {'success': False, 'message': f'Unknown action: {action}'}

                results.append({
                    'step': i + 1,
                    'action': action,
                    'result': result
                })

                # Stop if step failed and marked as critical
                if not result.get('success') and step.get('critical', False):
                    logger.error(f"❌ Critical step {i+1} failed, stopping workflow")
                    break

                # Wait between steps
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"❌ Step {i+1} error: {e}")
                results.append({
                    'step': i + 1,
                    'action': action,
                    'result': {'success': False, 'message': str(e)}
                })

                if step.get('critical', False):
                    break

        # Check overall success
        success_count = sum(1 for r in results if r['result'].get('success'))

        return {
            'success': success_count == len(steps),
            'total_steps': len(steps),
            'successful_steps': success_count,
            'failed_steps': len(steps) - success_count,
            'results': results
        }

    async def detect_captcha(self) -> Dict[str, Any]:
        """
        Detect if there's a CAPTCHA on the page

        Returns:
            Detection result with captcha type if found
        """
        if not self.page:
            return {'success': False, 'message': 'No page available'}

        try:
            captcha_detected = False
            captcha_type = None
            captcha_info = {}

            # Check for reCAPTCHA
            recaptcha_frame = None
            for frame in self.page.frames:
                if 'recaptcha' in frame.url.lower():
                    recaptcha_frame = frame
                    captcha_detected = True
                    captcha_type = 'recaptcha'
                    break

            # Check for reCAPTCHA elements
            if not captcha_detected:
                recaptcha_elements = await self.page.query_selector_all('[class*="recaptcha"], [id*="recaptcha"], iframe[src*="recaptcha"]')
                if recaptcha_elements:
                    captcha_detected = True
                    captcha_type = 'recaptcha'

            # Check for hCaptcha
            hcaptcha_elements = await self.page.query_selector_all('[class*="hcaptcha"], [id*="hcaptcha"], iframe[src*="hcaptcha"]')
            if hcaptcha_elements:
                captcha_detected = True
                captcha_type = 'hcaptcha'

            # Check for image-based CAPTCHAs
            captcha_images = await self.page.query_selector_all('img[alt*="captcha"], img[src*="captcha"], canvas')
            if captcha_images and not captcha_detected:
                captcha_detected = True
                captcha_type = 'image-captcha'

            # Get page text to check for CAPTCHA instructions
            page_text = await self.page.evaluate('() => document.body.innerText.toLowerCase()')
            if any(phrase in page_text for phrase in ['verify you are human', 'prove you are not a robot', 'security check', 'select all images']):
                if not captcha_detected:
                    captcha_detected = True
                    captcha_type = 'unknown-captcha'

            return {
                'success': True,
                'captcha_detected': captcha_detected,
                'captcha_type': captcha_type,
                'captcha_info': captcha_info
            }

        except Exception as e:
            logger.error(f"CAPTCHA detection failed: {e}")
            return {'success': False, 'message': str(e)}

    async def solve_simple_captcha(self, vision_callback=None) -> Dict[str, Any]:
        """
        Attempt to solve simple image-based CAPTCHAs
        NOTE: This will NOT work for reCAPTCHA v3 (behavioral analysis)

        Args:
            vision_callback: Optional callback function that takes screenshot
                           and returns analysis (used with Claude vision)

        Returns:
            Result dict with success status
        """
        if not self.page:
            return {'success': False, 'message': 'No page available'}

        try:
            # First detect what kind of CAPTCHA we're dealing with
            detection = await self.detect_captcha()

            if not detection.get('captcha_detected'):
                return {
                    'success': False,
                    'message': 'No CAPTCHA detected on page'
                }

            captcha_type = detection.get('captcha_type')

            # Handle reCAPTCHA v2 checkbox
            if captcha_type == 'recaptcha':
                logger.info("🤖 Detected reCAPTCHA - attempting checkbox click")

                # Try to click the "I'm not a robot" checkbox
                for frame in self.page.frames:
                    if 'recaptcha' in frame.url.lower():
                        try:
                            checkbox = await frame.wait_for_selector('.recaptcha-checkbox-border', timeout=5000)
                            if checkbox:
                                await checkbox.click()
                                await asyncio.sleep(2)

                                # Check if we need to solve image challenge
                                image_challenge = await frame.query_selector('.rc-imageselect')
                                if image_challenge:
                                    return {
                                        'success': False,
                                        'message': 'reCAPTCHA image challenge detected - requires advanced solving',
                                        'captcha_type': 'recaptcha-image-challenge',
                                        'note': 'Sarah can see the challenge with vision, but solving requires pixel-perfect tile clicking'
                                    }
                                else:
                                    # Checkbox worked!
                                    return {
                                        'success': True,
                                        'message': 'reCAPTCHA checkbox solved!',
                                        'method': 'checkbox-click'
                                    }
                        except Exception as e:
                            logger.warning(f"reCAPTCHA checkbox click failed: {e}")

                return {
                    'success': False,
                    'message': 'reCAPTCHA detected but could not interact',
                    'captcha_type': captcha_type
                }

            # hCaptcha
            elif captcha_type == 'hcaptcha':
                return {
                    'success': False,
                    'message': 'hCaptcha detected - requires advanced solving',
                    'captcha_type': captcha_type,
                    'note': 'hCaptcha is designed to resist automation'
                }

            # Simple image CAPTCHA (less common now)
            elif captcha_type == 'image-captcha':
                if vision_callback:
                    # Use vision to analyze the CAPTCHA
                    screenshot = await self.page.screenshot()
                    analysis = await vision_callback(screenshot)

                    return {
                        'success': False,
                        'message': 'Image CAPTCHA detected - vision analysis available',
                        'captcha_type': captcha_type,
                        'vision_analysis': analysis,
                        'note': 'Sarah can SEE the CAPTCHA but needs human help to solve complex puzzles'
                    }
                else:
                    return {
                        'success': False,
                        'message': 'Image CAPTCHA detected but no vision callback provided',
                        'captcha_type': captcha_type
                    }

            else:
                return {
                    'success': False,
                    'message': f'Unknown CAPTCHA type: {captcha_type}',
                    'captcha_type': captcha_type
                }

        except Exception as e:
            logger.error(f"CAPTCHA solving failed: {e}")
            return {'success': False, 'message': str(e)}

    async def click_coordinates(self, x: int, y: int) -> Dict[str, Any]:
        """
        Click at specific pixel coordinates
        Useful for CAPTCHA tile clicking

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Result dict
        """
        if not self.page:
            return {'success': False, 'message': 'No page available'}

        try:
            await self.page.mouse.click(x, y)
            logger.info(f"✅ Clicked at coordinates ({x}, {y})")
            return {
                'success': True,
                'message': f'Clicked at ({x}, {y})'
            }
        except Exception as e:
            logger.error(f"Coordinate click failed: {e}")
            return {'success': False, 'message': str(e)}

    async def stealth_click_button(self, keywords: List[str] = None) -> Dict[str, Any]:
        """
        STEALTH MODE: Click button like a HUMAN (not a bot!)

        This is designed to bypass Google's bot detection by:
        - Using ONE method only (no multi-attempt fingerprint)
        - Random human-like delays (not fixed timing)
        - Natural mouse movement simulation
        - Hovering before clicking (humans pause)
        - Stopping after ONE attempt (success or fail)

        Google detects bots by watching for:
        - Multiple failed click attempts
        - Different interaction methods (keyboard, JS, coordinates)
        - Fixed timing patterns (sleep(0.1) consistently)
        - No mouse movement / hovering

        Args:
            keywords: Keywords to find buttons (default: accept/ok words)

        Returns:
            Result dict with success status
        """
        if not self.page:
            return {'success': False, 'message': 'No page available'}

        if keywords is None:
            keywords = ['accept', 'ok', 'akkoord', 'accepter', 'akzeptieren', 'aceptar', 'agree', 'consent']

        logger.info("🥷 STEALTH MODE ACTIVATED - Acting like a human...")

        try:
            import random

            # 🚫 EXCLUSION KEYWORDS - Skip management buttons
            exclude_keywords = [
                'beheren', 'manage', 'afwijzen', 'reject', 'weigeren', 'refuse',
                'opties', 'options', 'meer', 'more', 'instellingen', 'settings',
                'keuzes', 'choices', 'preferences', 'voorkeuren', 'aanpassen', 'customize',
                'personaliseer', 'personalize', 'weiger', 'deny', 'decline'
            ]

            # ✅ EXACT MATCH PHRASES - Prioritize "Accept All"
            exact_accept_all = [
                'alles accepteren',  # Dutch
                'accept all', 'accept all cookies', 'alles akkoord',
                'tout accepter', "j'accepte tout",  # French
                'alle akzeptieren', 'alles akzeptieren',  # German
                'aceptar todo', 'aceptar todas',  # Spanish
                'aceitar tudo'  # Portuguese
            ]

            # STEP 1: Human-like delay (humans read/think before clicking: 1.2-3.5 seconds)
            think_time = random.uniform(1.2, 3.5)
            logger.info(f"🧠 Human thinking time: {think_time:.2f}s")
            await asyncio.sleep(think_time)

            # STEP 2: Find the button using smart detection (one-shot!)
            button_info = await self.page.evaluate('''([keywords, exactMatches, excludeWords]) => {
                const buttons = Array.from(document.querySelectorAll('button, a, [role="button"]'));

                // PRIORITY 1: Exact "Accept All" matches
                for (const btn of buttons) {
                    if (btn.offsetWidth > 0 && btn.offsetHeight > 0) {
                        const text = btn.innerText.toLowerCase();
                        if (exactMatches.some(exact => text.includes(exact))) {
                            const rect = btn.getBoundingClientRect();
                            return {
                                found: true,
                                text: btn.innerText,
                                x: rect.left + rect.width / 2,
                                y: rect.top + rect.height / 2,
                                width: rect.width,
                                height: rect.height,
                                priority: 'exact'
                            };
                        }
                    }
                }

                // PRIORITY 2: Keyword matches (but skip exclusions)
                for (const btn of buttons) {
                    if (btn.offsetWidth > 0 && btn.offsetHeight > 0) {
                        const text = btn.innerText.toLowerCase();
                        if (keywords.some(kw => text.includes(kw))) {
                            // Skip if contains exclusion words
                            if (excludeWords.some(excl => text.includes(excl))) {
                                continue;
                            }
                            const rect = btn.getBoundingClientRect();
                            return {
                                found: true,
                                text: btn.innerText,
                                x: rect.left + rect.width / 2,
                                y: rect.top + rect.height / 2,
                                width: rect.width,
                                height: rect.height,
                                priority: 'keyword'
                            };
                        }
                    }
                }

                return {found: false};
            }''', [keywords, exact_accept_all, exclude_keywords])

            if not button_info.get('found'):
                logger.warning("🥷 Stealth: No valid button found")
                return {'success': False, 'message': 'No accept button found'}

            logger.info(f"🎯 Stealth: Found button '{button_info.get('text')}' ({button_info.get('priority')})")

            # STEP 3: Scroll button into view (humans scroll to see things)
            await self.page.evaluate('''([x, y]) => {
                window.scrollTo({
                    top: y - window.innerHeight / 2,
                    behavior: 'smooth'
                });
            }''', [button_info['x'], button_info['y']])

            # Wait for scroll animation (0.3-0.6 seconds)
            await asyncio.sleep(random.uniform(0.3, 0.6))

            # STEP 4: Move mouse to button with natural variance (humans don't click exact center)
            # Add +/- 20% random offset to simulate natural clicking
            offset_x = random.uniform(-button_info['width'] * 0.2, button_info['width'] * 0.2)
            offset_y = random.uniform(-button_info['height'] * 0.2, button_info['height'] * 0.2)

            click_x = button_info['x'] + offset_x
            click_y = button_info['y'] + offset_y

            logger.info(f"🖱️  Stealth: Moving mouse to ({click_x:.1f}, {click_y:.1f})")
            await self.page.mouse.move(click_x, click_y)

            # STEP 5: Hover before clicking (humans pause 0.4-1.2 seconds)
            hover_time = random.uniform(0.4, 1.2)
            logger.info(f"⏸️  Stealth: Hovering for {hover_time:.2f}s")
            await asyncio.sleep(hover_time)

            # STEP 6: Click with JS event dispatch (most reliable, single attempt)
            # Use the EXACT button we found (no searching again)
            click_result = await self.page.evaluate('''(btnText) => {
                const buttons = Array.from(document.querySelectorAll('button, a, [role="button"]'));

                // Find the exact button we identified earlier
                for (const btn of buttons) {
                    if (btn.innerText === btnText) {
                        // Dispatch natural click events
                        btn.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
                        btn.dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));
                        btn.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                        btn.click();
                        return {success: true, clicked: btnText};
                    }
                }
                return {success: false};
            }''', button_info['text'])

            if click_result.get('success'):
                # Random post-click delay (humans wait to see result: 0.8-1.5s)
                await asyncio.sleep(random.uniform(0.8, 1.5))
                logger.info(f"✅ STEALTH SUCCESS: Clicked '{button_info.get('text')}' naturally!")
                return {
                    'success': True,
                    'method': 'stealth-click',
                    'button_text': button_info.get('text'),
                    'attempts': 1  # Only ONE attempt!
                }
            else:
                logger.warning("🥷 Stealth: Click execution failed")
                return {'success': False, 'message': 'Click failed'}

        except Exception as e:
            logger.error(f"🥷 Stealth mode error: {e}")
            return {'success': False, 'message': str(e)}

    async def accessibility_click(self, target_keywords: List[str] = None) -> Dict[str, Any]:
        """
        ACCESSIBILITY-FIRST CLICK: Use assistive technology methods

        This mimics how screen readers and keyboard-only users interact with pages.
        By law (ADA/WCAG), all interactive elements MUST work with these methods!

        Benefits:
        - REQUIRED to work by law (websites must support accessibility)
        - Keyboard navigation is natural for assistive tech users
        - ARIA labels give us exact element identification
        - Less suspicious than automated mouse clicks
        - No complex visual detection needed

        Strategy:
        1. Try ARIA label matching (most reliable)
        2. Try role-based selection (semantic HTML)
        3. Try keyboard navigation (Tab + Enter/Space)
        4. Record which method works for future learning

        Args:
            target_keywords: Keywords to find in ARIA labels/text

        Returns:
            Result dict with success status and method used
        """
        if not self.page:
            return {'success': False, 'message': 'No page available'}

        if target_keywords is None:
            target_keywords = ['accept', 'ok', 'agree', 'consent', 'allow', 'enable']

        logger.info("♿ ACCESSIBILITY MODE: Using assistive technology methods...")

        try:
            import random
            import asyncio

            # ✅ EXACT MATCH PHRASES - Prioritize "Accept All"
            exact_accept_all = [
                'alles accepteren',  # Dutch - PRIORITY!
                'accept all', 'accept all cookies', 'alles akkoord',
                'tout accepter', "j'accepte tout",  # French
                'alle akzeptieren', 'alles akzeptieren',  # German
                'aceptar todo', 'aceptar todas',  # Spanish
                'aceitar tudo'  # Portuguese
            ]

            # 🚫 EXCLUSION KEYWORDS - Skip these
            exclude_keywords = [
                'beheren', 'manage', 'afwijzen', 'reject', 'weigeren', 'refuse',
                'opties', 'options', 'meer', 'more', 'instellingen', 'settings',
                'keuzes', 'choices', 'preferences', 'voorkeuren', 'aanpassen', 'customize',
                'personaliseer', 'personalize', 'weiger', 'deny', 'decline'
            ]

            # STEP 1: Try ARIA label matching (most reliable!)
            logger.info("🎯 Step 1: Looking for ARIA labels...")

            aria_result = await self.page.evaluate('''([keywords, exactMatches, excludeWords]) => {
                // Find elements by ARIA label
                const all_elements = document.querySelectorAll('[aria-label], [aria-labelledby], button, a, [role="button"]');

                // PRIORITY 1: Exact "Accept All" matches
                for (const elem of all_elements) {
                    if (elem.offsetWidth === 0 || elem.offsetHeight === 0) continue;

                    const ariaLabel = elem.getAttribute('aria-label') || '';
                    const ariaText = elem.innerText || '';
                    const combined = (ariaLabel + ' ' + ariaText).toLowerCase();

                    // Check for exact matches first
                    if (exactMatches.some(exact => combined.includes(exact))) {
                        const rect = elem.getBoundingClientRect();
                        return {
                            found: true,
                            method: 'aria-label-exact',
                            text: ariaLabel || ariaText,
                            selector: elem.id ? `#${elem.id}` : null,
                            x: rect.left + rect.width / 2,
                            y: rect.top + rect.height / 2,
                            priority: 'exact'
                        };
                    }
                }

                // PRIORITY 2: Keyword matches (but skip exclusions)
                for (const elem of all_elements) {
                    if (elem.offsetWidth === 0 || elem.offsetHeight === 0) continue;

                    const ariaLabel = elem.getAttribute('aria-label') || '';
                    const ariaText = elem.innerText || '';
                    const combined = (ariaLabel + ' ' + ariaText).toLowerCase();

                    // Check if any keyword matches
                    if (keywords.some(kw => combined.includes(kw))) {
                        // Skip reject/decline buttons
                        if (excludeWords.some(excl => combined.includes(excl))) {
                            continue;
                        }

                        const rect = elem.getBoundingClientRect();
                        return {
                            found: true,
                            method: 'aria-label',
                            text: ariaLabel || ariaText,
                            selector: elem.id ? `#${elem.id}` : null,
                            x: rect.left + rect.width / 2,
                            y: rect.top + rect.height / 2,
                            priority: 'keyword'
                        };
                    }
                }

                return {found: false};
            }''', [target_keywords, exact_accept_all, exclude_keywords])

            if aria_result.get('found'):
                logger.info(f"✅ Found via ARIA: '{aria_result.get('text')}'")

                # Human-like delay before interaction
                await asyncio.sleep(random.uniform(0.5, 1.2))

                # Click the element
                await self.page.mouse.click(aria_result['x'], aria_result['y'])
                await asyncio.sleep(random.uniform(0.3, 0.7))

                return {
                    'success': True,
                    'method': 'accessibility-aria',
                    'button_text': aria_result.get('text'),
                    'selector': aria_result.get('selector')
                }

            # STEP 2: Try keyboard navigation (Tab + Enter)
            logger.info("⌨️  Step 2: Trying keyboard navigation...")

            # Press Tab multiple times to cycle through focusable elements
            for i in range(10):  # Try up to 10 tab presses
                await self.page.keyboard.press('Tab')
                await asyncio.sleep(random.uniform(0.2, 0.4))

                # Check what's currently focused
                focused_info = await self.page.evaluate('''([keywords, exactMatches, excludeWords]) => {
                    const focused = document.activeElement;
                    if (!focused) return {found: false};

                    const text = (focused.innerText || focused.getAttribute('aria-label') || '').toLowerCase();

                    // PRIORITY 1: Exact matches
                    if (exactMatches.some(exact => text.includes(exact))) {
                        return {
                            found: true,
                            text: focused.innerText || focused.getAttribute('aria-label'),
                            tagName: focused.tagName,
                            priority: 'exact'
                        };
                    }

                    // PRIORITY 2: Keyword matches (but skip exclusions)
                    if (keywords.some(kw => text.includes(kw))) {
                        // Skip reject/decline/manage buttons
                        if (excludeWords.some(excl => text.includes(excl))) {
                            return {found: false};
                        }

                        return {
                            found: true,
                            text: focused.innerText || focused.getAttribute('aria-label'),
                            tagName: focused.tagName,
                            priority: 'keyword'
                        };
                    }

                    return {found: false};
                }''', [target_keywords, exact_accept_all, exclude_keywords])

                if focused_info.get('found'):
                    logger.info(f"✅ Focused on: '{focused_info.get('text')}'")

                    # Press Enter or Space to activate
                    await asyncio.sleep(random.uniform(0.3, 0.6))
                    await self.page.keyboard.press('Enter')
                    await asyncio.sleep(random.uniform(0.5, 1.0))

                    return {
                        'success': True,
                        'method': 'accessibility-keyboard',
                        'button_text': focused_info.get('text'),
                        'attempts': i + 1
                    }

            logger.warning("♿ Accessibility methods exhausted - no match found")
            return {'success': False, 'message': 'No accessible element found matching keywords'}

        except Exception as e:
            logger.error(f"♿ Accessibility click error: {e}")
            return {'success': False, 'message': str(e)}

    async def nuclear_bypass_dialog(self, keywords: List[str] = None) -> Dict[str, Any]:
        """
        NUCLEAR OPTION: Try EVERY method to bypass a dialog/popup
        Uses keyboard, JS events, cookie setting, element removal, etc.

        ⚠️ WARNING: This multi-method approach can trigger Google's bot detection!
        Multiple failed attempts = red flag. Consider using stealth_click_button() instead.

        This is the "no more Mr. Nice Guy" approach that tries everything
        until something works. Use sparingly for stubborn non-Google dialogs.

        Args:
            keywords: Keywords to find buttons (default: accept/ok words)

        Returns:
            Result dict with method that worked
        """
        if not self.page:
            return {'success': False, 'message': 'No page available'}

        if keywords is None:
            keywords = ['accept', 'ok', 'akkoord', 'accepter', 'akzeptieren', 'aceptar', 'agree', 'consent']

        logger.info("☢️  NUCLEAR BYPASS ACTIVATED - Trying all methods...")
        methods_tried = []

        # METHOD 1: Keyboard Navigation (most human-like)
        try:
            logger.info("🎹 Method 1: Keyboard Tab+Enter - SMART MODE")

            # 🚫 EXCLUSION KEYWORDS - Skip buttons with these words
            # (They open MORE dialogs instead of dismissing!)
            exclude_keywords = [
                'beheren', 'manage', 'afwijzen', 'reject', 'weigeren', 'refuse',
                'opties', 'options', 'meer', 'more', 'instellingen', 'settings',
                'keuzes', 'choices', 'preferences', 'voorkeuren', 'aanpassen', 'customize',
                'personaliseer', 'personalize', 'weiger', 'deny', 'decline'
            ]

            # ✅ EXACT MATCH PHRASES - Prioritize these "Accept All" variations
            exact_accept_all = [
                'alles accepteren',  # Dutch - THE ONE WE WANT!
                'accept all',
                'accept all cookies',
                'alles akkoord',
                'tout accepter',  # French
                "j'accepte tout",
                'alle akzeptieren',  # German
                'alles akzeptieren',
                'aceptar todo',  # Spanish
                'aceptar todas',
                'aceitar tudo'  # Portuguese
            ]

            # Tab through elements and press Enter on the RIGHT button
            for i in range(15):  # Increased from 10 to cover more buttons
                await self.page.keyboard.press('Tab')
                await asyncio.sleep(0.1)

                # Check what button is focused
                focused_text = await self.page.evaluate('''() => {
                    const el = document.activeElement;
                    return el ? el.innerText.toLowerCase() : '';
                }''')

                if not focused_text:
                    continue

                # 🎯 PRIORITY 1: Exact "Accept All" matches (highest priority!)
                if any(exact in focused_text for exact in exact_accept_all):
                    await self.page.keyboard.press('Enter')
                    await asyncio.sleep(1)
                    logger.info(f"🎯 NUCLEAR SUCCESS: Exact match - '{focused_text}'")
                    return {'success': True, 'method': 'keyboard-navigation-exact', 'button_text': focused_text, 'attempts': methods_tried}

                # ⚠️ PRIORITY 2: General accept keywords BUT skip management buttons
                if any(kw in focused_text for kw in keywords):
                    # Skip if it contains exclusion words (manage, settings, reject, etc.)
                    if any(excl in focused_text for excl in exclude_keywords):
                        logger.info(f"⏭️  Skipping management button: '{focused_text}'")
                        continue

                    # This looks like a real Accept button - click it!
                    await self.page.keyboard.press('Enter')
                    await asyncio.sleep(1)
                    logger.info(f"✅ NUCLEAR SUCCESS: Keyboard Enter on '{focused_text}'")
                    return {'success': True, 'method': 'keyboard-navigation', 'button_text': focused_text, 'attempts': methods_tried}

            methods_tried.append('keyboard-navigation (no valid buttons found)')
        except Exception as e:
            logger.warning(f"Keyboard method failed: {e}")
            methods_tried.append(f'keyboard-navigation (error: {e})')

        # METHOD 2: JavaScript Event Dispatch (bypass Playwright detection)
        try:
            logger.info("⚡ Method 2: JavaScript event dispatch - SMART MODE")
            result = await self.page.evaluate('''(keywords) => {
                // Exclusion words - skip these!
                const excludeWords = ['beheren', 'manage', 'afwijzen', 'reject', 'weigeren', 'refuse',
                                      'opties', 'options', 'meer', 'more', 'instellingen', 'settings',
                                      'keuzes', 'choices', 'preferences', 'voorkeuren', 'aanpassen', 'customize'];

                // Exact "Accept All" matches (try these first!)
                const exactMatches = ['alles accepteren', 'accept all', 'accept all cookies', 'alles akkoord',
                                      'tout accepter', "j'accepte tout", 'alle akzeptieren', 'alles akzeptieren',
                                      'aceptar todo', 'aceptar todas', 'aceitar tudo'];

                const buttons = Array.from(document.querySelectorAll('button, a, [role="button"]'));

                // PRIORITY 1: Try exact matches first
                for (const btn of buttons) {
                    const text = btn.innerText.toLowerCase();
                    if (exactMatches.some(exact => text.includes(exact))) {
                        btn.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
                        btn.dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));
                        btn.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                        btn.click();
                        return {success: true, text: btn.innerText, priority: 'exact'};
                    }
                }

                // PRIORITY 2: Try keyword matches (but skip exclusions)
                for (const btn of buttons) {
                    const text = btn.innerText.toLowerCase();
                    if (keywords.some(kw => text.includes(kw))) {
                        // Skip if contains exclusion words
                        if (excludeWords.some(excl => text.includes(excl))) {
                            continue;
                        }
                        btn.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
                        btn.dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));
                        btn.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                        btn.click();
                        return {success: true, text: btn.innerText, priority: 'keyword'};
                    }
                }
                return {success: false};
            }''', keywords)

            if result.get('success'):
                await asyncio.sleep(1)
                logger.info(f"✅ NUCLEAR SUCCESS: JS event dispatch on '{result.get('text')}' ({result.get('priority')})")
                return {'success': True, 'method': 'js-event-dispatch', 'button_text': result.get('text'), 'attempts': methods_tried}

            methods_tried.append('js-event-dispatch (no valid buttons)')
        except Exception as e:
            logger.warning(f"JS event dispatch failed: {e}")
            methods_tried.append(f'js-event-dispatch (error: {e})')

        # METHOD 3: Try iframes with JS dispatch
        try:
            logger.info("🖼️  Method 3: iframe JS dispatch - SMART MODE")
            for frame in self.page.frames:
                result = await frame.evaluate('''(keywords) => {
                    // Exclusion words - skip these!
                    const excludeWords = ['beheren', 'manage', 'afwijzen', 'reject', 'weigeren', 'refuse',
                                          'opties', 'options', 'meer', 'more', 'instellingen', 'settings',
                                          'keuzes', 'choices', 'preferences', 'voorkeuren', 'aanpassen', 'customize'];

                    // Exact "Accept All" matches (try these first!)
                    const exactMatches = ['alles accepteren', 'accept all', 'accept all cookies', 'alles akkoord',
                                          'tout accepter', "j'accepte tout", 'alle akzeptieren', 'alles akzeptieren',
                                          'aceptar todo', 'aceptar todas', 'aceitar tudo'];

                    const buttons = Array.from(document.querySelectorAll('button, a, [role="button"]'));

                    // PRIORITY 1: Try exact matches first
                    for (const btn of buttons) {
                        const text = btn.innerText.toLowerCase();
                        if (exactMatches.some(exact => text.includes(exact))) {
                            btn.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                            btn.click();
                            return {success: true, text: btn.innerText, priority: 'exact'};
                        }
                    }

                    // PRIORITY 2: Try keyword matches (but skip exclusions)
                    for (const btn of buttons) {
                        const text = btn.innerText.toLowerCase();
                        if (keywords.some(kw => text.includes(kw))) {
                            // Skip if contains exclusion words
                            if (excludeWords.some(excl => text.includes(excl))) {
                                continue;
                            }
                            btn.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                            btn.click();
                            return {success: true, text: btn.innerText, priority: 'keyword'};
                        }
                    }
                    return {success: false};
                }''', keywords)

                if result.get('success'):
                    await asyncio.sleep(1)
                    logger.info(f"✅ NUCLEAR SUCCESS: iframe JS dispatch on '{result.get('text')}' ({result.get('priority')})")
                    return {'success': True, 'method': 'iframe-js-dispatch', 'button_text': result.get('text'), 'attempts': methods_tried}

            methods_tried.append('iframe-js-dispatch (no valid buttons)')
        except Exception as e:
            logger.warning(f"iframe JS dispatch failed: {e}")
            methods_tried.append(f'iframe-js-dispatch (error: {e})')

        # METHOD 4: Remove CSS pointer-events blocking
        try:
            logger.info("🎨 Method 4: Override CSS pointer-events")
            await self.page.evaluate('''(keywords) => {
                // Remove pointer-events: none on everything
                const allElements = document.querySelectorAll('*');
                allElements.forEach(el => {
                    el.style.pointerEvents = 'auto';
                });

                // Now try clicking
                const buttons = Array.from(document.querySelectorAll('button, a, [role="button"]'));
                for (const btn of buttons) {
                    const text = btn.innerText.toLowerCase();
                    if (keywords.some(kw => text.includes(kw))) {
                        btn.click();
                        return true;
                    }
                }
                return false;
            }''', keywords)

            await asyncio.sleep(1)
            # Try our normal click now
            result = await self.click_by_description('accept all')
            if result.get('success'):
                logger.info("✅ NUCLEAR SUCCESS: CSS override + click")
                return {'success': True, 'method': 'css-override', 'attempts': methods_tried}

            methods_tried.append('css-override (failed)')
        except Exception as e:
            logger.warning(f"CSS override failed: {e}")
            methods_tried.append(f'css-override (error: {e})')

        # METHOD 5: Direct cookie manipulation (skip dialog entirely)
        try:
            logger.info("🍪 Method 5: Set consent cookies directly")
            url = self.page.url
            domain = None

            if 'google' in url:
                domain = '.google.com'
                # Google's consent cookie
                await self.page.context.add_cookies([{
                    'name': 'CONSENT',
                    'value': 'YES+',
                    'domain': domain,
                    'path': '/'
                }])
            elif 'youtube' in url:
                domain = '.youtube.com'
                await self.page.context.add_cookies([{
                    'name': 'CONSENT',
                    'value': 'YES+',
                    'domain': domain,
                    'path': '/'
                }])

            if domain:
                await self.page.reload()
                await asyncio.sleep(2)
                logger.info(f"✅ NUCLEAR SUCCESS: Set consent cookie for {domain}")
                return {'success': True, 'method': 'cookie-injection', 'attempts': methods_tried}

            methods_tried.append('cookie-injection (domain not supported)')
        except Exception as e:
            logger.warning(f"Cookie injection failed: {e}")
            methods_tried.append(f'cookie-injection (error: {e})')

        # METHOD 6: Remove the dialog element entirely (NUCLEAR!)
        try:
            logger.info("💣 Method 6: NUCLEAR - Remove dialog element")
            removed = await self.page.evaluate('''() => {
                // Find and remove common dialog/overlay elements
                const selectors = [
                    'dialog',
                    '[role="dialog"]',
                    '[class*="dialog"]',
                    '[class*="modal"]',
                    '[class*="popup"]',
                    '[class*="overlay"]',
                    '[class*="consent"]',
                    '[class*="cookie"]',
                    'iframe[src*="consent"]'
                ];

                let removed = 0;
                selectors.forEach(sel => {
                    const elements = document.querySelectorAll(sel);
                    elements.forEach(el => {
                        // Check if element has "accept" related text
                        if (el.innerText && el.innerText.toLowerCase().includes('accept')) {
                            el.remove();
                            removed++;
                        }
                    });
                });

                // Also remove any fixed overlays
                const allElements = document.querySelectorAll('*');
                allElements.forEach(el => {
                    const style = window.getComputedStyle(el);
                    if (style.position === 'fixed' && style.zIndex > 1000) {
                        const text = el.innerText?.toLowerCase() || '';
                        if (text.includes('cookie') || text.includes('consent') || text.includes('accept')) {
                            el.remove();
                            removed++;
                        }
                    }
                });

                return removed;
            }''')

            if removed > 0:
                await asyncio.sleep(0.5)
                logger.info(f"✅ NUCLEAR SUCCESS: Removed {removed} dialog elements")
                return {'success': True, 'method': 'element-removal', 'removed_count': removed, 'attempts': methods_tried}

            methods_tried.append('element-removal (nothing found)')
        except Exception as e:
            logger.warning(f"Element removal failed: {e}")
            methods_tried.append(f'element-removal (error: {e})')

        # METHOD 7: Brute force - click SMART (skip management buttons!)
        try:
            logger.info("🔨 Method 7: Brute force - SMART MODE")
            clicked = await self.page.evaluate('''(keywords) => {
                // Exclusion words - skip these even in brute force!
                const excludeWords = ['beheren', 'manage', 'afwijzen', 'reject', 'weigeren', 'refuse',
                                      'opties', 'options', 'meer', 'more', 'instellingen', 'settings',
                                      'keuzes', 'choices', 'preferences', 'voorkeuren', 'aanpassen', 'customize'];

                // Exact "Accept All" matches (try these first!)
                const exactMatches = ['alles accepteren', 'accept all', 'accept all cookies', 'alles akkoord'];

                const buttons = Array.from(document.querySelectorAll('button, a, [role="button"]'));
                let clicked = 0;

                // PRIORITY 1: Click exact matches first
                buttons.forEach(btn => {
                    if (btn.offsetWidth > 0 && btn.offsetHeight > 0) {
                        const text = btn.innerText.toLowerCase();
                        if (exactMatches.some(exact => text.includes(exact))) {
                            try {
                                btn.click();
                                clicked++;
                            } catch (e) {}
                        }
                    }
                });

                // PRIORITY 2: Click keyword matches (but skip exclusions)
                if (clicked === 0) {
                    buttons.forEach(btn => {
                        if (btn.offsetWidth > 0 && btn.offsetHeight > 0) {
                            const text = btn.innerText.toLowerCase();
                            if (keywords.some(kw => text.includes(kw))) {
                                // Skip if contains exclusion words
                                if (excludeWords.some(excl => text.includes(excl))) {
                                    return;
                                }
                                try {
                                    btn.click();
                                    clicked++;
                                } catch (e) {}
                            }
                        }
                    });
                }

                return clicked;
            }''', keywords)

            if clicked > 0:
                await asyncio.sleep(1)
                logger.info(f"✅ NUCLEAR SUCCESS: Smart brute forced {clicked} buttons")
                return {'success': True, 'method': 'brute-force-smart', 'clicked_count': clicked, 'attempts': methods_tried}

            methods_tried.append('brute-force (no valid buttons)')
        except Exception as e:
            logger.warning(f"Brute force failed: {e}")
            methods_tried.append(f'brute-force (error: {e})')

        # All methods failed
        logger.error("☢️  NUCLEAR BYPASS FAILED - All methods exhausted")
        return {
            'success': False,
            'message': 'All bypass methods failed',
            'methods_tried': methods_tried
        }
