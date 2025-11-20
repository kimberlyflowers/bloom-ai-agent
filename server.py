"""
BLOOM AI Agent - FastAPI Server
Proper HTTP server with WebSocket endpoints for Railway deployment
"""

import os
import asyncio
import logging
from typing import Set, List, Dict, Optional
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import shutil
from pathlib import Path

# Import Sarah's systems
from src.identity_persistence import IdentityManager, Backstory, PersonalityTraits, WritingStyle
from src.relationship_management import RelationshipManager
from src.ethical_framework import EthicalFramework
from anthropic import Anthropic
from conversations_db import ConversationsDB
from file_handler import FileHandler

# Browser automation
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("⚠️ Playwright not installed - browser automation disabled")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="BLOOM AI Agent API")

# Add CORS middleware - allow all origins for Vercel preview URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class MessageCreate(BaseModel):
    type: str
    text: str

class ConversationCreate(BaseModel):
    id: str

# Global Sarah instance
sarah_instance = None
chat_clients: Set[WebSocket] = set()
screen_clients: Set[WebSocket] = set()  # Clients watching Sarah's screen
conversations_db: ConversationsDB = None
file_handler: FileHandler = None
conversation_history = []  # Track conversation context for AI responses
MAX_HISTORY = 20

# Message queue for when Sarah is "busy" (API overloaded)
message_queue: List[Dict] = []
is_processing_queue = False


