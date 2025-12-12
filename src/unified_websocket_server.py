"""
Unified WebSocket Server for Sarah
Handles both chat and screen streaming on a single port with path-based routing

EXTENDED: Now includes command center WebSocket and HTTP file serving
NO FASTAPI - Pure WebSocket + HTTP via websockets library
"""

import asyncio
import logging
import os
from typing import Set, Optional
from pathlib import Path
import websockets
from websockets.server import WebSocketServerProtocol
from websockets.legacy.server import HTTPResponse

logger = logging.getLogger(__name__)


class UnifiedWebSocketServer:
    """
    Single WebSocket server that routes to chat or screen streaming based on path

    Routes:
    - /chat -> Chat server
    - /screen -> Screen streaming
    - /command -> Command center (NEW!)
    - /videos/{filename} -> HTTP file serving (NEW!)
    """

    def __init__(self, port: int, chat_server, screen_streamer, command_center_handler=None):
        """
        Initialize unified server

        Args:
            port: Port to listen on (Railway's PORT env var)
            chat_server: SarahChatServer instance
            screen_streamer: PlaywrightScreenStreamer instance
            command_center_handler: CommandCenterHandler instance (optional)
        """
        self.port = port
        self.chat_server = chat_server
        self.screen_streamer = screen_streamer
        self.command_center_handler = command_center_handler
        self.server = None

    async def start(self):
        """Start the unified WebSocket server"""
        logger.info(f"🚀 Starting unified WebSocket server on port {self.port}...")
        logger.info(f"   📍 Routes: /chat, /screen, /command")

        self.server = await websockets.serve(
            self.handle_connection,
            "0.0.0.0",
            self.port,
            # Low-latency configuration for real-time chat
            ping_interval=5,      # Send keepalive ping every 5 seconds (instead of 20)
            ping_timeout=10,      # Wait 10 seconds for pong (instead of 20)
            compression=None,     # Disable compression for lower latency
            max_size=10485760     # 10MB max message size (default is 1MB)
            # NOTE: HTTP video serving removed - was breaking WebSocket connections
            # Will implement video serving separately (not via websockets library)
        )

        logger.info(f"✅ Unified server running on ws://0.0.0.0:{self.port}")
        logger.info(f"   💬 Chat: ws://0.0.0.0:{self.port}/chat")
        logger.info(f"   🎥 Screen: ws://0.0.0.0:{self.port}/screen")
        if self.command_center_handler:
            logger.info(f"   🎛️  Command: ws://0.0.0.0:{self.port}/command")

    async def stop(self):
        """Stop the server"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("🔴 Unified server stopped")

    async def process_http_request(self, path: str, request_headers):
        """
        Handle HTTP requests for file serving
        NO FASTAPI - uses websockets library's HTTP support

        Args:
            path: Request path
            request_headers: HTTP headers

        Returns:
            HTTPResponse or None (None = upgrade to WebSocket)
        """
        # Only handle /videos/* paths, let WebSocket handle others
        if not path.startswith("/videos/"):
            return None  # Not an HTTP request, proceed with WebSocket

        logger.info(f"📹 HTTP request: {path}")

        try:
            # Extract filename from path
            filename = path.replace("/videos/", "")

            # Security: Prevent directory traversal
            if ".." in filename or filename.startswith("/"):
                logger.warning(f"⚠️ Invalid filename: {filename}")
                return HTTPResponse(403, [], b"Forbidden")

            # Check multiple possible directories
            video_paths = [
                Path("videos") / filename,
                Path("data/videos") / filename,
                Path(f"/tmp/videos/{filename}")
            ]

            video_path = None
            for vp in video_paths:
                if vp.exists():
                    video_path = vp
                    break

            if not video_path or not video_path.exists():
                logger.warning(f"⚠️ Video not found: {filename}")
                return HTTPResponse(404, [], b"Video not found")

            # Read video file
            with open(video_path, "rb") as f:
                video_data = f.read()

            # Determine content type
            content_type = "video/mp4"
            if filename.endswith(".webm"):
                content_type = "video/webm"
            elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
                content_type = "image/jpeg"
            elif filename.endswith(".png"):
                content_type = "image/png"

            logger.info(f"✅ Serving video: {filename} ({len(video_data)} bytes)")

            # Return HTTP response
            return HTTPResponse(
                200,
                [
                    ("Content-Type", content_type),
                    ("Content-Length", str(len(video_data))),
                    ("Access-Control-Allow-Origin", "*")  # Allow CORS
                ],
                video_data
            )

        except Exception as e:
            logger.error(f"❌ Error serving video: {e}")
            return HTTPResponse(500, [], b"Internal server error")

    async def handle_connection(self, websocket):
        """
        Route incoming connections based on path

        Args:
            websocket: WebSocket connection (has request.path attribute)
        """
        # Get path from the websocket request
        path = websocket.request.path
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

            elif path == "/command" or path == "/command/":
                # Route to command center (NEW!)
                if self.command_center_handler:
                    logger.info(f"   → Routing to command center")
                    await self.command_center_handler.handle_client(websocket)
                else:
                    logger.warning(f"   ⚠️ Command center not initialized")
                    await websocket.send("Error: Command center not available")
                    await websocket.close()

            else:
                # Unknown path
                logger.warning(f"   ⚠️ Unknown path: {path}")
                await websocket.send(f"Error: Unknown path '{path}'. Use /chat, /screen, or /command")
                await websocket.close()

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 Client disconnected from {path}: {client_id}")
        except Exception as e:
            logger.error(f"❌ Error handling connection to {path}: {e}")
            logger.exception(e)
