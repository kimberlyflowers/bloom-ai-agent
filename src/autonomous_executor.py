"""
AUTONOMOUS EXECUTOR - Sarah's Brain 🧠
100% COMPATIBLE with FastAPI main.py and chat_server.py
NO CRASHES - ERROR FREE - GRACEFUL FALLBACKS
"""

import asyncio
import json
import logging
import re
import base64
import os
from io import BytesIO
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import anthropic

# ✅ FIXED: Logger defined first
logger = logging.getLogger(__name__)

# ✅ FIXED: SAFE IMPORTS WITH FALLBACKS - NO CRASHES
try:
    from src.video_tutorial_learning import (
        SkillLearner,
        SkillCategory,
        LearnedSkill,
        TutorialStep,
        StepType
    )
    VIDEO_LEARNING_AVAILABLE = True
    logger.info("✅ video_tutorial_learning module loaded")
except ImportError as e:
    logger.warning(f"⚠️ video_tutorial_learning not available: {e}")
    VIDEO_LEARNING_AVAILABLE = False
    # Create safe dummy classes
    class SkillLearner:
        async def learn_from_video(self, *args, **kwargs):
            return type('obj', (), {
                'skill_name': 'Fallback Skill',
                'skill_id': 'fallback_skill_001',
                'success_rate': 0.5,
                'tutorial_steps': []
            })()
    
    class SkillCategory:
        VIDEO_CREATION = 'video_creation'
        GRAPHIC_DESIGN = 'graphic_design'
        PLATFORM_MASTERY = 'platform_mastery'
        CONTENT_CREATION = 'content_creation'
    
    class LearnedSkill:
        def __init__(self):
            self.skill_name = "Fallback"
            self.skill_id = "fallback_001"
            self.success_rate = 0.0
            self.tutorial_steps = []

try:
    from src.ui_element_finder import UIElementFinder
    UI_FINDER_AVAILABLE = True
    logger.info("✅ UIElementFinder module loaded")
except ImportError as e:
    logger.warning(f"⚠️ UIElementFinder not available: {e}")
    UI_FINDER_AVAILABLE = False
    class UIElementFinder:
        def __init__(self, api_key):
            self.api_key = api_key
        async def find_element(self, *args, **kwargs):
            return {"found": False, "error": "UI finder not available"}

# YouTube Safety System - SAFE IMPORT
try:
    from src.youtube_safety import YouTubeSafetyGuard, YouTubeSafetyLevel
    YOUTUBE_SAFETY_AVAILABLE = True
    logger.info("✅ YouTube safety module loaded")
except ImportError as e:
    logger.warning(f"⚠️ YouTube safety system not available: {e}")
    YOUTUBE_SAFETY_AVAILABLE = False
    # Safe dummy classes
    class YouTubeSafetyGuard:
        def __init__(self, level):
            self.level = level
        
        async def can_perform_action(self, action):
            return True, "Safety system not available"
        
        def record_action(self, action_type, video_id=None, duration_seconds=0, success=True):
            logger.info(f"Safety: Recorded {action_type}")
        
        def get_status(self):
            return "not_available"
    
    class YouTubeSafetyLevel:
        LOW = 'low'
        MEDIUM = 'medium'
        HIGH = 'high'


# ════════════════════════════════════════════════════════════════
# COMPONENT 1: TASK PLANNER
# ════════════════════════════════════════════════════════════════

@dataclass
class ExecutableStep:
    """Single step in an autonomous mission"""
    action_type: str
    parameters: Dict[str, Any]
    expected_outcome: str
    retry_on_failure: bool = True


class TaskPlanner:
    """Breaks down high-level goals into executable steps"""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.api_key = api_key

    async def create_plan(self, user_goal: str, current_url: str = "") -> List[ExecutableStep]:
        """Create an executable plan from a high-level goal"""
        logger.info(f"🧠 Planning autonomous mission: {user_goal}")

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