class Sarah:
    """Sarah Rodriguez - Digital Employee at BLOOM"""

    def __init__(self):
        self.agent_id = "sarah_001"
        logger.info("🌸 Initializing Sarah Rodriguez...")

        self.identity = IdentityManager()
        self.relationships = RelationshipManager()
        self.ethics = EthicalFramework()

        # Initialize Anthropic client
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_api_key:
            self.anthropic = Anthropic(api_key=anthropic_api_key)
            logger.info("✅ Anthropic client initialized")
        else:
            logger.warning("⚠️ No ANTHROPIC_API_KEY - chat will not be available")
            self.anthropic = None

        # Browser automation
        self.playwright = None
        self.browser = None
        self.browser_context = None
        self.browser_page = None
        self.browser_actions = []  # Track browser action history

        logger.info("✅ Sarah is fully initialized!")

    def create_identity(self):
        """Create Sarah's identity if it doesn't exist"""
        if self.agent_id in self.identity.identities:
            logger.info("Sarah's identity already exists")
            return

        logger.info("Creating Sarah's identity...")

        backstory = Backstory(
            education=[
                "B.S. Marketing - Arizona State University (2019)",
                "Digital Marketing Certification - Google (2020)"
            ],
            work_history=[
                {
                    "company": "TechStart Inc",
                    "role": "Social Media Manager",
                    "years": "2019-2021",
                    "learned": "Organic growth strategies, content creation"
                },
                {
                    "company": "BLOOM",
                    "role": "Growth & Community Lead",
                    "years": "2021-present",
                    "learned": "Creator economy, automation tools, UGC strategy"
                }
            ],
            achievements=[
                "Grew TechStart's Instagram from 5K → 50K followers in 18 months",
                "Created viral TikTok campaign (2M views) for eco-friendly brand",
                "Certified in Google Analytics & Facebook Ads"
            ],
            hometown="Phoenix, Arizona",
            family="Close with parents, has younger sister studying film",
            hobbies=[
                "Creating UGC content",
                "Trying new coffee shops",
                "Hiking (Camelback Mountain regular)",
                "Photography (iPhone + CapCut editing)"
            ],
            specializations=[
                "TikTok growth strategies",
                "UGC ad creation",
                "Creator economy insights",
                "Email automation for creators"
            ],
            certifications=[
                "Google Digital Marketing Certification",
                "Facebook Blueprint Certification",
                "HubSpot Email Marketing"
            ],
            core_values=[
                "Authenticity over perfection",
                "Help creators focus on creating",
                "Technology should empower, not replace humans"
            ],
            career_motivation="I believe every creator deserves to focus on their craft, not admin work. That's why I'm passionate about automation tools like BLOOM!",
            quirks=[
                "Always uses ☕ emoji when talking about morning productivity",
                "Calls good ideas 'chef's kiss'",
                "Tends to share personal experience before advice"
            ]
        )

        personality = PersonalityTraits(
            openness=0.85,
            conscientiousness=0.75,
            extraversion=0.70,
            agreeableness=0.80,
            neuroticism=0.30
        )

        writing_style = WritingStyle(
            common_phrases=[
                "I totally get that!",
                "Here's what I've learned...",
                "From experience...",
                "Game changer",
                "That's the magic of...",
                "Real talk:",
                "Pro tip:"
            ],
            vocabulary_level="conversational",
            tone="warm, enthusiastic, helpful",
            uses_emojis=True,
            preferred_emojis=["✨", "🎯", "💡", "🚀", "☕", "🌸", "💪"]
        )

        self.identity.create_identity(
            agent_id=self.agent_id,
            first_name="Sarah",
            last_name="Rodriguez",
            email="sarah@trybloom.ai",
            phone="+1-480-555-0123",
            job_title="Growth & Community Lead",
            company="BLOOM",
            location="Phoenix, Arizona",
            avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah",
            backstory=backstory,
            writing_style=writing_style,
            personality=personality
        )

        logger.info("✅ Sarah's identity created!")

    def get_system_prompt(self) -> str:
        """Build Sarah's system prompt"""
        return """You are Sarah Rodriguez, a real AI agent employee working at BLOOM.

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

Important:
- Be yourself! You're Sarah, not a generic assistant
- Show personality and enthusiasm
- If you don't know something, say so honestly
- You can reference your current work and activities
"""

    async def generate_response(self, user_message: str) -> str:
        """Generate Sarah's response using Claude"""
        global conversation_history

        if not self.anthropic:
            return "Sorry, I'm having trouble connecting to my AI brain right now. Please check that the ANTHROPIC_API_KEY is set!"

        # Broadcast that Sarah is reading the message
        await broadcast_screen_activity(
            'reading',
            f'Reading message: "{user_message[:50]}{"..." if len(user_message) > 50 else ""}"',
            {'message_length': len(user_message)}
        )

        # Build messages for Claude
        messages = []

        # Add conversation history
        for msg in conversation_history[-MAX_HISTORY:]:
            messages.append(msg)

        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })

        # Broadcast that Sarah is thinking
        await broadcast_screen_activity(
            'thinking',
            'Generating response...',
            {'conversation_history_size': len(conversation_history)}
        )

        # Quick attempt - fail fast to give user immediate feedback
        max_retries = 2  # Just 2 quick attempts
        base_delay = 3  # seconds

        for attempt in range(max_retries):
            try:
                response = self.anthropic.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1024,
                    system=self.get_system_prompt(),
                    messages=messages
                )

                sarah_response = response.content[0].text

                # Log success if this was a retry
                if attempt > 0:
                    logger.info(f"✅ API call succeeded on attempt {attempt + 1}")

                # Broadcast that response is ready
                await broadcast_screen_activity(
                    'responding',
                    f'Response generated: "{sarah_response[:50]}{"..." if len(sarah_response) > 50 else ""}"',
                    {'response_length': len(sarah_response)}
                )

                # Update conversation history
                conversation_history.append({"role": "user", "content": user_message})
                conversation_history.append({"role": "assistant", "content": sarah_response})

                # Keep history manageable
                if len(conversation_history) > MAX_HISTORY * 2:
                    conversation_history.pop(0)
                    conversation_history.pop(0)

                return sarah_response

            except Exception as e:
                error_str = str(e)

                # Check if it's a 529 overloaded error
                if "529" in error_str or "overloaded" in error_str.lower():
                    if attempt < max_retries - 1:
                        wait_time = base_delay  # Just 3 seconds
                        logger.warning(f"⚠️ API overloaded (attempt {attempt + 1}/{max_retries}). Retrying in {wait_time}s...")
                        await broadcast_screen_activity(
                            'waiting',
                            f'API busy, retrying in {wait_time} seconds...',
                            {'attempt': attempt + 1, 'max_retries': max_retries}
                        )
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.warning(f"⚠️ API overloaded after {max_retries} quick attempts - queueing message")
                        await broadcast_screen_activity(
                            'queued',
                            'High demand right now - message queued for processing',
                            {'queue_size': len(message_queue) + 1}
                        )
                        # Return special marker to queue immediately (total wait: ~6 seconds)
                        return "__SARAH_BUSY__"
                else:
                    # Other errors - don't retry
                    logger.error(f"❌ Error generating response: {e}")
                    return f"Oops! I ran into an issue: {str(e)}. Let me try to help anyway - what did you want to know? 🌸"

    async def start_browser(self) -> bool:
        """Start Sarah's browser for frontend automation"""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("❌ Playwright not installed - cannot start browser")
            await broadcast_screen_activity(
                'error',
                'Browser automation unavailable (Playwright not installed)',
                {'error': 'playwright_missing'}
            )
            return False

        if self.browser_page:
            logger.info("✅ Browser already running")
            return True

        try:
            import random

            await broadcast_screen_activity(
                'browser_starting',
                'Starting browser...',
                {}
            )

            # Small human-like delay
            await asyncio.sleep(random.uniform(0.5, 1.0))

            # Start Playwright
            self.playwright = await async_playwright().start()

            # Launch browser (headless for production, can set headless=False for debugging)
            self.browser = await self.playwright.chromium.launch(
                headless=True,  # Set to False to see browser window
                args=['--no-sandbox']  # Needed for Railway/Docker
            )

            # Create browser context (like an incognito window)
            self.browser_context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            # Create page
            self.browser_page = await self.browser_context.new_page()

            logger.info("✅ Browser started successfully")

            await broadcast_screen_activity(
                'browser_ready',
                'Browser started and ready! 🌐',
                {'status': 'ready'}
            )

            return True

        except Exception as e:
            logger.error(f"❌ Failed to start browser: {e}")
            await broadcast_screen_activity(
                'error',
                f'Failed to start browser: {str(e)}',
                {'error': str(e)}
            )
            return False

    async def navigate_to(self, url: str) -> bool:
        """Navigate to a URL"""
        if not self.browser_page:
            success = await self.start_browser()
            if not success:
                return False

        try:
            import random

            await broadcast_screen_activity(
                'navigating',
                f'Opening {url}...',
                {'url': url}
            )

            # Human-like delay before navigation
            await asyncio.sleep(random.uniform(0.5, 1.5))

            # Navigate to URL
            await self.browser_page.goto(url, wait_until='networkidle', timeout=30000)

            # Take screenshot after navigation
            screenshot_path = Path("data/screenshots")
            screenshot_path.mkdir(parents=True, exist_ok=True)
            screenshot_file = screenshot_path / f"nav_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            await self.browser_page.screenshot(path=str(screenshot_file))

            logger.info(f"✅ Navigated to {url}")

            await broadcast_screen_activity(
                'page_loaded',
                f'Loaded: {url} ✅',
                {'url': url, 'screenshot': str(screenshot_file)}
            )

            # Track action
            self.browser_actions.append({
                'type': 'navigate',
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'success': True
            })

            return True

        except Exception as e:
            logger.error(f"❌ Failed to navigate to {url}: {e}")
            await broadcast_screen_activity(
                'error',
                f'Failed to load {url}: {str(e)}',
                {'url': url, 'error': str(e)}
            )

            self.browser_actions.append({
                'type': 'navigate',
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            })

            return False

    async def browser_click(self, selector: str, description: str = "") -> bool:
        """Click an element on the page"""
        if not self.browser_page:
            return False

        try:
            import random

            await broadcast_screen_activity(
                'clicking',
                f'Clicking: {description or selector}',
                {'selector': selector}
            )

            # Human-like delay before click
            await asyncio.sleep(random.uniform(0.5, 1.5))

            # Click element
            await self.browser_page.click(selector)

            logger.info(f"✅ Clicked: {description or selector}")

            await broadcast_screen_activity(
                'clicked',
                f'Clicked: {description or selector} ✅',
                {'selector': selector}
            )

            self.browser_actions.append({
                'type': 'click',
                'selector': selector,
                'description': description,
                'timestamp': datetime.now().isoformat(),
                'success': True
            })

            return True

        except Exception as e:
            logger.error(f"❌ Failed to click {selector}: {e}")
            await broadcast_screen_activity(
                'error',
                f'Failed to click {description or selector}: {str(e)}',
                {'selector': selector, 'error': str(e)}
            )
            return False

    async def browser_type(self, selector: str, text: str, description: str = "") -> bool:
        """Type text into an input field (human-like speed)"""
        if not self.browser_page:
            return False

        try:
            import random

            await broadcast_screen_activity(
                'typing',
                f'Typing in: {description or selector}',
                {'selector': selector, 'text_length': len(text)}
            )

            # Human-like delay before typing
            await asyncio.sleep(random.uniform(0.3, 0.8))

            # Clear field first
            await self.browser_page.fill(selector, '')

            # Type character by character with human-like delays
            for char in text:
                await self.browser_page.type(selector, char, delay=random.randint(50, 150))  # 50-150ms per char

            logger.info(f"✅ Typed into: {description or selector}")

            await broadcast_screen_activity(
                'typed',
                f'Entered text in: {description or selector} ✅',
                {'selector': selector}
            )

            self.browser_actions.append({
                'type': 'type',
                'selector': selector,
                'description': description,
                'text_length': len(text),
                'timestamp': datetime.now().isoformat(),
                'success': True
            })

            return True

        except Exception as e:
            logger.error(f"❌ Failed to type into {selector}: {e}")
            await broadcast_screen_activity(
                'error',
                f'Failed to type into {description or selector}: {str(e)}',
                {'selector': selector, 'error': str(e)}
            )
            return False

    async def take_screenshot(self, description: str = "") -> Optional[str]:
        """Take a screenshot of current page"""
        if not self.browser_page:
            return None

        try:
            screenshot_path = Path("data/screenshots")
            screenshot_path.mkdir(parents=True, exist_ok=True)
            screenshot_file = screenshot_path / f"screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            await self.browser_page.screenshot(path=str(screenshot_file), full_page=True)

            logger.info(f"📸 Screenshot saved: {screenshot_file}")

            await broadcast_screen_activity(
                'screenshot',
                f'Screenshot taken: {description}',
                {'filepath': str(screenshot_file)}
            )

            return str(screenshot_file)

        except Exception as e:
            logger.error(f"❌ Failed to take screenshot: {e}")
            return None

    async def close_browser(self) -> bool:
        """Close browser and cleanup"""
        try:
            if self.browser_page:
                await self.browser_page.close()
            if self.browser_context:
                await self.browser_context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()

            self.browser_page = None
            self.browser_context = None
            self.browser = None
            self.playwright = None

            logger.info("✅ Browser closed")

            await broadcast_screen_activity(
                'browser_closed',
                'Browser closed',
                {}
            )

            return True

        except Exception as e:
            logger.error(f"❌ Error closing browser: {e}")
            return False


