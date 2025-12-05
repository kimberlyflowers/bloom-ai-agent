"""
BLOOM AI Agent - Main FastAPI Server
Runs Sarah Rodriguez as an autonomous AI agent employee
FIXED: Proper imports matching original structure
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== SARAH AGENT CLASS ====================

class SarahAgent:
    """Global Sarah instance with lazy imports"""
    
    def __init__(self):
        self.identity_manager = None
        self.browser = None
        self.chat_handler = None
        self.screen_streamer = None
        self.initialized = False

    async def initialize(self):
        """Initialize Sarah's core systems"""
        if self.initialized:
            logger.warning("⚠️ Sarah already initialized")
            return

        logger.info("🌸 Initializing Sarah Rodriguez...")

        # Get API key
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("❌ ANTHROPIC_API_KEY not set!")

        # 1. Initialize identity manager (lazy import)
        try:
            from src.identity_persistence import IdentityManager
            self.identity_manager = IdentityManager()
            logger.info("✅ Identity manager created")
        except ImportError:
            logger.warning("⚠️ Identity manager not available")
            self.identity_manager = None

        # 2. Initialize browser (lazy import)
        try:
            from src.sarah_browser import SarahBrowser
            self.browser = SarahBrowser(headless=True)
            logger.info("✅ Browser initialized")
        except ImportError as e:
            logger.error(f"❌ Browser import failed: {e}")
            self.browser = None

        # 3. Initialize chat handler (lazy import)
        try:
            from chat_server import SarahChatHandler
            self.chat_handler = SarahChatHandler(
                api_key=api_key,
                browser=self.browser
            )
            logger.info("✅ Chat handler initialized")
        except ImportError as e:
            logger.error(f"❌ Chat handler import failed: {e}")
            self.chat_handler = None

        # 4. Initialize screen streamer (lazy import)
        try:
            from src.live_screen_stream import LiveScreenStreamer
            self.screen_streamer = LiveScreenStreamer()
            logger.info("✅ Screen streamer initialized")
        except ImportError:
            logger.warning("⚠️ Screen streamer not available")
            self.screen_streamer = None

        logger.info("🚀 Starting Sarah's services...")

        # Start browser
        if self.browser and hasattr(self.browser, 'start'):
            try:
                await self.browser.start()
                logger.info("✅ Browser started")
            except Exception as e:
                logger.error(f"❌ Browser start failed: {e}")

        # Start screen streamer
        if self.screen_streamer and self.browser and hasattr(self.browser, 'page'):
            try:
                self.screen_streamer.start(self.browser.page)
                logger.info("✅ Screen streamer started")
            except Exception as e:
                logger.error(f"❌ Screen streamer start failed: {e}")

        # Load Sarah's identity
        if self.identity_manager:
            try:
                sarah_identity = self.identity_manager.get_agent_identity("sarah_001")
                logger.info("✅ Sarah's identity ready")
                logger.info(f"   Name: {sarah_identity.name}")
                logger.info(f"   Role: {sarah_identity.role}")
                logger.info(f"   Location: {sarah_identity.location}")
            except Exception as e:
                logger.warning(f"⚠️ Could not load identity: {e}")

        self.initialized = True
        logger.info("✅ Sarah is online!")

    async def shutdown(self):
        """Clean shutdown of Sarah's systems"""
        logger.info("🌙 Shutting down Sarah...")

        if self.screen_streamer and hasattr(self.screen_streamer, 'stop'):
            try:
                self.screen_streamer.stop()
                logger.info("✅ Screen streamer stopped")
            except Exception as e:
                logger.error(f"❌ Screen streamer stop failed: {e}")

        if self.browser and hasattr(self.browser, 'close'):
            try:
                await self.browser.close()
                logger.info("✅ Browser closed")
            except Exception as e:
                logger.error(f"❌ Browser close failed: {e}")

        self.initialized = False
        logger.info("✅ Sarah shutdown complete")


# Global Sarah instance
sarah = SarahAgent()


