"""
Universal Element Locator - LANGUAGE & LAYOUT AGNOSTIC
Uses LLM vision + semantic understanding to find elements on ANY site
NO site-specific selectors, NO language assumptions, NO layout hardcoding
"""

import asyncio
import json
import logging
import base64
from typing import Dict, Any, Optional, List
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class UniversalElementLocator:
    """
    LLM-powered element finder that works on ANY site, ANY language, ANY layout

    Core Principle: Semantic understanding over CSS selectors
    - "Search for movies" → Finds search box whether it says "Search", "Zoeken", "検索"
    - "Click navigation" → Finds nav whether it's sidebar, topbar, or menu
    - "Find settings" → Understands what settings means on that specific site
    """

    def __init__(self, anthropic_api_key: str):
        self.anthropic = Anthropic(api_key=anthropic_api_key)

    async def locate_element(
        self,
        user_intent: str,
        page_screenshot: str,
        page_url: str = "",
        page_text: str = ""
    ) -> Dict[str, Any]:
        """
        Universal element locator - works on ANY site, ANY language

        Args:
            user_intent: What the user wants to do (e.g., "search for movies", "click home button")
            page_screenshot: Base64 encoded screenshot of current page
            page_url: Current page URL (for context)
            page_text: Extracted text from page (optional, helps with language understanding)

        Returns:
            {
                'success': bool,
                'strategy': str,  # 'coordinates' | 'aria_label' | 'text_content' | 'visual_description'
                'target': dict,   # Depends on strategy
                'reasoning': str, # LLM's explanation
                'confidence': float  # 0.0-1.0
            }
        """
        try:
            logger.info(f"🔍 Universal Element Locator: Finding element for '{user_intent}'")
            logger.info(f"   📍 Page: {page_url}")

            # Call Claude with vision to analyze page and locate element
            response = await asyncio.to_thread(
                self.anthropic.messages.create,
                model="claude-3-5-sonnet-20241022",  # Latest working model with vision
                max_tokens=1000,
                temperature=0,  # Deterministic for element location
                messages=[{
                    'role': 'user',
                    'content': [
                        {
                            'type': 'image',
                            'source': {
                                'type': 'base64',
                                'media_type': 'image/png',
                                'data': page_screenshot
                            }
                        },
                        {
                            'type': 'text',
                            'text': f"""You are a universal element locator for web automation. Analyze this page and locate the element the user wants to interact with.

**USER INTENT:** {user_intent}

**PAGE CONTEXT:**
- URL: {page_url}
- Visible text: {page_text[:500] if page_text else "N/A"}

**YOUR TASK:**
Locate the element the user wants to interact with using semantic understanding, NOT CSS selectors.

**LANGUAGE AGNOSTIC:**
- "search for movies" should find search box whether it says "Search", "Zoeken" (Dutch), "検索" (Japanese), "Buscar" (Spanish)
- Look for visual patterns: magnifying glass icons, text input fields in navigation areas
- Understand intent, not literal text matching

**LAYOUT AGNOSTIC:**
- "navigation" could be sidebar, topbar, menu button, tabs
- "search" could be top-right, center, overlay, hidden in menu
- Analyze visual structure and spatial relationships

**INTERACTION STRATEGIES (Choose the best one):**

1. **COORDINATES** (Most reliable for visual elements)
   - Use when element is clearly visible
   - Return approximate coordinates (percentage of screen)
   - Example: {{"x_percent": 85, "y_percent": 10}} for top-right element

2. **ARIA_LABEL** (Best for accessibility-labeled elements)
   - Use when element has clear aria-label or aria-labelledby
   - Example: {{"aria_label": "Search"}}

3. **TEXT_CONTENT** (Good for buttons/links with text)
   - Use when element has visible text
   - Return EXACT text you see (any language)
   - Example: {{"text": "Zoeken", "partial": false}}

4. **VISUAL_DESCRIPTION** (Fallback for complex cases)
   - Use when above strategies won't work
   - Describe position and appearance
   - Example: {{"description": "Second blue button in top navigation bar, right side"}}

**RETURN FORMAT (JSON only):**
{{
    "success": true/false,
    "strategy": "coordinates" | "aria_label" | "text_content" | "visual_description",
    "target": {{"x_percent": 50, "y_percent": 20}} OR {{"aria_label": "..."}} OR {{"text": "..."}} OR {{"description": "..."}},
    "reasoning": "I found the search box in the top-right corner. It has a magnifying glass icon and placeholder text 'Zoeken' (Dutch for Search)",
    "confidence": 0.95,
    "element_type": "button" | "input" | "link" | "icon" | "text",
    "language_detected": "en" | "nl" | "ja" | etc
}}

If element cannot be found:
{{
    "success": false,
    "reasoning": "No search box visible on current page",
    "confidence": 0.0
}}

**ANALYZE THE SCREENSHOT AND RESPOND:**"""
                        }
                    ]
                }]
            )

            # Parse LLM response
            response_text = response.content[0].text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
            response_text = response_text.strip()

            result = json.loads(response_text)

            # Log result
            if result.get('success'):
                logger.info(f"✅ Element located: {result.get('strategy')} - {result.get('reasoning')[:100]}")
                logger.info(f"   🎯 Confidence: {result.get('confidence', 0.0):.2f}")
                logger.info(f"   🌍 Language: {result.get('language_detected', 'unknown')}")
            else:
                logger.warning(f"❌ Element not found: {result.get('reasoning')}")

            return result

        except Exception as e:
            logger.error(f"❌ Universal Element Locator error: {e}")
            return {
                'success': False,
                'reasoning': f"Locator error: {str(e)}",
                'confidence': 0.0
            }

    async def locate_multiple_elements(
        self,
        user_intent: str,
        page_screenshot: str,
        page_url: str = "",
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Locate multiple matching elements (e.g., "find all videos", "find all links")

        Returns list of located elements, sorted by relevance
        """
        try:
            logger.info(f"🔍 Universal Element Locator: Finding multiple elements for '{user_intent}'")

            response = await asyncio.to_thread(
                self.anthropic.messages.create,
                model="claude-3-5-sonnet-20241022",  # Latest working model with vision
                max_tokens=1500,
                temperature=0,
                messages=[{
                    'role': 'user',
                    'content': [
                        {
                            'type': 'image',
                            'source': {
                                'type': 'base64',
                                'media_type': 'image/png',
                                'data': page_screenshot
                            }
                        },
                        {
                            'type': 'text',
                            'text': f"""Locate ALL elements matching the user's intent. Return up to {count} most relevant matches.

**USER INTENT:** {user_intent}
**PAGE:** {page_url}

Return JSON array:
[
    {{
        "strategy": "coordinates",
        "target": {{"x_percent": 25, "y_percent": 40}},
        "description": "First video thumbnail in grid",
        "confidence": 0.9
    }},
    ...
]"""
                        }
                    ]
                }]
            )

            response_text = response.content[0].text.strip()
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
            response_text = response_text.strip()

            results = json.loads(response_text)

            logger.info(f"✅ Found {len(results)} matching elements")
            return results

        except Exception as e:
            logger.error(f"❌ Multiple element locator error: {e}")
            return []

    async def verify_element_interaction(
        self,
        user_intent: str,
        before_screenshot: str,
        after_screenshot: str
    ) -> Dict[str, Any]:
        """
        Verify that interaction succeeded by comparing before/after screenshots

        Returns:
            {
                'success': bool,
                'changes_detected': List[str],
                'reasoning': str
            }
        """
        try:
            logger.info(f"🔍 Verifying interaction result for: {user_intent}")

            response = await asyncio.to_thread(
                self.anthropic.messages.create,
                model="claude-3-5-sonnet-20241022",  # Latest working model with vision
                max_tokens=500,
                temperature=0,
                messages=[{
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': f"**USER INTENT:** {user_intent}\n\n**BEFORE (screenshot 1):**"
                        },
                        {
                            'type': 'image',
                            'source': {
                                'type': 'base64',
                                'media_type': 'image/png',
                                'data': before_screenshot
                            }
                        },
                        {
                            'type': 'text',
                            'text': "**AFTER (screenshot 2):**"
                        },
                        {
                            'type': 'image',
                            'source': {
                                'type': 'base64',
                                'media_type': 'image/png',
                                'data': after_screenshot
                            }
                        },
                        {
                            'type': 'text',
                            'text': """Compare the screenshots. Did the interaction succeed?

Return JSON:
{
    "success": true/false,
    "changes_detected": ["Search box opened", "Results appeared"],
    "reasoning": "The search overlay appeared with focus on input field"
}"""
                        }
                    ]
                }]
            )

            response_text = response.content[0].text.strip()
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
            response_text = response_text.strip()

            result = json.loads(response_text)

            if result.get('success'):
                logger.info(f"✅ Interaction verified: {result.get('reasoning')}")
            else:
                logger.warning(f"❌ Interaction may have failed: {result.get('reasoning')}")

            return result

        except Exception as e:
            logger.error(f"❌ Verification error: {e}")
            return {
                'success': False,
                'changes_detected': [],
                'reasoning': f"Verification error: {str(e)}"
            }
