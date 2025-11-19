"""
BLOOM AI Agent - Telegram Integration
Telegram is BUILT for bots - commercial activity fully allowed!
"""

import logging
import os
from datetime import datetime
from typing import List, Dict, Optional
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logger = logging.getLogger(__name__)


class TelegramMonitor:
    """
    Monitors Telegram groups/channels for IP protection discussions.
    Telegram LOVES bots - perfect for our use case!
    """

    # Target keywords (same as Discord)
    TARGET_KEYWORDS = [
        'stolen', 'copyright', 'ai training', 'protect',
        'dmca', 'infringement', 'theft', 'scraped',
        'unauthorized', 'copied', 'plagiarism',
        'watermark', 'fingerprint', 'blockchain'
    ]

    # Recommended group types
    RECOMMENDED_GROUPS = [
        "Crypto Art Communities",
        "NFT Creator Groups",
        "Digital Artist Channels",
        "Music Producer Groups",
        "Freelancer Networks",
        "Web3 Creator Communities",
        "Photography Groups",
        "Designer Communities"
    ]

    def __init__(self, bot_token: str = None):
        """Initialize Telegram bot"""
        token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')

        if not token:
            raise ValueError("Telegram bot token required")

        self.token = token
        self.bot = Bot(token=token)
        self.application = Application.builder().token(token).build()

        # Track activity
        self.messages_seen = []
        self.responses_sent = []

        # Setup handlers
        self._setup_handlers()

        logger.info("Telegram bot initialized")

    def _setup_handlers(self):
        """Setup message and command handlers"""

        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("protect", self.protect_command))
        self.application.add_handler(CommandHandler("help", self.help_command))

        # Message handler (for monitoring groups)
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

        logger.info("Telegram handlers configured")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_text = """
        👋 **Welcome to BLOOM IP Protection Bot!**

        I help creators protect their work from unauthorized use and AI training.

        Commands:
        /protect - Learn about IP protection
        /help - Show available commands

        I also monitor this group for IP-related questions and offer help!
        """

        await update.message.reply_text(welcome_text, parse_mode='Markdown')

        logger.info(f"/start command from {update.effective_user.username}")

    async def protect_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /protect command"""
        response = """
        🛡️ **Protecting Your Creative Work**

        **Common methods** (and their problems):
        • Watermarking - Can be removed by AI
        • Copyright registration - Takes 6-12 months
        • Manual DMCA - Only 30% success rate
        • Reverse image search - Misses 60% of theft

        **Better solution:** BLOOM
        ✅ Instant content fingerprinting
        ✅ 24/7 automated monitoring
        ✅ AI-powered theft detection
        ✅ One-click DMCA automation
        ✅ Blockchain proof of ownership

        Learn more: https://bloom.com?utm_source=telegram&utm_medium=bot
        """

        await update.message.reply_text(response, parse_mode='Markdown')

        logger.info(f"/protect command from {update.effective_user.username}")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        response = """
        🤖 **BLOOM Bot Help**

        **Commands:**
        /start - Welcome message
        /protect - IP protection info
        /help - This message

        **What I do:**
        I monitor this group for questions about:
        • Copyright and IP protection
        • AI training data concerns
        • Content theft issues
        • Unauthorized use

        When I see a relevant question, I offer helpful advice!

        **Questions?** Visit https://bloom.com
        """

        await update.message.reply_text(response, parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages (monitoring)"""

        message = update.message
        if not message or not message.text:
            return

        # Check if message is relevant
        if self._is_relevant(message.text):
            logger.info(f'Relevant message in {message.chat.title}: {message.text[:100]}...')

            # Store for processing
            self.messages_seen.append({
                'message_id': message.message_id,
                'chat_id': message.chat_id,
                'user_id': message.from_user.id,
                'username': message.from_user.username,
                'content': message.text,
                'timestamp': message.date.isoformat(),
                'chat_title': message.chat.title if message.chat.title else 'Private',
                'chat_type': message.chat.type
            })

    def _is_relevant(self, text: str) -> bool:
        """Check if message is relevant to IP protection"""
        text_lower = text.lower()

        # Check keywords
        for keyword in self.TARGET_KEYWORDS:
            if keyword in text_lower:
                return True

        # Check question patterns
        question_patterns = [
            'how to protect',
            'how do i',
            'what should i do',
            'someone stole',
            'help with',
            'advice on'
        ]

        for pattern in question_patterns:
            if pattern in text_lower:
                return True

        return False

    def get_recent_opportunities(self, limit: int = 50) -> List[Dict]:
        """Get recent relevant messages"""
        sorted_messages = sorted(
            self.messages_seen,
            key=lambda x: x['timestamp'],
            reverse=True
        )

        return sorted_messages[:limit]

    async def send_message(self, chat_id: int, text: str,
                          tracking_id: str = None) -> Optional[int]:
        """
        Send message to a chat.
        Returns message ID if successful.
        """
        try:
            # Add tracking
            tracked_text = self._add_tracking(text, tracking_id, 'telegram_message')

            message = await self.bot.send_message(
                chat_id=chat_id,
                text=tracked_text,
                parse_mode='Markdown'
            )

            self.responses_sent.append({
                'message_id': message.message_id,
                'chat_id': chat_id,
                'text': text,
                'timestamp': datetime.now().isoformat(),
                'tracking_id': tracking_id
            })

            logger.info(f"✅ Sent message to chat {chat_id}")

            return message.message_id

        except Exception as e:
            logger.error(f"Error sending message to chat {chat_id}: {e}")
            return None

    async def reply_to_message(self, chat_id: int, message_id: int,
                              text: str, tracking_id: str = None) -> Optional[int]:
        """Reply to a specific message"""
        try:
            tracked_text = self._add_tracking(text, tracking_id, 'telegram_reply')

            message = await self.bot.send_message(
                chat_id=chat_id,
                text=tracked_text,
                reply_to_message_id=message_id,
                parse_mode='Markdown'
            )

            logger.info(f"✅ Replied to message {message_id}")

            return message.message_id

        except Exception as e:
            logger.error(f"Error replying to message: {e}")
            return None

    def _add_tracking(self, text: str, tracking_id: str, source: str) -> str:
        """Add UTM tracking"""
        if tracking_id:
            bloom_url = f"https://bloom.com?utm_source=telegram&utm_medium=ai_agent&utm_campaign={tracking_id}&utm_content={source}"

            if 'bloom.com' not in text.lower():
                text += f"\n\nLearn more: {bloom_url}"

        return text

    def start(self):
        """Start the Telegram bot"""
        logger.info("Starting Telegram bot...")
        self.application.run_polling()


