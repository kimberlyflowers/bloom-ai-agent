"""
VIDEO TUTORIAL SYNC - Sarah's Learning Engine 🎓

Watches UI tutorials and learns to replicate the workflows.

Example:
    Video: "How to edit videos in CapCut"

    Sarah:
    1. Plays video, extracts transcript with timestamps
    2. For each instruction:
       - "Open CapCut" → Takes screenshot, finds button, clicks
       - "Click New Project" → Takes screenshot, finds button, clicks
       - "Import video" → Takes screenshot, finds button, clicks
       ...
    3. Saves complete workflow for future use
    4. Can now execute "edit_video_in_capcut()" without tutorial

This is how Sarah learns to OPERATE tools, not just know about them!
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from youtube_transcript_api import YouTubeTranscriptApi
from src.learned_workflows import LearnedWorkflow, WorkflowStep
from src.ui_element_finder import UIElementFinder, ActionInstructionParser

logger = logging.getLogger(__name__)


class VideoTutorialLearner:
    """
    Learns workflows from UI tutorial videos

    This is the core of Sarah's ability to learn new tools.
    """

    def __init__(
        self,
        anthropic_api_key: str,
        browser,
        progress_callback=None
    ):
        self.ui_finder = UIElementFinder(anthropic_api_key)
        self.browser = browser
        self.progress = progress_callback or (lambda msg: None)
        self.instruction_parser = ActionInstructionParser()

    async def learn_from_tutorial(
        self,
        video_url: str,
        workflow_name: str,
        tool_name: str,
        description: str = ""
    ) -> Optional[LearnedWorkflow]:
        """
        Watch a UI tutorial and learn the workflow

        Args:
            video_url: YouTube URL of tutorial
            workflow_name: Name to save workflow as (e.g., "create_heygen_video")
            tool_name: Tool being learned (e.g., "HeyGen", "CapCut")
            description: Description of what this workflow does

        Returns:
            LearnedWorkflow if successful, None otherwise
        """
        logger.info(f"🎓 Learning from tutorial: {video_url}")
        await self.progress(f"Starting tutorial learning: {description}")

        # Step 1: Extract video ID and get transcript
        video_id = self._extract_video_id(video_url)
        if not video_id:
            logger.error("❌ Invalid YouTube URL")
            return None

        await self.progress("Extracting tutorial transcript...")
        transcript = await self._get_transcript_with_timestamps(video_id)

        if not transcript:
            logger.error("❌ Could not get transcript")
            return None

        logger.info(f"📜 Transcript extracted: {len(transcript)} segments")

        # Step 2: Parse transcript for actionable instructions
        await self.progress("Identifying action steps...")
        action_instructions = self._extract_action_instructions(transcript)

        logger.info(f"🎯 Found {len(action_instructions)} action instructions")

        # Step 3: Create workflow
        workflow = LearnedWorkflow(
            name=workflow_name,
            tool=tool_name,
            description=description,
            source_video=video_url
        )

        # Step 4: Learn each step
        await self.progress(f"Learning {len(action_instructions)} steps...")

        for i, (timestamp, instruction) in enumerate(action_instructions):
            step_num = i + 1
            logger.info(f"📍 Step {step_num}/{len(action_instructions)}: {instruction}")
            await self.progress(f"Learning step {step_num}: {instruction}")

            # Parse the instruction
            parsed = self.instruction_parser.parse(instruction)

            if not parsed['is_actionable']:
                logger.info(f"⏭️ Skipping non-actionable: {instruction}")
                continue

            # Learn this step
            learned_step = await self._learn_step(
                instruction=instruction,
                action_type=parsed['action'],
                target=parsed.get('target'),
                text_input=parsed.get('input'),
                timestamp=timestamp,
                step_number=step_num
            )

            if learned_step:
                # Add to workflow
                workflow.steps.append(learned_step)

                # Small delay between steps
                await asyncio.sleep(1)

        # Step 5: Save workflow
        if workflow.steps:
            workflow.save()
            logger.info(f"✅ Learned workflow: {workflow_name} ({len(workflow.steps)} steps)")
            await self.progress(f"✅ Learned {len(workflow.steps)} steps!")
            return workflow
        else:
            logger.warning("⚠️ No steps learned")
            return None

    async def _learn_step(
        self,
        instruction: str,
        action_type: str,
        target: Optional[str],
        text_input: Optional[str],
        timestamp: float,
        step_number: int
    ) -> Optional[WorkflowStep]:
        """
        Learn a single step from the tutorial

        Args:
            instruction: What the tutorial said to do
            action_type: Type of action (click, type, etc.)
            target: What to interact with
            text_input: Text to type (if applicable)
            timestamp: When this happens in video
            step_number: Step number in sequence

        Returns:
            WorkflowStep if learned successfully
        """
        try:
            # Take screenshot of current state
            screenshot = await self.browser.take_screenshot()

            if action_type == 'click' or action_type == 'select':
                # Find the element to click
                element_info = await self.ui_finder.find_element(
                    screenshot=screenshot,
                    instruction=instruction
                )

                if element_info and element_info.get('found'):
                    # Click it
                    coords = element_info.get('coordinates')
                    if coords:
                        await self.browser.page.mouse.click(coords['x'], coords['y'])
                        logger.info(f"✅ Clicked: {target} at ({coords['x']}, {coords['y']})")

                        # Create step
                        return WorkflowStep(
                            step_number=step_number,
                            instruction=instruction,
                            action=action_type,
                            target=target or "element",
                            location=coords,
                            element_description=element_info.get('description', ''),
                            timestamp=timestamp,
                            verification=None  # TODO: Could add verification
                        )

            elif action_type == 'type':
                # Type text
                if text_input:
                    await self.browser.page.keyboard.type(text_input)
                    logger.info(f"⌨️ Typed: {text_input}")

                    return WorkflowStep(
                        step_number=step_number,
                        instruction=instruction,
                        action='type',
                        target=target or "input field",
                        text_input=text_input,
                        timestamp=timestamp
                    )

            elif action_type == 'navigate':
                # Navigate to URL/page
                if target:
                    # Check if target is a URL
                    if 'http' in target or '.com' in target or '.org' in target:
                        await self.browser.navigate(target)
                        logger.info(f"🌐 Navigated to: {target}")

                        return WorkflowStep(
                            step_number=step_number,
                            instruction=instruction,
                            action='navigate',
                            target=target,
                            text_input=target,  # Store URL here
                            timestamp=timestamp
                        )

            elif action_type == 'wait':
                # Wait step
                await asyncio.sleep(2)

                return WorkflowStep(
                    step_number=step_number,
                    instruction=instruction,
                    action='wait',
                    target=None,
                    location={'seconds': 2},
                    timestamp=timestamp
                )

            return None

        except Exception as e:
            logger.error(f"❌ Failed to learn step: {e}")
            return None

    async def _get_transcript_with_timestamps(
        self,
        video_id: str
    ) -> Optional[List[Tuple[float, str]]]:
        """
        Get YouTube transcript with timestamps

        Args:
            video_id: YouTube video ID

        Returns:
            List of (timestamp, text) tuples
        """
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)

            # Convert to (timestamp, text) tuples
            result = []
            for entry in transcript:
                timestamp = entry['start']
                text = entry['text']
                result.append((timestamp, text))

            return result

        except Exception as e:
            logger.error(f"❌ Failed to get transcript: {e}")
            return None

    def _extract_action_instructions(
        self,
        transcript: List[Tuple[float, str]]
    ) -> List[Tuple[float, str]]:
        """
        Extract actionable instructions from transcript

        Args:
            transcript: List of (timestamp, text) tuples

        Returns:
            List of (timestamp, instruction) tuples for actionable steps
        """
        action_instructions = []

        # Action verbs to look for
        action_verbs = [
            'click', 'press', 'tap', 'hit',
            'type', 'enter', 'input', 'write',
            'select', 'choose', 'pick',
            'drag', 'drop',
            'go to', 'navigate', 'open', 'visit',
            'scroll', 'swipe'
        ]

        for timestamp, text in transcript:
            text_lower = text.lower()

            # Check if this contains an action verb
            if any(verb in text_lower for verb in action_verbs):
                # This might be an instruction
                action_instructions.append((timestamp, text.strip()))

        return action_instructions

    def _extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract YouTube video ID from URL

        Args:
            url: YouTube URL

        Returns:
            Video ID or None
        """
        # Pattern 1: https://www.youtube.com/watch?v=VIDEO_ID
        match = re.search(r'[?&]v=([^&]+)', url)
        if match:
            return match.group(1)

        # Pattern 2: https://youtu.be/VIDEO_ID
        match = re.search(r'youtu\.be/([^?&]+)', url)
        if match:
            return match.group(1)

        return None


