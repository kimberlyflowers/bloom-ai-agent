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
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app for Railway
app = FastAPI(title="BLOOM AI Agent - Sarah Rodriguez")

# ==================== GLOBAL INSTANCES ====================
sarah_instance = None
chat_server_port = 8766    # INTERNAL port for chat
screen_server_port = 8767  # INTERNAL port for screen

# ==================== PROXY FUNCTIONS ====================

async def proxy_to_chat_server(client_ws: WebSocket):
    """Proxy WebSocket to CHAT server (port 8766)"""
    await client_ws.accept()
    
    try:
        async with websockets.connect(f"ws://localhost:{chat_server_port}") as server_ws:
            logger.info(f"💬 Chat proxy → {chat_server_port}")
            
            async def forward_client_to_server():
                try:
                    while True:
                        data = await client_ws.receive_text()
                        await server_ws.send(data)
                except:
                    pass
            
            async def forward_server_to_client():
                try:
                    while True:
                        data = await server_ws.recv()
                        await client_ws.send_text(data)
                except:
                    pass
            
            await asyncio.gather(
                forward_client_to_server(),
                forward_server_to_client(),
                return_exceptions=True
            )
    except ConnectionRefusedError:
        logger.error(f"❌ Chat server offline")
        await client_ws.close()
    except Exception as e:
        logger.error(f"❌ Chat proxy error: {e}")
        await client_ws.close()

async def proxy_to_screen_server(client_ws: WebSocket):
    """Proxy WebSocket to SCREEN server (port 8767)"""
    await client_ws.accept()
    
    try:
        async with websockets.connect(f"ws://localhost:{screen_server_port}") as server_ws:
            logger.info(f"🎥 Screen proxy → {screen_server_port}")
            
            # Send start command to screen server
            await server_ws.send(json.dumps({
                "type": "start_stream",
                "message": "Start browser streaming"
            }))
            
            async def forward_client_to_server():
                try:
                    while True:
                        data = await client_ws.receive_text()
                        await server_ws.send(data)
                except:
                    pass
            
            async def forward_server_to_client():
                try:
                    while True:
                        data = await server_ws.recv()
                        await client_ws.send_text(data)
                except:
                    pass
            
            await asyncio.gather(
                forward_client_to_server(),
                forward_server_to_client(),
                return_exceptions=True
            )
    except ConnectionRefusedError:
        logger.error(f"❌ Screen server offline")
        await client_ws.close()
    except Exception as e:
        logger.error(f"❌ Screen proxy error: {e}")
        await client_ws.close()

# ==================== WEBSOCKET ENDPOINTS ====================

@app.websocket("/")
@app.websocket("/chat")
async def websocket_chat(websocket: WebSocket):
    """Route / and /chat to chat server"""
    await proxy_to_chat_server(websocket)

@app.websocket("/screen")
async def websocket_screen(websocket: WebSocket):
    """Route /screen to screen server"""
    await proxy_to_screen_server(websocket)

# ==================== SARAH CLASS ====================