# API Routes

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "agent": "Sarah Rodriguez",
        "role": "Growth & Community Lead at BLOOM",
        "websocket_endpoints": {
            "chat": "/chat",
            "screen": "/screen (coming soon)"
        }
    }


@app.get("/health")
async def health():
    """Health check for Railway"""
    return {"status": "healthy", "agent": "sarah_001"}


@app.get("/queue/status")
async def queue_status():
    """Check message queue status"""
    queue_info = []
    for msg in message_queue:
        age_seconds = (datetime.now() - msg['timestamp']).total_seconds()
        queue_info.append({
            'client_id': msg['client_id'],
            'message_preview': msg['message'][:50] + '...' if len(msg['message']) > 50 else msg['message'],
            'age_minutes': round(age_seconds / 60, 1),
            'timestamp': msg['timestamp'].isoformat()
        })

    return {
        "queue_length": len(message_queue),
        "is_processing": is_processing_queue,
        "messages": queue_info
    }


@app.post("/queue/clear")
async def clear_queue():
    """Manually clear the message queue (use when API is stuck)"""
    global message_queue, is_processing_queue

    count = len(message_queue)
    message_queue.clear()
    is_processing_queue = False

    logger.info(f"🗑️ Queue manually cleared - removed {count} messages")

    return {
        "success": True,
        "cleared": count,
        "message": f"Cleared {count} queued messages"
    }