class TutorialLearningDetector:
    """
    Detects if user wants Sarah to learn from a UI tutorial

    Examples:
        "Learn how to use CapCut" → UI tutorial learning
        "Watch a HeyGen tutorial and learn it" → UI tutorial learning
        "Show me how to edit in Canva" → UI tutorial learning
        "Research TikTok strategies" → Strategy learning (NOT tutorial)
    """

    @staticmethod
    def is_ui_tutorial_request(user_message: str) -> bool:
        """
        Check if user wants Sarah to learn from a UI tutorial

        Args:
            user_message: User's message

        Returns:
            True if this is a UI tutorial learning request
        """
        message_lower = user_message.lower()

        # Strong indicators of UI tutorial learning
        ui_tutorial_patterns = [
            r'learn\s+how\s+to\s+use',
            r'watch.*tutorial.*learn',
            r'show\s+me\s+how\s+to',
            r'teach\s+yourself.*to\s+use',
            r'figure\s+out\s+how\s+to',
            r'learn\s+to\s+operate',
            r'learn\s+.*\s+(capcut|heygen|canva|tiktok|instagram)',
        ]

        for pattern in ui_tutorial_patterns:
            if re.search(pattern, message_lower):
                return True

        return False

    @staticmethod
    def extract_tool_name(user_message: str) -> Optional[str]:
        """
        Extract tool name from request

        Args:
            user_message: User's message

        Returns:
            Tool name (e.g., "CapCut", "HeyGen") or None
        """
        # Common tools
        tools = {
            'capcut': 'CapCut',
            'heygen': 'HeyGen',
            'canva': 'Canva',
            'tiktok': 'TikTok',
            'instagram': 'Instagram',
            'photoshop': 'Photoshop',
            'premiere': 'Adobe Premiere',
            'after effects': 'After Effects',
            'figma': 'Figma',
        }

        message_lower = user_message.lower()

        for tool_key, tool_name in tools.items():
            if tool_key in message_lower:
                return tool_name

        return None
