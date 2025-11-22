"""
Vision-Guided Action Reasoning System

Instead of hardcoded pattern matching, Sarah uses vision + reasoning to:
1. Analyze what's on screen (vision analysis)
2. Understand user intent (intent parsing)
3. Reason about appropriate actions (action planning)
4. Execute with validation (feedback loop)

This eliminates bug-by-bug fixes by giving Sarah a systematic framework
for understanding and interacting with ANY web interface.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class UIElement:
    """Represents a UI element Sarah can interact with"""
    type: str  # button, link, input, video, image, form, etc.
    description: str  # visual description
    action: str  # click, type, scroll_to, etc.
    confidence: float  # 0-1


@dataclass
class PageAnalysis:
    """Results of vision analysis"""
    page_type: str  # search_engine, video_site, article, form, social_media, etc.
    elements: List[UIElement]
    state: str  # loading, ready, popup_visible, form_incomplete, etc.
    observations: List[str]  # what Sarah notices


@dataclass
class ActionPlan:
    """Planned actions to achieve user's goal"""
    goal: str  # what user wants to accomplish
    steps: List[Dict[str, Any]]  # sequence of actions
    reasoning: str  # why this plan


class VisionActionReasoner:
    """
    Systematic reasoning framework for browser interactions

    Process:
    1. Vision Analysis: What's on screen?
    2. Intent Understanding: What does user want?
    3. Action Planning: What should I do?
    4. Execution: Do it with validation
    """

    def __init__(self):
        self.last_analysis: Optional[PageAnalysis] = None
        self.last_plan: Optional[ActionPlan] = None

    def analyze_vision_context(self, screenshot_description: str, url: str) -> PageAnalysis:
        """
        Analyze what's visible on screen to understand UI elements and page state

        This replaces hardcoded keyword matching with actual visual understanding
        """
        observations = []
        elements = []

        # Determine page type from URL and context
        page_type = self._infer_page_type(url, screenshot_description)
        observations.append(f"Page type: {page_type}")

        # Identify interactive elements
        elements = self._identify_ui_elements(screenshot_description)
        observations.append(f"Found {len(elements)} interactive elements")

        # Determine page state
        state = self._determine_page_state(screenshot_description)
        observations.append(f"Page state: {state}")

        analysis = PageAnalysis(
            page_type=page_type,
            elements=elements,
            state=state,
            observations=observations
        )

        self.last_analysis = analysis
        return analysis

    def parse_user_intent(self, user_message: str) -> Dict[str, Any]:
        """
        Understand what the user wants to accomplish

        Instead of keyword matching, extract actual intent:
        - Navigation: "go to X", "open Y"
        - Search: "search for X", "find Y"
        - Interaction: "click X", "watch Y", "read Z"
        - Input: "type X", "fill out Y"
        - Observation: "what do you see?", "describe X"
        """
        text_lower = user_message.lower()

        # Navigation intent
        if any(word in text_lower for word in ['go to', 'open', 'navigate to', 'visit']):
            # Extract URL or destination
            url_match = re.search(r'https?://[^\s]+', user_message)
            if url_match:
                return {
                    'type': 'navigate',
                    'target': url_match.group(0),
                    'confidence': 0.95
                }
            # Look for quoted destinations
            quote_match = re.search(r'["\']([^"\']+)["\']', user_message)
            if quote_match:
                return {
                    'type': 'navigate',
                    'target': quote_match.group(1),
                    'confidence': 0.85
                }
            # Fallback: Extract word after "go to", "open", etc.
            for keyword in ['go to', 'open', 'navigate to', 'visit']:
                if keyword in text_lower:
                    # Extract everything after the keyword
                    parts = user_message.lower().split(keyword, 1)
                    if len(parts) > 1:
                        target = parts[1].strip().split()[0]  # First word after keyword
                        # Clean up common punctuation
                        target = target.rstrip('.,!?')
                        if target:
                            return {
                                'type': 'navigate',
                                'target': target,
                                'confidence': 0.80
                            }
                    break

        # Search intent
        if any(word in text_lower for word in ['search for', 'find', 'look up', 'look for']):
            # Extract search query
            for pattern in [
                r'search for ["\']?([^"\']+)["\']?',
                r'find ["\']?([^"\']+)["\']?',
                r'look up ["\']?([^"\']+)["\']?'
            ]:
                match = re.search(pattern, text_lower)
                if match:
                    return {
                        'type': 'search',
                        'query': match.group(1).strip(),
                        'confidence': 0.9
                    }

        # Click/interaction intent
        if any(word in text_lower for word in ['click', 'select', 'choose', 'press', 'tap']):
            # Check if user is asking Sarah to choose (not commanding specific click)
            if any(phrase in text_lower for phrase in ['whatever you', 'anything', 'something', 'you choose', 'you decide', 'you pick', 'your choice']):
                # User wants Sarah to decide what to click - not a specific click command
                return {
                    'type': 'observe',
                    'confidence': 0.90
                }

            # Extract what to click
            target = self._extract_click_target(user_message)
            return {
                'type': 'click',
                'target': target,
                'confidence': 0.85
            }

        # Watch/view video intent
        if any(word in text_lower for word in ['watch', 'play', 'view video', 'see video']):
            return {
                'type': 'interact_video',
                'action': 'play',
                'confidence': 0.9
            }

        # Input/typing intent
        if any(word in text_lower for word in ['type', 'enter', 'fill in', 'write']):
            # Extract what to type
            quote_match = re.search(r'["\']([^"\']+)["\']', user_message)
            if quote_match:
                return {
                    'type': 'input',
                    'text': quote_match.group(1),
                    'confidence': 0.9
                }

        # Observation/question intent
        if any(word in text_lower for word in ['what do you see', 'describe', 'what is', 'where are']):
            return {
                'type': 'observe',
                'confidence': 0.95
            }

        # Acknowledge/confirmation (not an action)
        if user_message.lower() in ['ok', 'ok cool', 'nice', 'great', 'thanks', 'good']:
            return {
                'type': 'acknowledgment',
                'confidence': 0.95
            }

        # Unknown intent - need clarification
        return {
            'type': 'unknown',
            'confidence': 0.3
        }

    def plan_actions(
        self,
        user_intent: Dict[str, Any],
        page_analysis: PageAnalysis
    ) -> ActionPlan:
        """
        Create action plan based on user intent and what's visible

        This is where reasoning happens:
        - If user wants to watch video + page shows search results → click video first
        - If user wants to search + popup is visible → dismiss popup first
        - If user wants to click + multiple matches → choose most relevant
        """
        intent_type = user_intent.get('type')
        steps = []
        reasoning = ""

        # Handle different intent types
        if intent_type == 'navigate':
            # Simple navigation
            steps.append({
                'action': 'navigate',
                'target': user_intent['target']
            })
            reasoning = f"Navigate to {user_intent['target']}"

        elif intent_type == 'search':
            # Check if popup is blocking
            if page_analysis.state == 'popup_visible':
                steps.append({
                    'action': 'dismiss_popup',
                    'method': 'accessibility_first'
                })
                reasoning = "Dismiss popup before searching. "

            # Perform search
            steps.append({
                'action': 'search',
                'query': user_intent['query']
            })
            reasoning += f"Search for: {user_intent['query']}"

        elif intent_type == 'click':
            # Check if popup is blocking
            if page_analysis.state == 'popup_visible':
                steps.append({
                    'action': 'dismiss_popup',
                    'method': 'accessibility_first'
                })
                reasoning = "Dismiss popup before clicking. "

            # Find matching element
            target = user_intent.get('target', '')
            matching_elements = self._find_matching_elements(target, page_analysis.elements)

            if matching_elements:
                best_match = matching_elements[0]  # highest confidence
                steps.append({
                    'action': 'click_element',
                    'description': target,
                    'element_type': best_match.type
                })
                reasoning += f"Click {best_match.type}: {target}"
            else:
                # No clear match - use vision-guided click
                steps.append({
                    'action': 'click_by_description',
                    'description': target
                })
                reasoning += f"Vision-guided click: {target}"

        elif intent_type == 'interact_video':
            # Check if we're on video page or search results
            if page_analysis.page_type == 'search_engine':
                # Need to click video first
                steps.append({
                    'action': 'click_element',
                    'description': 'video thumbnail',
                    'element_type': 'video'
                })
                steps.append({
                    'action': 'wait',
                    'duration': 2
                })
                steps.append({
                    'action': 'click_element',
                    'description': 'play button',
                    'element_type': 'button'
                })
                reasoning = "Click video thumbnail, then play"
            else:
                # Already on video page
                steps.append({
                    'action': 'click_element',
                    'description': 'play button',
                    'element_type': 'button'
                })
                reasoning = "Click play button on video"

        elif intent_type == 'observe':
            # Just describe what's visible
            steps.append({
                'action': 'observe',
                'return': 'description'
            })
            reasoning = "Describe current page state"

        elif intent_type == 'acknowledgment':
            # No action needed
            steps = []
            reasoning = "User acknowledgment - no action required"

        else:
            # Unknown intent - ask for clarification
            steps.append({
                'action': 'clarify',
                'message': "I'm not sure what you want me to do. Can you be more specific?"
            })
            reasoning = "Intent unclear - requesting clarification"

        plan = ActionPlan(
            goal=user_intent.get('type', 'unknown'),
            steps=steps,
            reasoning=reasoning
        )

        self.last_plan = plan
        return plan

    def should_take_action(self, user_intent: Dict[str, Any]) -> bool:
        """
        Determine if this message requires an action or just a response

        Acknowledgments like "ok cool" should NOT trigger actions
        """
        intent_type = user_intent.get('type')

        # These require actions
        action_types = ['navigate', 'search', 'click', 'interact_video', 'input']

        # These do NOT require actions
        non_action_types = ['acknowledgment', 'observe']

        if intent_type in action_types:
            return True
        elif intent_type in non_action_types:
            return False
        else:
            # Unknown - be conservative, don't act
            return False

    # Helper methods

    def _infer_page_type(self, url: str, context: str) -> str:
        """Infer page type from URL and visual context"""
        url_lower = url.lower()
        context_lower = context.lower()

        if 'google.com' in url_lower or 'search' in url_lower:
            return 'search_engine'
        elif 'youtube.com' in url_lower or 'video' in context_lower:
            return 'video_site'
        elif 'tiktok.com' in url_lower:
            return 'social_media'
        elif 'form' in context_lower or 'input' in context_lower:
            return 'form'
        elif 'article' in context_lower or 'blog' in context_lower:
            return 'article'
        else:
            return 'general'

    def _identify_ui_elements(self, context: str) -> List[UIElement]:
        """Identify interactive elements from visual context"""
        elements = []
        context_lower = context.lower()

        # Look for common UI elements
        if 'button' in context_lower:
            elements.append(UIElement('button', 'button', 'click', 0.8))
        if 'link' in context_lower:
            elements.append(UIElement('link', 'link', 'click', 0.8))
        if 'video' in context_lower or 'thumbnail' in context_lower:
            elements.append(UIElement('video', 'video thumbnail', 'click', 0.85))
        if 'input' in context_lower or 'search box' in context_lower:
            elements.append(UIElement('input', 'input field', 'type', 0.85))
        if 'popup' in context_lower or 'dialog' in context_lower or 'modal' in context_lower:
            elements.append(UIElement('popup', 'popup dialog', 'dismiss', 0.9))

        return elements

    def _determine_page_state(self, context: str) -> str:
        """Determine current page state"""
        context_lower = context.lower()

        if any(word in context_lower for word in ['popup', 'dialog', 'modal', 'cookie', 'consent']):
            return 'popup_visible'
        elif 'loading' in context_lower:
            return 'loading'
        elif 'error' in context_lower:
            return 'error'
        else:
            return 'ready'

    def _extract_click_target(self, user_message: str) -> str:
        """Extract what user wants to click"""
        text_lower = user_message.lower()

        # Try to extract quoted text
        quote_match = re.search(r'["\']([^"\']+)["\']', user_message)
        if quote_match:
            return quote_match.group(1)

        # Look for common patterns
        patterns = [
            r'click (?:the )?(.+?)(?:\.|$)',
            r'select (?:the )?(.+?)(?:\.|$)',
            r'press (?:the )?(.+?)(?:\.|$)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                target = match.group(1).strip()
                # Filter out common words
                if target not in ['it', 'that', 'this', 'one']:
                    return target

        # Default
        return 'element'

    def _find_matching_elements(
        self,
        target: str,
        elements: List[UIElement]
    ) -> List[UIElement]:
        """Find UI elements matching the target description"""
        target_lower = target.lower()
        matches = []

        for element in elements:
            if target_lower in element.description.lower():
                matches.append(element)

        # Sort by confidence
        matches.sort(key=lambda e: e.confidence, reverse=True)
        return matches
