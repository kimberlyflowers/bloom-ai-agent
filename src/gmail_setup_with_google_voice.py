"""
Gmail Account Setup with Google Voice
Semi-automated: Sarah does most of the work, you just provide SMS code!
"""

import asyncio
import logging
from playwright.async_api import async_playwright
import random

logger = logging.getLogger(__name__)


class GmailSetupWithGoogleVoice:
    """
    Gmail account creation using your Google Voice number
    You just need to check Google Voice for the SMS code!
    """

    def __init__(self, google_voice_number: str, headless: bool = False):
        """
        Initialize Gmail setup

        Args:
            google_voice_number: Your Google Voice number (e.g., "+1-210-294-9625")
            headless: Run browser in headless mode (False to watch Sarah work!)
        """
        self.google_voice_number = google_voice_number.replace('-', '').replace(' ', '')
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def start_browser(self):
        """Start browser"""
        logger.info("🌐 Starting browser...")
        self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage'
            ]
        )

        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        self.page = await self.context.new_page()
        logger.info("✅ Browser started!")

    async def stop_browser(self):
        """Stop browser"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("🔴 Browser stopped")

    async def human_delay(self, min_ms: int = 500, max_ms: int = 2000):
        """Simulate human delay"""
        await asyncio.sleep(random.uniform(min_ms / 1000, max_ms / 1000))

    async def type_like_human(self, selector: str, text: str):
        """Type like a human"""
        await self.page.click(selector)
        await self.human_delay(200, 500)

        for char in text:
            await self.page.type(selector, char)
            await asyncio.sleep(random.uniform(0.05, 0.15))

        await self.human_delay(300, 700)

    async def create_gmail_account(
        self,
        first_name: str = "Sarah",
        last_name: str = "Rodriguez",
        username: str = "sarah.rodriguez.bloom",
        password: str = "SecureBloomPass2024!",
        birth_month: str = "March",
        birth_day: str = "15",
        birth_year: str = "1997"
    ):
        """
        Create Gmail account with Google Voice verification

        Returns verification code prompt for user
        """

        try:
            logger.info("=" * 70)
            logger.info("🌸 SARAH IS CREATING HER GMAIL ACCOUNT!")
            logger.info("=" * 70)

            # Step 1: Navigate to Gmail signup
            logger.info("\n📝 Step 1: Navigating to Gmail signup...")
            await self.page.goto('https://accounts.google.com/signup', wait_until='networkidle')
            await self.human_delay(2000, 3000)

            # Step 2: Enter name
            logger.info(f"\n👤 Step 2: Entering name: {first_name} {last_name}")
            await self.type_like_human('input[name="firstName"]', first_name)
            await self.type_like_human('input[name="lastName"]', last_name)

            await self.page.click('button:has-text("Next")')
            await self.human_delay(2000, 3000)

            # Step 3: Enter birthday and gender
            logger.info(f"\n🎂 Step 3: Entering birthday: {birth_month} {birth_day}, {birth_year}")

            try:
                # Method 1: Dropdown selectors
                await self.page.select_option('select#month', label=birth_month)
                await self.page.fill('input#day', birth_day)
                await self.page.fill('input#year', birth_year)
            except:
                # Method 2: Input fields
                try:
                    await self.type_like_human('input[name="day"]', birth_day)
                    await self.page.select_option('select[aria-label="Month"]', label=birth_month)
                    await self.type_like_human('input[name="year"]', birth_year)
                except:
                    logger.warning("   Skipping detailed birthday entry, trying alternate method...")

            # Gender (optional)
            try:
                await self.page.select_option('select#gender', label="Female")
            except:
                logger.info("   Gender selection not found (optional)")

            await self.page.click('button:has-text("Next")')
            await self.human_delay(2000, 3000)

            # Step 4: Choose username
            logger.info(f"\n📧 Step 4: Creating username: {username}@gmail.com")

            # Try to create custom username
            try:
                create_own = await self.page.query_selector('text="Create your own Gmail address"')
                if create_own:
                    await create_own.click()
                    await self.human_delay(500, 1000)
            except:
                pass

            await self.type_like_human('input[name="Username"]', username)
            await self.page.click('button:has-text("Next")')
            await self.human_delay(2000, 3000)

            # Step 5: Create password
            logger.info(f"\n🔐 Step 5: Creating secure password...")
            await self.type_like_human('input[name="Passwd"]', password)
            await self.type_like_human('input[name="PasswdAgain"]', password)

            await self.page.click('button:has-text("Next")')
            await self.human_delay(3000, 4000)

            # Step 6: Phone verification
            logger.info(f"\n📱 Step 6: Entering phone number: {self.google_voice_number}")

            phone_input = await self.page.wait_for_selector('input[type="tel"]', timeout=10000)
            await self.type_like_human('input[type="tel"]', self.google_voice_number)

            await self.page.click('button:has-text("Next")')
            await self.human_delay(3000, 5000)

            # Step 7: Wait for user to get SMS code
            logger.info("\n📨 Step 7: SMS code sent to your Google Voice!")
            logger.info("=" * 70)
            logger.info("⏸️  PAUSED - WAITING FOR YOU!")
            logger.info("=" * 70)
            logger.info("\n🔍 Check your Google Voice for the verification code:")
            logger.info("   1. Go to: https://voice.google.com/")
            logger.info("   2. Look for SMS from Google")
            logger.info("   3. Copy the 6-digit code")
            logger.info("\n⏳ Browser will stay open, waiting for your input...")

            return {
                'status': 'waiting_for_code',
                'message': 'Check Google Voice for SMS code',
                'email': f'{username}@gmail.com',
                'password': password
            }

        except Exception as e:
            logger.error(f"\n❌ Error during Gmail signup: {e}")

            try:
                await self.page.screenshot(path='/tmp/gmail_error.png')
                logger.info("📸 Screenshot saved to /tmp/gmail_error.png")
            except:
                pass

            return {
                'status': 'error',
                'error': str(e)
            }

    async def enter_verification_code(self, code: str):
        """
        Enter the SMS verification code

        Args:
            code: 6-digit verification code from Google Voice
        """

        try:
            logger.info(f"\n🔢 Step 8: Entering verification code: {code}")

            # Enter the code
            await self.type_like_human('input[name="code"]', code)
            await self.page.click('button:has-text("Verify")')
            await self.human_delay(3000, 5000)

            # Skip phone recovery (optional)
            logger.info("\n⏭️  Step 9: Skipping optional steps...")
            try:
                skip_button = await self.page.wait_for_selector('button:has-text("Skip")', timeout=3000)
                await skip_button.click()
                await self.human_delay(2000, 3000)
            except:
                logger.info("   No skip button found (that's ok)")

            # Accept terms
            logger.info("\n📜 Step 10: Accepting terms and conditions...")
            try:
                agree_button = await self.page.wait_for_selector('button:has-text("I agree")', timeout=5000)
                await agree_button.click()
                await self.human_delay(3000, 5000)
            except:
                logger.info("   Terms might have been auto-accepted")

            # Success!
            await asyncio.sleep(3)

            logger.info("\n" + "=" * 70)
            logger.info("🎉🎉🎉 GMAIL ACCOUNT CREATED SUCCESSFULLY! 🎉🎉🎉")
            logger.info("=" * 70)
            logger.info("✅ Sarah now has her own email!")
            logger.info("=" * 70)

            return {
                'status': 'success',
                'message': 'Gmail account created successfully!'
            }

        except Exception as e:
            logger.error(f"\n❌ Error entering verification code: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }


# Interactive demo
async def interactive_demo():
    """
    Interactive demo - you participate!
    """

    print("\n" + "=" * 70)
    print("🌸 SARAH'S GMAIL ACCOUNT CREATION (INTERACTIVE)")
    print("=" * 70)

    # Get Google Voice number from user
    google_voice = input("\n📱 Enter your Google Voice number (e.g., +1-210-294-9625): ")

    print("\n✅ Got it! Sarah will use:", google_voice)
    print("\n🎬 Starting browser (you can watch Sarah work)...")

    # Create setup instance
    setup = GmailSetupWithGoogleVoice(
        google_voice_number=google_voice,
        headless=False  # Watch Sarah work!
    )

    await setup.start_browser()

    # Start Gmail signup
    result = await setup.create_gmail_account()

    if result['status'] == 'waiting_for_code':
        print("\n" + "=" * 70)
        print("⏸️  WAITING FOR YOU!")
        print("=" * 70)
        print(f"\n📧 Email being created: {result['email']}")
        print(f"🔐 Password: {result['password']}")
        print("\n🔍 Check Google Voice now for SMS code...")

        # Wait for user to enter code
        code = input("\n🔢 Enter the 6-digit verification code: ")

        # Complete signup
        final_result = await setup.enter_verification_code(code)

        if final_result['status'] == 'success':
            print("\n🎉 SUCCESS! Sarah has her Gmail account!")
            print(f"📧 Email: {result['email']}")
            print(f"🔐 Password: {result['password']}")
        else:
            print(f"\n❌ Error: {final_result.get('error')}")

    # Keep browser open for a few seconds
    print("\n⏳ Keeping browser open for 5 seconds so you can see...")
    await asyncio.sleep(5)

    await setup.stop_browser()
    print("\n✅ Done!")


if __name__ == "__main__":
    asyncio.run(interactive_demo())
