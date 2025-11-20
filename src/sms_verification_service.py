"""
SMS Verification Service - Automated Phone Verification
Uses SMS-Activate API to get temporary phone numbers and receive SMS codes

API Docs: https://sms-activate.org/en/api2
"""

import asyncio
import logging
import requests
from typing import Optional, Dict
from enum import Enum

logger = logging.getLogger(__name__)


class SMSService(Enum):
    """Supported SMS services"""
    GOOGLE = "go"  # Gmail/Google
    TIKTOK = "tiktok"
    TWITTER = "tw"
    INSTAGRAM = "ig"


class SMSVerificationService:
    """
    Automated SMS verification using SMS-Activate

    Cost: ~$0.50-1 per verification
    """

    def __init__(self, api_key: str):
        """
        Initialize SMS verification service

        Args:
            api_key: Your SMS-Activate API key
                    Get one at: https://sms-activate.org/
        """
        self.api_key = api_key
        self.base_url = "https://api.sms-activate.org/stubs/handler_api.php"
        self.activation_id = None
        self.phone_number = None

    def _make_request(self, action: str, **params) -> str:
        """Make API request to SMS-Activate"""
        params['api_key'] = self.api_key
        params['action'] = action

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.text

        except Exception as e:
            logger.error(f"❌ SMS-Activate API error: {e}")
            raise

    def get_balance(self) -> float:
        """
        Check account balance

        Returns:
            Balance in USD
        """
        try:
            result = self._make_request('getBalance')

            if result.startswith('ACCESS_BALANCE:'):
                balance = float(result.split(':')[1])
                logger.info(f"💰 SMS-Activate balance: ${balance:.2f}")
                return balance
            else:
                logger.error(f"Error getting balance: {result}")
                return 0.0

        except Exception as e:
            logger.error(f"Error checking balance: {e}")
            return 0.0

    async def get_phone_number(
        self,
        service: SMSService = SMSService.GOOGLE,
        country: str = "0"  # 0 = any country (cheapest)
    ) -> Dict[str, str]:
        """
        Get a temporary phone number for verification

        Args:
            service: Which service to verify (Google, TikTok, etc.)
            country: Country code (0 = any, 12 = Russia, 187 = USA, etc.)

        Returns:
            {
                'success': bool,
                'phone': str,  # Full phone number with country code
                'activation_id': str,  # ID to check for SMS later
                'cost': float
            }
        """
        try:
            logger.info(f"📱 Requesting phone number for {service.value}...")

            result = self._make_request(
                'getNumber',
                service=service.value,
                country=country
            )

            # Expected format: ACCESS_NUMBER:activation_id:phone_number
            if result.startswith('ACCESS_NUMBER:'):
                parts = result.split(':')
                self.activation_id = parts[1]
                self.phone_number = parts[2]

                logger.info(f"✅ Got phone number: +{self.phone_number}")
                logger.info(f"   Activation ID: {self.activation_id}")

                return {
                    'success': True,
                    'phone': f"+{self.phone_number}",
                    'activation_id': self.activation_id,
                    'cost': 0.50  # Approximate cost
                }

            elif result == 'NO_NUMBERS':
                logger.error("❌ No phone numbers available right now")
                return {'success': False, 'error': 'No numbers available'}

            elif result == 'NO_BALANCE':
                logger.error("❌ Insufficient balance in SMS-Activate account")
                return {'success': False, 'error': 'Insufficient balance'}

            else:
                logger.error(f"❌ Unexpected response: {result}")
                return {'success': False, 'error': result}

        except Exception as e:
            logger.error(f"Error getting phone number: {e}")
            return {'success': False, 'error': str(e)}

    async def wait_for_sms_code(
        self,
        activation_id: Optional[str] = None,
        timeout: int = 300,  # 5 minutes
        poll_interval: int = 10  # Check every 10 seconds
    ) -> Dict[str, str]:
        """
        Wait for SMS verification code to arrive

        Args:
            activation_id: ID from get_phone_number (optional if already set)
            timeout: Max seconds to wait
            poll_interval: Seconds between checks

        Returns:
            {
                'success': bool,
                'code': str,  # The verification code
                'full_sms': str  # Complete SMS text
            }
        """
        if activation_id:
            self.activation_id = activation_id

        if not self.activation_id:
            return {'success': False, 'error': 'No activation ID'}

        logger.info(f"📨 Waiting for SMS code (timeout: {timeout}s)...")

        elapsed = 0
        while elapsed < timeout:
            try:
                # Check for SMS
                result = self._make_request(
                    'getStatus',
                    id=self.activation_id
                )

                # STATUS_WAIT_CODE = waiting for SMS
                if result == 'STATUS_WAIT_CODE':
                    logger.info(f"   ⏳ Still waiting... ({elapsed}s elapsed)")

                # STATUS_OK:code = SMS received!
                elif result.startswith('STATUS_OK:'):
                    code = result.split(':')[1]
                    logger.info(f"✅ SMS code received: {code}")

                    # Mark as completed
                    self._make_request(
                        'setStatus',
                        id=self.activation_id,
                        status=6  # 6 = activation complete
                    )

                    return {
                        'success': True,
                        'code': code,
                        'full_sms': f"Your verification code is: {code}"
                    }

                # STATUS_CANCEL = cancelled/expired
                elif result == 'STATUS_CANCEL':
                    logger.error("❌ Activation was cancelled")
                    return {'success': False, 'error': 'Activation cancelled'}

                else:
                    logger.warning(f"Unexpected status: {result}")

            except Exception as e:
                logger.error(f"Error checking SMS status: {e}")

            # Wait before next check
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        # Timeout reached
        logger.error(f"❌ Timeout waiting for SMS ({timeout}s)")

        # Cancel activation to get refund
        try:
            self._make_request(
                'setStatus',
                id=self.activation_id,
                status=8  # 8 = cancel activation (refund)
            )
            logger.info("💰 Activation cancelled - balance refunded")
        except:
            pass

        return {'success': False, 'error': 'Timeout waiting for SMS'}

    async def cancel_activation(self, activation_id: Optional[str] = None):
        """
        Cancel activation and get refund
        (Use if you don't need the number anymore)
        """
        if activation_id:
            self.activation_id = activation_id

        if not self.activation_id:
            return

        try:
            self._make_request(
                'setStatus',
                id=self.activation_id,
                status=8  # 8 = cancel (refund)
            )
            logger.info("✅ Activation cancelled - refunded")
        except Exception as e:
            logger.error(f"Error cancelling activation: {e}")


