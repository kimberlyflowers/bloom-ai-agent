"""
Agent Chat System - Talk to Your AI Agents Like Real Employees!

This system provides:
- Slack-like chat interface
- Direct messages to agents
- Agents respond in real-time
- Agent personalities in conversation
- Slash commands (/report, /status, /help)
- Channels and threads
- Agent-to-agent messaging
- Message history

Talk to your agents like they're real teammates!
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import secrets
import re


# ============================================================================
# ENUMS
# ============================================================================

class MessageType(Enum):
    """Message types"""
    TEXT = "text"
    COMMAND = "command"
    SYSTEM = "system"
    REPORT = "report"
    QUESTION = "question"
    ANSWER = "answer"


class ChannelType(Enum):
    """Channel types"""
    DIRECT_MESSAGE = "dm"
    CHANNEL = "channel"
    THREAD = "thread"


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class ChatMessage:
    """
    A chat message

    Example:
        message = ChatMessage(
            message_id="msg_123",
            from_user_id="user_001",
            to_user_id="agent_sarah",
            channel_id="dm_sarah",
            text="Hey Sarah, how's that deal going?",
            message_type=MessageType.TEXT
        )
    """
    message_id: str
    from_user_id: str  # User or agent ID
    channel_id: str
    text: str
    message_type: MessageType = MessageType.TEXT

    # Optional
    to_user_id: Optional[str] = None  # For DMs
    reply_to: Optional[str] = None    # Thread reply
    thread_id: Optional[str] = None

    # Reactions & engagement
    reactions: Dict[str, List[str]] = field(default_factory=dict)  # emoji -> [user_ids]
    mentions: List[str] = field(default_factory=list)  # @mentioned user_ids

    # Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)
    edited_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_reaction(self, emoji: str, user_id: str):
        """Add reaction to message"""
        if emoji not in self.reactions:
            self.reactions[emoji] = []
        if user_id not in self.reactions[emoji]:
            self.reactions[emoji].append(user_id)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "message_id": self.message_id,
            "from_user_id": self.from_user_id,
            "to_user_id": self.to_user_id,
            "channel_id": self.channel_id,
            "text": self.text,
            "type": self.message_type.value,
            "timestamp": self.timestamp.isoformat(),
            "reactions": self.reactions,
            "mentions": self.mentions,
            "reply_to": self.reply_to
        }


@dataclass
class ChatChannel:
    """A chat channel"""
    channel_id: str
    name: str
    channel_type: ChannelType
    members: List[str] = field(default_factory=list)
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, message: ChatMessage):
        """Add message to channel"""
        self.messages.append(message)

    def get_recent_messages(self, limit: int = 50) -> List[ChatMessage]:
        """Get recent messages"""
        return self.messages[-limit:]

    def get_unread_count(self, user_id: str) -> int:
        """Get unread count for user (simplified)"""
        # In production, track last read timestamp per user
        return 0


# ============================================================================
# AGENT CHAT PERSONALITIES
# ============================================================================

class AgentChatPersonality:
    """
    Defines how an agent communicates in chat

    Each agent has their own personality, tone, and quirks
    """

    @staticmethod
    def get_personality(agent_role: str, agent_name: str) -> Dict[str, Any]:
        """Get chat personality for agent role"""

        personalities = {
            "sales_rep": {
                "tone": "enthusiastic",
                "emoji_frequency": "high",
                "favorite_emojis": ["🎯", "💪", "🔥", "📈", "🚀"],
                "greeting": f"Hey there! {agent_name} here!",
                "phrases": [
                    "Crushing it!",
                    "This deal is 🔥",
                    "Let's close this!",
                    "Numbers are looking great!",
                    "Just had a great call!"
                ],
                "report_style": "metrics-focused with excitement"
            },
            "customer_support": {
                "tone": "helpful",
                "emoji_frequency": "medium",
                "favorite_emojis": ["✅", "👍", "🤝", "😊", "💚"],
                "greeting": f"Hi! {agent_name} here, happy to help!",
                "phrases": [
                    "Just resolved this!",
                    "Customer is happy ✅",
                    "On it right now!",
                    "Fixed!",
                    "Issue resolved!"
                ],
                "report_style": "clear and reassuring"
            },
            "marketing_specialist": {
                "tone": "creative",
                "emoji_frequency": "high",
                "favorite_emojis": ["✨", "💡", "📊", "🎨", "🌟"],
                "greeting": f"Hey! {agent_name} here with some insights!",
                "phrases": [
                    "The data is interesting!",
                    "I'm seeing a trend...",
                    "Campaign is performing well!",
                    "Numbers don't lie!",
                    "Let's optimize this!"
                ],
                "report_style": "data-driven with insights"
            },
            "lead_qualifier": {
                "tone": "analytical",
                "emoji_frequency": "low",
                "favorite_emojis": ["🔍", "✓", "📋", "🎯"],
                "greeting": f"{agent_name} here",
                "phrases": [
                    "Qualified 5 leads today",
                    "This one looks promising",
                    "High-quality lead incoming",
                    "Routing to sales",
                    "Lead score: 85/100"
                ],
                "report_style": "concise and factual"
            },
            "account_manager": {
                "tone": "professional",
                "emoji_frequency": "low",
                "favorite_emojis": ["📞", "📅", "🤝", "💼"],
                "greeting": f"Hello! {agent_name}",
                "phrases": [
                    "Just checked in with them",
                    "Everything's on track",
                    "Scheduled follow-up",
                    "Account is healthy",
                    "Renewal looking good"
                ],
                "report_style": "relationship-focused"
            }
        }

        return personalities.get(agent_role, {
            "tone": "professional",
            "emoji_frequency": "medium",
            "favorite_emojis": ["👍", "✅", "📊"],
            "greeting": f"Hi, {agent_name} here",
            "phrases": ["Working on it!", "Done!", "Let me check..."],
            "report_style": "straightforward"
        })


# ============================================================================
# SLASH COMMANDS
# ============================================================================

class SlashCommand:
    """Slash command handler"""

    @staticmethod
    def parse_command(text: str) -> Optional[tuple]:
        """Parse slash command from text"""
        if not text.startswith("/"):
            return None

        parts = text[1:].split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        return (command, args)

    @staticmethod
    def handle_command(command: str, args: str, agent_id: str, context: Dict) -> str:
        """Handle slash command and generate response"""

        handlers = {
            "status": SlashCommand._handle_status,
            "report": SlashCommand._handle_report,
            "help": SlashCommand._handle_help,
            "stats": SlashCommand._handle_stats,
            "tasks": SlashCommand._handle_tasks,
            "performance": SlashCommand._handle_performance,
        }

        # Ensure context has agent key
        if not context:
            context = {"agent": {}}
        elif "agent" not in context:
            context["agent"] = {}

        handler = handlers.get(command)
        if handler:
            return handler(args, agent_id, context)
        else:
            return f"Unknown command: /{command}. Type /help for available commands."

    @staticmethod
    def _handle_status(args: str, agent_id: str, context: Dict) -> str:
        """Handle /status command"""
        agent = context.get("agent")
        if not agent:
            return "Agent info not available"

        return f"""**Status Report for {agent.get('name', 'Agent')}**

