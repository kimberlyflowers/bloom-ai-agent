"""
Parallel Execution Engine - PERFORMANCE AGNOSTIC
Executes multiple interaction strategies SIMULTANEOUSLY, uses first success
NO MORE sequential timeout cascade (15s + 10s + success = 36.5s waste)
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class ParallelExecutionEngine:
    """
    Executes multiple strategies in parallel, returns first success

    Performance improvement:
    - Before: Try A (15s timeout) → fail → Try B (10s) → fail → Try C (success) = 36.5s
    - After: Try A, B, C simultaneously → first success wins = 3-5s
    """

    def __init__(self, max_total_timeout: float = 10.0):
        """
        Args:
            max_total_timeout: Maximum time to wait for ANY strategy to succeed (default 10s)
        """
        self.max_total_timeout = max_total_timeout

    async def execute_parallel(
        self,
        strategies: List[Dict[str, Any]],
        description: str = "action"
    ) -> Dict[str, Any]:
        """
        Execute multiple strategies in parallel, return first success

        Args:
            strategies: List of strategy dicts with 'name', 'func', and 'args'
                Example: [
                    {'name': 'coordinates', 'func': click_by_coords, 'args': (50, 50)},
                    {'name': 'aria_label', 'func': click_by_aria, 'args': ('Search',)},
                    {'name': 'text', 'func': click_by_text, 'args': ('Zoeken',)}
                ]
            description: Description of what we're trying to do (for logging)

        Returns:
            {
                'success': bool,
                'strategy': str,  # Name of winning strategy
                'result': Any,    # Result from winning strategy
                'time_taken': float,  # Seconds
                'strategies_tried': List[str],  # All strategies that were attempted
                'strategies_completed': int  # How many finished before we got a winner
            }
        """
        if not strategies:
            return {
                'success': False,
                'error': 'No strategies provided',
                'time_taken': 0.0
            }

        start_time = datetime.now()
        logger.info(f"🚀 PARALLEL EXECUTION: Trying {len(strategies)} strategies simultaneously for '{description}'")

        # Create tasks for all strategies
        tasks = []
        strategy_names = []

        for i, strategy in enumerate(strategies):
            name = strategy.get('name', f'strategy_{i}')
            func = strategy.get('func')
            args = strategy.get('args', ())
            kwargs = strategy.get('kwargs', {})

            if not func:
                logger.warning(f"⚠️  Strategy '{name}' has no function, skipping")
                continue

            # Wrap strategy in a task with its name
            task = asyncio.create_task(
                self._execute_strategy(name, func, args, kwargs)
            )
            tasks.append(task)
            strategy_names.append(name)

        if not tasks:
            return {
                'success': False,
                'error': 'No valid strategies to execute',
                'time_taken': 0.0
            }

        logger.info(f"   Strategies: {', '.join(strategy_names)}")

        try:
            # Wait for first success or all failures (with timeout)
            winner = None
            completed_count = 0

            # Use asyncio.wait with FIRST_COMPLETED to get results as they finish
            pending = set(tasks)

            while pending and not winner:
                # Wait for next completion or timeout
                done, pending = await asyncio.wait(
                    pending,
                    timeout=self.max_total_timeout,
                    return_when=asyncio.FIRST_COMPLETED
                )

                # Check completed tasks for success
                for task in done:
                    completed_count += 1
                    try:
                        result = await task
                        if result.get('success'):
                            # Found a winner!
                            winner = result
                            logger.info(f"✅ PARALLEL EXECUTION: '{result['strategy']}' succeeded!")
                            break
                        else:
                            logger.debug(f"   '{result['strategy']}' failed: {result.get('error', 'unknown')}")
                    except Exception as e:
                        logger.debug(f"   Strategy failed with exception: {e}")

                # If we found a winner, cancel remaining tasks
                if winner:
                    for task in pending:
                        task.cancel()
                    break

                # If no pending tasks left and no winner, all failed
                if not pending and not winner:
                    break

            # Calculate time taken
            time_taken = (datetime.now() - start_time).total_seconds()

            if winner:
                return {
                    'success': True,
                    'strategy': winner['strategy'],
                    'result': winner.get('result'),
                    'time_taken': time_taken,
                    'strategies_tried': strategy_names,
                    'strategies_completed': completed_count
                }
            else:
                logger.warning(f"❌ PARALLEL EXECUTION: All {len(strategies)} strategies failed for '{description}'")
                return {
                    'success': False,
                    'error': f'All {len(strategies)} strategies failed',
                    'time_taken': time_taken,
                    'strategies_tried': strategy_names,
                    'strategies_completed': completed_count
                }

        except asyncio.TimeoutError:
            # Cancel all pending tasks
            for task in tasks:
                if not task.done():
                    task.cancel()

            time_taken = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ PARALLEL EXECUTION: Timeout after {time_taken:.1f}s for '{description}'")

            return {
                'success': False,
                'error': f'Timeout after {time_taken:.1f}s',
                'time_taken': time_taken,
                'strategies_tried': strategy_names
            }

        except Exception as e:
            time_taken = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ PARALLEL EXECUTION: Error - {e}")

            return {
                'success': False,
                'error': str(e),
                'time_taken': time_taken,
                'strategies_tried': strategy_names
            }

    async def _execute_strategy(
        self,
        name: str,
        func: Callable,
        args: tuple,
        kwargs: dict
    ) -> Dict[str, Any]:
        """
        Execute a single strategy and return standardized result

        Returns:
            {
                'success': bool,
                'strategy': str,
                'result': Any,
                'error': str (if failed)
            }
        """
        try:
            logger.debug(f"   🔄 Trying strategy: {name}")

            # Execute the strategy function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Standardize result format
            if isinstance(result, dict) and 'success' in result:
                # Already in correct format
                return {
                    'success': result.get('success', False),
                    'strategy': name,
                    'result': result,
                    'error': result.get('error', result.get('message', ''))
                }
            elif isinstance(result, bool):
                # Simple boolean result
                return {
                    'success': result,
                    'strategy': name,
                    'result': result
                }
            elif result is not None:
                # Truthy result = success
                return {
                    'success': True,
                    'strategy': name,
                    'result': result
                }
            else:
                # None or falsy = failure
                return {
                    'success': False,
                    'strategy': name,
                    'error': 'Strategy returned falsy result'
                }

        except asyncio.CancelledError:
            # Task was cancelled (another strategy succeeded)
            logger.debug(f"   ⏸️  Strategy '{name}' cancelled (another succeeded)")
            raise

        except Exception as e:
            logger.debug(f"   ❌ Strategy '{name}' failed: {e}")
            return {
                'success': False,
                'strategy': name,
                'error': str(e)
            }

    async def execute_with_confidence_routing(
        self,
        primary_strategy: Dict[str, Any],
        fallback_strategies: List[Dict[str, Any]],
        confidence_threshold: float = 0.7,
        description: str = "action"
    ) -> Dict[str, Any]:
        """
        Try primary strategy first, fall back to parallel execution if confidence is low

        Args:
            primary_strategy: Primary strategy dict with 'confidence' field
            fallback_strategies: List of fallback strategies
            confidence_threshold: Minimum confidence to skip fallbacks (default 0.7)
            description: Description for logging

        Returns:
            Same format as execute_parallel()
        """
        confidence = primary_strategy.get('confidence', 0.0)

        if confidence >= confidence_threshold:
            # High confidence - just try primary
            logger.info(f"🎯 High confidence ({confidence:.2f}) - trying primary strategy only")

            start_time = datetime.now()
            result = await self._execute_strategy(
                primary_strategy.get('name', 'primary'),
                primary_strategy.get('func'),
                primary_strategy.get('args', ()),
                primary_strategy.get('kwargs', {})
            )

            time_taken = (datetime.now() - start_time).total_seconds()

            if result.get('success'):
                result['time_taken'] = time_taken
                return result
            else:
                # Primary failed - try fallbacks
                logger.warning(f"⚠️  Primary strategy failed despite high confidence, trying fallbacks")
                return await self.execute_parallel(fallback_strategies, description)
        else:
            # Low confidence - try all strategies in parallel
            logger.info(f"⚠️  Low confidence ({confidence:.2f}) - trying all strategies in parallel")
            all_strategies = [primary_strategy] + fallback_strategies
            return await self.execute_parallel(all_strategies, description)
