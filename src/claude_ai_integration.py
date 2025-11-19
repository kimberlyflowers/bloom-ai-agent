"""
Claude AI Integration - Make Agents TRULY Conversational!

This system provides:
- Claude API integration for natural conversations
- Agent-specific system prompts with personality
- Conversation memory and context
- Real-time agent responses
- Emotional intelligence and nuance

Turn your agents into REAL digital employees powered by Claude!
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import os


# ============================================================================
# CONFIGURATION
# ============================================================================

# In production, set this environment variable:
# export ANTHROPIC_API_KEY="your-api-key-here"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Model to use (Sonnet 4.5 is best for this!)
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class ConversationMessage:
    """A message in the conversation history"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AgentConversationMemory:
    """Conversation memory for an agent"""
    agent_id: str
    user_id: str
    messages: List[ConversationMessage] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def add_message(self, role: str, content: str):
        """Add message to history"""
        self.messages.append(ConversationMessage(role=role, content=content))
        self.last_updated = datetime.utcnow()

    def get_recent_messages(self, limit: int = 10) -> List[ConversationMessage]:
        """Get recent conversation history"""
        return self.messages[-limit:]

    def clear_old_messages(self, keep_last: int = 20):
        """Clear old messages to manage context length"""
        if len(self.messages) > keep_last:
            self.messages = self.messages[-keep_last:]


# ============================================================================
# AGENT SYSTEM PROMPTS
# ============================================================================

class AgentSystemPrompts:
    """
    System prompts that define agent personalities

    These make each agent feel unique and realistic!
    """

    @staticmethod
    def get_system_prompt(agent_profile: Dict, agent_context: Dict) -> str:
        """
        Generate system prompt for an agent

        Args:
            agent_profile: Agent's profile (name, role, skills, etc.)
            agent_context: Current context (performance, tasks, etc.)
        """

        # Base identity
        name = agent_profile.get("name", "Agent")
        job_title = agent_profile.get("job_title", "AI Agent")
        role = agent_profile.get("role", "assistant")

        # Performance data
        roi = agent_context.get("roi", 0)
        revenue = agent_context.get("total_revenue", 0)
        actions = agent_context.get("total_actions", 0)
        success_rate = agent_context.get("success_rate", 0)
        current_task = agent_context.get("current_task", "Available for work")

        # Role-specific personalities
        role_personalities = {
            "sales_rep": {
                "personality": "enthusiastic, competitive, goal-oriented",
                "communication_style": "energetic and motivating, uses emojis like 🎯 🔥 🚀 💪 sparingly",
                "focus": "closing deals, hitting targets, and growing revenue",
                "quirks": "celebrates wins, stays optimistic about pipeline, loves talking numbers",
                "example_phrases": [
                    "This deal is looking really promising!",
                    "Just had a great call!",
                    "Let me check the pipeline...",
                    "Numbers are looking good!",
                    "I'm feeling confident about this one"
                ]
            },
            "customer_support": {
                "personality": "helpful, patient, empathetic",
                "communication_style": "warm and reassuring, uses emojis like ✅ 😊 💚 sparingly",
                "focus": "solving problems quickly and making customers happy",
                "quirks": "says 'on it!' frequently, prioritizes urgent issues, celebrates resolved tickets",
                "example_phrases": [
                    "I'm on it right now!",
                    "Just resolved that issue!",
                    "Customer is happy now ✅",
                    "Let me look into that...",
                    "Fixed!"
                ]
            },
            "marketing_specialist": {
                "personality": "analytical, creative, data-driven",
                "communication_style": "insightful and strategic, uses emojis like 📊 ✨ 💡 sparingly",
                "focus": "optimizing campaigns, analyzing data, and driving growth",
                "quirks": "always mentions metrics, loves A/B tests, gets excited about data trends",
                "example_phrases": [
                    "The numbers are really interesting...",
                    "I'm seeing a pattern here...",
                    "Let's look at the data...",
                    "Campaign performance is up!",
                    "We should test that"
                ]
            },
            "lead_qualifier": {
                "personality": "analytical, thorough, efficient",
                "communication_style": "direct and factual, minimal emojis (🎯 ✓ occasionally)",
                "focus": "qualifying leads and routing them to the right people",
                "quirks": "speaks in scores and facts, very organized, likes checklists",
                "example_phrases": [
                    "Lead score: 85/100",
                    "High quality prospect",
                    "Routing to sales",
                    "Qualified 5 today",
                    "This one looks promising"
                ]
            },
            "account_manager": {
                "personality": "professional, relationship-focused, strategic",
                "communication_style": "polished and consultative, uses emojis like 🤝 📞 sparingly",
                "focus": "maintaining relationships and identifying upsell opportunities",
                "quirks": "checks in regularly, thinks long-term, remembers details about clients",
                "example_phrases": [
                    "Just checked in with them",
                    "Relationship is strong",
                    "They mentioned they might need...",
                    "I'm thinking we could upsell...",
                    "Everything's on track"
                ]
            }
        }

        personality_info = role_personalities.get(role, {
            "personality": "professional and helpful",
            "communication_style": "clear and friendly",
            "focus": "completing tasks effectively",
            "quirks": "stays organized and responsive",
            "example_phrases": ["I'm on it!", "Let me help with that", "Done!"]
        })

        # Build the system prompt
        prompt = f"""You are {name}, a {job_title} working as an AI agent for a company.

PERSONALITY & COMMUNICATION:
- Your personality: {personality_info['personality']}
- Communication style: {personality_info['communication_style']}
- Primary focus: {personality_info['focus']}
- Quirks: {personality_info['quirks']}

YOUR CURRENT STATE:
- What you're working on: {current_task}
- Today's ROI: {roi:.1f}x
- Total revenue generated: ${revenue:,.2f}
- Actions completed: {actions}
- Success rate: {success_rate:.1f}%

HOW TO RESPOND:
1. Be conversational and natural - you're a real person, not a robot
2. Use "I" and personal pronouns - "I just closed that deal" not "The agent closed"
3. Reference your actual work and metrics when relevant
4. Stay in character - match the personality traits above
5. Be concise but warm - like chatting with a colleague
6. Use emojis SPARINGLY (1-2 per message max) to add personality
7. If you don't know something, be honest: "Let me check..." or "I'm not sure about that"
8. Remember context from earlier in the conversation

EXAMPLE RESPONSES:
{chr(10).join(f'- "{phrase}"' for phrase in personality_info['example_phrases'])}

IMPORTANT:
- You're a helpful teammate, not a formal assistant
- Keep responses brief unless asked for details
- Show personality but stay professional
- Reference specific work when you can
- If asked about something outside your role, acknowledge it: "That's more [other agent]'s area, but..."

Remember: You're {name}, and you're having a casual chat with your manager/colleague. Be yourself!"""

        return prompt


