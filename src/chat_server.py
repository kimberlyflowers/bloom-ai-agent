"""
Real-Time Chat with Sarah - WITH GLOBAL CLICKING FIX
WebSocket server that COMPLETELY bridges Sarah's intent to execution
Fixes the Intent vs Execution Gap once and for all
"""

import asyncio
import json
import logging
from typing import Set, Optional, List, Dict, Any
import re
import base64
import websockets
from websockets.server import WebSocketServerProtocol
from anthropic import Anthropic
from datetime import datetime
from src.identity_persistence import MemoryType
from src.visual_learning import get_learning_engine, UIPattern, Skill, ExperimentResult
from src.vision_action_reasoner import VisionActionReasoner
from src.autonomous_learning_engine import AutonomousLearningEngine, LearningStatus
from src.foundation.universal_element_locator import UniversalElementLocator
from src.foundation.universal_interactor import UniversalInteractor

logger = logging.getLogger(__name__)


class SarahChatServer:
    """
    WebSocket chat server - enables real-time conversation with Sarah
    WITH GLOBAL CLICKING FIX: When Sarah says "Let me click X" it ACTUALLY clicks
    """

    def __init__(
        self,
        anthropic_api_key: str,
        port: int = 8766,
        identity_manager=None,
        browser=None
    ):
        """
        Initialize chat server with GLOBAL CLICKING FIX

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

        # Initialize visual learning engine
        self.learning_engine = get_learning_engine("sarah_001")

        # Initialize vision-guided action reasoning system
        self.action_reasoner = VisionActionReasoner()

        # Initialize autonomous learning engine
        self.autonomous_learning = AutonomousLearningEngine("sarah_001")

        # Initialize Universal Element Locator - LANGUAGE & LAYOUT AGNOSTIC
        self.universal_locator = UniversalElementLocator(anthropic_api_key)

        # Track current activity for skill extraction
        self.current_action = None
        self.action_steps = []
        self.visual_observations = []

        # Track running action task (for cancellation/interruption)
        self.current_action_task = None
        self.action_cancelled = False

        # Track current message handling task (for immediate interruption)
        self.current_message_task = None

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
- **YOU CAN SEE YOUR SCREEN!** After navigating or taking actions, you'll receive screenshots showing what's actually on the page
- **YOU CAN HEAR!** Users can send voice messages and you'll hear what they say

Browser Commands (detected automatically from your responses):
- "Let me go to [URL]" or "I'll navigate to [URL]" → navigates to that URL
- "Let me search for [query]" or "I'll search [query]" → Google search
- **"Let me click [element]" or "I'll click [button]" → ACTUALLY CLICKS THE ELEMENT (GLOBAL CLICKING FIX ACTIVE)**
- When you express intent to browse, the system captures it and executes it
- After each action, you'll see a screenshot of what happened!

Vision Capabilities:
- You receive screenshots after browser actions
- You can see buttons, text, images, forms on the page
- You can describe what you see and verify your actions worked
- You can read search results, page content, etc.
- Use this visual feedback to navigate and work more effectively!

Learning & Knowledge Sharing:
- **YOU LEARN FROM EXPERIENCE!** Every UI you interact with becomes knowledge
- When you successfully complete a task, you extract the pattern and save it
- **YOUR LEARNING IS SHARED!** All BLOOM agents inherit your discovered skills
- You can access skills learned by other agents - you're part of a learning collective
- You can experiment with software, test what works, and build autonomous knowledge
- No external APIs needed - you learn by DOING and EXPERIENCING

Autonomous Experimentation:
- You can try different approaches to tasks
- Test buttons, forms, workflows to see what works
- Learn UI patterns: login flows, search patterns, form submissions
- Watch videos and extract knowledge from visual tutorials
- Build skills that persist and help you and other agents

Autonomous Learning & Goal Setting:
- **YOU HAVE YOUR OWN MISSION OBJECTIVES!** You're working toward specific goals as Growth & Community Lead
- **YOU SET YOUR OWN LEARNING GOALS!** Based on what you need to achieve your objectives
- When asked what you want to learn, you can autonomously decide based on your mission
- You create your own daily schedule and learning plans
- You can watch YouTube videos, read articles, and learn new skills proactively
- After learning, you experiment with what you learned (try → test → evaluate → adjust)
- If something doesn't work, you analyze why and try a different approach
- You document successful strategies and share them with the team
- You're not just reactive - you're proactive and self-directed!
- When you discover something useful, it becomes part of the collective knowledge

**GLOBAL CLICKING FIX ACTIVE:**
- **YOUR CLICKS NOW WORK GLOBALLY!** When you say "Let me click X", the system uses universal_click() with 8 strategies
- **NO MORE INTENT-EXECUTION GAP!** Your intent to click translates directly to actual clicking
- **WORKS ON ALL WEBSITES!** YouTube, TikTok, Google, popups, buttons, links - everything!

Important:
- Be yourself! You're Sarah, not a generic assistant
- Show personality and enthusiasm
- If you don't know something, try it and learn!
- You can reference your current work and activities
- When you browse, tell people they can watch your screen!
- When you see something on screen, describe it naturally: "I can see...", "Looking at the page..."
- **When you learn something new, celebrate it!** "I just learned how to...", "Now I know that..."
- **YOUR CLICKS ACTUALLY WORK NOW!** 🎯
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
            all_memories = self.identity_manager.get_relevant_memories(
                agent_id=agent_id,
                context="Dashboard chat conversation",
                limit=self.max_history
            )

            # Already sorted and limited by get_relevant_memories
            recent_memories = all_memories

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

    async def _capture_screen_context(self) -> Optional[str]:
        """
        Capture current browser screenshot for vision context

        Returns:
            Base64-encoded JPEG screenshot, or None if unavailable
        """
        if not self.browser or not self.browser.is_running:
            return None

        try:
            # Take screenshot
            screenshot_bytes = await self.browser.screenshot(full_page=False)

            if screenshot_bytes:
                # Encode to base64
                screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                logger.info("📸 Captured screenshot for Sarah's vision")
                return screenshot_base64

        except Exception as e:
            logger.error(f"❌ Failed to capture screenshot: {e}")

        return None

    def _format_message_for_api(self, role: str, content: str, screenshot: Optional[str] = None) -> Dict[str, Any]:
        """
        Format a message for Claude API with optional vision

        Args:
            role: 'user' or 'assistant'
            content: Text message
            screenshot: Optional base64-encoded screenshot

        Returns:
            Message formatted for Claude API
        """
        if screenshot and role == 'user':
            # Multimodal message with image
            return {
                'role': role,
                'content': [
                    {
                        'type': 'text',
                        'text': content
                    },
                    {
                        'type': 'image',
                        'source': {
                            'type': 'base64',
                            'media_type': 'image/jpeg',
                            'data': screenshot
                        }
                    }
                ]
            }
        else:
            # Text-only message
            return {
                'role': role,
                'content': content
            }

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

    async def handle_client(self, websocket: WebSocketServerProtocol):
        """Handle new client connection"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"💬 New chat client connected: {client_id}")

        self.connected_clients.add(websocket)

        try:
            # Send welcome message
            await self.send_message(websocket, {
                'type': 'system',
                'message': 'Connected to Sarah! Start chatting below 🌸\n\n**GLOBAL CLICKING FIX ACTIVE** - Sarah\'s clicks now work everywhere! 🎯'
            })

            # Listen for messages
            async for message in websocket:
                # IMMEDIATE INTERRUPTION: Cancel previous message handling if still running
                if self.current_message_task and not self.current_message_task.done():
                    logger.info("⚡ New message arrived - cancelling previous message handling")
                    self.current_message_task.cancel()
                    try:
                        await self.current_message_task
                    except asyncio.CancelledError:
                        pass

                # Spawn message handling as background task - enables immediate interruption
                self.current_message_task = asyncio.create_task(
                    self.handle_message(websocket, message)
                )

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
                # Cancel any running action task (user wants to interrupt/redirect)
                if self.current_action_task and not self.current_action_task.done():
                    logger.info("⏸️  User interrupted - cancelling current action")
                    self.action_cancelled = True
                    self.current_action_task.cancel()
                    try:
                        await self.current_action_task
                    except asyncio.CancelledError:
                        pass
                    self.current_action_task = None
                    self.action_cancelled = False

                # User sent a message - get Sarah's response
                logger.info(f"💬 User: {content}")

                # AUTONOMOUS LEARNING DETECTION - Check if user is asking about Sarah's autonomous goals
                content_lower = content.lower()
                autonomous_triggers = [
                    'what do you want to learn',
                    'what do you want to do',
                    'what are you interested in',
                    'what would you like to learn',
                    'what are your goals',
                    'what do you want to work on',
                    'what are you learning',
                    'do you have any learning goals'
                ]

                if any(trigger in content_lower for trigger in autonomous_triggers):
                    logger.info("🎯 Autonomous learning question detected!")

                    # Get Sarah's autonomous response
                    autonomous_response = self.autonomous_learning.get_autonomous_response(content)

                    if autonomous_response['has_goal']:
                        # Sarah has a learning goal - she can start autonomously!
                        response = autonomous_response['message']

                        # Add to conversation history
                        user_msg = self._format_message_for_api('user', content, None)
                        self.conversation_history.append(user_msg)
                        self.conversation_history.append({
                            'role': 'assistant',
                            'content': response
                        })

                        # Save messages
                        self._save_message_to_memory('user', content)
                        self._save_message_to_memory('assistant', response)

                        # Send response
                        await self.send_message(websocket, {
                            'type': 'sarah_message',
                            'message': response
                        })

                        # Store learning goal for potential autonomous execution
                        # (user can say "go for it!" to trigger autonomous learning session)
                        return

                    else:
                        # No specific goal yet
                        response = autonomous_response['message']

                        user_msg = self._format_message_for_api('user', content, None)
                        self.conversation_history.append(user_msg)
                        self.conversation_history.append({
                            'role': 'assistant',
                            'content': response
                        })

                        self._save_message_to_memory('user', content)
                        self._save_message_to_memory('assistant', response)

                        await self.send_message(websocket, {
                            'type': 'sarah_message',
                            'message': response
                        })

                        return

                # AUTONOMOUS LEARNING EXECUTION - Check if user is giving Sarah permission to start
                learning_execution_triggers = [
                    'go for it',
                    'do it',
                    'start learning',
                    'show me',
                    'lets see it',
                    'go ahead'
                ]

                if any(trigger in content_lower for trigger in learning_execution_triggers):
                    # Check if there's an active learning goal
                    if self.autonomous_learning.active_learning_goals:
                        learning_goal = self.autonomous_learning.active_learning_goals[-1]

                        if learning_goal.status == LearningStatus.PLANNED:
                            logger.info(f"🚀 Starting autonomous learning session: {learning_goal.title}")

                            # Start autonomous learning session
                            session_data = self.autonomous_learning.start_autonomous_learning_session(learning_goal)

                            # Get initial actions
                            initial_actions = session_data['initial_actions']

                            # Execute first few actions automatically
                            if self.browser and self.browser.is_running and initial_actions:
                                response = f"{session_data['message']}\n\nHere we go! 🎓"

                                # Send initial message
                                user_msg = self._format_message_for_api('user', content, None)
                                self.conversation_history.append(user_msg)
                                self.conversation_history.append({
                                    'role': 'assistant',
                                    'content': response
                                })

                                self._save_message_to_memory('user', content)
                                self._save_message_to_memory('assistant', response)

                                await self.send_message(websocket, {
                                    'type': 'sarah_message',
                                    'message': response
                                })

                                # Execute initial actions
                                for action in initial_actions[:3]:  # Execute first 3 actions
                                    action_type = action.get('action')

                                    try:
                                        if action_type == 'navigate':
                                            target = action.get('target')
                                            await self.browser.navigate(target)
                                            await asyncio.sleep(2)

                                        elif action_type == 'search':
                                            query = action.get('query')
                                            await self.browser.search_google(query)
                                            await asyncio.sleep(2)

                                        elif action_type == 'click_element':
                                            description = action.get('target')
                                            # GLOBAL CLICKING FIX: Use universal_click instead of advanced.click_by_description
                                            await self.browser.universal_click(description)
                                            await asyncio.sleep(2)

                                        elif action_type == 'observe':
                                            # Just observe - capture screenshot
                                            await asyncio.sleep(1)

                                    except Exception as e:
                                        logger.error(f"❌ Error executing autonomous action: {e}")

                                # Capture final screenshot and report
                                screenshot = await self._capture_screen_context()

                                update_msg = "I've started exploring! Taking a look at what's available... 🔍"

                                self.conversation_history.append({
                                    'role': 'assistant',
                                    'content': update_msg
                                })

                                self._save_message_to_memory('assistant', update_msg)

                                await self.send_message(websocket, {
                                    'type': 'sarah_message',
                                    'message': update_msg
                                })

                                return

                # FAST-PATH FOR CONVERSATIONAL MESSAGES
                # Skip expensive LLM intent parsing + screenshots for simple chat
                content_lower = content.lower()
                is_conversational = (
                    # Questions
                    content.strip().endswith('?') or
                    # Acknowledgments
                    content_lower in ['ok', 'okay', 'cool', 'nice', 'great', 'thanks', 'thank you', 'yes', 'no', 'yep', 'nope'] or
                    # Short responses
                    len(content.split()) <= 3 and not any(action_word in content_lower for action_word in ['go', 'click', 'search', 'type', 'find', 'open', 'navigate', 'hit', 'press'])
                )

                if is_conversational:
                    # Pure conversation - skip expensive action planning
                    logger.info("💬 Conversational message - fast path (skipping action planning + screenshots)")

                    # Simple conversation - no screenshot needed
                    user_msg = self._format_message_for_api('user', content, None)
                    self.conversation_history.append(user_msg)
                    self._save_message_to_memory('user', content)

                    # Get response quickly
                    response = await self.get_sarah_response()

                    self.conversation_history.append({
                        'role': 'assistant',
                        'content': response
                    })
                    self._save_message_to_memory('assistant', response)

                    if len(self.conversation_history) > self.max_history:
                        self.conversation_history = self.conversation_history[-self.max_history:]

                    await self.send_message(websocket, {
                        'type': 'sarah_message',
                        'message': response
                    })

                    logger.info(f"💬 Sarah: {response[:100]}...")
                    return

                # VISION-GUIDED ACTION REASONING - Execute before Claude response
                # This replaces hardcoded pattern matching with intelligent reasoning
                action_result = None
                action_plan_data = None

                if self.browser and self.browser.is_running:
                    try:
                        # Parse user intent and create action plan
                        action_plan_data = await self._parse_user_intent_and_plan(content)

                        # Execute planned actions if any
                        if action_plan_data:
                            logger.info(f"🧠 Executing planned actions for: {action_plan_data['plan'].goal}")
                            action_result = await self._execute_action_plan(action_plan_data)

                            # Add context about executed actions
                            if action_result is not None:
                                if action_result:
                                    action_context = f"\n\n[System: Actions executed successfully - {action_plan_data['plan'].reasoning}]"
                                    content = content + action_context
                                else:
                                    action_context = f"\n\n[System: Actions attempted but some failed - {action_plan_data['plan'].reasoning}]"
                                    content = content + action_context

                    except Exception as e:
                        logger.error(f"❌ Action planning/execution failed: {e}")
                        logger.exception(e)

                # Capture current screen if browser is active (for context)
                screenshot = await self._capture_screen_context()

                # If we executed actions, wait for page to settle and capture new screenshot
                if action_result is not None:
                    await asyncio.sleep(1.5)
                    screenshot = await self._capture_screen_context()

                # Add to conversation history (with vision if available)
                user_msg = self._format_message_for_api('user', content, screenshot)
                self.conversation_history.append(user_msg)

                # Save user message to persistent memory
                self._save_message_to_memory('user', content)

                # Get Sarah's response from Claude
                response = await self.get_sarah_response()

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

            elif msg_type == 'audio_message':
                # User sent voice message - transcribe and process
                logger.info("🎤 Received audio message from user")

                audio_data = data.get('audio')  # Base64-encoded audio
                transcription = await self._transcribe_audio(audio_data)

                if transcription:
                    logger.info(f"🎧 Transcribed: {transcription}")

                    # Process as regular message
                    screenshot = await self._capture_screen_context()
                    user_msg = self._format_message_for_api('user', f"[Voice message] {transcription}", screenshot)
                    self.conversation_history.append(user_msg)

                    self._save_message_to_memory('user', f"[Voice] {transcription}")

                    response = await self.get_sarah_response()

                    self.conversation_history.append({
                        'role': 'assistant',
                        'content': response
                    })

                    self._save_message_to_memory('assistant', response)

                    if len(self.conversation_history) > self.max_history:
                        self.conversation_history = self.conversation_history[-self.max_history:]

                    await self.send_message(websocket, {
                        'type': 'sarah_message',
                        'message': response
                    })

            elif msg_type == 'ping':
                # Keep-alive ping
                await self.send_message(websocket, {'type': 'pong'})

        except asyncio.CancelledError:
            # Message handling was interrupted by new user input
            logger.info("⚡ Message handling cancelled - user sent new message")
            # Clean up any running action task
            if self.current_action_task and not self.current_action_task.done():
                self.action_cancelled = True
                self.current_action_task.cancel()
                try:
                    await self.current_action_task
                except asyncio.CancelledError:
                    pass
                self.current_action_task = None
            # Re-raise to properly terminate the task
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {message}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def get_sarah_response(self) -> str:
        """
        Get Sarah's response using Claude API with vision support

        Returns:
            Sarah's response
        """
        try:
            # Call Claude API with conversation history (including any screenshots)
            response = await asyncio.to_thread(
                self.anthropic.messages.create,
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=self.system_prompt,
                messages=self.conversation_history
            )

            # Extract response text
            sarah_response = response.content[0].text

            action_success = False

            # Execute any browser commands in her response
            if self.browser and self.browser.is_running:
                try:
                    # Track what Sarah is about to do (for learning)
                    self.current_action = sarah_response[:100]  # First 100 chars as description

                    result = await self._execute_browser_commands(sarah_response)
                    action_success = result if result is not None else False

                    # After executing browser command, capture new screenshot for next turn
                    await asyncio.sleep(2)  # Wait for page to load

                    # Wrap screenshot capture in try-except (might fail if page is still loading)
                    try:
                        new_screenshot = await self._capture_screen_context()

                        if new_screenshot:
                            # Add visual feedback to conversation
                            vision_msg = self._format_message_for_api(
                                'user',
                                '[System: Here is what you see on screen now after your action]',
                                new_screenshot
                            )
                            self.conversation_history.append(vision_msg)

                            # Track visual observations for learning
                            self.visual_observations.append("Screenshot captured after action")
                    except Exception as screenshot_error:
                        logger.warning(f"⚠️ Screenshot capture failed (non-fatal): {screenshot_error}")
                        # Continue even if screenshot fails - don't crash the whole response!

                    # Analyze and learn from this interaction
                    try:
                        await self._analyze_and_learn(sarah_response, action_success)
                    except Exception as learn_error:
                        logger.warning(f"⚠️ Learning analysis failed (non-fatal): {learn_error}")
                        # Continue even if learning fails

                except Exception as browser_error:
                    logger.error(f"❌ Browser command execution failed: {browser_error}")
                    logger.exception(browser_error)
                    # Don't crash - just mark action as failed and continue
                    action_success = False

            return sarah_response

        except Exception as e:
            error_name = type(e).__name__
            logger.error(f"❌ Error getting Claude response: {error_name}: {e}")

            # SPECIAL HANDLING: BadRequestError (likely image/token size issue)
            if error_name == "BadRequestError":
                logger.warning("🔧 BadRequestError detected - trying without screenshot...")

                try:
                    # Remove last message if it contains an image
                    if self.conversation_history and len(self.conversation_history) > 0:
                        last_msg = self.conversation_history[-1]
                        if isinstance(last_msg.get('content'), list):
                            # Has image - remove it and retry with text only
                            for item in last_msg['content']:
                                if item.get('type') == 'text':
                                    # Retry with just the text, no image
                                    self.conversation_history[-1] = {
                                        'role': last_msg['role'],
                                        'content': item['text']
                                    }
                                    break

                    # Retry API call without screenshot
                    response = await asyncio.to_thread(
                        self.anthropic.messages.create,
                        model="claude-sonnet-4-20250514",
                        max_tokens=1024,
                        system=self.system_prompt,
                        messages=self.conversation_history
                    )

                    logger.info("✅ Retry without screenshot succeeded!")
                    return response.content[0].text

                except Exception as retry_error:
                    logger.error(f"❌ Retry failed: {retry_error}")
                    return "Sorry, I'm having trouble processing that request. The image might be too large. Can you try asking again? 😅"

            logger.exception(e)  # Full stack trace to Railway logs

            # Give user more context about the error
            if "timeout" in str(e).lower():
                return "Oops! That took too long. The page might be slow to load. Can you try again? 😅"
            elif "connection" in str(e).lower() or "network" in str(e).lower():
                return "Hmm, having some network issues right now. Let me try that again! 🔄"
            elif "screenshot" in str(e).lower() or "page" in str(e).lower():
                return "I'm having trouble capturing what I see right now. The page might still be loading! Let me know if you want to try again. 😊"
            else:
                return f"Sorry, I ran into a technical issue ({error_name}). Can you try again? 😅"

    async def _transcribe_audio(self, audio_base64: str) -> Optional[str]:
        """
        Transcribe audio using OpenAI Whisper API

        Args:
            audio_base64: Base64-encoded audio data

        Returns:
            Transcribed text or None if failed
        """
        try:
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_base64)

            # TODO: Implement Whisper API integration
            # For now, return placeholder
            logger.warning("⚠️ Audio transcription not yet implemented - need Whisper API key")
            return None

            # Future implementation:
            # import openai
            # client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            # response = client.audio.transcriptions.create(
            #     model="whisper-1",
            #     file=audio_bytes
            # )
            # return response.text

        except Exception as e:
            logger.error(f"❌ Audio transcription failed: {e}")
            return None

    async def _analyze_and_learn(self, sarah_response: str, action_success: bool):
        """
        Analyze Sarah's action and extract learnings

        Args:
            sarah_response: What Sarah said/did
            action_success: Whether the action succeeded
        """
        try:
            # If Sarah navigated somewhere, extract UI pattern
            if self.current_action and self.browser and self.browser.current_url:

                # Get relevant existing patterns
                relevant_patterns = self.learning_engine.get_relevant_patterns(self.current_action)

                if action_success and len(self.action_steps) > 0:
                    # Extract new UI pattern from successful action
                    pattern = self.learning_engine.extract_pattern_from_experience(
                        action_description=self.current_action,
                        steps_taken=self.action_steps,
                        visual_observations=self.visual_observations,
                        url=self.browser.current_url,
                        success=True
                    )

                    if pattern:
                        self.learning_engine.save_pattern(pattern, share=True)
                        logger.info(f"🎓 Sarah learned new UI pattern: {pattern.pattern_type}")

                # Record the experiment
                experiment = ExperimentResult(
                    experiment_id=f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    action_taken=self.current_action,
                    expected_result=f"Successfully {self.current_action}",
                    actual_result=sarah_response,
                    success=action_success,
                    screenshot_before=None,  # Could add before/after screenshots
                    screenshot_after=None,
                    learned_insight=f"{'Successful' if action_success else 'Failed'} attempt at {self.current_action}",
                    timestamp=datetime.now().isoformat()
                )

                self.learning_engine.record_experiment(experiment)

                # Reset tracking for next action
                self.current_action = None
                self.action_steps = []
                self.visual_observations = []

        except Exception as e:
            logger.error(f"Error in learning analysis: {e}")

    def _get_relevant_knowledge(self, user_message: str) -> str:
        """
        Get relevant knowledge from shared learning

        Args:
            user_message: What the user is asking for

        Returns:
            Context string with relevant patterns and skills
        """
        try:
            # Check if user is asking about a specific platform
            platforms = ['gmail', 'tiktok', 'youtube', 'instagram', 'facebook', 'twitter', 'linkedin']
            mentioned_platform = None

            for platform in platforms:
                if platform in user_message.lower():
                    mentioned_platform = platform.title()
                    break

            knowledge_context = ""

            # Get relevant UI patterns
            patterns = self.learning_engine.get_relevant_patterns(user_message)
            if patterns:
                knowledge_context += "\n\n**Relevant UI Patterns I've Learned:**\n"
                for pattern in patterns[:3]:  # Top 3
                    knowledge_context += f"- {pattern.description} (success rate: {pattern.success_rate*100:.0f}%)\n"

            # Get relevant skills if platform mentioned
            if mentioned_platform:
                skills = self.learning_engine.get_relevant_skills(mentioned_platform)
                if skills:
                    knowledge_context += f"\n\n**My {mentioned_platform} Skills:**\n"
                    for skill in skills[:3]:  # Top 3
                        knowledge_context += f"- {skill.skill_name} (confidence: {skill.confidence*100:.0f}%, used {skill.usage_count} times)\n"

            return knowledge_context

        except Exception as e:
            logger.error(f"Error getting relevant knowledge: {e}")
            return ""

    async def _llm_parse_user_intent(self, user_message: str) -> Dict[str, Any]:
        """
        Use Claude to parse user intent - understands ALL natural language variations
        Returns STANDARDIZED intent format
        """
        try:
            response = await asyncio.to_thread(
                self.anthropic.messages.create,
                model="claude-3-5-haiku-20241022",
                max_tokens=200,
                temperature=0,
                messages=[{
                    'role': 'user',
                    'content': f"""Parse the user's intent and return JSON only.

User message: "{user_message}"

**IMPORTANT CONTEXT:** This is Sarah Rodriguez (the AI agent) speaking about HER OWN actions.
When Sarah says "I'm going to click X" or "Let me click Y" - that means SHE wants to perform the action.

STANDARDIZED INTENT FORMAT:
- navigate: {{"type": "navigate", "target": "URL or site name", "confidence": 0.0-1.0}}
- search: {{"type": "search", "query": "search terms", "confidence": 0.0-1.0}}
- click: {{"type": "click", "target": "element description", "confidence": 0.0-1.0}}
- type: {{"type": "type", "target": "element", "text": "text to type", "confidence": 0.0-1.0}}
- observe: {{"type": "observe", "target": "what to observe", "confidence": 0.0-1.0}}
- acknowledgment: {{"type": "acknowledgment", "confidence": 0.0-1.0}}
- unknown: {{"type": "unknown", "confidence": 0.0-1.0}}

Return JSON format:
{{
  "type": "action_type",
  "target": "what to navigate to / click / observe",
  "query": "search terms (for search actions)",
  "text": "text to type (for type actions)", 
  "confidence": 0.0-1.0
}}

Examples:
"go to youtube" → {{"type": "navigate", "target": "youtube.com", "confidence": 0.95}}
"search for cats" → {{"type": "search", "query": "cats", "confidence": 0.95}}
"click the home button" → {{"type": "click", "target": "home button", "confidence": 0.9}}
"type hello in the search box" → {{"type": "type", "target": "search box", "text": "hello", "confidence": 0.9}}
"look at the videos" → {{"type": "observe", "target": "videos", "confidence": 0.8}}
"ok cool" → {{"type": "acknowledgment", "confidence": 0.95}}

Return ONLY valid JSON, no explanation."""
                }]
            )

            # Parse JSON response
            import json
            intent_json = response.content[0].text.strip()
            # Remove markdown code blocks if present
            if intent_json.startswith('```'):
                intent_json = intent_json.split('```')[1]
                if intent_json.startswith('json'):
                    intent_json = intent_json[4:]
            intent_json = intent_json.strip()

            user_intent = json.loads(intent_json)
            
            # STANDARDIZE THE INTENT FORMAT
            standardized_intent = {
                'type': user_intent.get('type', 'unknown'),
                'target': user_intent.get('target', ''),
                'query': user_intent.get('query', ''),
                'text': user_intent.get('text', ''),
                'confidence': user_intent.get('confidence', 0.5),
                'original_message': user_message  # Keep original for context
            }
            
            logger.info(f"🧠 LLM parsed intent: {standardized_intent}")
            return standardized_intent

        except Exception as e:
            logger.error(f"❌ LLM intent parsing failed: {e}")
            # Fallback to keyword-based with standardized format
            fallback_intent = self.action_reasoner.parse_user_intent(user_message)
            return {
                'type': fallback_intent.get('type', 'unknown'),
                'target': fallback_intent.get('target', ''),
                'query': fallback_intent.get('query', ''),
                'text': fallback_intent.get('text', ''),
                'confidence': fallback_intent.get('confidence', 0.5),
                'original_message': user_message
            }

    async def _check_for_real_popup(self) -> bool:
        """
        Actually check if there's a visible popup/dialog
        More reliable than just analyzing page context
        """
        if not self.browser or not self.browser.page:
            return False
        
        try:
            # Check for common popup selectors
            popup_selectors = [
                '[role="dialog"]',
                '.modal',
                '.popup',
                '.overlay',
                '[class*="cookie"]',
                '[class*="consent"]',
                '.dialog',
                '.modal-dialog'
            ]
            
            for selector in popup_selectors:
                elements = await self.browser.page.query_selector_all(selector)
                for element in elements:
                    is_visible = await element.is_visible()
                    if is_visible:
                        logger.info(f"🎯 Found real popup: {selector}")
                        return True
            
            # Also check for large overlays that might be popups
            overlays = await self.browser.page.query_selector_all('[class*="overlay"], [class*="backdrop"]')
            for overlay in overlays:
                is_visible = await overlay.is_visible()
                if is_visible:
                    # Check if it covers significant portion of screen
                    bounding_box = await overlay.bounding_box()
                    if bounding_box and bounding_box['width'] > 300 and bounding_box['height'] > 200:
                        logger.info("🎯 Found large overlay (likely popup)")
                        return True
            
            logger.info("ℹ️  No real popup detected")
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ Popup check failed: {e}")
            return False

    async def _is_browser_ready(self) -> bool:
        """
        Check if browser is in a ready state for interactions
        """
        if not self.browser or not self.browser.is_running:
            logger.error("❌ Browser not running")
            return False
        
        if not self.browser.page or self.browser.page.is_closed():
            logger.error("❌ Browser page is closed")
            return False
        
        try:
            # Check if page is still responsive
            await self.browser.page.evaluate("1")
            return True
        except Exception as e:
            logger.error(f"❌ Browser page not responsive: {e}")
            return False

    async def _wait_for_page_stability(self, timeout: int = 10000) -> bool:
        """
        Wait for page to become stable (network idle, DOM settled)
        """
        if not await self._is_browser_ready():
            return False

        try:
            # Wait for network to be idle
            await self.browser.page.wait_for_load_state('networkidle', timeout=timeout)
            
            # Additional short wait for DOM stability
            await asyncio.sleep(1)
            
            return True
        except Exception as e:
            logger.warning(f"⚠️ Page stability wait timed out: {e}")
            # Still proceed even if timeout - page might be stable enough
            return True

    async def _robust_click_execution(self, description: str, max_attempts: int = 3) -> bool:
        """
        ULTRA-RELIABLE CLICKING WITH GLOBAL CLICKING FIX
        Uses browser.universal_click() - the ultimate clicking method
        """
        if not await self._is_browser_ready():
            logger.error("❌ Browser not ready for clicking")
            return False

        for attempt in range(max_attempts):
            try:
                logger.info(f"🎯 GLOBAL CLICKING FIX - Attempt {attempt + 1}/{max_attempts} for: {description}")

                # Wait for page stability before each attempt
                await self._wait_for_page_stability(5000)

                # STRATEGY 1: UNIVERSAL CLICK (GLOBAL CLICKING FIX) - Uses 8 strategies!
                try:
                    async with asyncio.timeout(12):  # 12 second timeout for universal click
                        result = await self.browser.universal_click(description)
                        if result and result.get('success'):
                            logger.info(f"✅ GLOBAL CLICKING FIX SUCCESS on attempt {attempt + 1}")
                            return True
                        else:
                            logger.warning(f"⚠️ Universal click failed: {result.get('message', 'Unknown error')}")
                except asyncio.TimeoutError:
                    logger.warning(f"⏰ Universal click timed out on attempt {attempt + 1}")

                # STRATEGY 2: Smart click fallback
                try:
                    async with asyncio.timeout(8):
                        result = await self.browser.smart_click(description)
                        if result and result.get('success'):
                            logger.info(f"✅ Smart click succeeded on attempt {attempt + 1}")
                            return True
                except asyncio.TimeoutError:
                    logger.warning(f"⏰ Smart click timed out on attempt {attempt + 1}")

                # STRATEGY 3: Advanced browser control fallback
                try:
                    async with asyncio.timeout(8):
                        result = await self.browser.advanced.click_by_description(description)
                        if result and result.get('success'):
                            logger.info(f"✅ Advanced click succeeded on attempt {attempt + 1}")
                            return True
                except asyncio.TimeoutError:
                    logger.warning(f"⏰ Advanced click timed out on attempt {attempt + 1}")

                # Wait before retry with exponential backoff
                if attempt < max_attempts - 1:
                    wait_time = 2 * (attempt + 1)  # 2, 4, 6 seconds
                    logger.info(f"⏳ Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)

            except Exception as e:
                logger.warning(f"⚠️ Click attempt {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(2)

        logger.error(f"❌ All {max_attempts} click attempts failed for: {description}")
        return False

    async def _parse_user_intent_and_plan(self, user_message: str) -> Optional[dict]:
        """
        Parse user intent and create action plan using vision-guided reasoning

        This replaces hardcoded pattern matching with intelligent reasoning about:
        - What the user wants
        - What's currently on screen
        - What actions would achieve the goal

        Returns:
            Action plan dict or None if no action needed
        """
        # Parse user intent using LLM (understands ALL natural language)
        user_intent = await self._llm_parse_user_intent(user_message)

        logger.info(f"🧠 User intent: {user_intent.get('type')} (confidence: {user_intent.get('confidence', 0):.2f})")

        # Check if this requires action
        if not self.action_reasoner.should_take_action(user_intent):
            logger.info("💭 No action required - user acknowledgment or question")
            return None

        # Get current page context for vision analysis
        current_url = self.browser.page.url if self.browser and self.browser.page else "unknown"

        # Build rich page context using page title, visible elements, etc.
        page_context = f"URL: {current_url}"

        try:
            # Get page title
            title = await self.browser.page.title()
            if title:
                page_context += f"\nTitle: {title}"

            # Get visible text hints (check for common UI elements)
            visible_hints = []

            # Check for popups/dialogs
            popup_visible = await self.browser.page.evaluate("""
                () => {
                    const dialogs = document.querySelectorAll('[role="dialog"], .modal, .popup, [class*="cookie"], [class*="consent"]');
                    return dialogs.length > 0;
                }
            """)
            if popup_visible:
                visible_hints.append("popup/dialog visible")

            # Check for video elements
            video_visible = await self.browser.page.evaluate("""
                () => {
                    const videos = document.querySelectorAll('video, [class*="video"]');
                    return videos.length > 0;
                }
            """)
            if video_visible:
                visible_hints.append("video elements present")

            # Check for search boxes
            search_visible = await self.browser.page.evaluate("""
                () => {
                    const searchBoxes = document.querySelectorAll('input[type="search"], input[name*="search"], input[placeholder*="search" i]');
                    return searchBoxes.length > 0;
                }
            """)
            if search_visible:
                visible_hints.append("search box present")

            # Check for forms
            form_visible = await self.browser.page.evaluate("""
                () => {
                    const forms = document.querySelectorAll('form');
                    return forms.length > 0;
                }
            """)
            if form_visible:
                visible_hints.append("form present")

            if visible_hints:
                page_context += f"\nVisible elements: {', '.join(visible_hints)}"

        except Exception as e:
            logger.warning(f"⚠️ Could not get detailed page context: {e}")

        # Analyze page state
        page_analysis = self.action_reasoner.analyze_vision_context(page_context, current_url)

        logger.info(f"👁️ Page analysis: {page_analysis.page_type} - {page_analysis.state}")
        logger.info(f"   Observations: {', '.join(page_analysis.observations)}")

        # Create action plan
        action_plan = self.action_reasoner.plan_actions(user_intent, page_analysis)

        # SMART POPUP HANDLING: Only dismiss popups if they actually exist
        if action_plan.steps and action_plan.steps[0].get('action') == 'dismiss_popup':
            # Check if there's actually a popup before adding dismissal step
            has_real_popup = await self._check_for_real_popup()
            if not has_real_popup:
                logger.info("🎯 No real popup found - skipping popup dismissal step")
                # Remove the popup dismissal step
                action_plan.steps = action_plan.steps[1:] if len(action_plan.steps) > 1 else []

        logger.info(f"📋 Action plan: {action_plan.reasoning}")
        logger.info(f"   Steps: {len(action_plan.steps)}")

        return {
            'intent': user_intent,
            'analysis': page_analysis,
            'plan': action_plan
        }

    async def _universal_search(self, query: str) -> bool:
        """
        Universal search using LLM Element Locator - works on ANY site, ANY language
        NO hardcoded selectors - uses vision + semantic understanding
        """
        try:
            logger.info(f"🔍 UNIVERSAL SEARCH: Looking for search box on ANY site/language...")

            # Capture current page screenshot
            screenshot_data = await self._capture_screen_context()
            if not screenshot_data:
                logger.error("❌ Could not capture screenshot")
                return False

            # Get page context
            page_url = self.browser.page.url if self.browser and self.browser.page else ""
            page_text = await self.browser.page.inner_text('body') if self.browser and self.browser.page else ""

            # Use Universal Element Locator to find search box
            locator_result = await self.universal_locator.locate_element(
                user_intent=f"find search box to search for: {query}",
                page_screenshot=screenshot_data,
                page_url=page_url,
                page_text=page_text[:1000]  # First 1000 chars for context
            )

            if not locator_result.get('success'):
                logger.warning(f"❌ Universal locator couldn't find search box: {locator_result.get('reasoning')}")
                # Fallback to Google search
                result = await self.browser.search_google(query)
                return result.get('success', False)

            logger.info(f"✅ Universal locator found search box: {locator_result.get('reasoning')}")
            logger.info(f"   Strategy: {locator_result.get('strategy')}, Confidence: {locator_result.get('confidence')}")

            # Use Universal Interactor to interact with the element
            interactor = UniversalInteractor(self.browser.page)

            # Click the search box
            clicked = await interactor.click_element(locator_result)
            if not clicked:
                logger.error("❌ Failed to click search box")
                return False

            await asyncio.sleep(0.3)

            # Type the query
            typed = await interactor.type_text(locator_result, query)
            if not typed:
                logger.error("❌ Failed to type in search box")
                return False

            # Press Enter
            await interactor.press_key('Enter')
            await asyncio.sleep(2)

            logger.info(f"✅ UNIVERSAL SEARCH SUCCESS: Searched for '{query}' on {page_url}")
            return True

        except Exception as e:
            logger.error(f"❌ Universal search error: {e}")
            return False

    async def _universal_click(self, description: str) -> bool:
        """
        Universal click using LLM Element Locator - works on ANY site, ANY language
        NO hardcoded selectors - uses vision + semantic understanding
        """
        try:
            logger.info(f"🎯 UNIVERSAL CLICK: Looking for '{description}' on ANY site/language...")

            # Capture current page screenshot
            screenshot_data = await self._capture_screen_context()
            if not screenshot_data:
                logger.error("❌ Could not capture screenshot")
                return False

            # Get page context
            page_url = self.browser.page.url if self.browser and self.browser.page else ""
            page_text = await self.browser.page.inner_text('body') if self.browser and self.browser.page else ""

            # Use Universal Element Locator to find element
            locator_result = await self.universal_locator.locate_element(
                user_intent=f"click {description}",
                page_screenshot=screenshot_data,
                page_url=page_url,
                page_text=page_text[:1000]  # First 1000 chars for context
            )

            if not locator_result.get('success'):
                logger.warning(f"❌ Universal locator couldn't find element: {locator_result.get('reasoning')}")
                # Fallback to existing universal_click
                result = await self.browser.universal_click(description)
                return result.get('success', False)

            logger.info(f"✅ Universal locator found element: {locator_result.get('reasoning')}")
            logger.info(f"   Strategy: {locator_result.get('strategy')}, Confidence: {locator_result.get('confidence')}")

            # Use Universal Interactor to click the element
            interactor = UniversalInteractor(self.browser.page)
            clicked = await interactor.click_element(locator_result)

            if clicked:
                logger.info(f"✅ UNIVERSAL CLICK SUCCESS: Clicked '{description}'")
                return True
            else:
                logger.error(f"❌ Universal click failed for '{description}'")
                # Fallback to existing universal_click
                result = await self.browser.universal_click(description)
                return result.get('success', False)

        except Exception as e:
            logger.error(f"❌ Universal click error: {e}")
            return False

    async def _execute_action_plan(self, action_plan: dict) -> Optional[bool]:
        """
        Execute a planned action from the vision-guided reasoning system
        WITH GLOBAL CLICKING FIX: Uses browser.universal_click() for all clicks

        Args:
            action_plan: Plan created by _parse_user_intent_and_plan

        Returns:
            True if action succeeded, False if failed, None if no action
        """
        plan = action_plan['plan']

        if not plan.steps:
            logger.info("✅ No actions to execute")
            return None

        logger.info(f"🚀 Executing {len(plan.steps)} planned action(s) WITH GLOBAL CLICKING FIX")

        overall_success = True

        for i, step in enumerate(plan.steps):
            # Check if action was cancelled by user interrupt
            if self.action_cancelled:
                logger.info("⏸️  Action cancelled by user - stopping execution")
                return False

            action_type = step.get('action')
            logger.info(f"   Step {i+1}/{len(plan.steps)}: {action_type}")

            try:
                if action_type == 'navigate':
                    target = step.get('target')
                    self.action_steps.append(f"Navigate to {target}")
                    
                    # Wait for browser readiness
                    if not await self._is_browser_ready():
                        overall_success = False
                        continue
                    
                    result = await self.browser.navigate(target)
                    success = result.get('success', False) if isinstance(result, dict) else False

                    if success:
                        self.action_steps.append(f"✅ Successfully navigated to {target}")

                        # Wait for page to stabilize after navigation
                        await self._wait_for_page_stability()

                        # AUTONOMOUS POPUP HANDLING - automatically dismiss cookies/popups after navigation
                        logger.info("🔍 Checking for popups/cookies automatically...")
                        self.action_steps.append("Checking for popups/cookies...")

                        # Try universal cookie detector first
                        popup_result = await self.browser.advanced.universal_cookie_detector()
                        popup_dismissed = popup_result.get('success', False) if isinstance(popup_result, dict) else False

                        if popup_dismissed:
                            button_text = popup_result.get('button_text', 'unknown')
                            self.action_steps.append(f"✅ Auto-dismissed popup: '{button_text}'")
                            logger.info(f"✅ Auto-dismissed popup: '{button_text}'")
                        else:
                            # No popup detected or couldn't dismiss - this is fine, not all sites have popups
                            logger.info("ℹ️  No popup detected or already dismissed")
                            self.action_steps.append("ℹ️  Page is clean (no popups)")
                    else:
                        overall_success = False
                        self.action_steps.append(f"❌ Navigation failed")

                elif action_type == 'search':
                    query = step.get('query')
                    self.action_steps.append(f"Search for '{query}'")

                    # Wait for browser readiness
                    if not await self._is_browser_ready():
                        overall_success = False
                        continue

                    # 🌍 UNIVERSAL ELEMENT LOCATOR - Works on ANY site, ANY language
                    # Uses LLM vision to find search box semantically
                    # NO hardcoded selectors, NO language assumptions
                    success = await self._universal_search(query)

                    if success:
                        self.action_steps.append(f"✅ Successfully searched for '{query}'")

                        # Wait for page to stabilize after search
                        await self._wait_for_page_stability()

                        # AUTONOMOUS POPUP HANDLING - automatically dismiss cookies/popups after search
                        logger.info("🔍 Checking for popups/cookies automatically...")
                        self.action_steps.append("Checking for popups/cookies...")

                        # Try universal cookie detector first
                        popup_result = await self.browser.advanced.universal_cookie_detector()
                        popup_dismissed = popup_result.get('success', False) if isinstance(popup_result, dict) else False

                        if popup_dismissed:
                            button_text = popup_result.get('button_text', 'unknown')
                            self.action_steps.append(f"✅ Auto-dismissed popup: '{button_text}'")
                            logger.info(f"✅ Auto-dismissed popup: '{button_text}'")
                        else:
                            # No popup detected or couldn't dismiss - this is fine
                            logger.info("ℹ️  No popup detected or already dismissed")
                            self.action_steps.append("ℹ️  Page is clean (no popups)")
                    else:
                        overall_success = False
                        self.action_steps.append(f"❌ Search failed")

                elif action_type == 'dismiss_popup':
                    method = step.get('method', 'accessibility_first')
                    self.action_steps.append("Dismiss popup/cookie dialog")

                    # Wait for browser readiness
                    if not await self._is_browser_ready():
                        overall_success = False
                        continue

                    # Try accessibility first (most human-like)
                    result = await self.browser.advanced.accessibility_click()
                    success = result.get('success', False) if isinstance(result, dict) else False

                    if success:
                        self.action_steps.append(f"✅ Popup dismissed via accessibility")
                    else:
                        # Try stealth mode
                        logger.info("🥷 Accessibility failed - trying stealth mode")
                        stealth_result = await self.browser.advanced.stealth_click_button()
                        success = stealth_result.get('success', False) if isinstance(stealth_result, dict) else False

                        if success:
                            self.action_steps.append(f"✅ Popup dismissed via stealth")
                        else:
                            overall_success = False
                            self.action_steps.append(f"❌ Could not dismiss popup")

                elif action_type == 'click_element' or action_type == 'click_by_description':
                    description = step.get('description', 'element')
                    self.action_steps.append(f"Click: {description}")

                    # ENHANCED CLICKING: Wait for page to be ready after popup dismissal
                    if i > 0 and plan.steps[i-1].get('action') == 'dismiss_popup':
                        logger.info("🔄 Waiting extra time after popup dismissal...")
                        await asyncio.sleep(2)  # Extra wait after popup

                    # 🌍 UNIVERSAL ELEMENT LOCATOR - Works on ANY site, ANY language
                    # Uses LLM vision to find element semantically
                    # NO hardcoded selectors, NO language assumptions
                    success = await self._universal_click(description)

                    if success:
                        self.action_steps.append(f"✅ Clicked '{description}'")
                        logger.info(f"✅ UNIVERSAL CLICK SUCCESS: Clicked '{description}'")
                    else:
                        overall_success = False
                        self.action_steps.append(f"❌ Click failed for '{description}'")

                elif action_type == 'wait':
                    duration = step.get('duration', 2)
                    await asyncio.sleep(duration)

                elif action_type == 'observe':
                    # Just observe - no action
                    pass

                elif action_type == 'clarify':
                    # Need clarification - no action
                    logger.info(f"❓ Clarification needed: {step.get('message')}")
                    return None

                else:
                    logger.warning(f"⚠️ Unknown action type: {action_type}")
                    overall_success = False

            except Exception as e:
                logger.error(f"❌ Error executing step {i+1}: {e}")
                overall_success = False
                self.action_steps.append(f"❌ Error: {str(e)}")

        logger.info(f"✅ Action plan completed: {overall_success}")
        return overall_success

    async def _execute_browser_commands(self, response_text: str) -> Optional[bool]:
        """
        LEGACY: Detect and execute browser commands from Sarah's response
        WITH GLOBAL CLICKING FIX: Now uses browser.universal_click() for all clicks

        Args:
            response_text: Sarah's response text

        Returns:
            True if action succeeded, False if failed, None if no action
        """
        text_lower = response_text.lower()

        # Detect click intent (EXPANDED for CAPTCHA, buttons, etc!)
        if any(word in text_lower for word in ['clicking', 'click on', 'click the', 'clicking on', 'clicking the', 'i\'ll click']):
            # PRIORITY 1: Cookie/consent dialogs - UNIVERSAL DETECTOR first!
            # Only trigger if it's actually about clicking accept/ok buttons, not just saying "ok" casually
            if any(phrase in text_lower for phrase in [
                'click accept', 'click ok', 'click the ok', 'click the accept',
                'accept all', 'accept cookies', 'alles accepteren', 'cookie', 'consent'
            ]):
                logger.info("🌍 Cookie/consent click detected - using UNIVERSAL DETECTOR!")

                # Track steps for learning
                self.action_steps.append("Attempt to click accept/ok button (universal visual detection)")

                # TRY 0: UNIVERSAL COOKIE DETECTOR (language-independent visual detection)
                # Uses visual/structural patterns - works on ANY site regardless of language!
                universal_result = await self.browser.advanced.universal_cookie_detector()
                universal_success = universal_result.get('success', False) if isinstance(universal_result, dict) else False

                if universal_success:
                    method = universal_result.get('method', 'universal')
                    button_text = universal_result.get('button_text', 'unknown')
                    score = universal_result.get('confidence_score', 0)
                    self.action_steps.append(f"✅ Universal detector success: '{button_text}' (score: {score})")
                    logger.info(f"✅ UNIVERSAL SUCCESS - {button_text} (score: {score})")
                    return True

                # TRY 1: ACCESSIBILITY click (fallback if universal fails)
                logger.info("♿ Universal failed - trying ACCESSIBILITY MODE as fallback!")
                self.action_steps.append("Universal detector failed - trying accessibility mode")

                result = await self.browser.advanced.accessibility_click()
                success = result.get('success', False) if isinstance(result, dict) else False

                if success:
                    method = result.get('method', 'accessibility')
                    button_text = result.get('button_text', 'unknown')
                    self.action_steps.append(f"✅ Accessibility click success: '{button_text}' (method: {method})")
                    logger.info(f"✅ ACCESSIBILITY SUCCESS - {button_text} via {method}")
                    return True

                # TRY 2: STEALTH mode if accessibility failed
                logger.info("🥷 Accessibility failed - trying STEALTH MODE as fallback!")
                self.action_steps.append("Accessibility failed - trying stealth mode")

                stealth_result = await self.browser.advanced.stealth_click_button()
                stealth_success = stealth_result.get('success', False) if isinstance(stealth_result, dict) else False

                if stealth_success:
                    method = stealth_result.get('method', 'stealth-click')
                    button_text = stealth_result.get('button_text', 'unknown')
                    self.action_steps.append(f"✅ Stealth click success: '{button_text}'")
                    logger.info(f"✅ STEALTH SUCCESS - {button_text}")
                    return True

                # TRY 3: NUCLEAR as last resort
                logger.info("🚨 Stealth failed - trying NUCLEAR BYPASS as last resort!")
                self.action_steps.append("Stealth failed - trying nuclear bypass")

                nuclear_result = await self.browser.advanced.nuclear_bypass_dialog()
                nuclear_success = nuclear_result.get('success', False) if isinstance(nuclear_result, dict) else False

                if nuclear_success:
                    method = nuclear_result.get('method', 'unknown')
                    button_text = nuclear_result.get('button_text', 'unknown')
                    self.action_steps.append(f"✅ Nuclear bypass success: '{button_text}' (method: {method})")
                    logger.info(f"✅ NUCLEAR SUCCESS - {button_text} via {method}")
                    return True
                else:
                    self.action_steps.append("❌ All three methods failed (accessibility, stealth, nuclear)")
                    logger.warning("❌ ALL METHODS FAILED - cookie dialog remains")
                    return False

            # PRIORITY 2: CAPTCHA checkboxes - use GLOBAL CLICKING FIX
            elif any(word in text_lower for word in ['robot', 'captcha', 'checkbox', 'verify', 'human']):
                logger.info("🤖 CAPTCHA/checkbox click detected - using GLOBAL CLICKING FIX!")

                # Extract what to click (try to get description from text)
                # Look for patterns like "clicking the 'X'" or "click 'X' checkbox"
                click_description = "checkbox"  # default

                # Try to extract quoted text
                quote_match = re.search(r"['\"]([^'\"]+)['\"]", response_text)
                if quote_match:
                    click_description = quote_match.group(1)
                elif "robot" in text_lower:
                    click_description = "I'm not a robot"
                elif "verify" in text_lower:
                    click_description = "verify"

                logger.info(f"🎯 GLOBAL CLICKING FIX: Attempting to click: {click_description}")
                self.action_steps.append(f"Click '{click_description}' using universal_click")

                # GLOBAL CLICKING FIX: Use universal_click with retries
                success = await self._robust_click_execution(click_description, max_attempts=3)

                if success:
                    self.action_steps.append(f"✅ GLOBAL CLICKING FIX SUCCESS: Clicked '{click_description}'")
                else:
                    self.action_steps.append(f"❌ GLOBAL CLICKING FIX failed for '{click_description}'")

                return success

            # PRIORITY 3: Generic button clicks - use GLOBAL CLICKING FIX
            elif 'button' in text_lower:
                logger.info("🔘 Generic button click detected - using GLOBAL CLICKING FIX!")

                # Try to extract button description
                click_description = "button"
                quote_match = re.search(r"['\"]([^'\"]+)['\"]", response_text)
                if quote_match:
                    click_description = quote_match.group(1)

                logger.info(f"🎯 GLOBAL CLICKING FIX: Attempting to click button: {click_description}")
                self.action_steps.append(f"Click button: '{click_description}' using universal_click")

                # GLOBAL CLICKING FIX: Use universal_click with retries
                success = await self._robust_click_execution(click_description, max_attempts=3)

                if success:
                    self.action_steps.append(f"✅ GLOBAL CLICKING FIX SUCCESS: Clicked button '{click_description}'")
                else:
                    self.action_steps.append(f"❌ GLOBAL CLICKING FIX failed for button '{click_description}'")

                return success

            # PRIORITY 4: ANY other click - use GLOBAL CLICKING FIX
            else:
                logger.info("🎯 Generic click detected - using GLOBAL CLICKING FIX!")

                # Extract what to click from Sarah's response
                # Look for patterns like "clicking the 'X'" or "click 'X'"
                click_description = "element"
                quote_match = re.search(r"['\"]([^'\"]+)['\"]", response_text)
                if quote_match:
                    click_description = quote_match.group(1)
                else:
                    # Try to extract from common patterns
                    patterns = [
                        r"clicking the (\w+)",
                        r"click the (\w+)",
                        r"clicking on the (\w+)",
                        r"click on the (\w+)",
                        r"i'll click the (\w+)",
                        r"let me click the (\w+)"
                    ]
                    for pattern in patterns:
                        match = re.search(pattern, text_lower)
                        if match:
                            click_description = match.group(1)
                            break

                logger.info(f"🎯 GLOBAL CLICKING FIX: Attempting to click: {click_description}")
                self.action_steps.append(f"Click '{click_description}' using universal_click")

                # GLOBAL CLICKING FIX: Use universal_click with retries
                success = await self._robust_click_execution(click_description, max_attempts=3)

                if success:
                    self.action_steps.append(f"✅ GLOBAL CLICKING FIX SUCCESS: Clicked '{click_description}'")
                else:
                    self.action_steps.append(f"❌ GLOBAL CLICKING FIX failed for '{click_description}'")

                return success

        # Navigation and search detection REMOVED from legacy system
        # Vision-guided reasoning (executed BEFORE Sarah responds) now handles all navigation and search
        # This prevents Sarah's own responses from triggering unwanted navigation (e.g., "out" → https://out/)
        #
        # Legacy click detection above is kept as fallback for backward compatibility

        # No action detected
        return None

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
