"""
AUTONOMOUS EXECUTOR - Sarah's Brain 🧠

Transforms Sarah from puppet to autonomous agent.
User says: "Go watch 5 TikTok strategy videos"
Sarah: Plans, executes, reports - no hand-holding needed.
"""

import asyncio
import json
import logging
import re
import base64
from io import BytesIO
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import anthropic
import os

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════
# COMPONENT 1: TASK PLANNER
# ════════════════════════════════════════════════════════════════

@dataclass
class ExecutableStep:
    """Single step in an autonomous mission"""
    action_type: str  # 'navigate', 'search', 'click', 'analyze', 'wait', 'report'
    parameters: Dict[str, Any]
    expected_outcome: str
    retry_on_failure: bool = True


class TaskPlanner:
    """
    Breaks down high-level goals into executable steps

    Example:
        Input: "Go watch 5 TikTok strategy videos and tell me what you learned"
        Output: [
            ExecutableStep(action_type='navigate', parameters={'url': 'youtube.com'}, ...),
            ExecutableStep(action_type='search', parameters={'query': 'TikTok strategies'}, ...),
            ExecutableStep(action_type='analyze', parameters={'task': 'select_videos', 'count': 5}, ...),
            ...
        ]
    """

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    async def create_plan(self, user_goal: str, current_url: str = "") -> List[ExecutableStep]:
        """
        Create an executable plan from a high-level goal

        Args:
            user_goal: What the user wants Sarah to do
            current_url: Where Sarah currently is (to avoid redundant navigation)

        Returns:
            List of executable steps
        """
        logger.info(f"🧠 Planning autonomous mission: {user_goal}")

        # Use Claude to create the plan
        planning_prompt = f"""You are Sarah's task planner. Break down this high-level goal into executable steps.

User goal: {user_goal}
Current location: {current_url or 'Not on any page yet'}

Available action types:
- navigate: Go to a URL (parameters: url)
- search: Search on current platform (parameters: query, platform='youtube'/'google')
- analyze_and_select: Use vision to analyze page and select items (parameters: task, count, criteria)
- click: Click on something (parameters: description)
- wait: Wait for content to load (parameters: seconds, reason)
- extract_info: Extract information from current page (parameters: info_type, details)
- report: Report findings to user (parameters: message)

Return ONLY a JSON array of steps. Each step must have:
- action_type: one of the types above
- parameters: dict with required params for that action
- expected_outcome: what should happen after this step
- retry_on_failure: true/false

Example for "watch 3 TikTok videos":
[
  {{"action_type": "navigate", "parameters": {{"url": "https://youtube.com"}}, "expected_outcome": "On YouTube homepage", "retry_on_failure": true}},
  {{"action_type": "search", "parameters": {{"query": "TikTok strategies", "platform": "youtube"}}, "expected_outcome": "YouTube search results visible", "retry_on_failure": true}},
  {{"action_type": "analyze_and_select", "parameters": {{"task": "select_videos", "count": 3, "criteria": "best TikTok strategy videos by views and relevance"}}, "expected_outcome": "3 videos selected", "retry_on_failure": false}},
  {{"action_type": "click", "parameters": {{"description": "first selected video"}}, "expected_outcome": "Video playing", "retry_on_failure": true}},
  {{"action_type": "wait", "parameters": {{"seconds": 10, "reason": "watch video content"}}, "expected_outcome": "Video watched", "retry_on_failure": false}},
  {{"action_type": "extract_info", "parameters": {{"info_type": "video_insights", "details": "key points from video"}}, "expected_outcome": "Insights extracted", "retry_on_failure": false}},
  {{"action_type": "report", "parameters": {{"message": "Completed watching 3 videos"}}, "expected_outcome": "User informed", "retry_on_failure": false}}
]

Now create the plan for the user's goal. Return ONLY valid JSON array, no explanations."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2048,
                messages=[{"role": "user", "content": planning_prompt}]
            )

            plan_json = response.content[0].text.strip()

            # Extract JSON if wrapped in code blocks
            if '```json' in plan_json:
                plan_json = plan_json.split('```json')[1].split('```')[0].strip()
            elif '```' in plan_json:
                plan_json = plan_json.split('```')[1].split('```')[0].strip()

            plan_data = json.loads(plan_json)

            # Convert to ExecutableStep objects
            steps = [
                ExecutableStep(
                    action_type=step['action_type'],
                    parameters=step['parameters'],
                    expected_outcome=step['expected_outcome'],
                    retry_on_failure=step.get('retry_on_failure', True)
                )
                for step in plan_data
            ]

            logger.info(f"✅ Created plan with {len(steps)} steps")
            return steps

        except Exception as e:
            logger.error(f"❌ Planning failed: {e}")
            # Return a basic fallback plan
            return self._create_fallback_plan(user_goal)

    def _create_fallback_plan(self, user_goal: str) -> List[ExecutableStep]:
        """Simple fallback if AI planning fails"""
        logger.warning("Using fallback plan")
        return [
            ExecutableStep(
                action_type='report',
                parameters={'message': f"I couldn't create a plan for: {user_goal}. Please try rephrasing."},
                expected_outcome='User informed',
                retry_on_failure=False
            )
        ]


# ════════════════════════════════════════════════════════════════
# COMPONENT 2: VISUAL DECISION MAKER
# ════════════════════════════════════════════════════════════════

class VisualDecisionMaker:
    """
    Uses Claude Vision to analyze screenshots and make intelligent decisions

    Example:
        Task: "Select 5 best TikTok strategy videos"
        Process:
            1. Take screenshot of YouTube results
            2. Send to Claude Vision with selection criteria
            3. Parse response with selected videos
            4. Return video titles/positions to click
    """

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    async def analyze_and_select(
        self,
        screenshot_base64: str,
        task: str,
        count: int,
        criteria: str
    ) -> Dict[str, Any]:
        """
        Analyze a screenshot and make selections based on criteria

        Args:
            screenshot_base64: Base64 encoded screenshot
            task: What to select (e.g., 'select_videos', 'select_links', 'find_button')
            count: How many to select
            criteria: Selection criteria (e.g., 'best by views and relevance')

        Returns:
            Dict with selected items and reasoning
        """
        logger.info(f"👁️ Analyzing screenshot for: {task}")

        vision_prompt = self._build_vision_prompt(task, count, criteria)

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2048,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": screenshot_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": vision_prompt
                        }
                    ]
                }]
            )

            analysis_text = response.content[0].text.strip()

            # Extract JSON from response
            if '```json' in analysis_text:
                json_text = analysis_text.split('```json')[1].split('```')[0].strip()
            elif '```' in analysis_text:
                json_text = analysis_text.split('```')[1].split('```')[0].strip()
            else:
                json_text = analysis_text

            result = json.loads(json_text)
            logger.info(f"✅ Vision analysis complete: {len(result.get('selections', []))} items selected")
            return result

        except Exception as e:
            logger.error(f"❌ Vision analysis failed: {e}")
            return {'selections': [], 'error': str(e)}

    def _build_vision_prompt(self, task: str, count: int, criteria: str) -> str:
        """Build the vision analysis prompt based on task type"""

        if task == 'select_videos':
            return f"""You are analyzing a YouTube search results page.

