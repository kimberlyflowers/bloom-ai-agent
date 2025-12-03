"""
Self-Learning from Video Tutorials - System #26

🎓 AGENTS TEACH THEMSELVES NEW SKILLS!

How it works:
1. Agent finds YouTube tutorial (e.g., "How to create UGC ad with Arcade")
2. Watches video, Claude Vision analyzes each frame
3. Extracts step-by-step instructions
4. Follows along with browser automation
5. Records workflow with screenshots
6. Saves as "learned skill" in memory
7. Can repeat skill anytime with new context!

Example:
- Sarah watches: "How to create UGC video ad"
- Sarah learns: Complete workflow
- Sarah creates: UGC ad with HER AI face promoting BLOOM
- Sarah posts: TikTok, Instagram Reels
- Result: Professional UGC content at scale!

When one agent learns → ALL agents can do it (via Learning Network)!
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Protocol
from enum import Enum
from pathlib import Path
import json
import time
import asyncio
import os
import re
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# ============================================================================
# INTERFACE DEFINITIONS (To avoid circular imports)
# ============================================================================

class BrowserInterface(Protocol):
    """Protocol for browser interaction"""
    async def navigate(self, url: str) -> None:
        ...
    
    async def take_screenshot(self):
        ...
    
    @property
    def page(self):
        ...
    
    async def __aenter__(self):
        ...
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...


class UIElementFinder(Protocol):
    """Protocol for finding UI elements using Vision"""
    async def find_element(self, screenshot, instruction: str) -> Dict[str, Any]:
        ...
    
    async def analyze_ui_state(self, screenshot, question: str) -> str:
        ...


# ============================================================================
# CONFIGURATION
# ============================================================================

SKILLS_DIR = Path("data/learned_skills")
SKILLS_DIR.mkdir(parents=True, exist_ok=True)

WORKFLOWS_DIR = Path("data/skill_workflows")
WORKFLOWS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# LEARNED SKILL MODELS
# ============================================================================

class SkillCategory(Enum):
    """Categories of learnable skills"""
    VIDEO_CREATION = "video_creation"
    GRAPHIC_DESIGN = "graphic_design"
    PLATFORM_MASTERY = "platform_mastery"
    CONTENT_CREATION = "content_creation"
    AUTOMATION_WORKFLOW = "automation_workflow"
    MARKETING_TECHNIQUE = "marketing_technique"
    SALES_PROCESS = "sales_process"
    TECHNICAL_SKILL = "technical_skill"


class StepType(Enum):
    """Types of steps in a tutorial"""
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SELECT = "select"
    UPLOAD = "upload"
    WAIT = "wait"
    VERIFY = "verify"
    EXTRACT = "extract"


@dataclass
class TutorialStep:
    """A single step from a tutorial"""
    step_number: int
    description: str
    action_type: StepType
    target: Optional[str] = None
    target_element: Optional[str] = None
    input_value: Optional[str] = None
    expected_result: Optional[str] = None
    screenshot_before: Optional[str] = None
    screenshot_after: Optional[str] = None
    timing_notes: Optional[str] = None
    timestamp: Optional[float] = None
    pro_tips: List[str] = field(default_factory=list)
    common_mistakes: List[str] = field(default_factory=list)
    success: Optional[bool] = None

    def __post_init__(self):
        if self.target_element is None and self.target is not None:
            self.target_element = self.target


@dataclass
class LearnedSkill:
    """A skill learned from a video tutorial"""
    skill_id: str
    skill_name: str
    category: SkillCategory
    agent_id: str
    video_url: str
    video_title: str = ""
    video_creator: str = ""
    tutorial_quality: float = 0.0
    tutorial_steps: List[TutorialStep] = field(default_factory=list)
    required_tools: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    times_practiced: int = 0
    success_rate: float = 0.0
    avg_duration_seconds: float = 0.0
    variable_inputs: Dict[str, str] = field(default_factory=dict)
    output_description: str = ""
    shared_with_network: bool = False
    adopted_by: List[str] = field(default_factory=list)
    learned_at: datetime = field(default_factory=datetime.utcnow)
    last_practiced: Optional[datetime] = None
    clarity_score: float = 0.0
    replicability_score: float = 0.0
    usefulness_score: float = 0.0

    @property
    def learned_by(self) -> str:
        return self.agent_id
    
    @property
    def steps(self) -> List[TutorialStep]:
        return self.tutorial_steps
    
    @property
    def source_video_url(self) -> str:
        return self.video_url
    
    @property
    def times_executed(self) -> int:
        return self.times_practiced
    
    @property
    def last_used_date(self) -> Optional[datetime]:
        return self.last_practiced


@dataclass
class SkillExecution:
    """A specific execution of a learned skill"""
    execution_id: str
    skill_id: str
    agent_id: str
    context: Dict[str, Any]
    success: bool = False
    output: Optional[str] = None
    screenshots: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    errors: List[str] = field(default_factory=list)
    executed_at: datetime = field(default_factory=datetime.utcnow)


# ============================================================================
# VIDEO ANALYSIS
# ============================================================================

class VideoTutorialAnalyzer:
    """Analyze video tutorials to extract learnable steps"""
    
    def __init__(self):
        self.frame_interval = 2.0
        self.logger = logging.getLogger(__name__)

    async def get_transcript_with_timestamps(self, video_url: str) -> List[Dict[str, Any]]:
        """Extract real YouTube transcript with timestamps"""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
        except ImportError:
            self.logger.error("❌ youtube-transcript-api not installed")
            raise ImportError("Install with: pip install youtube-transcript-api")

        self.logger.info(f"📝 Extracting transcript from: {video_url}")

        # Extract video ID
        video_id = None
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:shorts\/)([0-9A-Za-z_-]{11})',
            r'^([0-9A-Za-z_-]{11})$'
        ]

        for pattern in patterns:
            match = re.search(pattern, video_url)
            if match:
                video_id = match.group(1)
                break

        if not video_id:
            raise ValueError(f"Invalid YouTube URL: {video_url}")

        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            self.logger.info(f"✅ Extracted {len(transcript_list)} transcript segments")
            return transcript_list
        except Exception as e:
            self.logger.error(f"❌ Failed to get transcript: {e}")
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                self.logger.info(f"✅ Extracted {len(transcript_list)} segments (auto-generated)")
                return transcript_list
            except Exception as e2:
                raise ValueError(f"Could not extract transcript: {e2}")

    async def parse_transcript_into_actions(self, transcript: List[Dict], skill_name: str) -> List[TutorialStep]:
        """Use Claude API to parse transcript into actionable UI steps"""
        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            self.logger.error("❌ anthropic not installed")
            raise ImportError("Install with: pip install anthropic")

        self.logger.info(f"🤖 Parsing transcript into actionable steps...")

        # Combine transcript
        full_transcript = "\n".join([
            f"[{entry['start']:.1f}s] {entry['text']}"
            for entry in transcript[:100]
        ])

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY required")

        client = AsyncAnthropic(api_key=api_key)

        prompt = f"""Extract actionable UI steps from this tutorial transcript:

