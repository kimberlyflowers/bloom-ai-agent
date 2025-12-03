"""
UI Element Finder - Sarah's Eyes 👁️
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

import os
import base64
import json
import logging
from typing import Dict, Any, Optional, Tuple, List
from io import BytesIO
from PIL import Image
import anthropic
from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)


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

    def __init__(self, model: Optional[str] = None):
        """
        Initialize UI Element Finder
        
        Args:
            model: Claude model to use (default: claude-3-sonnet-20240229)
        """
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        self.client = AsyncAnthropic(api_key=api_key)
        self.logger = logging.getLogger(__name__)
        
        # Use provided model or default to a standard Claude 3 Sonnet model
        self.model = model or "claude-3-sonnet-20240229"
        
        # Validate model name is reasonable
        if not self.model.startswith("claude"):
            self.logger.warning(f"Model name '{self.model}' may not be