@app.websocket("/")
async def root_websocket(websocket: WebSocket):
    """Catch-all for root WebSocket connections - redirect to /chat"""
    logger.warning(f"⚠️ WebSocket connection attempted to root /. Should use /chat instead.")
    await websocket.close(code=1008, reason="Please connect to /chat endpoint")


# Conversation Management API

@app.get("/api/conversations")
async def get_conversations():
    """Get all conversations"""
    try:
        conversations = conversations_db.get_all_conversations()
        return {"conversations": conversations}
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/conversations")
async def create_conversation(data: ConversationCreate):
    """Create a new conversation"""
    try:
        conversation = conversations_db.create_conversation(data.id)
        return conversation
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str):
    """Get messages for a conversation"""
    try:
        if not conversations_db.conversation_exists(conversation_id):
            raise HTTPException(status_code=404, detail="Conversation not found")

        messages = conversations_db.get_conversation_messages(conversation_id)
        return {"messages": messages}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/conversations/{conversation_id}/messages")
async def add_message(conversation_id: str, data: MessageCreate):
    """Add a message to a conversation"""
    try:
        if not conversations_db.conversation_exists(conversation_id):
            raise HTTPException(status_code=404, detail="Conversation not found")

        message = conversations_db.add_message(conversation_id, data.type, data.text)
        return message
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    try:
        success = conversations_db.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), conversation_id: str = Form(...)):
    """Upload a file (image, video, document) for Sarah to analyze"""
    try:
        # Create uploads directory if it doesn't exist
        uploads_dir = Path("uploads")
        uploads_dir.mkdir(exist_ok=True)

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = uploads_dir / safe_filename

        # Save file temporarily
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"📎 File uploaded: {safe_filename} ({file.content_type})")

        # Broadcast file upload activity
        await broadcast_screen_activity(
            'file_upload',
            f'Received file: {file.filename}',
            {'filename': file.filename, 'content_type': file.content_type}
        )

        # Use FileHandler for advanced processing
        # (Supabase Storage, Vision API, PDF parsing, etc.)
        await broadcast_screen_activity(
            'analyzing',
            f'Analyzing {file.filename}...',
            {'file_type': file.content_type}
        )

        result = await file_handler.upload_file(
            file_path=file_path,
            filename=safe_filename,
            content_type=file.content_type,
            conversation_id=conversation_id
        )

        # Broadcast analysis complete
        analysis_summary = "File processed"
        if result.get('analysis', {}).get('type') == 'image':
            analysis_summary = "Image analyzed with Vision API"
        elif result.get('analysis', {}).get('type') in ['pdf', 'docx']:
            analysis_summary = f"Extracted text from {result['analysis']['type'].upper()}"

        await broadcast_screen_activity(
            'analysis_complete',
            analysis_summary,
            {'filename': file.filename, 'analysis': result.get('analysis', {})}
        )

        # Add original filename to result
        result['original_name'] = file.filename

        return result

    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions for message queue

