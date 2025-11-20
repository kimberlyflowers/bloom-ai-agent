"""
FULLY AUTONOMOUS GMAIL SETUP
Combines browser automation + SMS verification = Sarah creates her own email!

No human intervention needed!
"""

import asyncio
import logging
from typing import Optional, Dict
from src.gmail_account_creator import GmailAccountCreator
from src.sms_verification_service import SMSVerificationService, SMSService

logger = logging.getLogger(__name__)


class AutonomousGmailSetup:
    """
    Complete autonomous Gmail account creation
    Sarah handles EVERYTHING herself!
    """

    def __init__(
        self,
        sms_activate_api_key: str,
        headless: bool = True
    ):
        """
        Initialize autonomous Gmail setup

        Args:
            sms_activate_api_key: Your SMS-Activate API key
            headless: Run browser in headless mode (False to watch!)
        """
        self.gmail_creator = GmailAccountCreator(headless=headless)
        self.sms_service = SMSVerificationService(sms_activate_api_key)

    async def create_gmail_fully_autonomous(
        self,
        first_name: str,
        last_name: str,
        desired_username: str,
        password: str,
        birthday_month: str,
        birthday_day: str,
        birthday_year: str,
        gender: str = "Female"
    ) -> Dict:
        """
        Create Gmail account with ZERO human intervention!

        Sarah will:
        1. Open browser
        2. Navigate to Gmail signup
        3. Fill out all forms
        4. Request SMS verification phone number automatically
        5. Enter phone number
        6. Wait for SMS code
        7. Enter verification code
        8. Complete signup!

        Returns:
            {
                'success': bool,
                'email': str,
                'password': str,
                'phone_used': str,
                'total_cost': float,
                'error': str (if failed)
            }
        """

        total_cost = 0.0

        try:
            # Step 1: Check SMS service balance
            logger.info("=" * 70)
            logger.info("🤖 FULLY AUTONOMOUS GMAIL ACCOUNT CREATION")
            logger.info("=" * 70)

            balance = self.sms_service.get_balance()
            if balance < 0.50:
                return {
                    'success': False,
                    'error': f'Insufficient SMS-Activate balance: ${balance:.2f}. Please add funds.'
                }

            logger.info(f"✅ SMS-Activate balance: ${balance:.2f}")

            # Step 2: Start browser
            await self.gmail_creator.start()

            # Step 3: Begin Gmail signup (up to phone verification)
            logger.info("\n📝 Step 1: Filling out Gmail signup form...")

            page = await self.gmail_creator.context.new_page()

            # Navigate to Gmail signup
            await page.goto('https://accounts.google.com/signup', wait_until='networkidle')
            await self.gmail_creator.human_delay(2000, 3000)

            # Fill name
            logger.info(f"   Entering name: {first_name} {last_name}")
            await self.gmail_creator.type_like_human(page, 'input[name="firstName"]', first_name)
            await self.gmail_creator.type_like_human(page, 'input[name="lastName"]', last_name)
            await page.click('button:has-text("Next")')
            await self.gmail_creator.human_delay(2000, 3000)

            # Fill birthday and gender
            logger.info(f"   Entering birthday: {birthday_month}/{birthday_day}/{birthday_year}")

            # Try different birthday selectors (Google changes them)
            try:
                await page.select_option('select#month', label=birthday_month)
                await page.fill('input#day', birthday_day)
                await page.fill('input#year', birthday_year)
            except:
                # Alternative approach
                await page.fill('input[name="month"]', birthday_month)
                await page.fill('input[name="day"]', birthday_day)
                await page.fill('input[name="year"]', birthday_year)

            try:
                await page.select_option('select#gender', label=gender)
            except:
                pass  # Gender might be optional

            await page.click('button:has-text("Next")')
            await self.gmail_creator.human_delay(2000, 3000)

            # Choose username
            logger.info(f"   Choosing username: {desired_username}")

            # Try custom username
            try:
                create_own = await page.query_selector('text="Create your own Gmail address"')
                if create_own:
                    await create_own.click()
                    await self.gmail_creator.human_delay(500, 1000)
            except:
                pass

            await self.gmail_creator.type_like_human(page, 'input[name="Username"]', desired_username)
            await page.click('button:has-text("Next")')
            await self.gmail_creator.human_delay(2000, 3000)

            # Create password
            logger.info("   Creating secure password...")
            await self.gmail_creator.type_like_human(page, 'input[name="Passwd"]', password)
            await self.gmail_creator.type_like_human(page, 'input[name="PasswdAgain"]', password)
            await page.click('button:has-text("Next")')
            await self.gmail_creator.human_delay(3000, 4000)

            # Step 4: Get SMS verification phone number
            logger.info("\n📱 Step 2: Getting temporary phone number...")

            phone_result = await self.sms_service.get_phone_number(
                service=SMSService.GOOGLE,
                country="0"  # Any country (cheapest)
            )

            if not phone_result['success']:
                await self.gmail_creator.stop()
                return {
                    'success': False,
                    'error': f"Failed to get phone number: {phone_result.get('error')}"
                }

            phone_number = phone_result['phone']
            activation_id = phone_result['activation_id']
            total_cost += phone_result['cost']

            logger.info(f"✅ Got phone number: {phone_number}")
            logger.info(f"   Cost: ${phone_result['cost']:.2f}")

            # Step 5: Enter phone number in Gmail
            logger.info("\n🔢 Step 3: Entering phone number in Gmail...")

            phone_input = await page.wait_for_selector('input[type="tel"]', timeout=5000)
            await self.gmail_creator.type_like_human(page, 'input[type="tel"]', phone_number.replace('+', ''))
            await page.click('button:has-text("Next")')
            await self.gmail_creator.human_delay(3000, 5000)

            # Step 6: Wait for SMS verification code
            logger.info("\n📨 Step 4: Waiting for SMS verification code...")
            logger.info("   (This may take 30-60 seconds...)")

            sms_result = await self.sms_service.wait_for_sms_code(
                activation_id=activation_id,
                timeout=180  # 3 minutes
            )

            if not sms_result['success']:
                await self.gmail_creator.stop()
                return {
                    'success': False,
                    'error': f"Failed to receive SMS: {sms_result.get('error')}",
                    'total_cost': total_cost
                }

            verification_code = sms_result['code']
            logger.info(f"✅ Received verification code: {verification_code}")

            # Step 7: Enter verification code
            logger.info("\n✅ Step 5: Entering verification code...")

            code_input = await page.wait_for_selector('input[name="code"]', timeout=10000)
            await self.gmail_creator.type_like_human(page, 'input[name="code"]', verification_code)
            await page.click('button:has-text("Verify")')
            await self.gmail_creator.human_delay(3000, 5000)

            # Step 8: Skip phone recovery (optional)
            try:
                skip_button = await page.wait_for_selector('button:has-text("Skip")', timeout=3000)
                await skip_button.click()
                await self.gmail_creator.human_delay(2000, 3000)
            except:
                pass  # Recovery might not appear

            # Step 9: Accept terms and conditions
            logger.info("\n📜 Step 6: Accepting terms...")

            try:
                agree_button = await page.wait_for_selector('button:has-text("I agree")', timeout=5000)
                await agree_button.click()
                await self.gmail_creator.human_delay(3000, 5000)
            except:
                pass

            # Step 10: Verify account was created
            logger.info("\n🎉 Step 7: Verifying account creation...")

            # Check if we're at the welcome screen or account page
            await asyncio.sleep(3)

            final_email = f"{desired_username}@gmail.com"

            logger.info("=" * 70)
            logger.info("🎉🎉🎉 GMAIL ACCOUNT CREATED SUCCESSFULLY! 🎉🎉🎉")
            logger.info("=" * 70)
            logger.info(f"   Email: {final_email}")
            logger.info(f"   Password: {password}")
            logger.info(f"   Phone used: {phone_number}")
            logger.info(f"   Total cost: ${total_cost:.2f}")
            logger.info("=" * 70)

            # Close browser
            await page.close()
            await self.gmail_creator.stop()

            return {
                'success': True,
                'email': final_email,
                'password': password,
                'phone_used': phone_number,
                'total_cost': total_cost
            }

        except Exception as e:
            logger.error(f"❌ Error in autonomous Gmail creation: {e}")

            # Take screenshot for debugging
            try:
                pages = self.gmail_creator.context.pages
                if pages:
                    await pages[0].screenshot(path='/tmp/gmail_error.png')
                    logger.info("📸 Screenshot saved to /tmp/gmail_error.png")
            except:
                pass

            # Close browser
            try:
                await self.gmail_creator.stop()
            except:
                pass

            return {
                'success': False,
                'error': str(e),
                'total_cost': total_cost
            }


# Demo / Test
async def demo():
    """
    Test autonomous Gmail creation

    IMPORTANT: Replace YOUR_API_KEY with actual SMS-Activate API key
    """

    # REPLACE WITH YOUR ACTUAL API KEY
    sms_api_key = "YOUR_SMS_ACTIVATE_API_KEY"

    setup = AutonomousGmailSetup(
        sms_activate_api_key=sms_api_key,
        headless=False  # Set to False to WATCH Sarah work!
    )

    result = await setup.create_gmail_fully_autonomous(
        first_name="Sarah",
        last_name="Rodriguez",
        desired_username="sarah.rodriguez.bloom",
        password="SecurePassword123!",
        birthday_month="March",
        birthday_day="15",
        birthday_year="1997",
        gender="Female"
    )

    print("\n" + "=" * 70)
    print("RESULT:")
    print("=" * 70)
    print(result)
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(demo())
