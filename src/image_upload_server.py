"""
Simple HTTP Image Upload Server
Separate from WebSocket - handles image uploads via HTTP POST
"""
import asyncio
import json
import base64
import os
from aiohttp import web
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class ImageUploadServer:
    """HTTP server for handling image uploads (separate from WebSocket)"""

    def __init__(self, port: int = 8081, upload_dir: str = "uploaded_images"):
        self.port = port
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        self.app = None
        self.runner = None

        # Track latest uploaded image for Sarah to view
        self.latest_image_path = None

    async def handle_upload(self, request):
        """Handle image upload POST request"""
        try:
            data = await request.json()

            # Extract image data
            image_base64 = data.get('image')
            filename = data.get('filename', f'upload_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg')
            message = data.get('message', '')

            if not image_base64:
                return web.json_response({
                    'success': False,
                    'error': 'No image data provided'
                }, status=400)

            # Decode base64 image
            try:
                # Remove data URL prefix if present
                if ',' in image_base64:
                    image_base64 = image_base64.split(',')[1]

                image_bytes = base64.b64decode(image_base64)
            except Exception as e:
                logger.error(f"Failed to decode image: {e}")
                return web.json_response({
                    'success': False,
                    'error': 'Invalid base64 image data'
                }, status=400)

            # Save image to disk
            image_path = self.upload_dir / filename
            with open(image_path, 'wb') as f:
                f.write(image_bytes)

            # Update latest image reference
            self.latest_image_path = str(image_path)

            logger.info(f"📸 Image uploaded: {filename} ({len(image_bytes)} bytes)")
            if message:
                logger.info(f"💬 With message: {message}")

            return web.json_response({
                'success': True,
                'filename': filename,
                'path': str(image_path),
                'size': len(image_bytes)
            })

        except Exception as e:
            logger.error(f"Error handling upload: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    async def handle_cors_preflight(self, request):
        """Handle CORS preflight requests"""
        return web.Response(
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )

    async def get_latest_image(self):
        """Get the latest uploaded image for Sarah to view"""
        if not self.latest_image_path or not os.path.exists(self.latest_image_path):
            return None

        try:
            with open(self.latest_image_path, 'rb') as f:
                image_bytes = f.read()

            # Return as base64 for Claude Vision API
            return base64.b64encode(image_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"Error reading latest image: {e}")
            return None

    def clear_latest_image(self):
        """Clear the latest image reference after Sarah has seen it"""
        self.latest_image_path = None

    async def start(self):
        """Start the HTTP server"""
        self.app = web.Application()

        # Add CORS middleware
        async def cors_middleware(app, handler):
            async def middleware_handler(request):
                if request.method == 'OPTIONS':
                    return await self.handle_cors_preflight(request)

                response = await handler(request)
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
                return response
            return middleware_handler

        self.app.middlewares.append(cors_middleware)

        # Routes
        self.app.router.add_post('/upload', self.handle_upload)
        self.app.router.add_options('/upload', self.handle_cors_preflight)

        # Start server
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, '0.0.0.0', self.port)
        await site.start()

        logger.info(f"📸 Image upload server started on port {self.port}")
        logger.info(f"   📁 Upload directory: {self.upload_dir.absolute()}")
        logger.info(f"   🔗 Upload endpoint: http://localhost:{self.port}/upload")

    async def stop(self):
        """Stop the HTTP server"""
        if self.runner:
            await self.runner.cleanup()
            logger.info("📸 Image upload server stopped")
