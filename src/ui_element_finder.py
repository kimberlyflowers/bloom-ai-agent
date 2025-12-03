"""
UI Element Finder - Uses Claude Vision to locate elements in screenshots

This enables Sarah to find UI elements by description rather than CSS selectors,
making tutorial learning work across different interfaces.
"""

import os
import base64
import json
import logging
from typing import Dict, Any, Optional, Tuple
from io import BytesIO
from PIL import Image
from anthropic import AsyncAnthropic


class UIElementFinder:
    """
    Finds UI elements in screenshots using Claude Vision API

    Usage:
        finder = UIElementFinder()
        screenshot = browser.take_screenshot()  # PIL Image
        result = await finder.find_element(screenshot, "the blue Login button")
        if result["found"]:
            x, y = result["coordinates"]["x"], result["coordinates"]["y"]
            await browser.page.mouse.click(x, y)
    """

    def __init__(self):
        self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.logger = logging.getLogger(__name__)
        self.model = "claude-sonnet-4-20250514"

    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    async def find_element(
        self,
        screenshot: Image.Image,
        instruction: str
    ) -> Dict[str, Any]:
        """
        Find a UI element in a screenshot using Claude Vision

        Args:
            screenshot: PIL Image of the screen
            instruction: Natural language description of element to find
                       e.g., "the blue Login button in top right"

        Returns:
            Dict with:
                - found: bool (whether element was found)
                - coordinates: {"x": int, "y": int} (pixel coordinates)
                - confidence: str (high/medium/low)
                - description: str (what was found)
        """
        try:
            # Convert screenshot to base64
            image_base64 = self._image_to_base64(screenshot)

            # Create Vision prompt
            prompt = f"""You are analyzing a screenshot to locate a specific UI element.

TASK: Find "{instruction}"

Please analyze the screenshot and identify the element's location.

Respond with ONLY a JSON object (no other text):

{{
  "found": true/false,
  "coordinates": {{"x": 0, "y": 0}},
  "confidence": "high/medium/low",
  "description": "what you see at that location"
}}

IMPORTANT:
- Coordinates should be center of the element
- If element not found, set found=false and explain in description
- Be precise with coordinates
- x and y are pixel positions from top-left (0,0)
"""

            # Call Claude Vision API
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            )

            # Parse response
            response_text = response.content[0].text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            # Parse JSON
            result = json.loads(response_text)

            self.logger.info(f"Vision result: {result}")
            return result

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse Vision response: {e}")
            self.logger.error(f"Response was: {response_text[:200]}")
            return {
                "found": False,
                "coordinates": {"x": 0, "y": 0},
                "confidence": "none",
                "description": f"Failed to parse response: {e}"
            }
        except Exception as e:
            self.logger.error(f"Vision API error: {e}")
            return {
                "found": False,
                "coordinates": {"x": 0, "y": 0},
                "confidence": "none",
                "description": f"Error: {str(e)}"
            }

    async def find_clickable_area(
        self,
        screenshot: Image.Image,
        element_description: str
    ) -> Optional[Tuple[int, int]]:
        """
        Convenience method that returns just (x, y) coordinates or None

        Args:
            screenshot: PIL Image of screen
            element_description: What to find

        Returns:
            (x, y) tuple if found, None otherwise
        """
        result = await self.find_element(screenshot, element_description)

        if result.get("found"):
            coords = result.get("coordinates", {})
            return (coords.get("x"), coords.get("y"))

        return None

    async def verify_element_exists(
        self,
        screenshot: Image.Image,
        element_description: str
    ) -> bool:
        """
        Check if an element exists without getting coordinates

        Args:
            screenshot: PIL Image
            element_description: What to look for

        Returns:
            True if element is visible, False otherwise
        """
        result = await self.find_element(screenshot, element_description)
        return result.get("found", False)

    async def analyze_ui_state(
        self,
        screenshot: Image.Image,
        question: str
    ) -> str:
        """
        Ask a question about the UI state using Vision

        Args:
            screenshot: PIL Image of screen
            question: Question about the UI (e.g., "What page am I on?")

        Returns:
            Claude's answer as a string
        """
        try:
            image_base64 = self._image_to_base64(screenshot)

            prompt = f"""You are analyzing a screenshot of a user interface.

QUESTION: {question}

Please answer the question based on what you see in the screenshot.
Be concise and specific."""

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=512,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            )

            answer = response.content[0].text.strip()
            self.logger.info(f"UI analysis: {answer}")
            return answer

        except Exception as e:
            self.logger.error(f"UI analysis error: {e}")
            return f"Error analyzing UI: {str(e)}"


# Example usage
if __name__ == "__main__":
    import asyncio
    from PIL import Image

    async def test():
        # Create finder
        finder = UIElementFinder()

        # Load a test screenshot
        # screenshot = Image.open("test_screenshot.png")

        # Find an element
        # result = await finder.find_element(screenshot, "the blue Login button")
        # print(result)

        print("UIElementFinder created successfully!")

    asyncio.run(test())