# ==================== FASTAPI LIFESPAN ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan manager
    Handles startup and shutdown
    """
    # Startup
    logger.info("============================================================")
    logger.info("🚀 BLOOM AI AGENT - STARTING UP")
    logger.info("============================================================")

    try:
        await sarah.initialize()
        logger.info("✅ Sarah initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Sarah: {e}")
        logger.exception(e)
        raise

    yield

    # Shutdown
    logger.info("============================================================")
    logger.info("🌙 BLOOM AI AGENT - SHUTTING DOWN")
    logger.info("============================================================")

    try:
        await sarah.shutdown()
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")
        logger.exception(e)


# ==================== FASTAPI APP ====================

app = FastAPI(
    title="BLOOM AI Agent",
    description="Sarah Rodriguez - Autonomous AI Agent Employee",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== HEALTH ENDPOINTS ====================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "BLOOM AI Agent",
        "agent": "Sarah Rodriguez",
        "status": "online" if sarah.initialized else "initializing",
        "endpoints": {
            "health": "/health",
            "chat": "ws://[host]/chat",
            "screen": "ws://[host]/screen"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    if not sarah.initialized:
        return JSONResponse(
            status_code=503,
            content={
                "status": "initializing",
                "message": "Sarah is still starting up..."
            }
        )

    browser_running = (
        sarah.browser and 
        hasattr(sarah.browser, 'is_running') and 
        sarah.browser.is_running
    )

    return {
        "status": "healthy",
        "agent": "Sarah Rodriguez",
        "systems": {
            "browser": "running" if browser_running else "stopped",
            "chat": "ready" if sarah.chat_handler else "not initialized",
            "screen_stream": "active" if sarah.screen_streamer else "not initialized"
        }
    }


# ==================== WEBSOCKET ENDPOINTS ====================

@app.websocket("/chat")
async def chat_websocket(websocket: WebSocket):
    """
    Chat WebSocket - Direct FastAPI handling
    No proxy, no double accept, just works!
    """
    if not sarah.initialized or not sarah.chat_handler:
        await websocket.accept()
        await websocket.send_json({
            'type': 'error',
            'message': 'Sarah is still initializing. Please wait a moment and try again.'
        })
        await websocket.close()
        return

    try:
        # Let Sarah's chat handler handle this connection
        await sarah.chat_handler.handle_websocket(websocket)
    except WebSocketDisconnect:
        logger.info("💬 Client disconnected from chat")
    except Exception as e:
        logger.error(f"❌ Chat WebSocket error: {e}")
        logger.exception(e)


@app.websocket("/screen")
async def screen_websocket(websocket: WebSocket):
    """
    Screen streaming WebSocket
    Watch Sarah work in real-time!
    """
    if not sarah.initialized or not sarah.screen_streamer:
        await websocket.accept()
        await websocket.send_json({
            'type': 'error',
            'message': 'Screen streaming not available yet'
        })
        await websocket.close()
        return

    await websocket.accept()
    logger.info("🎥 New screen connection")

    try:
        # Add client to streamer (FIXED: use connected_clients not clients!)
        sarah.screen_streamer.connected_clients.add(websocket)

        # Keep connection alive
        while True:
            try:
                # Wait for client messages (mostly pings)
                message = await websocket.receive_text()
                
                # Echo back pings
                if message == "ping":
                    await websocket.send_text("pong")
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.debug(f"Screen WebSocket receive error: {e}")
                break

    except Exception as e:
        logger.error(f"❌ Screen WebSocket error: {e}")
    finally:
        # Remove client from streamer (FIXED: use connected_clients not clients!)
        if websocket in sarah.screen_streamer.connected_clients:
            sarah.screen_streamer.connected_clients.remove(websocket)
        logger.info("🎥 Screen client disconnected")


# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or default to 8080
    port = int(os.environ.get('PORT', 8080))
    
    logger.info("============================================================")
    logger.info(f"🚀 Starting server on port {port}")
    logger.info(f"   Chat WebSocket: ws://localhost:{port}/chat")
    logger.info(f"   Screen WebSocket: ws://localhost:{port}/screen")
    logger.info(f"   Health check: http://localhost:{port}/health")
    logger.info("============================================================")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