Tutorial: {skill_name}

Transcript:
{full_transcript}

Return ONLY a JSON array of steps:
[
  {{
    "step_number": 1,
    "action_type": "CLICK",
    "description": "Click the Create button",
    "target_element": "Create button in top right",
    "input_value": null,
    "expected_result": "New project dialog opens",
    "timestamp": 15.5
  }}
]
"""

        try:
            response = await client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            steps_data = json.loads(response_text)
            self.logger.info(f"✅ Parsed {len(steps_data)} actionable steps")

            # Convert to TutorialStep objects
            tutorial_steps = []
            for step_data in steps_data:
                action_type_str = step_data["action_type"].upper()
                try:
                    action_type = StepType[action_type_str]
                except KeyError:
                    self.logger.warning(f"⚠️  Unknown action type '{action_type_str}', defaulting to CLICK")
                    action_type = StepType.CLICK

                tutorial_steps.append(TutorialStep(
                    step_number=step_data["step_number"],
                    action_type=action_type,
                    description=step_data["description"],
                    target_element=step_data.get("target_element"),
                    input_value=step_data.get("input_value"),
                    expected_result=step_data.get("expected_result"),
                    timing_notes=f"Occurs at {step_data.get('timestamp', 0)}s in video",
                    timestamp=step_data.get("timestamp")
                ))

            return tutorial_steps

        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Failed to parse JSON: {e}")
            raise
        except Exception as e:
            self.logger.error(f"❌ Failed to parse transcript: {e}")
            raise

    async def analyze_tutorial(
        self,
        video_url: str,
        skill_name: str,
        category: SkillCategory
    ) -> List[TutorialStep]:
        """Analyze YouTube tutorial and extract steps"""
        self.logger.info(f"🎥 Analyzing tutorial: {skill_name}")

        try:
            transcript = await self.get_transcript_with_timestamps(video_url)
            if not transcript:
                raise ValueError("No transcript available")

            tutorial_steps = await self.parse_transcript_into_actions(transcript, skill_name)
            self.logger.info(f"✅ Analysis complete: {len(tutorial_steps)} steps identified")
            return tutorial_steps
        except Exception as e:
            self.logger.error(f"❌ Tutorial analysis failed: {e}")
            raise


# ============================================================================
# SKILL LEARNER
# ============================================================================

class SkillLearner:
    """Learn skills by following tutorials"""
    
    def __init__(self):
        self.analyzer = VideoTutorialAnalyzer()
        self.learned_skills: Dict[str, LearnedSkill] = {}
        self.logger = logging.getLogger(__name__)
        self.max_retries = 3
        self.retry_delay = 2.0

    def _is_transient_error(self, error: Exception) -> bool:
        """Check if error is transient"""
        transient_keywords = ["timeout", "connection", "network", "rate limit", "503", "502", "429"]
        error_str = str(error).lower()
        return any(keyword in error_str for keyword in transient_keywords)

    async def execute_tutorial_step(
        self,
        step: TutorialStep,
        browser: BrowserInterface,
        ui_finder: UIElementFinder
    ) -> Tuple[bool, Optional[str]]:
        """Execute a single tutorial step"""
        self.logger.info(f"▶️  Executing: {step.description}")

        try:
            if step.action_type == StepType.NAVIGATE:
                url = step.input_value or step.target_element or step.target
                if url:
                    await browser.navigate(url)
                    await asyncio.sleep(2)
                    self.logger.info(f"✅ Navigated to: {url}")
                    return (True, None)
                return (False, "No URL provided for navigation")

            elif step.action_type == StepType.CLICK:
                screenshot = await browser.take_screenshot()
                element_info = await ui_finder.find_element(
                    screenshot=screenshot,
                    instruction=f"Find the {step.target_element}"
                )

                if element_info and element_info.get("found"):
                    coords = element_info.get("coordinates", {})
                    x = coords.get("x")
                    y = coords.get("y")

                    if x is not None and y is not None:
                        await browser.page.mouse.click(x, y)
                        await asyncio.sleep(1.5)

                        if step.expected_result:
                            await asyncio.sleep(0.5)
                            new_screenshot = await browser.take_screenshot()
                            verification = await ui_finder.analyze_ui_state(
                                screenshot=new_screenshot,
                                question=f"Did this happen: {step.expected_result}?"
                            )
                            self.logger.info(f"🔍 Verification: {verification}")

                        self.logger.info(f"✅ Click executed")
                        return (True, None)
                    else:
                        return (False, "No coordinates returned")
                else:
                    return (False, f"Could not find element: {step.target_element}")

            elif step.action_type == StepType.TYPE:
                screenshot = await browser.take_screenshot()
                element_info = await ui_finder.find_element(
                    screenshot=screenshot,
                    instruction=f"Find the {step.target_element} (input field)"
                )

                if element_info and element_info.get("found"):
                    coords = element_info.get("coordinates", {})
                    x = coords.get("x")
                    y = coords.get("y")

                    if x is not None and y is not None:
                        await browser.page.mouse.click(x, y)
                        await asyncio.sleep(0.5)
                        
                        text_to_type = step.input_value or ""
                        if text_to_type:
                            await browser.page.keyboard.type(text_to_type, delay=50)
                            await asyncio.sleep(1)
                        
                        self.logger.info(f"✅ Typed: {text_to_type}")
                        return (True, None)
                    else:
                        return (False, "No coordinates for input field")
                else:
                    return (False, f"Could not find input field: {step.target_element}")

            elif step.action_type == StepType.WAIT:
                wait_seconds = float(step.input_value) if step.input_value else 2.0
                self.logger.info(f"⏸️  Waiting {wait_seconds} seconds...")
                await asyncio.sleep(wait_seconds)
                return (True, None)

            elif step.action_type == StepType.SELECT:
                screenshot = await browser.take_screenshot()
                element_info = await ui_finder.find_element(
                    screenshot=screenshot,
                    instruction=f"Find the {step.target_element} (dropdown)"
                )

                if element_info and element_info.get("found"):
                    coords = element_info.get("coordinates", {})
                    x = coords.get("x")
                    y = coords.get("y")

                    if x and y:
                        await browser.page.mouse.click(x, y)
                        await asyncio.sleep(1)
                        self.logger.info(f"✅ Selected from: {step.target_element}")
                        return (True, None)
                    else:
                        return (False, "No dropdown coordinates")
                else:
                    return (False, f"Could not find dropdown: {step.target_element}")

            elif step.action_type == StepType.VERIFY:
                screenshot = await browser.take_screenshot()
                verification = await ui_finder.analyze_ui_state(
                    screenshot=screenshot,
                    question=f"Is this visible: {step.expected_result}?"
                )
                success = "yes" in verification.lower()
                self.logger.info(f"🔍 Verification: {verification}")
                return (success, None if success else "Verification failed")

            else:
                error = f"Action type {step.action_type} not implemented"
                self.logger.warning(f"⚠️  {error}")
                return (False, error)

        except Exception as e:
            error = f"Exception during execution: {str(e)}"
            self.logger.error(f"❌ {error}")
            return (False, error)

    async def execute_tutorial_step_with_retry(
        self,
        step: TutorialStep,
        browser: BrowserInterface,
        ui_finder: UIElementFinder,
        retry_count: int = 0
    ) -> Tuple[bool, Optional[str]]:
        """Execute step with retry logic"""
        try:
            return await asyncio.wait_for(
                self.execute_tutorial_step(step, browser, ui_finder),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            self.logger.error(f"⏱️  Step timed out")

            if retry_count < self.max_retries:
                self.logger.info(f"🔄 Retrying... ({retry_count + 1}/{self.max_retries})")
                await asyncio.sleep(self.retry_delay)
                return await self.execute_tutorial_step_with_retry(
                    step, browser, ui_finder, retry_count + 1
                )
            else:
                return (False, "Step timed out after retries")

        except Exception as e:
            self.logger.error(f"❌ Step execution failed: {e}")

            if retry_count < self.max_retries and self._is_transient_error(e):
                self.logger.info(f"🔄 Transient error detected, retrying...")
                await asyncio.sleep(self.retry_delay)
                return await self.execute_tutorial_step_with_retry(
                    step, browser, ui_finder, retry_count + 1
                )
            else:
                return (False, str(e))

    async def learn_from_video(
        self,
        agent_id: str,
        video_url: str,
        skill_name: str,
        category: SkillCategory,
        browser: BrowserInterface,
        ui_finder: UIElementFinder
    ) -> LearnedSkill:
        """Learn a skill by watching and following a YouTube tutorial"""
        import time
        from datetime import datetime

        self.logger.info(f"🎓 Learning '{skill_name}' from tutorial...")

        try:
            # 1. Analyze tutorial
            tutorial_steps = await self.analyzer.analyze_tutorial(
                video_url=video_url,
                skill_name=skill_name,
                category=category
            )

            if not tutorial_steps:
                raise ValueError("No actionable steps found")

            self.logger.info(f"✅ Found {len(tutorial_steps)} steps to learn")

            # 2. Execute steps
            successful_steps = 0
            failed_steps = []

            for i, step in enumerate(tutorial_steps, 1):
                self.logger.info(f"\n📍 Step {i}/{len(tutorial_steps)}: {step.description}")

                success, error_msg = await self.execute_tutorial_step_with_retry(
                    step=step,
                    browser=browser,
                    ui_finder=ui_finder
                )

                step.success = success

                if success:
                    successful_steps += 1
                    self.logger.info(f"✅ Step {i} completed")
                else:
                    failed_steps.append(step)
                    self.logger.error(f"❌ Step {i} failed: {error_msg}")

                await asyncio.sleep(0.5)

            # 3. Calculate success rate
            success_rate = successful_steps / len(tutorial_steps) if tutorial_steps else 0

            # 4. Create LearnedSkill object
            skill_id = f"{skill_name.lower().replace(' ', '_')}_{int(time.time())}"

            learned_skill = LearnedSkill(
                skill_id=skill_id,
                skill_name=skill_name,
                category=category,
                agent_id=agent_id,
                video_url=video_url,
                video_title=f"Tutorial: {skill_name}",
                video_creator="YouTube",
                tutorial_steps=tutorial_steps,
                required_tools=["Browser", "Claude Vision"],
                success_rate=success_rate,
                times_practiced=1,
                last_practiced=datetime.utcnow()
            )

            # 5. Save to memory and disk
            self.learned_skills[skill_id] = learned_skill
            await self.save_skill(learned_skill)

            self.logger.info(f"\n🎉 Successfully learned '{skill_name}' with {success_rate:.1%} success rate!")
            return learned_skill

        except Exception as e:
            self.logger.error(f"❌ Failed to learn from video: {e}")
            raise

    async def save_skill(self, skill: LearnedSkill):
        """Save a learned skill to disk"""
        try:
            skill_file = SKILLS_DIR / f"{skill.skill_id}.json"

            skill_data = {
                "skill_id": skill.skill_id,
                "skill_name": skill.skill_name,
                "category": skill.category.value,
                "agent_id": skill.agent_id,
                "video_url": skill.video_url,
                "video_title": skill.video_title,
                "video_creator": skill.video_creator,
                "tutorial_steps": [
                    {
                        "step_number": s.step_number,
                        "description": s.description,
                        "action_type": s.action_type.value,
                        "target": s.target,
                        "target_element": s.target_element,
                        "input_value": s.input_value,
                        "expected_result": s.expected_result,
                        "timing_notes": s.timing_notes,
                        "timestamp": s.timestamp,
                        "success": s.success
                    }
                    for s in skill.tutorial_steps
                ],
                "required_tools": skill.required_tools,
                "success_rate": skill.success_rate,
                "times_practiced": skill.times_practiced,
                "learned_at": skill.learned_at.isoformat(),
                "last_practiced": skill.last_practiced.isoformat() if skill.last_practiced else None
            }

            with open(skill_file, 'w') as f:
                json.dump(skill_data, f, indent=2)

            logger.info(f"💾 Saved skill to: {skill_file}")

        except Exception as e:
            logger.error(f"❌ Failed to save skill: {e}")

    async def load_skill(self, skill_id: str) -> Optional[LearnedSkill]:
        """Load a learned skill from disk"""
        try:
            skill_file = SKILLS_DIR / f"{skill_id}.json"

            if not skill_file.exists():
                return self.learned_skills.get(skill_id)

            with open(skill_file, 'r') as f:
                skill_data = json.load(f)

            from datetime import datetime

            tutorial_steps = [
                TutorialStep(
                    step_number=s["step_number"],
                    description=s["description"],
                    action_type=StepType[s["action_type"].upper()],
                    target=s.get("target"),
                    target_element=s.get("target_element"),
                    input_value=s.get("input_value"),
                    expected_result=s.get("expected_result"),
                    timing_notes=s.get("timing_notes"),
                    timestamp=s.get("timestamp"),
                    success=s.get("success")
                )
                for s in skill_data["tutorial_steps"]
            ]

            skill = LearnedSkill(
                skill_id=skill_data["skill_id"],
                skill_name=skill_data["skill_name"],
                category=SkillCategory[skill_data["category"].upper()],
                agent_id=skill_data["agent_id"],
                video_url=skill_data["video_url"],
                video_title=skill_data.get("video_title", ""),
                video_creator=skill_data.get("video_creator", ""),
                tutorial_steps=tutorial_steps,
                required_tools=skill_data.get("required_tools", []),
                success_rate=skill_data.get("success_rate", 0.0),
                times_practiced=skill_data.get("times_practiced", 0),
                learned_at=datetime.fromisoformat(skill_data["learned_at"]) if skill_data.get("learned_at") else datetime.utcnow(),
                last_practiced=datetime.fromisoformat(skill_data["last_practiced"]) if skill_data.get("last_practiced") else None
            )

            logger.info(f"✅ Loaded skill: {skill.skill_name}")
            return skill

        except Exception as e:
            logger.error(f"❌ Failed to load skill: {e}")
            return None

    async def execute_learned_skill(
        self,
        skill_id: str,
        browser: BrowserInterface,
        ui_finder: UIElementFinder,
        custom_inputs: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Execute a previously learned skill"""
        from datetime import datetime

        logger.info(f"▶️  Executing learned skill: {skill_id}")

        skill = await self.load_skill(skill_id)
        if not skill:
            raise ValueError(f"Skill not found: {skill_id}")

        logger.info(f"📋 Loaded skill: {skill.skill_name}")

        successful_steps = 0
        failed_steps = 0

        for i, step in enumerate(skill.tutorial_steps, 1):
            logger.info(f"\n📍 Step {i}/{len(skill.tutorial_steps)}: {step.description}")

            if custom_inputs and step.input_value:
                for key, value in custom_inputs.items():
                    if key.lower() in step.description.lower():
                        step.input_value = value
                        logger.info(f"📝 Using custom input: {value}")

            success, error_msg = await self.execute_tutorial_step_with_retry(
                step=step,
                browser=browser,
                ui_finder=ui_finder
            )

            if success:
                successful_steps += 1
                logger.info(f"✅ Step {i} completed")
            else:
                failed_steps += 1
                logger.error(f"❌ Step {i} failed: {error_msg}")

            await asyncio.sleep(0.5)

        skill.times_practiced += 1
        skill.last_practiced = datetime.utcnow()
        await self.save_skill(skill)

        execution_success_rate = successful_steps / len(skill.tutorial_steps) if skill.tutorial_steps else 0

        logger.info(f"\n📊 EXECUTION SUMMARY")
        logger.info(f"✅ Successful: {successful_steps}/{len(skill.tutorial_steps)}")
        logger.info(f"📈 Success rate: {execution_success_rate:.1%}")

        return {
            "status": "success" if execution_success_rate > 0.5 else "partial",
            "skill_name": skill.skill_name,
            "successful_steps": successful_steps,
            "failed_steps": failed_steps,
            "total_steps": len(skill.tutorial_steps),
            "success_rate": execution_success_rate,
        }