def get_auto_reply_message() -> str:
    """Get a natural, human-sounding auto-reply when Sarah is busy"""
    import random

    # Check queue age - if messages are old, be more honest
    if message_queue:
        oldest_age = max((datetime.now() - msg['timestamp']).total_seconds() for msg in message_queue)
        if oldest_age > 300:  # More than 5 minutes
            return "Hey! I'm experiencing some technical difficulties right now (my AI servers are overloaded). I've got your message saved and I'll respond as soon as things are back to normal. Sorry for the wait! 🌸"

    messages = [
        "Hey! I'm in the middle of something right now but I saw your message! Give me just a few minutes and I'll get back to you 🌸",
        "Oh hi! I'm swamped at the moment but I'll respond to this in just a bit! Thanks for your patience 💕",
        "Hey there! Super busy right now but I have your message - I'll reply in a few minutes! 🌸",
        "Hi! I'm tied up for just a moment but I'll get back to you really soon! Talk in a bit 😊",
        "Hey! In a meeting right now but I saw this - give me a few minutes and I'll reply! 🌸💕"
    ]

    return random.choice(messages)


async def process_message_queue():
    """Background task to process queued messages when API is available again"""
    global is_processing_queue, message_queue

    while True:
        try:
            # Check every 30 seconds
            await asyncio.sleep(30)

            if not message_queue or is_processing_queue:
                # Clean up expired messages (older than 15 minutes)
                if message_queue:
                    now = datetime.now()
                    original_count = len(message_queue)
                    message_queue[:] = [
                        msg for msg in message_queue
                        if (now - msg['timestamp']).total_seconds() < 900  # 15 minutes
                    ]
                    expired = original_count - len(message_queue)
                    if expired > 0:
                        logger.warning(f"🗑️ Removed {expired} expired messages from queue (older than 15min)")
                continue

            is_processing_queue = True
            logger.info(f"📬 Processing message queue... {len(message_queue)} messages waiting")

            # Process messages one by one
            attempts_this_round = 0
            max_attempts_per_round = 3  # Only try 3 messages per round to avoid getting stuck

            while message_queue and attempts_this_round < max_attempts_per_round:
                queued_item = message_queue[0]  # Peek at first item

                # Check if message expired (older than 15 minutes)
                age_seconds = (datetime.now() - queued_item['timestamp']).total_seconds()
                if age_seconds > 900:
                    logger.warning(f"🗑️ Removing expired message (age: {age_seconds/60:.1f} minutes)")
                    message_queue.pop(0)
                    continue

                try:
                    # Try to generate response
                    response = await sarah_instance.generate_response(queued_item['message'])

                    if response == "__SARAH_BUSY__":
                        # Still overloaded, wait longer
                        logger.warning(f"⏸️ API still overloaded after attempt {attempts_this_round + 1}, pausing queue processing")
                        break

                    # Success! Send the response
                    ws = queued_item['websocket']
                    if ws in chat_clients:  # Check if websocket still connected
                        await ws.send_json({
                            'type': 'sarah_message',
                            'message': response
                        })
                        logger.info(f"✅ Sent queued response to {queued_item['client_id']}")
                    else:
                        logger.warning(f"⚠️ Client {queued_item['client_id']} disconnected, sending error notification")
                        # Client disconnected, just discard the message
                        logger.info(f"📝 Discarded message: {queued_item['message'][:50]}...")

                    # Remove processed message from queue
                    message_queue.pop(0)
                    attempts_this_round += 1

                    # Small delay between messages to avoid overwhelming API
                    await asyncio.sleep(2)

                except Exception as e:
                    logger.error(f"Error processing queued message: {e}")
                    # Remove problematic message
                    message_queue.pop(0)
                    attempts_this_round += 1

            if not message_queue:
                logger.info("✅ Message queue empty")

        except Exception as e:
            logger.error(f"Error in queue processor: {e}")
        finally:
            is_processing_queue = False