# Demo usage
async def demo():
    """
    Demo of automated SMS verification

    To use:
    1. Sign up at https://sms-activate.org/
    2. Add $5-10 to your balance
    3. Get your API key from the profile page
    4. Replace 'YOUR_API_KEY' below
    """

    # REPLACE WITH YOUR ACTUAL API KEY
    api_key = "YOUR_SMS_ACTIVATE_API_KEY"

    sms = SMSVerificationService(api_key)

    # Check balance
    balance = sms.get_balance()
    if balance < 0.50:
        print(f"❌ Insufficient balance: ${balance:.2f}")
        print("Please add funds at: https://sms-activate.org/")
        return

    print(f"✅ Balance: ${balance:.2f}")

    # Get phone number for Gmail verification
    phone_result = await sms.get_phone_number(
        service=SMSService.GOOGLE,
        country="0"  # Any country (cheapest)
    )

    if not phone_result['success']:
        print(f"❌ Failed to get phone: {phone_result.get('error')}")
        return

    print(f"✅ Got phone number: {phone_result['phone']}")
    print(f"   Cost: ${phone_result['cost']:.2f}")
    print("\n📝 Use this number in Gmail signup form...")
    print("   Waiting for SMS code...")

    # Wait for SMS verification code
    sms_result = await sms.wait_for_sms_code(timeout=300)  # 5 minutes

    if sms_result['success']:
        print(f"\n🎉 Got verification code: {sms_result['code']}")
        print("   Enter this code in Gmail to complete signup!")
    else:
        print(f"\n❌ Failed to receive SMS: {sms_result.get('error')}")


if __name__ == "__main__":
    print("=" * 60)
    print("SMS VERIFICATION SERVICE - DEMO")
    print("=" * 60)
    print("\nThis will cost ~$0.50-1 per verification")
    print("Make sure you have balance in SMS-Activate account!")
    print("\n" + "=" * 60 + "\n")

    asyncio.run(demo())
