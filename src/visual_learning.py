"""
Visual Learning System - Sarah Learns from UI/UX Experiences

This system allows Sarah to:
1. Extract skills from visual experiences (watching videos, using software)
2. Learn from experimentation (try things, see what works)
3. Save learned knowledge to her DNA
4. Share learning with all agents through genealogy

Key Philosophy:
- No external API dependencies
- Learn from direct experience with software
- Test, experiment, discover autonomously
- "When one agent learns, they all learn"
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class UIPattern:
    """A learned UI pattern - reusable knowledge about interfaces"""
    pattern_id: str
    pattern_type: str  # 'login_flow', 'form_fill', 'navigation', 'search', etc.
    description: str
    steps: List[str]  # Step-by-step instructions
    visual_markers: List[str]  # What to look for visually
    common_issues: List[str]  # What can go wrong
    success_rate: float  # How often this pattern works
    learned_from: str  # URL or context where learned
    timestamp: str


@dataclass
class Skill:
    """A learned skill - higher level than UI patterns"""
    skill_id: str
    skill_name: str
    description: str
    related_patterns: List[str]  # UIPattern IDs this skill uses
    platform: str  # 'Gmail', 'TikTok', 'YouTube', etc.
    confidence: float  # How confident Sarah is in this skill
    usage_count: int  # How many times successfully used
    learned_date: str
    last_used: str


@dataclass
class ExperimentResult:
    """Result from Sarah trying something"""
    experiment_id: str
    action_taken: str
    expected_result: str
    actual_result: str
    success: bool
    screenshot_before: Optional[str]  # Base64 screenshot
    screenshot_after: Optional[str]  # Base64 screenshot
    learned_insight: str
    timestamp: str


class VisualLearningEngine:
    """
    Engine that extracts skills from Sarah's visual experiences

    This enables:
    - Learning UI patterns from screenshots
    - Extracting workflows from watching her work
    - Building reusable skills from experimentation
    - Sharing knowledge across all agents
    """

    def __init__(self, agent_id: str = "sarah_001"):
        self.agent_id = agent_id
        self.data_dir = Path("data/agent_learning")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Storage files
        self.patterns_file = self.data_dir / f"{agent_id}_ui_patterns.json"
        self.skills_file = self.data_dir / f"{agent_id}_skills.json"
        self.experiments_file = self.data_dir / f"{agent_id}_experiments.json"

        # Shared knowledge (all agents can access)
        self.shared_patterns_file = self.data_dir / "shared_ui_patterns.json"
        self.shared_skills_file = self.data_dir / "shared_skills.json"

        # Load existing knowledge
        self.ui_patterns: Dict[str, UIPattern] = self._load_patterns()
        self.skills: Dict[str, Skill] = self._load_skills()
        self.experiments: List[ExperimentResult] = self._load_experiments()

        # Load shared knowledge from other agents
        self.shared_patterns: Dict[str, UIPattern] = self._load_shared_patterns()
        self.shared_skills: Dict[str, Skill] = self._load_shared_skills()

        logger.info(f"📚 Visual Learning Engine initialized for {agent_id}")
        logger.info(f"   Personal patterns: {len(self.ui_patterns)}")
        logger.info(f"   Personal skills: {len(self.skills)}")
        logger.info(f"   Shared patterns: {len(self.shared_patterns)}")
        logger.info(f"   Shared skills: {len(self.shared_skills)}")

    def _load_patterns(self) -> Dict[str, UIPattern]:
        """Load personal UI patterns"""
        if not self.patterns_file.exists():
            return {}

        try:
            with open(self.patterns_file, 'r') as f:
                data = json.load(f)
                return {k: UIPattern(**v) for k, v in data.items()}
        except Exception as e:
            logger.error(f"Error loading patterns: {e}")
            return {}

    def _load_skills(self) -> Dict[str, Skill]:
        """Load personal skills"""
        if not self.skills_file.exists():
            return {}

        try:
            with open(self.skills_file, 'r') as f:
                data = json.load(f)
                return {k: Skill(**v) for k, v in data.items()}
        except Exception as e:
            logger.error(f"Error loading skills: {e}")
            return {}

    def _load_experiments(self) -> List[ExperimentResult]:
        """Load experiment results"""
        if not self.experiments_file.exists():
            return []

        try:
            with open(self.experiments_file, 'r') as f:
                data = json.load(f)
                return [ExperimentResult(**item) for item in data]
        except Exception as e:
            logger.error(f"Error loading experiments: {e}")
            return []

    def _load_shared_patterns(self) -> Dict[str, UIPattern]:
        """Load shared UI patterns from all agents"""
        if not self.shared_patterns_file.exists():
            return {}

        try:
            with open(self.shared_patterns_file, 'r') as f:
                data = json.load(f)
                return {k: UIPattern(**v) for k, v in data.items()}
        except Exception as e:
            logger.error(f"Error loading shared patterns: {e}")
            return {}

    def _load_shared_skills(self) -> Dict[str, Skill]:
        """Load shared skills from all agents"""
        if not self.shared_skills_file.exists():
            return {}

        try:
            with open(self.shared_skills_file, 'r') as f:
                data = json.load(f)
                return {k: Skill(**v) for k, v in data.items()}
        except Exception as e:
            logger.error(f"Error loading shared skills: {e}")
            return {}

    def save_pattern(self, pattern: UIPattern, share: bool = True):
        """
        Save a learned UI pattern

        Args:
            pattern: The UI pattern to save
            share: If True, also save to shared knowledge (default)
        """
        # Save to personal patterns
        self.ui_patterns[pattern.pattern_id] = pattern

        try:
            with open(self.patterns_file, 'w') as f:
                json.dump({k: asdict(v) for k, v in self.ui_patterns.items()}, f, indent=2)

            logger.info(f"✅ Saved UI pattern: {pattern.pattern_id}")

            # Share with all agents
            if share:
                self.shared_patterns[pattern.pattern_id] = pattern
                with open(self.shared_patterns_file, 'w') as f:
                    json.dump({k: asdict(v) for k, v in self.shared_patterns.items()}, f, indent=2)
                logger.info(f"🌍 Shared pattern with all agents: {pattern.pattern_id}")

        except Exception as e:
            logger.error(f"Error saving pattern: {e}")

    def save_skill(self, skill: Skill, share: bool = True):
        """
        Save a learned skill

        Args:
            skill: The skill to save
            share: If True, also save to shared knowledge (default)
        """
        # Save to personal skills
        self.skills[skill.skill_id] = skill

        try:
            with open(self.skills_file, 'w') as f:
                json.dump({k: asdict(v) for k, v in self.skills.items()}, f, indent=2)

            logger.info(f"✅ Saved skill: {skill.skill_name}")

            # Share with all agents
            if share:
                self.shared_skills[skill.skill_id] = skill
                with open(self.shared_skills_file, 'w') as f:
                    json.dump({k: asdict(v) for k, v in self.shared_skills.items()}, f, indent=2)
                logger.info(f"🌍 Shared skill with all agents: {skill.skill_name}")

        except Exception as e:
            logger.error(f"Error saving skill: {e}")

    def record_experiment(self, result: ExperimentResult):
        """Record an experiment result"""
        self.experiments.append(result)

        try:
            with open(self.experiments_file, 'w') as f:
                json.dump([asdict(exp) for exp in self.experiments], f, indent=2)

            logger.info(f"📊 Recorded experiment: {result.action_taken} → {'✅ Success' if result.success else '❌ Failed'}")

        except Exception as e:
            logger.error(f"Error recording experiment: {e}")

    def extract_pattern_from_experience(
        self,
        action_description: str,
        steps_taken: List[str],
        visual_observations: List[str],
        url: str,
        success: bool
    ) -> Optional[UIPattern]:
        """
        Extract a UI pattern from Sarah's experience

        Args:
            action_description: What Sarah was trying to do
            steps_taken: Steps she took
            visual_observations: What she saw
            url: Where this happened
            success: Whether it worked

        Returns:
            UIPattern if extractable, None otherwise
        """
        if not success:
            logger.info("⚠️ Not extracting pattern - action was not successful")
            return None

        # Generate pattern ID
        pattern_id = f"pattern_{len(self.ui_patterns) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Determine pattern type from description
        desc_lower = action_description.lower()
        if 'login' in desc_lower or 'sign in' in desc_lower:
            pattern_type = 'login_flow'
        elif 'search' in desc_lower:
            pattern_type = 'search'
        elif 'form' in desc_lower or 'fill' in desc_lower:
            pattern_type = 'form_fill'
        elif 'navigate' in desc_lower or 'browse' in desc_lower:
            pattern_type = 'navigation'
        else:
            pattern_type = 'general'

        pattern = UIPattern(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            description=action_description,
            steps=steps_taken,
            visual_markers=visual_observations,
            common_issues=[],  # Will be populated as Sarah encounters issues
            success_rate=1.0,  # First time it worked
            learned_from=url,
            timestamp=datetime.now().isoformat()
        )

        logger.info(f"🎓 Extracted UI pattern: {pattern_type} from {url}")
        return pattern

    def get_relevant_patterns(self, context: str) -> List[UIPattern]:
        """
        Get relevant UI patterns for a context

        Args:
            context: Description of what Sarah is trying to do

        Returns:
            List of relevant patterns (personal + shared)
        """
        all_patterns = {**self.shared_patterns, **self.ui_patterns}

        # Simple relevance matching (can be enhanced with embeddings)
        context_lower = context.lower()
        relevant = []

        for pattern in all_patterns.values():
            if (pattern.pattern_type in context_lower or
                any(word in context_lower for word in pattern.description.lower().split())):
                relevant.append(pattern)

        # Sort by success rate
        relevant.sort(key=lambda p: p.success_rate, reverse=True)

        return relevant

    def get_relevant_skills(self, platform: str) -> List[Skill]:
        """
        Get relevant skills for a platform

        Args:
            platform: Platform name (e.g., 'Gmail', 'TikTok')

        Returns:
            List of relevant skills (personal + shared)
        """
        all_skills = {**self.shared_skills, **self.skills}

        relevant = [
            skill for skill in all_skills.values()
            if skill.platform.lower() == platform.lower()
        ]

        # Sort by confidence and usage
        relevant.sort(key=lambda s: (s.confidence, s.usage_count), reverse=True)

        return relevant

    def update_skill_usage(self, skill_id: str, success: bool):
        """Update skill usage statistics"""
        if skill_id in self.skills:
            skill = self.skills[skill_id]
            skill.usage_count += 1
            skill.last_used = datetime.now().isoformat()

            if success:
                # Increase confidence with successful uses
                skill.confidence = min(1.0, skill.confidence + 0.05)
            else:
                # Decrease confidence with failures
                skill.confidence = max(0.0, skill.confidence - 0.1)

            self.save_skill(skill, share=True)


# Singleton instance
_learning_engine = None


def get_learning_engine(agent_id: str = "sarah_001") -> VisualLearningEngine:
    """Get the global learning engine instance"""
    global _learning_engine
    if _learning_engine is None:
        _learning_engine = VisualLearningEngine(agent_id)
    return _learning_engine
