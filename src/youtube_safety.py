"""
YouTube Safety System - Prevents detection and bans
Rate limits, human-like behavior, and anti-detection measures
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class YouTubeSafetyLevel(Enum):
    """Safety levels for different risk scenarios"""
    MAXIMUM = "maximum"      # No YouTube access at all
    HIGH = "high"            # Extreme rate limiting (1/hour)
    MEDIUM = "medium"        # Moderate rate limiting (3/hour)
    LOW = "low"              # Minimal rate limiting (10/hour)
    TESTING = "testing"      # Development/testing (no limits)


@dataclass
class YouTubeActionRecord:
    """Record of a YouTube action for rate limiting"""
    timestamp: datetime
    action_type: str  # "watch", "search", "click", "navigate"
    video_id: Optional[str] = None
    duration_seconds: Optional[float] = None
    success: bool = True


class YouTubeSafetyGuard:
    """
    Main safety guard that prevents YouTube detection
    Implements rate limiting, human-like behavior, and detection avoidance
    """
    
    # SAFETY CONSTANTS - DO NOT CHANGE THESE LIGHTLY!
    MAX_ACTIONS_PER_HOUR = 3          # Maximum YouTube actions per hour
    MIN_TIME_BETWEEN_ACTIONS = 300    # Minimum 5 minutes between actions
    MAX_WATCH_TIME_PER_SESSION = 1800 # Maximum 30 minutes per session
    MAX_SESSIONS_PER_DAY = 2          # Max 2 YouTube sessions per day
    COOLING_PERIOD_HOURS = 24         # 24-hour cooling if detection suspected
    
    def __init__(self, safety_level: YouTubeSafetyLevel = YouTubeSafetyLevel.MEDIUM):
        self.safety_level = safety_level
        self.action_history: List[YouTubeActionRecord] = []
        self.session_start: Optional[datetime] = None
        self.detection_warnings: int = 0
        self.last_detection: Optional[datetime] = None
        
        # Adjust limits based on safety level
        self._adjust_limits_by_safety()
        
        logger.info(f"YouTube Safety Guard initialized at {safety_level.value} level")
        logger.info(f"Rate limits: {self.MAX_ACTIONS_PER_HOUR}/hour, "
                   f"{self.MIN_TIME_BETWEEN_ACTIONS}s between actions")
    
    def _adjust_limits_by_safety(self):
        """Adjust safety limits based on safety level"""
        if self.safety_level == YouTubeSafetyLevel.MAXIMUM:
            self.MAX_ACTIONS_PER_HOUR = 0
            self.MIN_TIME_BETWEEN_ACTIONS = 999999
        elif self.safety_level == YouTubeSafetyLevel.HIGH:
            self.MAX_ACTIONS_PER_HOUR = 1
            self.MIN_TIME_BETWEEN_ACTIONS = 3600
        elif self.safety_level == YouTubeSafetyLevel.MEDIUM:
            self.MAX_ACTIONS_PER_HOUR = 3
            self.MIN_TIME_BETWEEN_ACTIONS = 300
        elif self.safety_level == YouTubeSafetyLevel.LOW:
            self.MAX_ACTIONS_PER_HOUR = 10
            self.MIN_TIME_BETWEEN_ACTIONS = 60
        elif self.safety_level == YouTubeSafetyLevel.TESTING:
            self.MAX_ACTIONS_PER_HOUR = 999
            self.MIN_TIME_BETWEEN_ACTIONS = 1
    
    async def can_perform_action(self, action_type: str) -> Tuple[bool, str]:
        """
        Check if an action is allowed based on rate limits and safety rules
        Returns: (allowed: bool, reason: str)
        """
        # Check if completely blocked
        if self.safety_level == YouTubeSafetyLevel.MAXIMUM:
            return False, "YouTube access completely blocked"
        
        # Check cooling period
        if self.last_detection:
            hours_since = (datetime.now() - self.last_detection).total_seconds() / 3600
            if hours_since < self.COOLING_PERIOD_HOURS:
                return False, f"In cooling period ({hours_since:.1f}/{self.COOLING_PERIOD_HOURS} hours)"
        
        # Check daily session limit
        if self._daily_session_limit_reached():
            return False, f"Daily session limit reached ({self.MAX_SESSIONS_PER_DAY}/day)"
        
        # Check hourly action limit
        recent_actions = self._get_recent_actions(hours=1)
        if len(recent_actions) >= self.MAX_ACTIONS_PER_HOUR:
            return False, f"Hourly action limit reached ({len(recent_actions)}/{self.MAX_ACTIONS_PER_HOUR})"
        
        # Check minimum time between actions
        if self.action_history:
            last_action = self.action_history[-1]
            time_since_last = (datetime.now() - last_action.timestamp).total_seconds()
            if time_since_last < self.MIN_TIME_BETWEEN_ACTIONS:
                wait_time = self.MIN_TIME_BETWEEN_ACTIONS - time_since_last
                return False, f"Waiting {wait_time:.0f}s between actions"
        
        return True, "Action allowed"
    
    def _get_recent_actions(self, hours: float = 1) -> List[YouTubeActionRecord]:
        """Get actions within the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [action for action in self.action_history if action.timestamp > cutoff]
    
    def _daily_session_limit_reached(self) -> bool:
        """Check if daily session limit has been reached"""
        today = datetime.now().date()
        today_sessions = 0
        
        for action in self.action_history:
            if action.timestamp.date() == today and action.action_type == "watch":
                today_sessions += 1
        
        return today_sessions >= self.MAX_SESSIONS_PER_DAY
    
    def record_action(self, action_type: str, video_id: Optional[str] = None, 
                     duration_seconds: Optional[float] = None, success: bool = True):
        """Record a YouTube action"""
        record = YouTubeActionRecord(
            timestamp=datetime.now(),
            action_type=action_type,
            video_id=video_id,
            duration_seconds=duration_seconds,
            success=success
        )
        self.action_history.append(record)
        
        if action_type == "watch" and not self.session_start:
            self.session_start = datetime.now()
        
        logger.info(f"Recorded YouTube action: {action_type}")
    
    def record_detection_warning(self):
        """Record a detection warning from YouTube"""
        self.detection_warnings += 1
        self.last_detection = datetime.now()
        
        if self.detection_warnings >= 3:
            logger.warning("Multiple detection warnings - Switching to MAXIMUM safety")
            self.safety_level = YouTubeSafetyLevel.MAXIMUM
            self._adjust_limits_by_safety()
    
    def get_status(self) -> Dict[str, any]:
        """Get current safety status"""
        recent_actions = self._get_recent_actions(hours=1)
        
        return {
            "safety_level": self.safety_level.value,
            "recent_actions_1h": len(recent_actions),
            "max_actions_per_hour": self.MAX_ACTIONS_PER_HOUR,
            "detection_warnings": self.detection_warnings
        }
