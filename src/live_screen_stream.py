"""
Live Screen Streaming - Watch Sarah Work in Real-Time!
Streams Sarah's browser screen to the dashboard via WebSocket
"""

import asyncio
import logging
import base64
import io
from typing import Optional, Set
from PIL import ImageGrab, Image
import websockets
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger(__name__)


class LiveScreenStreamer:
    """
    Streams Sarah's screen to the dashboard in real-time!

    You can literally watch her work - typing, clicking, browsing!
    """

    def __init__(self, port: int = 8765, fps: int = 2):
        """
        Initialize live screen streamer

        Args:
            port: WebSocket server port
            fps: Frames per second to stream (2-5 recommended for browser performance)
        """
        self.port = port
        self.fps = fps
        self.frame_delay = 1.0 / fps
        self.connected_clients: Set[WebSocketServerProtocol] = set()
        self.streaming = False
        self.server = None

    async def start_server(self):
        """Start WebSocket server for screen streaming"""
        logger.info(f"🎥 Starting live screen stream server on port {self.port}...")

        try:
            self.server = await websockets.serve(
                self.handle_client,
                "0.0.0.0",
                self.port
            )

            logger.info(f"✅ Live screen stream server running!")
            logger.info(f"   Connect dashboard to: ws://localhost:{self.port}")

            # Keep server running
            await asyncio.Future()  # Run forever

        except Exception as e:
            logger.error(f"❌ Error starting screen stream server: {e}")

    async def handle_client(self, websocket: WebSocketServerProtocol):
        """Handle new dashboard connection"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"

        logger.info(f"📺 Dashboard connected: {client_id}")
        self.connected_clients.add(websocket)

        try:
            # Send welcome message
            await websocket.send(f"CONNECTED:Live stream from Sarah's screen!")

            # Keep connection alive
            async for message in websocket:
                # Handle any commands from dashboard
                if message == "PING":
                    await websocket.send("PONG")

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"📺 Dashboard disconnected: {client_id}")
        finally:
            self.connected_clients.discard(websocket)

    async def capture_and_stream_screen(self, display_number: int = 99):
        """
        Capture screenshots and stream to all connected dashboards

        Args:
            display_number: Virtual display number (e.g., :99 for DISPLAY=:99)
        """
        logger.info(f"📸 Starting screen capture (Display :{display_number}, {self.fps} FPS)...")
        self.streaming = True

        frame_count = 0

        while self.streaming:
            try:
                if not self.connected_clients:
                    # No one watching, save resources
                    await asyncio.sleep(1)
                    continue

                # Capture screenshot
                # Note: In Railway/Docker, we'll use a different method
                # For now, this is the structure
                screenshot = await self.capture_screenshot(display_number)

                if screenshot:
                    # Broadcast to all connected dashboards
                    await self.broadcast_frame(screenshot)
                    frame_count += 1

                    if frame_count % (self.fps * 10) == 0:  # Log every 10 seconds
                        logger.info(f"📺 Streaming... ({len(self.connected_clients)} viewers, {frame_count} frames sent)")

                # Wait for next frame
                await asyncio.sleep(self.frame_delay)

            except Exception as e:
                logger.error(f"❌ Error capturing/streaming screen: {e}")
                await asyncio.sleep(1)

    async def capture_screenshot(self, display_number: int) -> Optional[str]:
        """
        Capture screenshot from virtual display

        Returns:
            Base64-encoded JPEG image, or None if failed
        """
        try:
            # This will be implemented differently in Docker/Railway
            # Using Playwright's screenshot capability instead
            # For now, return a placeholder

            # In production, we'll capture from the Playwright browser directly
            # playwright_page.screenshot() -> base64

            return None  # Placeholder

        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return None

    async def broadcast_frame(self, frame_data: str):
        """Broadcast frame to all connected dashboards"""
        if not self.connected_clients:
            return

        # Send to all clients
        disconnected = set()

        for client in self.connected_clients:
            try:
                await client.send(f"FRAME:{frame_data}")
            except:
                disconnected.add(client)

        # Remove disconnected clients
        self.connected_clients -= disconnected

    def stop_streaming(self):
        """Stop screen streaming"""
        logger.info("🔴 Stopping screen stream...")
        self.streaming = False


class PlaywrightScreenStreamer:
    """
    Better approach: Stream Playwright browser screenshots directly!
    No need for virtual display complexity
    """

    def __init__(self, port: int = 8765, fps: int = 2):
        self.port = port
        self.fps = fps
        self.frame_delay = 1.0 / fps
        self.connected_clients: Set[WebSocketServerProtocol] = set()
        self.streaming = False
        self.browser_page = None
        self.server = None

    async def start_server(self):
        """Start WebSocket server"""
        logger.info(f"🎥 Starting Playwright screen stream on port {self.port}...")

        self.server = await websockets.serve(
            self.handle_client,
            "0.0.0.0",
            self.port
        )

        logger.info(f"✅ Screen stream server ready!")
        logger.info(f"   Dashboard can connect to: ws://[railway-url]:{self.port}")

    async def handle_client(self, websocket: WebSocketServerProtocol):
        """Handle dashboard connection"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"📺 Dashboard connected: {client_id}")

        self.connected_clients.add(websocket)

        try:
            await websocket.send("CONNECTED:Sarah's Live Screen 🌸")

            async for message in websocket:
                if message == "PING":
                    await websocket.send("PONG")
                elif message == "REQUEST_FRAME":
                    # Send current screenshot on demand
                    if self.browser_page:
                        frame = await self.capture_browser_screenshot()
                        if frame:
                            await websocket.send(f"FRAME:{frame}")

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"📺 Dashboard disconnected: {client_id}")
        finally:
            self.connected_clients.discard(websocket)

    def set_browser_page(self, page):
        """
        Set the Playwright page to stream

        Args:
            page: Playwright Page object
        """
        self.browser_page = page
        logger.info("🎬 Browser page connected to streamer!")

    async def capture_browser_screenshot(self) -> Optional[str]:
        """Capture screenshot from Playwright browser"""
        if not self.browser_page:
            return None

        try:
            # Take screenshot
            screenshot_bytes = await self.browser_page.screenshot(
                type='jpeg',
                quality=60  # Lower quality for faster streaming
            )

            # Convert to base64
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            return screenshot_b64

        except Exception as e:
            logger.error(f"Error capturing browser screenshot: {e}")
            return None

    async def stream_browser(self):
        """
        Main streaming loop - captures and broadcasts browser screenshots
        """
        logger.info(f"📸 Starting browser screen stream ({self.fps} FPS)...")
        self.streaming = True

        frame_count = 0

        while self.streaming:
            try:
                if not self.connected_clients or not self.browser_page:
                    # No viewers or no browser, save resources
                    await asyncio.sleep(1)
                    continue

                # Capture screenshot from browser
                screenshot = await self.capture_browser_screenshot()

                if screenshot:
                    # Broadcast to all dashboards
                    await self.broadcast_frame(screenshot)
                    frame_count += 1

                    if frame_count % (self.fps * 10) == 0:
                        logger.info(f"📺 Streaming... ({len(self.connected_clients)} viewers)")

                # Wait for next frame
                await asyncio.sleep(self.frame_delay)

            except Exception as e:
                logger.error(f"Error in stream loop: {e}")
                await asyncio.sleep(1)

    async def broadcast_frame(self, frame_data: str):
        """Broadcast frame to all connected dashboards"""
        if not self.connected_clients:
            return

        disconnected = set()

        for client in self.connected_clients:
            try:
                await client.send(f"FRAME:{frame_data}")
            except:
                disconnected.add(client)

        self.connected_clients -= disconnected

    def stop_streaming(self):
        """Stop streaming"""
        self.streaming = False
        logger.info("🔴 Screen stream stopped")


# Demo
async def demo():
    """Demo of screen streaming"""
    streamer = PlaywrightScreenStreamer(port=8765, fps=2)

    # Start server
    server_task = asyncio.create_task(streamer.start_server())

    # In real usage, we'd set streamer.browser_page = playwright_page
    # and start streaming

    print("🎥 Screen stream server running on ws://localhost:8765")
    print("📺 Connect your dashboard to see Sarah's screen!")
    print("\nPress Ctrl+C to stop...")

    try:
        await server_task
    except KeyboardInterrupt:
        print("\n🔴 Stopping...")
        streamer.stop_streaming()


if __name__ == "__main__":
    asyncio.run(demo())