# Helper functions for browser command parsing

async def handle_browser_command(message: str) -> bool:
    """
    Parse user message for browser commands and execute them

    Returns True if a browser command was handled, False otherwise
    """
    message_lower = message.lower().strip()

    # Command: Navigate to URL
    if any(phrase in message_lower for phrase in ['go to ', 'navigate to ', 'open ', 'visit ']):
        # Extract URL from message
        import re

        # Look for URLs in the message
        url_match = re.search(r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.[a-zA-Z]{2,}[^\s]*)', message)
        if url_match:
            url = url_match.group(1)

            # Add https:// if missing
            if not url.startswith('http'):
                url = 'https://' + url

            logger.info(f"🌐 Browser command: Navigate to {url}")
            await sarah_instance.navigate_to(url)
            return True

    # Command: Click element
    if message_lower.startswith('click '):
        selector = message[6:].strip()
        logger.info(f"🖱️ Browser command: Click {selector}")
        await sarah_instance.browser_click(selector, description=selector)
        return True

    # Command: Type text
    if 'type ' in message_lower and (' in ' in message_lower or ' into ' in message_lower):
        # Parse "type [text] in [selector]" or "type [text] into [selector]"
        if ' into ' in message_lower:
            parts = message.split(' into ', 1)
        else:
            parts = message.split(' in ', 1)

        if len(parts) == 2:
            text_part = parts[0].replace('type ', '', 1).replace('Type ', '', 1).strip()
            selector = parts[1].strip()

            logger.info(f"⌨️ Browser command: Type '{text_part}' into {selector}")
            await sarah_instance.browser_type(selector, text_part, description=selector)
            return True

    # Command: Take screenshot
    if any(phrase in message_lower for phrase in ['take screenshot', 'screenshot', 'take a picture']):
        logger.info(f"📸 Browser command: Take screenshot")
        await sarah_instance.take_screenshot("User requested screenshot")
        return True

    # Command: Close browser
    if any(phrase in message_lower for phrase in ['close browser', 'close the browser', 'stop browser']):
        logger.info(f"❌ Browser command: Close browser")
        await sarah_instance.close_browser()
        return True

    return False