class Sarah:
    """Sarah Rodriguez - Digital Employee at BLOOM"""
    
    def __init__(self):
        self.agent_id = "sarah_001"
        logger.info("🌸 Initializing Sarah Rodriguez...")
        
        # Lazy imports to avoid circular issues
        try:
            from src.identity_persistence import IdentityManager, Backstory, PersonalityTraits, WritingStyle
            from src.relationship_management import RelationshipManager
            from src.ethical_framework import EthicalFramework
            from src.chat_server import SarahChatServer
            from src.sarah_browser import SarahBrowser
            
            self.identity = IdentityManager()
            self.relationships = RelationshipManager()
            self.ethics = EthicalFramework()
            
            # Get Railway's single public port
            railway_port = os.getenv("PORT", "8080")
            logger.info(f"🚂 Railway Public Port: {railway_port}")
            logger.info(f"   Internal Chat Port: {chat_server_port}")
            logger.info(f"   Internal Screen Port: {screen_server_port}")
            
            # Initialize browser
            self.browser = SarahBrowser(headless=True)
            logger.info("✅ Browser initialized")
            
            # Initialize chat server
            anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
            if anthropic_api_key:
                self.chat_server = SarahChatServer(
                    anthropic_api_key=anthropic_api_key,
                    port=chat_server_port,  # INTERNAL port
                    identity_manager=self.identity,
                    browser=self.browser
                )
                logger.info(f"✅ Chat server ready on port {chat_server_port}")
            else:
                logger.error("❌ No ANTHROPIC_API_KEY - chat disabled")
                self.chat_server = None
                
        except ImportError as e:
            logger.error(f"❌ Import error: {e}")
            self.chat_server = None
            self.browser = None
    
    def create_identity(self):
        """Create Sarah's identity"""
        try:
            # Check if identity exists
            if self.agent_id in self.identity.identities:
                logger.info("✅ Identity already exists")
                return
            
            from src.identity_persistence import Backstory, PersonalityTraits, WritingStyle
            
            backstory = Backstory(
                education=["B.S. Marketing - Arizona State University (2019)"],
                work_history=[{
                    "company": "BLOOM", 
                    "role": "Growth & Community Lead",
                    "years": "2021-present"
                }],
                hometown="Phoenix, Arizona",
                core_values=["Authenticity over perfection"]
            )
            
            personality = PersonalityTraits(
                openness=0.85, conscientiousness=0.75,
                extraversion=0.70, agreeableness=0.80, neuroticism=0.30
            )
            
            writing_style = WritingStyle(
                common_phrases=["I totally get that!", "Here's what I've learned..."],
                tone="warm, enthusiastic, helpful",
                uses_emojis=True,
                preferred_emojis=["✨", "🎯", "💡", "🚀", "☕"]
            )
            
            self.identity.create_identity(
                agent_id=self.agent_id,
                first_name="Sarah",
                last_name="Rodriguez",
                job_title="Growth & Community Lead",
                company="BLOOM",
                location="Phoenix, Arizona",
                backstory=backstory,
                writing_style=writing_style,
                personality=personality
            )
            
            logger.info("✅ Sarah's identity created!")
            
        except Exception as e:
            logger.error(f"❌ Identity creation failed: {e}")
    
    async def start_screen_stream_server(self):
        """Start screen streaming WebSocket server"""
        if not self.browser:
            logger.error("❌ No browser - cannot start screen stream")
            return False
        
        try:
            # Check if browser has screen streamer
            if not hasattr(self.browser, 'streamer'):
                logger.error("❌ Browser has no streamer attribute")
                return False
            
            # Start screen streaming server
            await self.browser.streamer.start_server(port=screen_server_port)
            logger.info(f"🎥 Screen stream server started on port {screen_server_port}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start screen server: {e}")
            return False
    
    async def check_youtube_ip_status(self):
        """Check YouTube IP status"""
        try:
            if not self.browser:
                return "No browser"
            
            await self.browser.navigate("https://www.youtube.com")
            await asyncio.sleep(2)
            title = await self.browser.page.title()
            
            if "Sign in" in title or "Log in" in title:
                return "⚠️ FLAGGED - Login required"
            elif "YouTube" in title:
                return "✅ CLEAN - Normal access"
            else:
                return f"❓ UNKNOWN - {title}"
                
        except Exception as e:
            return f"ERROR: {str(e)}"

# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_event():
    global sarah_instance
    
    logger.info("=" * 60)
    logger.info("🚀 BLOOM AI AGENT - STARTING UP")
    logger.info("=" * 60)
    
    sarah_instance = Sarah()
    sarah_instance.create_identity()
    
    # Start browser
    if sarah_instance.browser:
        browser_started = await sarah_instance.browser.start()
        if browser_started:
            logger.info("✅ Browser started")
            
            # Start screen streaming server
            await sarah_instance.start_screen_stream_server()
            
            # Check YouTube
            youtube_status = await sarah_instance.check_youtube_ip_status()
            logger.info(f"📊 YouTube: {youtube_status}")
        else:
            logger.error("❌ Browser failed to start")
    
    # Start chat server
    if sarah_instance.chat_server:
        asyncio.create_task(sarah_instance.chat_server.start_server())
        logger.info("💬 Chat server started")
    
    logger.info("✅ Sarah is online!")
    logger.info("   💬 Chat: /chat or /")
    logger.info("   🎥 Screen: /screen")

# ==================== REST ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "status": "online",
        "agent": "Sarah Rodriguez",
        "role": "Growth & Community Lead at BLOOM",
        "endpoints": {
            "chat": "/chat (WebSocket)",
            "screen": "/screen (WebSocket)",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    global sarah_instance
    if not sarah_instance:
        return JSONResponse(
            status_code=503,
            content={"status": "starting"}
        )
    
    return {
        "status": "healthy",
        "chat": "online" if sarah_instance.chat_server else "offline",
        "screen": "online" if sarah_instance.browser else "offline",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)