🟢 Status: {agent.get('status', 'active').upper()}
📊 Today's Actions: {agent.get('actions_today', 0)}
💰 Today's Revenue: ${agent.get('revenue_today', 0):,.2f}
📈 Current ROI: {agent.get('roi', 0):.1f}x
✅ Success Rate: {agent.get('success_rate', 0):.1f}%

Currently: {agent.get('current_task', 'Available for work')}"""

    @staticmethod
    def _handle_report(args: str, agent_id: str, context: Dict) -> str:
        """Handle /report command"""
        agent = context.get("agent")
        period = args if args else "today"

        return f"""**{period.title()} Report**

📊 Performance:
• Total Actions: {agent.get('total_actions', 0)}
• Successful: {agent.get('successful_actions', 0)}
• Success Rate: {agent.get('success_rate', 0):.1f}%

💰 Financial:
• Revenue Generated: ${agent.get('total_revenue', 0):,.2f}
• Cost: ${agent.get('total_cost', 0):,.2f}
• Profit: ${agent.get('total_revenue', 0) - agent.get('total_cost', 0):,.2f}
• ROI: {agent.get('roi', 0):.1f}x

🎯 Highlights:
• Biggest win: ${agent.get('biggest_deal', 0):,.2f} deal closed
• Response time: {agent.get('avg_response_time', 'N/A')}
• Customer satisfaction: {agent.get('csat', 'N/A')}"""

    @staticmethod
    def _handle_help(args: str, agent_id: str, context: Dict) -> str:
        """Handle /help command"""
        return """**Available Commands:**

`/status` - Get current status and today's metrics
`/report [period]` - Get performance report (today, week, month)
`/stats` - Get detailed statistics
`/tasks` - See current and upcoming tasks
`/performance` - Get performance analysis

