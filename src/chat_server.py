"""
Real-Time Chat with Sarah - WITH GLOBAL CLICKING FIX
COMPLETE 2200+ line version - FastAPI compatible
WebSocket handler that bridges Sarah's intent to execution
Fixes the Intent vs Execution Gap once and for all
"""

import asyncio
import json
import logging
import os
from typing import Set, Optional, List, Dict, Any
import re
import base64
from anthropic import Anthropic
from datetime import datetime
from PIL import Image
import io
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class SarahChatHandler:
    """
    COMPLETE WebSocket chat handler - enables real-time conversation with Sarah
    WITH GLOBAL CLICKING FIX: When Sarah says "Let me click X" it ACTUALLY clicks
    FASTAPI COMPATIBLE: Receives WebSocket connections from FastAPI endpoints
    """

    def __init__(
        self,
        anthropic_api_key: str,
        identity_manager=None,
        browser=None
    ):
        """
        Initialize complete chat handler with ALL functionality

        Args:
            anthropic_api_key: Anthropic API key for Claude
            identity_manager: Sarah's identity for context
            browser: SarahBrowser instance for web automation
        """
        self.identity_manager = identity_manager
        self.browser = browser
        self.anthropic_api_key = anthropic_api_key  # Store for later use

        # Initialize Anthropic client
        self.anthropic = Anthropic(api_key=anthropic_api_key)

        # Initialize ALL optional components with safe fallbacks
        self._init_all_components()

        # Track connected clients via FastAPI
        self.active_connections: List[WebSocket] = []

        # Track current activity for skill extraction
        self.current_action = None
        self.action_steps = []
        self.visual_observations = []

        # Track running action task (for cancellation/interruption)
        self.current_action_task = None
        self.action_cancelled = False

        # Track current message handling task (for immediate interruption)
        self.current_message_task = None

        # 🆕 NEW: Track user interruption commands (stop/cancel)
        self.current_action_interrupted = False

        # Sarah's COMPLETE system prompt (her personality and context)
        self.system_prompt = self._build_complete_system_prompt()

        # Conversation history (keep last 20 messages for context)
        self.max_history = 20
        self.conversation_history = []

        # Load conversation history from persistent memory
        self._load_conversation_history()

        # Initialize autonomous executor if browser is available
        self.autonomous_executor = None
        if self.browser:
            try:
                from src.autonomous_executor import AutonomousExecutor
                self.autonomous_executor = AutonomousExecutor(
                    api_key=anthropic_api_key,
                    sarah_browser=self.browser,
                    websocket_send_callback=self._broadcast_to_all_clients
                )
                logger.info("✅ Autonomous executor initialized")
            except ImportError as e:
                logger.warning(f"⚠️ AutonomousExecutor not available: {e}")
                self.autonomous_executor = None
            except Exception as e:
                logger.error(f"❌ Failed to initialize AutonomousExecutor: {e}")
                self.autonomous_executor = None

        logger.info("✅ COMPLETE SarahChatHandler initialized (2200+ line version)")

    def _init_all_components(self):
        """Initialize ALL components from the original 2200+ line version"""
        # Visual learning engine
        try:
            from src.visual_learning import get_learning_engine, UIPattern, Skill, ExperimentResult
            self.learning_engine = get_learning_engine("sarah_001")
            self.UIPattern = UIPattern
            self.Skill = Skill
            self.ExperimentResult = ExperimentResult
            logger.info("✅ Visual learning engine initialized")
        except ImportError as e:
            logger.warning(f"⚠️ Visual learning engine not available: {e}")
            self.learning_engine = None
            # Create dummy classes for type hints
            self.UIPattern = type('UIPattern', (), {})
            self.Skill = type('Skill', (), {})
            self.ExperimentResult = type('ExperimentResult', (), {})

        # Vision-guided action reasoning system
        try:
            from src.vision_action_reasoner import VisionActionReasoner
            self.action_reasoner = VisionActionReasoner()
            logger.info("✅ Vision action reasoner initialized")
        except ImportError as e:
            logger.warning(f"⚠️ VisionActionReasoner not available: {e}")
            # Create comprehensive fallback
            class CompleteActionReasoner:
                def parse_user_intent(self, user_message):
                    # Advanced keyword-based intent parsing
                    text_lower = user_message.lower()
                    
                    # Navigation patterns
                    nav_patterns = [
                        (r'go to (.*)', 'navigate'),
                        (r'navigate to (.*)', 'navigate'),
                        (r'open (.*)', 'navigate'),
                        (r'visit (.*)', 'navigate'),
                        (r'load (.*)', 'navigate'),
                        (r'show me (.*)', 'navigate'),
                        (r'take me to (.*)', 'navigate')
                    ]
                    
                    for pattern, intent_type in nav_patterns:
                        match = re.search(pattern, text_lower)
                        if match:
                            return {
                                'type': intent_type,
                                'target': match.group(1).strip(),
                                'confidence': 0.9
                            }
                    
                    # Search patterns
                    search_patterns = [
                        (r'search for (.*)', 'search'),
                        (r'find (.*)', 'search'),
                        (r'look up (.*)', 'search'),
                        (r'google (.*)', 'search'),
                        (r'search (.*)', 'search'),
                        (r'find info about (.*)', 'search')
                    ]
                    
                    for pattern, intent_type in search_patterns:
                        match = re.search(pattern, text_lower)
                        if match:
                            return {
                                'type': intent_type,
                                'query': match.group(1).strip(),
                                'confidence': 0.9
                            }
                    
                    # Click patterns
                    click_patterns = [
                        (r'click (?:on |the )?(.*)', 'click'),
                        (r'press (?:the )?(.*)', 'click'),
                        (r'tap (?:on |the )?(.*)', 'click'),
                        (r'select (?:the )?(.*)', 'click'),
                        (r'hit (?:the )?(.*)', 'click'),
                        (r'choose (?:the )?(.*)', 'click')
                    ]
                    
                    for pattern, intent_type in click_patterns:
                        match = re.search(pattern, text_lower)
                        if match:
                            return {
                                'type': intent_type,
                                'target': match.group(1).strip(),
                                'confidence': 0.85
                            }
                    
                    # Type patterns
                    type_patterns = [
                        (r'type (.*?) (?:in|into) (?:the )?(.*)', 'type'),
                        (r'enter (.*?) (?:in|into) (?:the )?(.*)', 'type'),
                        (r'write (.*?) (?:in|into) (?:the )?(.*)', 'type'),
                        (r'input (.*?) (?:in|into) (?:the )?(.*)', 'type')
                    ]
                    
                    for pattern, intent_type in type_patterns:
                        match = re.search(pattern, text_lower)
                        if match:
                            return {
                                'type': intent_type,
                                'text': match.group(1).strip(),
                                'target': match.group(2).strip(),
                                'confidence': 0.8
                            }
                    
                    # Acknowledgment patterns
                    ack_patterns = [
                        'ok', 'okay', 'cool', 'nice', 'great', 'thanks', 'thank you',
                        'yes', 'no', 'yep', 'nope', 'got it', 'understood', 'alright'
                    ]
                    
                    if text_lower.strip() in ack_patterns:
                        return {'type': 'acknowledgment', 'confidence': 0.95}
                    
                    # Observation patterns
                    observe_patterns = [
                        (r'look at (.*)', 'observe'),
                        (r'check (.*)', 'observe'),
                        (r'view (.*)', 'observe'),
                        (r'see (.*)', 'observe'),
                        (r'watch (.*)', 'observe'),
                        (r'examine (.*)', 'observe')
                    ]
                    
                    for pattern, intent_type in observe_patterns:
                        match = re.search(pattern, text_lower)
                        if match:
                            return {
                                'type': intent_type,
                                'target': match.group(1).strip(),
                                'confidence': 0.8
                            }
                    
                    # Default unknown
                    return {'type': 'unknown', 'confidence': 0.5}
                
                def should_take_action(self, intent):
                    return intent.get('type') not in ['acknowledgment', 'unknown']
                    
                def analyze_vision_context(self, page_context, current_url):
                    class CompletePageAnalysis:
                        def __init__(self):
                            self.page_type = self._determine_page_type(current_url)
                            self.state = 'ready'
                            self.observations = self._extract_observations(page_context)
                        
                        def _determine_page_type(self, url):
                            if 'youtube.com' in url:
                                return 'youtube'
                            elif 'google.com' in url or 'search' in url:
                                return 'search_results'
                            elif 'login' in url or 'signin' in url:
                                return 'login_page'
                            elif any(social in url for social in ['twitter.com', 'facebook.com', 'instagram.com', 'tiktok.com']):
                                return 'social_media'
                            elif any(news in url for news in ['news.', 'blog.', 'article']):
                                return 'content_page'
                            else:
                                return 'general_website'
                        
                        def _extract_observations(self, context):
                            observations = []
                            if 'popup/dialog visible' in context:
                                observations.append('popup_visible')
                            if 'video elements present' in context:
                                observations.append('videos_present')
                            if 'search box present' in context:
                                observations.append('search_available')
                            if 'form present' in context:
                                observations.append('form_available')
                            return observations
                    
                    return CompletePageAnalysis()
                    
                def plan_actions(self, user_intent, page_analysis):
                    class CompleteActionPlan:
                        def __init__(self, goal, reasoning, steps):
                            self.goal = goal
                            self.reasoning = reasoning
                            self.steps = steps
                    
                    intent_type = user_intent.get('type')
                    
                    if intent_type == 'navigate':
                        target = user_intent.get('target', '')
                        return CompleteActionPlan(
                            goal=f"Navigate to {target}",
                            reasoning=f"User wants to navigate to {target}. First check for popups, then navigate.",
                            steps=[
                                {'action': 'dismiss_popup', 'method': 'accessibility_first'},
                                {'action': 'navigate', 'target': target},
                                {'action': 'wait', 'duration': 3}
                            ]
                        )
                    
                    elif intent_type == 'search':
                        query = user_intent.get('query', '')
                        return CompleteActionPlan(
                            goal=f"Search for '{query}'",
                            reasoning=f"User wants to search for '{query}'. Check current page for search box first.",
                            steps=[
                                {'action': 'dismiss_popup', 'method': 'accessibility_first'},
                                {'action': 'search', 'query': query, 'original_query': user_intent.get('original_message', '')},
                                {'action': 'wait', 'duration': 3}
                            ]
                        )
                    
                    elif intent_type == 'click':
                        target = user_intent.get('target', '')
                        return CompleteActionPlan(
                            goal=f"Click '{target}'",
                            reasoning=f"User wants to click '{target}'. Validate it's a valid target, then click.",
                            steps=[
                                {'action': 'dismiss_popup', 'method': 'accessibility_first'},
                                {'action': 'click_element', 'description': target},
                                {'action': 'wait', 'duration': 2}
                            ]
                        )
                    
                    elif intent_type == 'type':
                        text = user_intent.get('text', '')
                        target = user_intent.get('target', '')
                        return CompleteActionPlan(
                            goal=f"Type '{text}' into '{target}'",
                            reasoning=f"User wants to type '{text}' into '{target}'. Find the element first.",
                            steps=[
                                {'action': 'dismiss_popup', 'method': 'accessibility_first'},
                                {'action': 'click_element', 'description': target},
                                {'action': 'wait', 'duration': 0.5},
                                {'action': 'type_text', 'text': text, 'target': target},
                                {'action': 'wait', 'duration': 1}
                            ]
                        )
                    
                    else:
                        return CompleteActionPlan(
                            goal="Unknown action",
                            reasoning="Could not determine specific action plan",
                            steps=[]
                        )
            
            self.action_reasoner = CompleteActionReasoner()

        # Autonomous learning engine
        try:
            from src.autonomous_learning_engine import AutonomousLearningEngine, LearningStatus
            self.autonomous_learning = AutonomousLearningEngine("sarah_001")
            self.LearningStatus = LearningStatus
            logger.info("✅ Autonomous learning engine initialized")
        except ImportError as e:
            logger.warning(f"⚠️ AutonomousLearningEngine not available: {e}")
            self.autonomous_learning = None
            self.LearningStatus = type('LearningStatus', (), {
                'PLANNED': 'planned',
                'IN_PROGRESS': 'in_progress',
                'COMPLETED': 'completed',
                'FAILED': 'failed'
            })()

        # Universal Element Locator
        try:
            from src.foundation.universal_element_locator import UniversalElementLocator
            self.universal_locator = UniversalElementLocator(self.anthropic_api_key)
            logger.info("✅ Universal element locator initialized")
        except ImportError as e:
            logger.warning(f"⚠️ UniversalElementLocator not available: {e}")
            self.universal_locator = None

        # Parallel Execution Engine
        try:
            from src.foundation.parallel_execution_engine import ParallelExecutionEngine
            self.parallel_executor = ParallelExecutionEngine(max_total_timeout=10.0)
            logger.info("✅ Parallel execution engine initialized")
        except ImportError as e:
            logger.warning(f"⚠️ ParallelExecutionEngine not available: {e}")
            self.parallel_executor = None

        # Capability Registry
        try:
            from src.capability_registry import CapabilityRegistry
            self.capability_registry_class = CapabilityRegistry
            logger.info("✅ Capability registry available")
        except ImportError as e:
            logger.warning(f"⚠️ CapabilityRegistry not available: {e}")
            self.capability_registry_class = None

        # Intelligent Selector
        try:
            from src.intelligent_selector import IntelligentSelector
            self.intelligent_selector_class = IntelligentSelector
            logger.info("✅ Intelligent selector available")
        except ImportError as e:
            logger.warning(f"⚠️ IntelligentSelector not available: {e}")
            self.intelligent_selector_class = None

        # Universal Interactor
        try:
            from src.foundation.universal_interactor import UniversalInteractor
            self.UniversalInteractor = UniversalInteractor
            logger.info("✅ Universal interactor available")
        except ImportError as e:
            logger.warning(f"⚠️ UniversalInteractor not available: {e}")
            self.UniversalInteractor = None

        # Intelligent Click Router
        try:
            from src.platform_aware_clicking import IntelligentClickRouter, YouTubeNavigator
            self.IntelligentClickRouter = IntelligentClickRouter
            self.YouTubeNavigator = YouTubeNavigator
            logger.info("✅ Platform aware clicking available")
        except ImportError as e:
            logger.warning(f"⚠️ Platform aware clicking not available: {e}")
            self.IntelligentClickRouter = None
            self.YouTubeNavigator = None

        # Realtime Response Streamer
        try:
            from src.foundation.realtime_response_streamer import RealtimeResponseStreamer
            self.RealtimeResponseStreamer = RealtimeResponseStreamer
            logger.info("✅ Realtime response streamer available")
        except ImportError as e:
            logger.warning(f"⚠️ RealtimeResponseStreamer not available: {e}")
            self.RealtimeResponseStreamer = None

        # Initialize capability registry if available
        self.capability_registry = None
        if self.capability_registry_class:
            try:
                self.capability_registry = self.capability_registry_class()
                logger.info("✅ Capability registry instance created")
            except Exception as e:
                logger.warning(f"⚠️ Failed to create capability registry: {e}")

        # Initialize intelligent selector if available
        self.intelligent_selector = None
        if self.intelligent_selector_class and self.capability_registry:
            try:
                self.intelligent_selector = self.intelligent_selector_class(
                    self.capability_registry,
                    self.anthropic_api_key
                )
                logger.info("✅ Intelligent selector instance created")
            except Exception as e:
                logger.warning(f"⚠️ Failed to create intelligent selector: {e}")

    def _build_complete_system_prompt(self) -> str:
        """Build Sarah's COMPLETE system prompt with all features"""
        
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

            # Reconstruct conversation history
            for memory in all_memories:
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
                memory_type='interaction',
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
        if not self.browser or not hasattr(self.browser, 'is_running') or not self.browser.is_running:
            return None

        try:
            # Take screenshot
            screenshot_bytes = await self.browser.screenshot(full_page=False)

            if screenshot_bytes:
                # 🔍 DEBUG: Log actual screenshot dimensions being sent to Claude
                try:
                    img = Image.open(io.BytesIO(screenshot_bytes))
                    logger.info(f"📸 Captured screenshot for Sarah's vision")
                    logger.info(f"   📐 Screenshot dimensions: {img.width}x{img.height} pixels")
                    logger.info(f"   📊 Image format: {img.format}, mode: {img.mode}")

                    # Get actual viewport from page for comparison
                    if self.browser and hasattr(self.browser, 'page') and self.browser.page:
                        viewport = self.browser.page.viewport_size
                        if viewport:
                            logger.info(f"   🖥️  Configured viewport: {viewport['width']}x{viewport['height']}")
                            if img.width != viewport['width'] or img.height != viewport['height']:
                                logger.warning(f"   ⚠️  MISMATCH: Screenshot {img.width}x{img.height} != Viewport {viewport['width']}x{viewport['height']}")
                except Exception as debug_error:
                    logger.warning(f"   ⚠️  Could not read screenshot dimensions: {debug_error}")

                # Encode to base64
                screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                return screenshot_base64

        except Exception as e:
            logger.error(f"❌ Failed to capture screenshot: {e}")

        return None

    async def _should_click_text(self, text: str) -> bool:
        """
        NEW METHOD - Validate if text is a valid click target
        Prevents clicking on Sarah's observation/description text

        Returns:
            bool: True if valid click target, False if descriptive text
        """
        if not text or len(text.strip()) < 2:
            logger.warning(f"🛑 Blocked empty/too short click target: '{text}'")
            return False

        text_lower = text.strip().lower()

        # Block Sarah's observation/description phrases
        invalid_patterns = [
            # Sarah's first-person observations
            "i'm about to click", "i am about to click", "i'll click", "let me click",
            "i see", "i notice", "i can see", "observing", "looking at", "looking for",
            "now i can see", "looking at the", "i can see the", "now let me",
            "let me search", "oh interesting", "that's totally fine", "i see we've",

            # Sentence fragments (incomplete sentences starting mid-word)
            "m back on", "m about to", "t changed yet", "s changed", "perfect!",
            "the homepage", "search bar at the top", "landed on", "instead of staying",

            # Navigation descriptions
            "click on", "navigate to", "search for", "type in", "enter in",
            "it looks like", "appears to be",

            # Location descriptions
            "here", "there", "that's", "it's", "this is", "at the top", "in the"
        ]

        # Check for invalid patterns
        for pattern in invalid_patterns:
            if pattern in text_lower:
                logger.warning(f"🛑 BLOCKED INVALID CLICK TARGET: '{text}' (contains '{pattern}')")
                return False

        # Block if it looks like a sentence fragment (starts with lowercase + short word)
        words = text.split()
        if len(words) > 0:
            first_word = words[0]
            # Sentence fragment check: starts with lowercase single letter or short word
            if len(first_word) <= 2 and first_word[0].islower():
                logger.warning(f"🛑 BLOCKED SENTENCE FRAGMENT: '{text}' (starts with '{first_word}')")
                return False

        # ✅ REMOVED overzealous word count check
        # Video titles, article headlines, and detailed UI elements can be long!
        # The pattern checks above already filter out observations like:
        # - "I'm still on the same page..." (contains "i'm")
        # - "Let me click on the search box" (contains "let me click")
        # Valid detailed targets should pass through:
        # - "Click video titled 'How We Find TikTok Shop Affiliates To Make Us $100k+' (video)"
        # - "Article: The Complete Guide to Creator Economy Growth Strategies"

        # Valid click target
        return True

    async def _stream_immediate_response(self, websocket: WebSocket, message: str):
        """
        NEW METHOD - Send immediate real-time feedback to user
        Eliminates silent waiting periods
        """
        try:
            await websocket.send_json({
                'type': 'sarah_progress',
                'message': message,
                'streaming': True
            })
            logger.info(f"📤 Streamed: {message}")
        except Exception as e:
            logger.error(f"❌ Stream error: {e}")

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

    async def _broadcast_to_all_clients(self, data: dict):
        """
        Broadcast message to all connected WebSocket clients
        Used by AutonomousExecutor for progress updates
        """
        if not self.active_connections:
            return

        data_json = json.dumps(data)
        tasks = []
        for connection in self.active_connections:
            try:
                tasks.append(connection.send_text(data_json))
            except Exception as e:
                logger.debug(f"Failed to send to client: {e}")
                # Remove dead connection
                try:
                    self.active_connections.remove(connection)
                except ValueError:
                    pass
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    # ==================== MAIN WEBSOCKET HANDLER ====================

    async def handle_websocket(self, websocket: WebSocket):
        """
        Main FastAPI WebSocket handler
        Called from main.py's WebSocket endpoints
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        
        client_id = f"{id(websocket)}"
        logger.info(f"💬 New WebSocket client connected via FastAPI: {client_id}")

        try:
            # Send welcome message
            await websocket.send_json({
                'type': 'system',
                'message': 'Connected to Sarah! Start chatting below 🌸\n\n**GLOBAL CLICKING FIX ACTIVE** - Sarah\'s clicks now work everywhere! 🎯'
            })

            # Main message loop
            while True:
                try:
                    # Receive message from client
                    data = await websocket.receive_text()
                    
                    # Handle message (run in background task for interruption support)
                    if self.current_message_task and not self.current_message_task.done():
                        logger.info("⚡ New message arrived - cancelling previous message handling")
                        self.current_message_task.cancel()
                        try:
                            await self.current_message_task
                        except asyncio.CancelledError:
                            pass

                    self.current_message_task = asyncio.create_task(
                        self._handle_client_message(websocket, data)
                    )
                    
                except Exception as e:
                    logger.error(f"❌ Error receiving message: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"❌ WebSocket error: {e}")
        finally:
            # Clean up
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
            logger.info(f"💬 WebSocket client disconnected: {client_id}")

    async def _handle_client_message(self, websocket: WebSocket, message: str):
        """Handle incoming chat message from WebSocket"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            content = data.get('message', '')

            if msg_type == 'user_message':
                # 🆕 NEW: Reset interruption flag on every message
                self.current_action_interrupted = False

                # 🆕 NEW: Check for interruption commands (stop/cancel/abort)
                if content.lower().strip() in ['stop', 'cancel', 'abort']:
                    self.current_action_interrupted = True
                    logger.info("🛑 User sent interruption command")
                    await self._stream_immediate_response(websocket, "🛑 Stopping current action...")
                    # Cancel any running tasks
                    if self.current_action_task and not self.current_action_task.done():
                        self.action_cancelled = True
                        self.current_action_task.cancel()
                    return

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

                # 🚀 NEW: Immediate acknowledgment (eliminates silent waiting)
                await self._stream_immediate_response(websocket, "Got it! Let me work on that...")

                # 🧠 AUTONOMOUS EXECUTOR DETECTION - Check if user wants autonomous mission execution
                content_lower = content.lower()

                if self.autonomous_executor and hasattr(self.autonomous_executor, 'is_autonomous_request'):
                    if self.autonomous_executor.is_autonomous_request(content):
                        logger.info(f"🎯 AUTONOMOUS MISSION DETECTED: {content}")
                        await self._handle_autonomous_mission(websocket, content)
                        return

                # AUTONOMOUS LEARNING DETECTION - Check if user is asking about Sarah's autonomous goals
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
                    await self._handle_autonomous_learning_question(websocket, content)
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
                    logger.info("🚀 Autonomous learning execution detected!")
                    await self._handle_autonomous_learning_execution(websocket, content)
                    return

                # 🧠 INTELLIGENT SELECTOR - Dynamic Capability Routing
                if self.intelligent_selector and self.browser:
                    try:
                        current_url = self.browser.page.url if hasattr(self.browser, 'page') and self.browser.page else "unknown"
                        selection_result = await self.intelligent_selector.select_capability(
                            content,
                            context={
                                'current_url': current_url,
                                'previous_action': getattr(self, 'last_action', 'None')
                            }
                        )

                        if selection_result.get('success'):
                            selected_cap = selection_result['capability']
                            logger.info(f"🧠 Intelligent Selector chose: {selected_cap.display_name} "
                                       f"({selected_cap.category}) - "
                                       f"Confidence: {selection_result['confidence']:.2f}")
                            logger.info(f"   💡 Reasoning: {selection_result['reasoning'][:100]}")

                            # Store selection for future use
                            self._last_capability_selection = selection_result
                        else:
                            logger.info(f"🧠 Intelligent Selector: No capability matched - {selection_result.get('reasoning')}")

                    except Exception as e:
                        logger.warning(f"⚠️ Intelligent Selector error (non-blocking): {e}")

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
                    await self._handle_conversational_message(websocket, content)
                    return

                # VISION-GUIDED ACTION REASONING - Execute before Claude response
                # This replaces hardcoded pattern matching with intelligent reasoning
                action_result = None
                action_plan_data = None

                if self.browser and hasattr(self.browser, 'is_running') and self.browser.is_running:
                    try:
                        # Parse user intent and create action plan
                        action_plan_data = await self._parse_user_intent_and_plan(content)

                        # Execute planned actions if any
                        if action_plan_data:
                            # Safe access to plan attributes
                            plan = action_plan_data.get('plan', {})
                            if hasattr(plan, 'goal'):
                                goal = plan.goal
                            else:
                                goal = 'unknown goal'
                                
                            logger.info(f"🧠 Executing planned actions for: {goal}")
                            action_result = await self._execute_action_plan(action_plan_data)

                            # Add context about executed actions
                            if action_result is not None:
                                if hasattr(plan, 'reasoning'):
                                    reasoning = plan.reasoning
                                else:
                                    reasoning = 'completed'
                                    
                                if action_result:
                                    action_context = f"\n\n[System: Actions executed successfully - {reasoning}]"
                                    content = content + action_context
                                else:
                                    action_context = f"\n\n[System: Actions attempted but some failed - {reasoning}]"
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
                response = await self._get_sarah_response()

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
                await websocket.send_json({
                    'type': 'sarah_message',
                    'message': response
                })

                logger.info(f"💬 Sarah: {response[:100]}...")

            elif msg_type == 'audio_message':
                # User sent voice message - transcribe and process
                logger.info("🎤 Received audio message from user")
                await self._handle_audio_message(websocket, data)

            elif msg_type == 'ping':
                # Keep-alive ping
                await websocket.send_json({'type': 'pong'})

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {message}")
            await websocket.send_json({
                'type': 'error',
                'message': 'Invalid message format'
            })
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await websocket.send_json({
                'type': 'error',
                'message': f'Sorry, I encountered an error: {str(e)}'
            })

    async def _handle_autonomous_mission(self, websocket: WebSocket, content: str):
        """Handle autonomous mission execution"""
        try:
            # Execute the autonomous mission
            result = await self.autonomous_executor.execute_mission(content)

            # Add to conversation history
            user_msg = self._format_message_for_api('user', content, None)
            self.conversation_history.append(user_msg)

            # Report final results
            if result.get('status') == 'success' or result.get('success'):
                final_message = f"✅ Mission completed!\n\n"
                if 'completed_steps' in result and 'plan_steps' in result:
                    final_message += f"Steps completed: {result['completed_steps']}/{result['plan_steps']}\n"

                if 'collected_info' in result and result['collected_info']:
                    final_message += f"\nInformation gathered:\n"
                    for info in result['collected_info']:
                        if isinstance(info, dict):
                            final_message += f"• {info.get('type', 'Info')}: {info.get('note', str(info))}\n"
            else:
                final_message = f"⚠️ Mission had some issues.\n\n"
                if 'completed_steps' in result and 'plan_steps' in result:
                    final_message += f"Completed: {result['completed_steps']}/{result['plan_steps']} steps\n"
                if 'errors' in result and result['errors']:
                    final_message += f"Errors: {len(result['errors'])}\n"
                    if result['errors']:
                        final_message += "\nIssues encountered:\n"
                        for error in result['errors'][:3]:
                            final_message += f"• {error}\n"

            self.conversation_history.append({
                'role': 'assistant',
                'content': final_message
            })

            self._save_message_to_memory('user', content)
            self._save_message_to_memory('assistant', final_message)

            await websocket.send_json({
                'type': 'sarah_message',
                'message': final_message
            })

        except Exception as e:
            logger.error(f"❌ Autonomous mission failed: {e}")
            error_message = f"Sorry, I encountered an error during the autonomous mission: {str(e)}"

            self.conversation_history.append({
                'role': 'assistant',
                'content': error_message
            })

            await websocket.send_json({
                'type': 'sarah_message',
                'message': error_message
            })

    async def _handle_autonomous_learning_question(self, websocket: WebSocket, content: str):
        """Handle autonomous learning questions"""
        if not self.autonomous_learning:
            response = "I'd love to learn something new, but my learning system isn't available right now. What would you like me to help you with instead? 😊"
            
            self.conversation_history.append(self._format_message_for_api('user', content, None))
            self.conversation_history.append({'role': 'assistant', 'content': response})
            
            self._save_message_to_memory('user', content)
            self._save_message_to_memory('assistant', response)
            
            await websocket.send_json({
                'type': 'sarah_message',
                'message': response
            })
            return

        # Get Sarah's autonomous response
        autonomous_response = self.autonomous_learning.get_autonomous_response(content)

        if autonomous_response['has_goal']:
            # Sarah has a learning goal
            response = autonomous_response['message']

            # Add to conversation history
            self.conversation_history.append(self._format_message_for_api('user', content, None))
            self.conversation_history.append({'role': 'assistant', 'content': response})

            # Save messages
            self._save_message_to_memory('user', content)
            self._save_message_to_memory('assistant', response)

            # Send response
            await websocket.send_json({
                'type': 'sarah_message',
                'message': response
            })

            # Store learning goal for potential autonomous execution
            return

        else:
            # No specific goal yet
            response = autonomous_response['message']

            self.conversation_history.append(self._format_message_for_api('user', content, None))
            self.conversation_history.append({'role': 'assistant', 'content': response})

            self._save_message_to_memory('user', content)
            self._save_message_to_memory('assistant', response)

            await websocket.send_json({
                'type': 'sarah_message',
                'message': response
            })
            return

    async def _handle_autonomous_learning_execution(self, websocket: WebSocket, content: str):
        """Handle autonomous learning execution"""
        if not self.autonomous_learning or not self.browser:
            response = "I'd love to start learning, but I need my learning system and browser to be available! 🚀"
            
            await websocket.send_json({
                'type': 'sarah_message',
                'message': response
            })
            return

        # Check if there's an active learning goal
        if not hasattr(self.autonomous_learning, 'active_learning_goals') or not self.autonomous_learning.active_learning_goals:
            response = "I don't have an active learning goal right now. Want me to explore something specific? 🎯"
            
            await websocket.send_json({
                'type': 'sarah_message',
                'message': response
            })
            return

        learning_goal = self.autonomous_learning.active_learning_goals[-1]

        if learning_goal.status == self.LearningStatus.PLANNED:
            logger.info(f"🚀 Starting autonomous learning session: {learning_goal.title}")

            # Start autonomous learning session
            session_data = self.autonomous_learning.start_autonomous_learning_session(learning_goal)

            # Get initial actions
            initial_actions = session_data['initial_actions']

            if self.browser and hasattr(self.browser, 'is_running') and self.browser.is_running and initial_actions:
                response = f"{session_data['message']}\n\nHere we go! 🎓"

                # Send initial message
                self.conversation_history.append(self._format_message_for_api('user', content, None))
                self.conversation_history.append({'role': 'assistant', 'content': response})

                self._save_message_to_memory('user', content)
                self._save_message_to_memory('assistant', response)

                await websocket.send_json({
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
                            original_query = action.get('original_query', query)

                            # PLATFORM DETECTION: Check if user wants YouTube
                            if 'youtube' in original_query.lower():
                                logger.info(f"🎬 YouTube search detected")
                                await self.browser.search_youtube(query)
                            else:
                                await self.browser.search_google(query)
                            await asyncio.sleep(2)

                        elif action_type == 'click_element':
                            description = action.get('target')
                            # GLOBAL CLICKING FIX: Use universal_click if available
                            if hasattr(self.browser, 'universal_click'):
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

                self.conversation_history.append({'role': 'assistant', 'content': update_msg})
                self._save_message_to_memory('assistant', update_msg)

                await websocket.send_json({
                    'type': 'sarah_message',
                    'message': update_msg
                })

                return

    async def _handle_conversational_message(self, websocket: WebSocket, content: str):
        """Handle simple conversational messages (no actions)"""
        # Simple conversation - no screenshot needed
        user_msg = self._format_message_for_api('user', content, None)
        self.conversation_history.append(user_msg)
        self._save_message_to_memory('user', content)

        # Get response quickly
        response = await self._get_sarah_response()

        self.conversation_history.append({
            'role': 'assistant',
            'content': response
        })
        self._save_message_to_memory('assistant', response)

        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

        await websocket.send_json({
            'type': 'sarah_message',
            'message': response
        })

    async def _handle_audio_message(self, websocket: WebSocket, data: dict):
        """Handle audio message transcription"""
        audio_data = data.get('audio')  # Base64-encoded audio
        transcription = await self._transcribe_audio(audio_data)

        if transcription:
            logger.info(f"🎧 Transcribed: {transcription}")

            # Process as regular message
            screenshot = await self._capture_screen_context()
            user_msg = self._format_message_for_api('user', f"[Voice message] {transcription}", screenshot)
            self.conversation_history.append(user_msg)

            self._save_message_to_memory('user', f"[Voice] {transcription}")

            response = await self._get_sarah_response()

            self.conversation_history.append({
                'role': 'assistant',
                'content': response
            })

            self._save_message_to_memory('assistant', response)

            if len(self.conversation_history) > self.max_history:
                self.conversation_history = self.conversation_history[-self.max_history:]

            await websocket.send_json({
                'type': 'sarah_message',
                'message': response
            })

    async def _transcribe_audio(self, audio_base64: str) -> Optional[str]:
        """
        Transcribe audio using OpenAI Whisper API

        Args:
            audio_base64: Base64-encoded audio data

        Returns:
            Transcribed text or None if failed
        """
        try:
            logger.warning("⚠️ Audio transcription not yet implemented - need Whisper API key")
            return None
        except Exception as e:
            logger.error(f"❌ Audio transcription failed: {e}")
            return None

    async def _get_sarah_response(self) -> str:
        """
        Get Sarah's response using Claude API with vision support

        Returns:
            Sarah's response
        """
        try:
            # Call Claude API with conversation history (including any screenshots)
            response = await asyncio.to_thread(
                self.anthropic.messages.create,
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system=self.system_prompt,
                messages=self.conversation_history
            )

            # Extract response text
            sarah_response = response.content[0].text

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
                        model="claude-3-5-sonnet-20241022",
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

    # ==================== ACTION REASONING AND EXECUTION ====================

    async def _llm_parse_user_intent(self, user_message: str) -> Dict[str, Any]:
        """
        Use Claude to parse user intent - understands ALL natural language variations
        Returns STANDARDIZED intent format
        """
        try:
            response = await asyncio.to_thread(
                self.anthropic.messages.create,
                model="claude-3-haiku-20240307",
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
        if not self.browser or not hasattr(self.browser, 'page') or not self.browser.page:
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
        if not self.browser or not hasattr(self.browser, 'is_running') or not self.browser.is_running:
            logger.error("❌ Browser not running")
            return False
        
        if not hasattr(self.browser, 'page') or not self.browser.page or self.browser.page.is_closed():
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
        if hasattr(self.action_reasoner, 'should_take_action') and not self.action_reasoner.should_take_action(user_intent):
            logger.info("💭 No action required - user acknowledgment or question")
            return None

        # Get current page context for vision analysis
        current_url = self.browser.page.url if self.browser and hasattr(self.browser, 'page') and self.browser.page else "unknown"

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
        if hasattr(self.action_reasoner, 'analyze_vision_context'):
            page_analysis = self.action_reasoner.analyze_vision_context(page_context, current_url)
        else:
            # Simple fallback analysis
            class SimplePageAnalysis:
                def __init__(self):
                    self.page_type = 'unknown'
                    self.state = 'ready'
                    self.observations = []
            page_analysis = SimplePageAnalysis()

        logger.info(f"👁️ Page analysis: {page_analysis.page_type} - {page_analysis.state}")
        if hasattr(page_analysis, 'observations'):
            logger.info(f"   Observations: {', '.join(page_analysis.observations)}")

        # Create action plan
        if hasattr(self.action_reasoner, 'plan_actions'):
            action_plan = self.action_reasoner.plan_actions(user_intent, page_analysis)
        else:
            # Simple action plan
            class SimpleActionPlan:
                def __init__(self):
                    self.goal = user_intent.get('type', 'unknown')
                    self.reasoning = f"Simple {user_intent.get('type')} action"
                    self.steps = []
            action_plan = SimpleActionPlan()
            action_plan.steps = [{'action': user_intent.get('type'), 'target': user_intent.get('target', '')}]

        # SMART POPUP HANDLING: Only dismiss popups if they actually exist
        if hasattr(action_plan, 'steps') and action_plan.steps and action_plan.steps[0].get('action') == 'dismiss_popup':
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

    async def _execute_action_plan(self, action_plan: dict) -> Optional[bool]:
        """
        Execute a planned action from the vision-guided reasoning system
        WITH GLOBAL CLICKING FIX: Uses browser.universal_click() for all clicks

        Args:
            action_plan: Plan created by _parse_user_intent_and_plan

        Returns:
            True if action succeeded, False if failed, None if no action
        """
        if not action_plan or 'plan' not in action_plan:
            return None
            
        plan = action_plan['plan']

        if not hasattr(plan, 'steps') or not plan.steps:
            logger.info("✅ No actions to execute")
            return None

        logger.info(f"🚀 Executing {len(plan.steps)} planned action(s) WITH GLOBAL CLICKING FIX")

        overall_success = True

        for i, step in enumerate(plan.steps):
            # Check if action was cancelled by user interrupt
            if self.action_cancelled:
                logger.info("⏸️  Action cancelled by user - stopping execution")
                return False

            # 🆕 NEW: Check for user interruption command
            if self.current_action_interrupted:
                logger.info("🛑 Action interrupted by user command (stop/cancel)")
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
                    
                    # Check if browser has navigate method
                    if not hasattr(self.browser, 'navigate'):
                        logger.error("❌ Browser doesn't have navigate method")
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

                        # Try universal cookie detector if available
                        if hasattr(self.browser, 'advanced') and hasattr(self.browser.advanced, 'universal_cookie_detector'):
                            try:
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
                            except Exception as e:
                                logger.warning(f"⚠️ Popup detection failed: {e}")
                        else:
                            logger.info("ℹ️  Universal cookie detector not available")
                    else:
                        overall_success = False
                        self.action_steps.append(f"❌ Navigation failed")

                elif action_type == 'search':
                    query = step.get('query')
                    original_query = step.get('original_query', query)

                    # PLATFORM DETECTION: Check if user wants YouTube search
                    search_on_youtube = 'youtube' in original_query.lower() if original_query else False

                    if search_on_youtube:
                        # User explicitly wants YouTube - go straight there!
                        logger.info(f"🎬 YouTube search detected - navigating to YouTube")
                        self.action_steps.append(f"Search YouTube for '{query}'")
                        
                        if hasattr(self.browser, 'search_youtube'):
                            result = await self.browser.search_youtube(query)
                            success = result.get('success', False) if isinstance(result, dict) else False

                            if success:
                                self.action_steps.append(f"✅ Successfully searched YouTube for '{query}'")
                            else:
                                overall_success = False
                                self.action_steps.append(f"❌ YouTube search failed")
                        else:
                            overall_success = False
                            self.action_steps.append(f"❌ YouTube search not available")

                        # Continue to next step
                        continue

                    # Otherwise, proceed with context-aware search
                    self.action_steps.append(f"Search for '{query}'")

                    # Wait for browser readiness
                    if not await self._is_browser_ready():
                        overall_success = False
                        continue

                    # Check if browser has search method
                    if hasattr(self.browser, 'search_google'):
                        result = await self.browser.search_google(query)
                        success = result.get('success', False) if isinstance(result, dict) else False

                        if success:
                            self.action_steps.append(f"✅ Successfully searched for '{query}'")

                            # Wait for page to stabilize after search
                            await self._wait_for_page_stability()
                        else:
                            overall_success = False
                            self.action_steps.append(f"❌ Search failed")
                    else:
                        logger.error("❌ Browser doesn't have search_google method")
                        overall_success = False

                elif action_type == 'dismiss_popup':
                    self.action_steps.append("Dismiss popup/cookie dialog")

                    # Wait for browser readiness
                    if not await self._is_browser_ready():
                        overall_success = False
                        continue

                    # Try accessibility if available
                    if hasattr(self.browser, 'advanced') and hasattr(self.browser.advanced, 'accessibility_click'):
                        result = await self.browser.advanced.accessibility_click()
                        success = result.get('success', False) if isinstance(result, dict) else False

                        if success:
                            self.action_steps.append(f"✅ Popup dismissed via accessibility")
                        else:
                            overall_success = False
                            self.action_steps.append(f"❌ Could not dismiss popup")
                    else:
                        logger.info("ℹ️ Accessibility click not available, skipping popup dismissal")
                        self.action_steps.append("ℹ️ Popup dismissal not available")

                elif action_type in ['click_element', 'click_by_description', 'click']:
                    description = step.get('description') or step.get('target', 'element')

                    # 🔍 Validate click target
                    should_click = await self._should_click_text(description)
                    logger.info(f"🔍 CLICK VALIDATION RESULT: '{description}' -> {should_click}")

                    if not should_click:
                        logger.error(f"🛑 BLOCKED INVALID CLICK: '{description}'")
                        self.action_steps.append(f"❌ Cannot click descriptive text: '{description}'")
                        overall_success = False
                        continue

                    self.action_steps.append(f"Click: {description}")

                    # ENHANCED CLICKING: Wait for page to be ready after popup dismissal
                    if i > 0 and plan.steps[i-1].get('action') == 'dismiss_popup':
                        logger.info("🔄 Waiting extra time after popup dismissal...")
                        await asyncio.sleep(2)

                    try:
                        # Capture BEFORE screenshot for verification
                        screenshot_before = await self._capture_screen_context()

                        # Use robust click execution with timeout
                        success = await asyncio.wait_for(
                            self._robust_click_execution(description, max_attempts=2),
                            timeout=15.0
                        )

                        if success:
                            # Wait for page to settle after click
                            await asyncio.sleep(2)

                            # Capture AFTER screenshot
                            screenshot_after = await self._capture_screen_context()

                            # 🔍 VERIFY: Did the click actually work?
                            if screenshot_before and screenshot_after and self.universal_locator:
                                try:
                                    verification = await self.universal_locator.verify_element_interaction(
                                        user_intent=f"click {description}",
                                        before_screenshot=screenshot_before,
                                        after_screenshot=screenshot_after
                                    )

                                    if verification.get('success'):
                                        self.action_steps.append(f"✅ Clicked '{description}' - Verified: {verification.get('reasoning', 'success')}")
                                        logger.info(f"✅ VERIFIED CLICK SUCCESS: {verification.get('reasoning', 'success')}")
                                    else:
                                        # Click executed but didn't have expected effect
                                        overall_success = False
                                        self.action_steps.append(f"⚠️ Click executed but verification failed: {verification.get('reasoning', 'unknown')}")
                                        logger.warning(f"⚠️ CLICK VERIFICATION FAILED: {verification.get('reasoning', 'unknown')}")
                                except Exception as e:
                                    logger.warning(f"⚠️ Click verification error: {e}")
                                    self.action_steps.append(f"✅ Clicked '{description}' (verification skipped)")
                            else:
                                # No screenshots available for verification
                                self.action_steps.append(f"✅ Clicked '{description}' (no verification)")
                                logger.info(f"✅ CLICK SUCCESS: Clicked '{description}'")
                        else:
                            overall_success = False
                            self.action_steps.append(f"❌ Click failed for '{description}'")

                    except asyncio.TimeoutError:
                        logger.error(f"⏰ CLICK TIMEOUT: '{description}' took >15s - CANCELLING ALL ACTIONS")
                        self.action_steps.append(f"⏰ Click timed out: '{description}'")
                        return False

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

    # ==================== LEARNING AND ANALYSIS ====================

    async def _analyze_and_learn(self, sarah_response: str, action_success: bool):
        """
        Analyze Sarah's action and extract learnings

        Args:
            sarah_response: What Sarah said/did
            action_success: Whether the action succeeded
        """
        try:
            # If learning engine is available, use it
            if self.learning_engine and self.current_action and self.browser and hasattr(self.browser, 'current_url') and self.browser.current_url:

                # Get relevant existing patterns
                relevant_patterns = []
                if hasattr(self.learning_engine, 'get_relevant_patterns'):
                    relevant_patterns = self.learning_engine.get_relevant_patterns(self.current_action)

                if action_success and len(self.action_steps) > 0:
                    # Extract new UI pattern from successful action
                    if hasattr(self.learning_engine, 'extract_pattern_from_experience'):
                        pattern = self.learning_engine.extract_pattern_from_experience(
                            action_description=self.current_action,
                            steps_taken=self.action_steps,
                            visual_observations=self.visual_observations,
                            url=self.browser.current_url,
                            success=True
                        )

                        if pattern and hasattr(self.learning_engine, 'save_pattern'):
                            self.learning_engine.save_pattern(pattern, share=True)
                            logger.info(f"🎓 Sarah learned new UI pattern: {pattern.pattern_type}")

                # Record the experiment
                if hasattr(self.learning_engine, 'record_experiment'):
                    experiment = self.ExperimentResult(
                        experiment_id=f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        action_taken=self.current_action,
                        expected_result=f"Successfully {self.current_action}",
                        actual_result=sarah_response,
                        success=action_success,
                        screenshot_before=None,
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

            # Get relevant UI patterns if learning engine is available
            if self.learning_engine and hasattr(self.learning_engine, 'get_relevant_patterns'):
                patterns = self.learning_engine.get_relevant_patterns(user_message)
                if patterns:
                    knowledge_context += "\n\n**Relevant UI Patterns I've Learned:**\n"
                    for pattern in patterns[:3]:  # Top 3
                        if hasattr(pattern, 'description') and hasattr(pattern, 'success_rate'):
                            knowledge_context += f"- {pattern.description} (success rate: {pattern.success_rate*100:.0f}%)\n"
                        elif isinstance(pattern, dict):
                            knowledge_context += f"- {pattern.get('description', 'Unknown pattern')}\n"

            # Get relevant skills if platform mentioned
            if mentioned_platform and self.learning_engine and hasattr(self.learning_engine, 'get_relevant_skills'):
                skills = self.learning_engine.get_relevant_skills(mentioned_platform)
                if skills:
                    knowledge_context += f"\n\n**My {mentioned_platform} Skills:**\n"
                    for skill in skills[:3]:  # Top 3
                        if hasattr(skill, 'skill_name') and hasattr(skill, 'confidence') and hasattr(skill, 'usage_count'):
                            knowledge_context += f"- {skill.skill_name} (confidence: {skill.confidence*100:.0f}%, used {skill.usage_count} times)\n"
                        elif isinstance(skill, dict):
                            knowledge_context += f"- {skill.get('skill_name', 'Unknown skill')}\n"

            return knowledge_context

        except Exception as e:
            logger.error(f"Error getting relevant knowledge: {e}")
            return ""


# Legacy compatibility class
class SarahChatServer(SarahChatHandler):
    """
    Legacy wrapper for backward compatibility
    Provides start_server() method for code expecting standalone server
    """
    async def start_server(self):
        """
        Legacy method - does nothing since FastAPI handles servers
        Returns True to indicate "server is running"
        """
        logger.warning("⚠️ start_server() called on FastAPI-compatible handler")
        logger.info("   FastAPI handles WebSocket servers, not this class")
        return True