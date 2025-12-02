"""
UI ELEMENT FINDER - Sarah's Eyes 👁️

Uses Claude Vision to find UI elements on screen.

Example:
    Tutorial says: "Click the Export button"
    → Takes screenshot
    → Asks Claude Vision: "Where is the Export button?"
    → Returns: {"x": 1200, "y": 650, "description": "Blue button labeled 'Export' in bottom-right"}
    → Sarah clicks it

This enables Sarah to follow UI tutorials even when:
- Element positions change
- Different screen sizes
- Different UI themes/versions
- Elements don't have stable selectors
"""

import logging
import json
import base64
from io import BytesIO
from typing import Dict, Optional, Tuple, Any
import anthropic
from PIL import Image

logger = logging.getLogger(__name__)


class UIElementFinder:
    """
    Finds UI elements using Claude Vision API

    This is how Sarah "sees" the screen and understands where to click.
    """

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    async def find_element(
        self,
        screenshot: Image.Image,
        instruction: str,
        context: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Find a UI element on the screen

        Args:
            screenshot: PIL Image of current screen
            instruction: What to find (e.g., "Click the Export button")
            context: Optional context about where we are (e.g., "On CapCut main screen")

        Returns:
            Dict with:
                - found: bool
                - element_type: str (button, link, input, etc.)
                - text: str (label/text of element)
                - location: str (description of position)
                - coordinates: {"x": int, "y": int}
                - confidence: str (high, medium, low)
                - description: str (full description)

            Or None if not found
        """
        logger.info(f"👁️ Looking for: {instruction}")

        # Convert screenshot to base64
        screenshot_base64 = self._screenshot_to_base64(screenshot)

        # Build the vision prompt
        prompt = self._build_element_finder_prompt(instruction, context)

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1024,
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
                            "text": prompt
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

            if result.get('found'):
                logger.info(f"✅ Found element: {result.get('description', 'Unknown')}")
                return result
            else:
                logger.warning(f"⚠️ Element not found: {instruction}")
                return None

        except Exception as e:
            logger.error(f"❌ UI element finder failed: {e}")
            return None

    async def find_clickable_area(
        self,
        screenshot: Image.Image,
        target_description: str
    ) -> Optional[Tuple[int, int]]:
        """
        Find coordinates to click for a target element

        Args:
            screenshot: PIL Image of screen
            target_description: Description of what to click

        Returns:
            Tuple (x, y) coordinates or None if not found
        """
        result = await self.find_element(screenshot, target_description)

        if result and result.get('found') and result.get('coordinates'):
            coords = result['coordinates']
            return (coords['x'], coords['y'])

        return None

    async def verify_element_exists(
        self,
        screenshot: Image.Image,
        element_description: str
    ) -> bool:
        """
        Check if an element exists on screen

        Args:
            screenshot: PIL Image of screen
            element_description: What to look for

        Returns:
            True if element found, False otherwise
        """
        result = await self.find_element(screenshot, element_description)
        return result is not None and result.get('found', False)

    async def analyze_ui_state(
        self,
        screenshot: Image.Image,
        question: str
    ) -> Optional[str]:
        """
        Ask a general question about the UI state

        Args:
            screenshot: PIL Image of screen
            question: Question about the UI (e.g., "What page am I on?", "Is the video loaded?")

        Returns:
            Answer string or None
        """
        logger.info(f"🤔 UI question: {question}")

        screenshot_base64 = self._screenshot_to_base64(screenshot)

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=512,
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
                            "text": f"""Analyze this screenshot and answer:

{question}

Provide a concise, direct answer."""
                        }
                    ]
                }]
            )

            answer = response.content[0].text.strip()
            logger.info(f"💡 Answer: {answer}")
            return answer

        except Exception as e:
            logger.error(f"❌ UI state analysis failed: {e}")
            return None

    def _screenshot_to_base64(self, screenshot: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    def _build_element_finder_prompt(self, instruction: str, context: str = "") -> str:
        """Build the prompt for finding UI elements"""

        context_section = f"\nContext: {context}\n" if context else ""

        return f"""You are helping an AI agent locate UI elements on a screen.

Task: {instruction}
{context_section}
Analyze this screenshot and locate the UI element needed to complete the task.

IMPORTANT:
- Provide pixel coordinates where the center of the element is located
- Coordinates should be actual pixel positions (e.g., x: 1200, y: 650 for 1920x1080 screen)
- Be as precise as possible

Return ONLY valid JSON with this exact structure:
{{
  "found": true/false,
  "element_type": "button/link/input/icon/menu/etc",
  "text": "Text visible on the element",
  "location": "Description of where it is (e.g., 'top-right corner', 'center of screen', 'left sidebar')",
  "coordinates": {{"x": <pixel_x>, "y": <pixel_y>}},
  "confidence": "high/medium/low",
  "description": "Full description of the element and how to recognize it"
}}

If the element cannot be found, return:
{{
  "found": false,
  "reason": "Why the element couldn't be located"
}}

Return ONLY the JSON, no explanations."""


class ActionInstructionParser:
    """
    Parses tutorial instructions to determine what UI action is needed

    Examples:
        "Click the Export button" → action="click", target="Export button"
        "Type 'Hello World' in the text box" → action="type", target="text box", input="Hello World"
        "Select the blue template" → action="select", target="blue template"
        "Drag the video to the timeline" → action="drag", target="video", destination="timeline"
    """

    @staticmethod
    def parse(instruction: str) -> Dict[str, Any]:
        """
        Parse an instruction into actionable components

        Args:
            instruction: Tutorial instruction text

        Returns:
            Dict with:
                - action: str (click, type, select, drag, wait, navigate)
                - target: str (what to interact with)
                - input: Optional[str] (for type actions)
                - destination: Optional[str] (for drag actions)
                - is_actionable: bool
        """
        instruction_lower = instruction.lower().strip()

        # Click actions
        if any(word in instruction_lower for word in ['click', 'press', 'tap', 'hit']):
            target = ActionInstructionParser._extract_target_after_verb(instruction, ['click', 'press', 'tap', 'hit'])
            return {
                'action': 'click',
                'target': target,
                'is_actionable': bool(target)
            }

        # Type/input actions
        if any(word in instruction_lower for word in ['type', 'enter', 'input', 'write']):
            # Extract what to type (usually in quotes or after "type")
            import re
            quote_match = re.search(r'["\']([^"\']+)["\']', instruction)
            if quote_match:
                text_input = quote_match.group(1)
            else:
                # Try to extract after "type"
                text_input = ActionInstructionParser._extract_target_after_verb(instruction, ['type', 'enter', 'input', 'write'])

            target = "input field"  # Generic target for now
            return {
                'action': 'type',
                'target': target,
                'input': text_input,
                'is_actionable': bool(text_input)
            }

        # Select actions
        if any(word in instruction_lower for word in ['select', 'choose', 'pick']):
            target = ActionInstructionParser._extract_target_after_verb(instruction, ['select', 'choose', 'pick'])
            return {
                'action': 'select',
                'target': target,
                'is_actionable': bool(target)
            }

        # Drag actions
        if 'drag' in instruction_lower:
            # Try to find "drag X to Y" pattern
            import re
            drag_match = re.search(r'drag\s+(.+?)\s+to\s+(.+)', instruction_lower)
            if drag_match:
                target = drag_match.group(1).strip()
                destination = drag_match.group(2).strip()
                return {
                    'action': 'drag',
                    'target': target,
                    'destination': destination,
                    'is_actionable': True
                }

        # Wait actions
        if any(word in instruction_lower for word in ['wait', 'pause']):
            return {
                'action': 'wait',
                'target': None,
                'is_actionable': True
            }

        # Navigate/go to actions
        if any(word in instruction_lower for word in ['go to', 'navigate to', 'open', 'visit']):
            target = ActionInstructionParser._extract_target_after_verb(instruction, ['go to', 'navigate to', 'open', 'visit'])
            return {
                'action': 'navigate',
                'target': target,
                'is_actionable': bool(target)
            }

        # Not an actionable instruction
        return {
            'action': None,
            'target': None,
            'is_actionable': False,
            'reason': 'Not recognized as an actionable instruction'
        }

    @staticmethod
    def _extract_target_after_verb(instruction: str, verbs: list) -> str:
        """Extract the target element mentioned after the action verb"""
        instruction_lower = instruction.lower()

        for verb in verbs:
            if verb in instruction_lower:
                # Find position of verb
                pos = instruction_lower.index(verb)
                # Extract everything after verb
                after_verb = instruction[pos + len(verb):].strip()

                # Remove common words like "on the", "the", "a", "an"
                for filler in ['on the ', 'the ', 'a ', 'an ', 'in the ', 'to the ']:
                    if after_verb.lower().startswith(filler):
                        after_verb = after_verb[len(filler):]

                return after_verb.strip()

        return ""
