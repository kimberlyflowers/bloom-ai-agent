"""
YouTube Safety Guard - Protects Railway IP from bot detection

Key principle: YouTube detects PATTERNS, not just volume.
- Perfect timing (always 5.0s) = Bot detected
- Human variance (1-8s random) = Looks natural
"""

import time
import random
from datetime import datetime, timedelta
from typing import Tuple
import json
from pathlib import Path

class YouTubeSafetyLevel:
    """Safety levels for YouTube access"""
    TESTING = "testing"        # 5 actions/hour for initial tests
    LOW = "low"               # 15 actions/hour - cautious
    MEDIUM = "medium"         # 30 actions/hour - normal human
    HIGH = "high"             # 50 actions/hour - active human
    MAXIMUM = "maximum"       # 100 actions/hour - power user (risky)

class YouTubeSafetyGuard:
    """
    Protects Railway IP from YouTube bot detection using human-like timing patterns.

    Key principle: YouTube detects PATTERNS, not just volume.
    - Perfect timing (always 5.0s) = Bot detected
    - Human variance (1-8s random) = Looks natural
    """

    def __init__(self, level: str = YouTubeSafetyLevel.MEDIUM):
        self.level = level
        self.data_file = Path("data/youtube_safety_log.json")
        self.data_file.parent.mkdir(exist_ok=True)

        # Human-like limits based on safety level
        self.limits = {
            YouTubeSafetyLevel.TESTING: {
                "max_per_hour": 5,
                "max_per_day": 20,
                "min_delay": 60,      # 1 minute
                "max_delay": 300      # 5 minutes
            },
            YouTubeSafetyLevel.LOW: {
                "max_per_hour": 15,
                "max_per_day": 60,
                "min_delay": 30,      # 30 seconds
                "max_delay": 180      # 3 minutes
            },
            YouTubeSafetyLevel.MEDIUM: {
                "max_per_hour": 30,
                "max_per_day": 150,
                "min_delay": 15,      # 15 seconds
                "max_delay": 120      # 2 minutes
            },
            YouTubeSafetyLevel.HIGH: {
                "max_per_hour": 50,
                "max_per_day": 300,
                "min_delay": 10,      # 10 seconds
                "max_delay": 90       # 90 seconds
            },
            YouTubeSafetyLevel.MAXIMUM: {
                "max_per_hour": 100,
                "max_per_day": 600,
                "min_delay": 5,       # 5 seconds
                "max_delay": 60       # 1 minute
            }
        }

        self.current_limits = self.limits[self.level]
        self._load_or_create_log()

    def _load_or_create_log(self):
        """Load existing log or create new one"""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                self.log = json.load(f)
        else:
            self.log = {
                "actions": [],
                "total_actions": 0,
                "last_action": None,
                "ip_status": "clean",
                "created_at": datetime.now().isoformat()
            }
            self._save_log()

    def _save_log(self):
        """Save log to disk"""
        with open(self.data_file, 'w') as f:
            json.dump(self.log, f, indent=2)

    def _get_human_delay(self) -> float:
        """
        Generate human-like random delay.

        Mimics real human behavior:
        - Most delays are short (quick actions)
        - Occasional longer delays (reading, thinking)
        - Never perfectly consistent
        """
        min_delay = self.current_limits["min_delay"]
        max_delay = self.current_limits["max_delay"]

        # 70% of time: Short delay (min to mid-range)
        # 20% of time: Medium delay (mid to high range)
        # 10% of time: Long delay (thinking pause)

        rand = random.random()

        if rand < 0.7:
            # Quick action
            delay = random.uniform(min_delay, (min_delay + max_delay) / 2)
        elif rand < 0.9:
            # Normal action
            delay = random.uniform((min_delay + max_delay) / 2, max_delay)
        else:
            # Thinking pause (up to 2x max delay)
            delay = random.uniform(max_delay, max_delay * 2)

        # Add micro-variance (humans never click at exact intervals)
        delay += random.uniform(-2, 2)

        return max(min_delay, delay)  # Never go below minimum

    def can_access_youtube(self) -> Tuple[bool, str]:
        """
        Check if YouTube access is allowed based on current rate limits.

        Returns:
            (allowed: bool, reason: str)
        """
        now = datetime.now()

        # Clean old actions (older than 24 hours)
        self._clean_old_actions()

        # Check hourly limit
        hour_ago = now - timedelta(hours=1)
        recent_actions = [
            a for a in self.log["actions"]
            if datetime.fromisoformat(a["timestamp"]) > hour_ago
        ]

        if len(recent_actions) >= self.current_limits["max_per_hour"]:
            next_available = min([
                datetime.fromisoformat(a["timestamp"]) + timedelta(hours=1)
                for a in recent_actions
            ])
            wait_minutes = int((next_available - now).total_seconds() / 60)
            return False, f"Hourly limit reached ({len(recent_actions)}/{self.current_limits['max_per_hour']}). Wait {wait_minutes} minutes."

        # Check daily limit
        day_ago = now - timedelta(days=1)
        daily_actions = [
            a for a in self.log["actions"]
            if datetime.fromisoformat(a["timestamp"]) > day_ago
        ]

        if len(daily_actions) >= self.current_limits["max_per_day"]:
            return False, f"Daily limit reached ({len(daily_actions)}/{self.current_limits['max_per_day']}). Try tomorrow."

        # Check minimum time between actions
        if self.log["last_action"]:
            last_action_time = datetime.fromisoformat(self.log["last_action"])
            time_since_last = (now - last_action_time).total_seconds()

            required_delay = self._get_human_delay()

            if time_since_last < self.current_limits["min_delay"]:
                wait_seconds = int(self.current_limits["min_delay"] - time_since_last)
                return False, f"Too soon after last action. Wait {wait_seconds} seconds (human-like timing)."

        return True, f"✅ Access allowed ({len(recent_actions)}/{self.current_limits['max_per_hour']} this hour)"

    def record_action(self, action_type: str = "tutorial_learning"):
        """Record a YouTube action"""
        now = datetime.now()

        self.log["actions"].append({
            "timestamp": now.isoformat(),
            "type": action_type
        })
        self.log["total_actions"] += 1
        self.log["last_action"] = now.isoformat()

        self._save_log()

    def _clean_old_actions(self):
        """Remove actions older than 24 hours"""
        cutoff = datetime.now() - timedelta(days=1)
        self.log["actions"] = [
            a for a in self.log["actions"]
            if datetime.fromisoformat(a["timestamp"]) > cutoff
        ]
        self._save_log()

    def get_status(self) -> dict:
        """Get current safety status"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)

        recent_hourly = len([
            a for a in self.log["actions"]
            if datetime.fromisoformat(a["timestamp"]) > hour_ago
        ])

        recent_daily = len([
            a for a in self.log["actions"]
            if datetime.fromisoformat(a["timestamp"]) > day_ago
        ])

        return {
            "level": self.level,
            "hourly_usage": f"{recent_hourly}/{self.current_limits['max_per_hour']}",
            "daily_usage": f"{recent_daily}/{self.current_limits['max_per_day']}",
            "total_actions": self.log["total_actions"],
            "last_action": self.log["last_action"],
            "ip_status": self.log["ip_status"]
        }

    def wait_for_next_action(self) -> float:
        """
        Calculate and return human-like delay before next action.

        Returns:
            Delay in seconds
        """
        return self._get_human_delay()

# Global instance - default to MEDIUM safety
youtube_safety = YouTubeSafetyGuard(level=YouTubeSafetyLevel.MEDIUM)