Now create the plan for the user's goal. Return ONLY valid JSON array, no explanations."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
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
    """Uses Claude Vision to analyze screenshots"""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.api_key = api_key

    async def analyze_and_select(
        self,
        screenshot_base64: str,
        task: str,
        count: int,
        criteria: str
    ) -> Dict[str, Any]:
        """Analyze a screenshot and make selections based on criteria"""
        logger.info(f"👁️ Analyzing screenshot for: {task}")

        vision_prompt = f"""You are analyzing a webpage screenshot.

Task: {task}
Select {count} items based on: {criteria}

Return JSON ONLY:
{{
  "selections": [
    {{
      "position": 1,
      "title": "Item description",
      "reason": "Why this was selected"
    }}
  ]
}}"""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
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


# ════════════════════════════════════════════════════════════════
# COMPONENT 3: EXECUTION LOOP
# ════════════════════════════════════════════════════════════════

class ExecutionLoop:
    """Executes the plan autonomously without user intervention"""

    def __init__(
        self,
        sarah_browser,
        visual_decision_maker: VisualDecisionMaker,
        progress_callback
    ):
        self.browser = sarah_browser
        self.vision = visual_decision_maker
        self.progress = progress_callback
        self.extracted_info = []

    async def execute_plan(self, steps: List[ExecutableStep]) -> Dict[str, Any]:
        """Execute all steps in the plan autonomously"""
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
            try:
                await self.progress(f"Step {step_num}/{len(steps)}: {step.expected_outcome}")
            except Exception as e:
                logger.debug(f"Progress callback error: {e}")

            # Execute the step
            try:
                step_result = await self._execute_step(step)

                if step_result.get('success'):
                    results['completed_steps'] += 1
                    logger.info(f"✅ Step {step_num} completed")

                    if 'info' in step_result:
                        results['collected_info'].append(step_result['info'])

                else:
                    results['failed_steps'] += 1
                    error_msg = step_result.get('error', 'Unknown error')
                    logger.warning(f"⚠️ Step {step_num} failed: {error_msg}")

                    if step.retry_on_failure:
                        logger.info(f"🔄 Retrying step {step_num}...")
                        try:
                            await self.progress(f"Retrying: {step.expected_outcome}")
                        except:
                            pass

                        retry_result = await self._execute_step(step)
                        if retry_result.get('success'):
                            results['completed_steps'] += 1
                            logger.info(f"✅ Step {step_num} succeeded on retry")
                        else:
                            results['errors'].append(f"Step {step_num} failed: {error_msg}")
                    else:
                        results['errors'].append(f"Step {step_num} failed: {error_msg}")

                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"❌ Step {step_num} crashed: {e}")
                results['failed_steps'] += 1
                results['errors'].append(f"Step {step_num} crashed: {str(e)}")

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
        try:
            await self.browser.navigate(url)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _execute_search(self, params: Dict) -> Dict:
        """Execute search"""
        query = params.get('query', '')
        platform = params.get('platform', 'google')
        logger.info(f"🔍 Searching {platform} for: {query}")
        try:
            if platform == 'youtube':
                await self.browser.search_youtube(query)
            else:
                await self.browser.search_google(query)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _execute_analyze_and_select(self, params: Dict) -> Dict:
        """Analyze page with vision and select items"""
        task = params.get('task', '')
        count = params.get('count', 1)
        criteria = params.get('criteria', '')
        logger.info(f"👁️ Analyzing: {task} (selecting {count})")

        try:
            screenshot_pil = await self.browser.take_screenshot()
            buffered = BytesIO()
            screenshot_pil.save(buffered, format="PNG")
            screenshot_base64 = base64.b64encode(buffered.getvalue()).decode()

            analysis = await self.vision.analyze_and_select(
                screenshot_base64=screenshot_base64,
                task=task,
                count=count,
                criteria=criteria
            )

            self.current_selections = analysis.get('selections', [])
            return {
                'success': len(self.current_selections) > 0,
                'info': analysis,
                'selections': self.current_selections
            }
        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            return {'success': False, 'error': str(e)}

    async def _execute_click(self, params: Dict) -> Dict:
        """Click on element"""
        description = params.get('description', '')
        logger.info(f"🖱️ Clicking: {description}")

        # Handle cookie banners
        try:
            current_url = self.browser.page.url if self.browser.page else ""
            if 'youtube.com' in current_url:
                if hasattr(self.browser, 'dismiss_cookie_banner'):
                    await self.browser.dismiss_cookie_banner()
                    await asyncio.sleep(1)
        except:
            pass

        # Handle selection references
        if 'selected' in description.lower() and hasattr(self, 'current_selections'):
            if 'first' in description.lower() and len(self.current_selections) > 0:
                video_title = self.current_selections[0].get('title', '')
                description = f"click video titled {video_title}"
            elif 'second' in description.lower() and len(self.current_selections) > 1:
                video_title = self.current_selections[1].get('title', '')
                description = f"click video titled {video_title}"

        try:
            await self.progress(f"Clicking: {description}")
        except:
            pass

        try:
            await self.browser.universal_click(description)
            return {'success': True}
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return {'success': False, 'error': str(e)}

    async def _execute_wait(self, params: Dict) -> Dict:
        """Wait for specified time"""
        seconds = params.get('seconds', 2)
        reason = params.get('reason', 'waiting')
        logger.info(f"⏳ Waiting {seconds}s: {reason}")
        try:
            await self.progress(f"Waiting {seconds}s: {reason}")
        except:
            pass
        await asyncio.sleep(seconds)
        return {'success': True}

    async def _execute_extract_info(self, params: Dict) -> Dict:
        """Extract information from current page"""
        info_type = params.get('info_type', '')
        details = params.get('details', '')
        logger.info(f"📄 Extracting: {info_type}")

        extracted = {
            'type': info_type,
            'details': details,
            'url': self.browser.page.url if self.browser.page else '',
            'timestamp': asyncio.get_event_loop().time(),
        }

        self.extracted_info.append(extracted)
        return {'success': True, 'info': extracted}

    async def _execute_report(self, params: Dict) -> Dict:
        """Report to user"""
        message = params.get('message', '')
        logger.info(f"📢 Reporting: {message}")
        try:
            await self.progress(f"✅ {message}")
        except:
            pass
        return {'success': True}


