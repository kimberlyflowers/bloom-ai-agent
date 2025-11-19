"""
BLOOM AI Agent - Discord Integration
Discord ENCOURAGES bots - fully compliant and monetizable!
"""

import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


class DiscordMonitor:
    """
    Monitors Discord servers for IP protection discussions.
    Discord is PERFECT for this - bots are encouraged!
    """

    # Target server types and keywords
    TARGET_KEYWORDS = [
        # IP theft concerns
        'stolen', 'copyright', 'ai training', 'protect my art',
        'dmca', 'infringement', 'unauthorized use',

        # Creator pain points
        'someone copied my', 'theft', 'scraped my work',
        'ai generated', 'model trained on', 'dataset',

        # Protection questions
        'how to protect', 'watermark', 'copyright registration',
        'proof of ownership', 'blockchain', 'fingerprint',

        # BLOOM-relevant
        'content protection', 'ip protection', 'creator rights'
    ]

    # Recommended server types to join
    RECOMMENDED_SERVERS = [
        "Digital Art Communities",
        "Music Production Servers",
        "Game Development Communities",
        "3D Artist Hubs",
        "Photography Communities",
        "NFT/Web3 Creator Spaces",
        "Freelancer Networks",
        "Designer Communities"
    ]

    def __init__(self, bot_token: str = None):
        """Initialize Discord bot"""
        token = bot_token or os.getenv('DISCORD_BOT_TOKEN')

        # Create bot with necessary intents
        intents = discord.Intents.default()
        intents.message_content = True  # Need this to read messages
        intents.guilds = True
        intents.members = True

        self.bot = commands.Bot(command_prefix='!bloom ', intents=intents)
        self.token = token

        # Track our activity
        self.messages_seen = []
        self.responses_sent = []

        # Setup event handlers
        self._setup_handlers()

        logger.info("Discord bot initialized")

    def _setup_handlers(self):
        """Setup Discord event handlers"""

        @self.bot.event
        async def on_ready():
            """Called when bot connects"""
            logger.info(f'Discord bot connected as {self.bot.user}')
            logger.info(f'Connected to {len(self.bot.guilds)} servers')

            # List servers we're in
            for guild in self.bot.guilds:
                logger.info(f'  - {guild.name} ({guild.member_count} members)')

        @self.bot.event
        async def on_message(message):
            """Called when any message is posted in servers we're in"""

            # Ignore our own messages
            if message.author == self.bot.user:
                return

            # Check if message is relevant
            if self._is_relevant(message.content):
                logger.info(f'Relevant message found in #{message.channel.name}: {message.content[:100]}...')

                # Store for processing
                self.messages_seen.append({
                    'message_id': message.id,
                    'channel_id': message.channel.id,
                    'guild_id': message.guild.id if message.guild else None,
                    'author_id': message.author.id,
                    'content': message.content,
                    'timestamp': message.created_at.isoformat(),
                    'channel_name': message.channel.name,
                    'guild_name': message.guild.name if message.guild else 'DM'
                })

            # Process commands (for !bloom commands)
            await self.bot.process_commands(message)

    def _is_relevant(self, content: str) -> bool:
        """Check if message content is relevant to IP protection"""
        content_lower = content.lower()

        # Check for keywords
        for keyword in self.TARGET_KEYWORDS:
            if keyword in content_lower:
                return True

        # Check for question patterns
        question_patterns = [
            'how do i protect',
            'how to prevent',
            'what can i do',
            'help with copyright',
            'someone stole',
            'my work was copied'
        ]

        for pattern in question_patterns:
            if pattern in content_lower:
                return True

        return False

    def get_recent_opportunities(self, limit: int = 50) -> List[Dict]:
        """
        Get recent relevant messages we've seen.
        Returns list of opportunities sorted by recency.
        """
        # Sort by timestamp (most recent first)
        sorted_messages = sorted(
            self.messages_seen,
            key=lambda x: x['timestamp'],
            reverse=True
        )

        return sorted_messages[:limit]

    async def send_message(self, channel_id: int, content: str,
                          tracking_id: str = None) -> Optional[str]:
        """
        Send a message to a channel.
        Returns message ID if successful.
        """
        try:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.error(f"Channel {channel_id} not found")
                return None

            # Add UTM tracking if there's a BLOOM link
            tracked_content = self._add_tracking(content, tracking_id, 'discord_message')

            message = await channel.send(tracked_content)

            self.responses_sent.append({
                'message_id': message.id,
                'channel_id': channel_id,
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'tracking_id': tracking_id
            })

            logger.info(f"✅ Sent message to #{channel.name}")

            return str(message.id)

        except Exception as e:
            logger.error(f"Error sending message to channel {channel_id}: {e}")
            return None

    async def send_dm(self, user_id: int, content: str,
                     tracking_id: str = None) -> Optional[str]:
        """
        Send a DM to a user.
        Use sparingly - don't spam DMs!
        """
        try:
            user = await self.bot.fetch_user(user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return None

            # Add tracking
            tracked_content = self._add_tracking(content, tracking_id, 'discord_dm')

            message = await user.send(tracked_content)

            logger.info(f"✅ Sent DM to {user.name}")

            return str(message.id)

        except discord.Forbidden:
            logger.warning(f"Cannot DM user {user_id} (DMs disabled or not mutual server)")
            return None
        except Exception as e:
            logger.error(f"Error sending DM to user {user_id}: {e}")
            return None

    def _add_tracking(self, content: str, tracking_id: str, source: str) -> str:
        """Add UTM tracking to BLOOM URLs"""
        bloom_url = f"https://bloom.com?utm_source=discord&utm_medium=ai_agent&utm_campaign={tracking_id}&utm_content={source}"

        # If content doesn't have a URL, add it naturally
        if 'bloom.com' not in content.lower() and 'http' not in content.lower():
            content += f"\n\nLearn more: {bloom_url}"

        return content

    def start(self):
        """Start the Discord bot"""
        if not self.token:
            raise ValueError("Discord bot token not provided")

        logger.info("Starting Discord bot...")
        self.bot.run(self.token)


class DiscordStrategy:
    """
    Executes Discord marketing strategies.
    """

    def __init__(self, monitor: DiscordMonitor, agent):
        """Initialize with DiscordMonitor and BloomAIAgent"""
        self.monitor = monitor
        self.agent = agent

    async def execute_helpful_reply_strategy(self) -> bool:
        """
        Find relevant message and post helpful reply.
        Returns True if successful.
        """
        # Get recent opportunities
        opportunities = self.monitor.get_recent_opportunities(limit=10)

        if not opportunities:
            logger.info("No Discord opportunities found")
            return False

        # Pick best opportunity (most recent)
        best = opportunities[0]

        # Generate helpful reply
        context = {
            'message': best['content'],
            'channel': best['channel_name'],
            'guild': best['guild_name']
        }

        reply_text = self.agent.generate_content('discord_helpful_reply', context)

        # Send reply
        tracking_id = f"discord_reply_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        message_id = await self.monitor.send_message(
            channel_id=best['channel_id'],
            content=reply_text,
            tracking_id=tracking_id
        )

        return message_id is not None

    async def execute_educational_post_strategy(self, channel_id: int,
                                               topic: str = None) -> bool:
        """
        Post educational content in a channel.
        Use in channels where you have permission!
        """
        # Generate topic if not specified
        if not topic:
            topic = "protecting your creative work from unauthorized use"

        # Generate educational content
        context = {
            'topic': topic,
            'platform': 'discord'
        }

        content = self.agent.generate_content('discord_educational_post', context)

        # Post it
        tracking_id = f"discord_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        message_id = await self.monitor.send_message(
            channel_id=channel_id,
            content=content,
            tracking_id=tracking_id
        )

        return message_id is not None