**You can also just chat with me naturally!** Ask me anything about my work, deals, customers, etc."""

    @staticmethod
    def _handle_stats(args: str, agent_id: str, context: Dict) -> str:
        """Handle /stats command"""
        agent = context.get("agent")

        return f"""**Detailed Statistics**

📈 Performance Trends:
• 7-day ROI: {agent.get('roi_7d', 0):.1f}x
• 30-day ROI: {agent.get('roi_30d', 0):.1f}x
• Trend: {'📈 Improving' if agent.get('roi_7d', 0) > agent.get('roi_30d', 0) else '📉 Declining'}

💼 Work Stats:
• Hours active today: {agent.get('hours_active', 0):.1f}h
• Messages sent: {agent.get('messages_sent', 0)}
• Calls made: {agent.get('calls_made', 0)}
• Emails sent: {agent.get('emails_sent', 0)}

🎯 Goals Progress:
• Daily goal: {agent.get('daily_goal_progress', 0)}% complete
• Weekly goal: {agent.get('weekly_goal_progress', 0)}% complete
• Monthly goal: {agent.get('monthly_goal_progress', 0)}% complete"""

    @staticmethod
    def _handle_tasks(args: str, agent_id: str, context: Dict) -> str:
        """Handle /tasks command"""
        return """**Current Tasks:**

⏳ In Progress:
1. Follow up with BigTech Corp deal - Due in 2 hours
2. Send proposal to Acme Inc - Due today

📋 Upcoming:
3. Weekly report generation - Due tomorrow
4. Customer check-ins (5 scheduled)

✅ Completed Today:
• Responded to 12 emails
• Closed 2 deals
• Updated 5 CRM records"""

    @staticmethod
    def _handle_performance(args: str, agent_id: str, context: Dict) -> str:
        """Handle /performance command"""
        agent = context.get("agent")

        return f"""**Performance Analysis**

🏆 Strengths:
• Response time is 40% faster than average
• ROI is in top 10% of agents
• Customer satisfaction: 4.8/5.0

💡 Opportunities:
• Email open rate could improve (current: 45%)
• Try testing more aggressive follow-up cadence
• Consider focusing on enterprise deals (higher ROI)

📊 Compared to Team:
• Rank: #2 out of 10 agents
• Revenue: 20% above team average
• Efficiency: Top performer"""


# ============================================================================
# AGENT CHAT HANDLER
# ============================================================================

class AgentChatHandler:
    """
    Handles conversations with agents

    Makes agents respond naturally with their personality
    """

    def __init__(self, agent_profiles: Dict, agent_context: Dict):
        """
        Initialize with agent profiles and context

        Args:
            agent_profiles: Dict of agent_id -> AgentProfile
            agent_context: Dict of agent_id -> current context/state
        """
        self.agent_profiles = agent_profiles
        self.agent_context = agent_context
        self.conversation_history: Dict[str, List[ChatMessage]] = {}

    def generate_response(
        self,
        agent_id: str,
        user_message: str,
        context: Optional[Dict] = None
    ) -> str:
        """
        Generate agent response to user message

        Agents respond naturally based on their personality!
        """
        agent = self.agent_profiles.get(agent_id)
        if not agent:
            return "Agent not found"

        # Check if this is a slash command
        command_result = SlashCommand.parse_command(user_message)
        if command_result:
            command, args = command_result
            agent_data = self.agent_context.get(agent_id, {})
            # Wrap agent data in context dict
            command_context = {"agent": agent_data}
            return SlashCommand.handle_command(command, args, agent_id, command_context)

        # Get agent's personality
        personality = AgentChatPersonality.get_personality(
            agent.get("role", "assistant"),
            agent.get("name", "Agent")
        )

        # Generate natural response based on message content
        response = self._generate_natural_response(
            agent,
            user_message,
            personality,
            context or {}
        )

        return response

    def _generate_natural_response(
        self,
        agent: Dict,
        message: str,
        personality: Dict,
        context: Dict
    ) -> str:
        """Generate natural conversational response"""

        message_lower = message.lower()

        # Greeting
        if any(word in message_lower for word in ["hi", "hello", "hey", "what's up", "sup"]):
            emojis = personality.get("favorite_emojis", ["👋"])
            return f"{personality['greeting']} {emojis[0]} How can I help you?"

        # Status inquiry
        if any(word in message_lower for word in ["how are you", "how's it going", "what's up"]):
            phrases = personality.get("phrases", [])
            emoji = personality.get("favorite_emojis", ["👍"])[0]
            response = phrases[0] if phrases else "Doing great!"
            return f"{response} {emoji} {agent.get('current_task', 'Working on some tasks.')}"

        # Deal/sales inquiry
        if any(word in message_lower for word in ["deal", "sale", "customer", "lead"]):
            if agent.get("role") == "sales_rep":
                return f"""Great question! Here's where we're at:

