"""
Learning Replay Visualization - Transparent agent decision-making

Shows users HOW and WHY agents made decisions, building trust and enabling
users to learn marketing strategies from their agents.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """Types of decisions agents make"""
    STRATEGY_SELECTION = "strategy_selection"
    BUDGET_ALLOCATION = "budget_allocation"
    PLATFORM_CHOICE = "platform_choice"
    CONTENT_CREATION = "content_creation"
    AUDIENCE_TARGETING = "audience_targeting"
    TIMING_OPTIMIZATION = "timing_optimization"
    EXPERIMENTATION = "experimentation"


@dataclass
class DecisionEvent:
    """Single decision made by agent"""
    timestamp: datetime
    agent_id: str
    decision_type: DecisionType
    decision: str  # What was decided
    reasoning: str  # Why this decision was made

    # Context
    available_options: List[str]  # What options were considered
    selected_option: str  # Which was chosen

    # Scoring
    option_scores: Dict[str, float]  # Score for each option

    # Outcome
    expected_outcome: str  # What agent expected
    actual_outcome: Optional[str] = None  # What actually happened
    success: Optional[bool] = None  # Did it work?


@dataclass
class LearningPhase:
    """Phase of agent learning"""
    phase_name: str
    start_date: datetime
    end_date: Optional[datetime]
    description: str
    key_discoveries: List[str] = field(default_factory=list)
    decisions: List[DecisionEvent] = field(default_factory=list)


@dataclass
class LearningJourney:
    """Complete learning journey of an agent"""
    agent_id: str
    created_at: datetime

    # Phases
    phases: List[LearningPhase] = field(default_factory=list)

    # Milestones
    milestones: List[dict] = field(default_factory=list)

    # Performance timeline
    performance_timeline: List[dict] = field(default_factory=list)  # {date, roi, conversions}


class LearningReplay:
    """
    Captures and visualizes agent learning journey.

    Enables users to:
    - See every decision the agent made
    - Understand WHY each decision was made
    - Learn which strategies work
    - Identify breakthrough moments
    - Build trust through transparency
    """

    def __init__(self):
        # Journeys for all agents
        self.journeys: Dict[str, LearningJourney] = {}

    def start_journey(self, agent_id: str):
        """Start tracking learning journey for an agent"""
        journey = LearningJourney(
            agent_id=agent_id,
            created_at=datetime.now()
        )

        # Initialize first phase (Discovery)
        discovery_phase = LearningPhase(
            phase_name="Discovery",
            start_date=datetime.now(),
            end_date=None,
            description="Agent is exploring different strategies to find what works"
        )
        journey.phases.append(discovery_phase)

        self.journeys[agent_id] = journey
        logger.info(f"Started learning journey for {agent_id}")

    def record_decision(self, agent_id: str, decision_type: DecisionType,
                       decision: str, reasoning: str,
                       available_options: List[str],
                       selected_option: str,
                       option_scores: Dict[str, float],
                       expected_outcome: str):
        """Record a decision made by the agent"""
        if agent_id not in self.journeys:
            self.start_journey(agent_id)

        journey = self.journeys[agent_id]

        event = DecisionEvent(
            timestamp=datetime.now(),
            agent_id=agent_id,
            decision_type=decision_type,
            decision=decision,
            reasoning=reasoning,
            available_options=available_options,
            selected_option=selected_option,
            option_scores=option_scores,
            expected_outcome=expected_outcome
        )

        # Add to current phase
        current_phase = journey.phases[-1]
        current_phase.decisions.append(event)

        logger.info(f"{agent_id} decided: {decision} (reasoning: {reasoning})")

    def record_outcome(self, agent_id: str, decision_timestamp: datetime,
                      actual_outcome: str, success: bool):
        """Record the actual outcome of a decision"""
        if agent_id not in self.journeys:
            return

        journey = self.journeys[agent_id]

        # Find the decision
        for phase in journey.phases:
            for decision in phase.decisions:
                if decision.timestamp == decision_timestamp:
                    decision.actual_outcome = actual_outcome
                    decision.success = success

                    # If this was a breakthrough, record it
                    if success and decision.decision_type == DecisionType.STRATEGY_SELECTION:
                        journey.milestones.append({
                            'timestamp': datetime.now(),
                            'type': 'breakthrough',
                            'description': f"Discovered successful strategy: {decision.selected_option}"
                        })

                    logger.info(f"{agent_id} outcome: {actual_outcome} ({'success' if success else 'failure'})")
                    return

    def advance_phase(self, agent_id: str, new_phase_name: str, description: str):
        """Move agent to new learning phase"""
        if agent_id not in self.journeys:
            return

        journey = self.journeys[agent_id]

        # End current phase
        current_phase = journey.phases[-1]
        current_phase.end_date = datetime.now()

        # Start new phase
        new_phase = LearningPhase(
            phase_name=new_phase_name,
            start_date=datetime.now(),
            end_date=None,
            description=description
        )
        journey.phases.append(new_phase)

        # Record milestone
        journey.milestones.append({
            'timestamp': datetime.now(),
            'type': 'phase_change',
            'description': f"Entered {new_phase_name} phase"
        })

        logger.info(f"{agent_id} advanced to {new_phase_name} phase")

    def generate_replay(self, agent_id: str, format: str = "text") -> str:
        """
        Generate replay of agent's learning journey.

        Formats:
        - text: Human-readable text
        - json: Structured data for visualization
        - html: Interactive HTML timeline
        """
        if agent_id not in self.journeys:
            return "No journey recorded for this agent"

        journey = self.journeys[agent_id]

        if format == "text":
            return self._generate_text_replay(journey)
        elif format == "json":
            return self._generate_json_replay(journey)
        else:
            return "Format not supported"

    def _generate_text_replay(self, journey: LearningJourney) -> str:
        """Generate human-readable text replay"""
        lines = []
        lines.append("=" * 80)
        lines.append(f"LEARNING JOURNEY: {journey.agent_id}".center(80))
        lines.append("=" * 80)
        lines.append(f"\nStarted: {journey.created_at.strftime('%Y-%m-%d')}")
        lines.append(f"Duration: {(datetime.now() - journey.created_at).days} days")

        # Show phases
        for i, phase in enumerate(journey.phases, 1):
            lines.append(f"\n{'='*80}")
            lines.append(f"PHASE {i}: {phase.phase_name.upper()}")
            lines.append(f"{'='*80}")
            lines.append(f"\n{phase.description}")

            duration = "ongoing"
            if phase.end_date:
                duration = f"{(phase.end_date - phase.start_date).days} days"
            lines.append(f"Duration: {duration}")

            # Show key decisions
            if phase.decisions:
                lines.append(f"\nKey Decisions ({len(phase.decisions)}):")

                for j, decision in enumerate(phase.decisions[:5], 1):  # Show first 5
                    lines.append(f"\n{j}. {decision.decision}")
                    lines.append(f"   Reasoning: {decision.reasoning}")
                    lines.append(f"   Options considered: {len(decision.available_options)}")

                    # Show top 3 options and scores
                    sorted_options = sorted(
                        decision.option_scores.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )
                    lines.append(f"   Scoring:")
                    for option, score in sorted_options[:3]:
                        marker = "✅" if option == decision.selected_option else "  "
                        lines.append(f"     {marker} {option}: {score:.2f}")

                    if decision.actual_outcome:
                        result = "✅ SUCCESS" if decision.success else "❌ FAILED"
                        lines.append(f"   Result: {result} - {decision.actual_outcome}")

            # Show discoveries
            if phase.key_discoveries:
                lines.append(f"\nKey Discoveries:")
                for discovery in phase.key_discoveries:
                    lines.append(f"  • {discovery}")

        # Show milestones
        if journey.milestones:
            lines.append(f"\n{'='*80}")
            lines.append("MILESTONES")
            lines.append(f"{'='*80}")

            for milestone in journey.milestones:
                timestamp = milestone['timestamp'].strftime('%Y-%m-%d')
                lines.append(f"\n🎯 {timestamp}: {milestone['description']}")

        return "\n".join(lines)

    def _generate_json_replay(self, journey: LearningJourney) -> Dict:
        """Generate structured JSON replay for visualization"""
        return {
            'agent_id': journey.agent_id,
            'created_at': journey.created_at.isoformat(),
            'phases': [
                {
                    'name': phase.phase_name,
                    'start': phase.start_date.isoformat(),
                    'end': phase.end_date.isoformat() if phase.end_date else None,
                    'description': phase.description,
                    'decisions': len(phase.decisions),
                    'discoveries': phase.key_discoveries
                }
                for phase in journey.phases
            ],
            'milestones': [
                {
                    'timestamp': m['timestamp'].isoformat(),
                    'type': m['type'],
                    'description': m['description']
                }
                for m in journey.milestones
            ],
            'performance_timeline': journey.performance_timeline
        }

    def get_counterfactuals(self, agent_id: str, decision_timestamp: datetime) -> Dict:
        """
        Show what would have happened with different decisions.

        "What if the agent had chosen Discord instead of Twitter?"
        """
        if agent_id not in self.journeys:
            return {}

        journey = self.journeys[agent_id]

        # Find decision
        for phase in journey.phases:
            for decision in phase.decisions:
                if decision.timestamp == decision_timestamp:
                    counterfactuals = {}

                    for option in decision.available_options:
                        if option == decision.selected_option:
                            continue  # Skip actual choice

                        # Estimate outcome if this option was chosen
                        score = decision.option_scores.get(option, 0.0)
                        estimated_outcome = self._estimate_outcome(score)

                        counterfactuals[option] = {
                            'score': score,
                            'estimated_outcome': estimated_outcome,
                            'comparison': f"{'Better' if score > decision.option_scores[decision.selected_option] else 'Worse'} than actual choice"
                        }

                    return counterfactuals

        return {}

    def _estimate_outcome(self, score: float) -> str:
        """Estimate outcome based on score"""
        if score > 8.0:
            return "Likely very successful (8+ ROI expected)"
        elif score > 5.0:
            return "Likely successful (5-8x ROI expected)"
        elif score > 3.0:
            return "Moderately successful (3-5x ROI expected)"
        elif score > 1.5:
            return "Marginally successful (1.5-3x ROI expected)"
        else:
            return "Likely unsuccessful (<1.5x ROI expected)"


if __name__ == "__main__":
    # Demo
    print("=" * 80)
    print("LEARNING REPLAY VISUALIZATION - DEMO".center(80))
    print("=" * 80)

    replay = LearningReplay()

    # Start agent journey
    replay.start_journey("agent_alpha")

    # Simulate learning over time
    import time
    from datetime import timedelta

    # Week 1: Discovery - trying different strategies
    print("\n1. RECORDING DECISIONS (Week 1: Discovery)")
    print("-" * 80)

    replay.record_decision(
        "agent_alpha",
        DecisionType.STRATEGY_SELECTION,
        "Try Discord helpful replies strategy",
        "Discord communities value genuine help. Low spam tolerance means high-quality engagement needed.",
        available_options=["discord_helpful_reply", "twitter_thread", "reddit_post"],
        selected_option="discord_helpful_reply",
        option_scores={
            "discord_helpful_reply": 5.2,
            "twitter_thread": 2.8,
            "reddit_post": 1.5
        },
        expected_outcome="5.2x ROI from Discord engagement"
    )

    print("✅ Recorded: Discord strategy selection")

    # Record outcome after testing
    replay.record_outcome(
        "agent_alpha",
        list(replay.journeys["agent_alpha"].phases[0].decisions)[0].timestamp,
        "Achieved 5.4x ROI from Discord - strategy works!",
        success=True
    )

    # Week 2-3: More experimentation
    replay.record_decision(
        "agent_alpha",
        DecisionType.PLATFORM_CHOICE,
        "Experiment with Twitter threads",
        "Twitter threads can go viral. Worth testing even though score is lower.",
        available_options=["discord", "twitter", "telegram"],
        selected_option="twitter",
        option_scores={
            "discord": 5.4,  # Proven
            "twitter": 2.8,  # Unknown
            "telegram": 3.2  # Moderate
        },
        expected_outcome="2.8x ROI, but potential for viral growth"
    )

    print("✅ Recorded: Twitter experimentation")

    # Week 4: Breakthrough!
    replay.advance_phase(
        "agent_alpha",
        "Optimization",
        "Agent found strategies that work and is now optimizing them"
    )

    replay.record_decision(
        "agent_alpha",
        DecisionType.BUDGET_ALLOCATION,
        "Allocate 60% budget to Discord, 40% to Twitter",
        "Discord is proven (5.4x ROI), Twitter showing promise (improving to 4.1x). Balanced approach.",
        available_options=["100% Discord", "60% Discord / 40% Twitter", "50/50 split"],
        selected_option="60% Discord / 40% Twitter",
        option_scores={
            "100% Discord": 5.4,
            "60% Discord / 40% Twitter": 6.2,  # Combined = higher!
            "50/50 split": 5.8
        },
        expected_outcome="6.2x combined ROI from diversified approach"
    )

    print("✅ Recorded: Budget optimization")

    # Generate replay
    print("\n2. LEARNING REPLAY")
    print("-" * 80)

    text_replay = replay.generate_replay("agent_alpha", format="text")
    print(text_replay)

    # Show counterfactuals
    print("\n3. COUNTERFACTUAL ANALYSIS (What If?)")
    print("-" * 80)

    first_decision = list(replay.journeys["agent_alpha"].phases[0].decisions)[0]
    counterfactuals = replay.get_counterfactuals("agent_alpha", first_decision.timestamp)

    print("\nWhat if agent had chosen differently?")
    for option, data in counterfactuals.items():
        print(f"\n  IF CHOSEN: {option}")
        print(f"    Score: {data['score']:.2f}")
        print(f"    Estimated outcome: {data['estimated_outcome']}")
        print(f"    {data['comparison']}")

    print("\n" + "=" * 80)
    print("KEY BENEFITS".center(80))
    print("=" * 80)
    print("""
1. TRANSPARENCY
   - See every decision the agent made
   - Understand WHY each choice was made
   - Build trust through visibility

2. LEARNING
   - Users learn what strategies work
   - Understand platform dynamics
   - Apply insights to other marketing

3. DEBUGGING
   - Identify when agent made wrong choice
   - See where assumptions were wrong
   - Fix strategy scoring logic

4. COUNTERFACTUAL ANALYSIS
   - "What if agent chose Twitter instead?"
   - Learn from paths not taken
   - Understand decision quality

5. MILESTONE TRACKING
   - See breakthrough moments
   - Celebrate progress
   - Understand learning curve

RECOMMENDATION: Use for all agents to build user trust!
    """)
    print("=" * 80)