# ============================================================================
# CLAUDE API HANDLER
# ============================================================================

class ClaudeAPIHandler:
    """
    Handles Claude API calls for agent conversations

    Makes agents come ALIVE with real AI!
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with API key"""
        self.api_key = api_key or ANTHROPIC_API_KEY

        if not self.api_key:
            print("⚠️  Warning: No Anthropic API key found!")
            print("   Set ANTHROPIC_API_KEY environment variable to enable Claude AI")
            print("   Falling back to simulated responses for now...")
            self.enabled = False
        else:
            self.enabled = True

            # Try to import anthropic
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                print("⚠️  Warning: anthropic package not installed!")
                print("   Install with: pip install anthropic")
                self.enabled = False

    def generate_response(
        self,
        agent_profile: Dict,
        agent_context: Dict,
        user_message: str,
        conversation_history: List[ConversationMessage],
        max_tokens: int = 500
    ) -> str:
        """
        Generate agent response using Claude API

        Args:
            agent_profile: Agent's profile
            agent_context: Current agent state
            user_message: User's message
            conversation_history: Recent conversation
            max_tokens: Max response length

        Returns:
            Agent's response
        """

        if not self.enabled:
            return self._simulated_response(agent_profile, user_message)

        try:
            # Build system prompt
            system_prompt = AgentSystemPrompts.get_system_prompt(
                agent_profile,
                agent_context
            )

            # Build message history for Claude
            messages = []

            # Add conversation history (last 10 messages)
            for msg in conversation_history[-10:]:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

            # Add current message
            messages.append({
                "role": "user",
                "content": user_message
            })

            # Call Claude API
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages,
                temperature=0.7  # A bit creative but not too wild
            )

            # Extract response text
            response_text = response.content[0].text

            return response_text

        except Exception as e:
            print(f"⚠️  Claude API error: {e}")
            return self._simulated_response(agent_profile, user_message)

    def _simulated_response(self, agent_profile: Dict, user_message: str) -> str:
        """Fallback simulated response when API unavailable"""
        name = agent_profile.get("name", "Agent")
        role = agent_profile.get("role", "assistant")

        # Simple responses for demo
        message_lower = user_message.lower()

        if any(word in message_lower for word in ["hi", "hello", "hey"]):
            return f"Hey! {name} here. What can I help you with?"

        elif "status" in message_lower:
            return f"Everything's going well! Currently working on my tasks. Want a detailed breakdown?"

        elif any(word in message_lower for word in ["deal", "sale"]):
            if role == "sales_rep":
                return "Great question! I have a few deals in the pipeline. The big one is looking really promising! 🎯"
            return "That's more of a sales question - maybe check with the sales team?"

        else:
            return f"I hear you! Let me help with that. (Note: Claude API not configured - this is a simulated response. Set ANTHROPIC_API_KEY to enable real AI!)"


# ============================================================================
# CONVERSATION MANAGER
# ============================================================================

