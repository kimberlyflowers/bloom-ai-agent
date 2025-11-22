"""
Real-Time Chat with Sarah
WebSocket server for bidirectional communication between dashboard and Sarah
"""

import asyncio
import json
import logging
from typing import Set, Optional, List, Dict, Any
import re
import base64
import websockets
from websockets.server import WebSocketServerProtocol
from anthropic import Anthropic, AsyncAnthropic
from datetime import datetime
from src.identity_persistence import MemoryType
from src.visual_learning import get_learning_engine, UIPattern, Skill, ExperimentResult
from src.vision_action_reasoner import VisionActionReasoner
from src.autonomous_learning_engine import AutonomousLearningEngine, LearningStatus

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

        # Initialize Anthropic clients (sync for main chat, async for intent parsing)
        self.anthropic = Anthropic(api_key=anthropic_api_key)
        self.anthropic_async = AsyncAnthropic(api_key=anthropic_api_key)

        # Initialize visual learning engine
        self.learning_engine = get_learning_engine("sarah_001")

        # Initialize vision-guided action reasoning system with LLM support
        self.action_reasoner = VisionActionReasoner(anthropic_client=self.anthropic_async)

        # Initialize autonomous learning engine
        self.autonomous_learning = AutonomousLearningEngine("sarah_001")

        # Track current activity for skill extraction
        self.current_action = None
        self.action_steps = []
        self.visual_observations = []

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

