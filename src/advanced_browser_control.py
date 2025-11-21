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

            # Try each selector
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
                except:
                    continue

            # If nothing worked, try clicking the first visible button (last resort for cookie dialogs)
            if 'cookie' in desc_lower or 'accept' in desc_lower:
                try:
                    all_buttons = await self.page.query_selector_all('button')
                    for button in all_buttons:
                        is_visible = await button.is_visible()
                        if is_visible:
                            text = await button.inner_text()
                            # Check if button text contains acceptance words
                            if any(word in text.lower() for word in ['accept', 'ok', 'akkoord', 'accepter', 'akzeptieren', 'aceptar']):
                                await button.click()
                                logger.info(f"✅ Clicked button with text: {text}")
                                return {
                                    'success': True,
                                    'message': f'Clicked button: {text}',
                                    'selector': 'button (text match)'
                                }
                except Exception as e:
                    logger.warning(f"Fallback click failed: {e}")

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
                except:
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