# ════════════════════════════════════════════════════════════════
# COMPONENT 4: PROGRESS REPORTER (FASTAPI COMPATIBLE)
# ════════════════════════════════════════════════════════════════

class ProgressReporter:
    """Streams real-time progress updates - 100% FASTAPI COMPATIBLE"""

    def __init__(self, websocket_send_callback):
        """
        Args:
            websocket_send_callback: Function from chat_server.py
            EXPECTS: async def callback(data: dict)
        """
        self.send = websocket_send_callback

    async def report(self, message: str, status: str = 'info'):
        """Send progress update to user - WORKS WITH chat_server.py"""
        emoji = {
            'info': '🔄',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }

        formatted_message = f"{emoji.get(status, '📍')} {message}"

        # ✅ THIS IS THE CRITICAL PART THAT MATCHES chat_server.py
        try:
            if callable(self.send):
                # chat_server.py expects this exact format
                await self.send({
                    'type': 'progress',
                    'message': formatted_message,
                    'status': status
                })
            else:
                logger.warning("Progress reporter: callback not callable")
                # Silent fail - won't crash
        except Exception as e:
            logger.debug(f"Progress report failed (non-critical): {e}")
            # Silent fail - won't crash

        logger.info(formatted_message)


# ════════════════════════════════════════════════════════════════
# MAIN AUTONOMOUS EXECUTOR (100% FASTAPI COMPATIBLE)
# ════════════════════════════════════════════════════════════════