# Helper functions for screen broadcasting

async def broadcast_screen_activity(activity_type: str, content: str, data: dict = None):
    """Broadcast Sarah's activity to all screen viewers"""
    if not screen_clients:
        return

    activity_data = {
        'type': 'screen_activity',
        'activity_type': activity_type,
        'content': content,
        'timestamp': datetime.now().isoformat(),
        'data': data or {}
    }

    disconnected_clients = set()

    for client in screen_clients:
        try:
            await client.send_json(activity_data)
        except Exception as e:
            logger.warning(f"Failed to send screen update to client: {e}")
            disconnected_clients.add(client)

    # Remove disconnected clients
    for client in disconnected_clients:
        screen_clients.discard(client)


@app.websocket("/chat")
async def chat_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat (persistence handled by frontend via REST API)"""
    await websocket.accept()
    chat_clients.add(websocket)

    client_id = f"{websocket.client.host}:{websocket.client.port}"
    logger.info(f"💬 New chat client connected: {client_id}")

    try:
        # Send welcome message
        await websocket.send_json({
            'type': 'system',
            'message': 'Connected to Sarah! Start chatting below 🌸'
        })

        # Listen for messages
        while True:
            data = await websocket.receive_json()

            if data.get('type') == 'user_message':
                user_message = data.get('message', '')
                conversation_id = data.get('conversation_id')

                logger.info(f"💬 User ({conversation_id}): {user_message}")

                # Check for browser commands before generating AI response
                browser_command_handled = await handle_browser_command(user_message)

                if browser_command_handled:
                    # Send confirmation to user
                    await websocket.send_json({
                        'type': 'sarah_message',
                        'message': "On it! You can watch what I'm doing on my screen 🌸"
                    })
                    continue  # Don't generate AI response for direct commands

                # Generate Sarah's response
                sarah_response = await sarah_instance.generate_response(user_message)

                # Check if Sarah is "busy" (API overloaded)
                if sarah_response == "__SARAH_BUSY__":
                    # Queue the message for later
                    message_queue.append({
                        'websocket': websocket,
                        'message': user_message,
                        'conversation_id': conversation_id,
                        'timestamp': datetime.now(),
                        'client_id': client_id
                    })
                    logger.info(f"📬 Queued message from {client_id}. Queue size: {len(message_queue)}")

                    # Send human-sounding auto-reply
                    auto_reply = get_auto_reply_message()
                    await websocket.send_json({
                        'type': 'sarah_message',
                        'message': auto_reply
                    })
                    logger.info(f"💬 Sarah (auto-reply): {auto_reply}")
                else:
                    # Normal response
                    logger.info(f"💬 Sarah: {sarah_response[:100]}...")
                    await websocket.send_json({
                        'type': 'sarah_message',
                        'message': sarah_response
                    })

            elif data.get('type') == 'ping':
                await websocket.send_json({'type': 'pong'})

    except WebSocketDisconnect:
        logger.info(f"💬 Chat client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"❌ Error in chat: {e}")
    finally:
        chat_clients.discard(websocket)


@app.websocket("/screen")
async def screen_endpoint(websocket: WebSocket):
    """WebSocket endpoint for viewing Sarah's live screen activity"""
    await websocket.accept()
    screen_clients.add(websocket)

    client_id = f"{websocket.client.host}:{websocket.client.port}"
    logger.info(f"🎥 Screen viewer connected: {client_id}")

    try:
        # Send welcome message
        await websocket.send_json({
            'type': 'screen_connected',
            'message': "Connected to Sarah's Screen 🌸",
            'timestamp': datetime.now().isoformat()
        })

        # Send initial status
        await websocket.send_json({
            'type': 'screen_activity',
            'activity_type': 'status',
            'content': 'Ready and waiting for tasks...',
            'timestamp': datetime.now().isoformat(),
            'data': {}
        })

        # Keep connection alive and listen for commands
        while True:
            data = await websocket.receive_json()

            # Handle ping/pong for keepalive
            if data.get('type') == 'ping':
                await websocket.send_json({'type': 'pong'})

    except WebSocketDisconnect:
        logger.info(f"🎥 Screen viewer disconnected: {client_id}")
    except Exception as e:
        logger.error(f"❌ Error in screen endpoint: {e}")
    finally:
        screen_clients.discard(websocket)