Task: Select the {count} best videos based on: {criteria}

Look for:
- Video titles (relevant to the search)
- View counts (higher = more credible)
- Creator names (known experts preferred)
- Thumbnails (professional quality)

Return JSON ONLY (no explanations):
{{
  "selections": [
    {{
      "position": 1,
      "title": "Full video title",
      "creator": "Channel name",
      "views": "View count if visible",
      "reason": "Why this video was selected"
    }},
    ...
  ]
}}

Select exactly {count} videos. Return ONLY valid JSON."""

        elif task == 'find_button':
            return f"""You are analyzing a webpage looking for a specific button or element.

Task: Find and locate: {criteria}

Return JSON ONLY:
{{
  "found": true/false,
  "element": "Description of what you found",
  "location": "Where it is on the page (top-left, center, etc)",
  "confidence": "high/medium/low"
}}"""

        else:
            # Generic analysis
            return f"""Analyze this screenshot and complete the following task:

Task: {task}
Count: {count}
Criteria: {criteria}

Return your analysis as JSON with relevant fields."""


# ════════════════════════════════════════════════════════════════
# COMPONENT 3: EXECUTION LOOP
# ════════════════════════════════════════════════════════════════

class ExecutionLoop:
    """
    Executes the plan autonomously without user intervention

    Runs each step, handles failures, adapts as needed
    """

    def __init__(
        self,
        sarah_browser,
        visual_decision_maker: VisualDecisionMaker,
        progress_callback
    ):
        self.browser = sarah_browser
        self.vision = visual_decision_maker
        self.progress = progress_callback
        self.extracted_info = []  # Store info collected during mission

    async def execute_plan(self, steps: List[ExecutableStep]) -> Dict[str, Any]:
        """
        Execute all steps in the plan autonomously

        Returns:
            Dict with execution results and collected information
        """
        logger.info(f"🚀 Starting autonomous execution: {len(steps)} steps")

        results = {
            'success': True,
            'completed_steps': 0,
            'failed_steps': 0,
            'collected_info': [],
            'errors': []
        }

        for i, step in enumerate(steps):
            step_num = i + 1
            logger.info(f"📍 Step {step_num}/{len(steps)}: {step.action_type}")

            # Report progress
            await self.progress(f"Step {step_num}/{len(steps)}: {step.expected_outcome}")

            # Execute the step
            try:
                step_result = await self._execute_step(step)

                if step_result.get('success'):
                    results['completed_steps'] += 1
                    logger.info(f"✅ Step {step_num} completed")

                    # Store any collected information
                    if 'info' in step_result:
                        results['collected_info'].append(step_result['info'])

                else:
                    # Step failed
                    results['failed_steps'] += 1
                    error_msg = step_result.get('error', 'Unknown error')
                    logger.warning(f"⚠️ Step {step_num} failed: {error_msg}")

                    if step.retry_on_failure:
                        logger.info(f"🔄 Retrying step {step_num}...")
                        await self.progress(f"Retrying: {step.expected_outcome}")

                        retry_result = await self._execute_step(step)
                        if retry_result.get('success'):
                            results['completed_steps'] += 1
                            logger.info(f"✅ Step {step_num} succeeded on retry")
                        else:
                            results['errors'].append(f"Step {step_num} failed: {error_msg}")
                            # Continue anyway unless it's critical
                    else:
                        results['errors'].append(f"Step {step_num} failed: {error_msg}")

                # Small delay between steps
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"❌ Step {step_num} crashed: {e}")
                results['failed_steps'] += 1
                results['errors'].append(f"Step {step_num} crashed: {str(e)}")

        # Final status
        if results['failed_steps'] > 0:
            results['success'] = False

        logger.info(f"🏁 Execution complete: {results['completed_steps']}/{len(steps)} steps succeeded")
        return results

    async def _execute_step(self, step: ExecutableStep) -> Dict[str, Any]:
        """Execute a single step"""

        action_type = step.action_type
        params = step.parameters

        try:
            if action_type == 'navigate':
                return await self._execute_navigate(params)

            elif action_type == 'search':
                return await self._execute_search(params)

            elif action_type == 'analyze_and_select':
                return await self._execute_analyze_and_select(params)

            elif action_type == 'click':
                return await self._execute_click(params)

            elif action_type == 'wait':
                return await self._execute_wait(params)

            elif action_type == 'extract_info':
                return await self._execute_extract_info(params)

            elif action_type == 'report':
                return await self._execute_report(params)

            else:
                return {'success': False, 'error': f'Unknown action type: {action_type}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _execute_navigate(self, params: Dict) -> Dict:
        """Navigate to URL"""
        url = params.get('url', '')
        logger.info(f"🌐 Navigating to: {url}")

        result = await self.browser.navigate(url)
        return result

    async def _execute_search(self, params: Dict) -> Dict:
        """Execute search"""
        query = params.get('query', '')
        platform = params.get('platform', 'google')

        logger.info(f"🔍 Searching {platform} for: {query}")

        if platform == 'youtube':
            result = await self.browser.search_youtube(query)
        else:
            result = await self.browser.search_google(query)

        return result

    async def _execute_analyze_and_select(self, params: Dict) -> Dict:
        """Analyze page with vision and select items"""
        task = params.get('task', '')
        count = params.get('count', 1)
        criteria = params.get('criteria', '')

        logger.info(f"👁️ Analyzing: {task} (selecting {count})")

        # Take screenshot (returns PIL Image)
        screenshot_pil = await self.browser.take_screenshot()

        # Convert PIL Image to base64 for Claude Vision API
        buffered = BytesIO()
        screenshot_pil.save(buffered, format="PNG")
        screenshot_base64 = base64.b64encode(buffered.getvalue()).decode()

        logger.info(f"📸 Screenshot captured and converted to base64")

        # Analyze with vision
        analysis = await self.vision.analyze_and_select(
            screenshot_base64=screenshot_base64,
            task=task,
            count=count,
            criteria=criteria
        )

        # Store selections for next steps
        self.current_selections = analysis.get('selections', [])

        return {
            'success': len(self.current_selections) > 0,
            'info': analysis,
            'selections': self.current_selections
        }

    async def _execute_click(self, params: Dict) -> Dict:
        """Click on element"""
        description = params.get('description', '')

        logger.info(f"🖱️ Clicking: {description}")

        # 🍪 BUG FIX: Dismiss cookie banners on YouTube before clicking
        try:
            current_url = self.browser.page.url if self.browser.page else ""
            if 'youtube.com' in current_url:
                logger.info("🍪 Checking for YouTube cookie banner...")

                # Try to dismiss cookie banner if it exists
                cookie_dismissed = await self.browser.dismiss_cookie_banner()

                if cookie_dismissed:
                    logger.info("✅ Cookie banner dismissed")
                    await self.progress("Dismissed cookie banner")
                    # Small delay for banner to disappear
                    await asyncio.sleep(1)
        except Exception as e:
            # Don't fail the whole click if cookie dismissal fails
            logger.warning(f"Cookie banner dismissal failed (non-critical): {e}")

        # Check if description references a selection (e.g., "first selected video")
        if 'selected' in description.lower() and hasattr(self, 'current_selections'):
            # Extract which selection (first, second, etc.)
            if 'first' in description.lower() and len(self.current_selections) > 0:
                video_title = self.current_selections[0].get('title', '')
                description = f"click video titled {video_title}"
            elif 'second' in description.lower() and len(self.current_selections) > 1:
                video_title = self.current_selections[1].get('title', '')
                description = f"click video titled {video_title}"
            elif 'third' in description.lower() and len(self.current_selections) > 2:
                video_title = self.current_selections[2].get('title', '')
                description = f"click video titled {video_title}"

        await self.progress(f"Clicking: {description}")

        # Use browser's universal_click method (integrates with platform-aware clicking)
        try:
            result = await self.browser.universal_click(description)
            return result
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _execute_wait(self, params: Dict) -> Dict:
        """Wait for specified time"""
        seconds = params.get('seconds', 2)
        reason = params.get('reason', 'waiting')

        logger.info(f"⏳ Waiting {seconds}s: {reason}")
        await self.progress(f"Waiting {seconds}s: {reason}")

        await asyncio.sleep(seconds)

        return {'success': True}

    async def _execute_extract_info(self, params: Dict) -> Dict:
        """Extract information from current page"""
        info_type = params.get('info_type', '')
        details = params.get('details', '')

        logger.info(f"📄 Extracting: {info_type}")

        # Placeholder for now - future versions will extract real insights
        # Could use Claude Vision to analyze video content, read text, etc.

        extracted = {
            'type': info_type,
            'details': details,
            'url': self.browser.page.url if self.browser.page else '',
            'timestamp': asyncio.get_event_loop().time(),
            'note': 'Placeholder - extraction capability coming soon'
        }

        self.extracted_info.append(extracted)

        return {'success': True, 'info': extracted}

    async def _execute_report(self, params: Dict) -> Dict:
        """Report to user"""
        message = params.get('message', '')

        logger.info(f"📢 Reporting: {message}")
        await self.progress(f"✅ {message}")

        return {'success': True}


# ════════════════════════════════════════════════════════════════
# COMPONENT 4: PROGRESS REPORTER
# ════════════════════════════════════════════════════════════════

class ProgressReporter:
    """
    Streams real-time progress updates to the user

    Integrates with existing chat streaming in chat_server.py
    """

    def __init__(self, websocket_send_callback):
        """
        Args:
            websocket_send_callback: Function to send messages to user's websocket
        """
        self.send = websocket_send_callback

    async def report(self, message: str, status: str = 'info'):
        """
        Send progress update to user

        Args:
            message: Progress message
            status: 'info', 'success', 'warning', 'error'
        """
        # Emoji indicators
        emoji = {
            'info': '🔄',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }

        formatted_message = f"{emoji.get(status, '📍')} {message}"

        # Send via websocket
        await self.send({
            'type': 'progress',
            'message': formatted_message,
            'status': status
        })

        logger.info(formatted_message)


# ════════════════════════════════════════════════════════════════
# MAIN AUTONOMOUS EXECUTOR
# ════════════════════════════════════════════════════════════════

class AutonomousExecutor:
    """
    Main coordinator for autonomous missions

    Usage:
        executor = AutonomousExecutor(api_key, sarah_browser, websocket_send)
        result = await executor.execute_mission("Go watch 5 TikTok strategy videos")
    """

    def __init__(self, api_key: str, sarah_browser, websocket_send_callback):
        self.planner = TaskPlanner(api_key)
        self.vision = VisualDecisionMaker(api_key)
        self.reporter = ProgressReporter(websocket_send_callback)
        self.browser = sarah_browser

    async def execute_mission(self, user_goal: str) -> Dict[str, Any]:
        """
        Execute a complete autonomous mission

        Args:
            user_goal: High-level goal from user

        Returns:
            Dict with mission results and collected information
        """
        logger.info(f"🎯 AUTONOMOUS MISSION: {user_goal}")

        await self.reporter.report(f"Mission received: {user_goal}", 'info')
        await self.reporter.report("Creating execution plan...", 'info')

        # Step 1: Create the plan
        current_url = self.browser.page.url if self.browser.page else ""
        plan = await self.planner.create_plan(user_goal, current_url)

        await self.reporter.report(f"Plan created: {len(plan)} steps", 'success')

        # Step 2: Execute the plan
        execution_loop = ExecutionLoop(
            sarah_browser=self.browser,
            visual_decision_maker=self.vision,
            progress_callback=lambda msg: self.reporter.report(msg, 'info')
        )

        results = await execution_loop.execute_plan(plan)

        # Step 3: Report final results
        if results['success']:
            await self.reporter.report(
                f"Mission complete! {results['completed_steps']} steps succeeded",
                'success'
            )
        else:
            await self.reporter.report(
                f"Mission had issues: {results['failed_steps']} steps failed",
                'warning'
            )

        # Include collected information
        results['mission'] = user_goal
        results['plan_steps'] = len(plan)

        return results

    @staticmethod
    def is_autonomous_request(user_message: str) -> bool:
        """
        Detect if user is requesting autonomous execution

        Args:
            user_message: User's message

        Returns:
            True if this should trigger autonomous mode
        """
        autonomous_patterns = [
            r'\bgo\s+watch\b',
            r'\bwatch\s+\d+',
            r'\bresearch\b.*\btopic\b',
            r'\bfind\s+me\s+information\b',
            r'\blearn\s+about\b',
            r'\bgo\s+to\b.*\band\s+(watch|find|search|learn)',
            r'\bshow\s+me\s+\d+',
            r'\bget\s+me\s+\d+',
        ]

        message_lower = user_message.lower()

        for pattern in autonomous_patterns:
            if re.search(pattern, message_lower):
                return True

        return False