# ============================================================================
# SKILL LIBRARY MANAGER
# ============================================================================

class SkillLibrary:
    """Manage all learned skills across all agents"""
    
    def __init__(self):
        self.learner = SkillLearner()
        self.all_skills: Dict[str, LearnedSkill] = {}
        self.agent_skills: Dict[str, List[str]] = {}

    async def agent_learns_skill(
        self,
        agent_id: str,
        video_url: str,
        skill_name: str,
        category: SkillCategory,
        browser: BrowserInterface,
        ui_finder: UIElementFinder
    ) -> LearnedSkill:
        """Agent learns a new skill"""
        skill = await self.learner.learn_from_video(
            agent_id=agent_id,
            video_url=video_url,
            skill_name=skill_name,
            category=category,
            browser=browser,
            ui_finder=ui_finder
        )

        self.all_skills[skill.skill_id] = skill

        if agent_id not in self.agent_skills:
            self.agent_skills[agent_id] = []
        self.agent_skills[agent_id].append(skill.skill_id)

        return skill

    def get_skill_summary(self) -> str:
        """Get summary of all learned skills"""
        summary = f"\n{'='*80}\nLEARNED SKILLS LIBRARY\n{'='*80}\n\n"
        summary += f"📚 TOTAL SKILLS: {len(self.all_skills)}\n"

        by_category: Dict[SkillCategory, int] = {}
        for skill in self.all_skills.values():
            by_category[skill.category] = by_category.get(skill.category, 0) + 1

        summary += f"\n📊 BY CATEGORY:\n"
        for cat, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
            summary += f"   • {cat.value}: {count} skills\n"

        top_skills = sorted(
            self.all_skills.values(),
            key=lambda s: (s.success_rate, s.times_practiced),
            reverse=True
        )[:5]

        summary += f"\n🏆 TOP SKILLS:\n"
        for i, skill in enumerate(top_skills, 1):
            summary += f"\n   {i}. {skill.skill_name}\n"
            summary += f"      Category: {skill.category.value}\n"
            summary += f"      Success rate: {skill.success_rate:.0%}\n"
            summary += f"      Times practiced: {skill.times_practiced}\n"

        summary += f"\n{'='*80}\n"
        return summary


