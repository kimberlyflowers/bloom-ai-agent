"""
Sarah Rodriguez - AI Agent Employee
Main entry point for Railway deployment
"""

import os
import asyncio
import logging
from datetime import datetime
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
import websockets

# Import Sarah's core systems
from src.identity_persistence import IdentityManager, Backstory, PersonalityTraits, WritingStyle
from src.relationship_management import RelationshipManager
from src.ethical_framework import EthicalFramework
from src.chat_server import SarahChatServer
from src.visual_capabilities import BrowserAgent
from src.autonomous_executor import AutonomousExecutor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app for Railway
app = FastAPI(title="BLOOM AI Agent - Sarah Rodriguez")

async def proxy_to_chat_server(client_ws: WebSocket):
    """
    Proxy WebSocket connection to Sarah's real chat server on port 8766
    All paths connect to Sarah's root endpoint
    """
    await client_ws.accept()
    
    # ALWAYS connect to root - Sarah's server doesn't handle sub-paths
    server_url = "ws://localhost:8766"
    
    try:
        async with websockets.connect(server_url) as server_ws:
            logger.info(f"✅ Proxy connected to chat server")
            
            # Forward client messages to server
            async def client_to_server():
                try:
                    while True:
                        data = await client_ws.receive_text()
                        await server_ws.send(data)
                except Exception as e:
                    logger.debug(f"Client→Server closed: {e}")
            
            # Forward server messages to client
            async def server_to_client():
                try:
                    while True:
                        data = await server_ws.recv()
                        await client_ws.send_text(data)
                except Exception as e:
                    logger.debug(f"Server→Client closed: {e}")
            
            # Run both directions concurrently
            await asyncio.gather(
                client_to_server(),
                server_to_client(),
                return_exceptions=True
            )
            
    except ConnectionRefusedError:
        logger.error("❌ Chat server not available on port 8766")
        try:
            await client_ws.send_json({
                "error": "Chat server offline",
                "status": "unavailable"
            })
        except:
            pass
        await client_ws.close()
    except Exception as e:
        logger.error(f"❌ WebSocket proxy error: {e}")
        try:
            await client_ws.close()
        except:
            pass

# ==================== WEBSOCKET PROXY ENDPOINTS ====================

@app.websocket("/")
async def websocket_root(websocket: WebSocket):
    """Proxy root WebSocket to chat server"""
    await proxy_to_chat_server(websocket)

@app.websocket("/screen")
async def websocket_screen(websocket: WebSocket):
    """Proxy /screen WebSocket to chat server"""
    await proxy_to_chat_server(websocket)

@app.websocket("/chat")
async def websocket_chat(websocket: WebSocket):
    """Proxy /chat WebSocket to chat server"""
    await proxy_to_chat_server(websocket)