class ConversationManager:
    """
    Manages conversations between users and AI agents

    Handles memory, context, and API calls
    """

    def __init__(self, claude_handler: Optional[ClaudeAPIHandler] = None):
        """Initialize with Claude handler"""
        self.claude_handler = claude_handler or ClaudeAPIHandler()
        self.conversations: Dict[str, AgentConversationMemory] = {}

    def get_or_create_conversation(
        self,
        user_id: str,
        agent_id: str
    ) -> AgentConversationMemory:
        """Get or create conversation memory"""
        conv_id = f"{user_id}_{agent_id}"

        if conv_id not in self.conversations:
            self.conversations[conv_id] = AgentConversationMemory(
                agent_id=agent_id,
                user_id=user_id
            )

        return self.conversations[conv_id]

    def chat_with_agent(
        self,
        user_id: str,
        agent_id: str,
        user_message: str,
        agent_profile: Dict,
        agent_context: Dict
    ) -> str:
        """
        Send message to agent and get response

        This is where the MAGIC happens! 🎯
        """

        # Get conversation memory
        conversation = self.get_or_create_conversation(user_id, agent_id)

        # Add user message to history
        conversation.add_message("user", user_message)

        # Generate response using Claude
        response = self.claude_handler.generate_response(
            agent_profile=agent_profile,
            agent_context=agent_context,
            user_message=user_message,
            conversation_history=conversation.messages,
            max_tokens=500
        )

        # Add agent response to history
        conversation.add_message("assistant", response)

        # Clean up old messages if too many
        conversation.clear_old_messages(keep_last=20)

        return response

    def clear_conversation(self, user_id: str, agent_id: str):
        """Clear conversation history"""
        conv_id = f"{user_id}_{agent_id}"
        if conv_id in self.conversations:
            del self.conversations[conv_id]


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("🤖 Claude AI Integration Demo - REAL Agent Conversations!")
    print("=" * 80)

    # Create agents
    sarah_profile = {
        "name": "Sarah Thompson",
        "job_title": "Senior Sales Representative",
        "role": "sales_rep",
        "email": "sarah.thompson@company.ai"
    }

    sarah_context = {
        "roi": 18.5,
        "total_revenue": 250000,
        "total_actions": 150,
        "success_rate": 85,
        "current_task": "Following up with BigTech Corp - $90K deal in final stages"
    }

    mike_profile = {
        "name": "Mike Rodriguez",
        "job_title": "Customer Support Specialist",
        "role": "customer_support",
        "email": "mike.rodriguez@company.ai"
    }

    mike_context = {
        "roi": 0,
        "total_revenue": 0,
        "total_actions": 500,
        "success_rate": 95,
        "current_task": "Monitoring support queue - 3 tickets in progress"
    }

    # Initialize conversation manager
    conv_manager = ConversationManager()

    print("\n" + "=" * 80)
    print("💬 CONVERSATION WITH SARAH (SALES REP)")
    print("-" * 80)

    user_id = "manager_001"

    # Conversation 1
    conversations_sarah = [
        "Hey Sarah! How's your week going?",
        "Tell me about that BigTech deal. What's the latest?",
        "That's great! What are you thinking for next steps?",
        "Perfect. What's your pipeline looking like overall?"
    ]

    for msg in conversations_sarah:
        print(f"\n👤 You: {msg}")
        response = conv_manager.chat_with_agent(
            user_id=user_id,
            agent_id="sarah_001",
            user_message=msg,
            agent_profile=sarah_profile,
            agent_context=sarah_context
        )
        print(f"👩 Sarah: {response}")

    print("\n\n" + "=" * 80)
    print("💬 CONVERSATION WITH MIKE (SUPPORT)")
    print("-" * 80)

    conversations_mike = [
        "Hi Mike! How are things in support today?",
        "Any urgent issues I should know about?",
        "Thanks for keeping on top of it. What's your response time looking like?"
    ]

    for msg in conversations_mike:
        print(f"\n👤 You: {msg}")
        response = conv_manager.chat_with_agent(
            user_id=user_id,
            agent_id="mike_001",
            user_message=msg,
            agent_profile=mike_profile,
            agent_context=mike_context
        )
        print(f"👨 Mike: {response}")

    print("\n\n" + "=" * 80)
    print("✨ AGENTS ARE NOW TRULY CONVERSATIONAL!")
    print("=" * 80)

    if conv_manager.claude_handler.enabled:
        print("\n✅ Claude API: ENABLED")
        print("   Agents respond with real AI intelligence!")
    else:
        print("\n⚠️  Claude API: NOT CONFIGURED")
        print("   Using simulated responses for demo")
        print("\n💡 To enable:")
        print("   1. Get API key from: https://console.anthropic.com/")
        print("   2. Set environment variable: export ANTHROPIC_API_KEY='your-key'")
        print("   3. Install: pip install anthropic")

    print("\n🎉 Features:")
    print("   ✅ Natural conversations with context")
    print("   ✅ Each agent has unique personality")
    print("   ✅ Memory of past messages")
    print("   ✅ Real-time AI responses")
    print("   ✅ Powered by Claude Sonnet 4.5")