# ============================================================================
# WEBSOCKET SUPPORT
# ============================================================================

class WebSocketSkillServer:
    """WebSocket server for real-time skill learning updates"""
    
    def __init__(self, skill_library: SkillLibrary):
        self.skill_library = skill_library
        self.connected_clients = set()
        self.logger = logging.getLogger(__name__)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        for client in self.connected_clients:
            try:
                await client.send(json.dumps(message))
            except Exception as e:
                self.logger.error(f"Failed to send to client: {e}")

    async def handle_learning_progress(self, skill_id: str, step_number: int, total_steps: int, status: str):
        """Send learning progress update"""
        await self.broadcast({
            "type": "learning_progress",
            "skill_id": skill_id,
            "step": step_number,
            "total_steps": total_steps,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def handle_skill_completed(self, skill: LearnedSkill):
        """Send skill completion notification"""
        await self.broadcast({
            "type": "skill_completed",
            "skill_id": skill.skill_id,
            "skill_name": skill.skill_name,
            "agent_id": skill.agent_id,
            "success_rate": skill.success_rate,
            "steps_learned": len(skill.tutorial_steps),
            "timestamp": datetime.utcnow().isoformat()
        })


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print(" " * 15 + "🎓 VIDEO TUTORIAL LEARNING SYSTEM")
    print("=" * 80)

    print("\n🌟 Features:")
    print("   • YouTube transcript extraction")
    print("   • Claude AI step parsing")
    print("   • Browser automation with retry logic")
    print("   • Skill persistence and sharing")
    print("   • WebSocket support for real-time updates")
    print("   • Collective learning across agents")

    print("\n📋 Requirements:")
    print("   • ANTHROPIC_API_KEY environment variable")
    print("   • youtube-transcript-api: pip install youtube-transcript-api")
    print("   • anthropic: pip install anthropic")
    print("   • Browser automation setup")

    print("\n" + "="*80)
    print("Ready to learn from video tutorials! 🚀")
    print("=" * 80)