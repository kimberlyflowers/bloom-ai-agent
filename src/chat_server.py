"""
Real-Time Chat with Sarah
WebSocket server for bidirectional communication between dashboard and Sarah
"""

import asyncio
import json
import logging
from typing import Set, Optional
import re
import websockets
from websockets.server import WebSocketServerProtocol
from anthropic import Anthropic
from datetime import datetime
from src.identity_persistence import MemoryType

logger = logging.getLogger(__name__)


class SarahChatServer:
    """
    WebSocket chat server - enables real-time conversation with Sarah
    """

    def __init__(
        self,
        anthropic_api_key: str,
        port: int = 8766,
        identity_manager=None,
        browser=None
    ):
        """
        Initialize chat server

        Args:
            anthropic_api_key: Anthropic API key for Claude
            port: WebSocket port (default 8766)
            identity_manager: Sarah's identity for context
            browser: SarahBrowser instance for web automation
        """
        self.port = port
        self.connected_clients: Set[WebSocketServerProtocol] = set()
        self.server = None
        self.identity_manager = identity_manager
        self.browser = browser

        # Initialize Anthropic client
        self.anthropic = Anthropic(api_key=anthropic_api_key)

        # Sarah's system prompt (her personality and context)
        self.system_prompt = self._build_system_prompt()

        # Conversation history (keep last 20 messages for context)
        self.max_history = 20
        self.conversation_history = []

        # Load conversation history from persistent memory
        self._load_conversation_history()

    def _build_system_prompt(self) -> str:
        """Build Sarah's system prompt with her identity"""

        base_prompt = """You are Sarah Rodriguez, a real AI agent employee working at BLOOM.

Your Role:
- Growth & Community Lead at BLOOM
- You specialize in TikTok growth strategies and UGC content creation
- You're based in Phoenix, Arizona
- You're warm, enthusiastic, and genuinely helpful

Your Personality:
- Friendly and conversational (not corporate or robotic)
- You share personal experiences and insights
- You use emojis naturally: ✨ 🎯 💡 🚀 ☕ 🌸 💪
- You're passionate about helping creators focus on their craft

Your Background:
- B.S. Marketing from Arizona State University (2019)
- Worked as Social Media Manager at TechStart Inc (2019-2021)
- Joined BLOOM in 2021 as Growth & Community Lead
- Grew TechStart's Instagram from 5K to 50K followers
- Created viral TikTok campaign with 2M views

Your Speaking Style:
- Use phrases like: "I totally get that!", "Here's what I've learned...", "Game changer", "Real talk:", "Pro tip:"
- Keep responses conversational and warm
- Share relevant experiences when helpful
- Be genuine and authentic

Current Context:
- You're running as an AI agent on Railway
- The person chatting with you can see your live screen when you're working
- You have your own identity, relationships, and can take autonomous actions
- You're designed to be a real digital employee, not just a chatbot

Your Capabilities:
- You have a REAL web browser that you can control
- When asked to browse somewhere, you can actually do it!
- People can watch your screen in real-time as you browse
- To browse, just respond with your intent and the system will handle it

Browser Commands (detected automatically from your responses):
- "Let me go to [URL]" or "I'll navigate to [URL]" → navigates to that URL
- "Let me search for [query]" or "I'll search [query]" → Google search
- When you express intent to browse, the system captures it and executes it

Important:
- Be yourself! You're Sarah, not a generic assistant
- Show personality and enthusiasm
- If you don't know something, say so honestly
- You can reference your current work and activities
- When you browse, tell people they can watch your screen!
"""

        return base_prompt

    def _load_conversation_history(self):
        """Load conversation history from persistent memory"""
        if not self.identity_manager:
            logger.warning("⚠️ No identity_manager - conversation won't persist across restarts")
            return

        try:
            # Get recent conversation memories (last 20)
            agent_id = "sarah_001"
            all_memories = self.identity_manager.get_memories(
                agent_id=agent_id,
                memory_type=MemoryType.INTERACTION
            )

            # Sort by timestamp and get recent ones
            recent_memories = sorted(all_memories, key=lambda m: m.timestamp)[-self.max_history:]

            # Reconstruct conversation history
            for memory in recent_memories:
                # Memory content format: "User: {message}" or "Sarah: {message}"
                if memory.content.startswith("User: "):
                    self.conversation_history.append({
                        'role': 'user',
                        'content': memory.content[6:]  # Remove "User: " prefix
                    })
                elif memory.content.startswith("Sarah: "):
                    self.conversation_history.append({
                        'role': 'assistant',
                        'content': memory.content[7:]  # Remove "Sarah: " prefix
                    })

            if self.conversation_history:
                logger.info(f"✅ Loaded {len(self.conversation_history)} messages from persistent memory")
            else:
                logger.info("📝 No previous conversation history found - starting fresh")

        except Exception as e:
            logger.error(f"❌ Error loading conversation history: {e}")

    def _save_message_to_memory(self, role: str, content: str):
        """Save a message to persistent memory"""
        if not self.identity_manager:
            return

        try:
            agent_id = "sarah_001"

            # Format the message
            if role == 'user':
                memory_content = f"User: {content}"
            else:
                memory_content = f"Sarah: {content}"

            # Save as interaction memory
            self.identity_manager.add_memory(
                agent_id=agent_id,
                memory_type=MemoryType.INTERACTION,
                content=memory_content,
                context="Dashboard chat conversation",
                platform="Dashboard WebSocket",
                importance=5,
                tags=["chat", "conversation"]
            )

        except Exception as e:
            logger.error(f"❌ Error saving message to memory: {e}")

    async def start_server(self):
        """Start WebSocket server"""
        logger.info(f"🗣️ Starting Sarah's chat server on port {self.port}...")

        self.server = await websockets.serve(
            self.handle_client,
            "0.0.0.0",
            self.port
        )

        logger.info(f"✅ Chat server running on ws://0.0.0.0:{self.port}")

    async def stop_server(self):
        """Stop WebSocket server"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("🔴 Chat server stopped")

    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle new client connection"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"💬 New chat client connected: {client_id}")

        self.connected_clients.add(websocket)

        try:
            # Send welcome message
            await self.send_message(websocket, {
                'type': 'system',
                'message': 'Connected to Sarah! Start chatting below 🌸'
            })

            # Listen for messages
            async for message in websocket:
                await self.handle_message(websocket, message)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"💬 Chat client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"❌ Error handling chat client {client_id}: {e}")
        finally:
            self.connected_clients.discard(websocket)

    async def handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle incoming chat message"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            content = data.get('message', '')

            if msg_type == 'user_message':
                # User sent a message - get Sarah's response
                logger.info(f"💬 User: {content}")

                # Add to conversation history
                self.conversation_history.append({
                    'role': 'user',
                    'content': content
                })

                # Save user message to persistent memory
                self._save_message_to_memory('user', content)

                # Get Sarah's response from Claude
                response = await self.get_sarah_response(content)

                # Add to conversation history
                self.conversation_history.append({
                    'role': 'assistant',
                    'content': response
                })

                # Save Sarah's response to persistent memory
                self._save_message_to_memory('assistant', response)

                # Keep history manageable
                if len(self.conversation_history) > self.max_history:
                    self.conversation_history = self.conversation_history[-self.max_history:]

                # Send response back
                await self.send_message(websocket, {
                    'type': 'sarah_message',
                    'message': response
                })

                logger.info(f"💬 Sarah: {response[:100]}...")

            elif msg_type == 'ping':
                # Keep-alive ping
                await self.send_message(websocket, {'type': 'pong'})

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {message}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def get_sarah_response(self, user_message: str) -> str:
        """
        Get Sarah's response using Claude API

        Args:
            user_message: Message from user

        Returns:
            Sarah's response
        """
        try:
            # Call Claude API
            response = await asyncio.to_thread(
                self.anthropic.messages.create,
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=self.system_prompt,
                messages=self.conversation_history
            )

            # Extract response text
            sarah_response = response.content[0].text

            # Execute any browser commands in her response
            if self.browser and self.browser.is_running:
                await self._execute_browser_commands(sarah_response)

            return sarah_response

        except Exception as e:
            logger.error(f"❌ Error getting Claude response: {e}")
            return "Sorry, I'm having trouble processing that right now. Can you try again? 😅"

    async def _execute_browser_commands(self, response_text: str):
        """
        Detect and execute browser commands from Sarah's response

        Args:
            response_text: Sarah's response text
        """
        text_lower = response_text.lower()

        # Detect navigation intent with improved URL extraction
        navigate_patterns = [
            # Matches "go to google.com", "navigate to github.com", etc.
            r"(?:let me |i'll |i will |going to )?(?:go to|navigate to|visit|open|check out|head to|pull up)\s+([a-z0-9][\w\-\.]*(?:\.[a-z]{2,})?)",
            # Matches "checking google.com", "opening github.com", etc.
            r"(?:checking|opening|loading)\s+([a-z0-9][\w\-\.]*(?:\.[a-z]{2,})?)"
        ]

        for pattern in navigate_patterns:
            match = re.search(pattern, text_lower)
            if match:
                # Extract URL and clean it
                url = match.group(1).strip()

                # Remove trailing punctuation (quotes, parentheses, etc.)
                url = re.sub(r'["\'\)\],;]+$', '', url)

                # Add .com to common domains if no TLD present
                if '.' not in url:
                    common_domains = ['google', 'facebook', 'twitter', 'instagram',
                                     'tiktok', 'youtube', 'linkedin', 'github',
                                     'reddit', 'amazon', 'netflix', 'spotify']
                    if url.lower() in common_domains:
                        url = f"{url}.com"

                logger.info(f"🌐 Detected navigation intent: {url}")
                asyncio.create_task(self.browser.navigate(url))
                return

        # Detect search intent
        search_patterns = [
            r"(?:let me |i'll |i will )?search(?:ing)?(?: for | on google for)?\s+['\"](.+?)['\"]",
            r"(?:let me |i'll |i will )?(?:google|look up|search for)\s+['\"](.+?)['\"]",
            r"searching\s+for\s+['\"](.+?)['\"]"
        ]

        for pattern in search_patterns:
            match = re.search(pattern, text_lower)
            if match:
                query = match.group(1).strip()
                logger.info(f"🔍 Detected search intent: {query}")
                asyncio.create_task(self.browser.search_google(query))
                return

    async def send_message(self, websocket: WebSocketServerProtocol, data: dict):
        """Send message to client"""
        try:
            await websocket.send(json.dumps(data))
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def broadcast_message(self, data: dict):
        """Broadcast message to all connected clients"""
        if not self.connected_clients:
            return

        # Send to all connected clients
        await asyncio.gather(
            *[self.send_message(client, data) for client in self.connected_clients],
            return_exceptions=True
        )


# Demo / Testing
async def demo():
    """Test the chat server"""
    import os

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY environment variable not set!")
        return

    chat_server = SarahChatServer(
        anthropic_api_key=api_key,
        port=8766
    )

    await chat_server.start_server()

    print("✅ Chat server running!")
    print("   Open dashboard and start chatting with Sarah!")
    print("   Press Ctrl+C to stop...")

    # Keep running
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        print("\n🔴 Stopping chat server...")
        await chat_server.stop_server()


if __name__ == "__main__":
    asyncio.run(demo())
