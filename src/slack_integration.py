"""
BLOOM AI Agent - Slack Integration
Slack for B2B creator workspaces - higher value customers!
"""

import logging
import os
from datetime import datetime
from typing import List, Dict, Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse

logger = logging.getLogger(__name__)


class SlackMonitor:
    """
    Monitors Slack workspaces for IP protection discussions.
    Perfect for B2B - design agencies, studios, freelance collectives.
    """

    TARGET_KEYWORDS = [
        'copyright', 'ip protection', 'client theft',
        'protect our work', 'portfolio stolen', 'contract',
        'licensing', 'unauthorized use', 'dmca',
        'infringement', 'legal protection'
    ]

    RECOMMENDED_WORKSPACES = [
        "Design Agency Slacks",
        "Creative Studio Workspaces",
        "Freelance Collectives",
        "Photography Studios",
        "Video Production Teams",
        "Marketing Agency Slacks"
    ]

    def __init__(self, bot_token: str = None, app_token: str = None):
        """Initialize Slack bot"""
        self.bot_token = bot_token or os.getenv('SLACK_BOT_TOKEN')
        self.app_token = app_token or os.getenv('SLACK_APP_TOKEN')

        if not self.bot_token:
            raise ValueError("Slack bot token required")

        # Web client for API calls
        self.client = WebClient(token=self.bot_token)

        # Socket mode client for real-time events (if app token provided)
        self.socket_client = None
        if self.app_token:
            self.socket_client = SocketModeClient(
                app_token=self.app_token,
                web_client=self.client
            )
            self.socket_client.socket_mode_request_listeners.append(
                self.process_socket_event
            )

        # Track activity
        self.messages_seen = []
        self.responses_sent = []

        logger.info("Slack bot initialized")

    def process_socket_event(self, client: SocketModeClient, req: SocketModeRequest):
        """Process incoming socket mode events"""

        if req.type == "events_api":
            # Acknowledge the request
            response = SocketModeResponse(envelope_id=req.envelope_id)
            client.send_socket_mode_response(response)

            # Process the event
            event = req.payload.get("event", {})
            if event.get("type") == "message" and not event.get("subtype"):
                self.handle_message(event)

    def handle_message(self, event: dict):
        """Handle incoming message event"""

        text = event.get("text", "")
        if not text:
            return

        # Check if relevant
        if self._is_relevant(text):
            logger.info(f'Relevant Slack message: {text[:100]}...')

            self.messages_seen.append({
                'timestamp': event.get('ts'),
                'channel': event.get('channel'),
                'user': event.get('user'),
                'text': text,
                'thread_ts': event.get('thread_ts'),
                'recorded_at': datetime.now().isoformat()
            })

    def _is_relevant(self, text: str) -> bool:
        """Check if message is relevant"""
        text_lower = text.lower()

        for keyword in self.TARGET_KEYWORDS:
            if keyword in text_lower:
                return True

        # Question patterns
        if any(pattern in text_lower for pattern in [
            'how do we protect',
            'what should we do',
            'advice on',
            'help with',
            'client wants'
        ]):
            return True

        return False

    def get_recent_opportunities(self, limit: int = 50) -> List[Dict]:
        """Get recent relevant messages"""
        sorted_messages = sorted(
            self.messages_seen,
            key=lambda x: x['recorded_at'],
            reverse=True
        )

        return sorted_messages[:limit]

    def send_message(self, channel: str, text: str,
                    tracking_id: str = None, thread_ts: str = None) -> Optional[str]:
        """
        Send message to a channel or thread.
        Returns message timestamp if successful.
        """
        try:
            # Add tracking
            tracked_text = self._add_tracking(text, tracking_id, 'slack_message')

            response = self.client.chat_postMessage(
                channel=channel,
                text=tracked_text,
                thread_ts=thread_ts  # Reply in thread if provided
            )

            ts = response['ts']

            self.responses_sent.append({
                'ts': ts,
                'channel': channel,
                'text': text,
                'thread_ts': thread_ts,
                'timestamp': datetime.now().isoformat(),
                'tracking_id': tracking_id
            })

            logger.info(f"✅ Sent Slack message to {channel}")

            return ts

        except SlackApiError as e:
            logger.error(f"Error sending Slack message: {e.response['error']}")
            return None

    def send_dm(self, user_id: str, text: str,
               tracking_id: str = None) -> Optional[str]:
        """Send DM to a user"""
        try:
            # Open DM channel
            response = self.client.conversations_open(users=[user_id])
            channel_id = response['channel']['id']

            # Send message
            return self.send_message(channel_id, text, tracking_id)

        except SlackApiError as e:
            logger.error(f"Error sending DM: {e.response['error']}")
            return None

    def _add_tracking(self, text: str, tracking_id: str, source: str) -> str:
        """Add UTM tracking"""
        if tracking_id:
            bloom_url = f"https://bloom.com?utm_source=slack&utm_medium=ai_agent&utm_campaign={tracking_id}&utm_content={source}"

            if 'bloom.com' not in text.lower():
                text += f"\n\nLearn more: <{bloom_url}|BLOOM IP Protection>"

        return text

    def list_channels(self) -> List[Dict]:
        """List all channels in workspace"""
        try:
            response = self.client.conversations_list(
                types="public_channel,private_channel"
            )

            channels = []
            for channel in response['channels']:
                channels.append({
                    'id': channel['id'],
                    'name': channel['name'],
                    'num_members': channel.get('num_members', 0),
                    'is_member': channel.get('is_member', False)
                })

            return channels

        except SlackApiError as e:
            logger.error(f"Error listing channels: {e.response['error']}")
            return []

    def join_channel(self, channel_id: str) -> bool:
        """Join a channel"""
        try:
            self.client.conversations_join(channel=channel_id)
            logger.info(f"✅ Joined channel {channel_id}")
            return True

        except SlackApiError as e:
            logger.error(f"Error joining channel: {e.response['error']}")
            return False

    def start(self):
        """Start socket mode connection"""
        if not self.socket_client:
            raise ValueError("Socket mode requires SLACK_APP_TOKEN")

        logger.info("Starting Slack bot (socket mode)...")
        self.socket_client.connect()

        # Keep running
        from threading import Event
        Event().wait()


