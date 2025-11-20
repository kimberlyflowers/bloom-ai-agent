"""
BLOOM AI Agent - FastAPI Server
Proper HTTP server with WebSocket endpoints for Railway deployment
"""

import os
import asyncio
import logging
from typing import Set, List, Dict
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import Sarah's systems
from src.identity_persistence import IdentityManager, Backstory, PersonalityTraits, WritingStyle
from src.relationship_management import RelationshipManager
from src.ethical_framework import EthicalFramework
from anthropic import Anthropic
from conversations_db import ConversationsDB

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
conversations_db: ConversationsDB = None
MAX_HISTORY = 20


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
        if not self.anthropic:
            return "Sorry, I'm having trouble connecting to my AI brain right now. Please check that the ANTHROPIC_API_KEY is set!"

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

        try:
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=self.get_system_prompt(),
                messages=messages
            )

            sarah_response = response.content[0].text

            # Update conversation history
            conversation_history.append({"role": "user", "content": user_message})
            conversation_history.append({"role": "assistant", "content": sarah_response})

            # Keep history manageable
            if len(conversation_history) > MAX_HISTORY * 2:
                conversation_history.pop(0)
                conversation_history.pop(0)

            return sarah_response

        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            return f"Oops! I ran into an issue: {str(e)}. Let me try to help anyway - what did you want to know? 🌸"


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


@app.websocket("/chat")
async def chat_endpoint(websocket: WebSocket):
    """WebSocket endpoint for chat"""
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
                logger.info(f"💬 User: {user_message}")

                # Generate Sarah's response
                sarah_response = await sarah_instance.generate_response(user_message)
                logger.info(f"💬 Sarah: {sarah_response[:100]}...")

                # Send response back
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
    """WebSocket endpoint for screen streaming (future feature)"""
    await websocket.accept()

    logger.info(f"🎥 Screen stream client connected")

    try:
        await websocket.send_text("CONNECTED:Sarah's Live Screen 🌸")

        # Keep connection alive
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        logger.info(f"🎥 Screen stream client disconnected")


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
    global sarah_instance, conversations_db

    logger.info("=" * 60)
    logger.info("🚀 BLOOM AI AGENT - STARTING UP")
    logger.info("=" * 60)

    # Initialize conversations database
    conversations_db = ConversationsDB()
    logger.info("✅ Conversations database initialized")

    sarah_instance = Sarah()
    sarah_instance.create_identity()

    logger.info("🌸 Sarah Rodriguez is online!")
    logger.info("💬 Chat WebSocket available at: /chat")
    logger.info("🎥 Screen WebSocket available at: /screen")
    logger.info("📚 Conversation API available at: /api/conversations")

    # Start background routine
    asyncio.create_task(run_daily_routine())


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
