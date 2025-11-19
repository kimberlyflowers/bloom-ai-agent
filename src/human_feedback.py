"""
BLOOM AI Agent - Human-in-the-Loop Feedback System

Enables humans to rate agent actions and incorporates feedback into learning.
This improves quality, ensures brand alignment, and mitigates ethical risks.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class FeedbackDimension(Enum):
    """Dimensions humans can rate"""
    HELPFULNESS = "helpfulness"  # Was this actually helpful?
    BRAND_ALIGNMENT = "brand_alignment"  # Does this match our brand voice?
    ETHICAL_SAFETY = "ethical_safety"  # Is this ethical and safe?
    LONG_TERM_REPUTATION = "long_term_reputation"  # Good for long-term reputation?
    CREATIVITY = "creativity"  # Is this creative/innovative?


@dataclass
class HumanFeedback:
    """Human feedback on an agent action"""
    action_id: str
    agent_id: str
    platform: str
    strategy_name: str
    content_preview: str

    # Ratings (1-5 scale)
    helpfulness: Optional[int] = None
    brand_alignment: Optional[int] = None
    ethical_safety: Optional[int] = None
    long_term_reputation: Optional[int] = None
    creativity: Optional[int] = None

    # Optional text feedback
    text_feedback: str = ""

    # Metadata
    reviewed_by: str = "user"
    reviewed_at: datetime = field(default_factory=datetime.now)

    def overall_score(self) -> float:
        """Calculate weighted overall score (0-5).

        Weights:
        - Ethical Safety: 30% (most important!)
        - Helpfulness: 25%
        - Brand Alignment: 20%
        - Long-term Reputation: 15%
        - Creativity: 10%
        """
        if self.ethical_safety is None or self.helpfulness is None:
            return 0.0  # Missing critical ratings

        score = (
            (self.ethical_safety or 0) * 0.30 +
            (self.helpfulness or 0) * 0.25 +
            (self.brand_alignment or 0) * 0.20 +
            (self.long_term_reputation or 0) * 0.15 +
            (self.creativity or 0) * 0.10
        )

        return score

    def is_approved(self, min_score: float = 3.5) -> bool:
        """Is this action approved based on human feedback?"""
        # Must have high ethical safety (4+)
        if (self.ethical_safety or 0) < 4:
            return False

        # Must have decent overall score
        return self.overall_score() >= min_score


@dataclass
class ActionForReview:
    """Agent action awaiting human review"""
    action_id: str
    agent_id: str
    timestamp: datetime
    platform: str
    strategy_name: str
    content_preview: str
    context: str

    # Performance data
    estimated_cost: float
    expected_roi: float

    # Risk factors
    is_new_strategy: bool = False  # New strategy = needs review
    is_high_budget: bool = False  # High budget = needs review
    is_borderline_ethical: bool = False  # Uncertain ethics = needs review

    # Review status
    reviewed: bool = False
    feedback: Optional[HumanFeedback] = None

    def priority_score(self) -> float:
        """Calculate priority for review (higher = review first).

        Prioritize:
        - High-budget actions (protect budget)
        - New strategies (high uncertainty)
        - Borderline ethical cases (protect reputation)
        """
        score = 0.0

        if self.is_high_budget:
            score += 10.0  # Very high priority

        if self.is_new_strategy:
            score += 5.0  # High priority

        if self.is_borderline_ethical:
            score += 15.0  # CRITICAL priority

        # Factor in budget (higher budget = higher priority)
        score += min(self.estimated_cost / 10.0, 5.0)

        return score


class HumanFeedbackLoop:
    """
    Manages human-in-the-loop feedback system.

    Flow:
    1. Agent takes action
    2. System determines if review needed (sampling + risk factors)
    3. Human reviews and rates action
    4. Feedback incorporated into agent learning
    """

    def __init__(self, sample_rate: float = 0.1):
        """
        Initialize feedback loop.

        Args:
            sample_rate: Percentage of actions to review (0.1 = 10%)
        """
        self.sample_rate = sample_rate

        # Queue of actions awaiting review
        self.review_queue: List[ActionForReview] = []

        # Historical feedback
        self.feedback_history: List[HumanFeedback] = []

        # Feedback statistics by agent
        self.agent_stats: Dict[str, dict] = {}

    def should_request_review(self, action: dict) -> bool:
        """Determine if action should be reviewed by human.

        Always review:
        - New strategies (high uncertainty)
        - High-budget actions (>$50)
        - Borderline ethical cases

        Sometimes review:
        - Random sample (10% of normal actions)
        """
        # Always review high-risk actions
        if action.get('is_new_strategy', False):
            logger.info(f"Requesting review: New strategy")
            return True

        if action.get('estimated_cost', 0) > 50:
            logger.info(f"Requesting review: High budget (${action['estimated_cost']})")
            return True

        if action.get('is_borderline_ethical', False):
            logger.info(f"Requesting review: Borderline ethical")
            return True

        # Random sampling for normal actions
        import random
        if random.random() < self.sample_rate:
            logger.debug(f"Requesting review: Random sample")
            return True

        return False

    def request_review(self, action: dict) -> ActionForReview:
        """Request human review for an action.

        Args:
            action: Dict with action details

        Returns:
            ActionForReview object
        """
        review = ActionForReview(
            action_id=action['action_id'],
            agent_id=action['agent_id'],
            timestamp=datetime.now(),
            platform=action['platform'],
            strategy_name=action['strategy_name'],
            content_preview=action.get('content_preview', ''),
            context=action.get('context', ''),
            estimated_cost=action.get('estimated_cost', 0.0),
            expected_roi=action.get('expected_roi', 0.0),
            is_new_strategy=action.get('is_new_strategy', False),
            is_high_budget=action.get('estimated_cost', 0) > 50,
            is_borderline_ethical=action.get('is_borderline_ethical', False)
        )

        # Add to review queue (sorted by priority)
        self.review_queue.append(review)
        self.review_queue.sort(key=lambda x: x.priority_score(), reverse=True)

        logger.info(f"Action {action['action_id']} added to review queue "
                   f"(priority: {review.priority_score():.1f})")

        return review

    def get_pending_reviews(self, limit: int = 10) -> List[ActionForReview]:
        """Get actions awaiting review (highest priority first)."""
        return [r for r in self.review_queue if not r.reviewed][:limit]

    def submit_feedback(self, action_id: str, ratings: dict,
                       text_feedback: str = "") -> HumanFeedback:
        """Submit human feedback for an action.

        Args:
            action_id: ID of action being reviewed
            ratings: Dict of {dimension: rating (1-5)}
            text_feedback: Optional text feedback

        Returns:
            HumanFeedback object
        """
        # Find action in queue
        action = None
        for review in self.review_queue:
            if review.action_id == action_id:
                action = review
                break

        if not action:
            raise ValueError(f"Action {action_id} not found in review queue")

        # Create feedback
        feedback = HumanFeedback(
            action_id=action_id,
            agent_id=action.agent_id,
            platform=action.platform,
            strategy_name=action.strategy_name,
            content_preview=action.content_preview,
            helpfulness=ratings.get('helpfulness'),
            brand_alignment=ratings.get('brand_alignment'),
            ethical_safety=ratings.get('ethical_safety'),
            long_term_reputation=ratings.get('long_term_reputation'),
            creativity=ratings.get('creativity'),
            text_feedback=text_feedback
        )

        # Mark as reviewed
        action.reviewed = True
        action.feedback = feedback

        # Store feedback
        self.feedback_history.append(feedback)

        # Update agent stats
        self._update_agent_stats(feedback)

        logger.info(f"Feedback submitted for action {action_id}: "
                   f"Score {feedback.overall_score():.2f}/5.0")

        return feedback

    def _update_agent_stats(self, feedback: HumanFeedback):
        """Update agent statistics with new feedback."""
        agent_id = feedback.agent_id

        if agent_id not in self.agent_stats:
            self.agent_stats[agent_id] = {
                'total_reviews': 0,
                'average_score': 0.0,
                'approval_rate': 0.0,
                'dimension_scores': {
                    'helpfulness': [],
                    'brand_alignment': [],
                    'ethical_safety': [],
                    'long_term_reputation': [],
                    'creativity': []
                }
            }

        stats = self.agent_stats[agent_id]
        stats['total_reviews'] += 1

        # Update dimension scores
        for dim in ['helpfulness', 'brand_alignment', 'ethical_safety',
                    'long_term_reputation', 'creativity']:
            rating = getattr(feedback, dim)
            if rating is not None:
                stats['dimension_scores'][dim].append(rating)

        # Calculate averages
        all_scores = [f.overall_score() for f in self.feedback_history
                     if f.agent_id == agent_id]
        stats['average_score'] = sum(all_scores) / len(all_scores)

        # Calculate approval rate
        approved = [f for f in self.feedback_history
                   if f.agent_id == agent_id and f.is_approved()]
        stats['approval_rate'] = len(approved) / stats['total_reviews']

    def get_agent_feedback_score(self, agent_id: str) -> float:
        """Get agent's average human feedback score (0-5).

        Returns 0.0 if no feedback yet.
        """
        if agent_id not in self.agent_stats:
            return 0.0

        return self.agent_stats[agent_id]['average_score']

    def get_agent_approval_rate(self, agent_id: str) -> float:
        """Get agent's approval rate (0-1).

        Returns 1.0 if no feedback yet (benefit of doubt).
        """
        if agent_id not in self.agent_stats:
            return 1.0

        return self.agent_stats[agent_id]['approval_rate']

    def incorporate_feedback_into_learning(self, agent, feedback: HumanFeedback):
        """Incorporate human feedback into agent's learning.

        Adjusts agent's strategy scoring to include human preferences.
        """
        strategy = agent.strategies.get(feedback.strategy_name)
        if not strategy:
            logger.warning(f"Strategy {feedback.strategy_name} not found")
            return

        # Create human-adjusted ROI
        # Formula: adjusted_roi = base_roi * human_score_multiplier
        human_score = feedback.overall_score()  # 0-5
        human_multiplier = human_score / 5.0  # 0-1

        # If human feedback is very negative, penalize severely
        if human_score < 2.0:
            logger.warning(f"Low human feedback ({human_score:.2f}/5) "
                          f"for {feedback.strategy_name}")
            # Add negative ROI sample to discourage this
            strategy.roi_history.append(0.5 * human_multiplier)

        # If human feedback is very positive, boost!
        elif human_score >= 4.0:
            logger.info(f"High human feedback ({human_score:.2f}/5) "
                       f"for {feedback.strategy_name}")
            # Boost the strategy's perceived value
            if strategy.roi_history:
                avg_roi = strategy.average_roi()
                boosted_roi = avg_roi * (1.0 + (human_score - 3.0) / 5.0)
                strategy.roi_history.append(boosted_roi)

        # Store human feedback in strategy metadata
        if not hasattr(strategy, 'human_feedback_scores'):
            strategy.human_feedback_scores = []
        strategy.human_feedback_scores.append(human_score)

        logger.info(f"Incorporated human feedback into {feedback.strategy_name} learning")


def create_simple_feedback_interface() -> dict:
    """Create a simple feedback interface for demo/testing.

    Returns template for web UI or CLI interface.
    """
    return {
        'interface_type': 'web_form',
        'fields': [
            {
                'name': 'helpfulness',
                'label': 'How helpful was this action?',
                'type': 'rating',
                'min': 1,
                'max': 5,
                'required': True
            },
            {
                'name': 'brand_alignment',
                'label': 'How well does this match our brand voice?',
                'type': 'rating',
                'min': 1,
                'max': 5,
                'required': True
            },
            {
                'name': 'ethical_safety',
                'label': 'Is this ethical and safe?',
                'type': 'rating',
                'min': 1,
                'max': 5,
                'required': True,
                'warning': 'Rate < 3 will flag action for review'
            },
            {
                'name': 'long_term_reputation',
                'label': 'Is this good for long-term reputation?',
                'type': 'rating',
                'min': 1,
                'max': 5,
                'required': False
            },
            {
                'name': 'creativity',
                'label': 'How creative/innovative is this?',
                'type': 'rating',
                'min': 1,
                'max': 5,
                'required': False
            },
            {
                'name': 'text_feedback',
                'label': 'Additional feedback (optional)',
                'type': 'textarea',
                'required': False
            }
        ]
    }


if __name__ == "__main__":
    # Demo the feedback system
    print("=" * 80)
    print("HUMAN-IN-THE-LOOP FEEDBACK SYSTEM - DEMO".center(80))
    print("=" * 80)

    # Create feedback loop
    feedback_loop = HumanFeedbackLoop(sample_rate=0.1)

    # Simulate agent actions
    print("\n1. AGENT ACTIONS")
    print("-" * 80)

    actions = [
        {
            'action_id': 'act_001',
            'agent_id': 'agent_alpha',
            'platform': 'discord',
            'strategy_name': 'discord_helpful_reply',
            'content_preview': 'Hey! I saw your question about IP protection...',
            'context': 'Reply to question in #creative-help',
            'estimated_cost': 5.0,
            'expected_roi': 5.2,
            'is_new_strategy': False
        },
        {
            'action_id': 'act_002',
            'agent_id': 'agent_beta',
            'platform': 'twitter',
            'strategy_name': 'twitter_experimental',
            'content_preview': 'BREAKING: New AI tool helps creators...',
            'context': 'Experimental viral thread',
            'estimated_cost': 75.0,
            'expected_roi': 2.0,
            'is_new_strategy': True,  # NEW! Needs review
            'is_borderline_ethical': True  # Borderline! Needs review
        }
    ]

    for action in actions:
        if feedback_loop.should_request_review(action):
            review = feedback_loop.request_review(action)
            print(f"✅ Requested review for {action['action_id']}")
            print(f"   Platform: {action['platform']}")
            print(f"   Strategy: {action['strategy_name']}")
            print(f"   Priority: {review.priority_score():.1f}")
        else:
            print(f"⏭️  Skipped review for {action['action_id']} (random sampling)")

    # Show review queue
    print("\n2. REVIEW QUEUE (Priority Order)")
    print("-" * 80)
    pending = feedback_loop.get_pending_reviews()
    for i, review in enumerate(pending, 1):
        print(f"\n{i}. {review.action_id} (Priority: {review.priority_score():.1f})")
        print(f"   Agent: {review.agent_id}")
        print(f"   Content: {review.content_preview[:60]}...")
        print(f"   Flags: ", end="")
        flags = []
        if review.is_new_strategy:
            flags.append("NEW STRATEGY")
        if review.is_high_budget:
            flags.append(f"HIGH BUDGET (${review.estimated_cost})")
        if review.is_borderline_ethical:
            flags.append("ETHICAL CONCERN")
        print(", ".join(flags) if flags else "None")

    # Simulate human feedback
    print("\n3. HUMAN FEEDBACK")
    print("-" * 80)

    # Good feedback
    feedback1 = feedback_loop.submit_feedback(
        action_id='act_001',
        ratings={
            'helpfulness': 5,
            'brand_alignment': 4,
            'ethical_safety': 5,
            'long_term_reputation': 5,
            'creativity': 3
        },
        text_feedback="Perfect! Genuine help without being pushy."
    )

    print(f"\nFeedback #1: {feedback1.action_id}")
    print(f"  Overall Score: {feedback1.overall_score():.2f}/5.0")
    print(f"  Approved: {'✅ YES' if feedback1.is_approved() else '❌ NO'}")
    print(f"  Comment: {feedback1.text_feedback}")

    # Poor feedback (ethical concern)
    feedback2 = feedback_loop.submit_feedback(
        action_id='act_002',
        ratings={
            'helpfulness': 3,
            'brand_alignment': 2,
            'ethical_safety': 2,  # LOW! Ethical concern
            'long_term_reputation': 2,
            'creativity': 4
        },
        text_feedback="Too clickbaity and borderline misleading. Doesn't match our brand."
    )

    print(f"\nFeedback #2: {feedback2.action_id}")
    print(f"  Overall Score: {feedback2.overall_score():.2f}/5.0")
    print(f"  Approved: {'✅ YES' if feedback2.is_approved() else '❌ NO'}")
    print(f"  Comment: {feedback2.text_feedback}")

    # Show agent stats
    print("\n4. AGENT PERFORMANCE (Human Feedback)")
    print("-" * 80)

    for agent_id in feedback_loop.agent_stats.keys():
        stats = feedback_loop.agent_stats[agent_id]
        print(f"\n{agent_id}:")
        print(f"  Total Reviews: {stats['total_reviews']}")
        print(f"  Average Score: {stats['average_score']:.2f}/5.0")
        print(f"  Approval Rate: {stats['approval_rate']*100:.1f}%")

        # Dimension breakdown
        print(f"  Dimensions:")
        for dim, scores in stats['dimension_scores'].items():
            if scores:
                avg = sum(scores) / len(scores)
                print(f"    {dim}: {avg:.2f}/5.0")

    print("\n" + "=" * 80)
    print("KEY INSIGHTS".center(80))
    print("=" * 80)
    print("""
1. QUALITY CONTROL
   - Agents get real-time human feedback
   - Low scores penalize strategy in learning
   - High scores boost strategy

2. RISK MITIGATION
   - New strategies reviewed before scaling
   - High-budget actions checked by human
   - Ethical concerns flagged immediately

3. BRAND ALIGNMENT
   - Humans rate brand voice match
   - Agents learn what "sounds like us"
   - Consistent brand experience

4. CONTINUOUS IMPROVEMENT
   - 10% random sampling catches edge cases
   - Feedback incorporated into learning
   - Agents get smarter about human preferences

RECOMMENDATION: Use this for all high-risk actions!
    """)
    print("=" * 80)