class SlackStrategy:
    """
    Executes Slack marketing strategies (B2B focus).
    """

    def __init__(self, monitor: SlackMonitor, agent):
        self.monitor = monitor
        self.agent = agent

    def execute_helpful_reply_strategy(self) -> bool:
        """Reply to relevant message in workspace"""

        opportunities = self.monitor.get_recent_opportunities(limit=10)

        if not opportunities:
            logger.info("No Slack opportunities found")
            return False

        # Pick best
        best = opportunities[0]

        # Generate professional reply (B2B tone)
        context = {
            'message': best['text'],
            'platform': 'slack',
            'tone': 'professional'  # B2B audience
        }

        reply_text = self.agent.generate_content('slack_helpful_reply', context)

        # Send as thread reply
        tracking_id = f"slack_reply_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        ts = self.monitor.send_message(
            channel=best['channel'],
            text=reply_text,
            tracking_id=tracking_id,
            thread_ts=best.get('thread_ts') or best['timestamp']  # Reply in thread
        )

        return ts is not None

    def execute_channel_post_strategy(self, channel_id: str,
                                     topic: str = None) -> bool:
        """Post educational content (with permission!)"""

        if not topic:
            topic = "protecting agency IP and client work"

        # Generate B2B-focused content
        context = {
            'topic': topic,
            'platform': 'slack',
            'tone': 'professional'
        }

        content = self.agent.generate_content('slack_channel_post', context)

        # Post it
        tracking_id = f"slack_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        ts = self.monitor.send_message(
            channel=channel_id,
            text=content,
            tracking_id=tracking_id
        )

        return ts is not None


def setup_slack_bot(bot_token: str, app_token: str, agent) -> SlackMonitor:
    """
    Setup Slack bot.

    Note: Slack requires both bot token and app token for socket mode.

    Usage:
        monitor = setup_slack_bot(bot_token, app_token, agent)
        monitor.start()  # Runs forever
    """
    monitor = SlackMonitor(bot_token=bot_token, app_token=app_token)

    logger.info("Slack bot configured")

    return monitor