# Discord-specific slash commands (optional)
class DiscordCommands(commands.Cog):
    """
    Optional slash commands for the bot.
    Users can interact with !bloom commands.
    """

    def __init__(self, bot, agent):
        self.bot = bot
        self.agent = agent

    @commands.command(name='protect')
    async def protect_command(self, ctx):
        """
        !bloom protect - Quick info about protecting IP
        """
        response = """
        🛡️ **Protecting Your Creative Work**

        Common methods:
        • Watermarking (can be removed)
        • Copyright registration (6-12 months)
        • Manual DMCA (30% success rate)

        **Better way:** BLOOM's automated protection
        ✅ Instant fingerprinting
        ✅ 24/7 monitoring
        ✅ Automated takedowns
        ✅ Blockchain proof

        Learn more: https://bloom.com?utm_source=discord&utm_medium=bot_command
        """

        await ctx.send(response)

        logger.info(f"!bloom protect command used by {ctx.author}")

    @commands.command(name='help')
    async def help_command(self, ctx):
        """
        !bloom help - Show available commands
        """
        response = """
        🤖 **BLOOM Bot Commands**

        `!bloom protect` - Learn about IP protection
        `!bloom help` - Show this message

        I also monitor channels for IP-related questions and offer help!

        Questions? Visit https://bloom.com
        """

        await ctx.send(response)


def setup_discord_bot(token: str, agent) -> DiscordMonitor:
    """
    Setup and configure Discord bot with all features.

    Usage:
        monitor = setup_discord_bot(token, agent)
        monitor.start()  # Runs forever
    """
    monitor = DiscordMonitor(bot_token=token)

    # Add commands cog
    monitor.bot.add_cog(DiscordCommands(monitor.bot, agent))

    logger.info("Discord bot fully configured")

    return monitor
