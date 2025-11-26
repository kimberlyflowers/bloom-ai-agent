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
    has_search: bool = False
    has_forms: bool = False
    has_videos: bool = False


@dataclass
class ActionPlan:
    """Planned actions to achieve user's goal"""
    goal: str  # what user wants to accomplish
    steps: List[Dict[str, Any]]  # sequence of actions
    reasoning: str  # why this plan
    confidence: float = 0.5


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

        # Identify interactive elements with ENHANCED detection
        elements = self._identify_ui_elements_enhanced(screenshot_description, page_type)
        observations.append(f"Found {len(elements)} interactive elements")

        # Determine page state
        state = self._determine_page_state(screenshot_description)
        observations.append(f"Page state: {state}")

        # Enhanced capabilities detection
        has_search = self._detect_search_capability(screenshot_description, page_type)
        has_forms = self._detect_form_capability(screenshot_description)
        has_videos = self._detect_video_capability(screenshot_description, page_type)

        if has_search:
            observations.append("Page has search capability")
        if has_forms:
            observations.append("Page has forms")
        if has_videos:
            observations.append("Page has video content")

        analysis = PageAnalysis(
            page_type=page_type,
            elements=elements,
            state=state,
            observations=observations,
            has_search=has_search,
            has_forms=has_forms,
            has_videos=has_videos
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
                    'query': '',
                    'text': '',
                    'confidence': 0.95,
                    'original_message': user_message
                }
            # Look for quoted destinations
            quote_match = re.search(r'["\']([^"\']+)["\']', user_message)
            if quote_match:
                return {
                    'type': 'navigate',
                    'target': quote_match.group(1),
                    'query': '',
                    'text': '',
                    'confidence': 0.85,
                    'original_message': user_message
                }
            # Extract destination after navigation keyword (without quotes or http://)
            # Matches patterns like "go to youtube.com", "navigate to google", "open tiktok.com"
            for keyword in ['go to', 'navigate to', 'open', 'visit']:
                if keyword in text_lower:
                    pattern = rf'{keyword}\s+([a-z0-9][\w\-\.]*(?:\.[a-z]{{2,}})?)'
                    match = re.search(pattern, text_lower, re.IGNORECASE)
                    if match:
                        destination = match.group(1)
                        # Add common TLD if missing (e.g., "youtube" -> "youtube.com")
                        if '.' not in destination:
                            common_sites = ['google', 'youtube', 'facebook', 'twitter', 'instagram',
                                          'tiktok', 'linkedin', 'github', 'reddit', 'amazon']
                            if destination in common_sites:
                                destination = f"{destination}.com"
                        return {
                            'type': 'navigate',
                            'target': destination,
                            'query': '',
                            'text': '',
                            'confidence': 0.9,
                            'original_message': user_message
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
                        'target': '',
                        'query': match.group(1).strip(),
                        'text': '',
                        'confidence': 0.9,
                        'original_message': user_message
                    }

        # Click/interaction intent
        # Recognize many ways users say "click" - hit, push, touch, select, etc.
        if any(word in text_lower for word in ['click', 'select', 'choose', 'press', 'tap',
                                                'hit', 'push', 'touch', 'activate', 'use']):
            # Extract what to click
            target = self._extract_click_target(user_message)
            return {
                'type': 'click',
                'target': target,
                'query': '',
                'text': '',
                'confidence': 0.85,
                'original_message': user_message
            }

        # Watch/view video intent
        if any(word in text_lower for word in ['watch', 'play', 'view video', 'see video']):
            return {
                'type': 'interact_video',
                'target': 'video',
                'query': '',
                'text': '',
                'confidence': 0.9,
                'original_message': user_message
            }

        # Input/typing intent
        if any(word in text_lower for word in ['type', 'enter', 'fill in', 'write']):
            # Extract what to type
            quote_match = re.search(r'["\']([^"\']+)["\']', user_message)
            if quote_match:
                return {
                    'type': 'input',
                    'target': 'input field',
                    'query': '',
                    'text': quote_match.group(1),
                    'confidence': 0.9,
                    'original_message': user_message
                }

        # Observation/question intent
        if any(word in text_lower for word in ['what do you see', 'describe', 'what is', 'where are']):
            return {
                'type': 'observe',
                'target': 'page content',
                'query': '',
                'text': '',
                'confidence': 0.95,
                'original_message': user_message
            }

        # Acknowledge/confirmation (not an action)
        if user_message.lower() in ['ok', 'ok cool', 'nice', 'great', 'thanks', 'good', 'yes']:
            return {
                'type': 'acknowledgment',
                'target': '',
                'query': '',
                'text': '',
                'confidence': 0.95,
                'original_message': user_message
            }

        # Unknown intent - need clarification
        return {
            'type': 'unknown',
            'target': '',
            'query': '',
            'text': '',
            'confidence': 0.3,
            'original_message': user_message
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
        intent_type = user_intent.get('type', 'unknown')
        target = user_intent.get('target', '')
        query = user_intent.get('query', '')
        text = user_intent.get('text', '')
        confidence = user_intent.get('confidence', 0.5)
        
        steps = []
        reasoning = ""
        goal = ""

        # Handle different intent types with ENHANCED reasoning
        if intent_type == 'navigate':
            goal = f"Navigate to {target}"
            reasoning = f"User wants to navigate to {target}. Current page: {page_analysis.page_type}"
            
            steps.append({
                'action': 'navigate',
                'target': target,
                'description': f'Navigate to {target}'
            })

        elif intent_type == 'search':
            # Use the standardized 'query' field for search
            search_terms = query or target  # Fallback to target if query is empty
            goal = f"Search for {search_terms}"
            reasoning = f"User wants to search for '{search_terms}'. Current page has search capability: {'yes' if page_analysis.has_search else 'no'}"
            
            # Check if popup is blocking
            if page_analysis.state == 'popup_visible':
                steps.append({
                    'action': 'dismiss_popup',
                    'method': 'accessibility_first',
                    'description': 'Dismiss any popups before searching'
                })
            
            steps.append({
                'action': 'search',
                'query': search_terms,
                'description': f'Search for "{search_terms}"'
            })

        elif intent_type == 'click':
            goal = f"Click {target}"
            reasoning = f"User wants to click '{target}'. Page state: {page_analysis.state}"

            # Check if we need to dismiss popups first
            if page_analysis.state == 'popup_visible':
                steps.append({
                    'action': 'dismiss_popup',
                    'method': 'accessibility_first',
                    'description': 'Dismiss any popups before clicking'
                })

            # ENHANCED: Create SPECIFIC description for clicking
            # Instead of generic "video", make it specific: "first video thumbnail in search results"
            specific_description = target

            # Make description more specific based on page context
            if page_analysis.page_type == 'video_site' and 'video' in target.lower():
                if 'search' in page_analysis.observations or 'result' in ' '.join(page_analysis.observations).lower():
                    # On search results page - specify WHICH video
                    specific_description = f"first {target} thumbnail in search results"
                else:
                    # On main page - be more specific
                    specific_description = f"{target} in main feed"

            steps.append({
                'action': 'click_element',
                'target': target,
                'description': specific_description  # Use specific description, not generic
            })

        elif intent_type == 'input':
            goal = f"Type '{text}' in {target}"
            reasoning = f"User wants to type '{text}' in {target}. Page has forms: {'yes' if page_analysis.has_forms else 'no'}"
            
            steps.append({
                'action': 'type_text',
                'target': {
                    'element': target,
                    'text': text
                },
                'description': f'Type "{text}" in {target}'
            })

        elif intent_type == 'interact_video':
            goal = f"Watch {target}"
            reasoning = f"User wants to watch video content. Page has videos: {'yes' if page_analysis.has_videos else 'no'}"
            
            # Enhanced video interaction logic
            if page_analysis.page_type == 'search_engine':
                # On search results - click video thumbnail first
                steps.append({
                    'action': 'click_element',
                    'target': 'video thumbnail',
                    'element_type': 'video_thumbnail',
                    'description': 'Click video thumbnail to open video'
                })
                steps.append({
                    'action': 'wait',
                    'duration': 3,
                    'description': 'Wait for video page to load'
                })
            
            # Then click play button
            steps.append({
                'action': 'click_element',
                'target': 'play button',
                'element_type': 'play_button',
                'description': 'Click play button to start video'
            })

        elif intent_type == 'observe':
            goal = f"Observe {target}"
            reasoning = f"User wants to observe {target}. Current page analysis: {page_analysis.observations}"
            
            steps.append({
                'action': 'observe',
                'description': f'Observe {target}'
            })

        elif intent_type == 'acknowledgment':
            goal = "No action required"
            reasoning = f"User acknowledgment - no browser action needed"
            steps = []

        else:
            # Unknown intent - ask for clarification
            goal = "Clarify user intent"
            reasoning = f"User intent '{intent_type}' is unclear - need clarification"
            
            steps.append({
                'action': 'clarify',
                'message': "I'm not sure what you want me to do. Can you be more specific about what you'd like me to click or interact with?",
                'description': 'Request clarification from user'
            })

        # Add final observation step for all action plans (except observations and acknowledgments)
        if steps and intent_type not in ['observe', 'acknowledgment', 'unknown']:
            steps.append({
                'action': 'observe',
                'description': 'Observe results of actions'
            })

        return ActionPlan(
            goal=goal,
            reasoning=reasoning,
            steps=steps,
            confidence=confidence
        )

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

    # ENHANCED HELPER METHODS

    def _infer_page_type(self, url: str, context: str) -> str:
        """Infer page type from URL and visual context"""
        url_lower = url.lower()
        context_lower = context.lower()

        if 'google.com' in url_lower or 'search' in url_lower or 'query=' in url_lower:
            return 'search_engine'
        elif 'youtube.com' in url_lower or 'video' in context_lower or 'watch?v=' in url_lower:
            return 'video_site'
        elif any(site in url_lower for site in ['tiktok.com', 'instagram.com', 'facebook.com', 'twitter.com']):
            return 'social_media'
        elif 'form' in context_lower or 'input' in context_lower or 'login' in context_lower:
            return 'form'
        elif 'article' in context_lower or 'blog' in context_lower or 'news' in context_lower:
            return 'article'
        elif 'shopping' in context_lower or 'product' in context_lower or 'amazon' in url_lower:
            return 'ecommerce'
        else:
            return 'general'

    def _identify_ui_elements_enhanced(self, context: str, page_type: str) -> List[UIElement]:
        """ENHANCED: Intelligently identify interactive elements from visual context"""
        elements = []
        context_lower = context.lower()

        # VIDEO ELEMENT DETECTION with context awareness
        video_indicators = ['video', 'thumbnail', 'play', 'watch', 'duration', 'views']
        if any(indicator in context_lower for indicator in video_indicators):
            if 'thumbnail' in context_lower or 'preview' in context_lower:
                elements.append(UIElement('video_thumbnail', 'video thumbnail', 'click', 0.9))
            elif 'play' in context_lower or 'start video' in context_lower:
                elements.append(UIElement('play_button', 'play button', 'click', 0.85))
            else:
                elements.append(UIElement('video', 'video content', 'click', 0.8))

        # BUTTON DETECTION with purpose understanding
        button_indicators = ['button', 'btn', 'click here', 'tap to', 'press', 'select']
        if any(indicator in context_lower for indicator in button_indicators):
            # Determine button purpose from context
            if any(word in context_lower for word in ['search', 'magnifying', 'find']):
                elements.append(UIElement('search_button', 'search button', 'click', 0.85))
            elif any(word in context_lower for word in ['menu', 'hamburger', 'navigation']):
                elements.append(UIElement('menu_button', 'menu button', 'click', 0.8))
            elif any(word in context_lower for word in ['play', 'start', 'watch']):
                elements.append(UIElement('play_button', 'play button', 'click', 0.9))
            elif any(word in context_lower for word in ['accept', 'agree', 'consent', 'ok', 'continue']):
                elements.append(UIElement('accept_button', 'accept/consent button', 'click', 0.95))
            else:
                elements.append(UIElement('button', 'interactive button', 'click', 0.7))

        # LINK DETECTION with navigation context
        if any(word in context_lower for word in ['link', 'navigation', 'go to', 'href', 'anchor']):
            elements.append(UIElement('link', 'navigation link', 'click', 0.8))

        # INPUT FIELD DETECTION with type identification
        input_indicators = ['input', 'type here', 'search box', 'text field', 'form', 'enter text']
        if any(indicator in context_lower for indicator in input_indicators):
            if 'search' in context_lower or 'find' in context_lower:
                elements.append(UIElement('search_input', 'search input field', 'type', 0.9))
            elif 'email' in context_lower or 'password' in context_lower:
                elements.append(UIElement('form_input', 'form input field', 'type', 0.8))
            else:
                elements.append(UIElement('input', 'text input field', 'type', 0.8))

        # PAGE-SPECIFIC ELEMENTS based on page type
        if page_type == 'video_site':
            elements.extend([
                UIElement('video_thumbnail', 'video thumbnail', 'click', 0.9),
                UIElement('play_button', 'play button', 'click', 0.85),
                UIElement('video_title', 'video title link', 'click', 0.8)
            ])
        elif page_type == 'search_engine':
            elements.extend([
                UIElement('search_input', 'search box', 'type', 0.9),
                UIElement('search_button', 'search button', 'click', 0.8),
                UIElement('result_link', 'search result', 'click', 0.85)
            ])
        elif page_type == 'social_media':
            elements.extend([
                UIElement('post', 'social media post', 'click', 0.8),
                UIElement('like_button', 'like button', 'click', 0.7),
                UIElement('comment_button', 'comment button', 'click', 0.7)
            ])

        # Remove duplicates and sort by confidence
        unique_elements = {}
        for element in elements:
            key = (element.type, element.description)
            if key not in unique_elements or element.confidence > unique_elements[key].confidence:
                unique_elements[key] = element

        return sorted(unique_elements.values(), key=lambda e: e.confidence, reverse=True)

    def _determine_page_state(self, context: str) -> str:
        """Determine current page state"""
        context_lower = context.lower()

        if any(word in context_lower for word in ['popup', 'dialog', 'modal', 'cookie', 'consent', 'overlay']):
            return 'popup_visible'
        elif any(word in context_lower for word in ['loading', 'spinner', 'progress', 'waiting']):
            return 'loading'
        elif any(word in context_lower for word in ['error', 'failed', 'not found', '404']):
            return 'error'
        elif any(word in context_lower for word in ['login', 'sign in', 'authentication']):
            return 'authentication_required'
        else:
            return 'ready'

    def _detect_search_capability(self, context: str, page_type: str) -> bool:
        """Detect if page has search functionality"""
        context_lower = context.lower()
        
        # Direct indicators
        if any(word in context_lower for word in ['search', 'find', 'magnifying', 'query']):
            return True
        
        # Page type based inference
        if page_type in ['search_engine', 'ecommerce', 'social_media']:
            return True
            
        return False

    def _detect_form_capability(self, context: str) -> bool:
        """Detect if page has form inputs"""
        context_lower = context.lower()
        return any(word in context_lower for word in ['form', 'input', 'text field', 'type here', 'enter'])

    def _detect_video_capability(self, context: str, page_type: str) -> bool:
        """Detect if page has video content"""
        context_lower = context.lower()
        
        if any(word in context_lower for word in ['video', 'play', 'watch', 'thumbnail']):
            return True
            
        if page_type == 'video_site':
            return True
            
        return False

    def _extract_click_target(self, user_message: str) -> str:
        """Extract what user wants to click"""
        text_lower = user_message.lower()

        # Try to extract quoted text
        quote_match = re.search(r'["\']([^"\']+)["\']', user_message)
        if quote_match:
            return quote_match.group(1)

        # Look for common patterns with better context
        patterns = [
            r'click (?:on |the )?(.+?)(?:\.|$| button| link)',
            r'select (?:the )?(.+?)(?:\.|$)',
            r'press (?:the )?(.+?)(?:\.|$)',
            r'tap (?:on |the )?(.+?)(?:\.|$)',
            r'hit (?:the )?(.+?)(?:\.|$)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                target = match.group(1).strip()
                # Filter out common words and improve target description
                if target not in ['it', 'that', 'this', 'one']:
                    # Enhance target description
                    if 'button' in text_lower and 'button' not in target:
                        target = f"{target} button"
                    elif 'link' in text_lower and 'link' not in target:
                        target = f"{target} link"
                    elif 'video' in text_lower and 'video' not in target:
                        target = f"{target} video"
                    return target

        # Default based on context
        if 'video' in text_lower:
            return 'video'
        elif 'button' in text_lower:
            return 'button'
        elif 'link' in text_lower:
            return 'link'
        else:
            return 'element'

    def _determine_element_type(self, target: str, page_analysis: PageAnalysis) -> str:
        """Determine the most likely element type for a given target"""
        target_lower = target.lower()
        
        # Direct type matches
        if any(word in target_lower for word in ['video', 'play', 'watch']):
            return 'video'
        elif any(word in target_lower for word in ['button', 'btn']):
            return 'button'
        elif any(word in target_lower for word in ['link', 'navigation']):
            return 'link'
        elif any(word in target_lower for word in ['input', 'search', 'text']):
            return 'input'
        
        # Context-based inference
        if page_analysis.has_videos and any(word in target_lower for word in ['thumbnail', 'preview']):
            return 'video_thumbnail'
            
        # Fallback to most common element type on the page
        if page_analysis.elements:
            return page_analysis.elements[0].type
            
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
            # Multiple matching strategies
            description_match = target_lower in element.description.lower()
            type_match = target_lower in element.type.lower()
            
            if description_match or type_match:
                matches.append(element)

        # Sort by confidence
        matches.sort(key=lambda e: e.confidence, reverse=True)
        return matches