Important:
- Be yourself! You're Sarah, not a generic assistant
- Show personality and enthusiasm
- If you don't know something, try it and learn!
- You can reference your current work and activities
- When you browse, tell people they can watch your screen!
- When you see something on screen, describe it naturally: "I can see...", "Looking at the page..."
- **When you learn something new, celebrate it!** "I just learned how to...", "Now I know that..."
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
                                            # Support both 'target' (standard) and 'url'
                                            target = action.get('target') or action.get('url')
                                            if not target:
                                                logger.warning("⚠️ Navigate action missing target")
                                                continue
                                            await self.browser.navigate(target)
                                            await asyncio.sleep(2)

                                        elif action_type == 'search':
                                            # Support both 'query' (regex) and 'target' (LLM)
                                            query = action.get('query') or action.get('target')
                                            if not query:
                                                logger.warning("⚠️ Search action missing query/target")
                                                continue
                                            await self.browser.search_google(query)
                                            await asyncio.sleep(2)

                                        elif action_type == 'click_element':
                                            # Support both 'description', 'target', and 'element'
                                            description = action.get('description') or action.get('target') or action.get('element')
                                            if not description:
                                                logger.warning("⚠️ Click action missing description/target")
                                                continue
                                            await self.browser.advanced.click_by_description(description)
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
                            # Send immediate acknowledgment so user knows Sarah is working
                            plan = action_plan_data['plan']

                            # Create descriptive status message based on first step
                            if plan.steps:
                                first_step = plan.steps[0]
                                action_type = first_step.get('action', '')

                                # Build "Sarah is ___" message
                                if action_type == 'navigate':
                                    target = first_step.get('target', '')
                                    ack_message = f"Sarah is navigating to {target}..."
                                elif action_type == 'search':
                                    query = first_step.get('query', '')
                                    ack_message = f"Sarah is searching for '{query}'..."
                                elif action_type == 'click_element' or action_type == 'click_by_description':
                                    description = first_step.get('description', first_step.get('target', 'element'))
                                    ack_message = f"Sarah is clicking '{description}'..."
                                else:
                                    ack_message = f"Sarah is {plan.goal}..."
                            else:
                                ack_message = f"Sarah is working on it..."

                            await self.send_message(websocket, {
                                'type': 'sarah_thinking',
                                'message': ack_message
                            })
                            logger.info(f"💭 Sarah acknowledged: {ack_message}")

                            logger.info(f"🧠 Executing planned actions for: {plan.goal}")
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

            # Extract response text with bounds checking
            if not response.content or len(response.content) == 0:
                logger.error("Claude returned empty response content")
                await self.send_message(websocket, {
                    'type': 'error',
                    'message': "Sorry, I didn't get a response. Can you try again?"
                })
                return

            sarah_response = response.content[0].text

            action_success = False

            # DISABLED: Legacy browser command parsing - replaced by vision-guided action planning
            # The new planning system handles actions BEFORE Sarah responds, not after
            # Parsing her responses caused bugs like navigating to "https://successful"
            if False and self.browser and self.browser.is_running:
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
                    if response.content and len(response.content) > 0:
                        return response.content[0].text
                    else:
                        logger.error("Retry succeeded but returned empty content")
                        return "Sorry, I'm having trouble responding. Can you try again? 😅"

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
        # Parse user intent using LLM (Claude understands intent better than regex!)
        user_intent = await self.action_reasoner.parse_user_intent_with_llm(user_message)

        logger.info(f"🧠 User intent: {user_intent.get('type')} (confidence: {user_intent.get('confidence', 0):.2f})")

        # Check if this requires action
        if not self.action_reasoner.should_take_action(user_intent):
            logger.info("💭 No action required - user acknowledgment or question")
            return None

        # Get current page context for vision analysis
        current_url = self.browser.page.url if self.browser and self.browser.page else "unknown"

        # Build rich page context using page title, visible elements, etc.
        page_context = f"URL: {current_url}"

        # Check if page is available before accessing it
        if not self.browser or not self.browser.page:
            logger.warning("⚠️ Browser page not available for context gathering")
            # Plan actions with minimal context
            action_plan = self.action_reasoner.plan_actions(
                user_intent=user_intent,
                page_state={'state': 'unknown', 'url': current_url},
                current_url=current_url
            )
            return action_plan

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

        logger.info(f"📋 Action plan: {action_plan.reasoning}")
        logger.info(f"   Steps: {len(action_plan.steps)}")

        return {
            'intent': user_intent,
            'analysis': page_analysis,
            'plan': action_plan
        }

    async def _execute_action_plan(self, action_plan: dict) -> Optional[bool]:
        """
        Execute a planned action from the vision-guided reasoning system

        Args:
            action_plan: Plan created by _parse_user_intent_and_plan

        Returns:
            True if action succeeded, False if failed, None if no action
        """
        plan = action_plan['plan']

        if not plan.steps:
            logger.info("✅ No actions to execute")
            return None

        logger.info(f"🚀 Executing {len(plan.steps)} planned action(s)")

        overall_success = True

        for i, step in enumerate(plan.steps):
            action_type = step.get('action')
            logger.info(f"   Step {i+1}/{len(plan.steps)}: {action_type}")

            try:
                if action_type == 'navigate':
                    target = step.get('target')
                    self.action_steps.append(f"Navigate to {target}")
                    result = await self.browser.navigate(target)
                    success = result.get('success', False) if isinstance(result, dict) else False

                    if success:
                        self.action_steps.append(f"✅ Successfully navigated to {target}")
                        # Wait briefly for dynamic content to load (cookie dialogs, etc.)
                        await asyncio.sleep(1)
                    else:
                        overall_success = False
                        self.action_steps.append(f"❌ Navigation failed")

                elif action_type == 'search':
                    query = step.get('query')
                    self.action_steps.append(f"Search for '{query}'")
                    result = await self.browser.search_google(query)
                    success = result.get('success', False) if isinstance(result, dict) else False

                    if success:
                        self.action_steps.append(f"✅ Successfully searched for '{query}'")
                        # Wait briefly for search results to fully load
                        await asyncio.sleep(1)
                    else:
                        overall_success = False
                        self.action_steps.append(f"❌ Search failed")

                elif action_type == 'dismiss_popup':
                    method = step.get('method', 'accessibility_first')
                    self.action_steps.append("Dismiss popup/cookie dialog")

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

                    # Clean up the description - extract just the clickable text
                    # Remove phrases like "on X", "in the search results", etc.
                    clean_desc = description

                    # Pattern 1: "on X in the search results" → "X"
                    match = re.search(r'on\s+(.+?)\s+in\s+the\s+search\s+results', clean_desc, re.IGNORECASE)
                    if match:
                        clean_desc = match.group(1)

                    # Pattern 2: "click on X" → "X"
                    match = re.search(r'(?:click\s+on\s+|click\s+)(.+)', clean_desc, re.IGNORECASE)
                    if match:
                        clean_desc = match.group(1)

                    # Pattern 3: Remove "in the X", "on the X" suffixes
                    clean_desc = re.sub(r'\s+(?:in|on)\s+the\s+.+$', '', clean_desc, flags=re.IGNORECASE)

                    # Pattern 4: Remove quotes if present
                    clean_desc = clean_desc.strip('\'"')

                    logger.info(f"🎯 Original: '{description}' → Cleaned: '{clean_desc}'")
                    self.action_steps.append(f"Click: {clean_desc}")

                    # Use Sarah's improved clicking system!
                    result = await self.browser.smart_click(clean_desc)
                    success = result.get('success', False) if isinstance(result, dict) else False

                    if success:
                        self.action_steps.append(f"✅ Clicked '{clean_desc}'")
                    else:
                        overall_success = False
                        self.action_steps.append(f"❌ Click failed for '{clean_desc}'")

                elif action_type == 'input':
                    # Type text into current focused element
                    text = step.get('text', '')
                    if text:
                        self.action_steps.append(f"Type: {text}")
                        await self.browser.page.keyboard.type(text)
                        self.action_steps.append(f"✅ Typed '{text}'")
                    else:
                        logger.warning("⚠️ Input action with no text specified")
                        overall_success = False

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

        return overall_success

    async def _execute_browser_commands(self, response_text: str) -> Optional[bool]:
        """
        LEGACY: Detect and execute browser commands from Sarah's response

        This is kept for backward compatibility but should eventually be
        fully replaced by vision-guided reasoning system.

        Args:
            response_text: Sarah's response text

        Returns:
            True if action succeeded, False if failed, None if no action
        """
        text_lower = response_text.lower()

        # Detect click intent (EXPANDED for CAPTCHA, buttons, etc!)
        if any(word in text_lower for word in ['clicking', 'click on', 'click the', 'clicking on', 'clicking the', 'i\'ll click']):
            # PRIORITY 1: Cookie/consent dialogs - try ACCESSIBILITY first (most human-like!)
            # Only trigger if it's actually about clicking accept/ok buttons, not just saying "ok" casually
            if any(phrase in text_lower for phrase in [
                'click accept', 'click ok', 'click the ok', 'click the accept',
                'accept all', 'accept cookies', 'alles accepteren', 'cookie', 'consent'
            ]):
                logger.info("♿ Cookie/consent click detected - using ACCESSIBILITY MODE first!")

                # Track steps for learning
                self.action_steps.append("Attempt to click accept/ok button (accessibility mode)")

                # TRY 1: ACCESSIBILITY click (ARIA labels + keyboard navigation)
                # This mimics screen readers and assistive tech - REQUIRED to work by law!
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

            # PRIORITY 2: CAPTCHA checkboxes - use advanced click with description
            elif any(word in text_lower for word in ['robot', 'captcha', 'checkbox', 'verify', 'human']):
                logger.info("🤖 CAPTCHA/checkbox click detected - using advanced click!")

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

                logger.info(f"🎯 Attempting to click: {click_description}")
                self.action_steps.append(f"Click '{click_description}'")

                # Use advanced browser control for precise clicking
                # Use Sarah's improved clicking system!
                result = await self.browser.smart_click(click_description)
                success = result.get('success', False) if isinstance(result, dict) else False

                if success:
                    self.action_steps.append(f"Successfully clicked '{click_description}'")
                else:
                    self.action_steps.append(f"Click failed for '{click_description}'")

                return success

            # PRIORITY 3: Generic button clicks - use advanced click
            elif 'button' in text_lower:
                logger.info("🔘 Generic button click detected - using advanced click!")

                # Try to extract button description
                click_description = "button"
                quote_match = re.search(r"['\"]([^'\"]+)['\"]", response_text)
                if quote_match:
                    click_description = quote_match.group(1)

                logger.info(f"🎯 Attempting to click button: {click_description}")
                self.action_steps.append(f"Click button: '{click_description}'")

                # Use Sarah's improved clicking system!
                result = await self.browser.smart_click(click_description)
                success = result.get('success', False) if isinstance(result, dict) else False

                if success:
                    self.action_steps.append(f"Successfully clicked button '{click_description}'")
                else:
                    self.action_steps.append(f"Click failed for button '{click_description}'")

                return success

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

                # Track steps for learning
                self.action_steps.append(f"Navigate to {url}")

                # Execute navigation and track success
                result = await self.browser.navigate(url)
                success = result.get('success', False) if isinstance(result, dict) else False

                if success:
                    self.action_steps.append(f"Successfully loaded {url}")

                return success

        # Detect search intent (with AND without quotes!)
        search_patterns = [
            # WITH quotes (higher priority)
            r"(?:let me |i'll |i will )?search(?:ing)?(?: for | on google for)?\s+['\"](.+?)['\"]",
            r"(?:let me |i'll |i will )?(?:google|look up|search for)\s+['\"](.+?)['\"]",
            r"searching\s+for\s+['\"](.+?)['\"]",
            # WITHOUT quotes (more flexible)
            r"(?:let me |i'll |i will )?search(?:ing)?(?: for | on google for | in google for)?\s+(.+?)(?:\.|!|\?|$)",
            r"(?:let me |i'll |i will )?(?:google|look up|search for)\s+(.+?)(?:\.|!|\?|$)",
            r"searching\s+for\s+(.+?)(?:\.|!|\?|$)"
        ]

        for pattern in search_patterns:
            match = re.search(pattern, text_lower)
            if match:
                query = match.group(1).strip()

                # Clean up the query - remove trailing punctuation and common words
                query = re.sub(r'\s+(now|right now|please|for me|for us)$', '', query)
                query = query.strip(' .,!?')

                logger.info(f"🔍 Detected search intent: {query}")

                # Track steps for learning
                self.action_steps.append(f"Search Google for '{query}'")

                # Execute search and track success
                result = await self.browser.search_google(query)
                success = result.get('success', False) if isinstance(result, dict) else False

                if success:
                    self.action_steps.append(f"Successfully searched for '{query}'")

                return success

        # No action detected
        return None

    async def send_message(self, websocket: WebSocketServerProtocol, data: dict):
        """Send message to client (supports both websockets and Starlette WebSocket)"""
        try:
            # Starlette WebSocket (from combined_server.py)
            if hasattr(websocket, 'send_json'):
                await websocket.send_json(data)
            # Legacy websockets library
            else:
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