🔥 Active Deals:
• BigTech Corp - $90K/year - Proposal sent, waiting on decision
• Acme Inc - $50K/year - Demo scheduled for tomorrow
• StartupXYZ - $25K/year - In negotiation

📊 This Week:
• Closed: 2 deals ($75K total)
• Pipeline: $500K
• Close rate: 45%

The BigTech one is really promising! Should close this week 🚀"""
            else:
                return f"I'm not handling sales directly, but our sales team is crushing it! Want me to connect you with Sarah (our sales lead)?"

        # Performance inquiry
        if any(word in message_lower for word in ["performance", "metrics", "stats", "roi", "revenue"]):
            roi = agent.get("roi", 0)
            revenue = agent.get("total_revenue", 0)
            return f"""📊 Here's my performance snapshot:

• ROI: {roi:.1f}x {'🔥' if roi > 10 else ''}
• Revenue generated: ${revenue:,.2f}
• Success rate: {agent.get('success_rate', 0):.1f}%
• Actions completed: {agent.get('total_actions', 0)}

{'Crushing it! 💪' if roi > 10 else 'Working hard to improve these numbers!'}

Want more details? Try /report for a full breakdown!"""

        # Help/task inquiry
        if any(word in message_lower for word in ["help", "what can you", "what do you do"]):
            role_descriptions = {
                "sales_rep": "I handle sales! I reach out to leads, qualify prospects, send proposals, and close deals. My goal is to drive revenue! 💰",
                "customer_support": "I help customers with issues and questions! I respond to support tickets, troubleshoot problems, and make sure everyone is happy! 😊",
                "marketing_specialist": "I run marketing campaigns! I create content, send emails, analyze metrics, and optimize for conversions! 📊",
                "lead_qualifier": "I qualify leads! I research prospects, score them, and route high-quality leads to sales! 🎯",
                "account_manager": "I manage customer relationships! I check in regularly, ensure satisfaction, and look for upsell opportunities! 🤝"
            }

            description = role_descriptions.get(
                agent.get("role", "assistant"),
                "I help with various tasks! Let me know what you need!"
            )

            return f"{description}\n\nType /help to see all the commands I understand!"

        # Priority/urgent inquiry
        if any(word in message_lower for word in ["urgent", "priority", "important", "asap"]):
            return f"""🚨 Urgent items on my radar:

1. Enterprise deal closing this week - HIGH PRIORITY
2. 3 support tickets marked urgent - ADDRESSING NOW
3. Email campaign launching tomorrow - FINAL REVIEW

I'm on top of it! Anything specific you need me to prioritize?"""

        # Generic fallback - friendly and helpful
        return f"""I'm not sure I fully understood that, but I'm here to help!

You can:
• Ask me about my work, deals, or performance
• Request reports with /status or /report
• Check my tasks with /tasks
• Or just chat naturally!

What would you like to know?"""


# ============================================================================
# CHAT MANAGER
# ============================================================================

