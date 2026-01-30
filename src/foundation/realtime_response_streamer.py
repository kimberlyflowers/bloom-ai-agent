"""
Real-time Response Streamer - ELIMINATES RESPONSE SILENCE
Provides immediate feedback while processing actions in background
NO MORE 36.5s silence - user sees progress instantly
"""

import asyncio
import logging
from typing import Optional, Callable
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger(__name__)


class RealtimeResponseStreamer:
    """
    Streams responses to user in real-time while processing actions

    Performance improvement:
    - Before: 36.5s silence → final response
    - After: Immediate "I'm on it!" → progress updates → final response
    """

    def __init__(self, websocket: WebSocketServerProtocol, send_message_func: Callable):
        """
        Args:
            websocket: WebSocket connection to user
            send_message_func: Function to send messages (e.g., chat_server.send_message)
        """
        self.websocket = websocket
        self.send_message = send_message_func

    async def stream_immediate_acknowledgment(self, user_intent: str):
        """
        Send immediate acknowledgment that we're working on the request

        Args:
            user_intent: What the user asked for (e.g., "search for movies")
        """
        # Parse intent to create natural acknowledgment
        intent_lower = user_intent.lower()

        if 'search' in intent_lower:
            message = "🔍 Looking for that now..."
        elif 'click' in intent_lower or 'tap' in intent_lower:
            message = "🎯 On it!"
        elif 'navigate' in intent_lower or 'go to' in intent_lower:
            message = "🚀 Taking you there..."
        elif 'type' in intent_lower or 'enter' in intent_lower:
            message = "⌨️  Typing that for you..."
        else:
            message = "💪 Working on it..."

        await self.send_message(self.websocket, {
            'type': 'sarah_message',
            'message': message,
            'streaming': True  # Indicates this is a streaming update, not final response
        })

        logger.info(f"📤 Streamed immediate acknowledgment: {message}")

    async def stream_progress_update(self, update: str):
        """
        Send progress update while action is executing

        Args:
            update: Progress message (e.g., "Found search box on page...")
        """
        await self.send_message(self.websocket, {
            'type': 'sarah_progress',
            'message': update,
            'streaming': True
        })

        logger.info(f"📤 Streamed progress: {update}")

    async def stream_action_result(self, success: bool, action: str, details: str = ""):
        """
        Send action result update

        Args:
            success: Whether action succeeded
            action: Action description
            details: Additional details
        """
        if success:
            message = f"✅ {action}"
        else:
            message = f"❌ {action} - {details}" if details else f"❌ {action}"

        await self.send_message(self.websocket, {
            'type': 'sarah_progress',
            'message': message,
            'streaming': True
        })

        logger.info(f"📤 Streamed result: {message}")

    async def stream_with_action(
        self,
        action_func: Callable,
        action_args: tuple = (),
        action_kwargs: dict = {},
        immediate_message: str = "Working on it...",
        success_message: str = "Done!",
        failure_message: str = "Couldn't complete that"
    ) -> tuple:
        """
        Execute action with real-time streaming updates

        Args:
            action_func: Async function to execute
            action_args: Args for action function
            action_kwargs: Kwargs for action function
            immediate_message: Message to send immediately
            success_message: Message on success
            failure_message: Message on failure

        Returns:
            (success: bool, result: Any)
        """
        # Immediate acknowledgment
        await self.send_message(self.websocket, {
            'type': 'sarah_message',
            'message': immediate_message,
            'streaming': True
        })

        logger.info(f"📤 Streaming action: {immediate_message}")

        try:
            # Execute action
            if asyncio.iscoroutinefunction(action_func):
                result = await action_func(*action_args, **action_kwargs)
            else:
                result = action_func(*action_args, **action_kwargs)

            # Determine success
            if isinstance(result, dict):
                success = result.get('success', False)
            elif isinstance(result, bool):
                success = result
            else:
                success = result is not None

            # Send result update
            if success:
                await self.send_message(self.websocket, {
                    'type': 'sarah_progress',
                    'message': success_message,
                    'streaming': True
                })
                logger.info(f"✅ Action succeeded: {success_message}")
            else:
                await self.send_message(self.websocket, {
                    'type': 'sarah_progress',
                    'message': failure_message,
                    'streaming': True
                })
                logger.warning(f"❌ Action failed: {failure_message}")

            return success, result

        except Exception as e:
            logger.error(f"❌ Action error: {e}")

            await self.send_message(self.websocket, {
                'type': 'sarah_progress',
                'message': f"{failure_message}: {str(e)}",
                'streaming': True
            })

            return False, None

    async def stream_multi_step_action(
        self,
        steps: list,
        overall_description: str = "Completing your request"
    ) -> bool:
        """
        Execute multi-step action with progress updates for each step

        Args:
            steps: List of step dicts with 'name', 'func', 'args', 'kwargs'
            overall_description: Overall description of what we're doing

        Returns:
            bool: True if all steps succeeded
        """
        # Immediate acknowledgment
        await self.send_message(self.websocket, {
            'type': 'sarah_message',
            'message': f"🚀 {overall_description}...",
            'streaming': True
        })

        logger.info(f"📤 Starting multi-step action: {overall_description}")

        overall_success = True

        for i, step in enumerate(steps):
            step_name = step.get('name', f'Step {i+1}')
            step_func = step.get('func')
            step_args = step.get('args', ())
            step_kwargs = step.get('kwargs', {})

            # Progress update for this step
            await self.send_message(self.websocket, {
                'type': 'sarah_progress',
                'message': f"   {i+1}/{len(steps)}: {step_name}...",
                'streaming': True
            })

            logger.info(f"   📤 Step {i+1}/{len(steps)}: {step_name}")

            try:
                # Execute step
                if asyncio.iscoroutinefunction(step_func):
                    result = await step_func(*step_args, **step_kwargs)
                else:
                    result = step_func(*step_args, **step_kwargs)

                # Check success
                if isinstance(result, dict):
                    success = result.get('success', False)
                elif isinstance(result, bool):
                    success = result
                else:
                    success = result is not None

                if success:
                    await self.send_message(self.websocket, {
                        'type': 'sarah_progress',
                        'message': f"   ✅ {step_name}",
                        'streaming': True
                    })
                    logger.info(f"   ✅ Step succeeded: {step_name}")
                else:
                    await self.send_message(self.websocket, {
                        'type': 'sarah_progress',
                        'message': f"   ❌ {step_name} failed",
                        'streaming': True
                    })
                    logger.warning(f"   ❌ Step failed: {step_name}")
                    overall_success = False

            except Exception as e:
                logger.error(f"   ❌ Step error ({step_name}): {e}")
                await self.send_message(self.websocket, {
                    'type': 'sarah_progress',
                    'message': f"   ❌ {step_name} error: {str(e)}",
                    'streaming': True
                })
                overall_success = False

        # Final status
        if overall_success:
            await self.send_message(self.websocket, {
                'type': 'sarah_progress',
                'message': f"✅ {overall_description} complete!",
                'streaming': True
            })
            logger.info(f"✅ Multi-step action complete: {overall_description}")
        else:
            await self.send_message(self.websocket, {
                'type': 'sarah_progress',
                'message': f"⚠️  {overall_description} completed with some issues",
                'streaming': True
            })
            logger.warning(f"⚠️  Multi-step action had issues: {overall_description}")

        return overall_success