class TelegramStrategy:
    """
    Executes Telegram marketing strategies.
    """

    def __init__(self, monitor: TelegramMonitor, agent):
        self.monitor = monitor
        self.agent = agent

    async def execute_helpful_reply_strategy(self) -> bool:
        """Find and reply to relevant message"""

        opportunities = self.monitor.get_recent_opportunities(limit=10)

        if not opportunities:
            logger.info("No Telegram opportunities found")
            return False

        # Pick best (most recent)
        best = opportunities[0]

        # Generate reply
        context = {
            'message': best['content'],
            'chat': best['chat_title'],
            'platform': 'telegram'
        }

        reply_text = self.agent.generate_content('telegram_helpful_reply', context)

        # Send reply
        tracking_id = f"telegram_reply_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        message_id = await self.monitor.reply_to_message(
            chat_id=best['chat_id'],
            message_id=best['message_id'],
            text=reply_text,
            tracking_id=tracking_id
        )

        return message_id is not None

    async def execute_channel_post_strategy(self, channel_id: int,
                                           topic: str = None) -> bool:
        """Post educational content in a channel (if admin)"""

        if not topic:
            topic = "protecting digital content from AI scraping"

        # Generate content
        context = {
            'topic': topic,
            'platform': 'telegram'
        }

        content = self.agent.generate_content('telegram_channel_post', context)

        # Post it
        tracking_id = f"telegram_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        message_id = await self.monitor.send_message(
            chat_id=channel_id,
            text=content,
            tracking_id=tracking_id
        )

        return message_id is not None


def setup_telegram_bot(token: str, agent) -> TelegramMonitor:
    """
    Setup Telegram bot.

    Usage:
        monitor = setup_telegram_bot(token, agent)
        monitor.start()  # Runs forever
    """
    monitor = TelegramMonitor(bot_token=token)

    logger.info("Telegram bot configured")

    return monitor