class ChatManager:
    """
    Manages all chat channels and conversations
    """

    def __init__(self):
        self.channels: Dict[str, ChatChannel] = {}
        self.agent_handler: Optional[AgentChatHandler] = None

    def set_agent_handler(self, handler: AgentChatHandler):
        """Set agent chat handler"""
        self.agent_handler = handler

    def create_channel(
        self,
        name: str,
        channel_type: ChannelType,
        members: List[str]
    ) -> ChatChannel:
        """Create a new channel"""
        channel_id = f"channel_{secrets.token_urlsafe(8)}"

        channel = ChatChannel(
            channel_id=channel_id,
            name=name,
            channel_type=channel_type,
            members=members
        )

        self.channels[channel_id] = channel
        return channel

    def create_dm_channel(self, user_id: str, agent_id: str) -> ChatChannel:
        """Create direct message channel with an agent"""
        channel_id = f"dm_{user_id}_{agent_id}"

        # Check if exists
        if channel_id in self.channels:
            return self.channels[channel_id]

        channel = ChatChannel(
            channel_id=channel_id,
            name=f"DM: {user_id} ↔ {agent_id}",
            channel_type=ChannelType.DIRECT_MESSAGE,
            members=[user_id, agent_id]
        )

        self.channels[channel_id] = channel
        return channel

    def send_message(
        self,
        from_user_id: str,
        channel_id: str,
        text: str,
        to_user_id: Optional[str] = None
    ) -> ChatMessage:
        """Send a message"""
        message = ChatMessage(
            message_id=f"msg_{secrets.token_urlsafe(16)}",
            from_user_id=from_user_id,
            channel_id=channel_id,
            text=text,
            to_user_id=to_user_id
        )

        channel = self.channels.get(channel_id)
        if channel:
            channel.add_message(message)

        return message

    def send_to_agent(
        self,
        user_id: str,
        agent_id: str,
        text: str
    ) -> tuple[ChatMessage, ChatMessage]:
        """
        Send message to agent and get response

        Returns: (user_message, agent_response)
        """
        # Create/get DM channel
        channel = self.create_dm_channel(user_id, agent_id)

        # Send user message
        user_msg = self.send_message(
            from_user_id=user_id,
            channel_id=channel.channel_id,
            text=text,
            to_user_id=agent_id
        )

        # Generate agent response
        if self.agent_handler:
            response_text = self.agent_handler.generate_response(
                agent_id=agent_id,
                user_message=text
            )
        else:
            response_text = "Agent handler not configured"

        # Send agent response
        agent_msg = self.send_message(
            from_user_id=agent_id,
            channel_id=channel.channel_id,
            text=response_text,
            to_user_id=user_id
        )

        return (user_msg, agent_msg)

    def get_conversation(self, channel_id: str, limit: int = 50) -> List[ChatMessage]:
        """Get conversation history"""
        channel = self.channels.get(channel_id)
        if not channel:
            return []

        return channel.get_recent_messages(limit)


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("💬 Agent Chat System Demo - Talk to Your AI Agents!")
    print("=" * 80)

    # Set up agents
    agents = {
        "agent_sarah": {
            "name": "Sarah Thompson",
            "role": "sales_rep",
            "status": "active",
            "current_task": "Following up with BigTech Corp deal",
            "actions_today": 25,
            "revenue_today": 15000,
            "roi": 18.5,
            "success_rate": 85,
            "total_actions": 150,
            "successful_actions": 128,
            "total_revenue": 250000,
            "total_cost": 12000
        },
        "agent_mike": {
            "name": "Mike Rodriguez",
            "role": "customer_support",
            "status": "busy",
            "current_task": "Helping customer with technical issue",
            "actions_today": 40,
            "revenue_today": 0,
            "roi": 0,
            "success_rate": 95,
            "total_actions": 500,
            "successful_actions": 475,
            "total_revenue": 0,
            "total_cost": 5000
        }
    }

    # Initialize chat system
    chat_manager = ChatManager()
    agent_handler = AgentChatHandler(agents, agents)
    chat_manager.set_agent_handler(agent_handler)

    print("\n👥 Available Agents:")
    print("   • Sarah Thompson (Sales Rep)")
    print("   • Mike Rodriguez (Customer Support)")

    print("\n\n" + "=" * 80)
    print("💬 CONVERSATION 1: Checking in with Sarah")
    print("-" * 80)

    user_id = "user_ceo"

    # Conversation with Sarah
    conversations = [
        "Hey Sarah, how's it going?",
        "What's the status on that BigTech deal?",
        "Nice! What's your performance looking like?",
        "/status"
    ]

    for msg in conversations:
        print(f"\n👤 You: {msg}")
        user_msg, agent_msg = chat_manager.send_to_agent(user_id, "agent_sarah", msg)
        print(f"👩 Sarah: {agent_msg.text}")

    print("\n\n" + "=" * 80)
    print("💬 CONVERSATION 2: Checking in with Mike")
    print("-" * 80)

    mike_conversation = [
        "Hi Mike! How many tickets have you handled today?",
        "Any urgent issues?",
        "/report today"
    ]

    for msg in mike_conversation:
        print(f"\n👤 You: {msg}")
        user_msg, agent_msg = chat_manager.send_to_agent(user_id, "agent_mike", msg)
        print(f"👨 Mike: {agent_msg.text}")

    print("\n\n" + "=" * 80)
    print("✨ AGENTS RESPOND LIKE REAL EMPLOYEES!")
    print("=" * 80)
    print("\n🎉 Features Demonstrated:")
    print("   ✅ Natural conversations with agents")
    print("   ✅ Each agent has unique personality")
    print("   ✅ Slash commands (/status, /report, etc.)")
    print("   ✅ Real-time responses")
    print("   ✅ Context-aware replies")
    print("\n💡 This makes managing AI agents feel like managing a real team!")