class Sarah:
    """Sarah Rodriguez - Digital Employee at BLOOM"""

    def __init__(self):
        self.agent_id = "sarah_001"

        # Initialize systems (they use in-memory storage for now)
        logger.info("🌸 Initializing Sarah Rodriguez...")

        self.identity = IdentityManager()
        self.relationships = RelationshipManager()
        self.ethics = EthicalFramework()

        # Initialize browser agent for autonomous execution
        logger.info("🌐 Initializing browser agent...")
        self.browser_agent = BrowserAgent(
            agent_id=self.agent_id,
            headless=False  # Show browser for debugging
        )
        # Start the browser
        browser_started = self.browser_agent.start()
        if browser_started:
            logger.info("✅ Browser agent started")
        else:
            logger.warning("⚠️ Browser agent failed to start")
            self.browser_agent = None

        # Initialize chat server with browser agent
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_api_key:
            self.chat_server = SarahChatServer(
                anthropic_api_key=anthropic_api_key,
                port=8766,
                identity_manager=self.identity,
                browser_agent=self.browser_agent  # Pass browser agent to chat server
            )
            logger.info("✅ Chat server initialized")
        else:
            logger.warning("⚠️ No ANTHROPIC_API_KEY - chat will not be available")
            self.chat_server = None

        logger.info("✅ Sarah is fully initialized!")

    def create_identity(self):
        """Create Sarah's identity if it doesn't exist"""

        # Check if identity already exists
        if self.agent_id in self.identity.identities:
            logger.info("Sarah's identity already exists")
            return

        logger.info("Creating Sarah's identity...")

        # Build backstory first
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
            openness=0.85,  # Creative, curious
            conscientiousness=0.75,  # Organized, reliable
            extraversion=0.70,  # Friendly, enthusiastic
            agreeableness=0.80,  # Helpful, empathetic
            neuroticism=0.30  # Calm, confident
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

        # Create Sarah's complete identity with all details
        identity_id = self.identity.create_identity(
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
        logger.info(f"   Name: Sarah Rodriguez")
        logger.info(f"   Role: Growth & Community Lead at BLOOM")
        logger.info(f"   Location: Phoenix, Arizona")
        logger.info(f"   Specialization: TikTok growth & UGC creation")

    async def check_email(self):
        """Check email and respond (placeholder for now)"""
        logger.info("📧 Checking email...")
        # TODO: Implement Gmail integration
        return []

    async def daily_routine(self):
        """Sarah's daily routine - runs every 5 minutes"""
        logger.info("🌅 Starting daily routine...")

        # 1. Check email
        await self.check_email()

        # 2. Check relationships
        total_relationships = len(self.relationships.relationships)
        logger.info(f"💝 Managing {total_relationships} relationships")

        # 3. Log activity
        logger.info("✅ Daily routine complete!")

# Global Sarah instance
sarah_instance = None

@app.on_event("startup")
async def startup_event():
    """Initialize Sarah on startup"""
    global sarah_instance

    logger.info("=" * 60)
    logger.info("🚀 BLOOM AI AGENT - STARTING UP")
    logger.info("=" * 60)

    sarah_instance = Sarah()
    sarah_instance.create_identity()

    # Start chat server in background
    if sarah_instance.chat_server:
        asyncio.create_task(sarah_instance.chat_server.start_server())
        logger.info("💬 Chat server started - ready for conversations!")

    # Start daily routine in background
    asyncio.create_task(run_sarah_routine())

    logger.info("✅ Sarah is fully online and ready!")

async def run_sarah_routine():
    """Run Sarah's daily routine in background"""
    global sarah_instance

    while True:
        try:
            await sarah_instance.daily_routine()

            # Sleep for 5 minutes (not 1 hour!)
            logger.info("😴 Sleeping for 5 minutes...")
            await asyncio.sleep(300)  # 5 minutes = 300 seconds

        except Exception as e:
            logger.error(f"❌ Error in daily routine: {e}")
            logger.exception(e)
            # Sleep 1 minute before retry
            await asyncio.sleep(60)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "online",
        "agent": "Sarah Rodriguez",
        "role": "Growth & Community Lead at BLOOM",
        "message": "Hi! I'm Sarah 🌸 I'm online and working!",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    global sarah_instance

    if sarah_instance is None:
        return JSONResponse(
            status_code=503,
            content={
                "status": "starting",
                "message": "Sarah is initializing..."
            }
        )

    return {
        "status": "healthy",
        "agent_id": sarah_instance.agent_id,
        "systems": {
            "identity": "online",
            "relationships": "online",
            "ethics": "online",
            "chat_server": "online" if sarah_instance.chat_server else "offline"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status")
async def get_status():
    """Get detailed status"""
    global sarah_instance

    if sarah_instance is None:
        return JSONResponse(
            status_code=503,
            content={
                "status": "starting",
                "message": "Sarah is initializing..."
            }
        )

    total_relationships = len(sarah_instance.relationships.relationships)

    return {
        "status": "operational",
        "agent": {
            "id": sarah_instance.agent_id,
            "name": "Sarah Rodriguez",
            "role": "Growth & Community Lead"
        },
        "stats": {
            "relationships": total_relationships,
            "identity_loaded": sarah_instance.agent_id in sarah_instance.identity.identities
        },
        "timestamp": datetime.now().isoformat()
    }

async def main():
    """Entry point for local development"""
    logger.info("=" * 60)
    logger.info("🚀 BLOOM AI AGENT - STARTING UP (Local Mode)")
    logger.info("=" * 60)

    sarah = Sarah()
    await sarah.run()

if __name__ == "__main__":
    # Run Sarah in local mode (asyncio)
    asyncio.run(main())