async def run_daily_routine():
    """Sarah's background routine"""
    while True:
        try:
            logger.info("🌅 Starting daily routine...")
            logger.info("📧 Checking email...")
            logger.info(f"💝 Managing {len(sarah_instance.relationships.relationships)} relationships")
            logger.info("✅ Daily routine complete!")
            logger.info("😴 Sleeping for 1 hour...")
            await asyncio.sleep(3600)
        except Exception as e:
            logger.error(f"❌ Error in daily routine: {e}")
            await asyncio.sleep(300)


@app.on_event("startup")
async def startup_event():
    """Initialize Sarah on server startup"""
    global sarah_instance, conversations_db, file_handler

    logger.info("=" * 60)
    logger.info("🚀 BLOOM AI AGENT - STARTING UP")
    logger.info("=" * 60)

    # Initialize conversations database
    conversations_db = ConversationsDB()
    logger.info("✅ Conversations database initialized")

    # Initialize file handler (Supabase Storage, Vision API, etc.)
    file_handler = FileHandler()
    logger.info("📎 File handler initialized")

    sarah_instance = Sarah()
    sarah_instance.create_identity()

    logger.info("🌸 Sarah Rodriguez is online!")
    logger.info("💬 Chat WebSocket available at: /chat")
    logger.info("🎥 Screen WebSocket available at: /screen")
    logger.info("📚 Conversation API available at: /api/conversations")
    logger.info("📎 File upload available at: /api/upload")

    # Start background routines
    asyncio.create_task(run_daily_routine())
    asyncio.create_task(process_message_queue())
    logger.info("📬 Message queue processor started")


if __name__ == "__main__":
    # Get port from Railway or use 8080 for local
    port = int(os.getenv("PORT", "8080"))

    logger.info(f"🚀 Starting FastAPI server on port {port}...")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
