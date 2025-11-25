"""
Unified WebSocket Server for Sarah
Handles both chat and screen streaming on a single port with path-based routing
"""

import asyncio
import logging
from typing import Set
import websockets
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger(__name__)


class UnifiedWebSocketServer:
    """
    Single WebSocket server that routes to chat or screen streaming based on path

    Routes:
    - /chat -> Chat server
    - /screen -> Screen streaming
    """

    def __init__(self, port: int, chat_server, screen_streamer):
        """
        Initialize unified server

        Args:
            port: Port to listen on (Railway's PORT env var)
            chat_server: SarahChatServer instance
            screen_streamer: PlaywrightScreenStreamer instance
        """
        self.port = port
        self.chat_server = chat_server
        self.screen_streamer = screen_streamer
        self.server = None

    async def start(self):
        """Start the unified WebSocket server"""
        logger.info(f"🚀 Starting unified WebSocket server on port {self.port}...")
        logger.info(f"   📍 Routes: /chat and /screen")

        self.server = await websockets.serve(
            self.handle_connection,
            "0.0.0.0",
            self.port,
            # Low-latency configuration for real-time chat
            ping_interval=5,      # Send keepalive ping every 5 seconds (instead of 20)
            ping_timeout=10,      # Wait 10 seconds for pong (instead of 20)
            compression=None,     # Disable compression for lower latency
            max_size=10485760     # 10MB max message size (default is 1MB)
        )

        logger.info(f"✅ Unified server running on ws://0.0.0.0:{self.port}")
        logger.info(f"   💬 Chat: ws://0.0.0.0:{self.port}/chat")
        logger.info(f"   🎥 Screen: ws://0.0.0.0:{self.port}/screen")

    async def stop(self):
        """Stop the server"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("🔴 Unified server stopped")

    async def handle_connection(self, websocket, path):
        """
        Route incoming connections based on path

        Args:
            websocket: WebSocket connection
            path: Request path from websockets.serve()
        """
        # Use path parameter from websockets.serve()
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"🔌 New connection from {client_id} to path: {path}")

        try:
            if path == "/chat" or path == "/chat/":
                # Route to chat server
                logger.info(f"   → Routing to chat server")
                await self.chat_server.handle_client(websocket)

            elif path == "/screen" or path == "/screen/":
                # Route to screen streamer
                logger.info(f"   → Routing to screen streamer")
                await self.screen_streamer.handle_client(websocket)

            else:
                # Unknown path
                logger.warning(f"   ⚠️ Unknown path: {path}")
                await websocket.send(f"Error: Unknown path '{path}'. Use /chat or /screen")
                await websocket.close()

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 Client disconnected from {path}: {client_id}")
        except Exception as e:
            logger.error(f"❌ Error handling connection to {path}: {e}")
            logger.exception(e)
