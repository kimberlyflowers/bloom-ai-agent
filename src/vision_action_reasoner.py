"""
VISION-GUIDED ACTION REASONING SYSTEM - ENHANCED CLICKING
Fixed to bridge Intent vs Execution Gap with GLOBAL clicking support
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class UIElement:
    type: str
    description: str
    action: str
    confidence: float

@dataclass 
class PageAnalysis:
    page_type: str
    elements: List[UIElement]
    state: str
    observations: List[str]
    has_search: bool = False
    has_forms: bool = False
    has_videos: bool = False

@dataclass
class ActionPlan:
    goal: str
    steps: List[Dict[str, Any]]
    reasoning: str
    confidence: float = 0.5

class VisionActionReasoner:
    """
    SYSTEMATIC CLICKING EXECUTION FRAMEWORK
    Now includes DIRECT execution commands for browser control
    """
    
    def __init__(self):
        self.last_analysis = None
        self.last_plan = None

    def analyze_vision_context(self, screenshot_description: str, url: str) -> PageAnalysis:
        """Enhanced analysis with clickable element detection"""
        observations = []
        elements = []
        
        page_type = self._infer_page_type(url, screenshot_description)
        observations.append(f"Page type: {page_type}")
        
        # ENHANCED: Detect ALL clickable elements
        elements = self._identify_clickable_elements(screenshot_description, page_type)
        observations.append(f"Found {len(elements)} clickable elements")
        
        state = self._determine_page_state(screenshot_description)
        observations.append(f"Page state: {state}")
        
        has_search = self._detect_search_capability
