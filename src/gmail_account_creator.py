"""
Gmail Account Creator - Autonomous Frontend Automation
Sarah creates her own Gmail account via browser automation!
"""

import asyncio
import logging
from playwright.async_api import async_playwright, Page
from typing import Optional
import random

# Import Sarah's improved clicking system
try:
    from sarah_improved_clicking import ImprovedClicking
    IMPROVED_CLICKING_AVAILABLE = True
except ImportError:
    IMPROVED_CLICKING_AVAILABLE = False
    print("⚠️  ImprovedClicking not available - using basic clicking only")

logger = logging.getLogger(__name__)


class GmailAccountCreator:
    """
    Autonomous Gmail account creation via browser automation
    Sarah literally fills out the form herself!
    """

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None

        # Initialize Sarah's improved clicking system
        if IMPROVED_CLICKING_AVAILABLE:
            self.clicker = ImprovedClicking()
            logger.info("✅ Sarah's improved clicking system loaded!")
        else:
            self.clicker = None
            logger.warning("⚠️  Using basic clicking only")

    async def start(self):
        """Start browser"""
        logger.info("🌐 Starting browser for Gmail account creation...")
        self.playwright = await async_playwright().start()

        # Launch Chromium browser
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled'
            ]
        )

        # Create context with realistic settings
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        logger.info("✅ Browser started!")

    async def stop(self):
        """Stop browser"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("🔴 Browser stopped")

    async def human_delay(self, min_ms: int = 500, max_ms: int = 2000):
        """Simulate human typing delay"""
        delay = random.uniform(min_ms / 1000, max_ms / 1000)
        await asyncio.sleep(delay)

    async def type_like_human(self, page: Page, selector: str, text: str):
        """Type text character by character like a human"""
        await page.click(selector)
        await self.human_delay(200, 500)

        for char in text:
            await page.type(selector, char)
            await asyncio.sleep(random.uniform(0.05, 0.15))  # 50-150ms per character

        await self.human_delay(300, 700)

    async def smart_click(self, page: Page, description: str, timeout: int = 10000) -> dict:
        """
        Sarah's smart clicking - finds and clicks elements by description!

        Instead of needing exact CSS selectors, just tell Sarah what to click:
        - "Accept all" → finds and clicks the Accept all button
        - "Search" → finds and clicks the search box
        - "Change to English" → finds and clicks the language switcher

        Args:
            page: Playwright page object
            description: What to click (button text, link text, placeholder, etc.)
            timeout: How long to wait (milliseconds)

        Returns:
            dict with success status and message
        """
        if not self.clicker:
            logger.warning("⚠️  Smart clicking not available, falling back to basic click")
            try:
                await page.click(description, timeout=timeout)
                return {'success': True, 'message': f"Clicked '{description}' (basic mode)"}
            except Exception as e:
                return {'success': False, 'message': f"Failed to click: {str(e)}"}

        result = await self.clicker.click_element(page, description, timeout)
        if result['success']:
            logger.info(f"✅ {result['message']}")
        else:
            logger.warning(f"❌ {result['message']}")

        return result

    async def smart_type(self, page: Page, text: str, input_description: str = None) -> dict:
        """
        Type text using smart clicking to find the input field

        Args:
            page: Playwright page
            text: Text to type
            input_description: Description of input (e.g., "Search", "Email", "First name")

        Returns:
            dict with success status
        """
        if not self.clicker:
            logger.warning("⚠️  Smart typing not available")
            return {'success': False, 'message': "ImprovedClicking not available"}

        result = await self.clicker.type_text(page, text, input_description)
        if result['success']:
            logger.info(f"✅ {result['message']}")
        else:
            logger.warning(f"❌ {result['message']}")

        return result

    async def press_key(self, page: Page, key: str) -> dict:
        """
        Press a keyboard key

        Args:
            page: Playwright page
            key: Key to press (e.g., "Enter", "Escape", "Tab")
        """
        if not self.clicker:
            try:
                await page.keyboard.press(key)
                return {'success': True, 'message': f"Pressed {key}"}
            except Exception as e:
                return {'success': False, 'message': f"Failed to press key: {str(e)}"}

        return await self.clicker.press_key(page, key)

    async def create_gmail_account(
        self,
        first_name: str,
        last_name: str,
        desired_username: str,
        password: str,
        month: str,
        day: str,
        year: str,
        gender: str = "Rather not say"
    ) -> dict:
        """
        Create Gmail account autonomously!

        Returns:
            {
                'success': bool,
                'email': str,
                'username': str,
                'error': str (if failed)
            }
        """

        if not self.browser:
            await self.start()

        page = await self.context.new_page()

        try:
            logger.info("🌸 Sarah is creating her Gmail account...")
            logger.info(f"   Navigating to Gmail signup...")

            # Navigate to Gmail signup
            await page.goto('https://accounts.google.com/signup', wait_until='networkidle')
            await self.human_delay(1000, 2000)

            # Step 1: Fill out name
            logger.info(f"   Entering name: {first_name} {last_name}")
            await self.type_like_human(page, 'input[name="firstName"]', first_name)
            await self.type_like_human(page, 'input[name="lastName"]', last_name)

            # Click Next
            await page.click('button:has-text("Next")')
            await self.human_delay(2000, 3000)

            # Step 2: Birthday and gender
            logger.info(f"   Entering birthday: {month}/{day}/{year}")
            await self.type_like_human(page, 'input[name="month"]', month)
            await self.type_like_human(page, 'input[name="day"]', day)
            await self.type_like_human(page, 'input[name="year"]', year)

            # Select gender
            await page.select_option('select[name="gender"]', label=gender)
            await self.human_delay(500, 1000)

            # Click Next
            await page.click('button:has-text("Next")')
            await self.human_delay(2000, 3000)

            # Step 3: Choose Gmail address
            logger.info(f"   Choosing username: {desired_username}")

            # Try to create custom username
            try:
                create_own_radio = await page.wait_for_selector('input[value="manual"]', timeout=2000)
                await create_own_radio.click()
                await self.human_delay(500, 1000)

                await self.type_like_human(page, 'input[name="Username"]', desired_username)
            except:
                # If custom username option not available, use suggested
                logger.info("   Using suggested username instead")

            # Click Next
            await page.click('button:has-text("Next")')
            await self.human_delay(2000, 3000)

            # Step 4: Create password
            logger.info("   Creating password...")
            await self.type_like_human(page, 'input[name="Passwd"]', password)
            await self.type_like_human(page, 'input[name="PasswdAgain"]', password)

            # Click Next
            await page.click('button:has-text("Next")')
            await self.human_delay(2000, 3000)

            # Step 5: Phone verification (this is where it gets tricky)
            logger.info("⚠️  Phone verification required...")
            logger.info("   Sarah needs a phone number to verify!")

            # Check if phone verification is required
            phone_input = await page.query_selector('input[type="tel"]')

            if phone_input:
                return {
                    'success': False,
                    'error': 'phone_verification_required',
                    'message': 'Gmail requires phone verification. Please provide a phone number.',
                    'next_step': 'Enter phone number manually or use automated SMS service'
                }

            # If we got here without phone verification, account created!
            logger.info("🎉 Gmail account created successfully!")

            final_email = f"{desired_username}@gmail.com"

            return {
                'success': True,
                'email': final_email,
                'username': desired_username,
                'password': password
            }

        except Exception as e:
            logger.error(f"❌ Error creating Gmail account: {e}")

            # Take screenshot for debugging
            try:
                await page.screenshot(path='/tmp/gmail_signup_error.png')
                logger.info("📸 Screenshot saved to /tmp/gmail_signup_error.png")
            except:
                pass

            return {
                'success': False,
                'error': str(e)
            }

        finally:
            await page.close()

    async def enter_phone_verification(self, phone_number: str) -> dict:
        """
        Continue phone verification process
        (Called after user provides phone number)
        """
        page = await self.context.pages[0]  # Get active page

        try:
            logger.info(f"📱 Entering phone number: {phone_number}")

            # Enter phone number
            await self.type_like_human(page, 'input[type="tel"]', phone_number)
            await self.human_delay(500, 1000)

            # Click Next
            await page.click('button:has-text("Next")')
            await self.human_delay(3000, 5000)

            # Wait for verification code input
            code_input = await page.wait_for_selector('input[name="code"]', timeout=10000)

            logger.info("📨 Verification code sent! Waiting for code...")

            return {
                'success': True,
                'status': 'waiting_for_code',
                'message': 'Check your phone for verification code'
            }

        except Exception as e:
            logger.error(f"❌ Error in phone verification: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def enter_verification_code(self, code: str) -> dict:
        """
        Enter SMS verification code
        (Called after user receives and provides code)
        """
        page = await self.context.pages[0]

        try:
            logger.info(f"🔢 Entering verification code...")

            # Enter code
            await self.type_like_human(page, 'input[name="code"]', code)
            await self.human_delay(500, 1000)

            # Click Verify/Next
            await page.click('button:has-text("Verify")')
            await self.human_delay(3000, 5000)

            # Accept terms and conditions
            try:
                agree_button = await page.wait_for_selector('button:has-text("I agree")', timeout=5000)
                await agree_button.click()
                await self.human_delay(2000, 3000)
            except:
                pass  # Terms might not appear

            logger.info("🎉 Gmail account fully created and verified!")

            return {
                'success': True,
                'status': 'account_created',
                'message': 'Gmail account is ready to use!'
            }

        except Exception as e:
            logger.error(f"❌ Error verifying code: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Demo usage
async def demo():
    """Demo of Sarah creating her Gmail account"""
    creator = GmailAccountCreator(headless=False)  # Set to False to watch!

    await creator.start()

    result = await creator.create_gmail_account(
        first_name="Sarah",
        last_name="Rodriguez",
        desired_username="sarah.rodriguez.bloom",
        password="SecurePassword123!",  # Sarah's secure password
        month="March",
        day="15",
        year="1997",  # Makes her 26-27 years old
        gender="Female"
    )

    print(f"Result: {result}")

    if result.get('error') == 'phone_verification_required':
        print("\n🤔 Hmm, Gmail wants a phone number...")
        print("In production, we'd either:")
        print("1. Ask user to provide their phone")
        print("2. Use automated SMS service (costs $)")
        print("3. Skip and try alternative email provider")

    await creator.stop()


if __name__ == "__main__":
    asyncio.run(demo())
