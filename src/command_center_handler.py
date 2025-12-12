"""
Command Center WebSocket Handler
Handles /command WebSocket connections for multi-agent dashboard

NO FASTAPI - Pure WebSocket using existing infrastructure
"""

import asyncio
import json
import logging
from typing import Set, Dict, Any, Optional
from datetime import datetime
import websockets
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger(__name__)


class CommandCenterHandler:
    """
    Handles /command WebSocket for command center dashboard

    Responsibilities:
    - Track connected dashboard clients
    - Broadcast agent status updates
    - Handle approval requests (approve/reject content)
    - Send pending content to clients
    - Receive user actions from dashboard

    NO FASTAPI - uses existing WebSocket infrastructure
    """

    def __init__(self, orchestration_dashboard):
        """
        Initialize command center handler

        Args:
            orchestration_dashboard: OrchestrationDashboard instance
        """
        self.dashboard = orchestration_dashboard
        self.connected_clients: Set[WebSocketServerProtocol] = set()
        self.broadcast_task: Optional[asyncio.Task] = None

        logger.info("🎛️  Command Center Handler initialized")

    async def start_broadcasting(self):
        """Start periodic broadcasts of agent data"""
        logger.info("📡 Starting periodic broadcasts...")

        while True:
            try:
                await asyncio.sleep(5)  # Broadcast every 5 seconds

                if self.connected_clients:
                    await self.broadcast_agent_updates()

            except asyncio.CancelledError:
                logger.info("📡 Broadcasting cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Broadcast error: {e}")

    async def handle_client(self, websocket: WebSocketServerProtocol):
        """
        Handle command center WebSocket client

        Args:
            websocket: WebSocket connection
        """
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"🎛️  Command center client connected: {client_id}")

        # Add to connected clients
        self.connected_clients.add(websocket)

        # Start broadcasting if this is first client
        if len(self.connected_clients) == 1 and not self.broadcast_task:
            self.broadcast_task = asyncio.create_task(self.start_broadcasting())

        try:
            # Send initial data
            await self.send_initial_data(websocket)

            # Listen for messages from client
            async for message in websocket:
                await self.handle_message(websocket, message)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🎛️  Command center client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"❌ Command center error: {e}")
            logger.exception(e)
        finally:
            # Remove from connected clients
            self.connected_clients.discard(websocket)

            # Stop broadcasting if no clients left
            if len(self.connected_clients) == 0 and self.broadcast_task:
                self.broadcast_task.cancel()
                self.broadcast_task = None

    async def send_initial_data(self, websocket: WebSocketServerProtocol):
        """Send initial dashboard data to newly connected client"""
        try:
            # Get all agents data
            agents_data = self.dashboard.get_all_agents_data()

            # Get pending approvals
            pending = self.dashboard.get_pending_approvals()

            # Send initial state
            await websocket.send(json.dumps({
                "type": "initial_data",
                "agents": agents_data,
                "pending_approvals": pending,
                "timestamp": datetime.utcnow().isoformat()
            }))

            logger.info(f"📤 Sent initial data: {len(agents_data)} agents, {len(pending)} pending approvals")

        except Exception as e:
            logger.error(f"❌ Error sending initial data: {e}")

    async def handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """
        Handle incoming message from dashboard client

        Message types:
        - get_agents: Request agent data
        - get_pending: Request pending approvals
        - approve_content: Approve content
        - reject_content: Reject content with feedback
        """
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            logger.info(f"📥 Command center message: {msg_type}")

            if msg_type == "get_agents":
                # Send agent data
                agents_data = self.dashboard.get_all_agents_data()
                await websocket.send(json.dumps({
                    "type": "agent_update",
                    "agents": agents_data,
                    "timestamp": datetime.utcnow().isoformat()
                }))

            elif msg_type == "get_pending":
                # Send pending approvals
                pending = self.dashboard.get_pending_approvals()
                await websocket.send(json.dumps({
                    "type": "pending_update",
                    "pending_approvals": pending,
                    "timestamp": datetime.utcnow().isoformat()
                }))

            elif msg_type == "approve_content":
                # Approve content
                content_id = data.get("content_id")
                feedback = data.get("feedback", "")

                success = await self.dashboard.approve_content(content_id, feedback)

                # Broadcast update to all clients
                await self.broadcast_approval_update(content_id, "approved", feedback)

                # Send confirmation
                await websocket.send(json.dumps({
                    "type": "approval_response",
                    "success": success,
                    "content_id": content_id,
                    "action": "approved"
                }))

            elif msg_type == "reject_content":
                # Reject content
                content_id = data.get("content_id")
                feedback = data.get("feedback", "Please make changes")

                success = await self.dashboard.reject_content(content_id, feedback)

                # Broadcast update to all clients
                await self.broadcast_approval_update(content_id, "rejected", feedback)

                # Send confirmation
                await websocket.send(json.dumps({
                    "type": "approval_response",
                    "success": success,
                    "content_id": content_id,
                    "action": "rejected"
                }))

            else:
                logger.warning(f"⚠️ Unknown message type: {msg_type}")

        except json.JSONDecodeError:
            logger.error(f"❌ Invalid JSON: {message}")
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")
            logger.exception(e)

    async def broadcast_agent_updates(self):
        """Broadcast agent updates to all connected clients"""
        try:
            agents_data = self.dashboard.get_all_agents_data()

            message = json.dumps({
                "type": "agent_update",
                "agents": agents_data,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Send to all connected clients
            disconnected = set()
            for client in self.connected_clients:
                try:
                    await client.send(message)
                except:
                    disconnected.add(client)

            # Remove disconnected clients
            self.connected_clients -= disconnected

        except Exception as e:
            logger.error(f"❌ Broadcast error: {e}")

    async def broadcast_approval_update(self, content_id: str, action: str, feedback: str):
        """Broadcast approval action to all clients"""
        try:
            message = json.dumps({
                "type": "approval_action",
                "content_id": content_id,
                "action": action,
                "feedback": feedback,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Send to all connected clients
            disconnected = set()
            for client in self.connected_clients:
                try:
                    await client.send(message)
                except:
                    disconnected.add(client)

            # Remove disconnected clients
            self.connected_clients -= disconnected

        except Exception as e:
            logger.error(f"❌ Broadcast approval error: {e}")

    async def broadcast_new_content(self, content: Dict[str, Any]):
        """Broadcast new content submission to all clients"""
        try:
            message = json.dumps({
                "type": "new_content",
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Send to all connected clients
            disconnected = set()
            for client in self.connected_clients:
                try:
                    await client.send(message)
                except:
                    disconnected.add(client)

            # Remove disconnected clients
            self.connected_clients -= disconnected

            logger.info(f"📢 Broadcasted new content: {content.get('title', 'untitled')}")

        except Exception as e:
            logger.error(f"❌ Broadcast new content error: {e}")