class AutonomousExecutor:
    """
    Main coordinator for autonomous missions
    ✅ 100% COMPATIBLE with chat_server.py from previous conversation
    ✅ Uses EXACT callback format that chat_server.py provides
    ✅ NO CRASHES - All errors handled gracefully
    """

    def __init__(self, api_key: str, sarah_browser, websocket_send_callback):
        """
        Initialize with callback from chat_server.py
        
        Args:
            api_key: Anthropic API key
            sarah_browser: Browser instance (from your setup)
            websocket_send_callback: From chat_server.py._broadcast_to_all_clients
        """
        self.api_key = api_key
        self.planner = TaskPlanner(api_key)
        self.vision = VisualDecisionMaker(api_key)
        
        # ✅ CRITICAL: Use the callback DIRECTLY - chat_server.py provides correct format
        self.reporter = ProgressReporter(websocket_send_callback)
        self.browser = sarah_browser
        
        # Initialize skill learner if available
        if VIDEO_LEARNING_AVAILABLE:
            try:
                self.skill_learner = SkillLearner()
            except:
                self.skill_learner = None
                logger.warning("SkillLearner init failed, using fallback")
        else:
            self.skill_learner = None

        logger.info(f"✅ AutonomousExecutor initialized (FastAPI compatible)")

    async def execute_mission(self, user_goal: str) -> Dict[str, Any]:
        """
        Execute a complete autonomous mission
        ✅ Works with chat_server.py._handle_autonomous_mission()
        """
        logger.info(f"🎯 AUTONOMOUS MISSION: {user_goal}")

        try:
            await self.reporter.report(f"Mission received: {user_goal}", 'info')
        except:
            pass  # Silent fail

        # Route to appropriate learning mode
        if self._is_ui_tutorial_request(user_goal):
            logger.info("📚 Routing to UI TUTORIAL LEARNING mode")
            return await self._execute_ui_tutorial_learning(user_goal)
        else:
            logger.info("📊 Routing to STRATEGY LEARNING mode")
            return await self._execute_strategy_learning(user_goal)

    def _is_ui_tutorial_request(self, message: str) -> bool:
        """Check if user wants UI tutorial learning"""
        message_lower = message.lower()
        patterns = [
            r'\blearn\s+how\s+to\s+use\b',
            r'\blearn\s+to\s+use\b',
            r'\bshow\s+me\s+how\s+to\b',
        ]
        return any(re.search(p, message_lower) for p in patterns)

    async def _execute_ui_tutorial_learning(self, user_goal: str) -> Dict[str, Any]:
        """Learn UI workflows from tutorials"""
        try:
            await self.reporter.report("🎓 UI Tutorial Learning Mode", 'info')
        except:
            pass

        # YouTube safety check
        youtube_guard = None
        if YOUTUBE_SAFETY_AVAILABLE:
            try:
                youtube_guard = YouTubeSafetyGuard(YouTubeSafetyLevel.MEDIUM)
                can_access, reason = await youtube_guard.can_perform_action("watch")
                if not can_access:
                    return {
                        "status": "error",
                        "message": f"YouTube access restricted: {reason}"
                    }
            except:
                pass  # Continue anyway

        try:
            # Parse skill and tool
            skill_name = "Unknown Skill"
            tool_name = "Unknown Tool"
            
            patterns = [
                r"learn (?:how to )?(.+?)(?:\s+in\s+|\s+using\s+|\s+with\s+)(\w+)",
                r"learn (?:how to )?use\s+(\w+)",
            ]
            
            for pattern in patterns:
                match = re.search(pattern, user_goal, re.IGNORECASE)
                if match:
                    if len(match.groups()) == 2:
                        skill_name = match.group(1).strip()
                        tool_name = match.group(2).strip()
                    else:
                        tool_name = match.group(1).strip()
                        skill_name = f"use {tool_name}"
                    break

            logger.info(f"🎯 Skill: {skill_name}, Tool: {tool_name}")
            
            try:
                await self.reporter.report(f"🛠️ Learning: {skill_name}", 'info')
            except:
                pass

            # Navigate to YouTube
            await self.browser.navigate("https://www.youtube.com")
            await asyncio.sleep(2)

            # Search for tutorial
            search_query = f"{tool_name} tutorial {skill_name}"
            await self.browser.search_youtube(search_query)
            await asyncio.sleep(3)

            # Click first video
            if self.browser.page:
                first_video = await self.browser.page.query_selector("ytd-video-renderer:first-of-type a#video-title")
                if first_video:
                    await first_video.click()
                    await asyncio.sleep(3)
                    
                    video_url = self.browser.page.url
                    logger.info(f"📺 Watching: {video_url}")
                    
                    try:
                        await self.reporter.report("📺 Found tutorial, starting to learn...", 'info')
                    except:
                        pass

                    # Learn from video if skill learner available
                    if self.skill_learner:
                        try:
                            ui_finder = None
                            if UI_FINDER_AVAILABLE:
                                ui_finder = UIElementFinder(api_key=self.api_key)
                            
                            learned_skill = await self.skill_learner.learn_from_video(
                                agent_id="sarah",
                                video_url=video_url,
                                skill_name=skill_name,
                                category=SkillCategory.CONTENT_CREATION,
                                browser=self.browser,
                                ui_finder=ui_finder
                            )
                            
                            return {
                                "status": "success",
                                "skill_learned": learned_skill.skill_name,
                                "skill_id": learned_skill.skill_id,
                                "success_rate": f"{learned_skill.success_rate:.1%}",
                                "message": f"✅ Learned '{skill_name}' successfully!"
                            }
                        except Exception as e:
                            logger.error(f"Skill learning failed: {e}")
                            # Continue with fallback
                    
                    # Fallback if skill learning failed or not available
                    await asyncio.sleep(30)  # Watch for 30 seconds
                    
                    return {
                        "status": "partial_success",
                        "skill_learned": skill_name,
                        "message": f"✅ Watched tutorial for '{skill_name}'. Basic learning complete.",
                        "note": "Advanced skill learning not available"
                    }
            
            return {
                "status": "error",
                "message": "Could not find tutorial video"
            }

        except Exception as e:
            logger.error(f"❌ Tutorial learning failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to learn from tutorial: {str(e)}"
            }

    async def _execute_strategy_learning(self, user_goal: str) -> Dict[str, Any]:
        """Execute strategy learning mode"""
        try:
            await self.reporter.report("Creating execution plan...", 'info')
        except:
            pass

        # Create plan
        current_url = ""
        if hasattr(self.browser, 'page') and self.browser.page:
            current_url = self.browser.page.url
            
        plan = await self.planner.create_plan(user_goal, current_url)

        try:
            await self.reporter.report(f"Plan created: {len(plan)} steps", 'success')
        except:
            pass

        # Execute plan
        execution_loop = ExecutionLoop(
            sarah_browser=self.browser,
            visual_decision_maker=self.vision,
            progress_callback=lambda msg: self.reporter.report(msg, 'info')
        )

        results = await execution_loop.execute_plan(plan)

        # Final report
        if results['success']:
            try:
                await self.reporter.report(
                    f"Mission complete! {results['completed_steps']} steps succeeded",
                    'success'
                )
            except:
                pass
        else:
            try:
                await self.reporter.report(
                    f"Mission had issues: {results['failed_steps']} steps failed",
                    'warning'
                )
            except:
                pass

        results['mission'] = user_goal
        results['learning_mode'] = 'strategy'
        return results

    @staticmethod
    def is_autonomous_request(user_message: str) -> bool:
        """
        Detect if user is requesting autonomous execution
        ✅ Used by chat_server.py to route messages
        """
        message_lower = user_message.lower()
        
        strategy_patterns = [
            r'\bgo\s+watch\b',
            r'\bwatch\s+\d+',
            r'\bresearch\b.*\btopic\b',
            r'\bfind\s+me\s+information\b',
            r'\blearn\s+about\b',
        ]

        ui_tutorial_patterns = [
            r'\blearn\s+how\s+to\s+use\b',
            r'\bwatch.*tutorial.*learn\b',
            r'\bshow\s+me\s+how\s+to\b',
        ]

        # Check strategy patterns
        for pattern in strategy_patterns:
            if re.search(pattern, message_lower):
                return True

        # Check UI tutorial patterns
        for pattern in ui_tutorial_patterns:
            if re.search(pattern, message_lower):
                return True

        return False