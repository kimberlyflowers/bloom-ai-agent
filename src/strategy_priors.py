"""
BLOOM AI Agent - Strategy Priors (Initial Knowledge Seeding)

Seeds agents with initial ROI estimates based on proven best practices.
Uses WEAK priors (1-2 samples) so real data easily overrides assumptions.

This is like teaching "fire is hot" vs letting agents burn themselves.
Some knowledge is worth seeding!
"""

from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class StrategyPriors:
    """
    Initial knowledge about what strategies tend to work well.

    Based on:
    - Platform best practices
    - Industry knowledge
    - Marketing research
    - Common sense

    IMPORTANT: These are WEAK priors (1-2 samples only).
    Real data will quickly override if these assumptions are wrong.
    """

    # Best Practices Knowledge Base
    PLATFORM_PRIORS = {
        # Discord - Community-focused, helpful engagement
        'discord': {
            'general_effectiveness': 4.5,  # Expected ROI: 4.5x (good!)
            'reasoning': 'Discord communities value genuine help, low spam tolerance',
            'best_practices': [
                'Helpful replies to questions',
                'Share valuable resources',
                'Build trust before promoting',
                'Join relevant servers (creative tools, IP protection)'
            ],
            'avoid': [
                'DM spam',
                'Self-promotion in wrong channels',
                'Copy-paste messages'
            ]
        },

        # Telegram - International, crypto/tech-savvy
        'telegram': {
            'general_effectiveness': 3.8,  # Expected ROI: 3.8x (pretty good)
            'reasoning': 'Tech-savvy users, global reach, bot-friendly',
            'best_practices': [
                'Join creator/artist groups',
                'Respond to IP concerns',
                'Offer genuine solutions',
                'Use bot commands thoughtfully'
            ],
            'avoid': [
                'Broadcast spam',
                'Join and immediately promote'
            ]
        },

        # Slack - Professional, B2B focus
        'slack': {
            'general_effectiveness': 3.5,  # Expected ROI: 3.5x (good for B2B)
            'reasoning': 'Professional users, higher LTV, studio/agency focus',
            'best_practices': [
                'Join design/creative Slacks',
                'Professional tone',
                'Focus on business value (ROI, protection)',
                'Target decision-makers'
            ],
            'avoid': [
                'Casual tone',
                'Public channel spam'
            ]
        },

        # Twitter/X - Public, viral potential
        'twitter': {
            'general_effectiveness': 2.5,  # Expected ROI: 2.5x (moderate)
            'reasoning': 'Public platform, can go viral, but noisy',
            'best_practices': [
                'Educational threads (IP protection tips)',
                'Reply to creators discussing theft',
                'Share success stories',
                'Use relevant hashtags (#AIart #CreatorEconomy)'
            ],
            'avoid': [
                'Reply spam',
                'Generic sales pitches',
                'Ignoring context'
            ]
        },

        # Reddit - Educational, anti-spam
        'reddit': {
            'general_effectiveness': 2.0,  # Expected ROI: 2.0x (risky if not careful)
            'reasoning': 'Anti-spam culture, must provide genuine value',
            'best_practices': [
                'Answer questions genuinely',
                'Participate in community first',
                'Educational AMAs (with mod approval)',
                'Subtle mentions, never hard sell'
            ],
            'avoid': [
                'Direct promotion without value',
                'New account posting links',
                'Ignoring subreddit rules',
                'Generic copy-paste comments'
            ]
        }
    }

    # Strategy-specific priors
    STRATEGY_PRIORS = {
        # High-confidence strategies (we're pretty sure these work)
        'discord_helpful_reply': {
            'initial_roi': 5.0,
            'confidence': 'medium',  # 2 samples (moderately confident)
            'samples': 2,
            'reasoning': 'Discord users value genuine help, good community fit'
        },

        'telegram_channel_post': {
            'initial_roi': 4.2,
            'confidence': 'medium',
            'samples': 2,
            'reasoning': 'Telegram channels reach engaged audiences'
        },

        'slack_dm_follow_up': {
            'initial_roi': 3.8,
            'confidence': 'low',  # 1 sample (not very confident)
            'samples': 1,
            'reasoning': 'Professional context, higher conversion potential'
        },

        # Moderate-confidence strategies
        'twitter_thread': {
            'initial_roi': 2.8,
            'confidence': 'low',
            'samples': 1,
            'reasoning': 'Educational threads can go viral, but hit or miss'
        },

        'twitter_reply': {
            'initial_roi': 2.3,
            'confidence': 'low',
            'samples': 1,
            'reasoning': 'Contextual replies work, but easy to get wrong'
        },

        # Lower-confidence strategies (educated guesses)
        'reddit_value_comment': {
            'initial_roi': 2.0,
            'confidence': 'low',
            'samples': 1,
            'reasoning': 'Can work if done carefully, but risky'
        },

        'reddit_educational_post': {
            'initial_roi': 1.8,
            'confidence': 'low',
            'samples': 1,
            'reasoning': 'Needs mod approval, must be genuinely educational'
        },

        # Paid strategies (lower confidence due to cost)
        'discord_boost': {
            'initial_roi': 1.5,
            'confidence': 'very_low',
            'samples': 0,  # No initial assumption (let agent test)
            'reasoning': 'Paid promotion, ROI depends on targeting'
        },

        'reddit_boost': {
            'initial_roi': 1.3,
            'confidence': 'very_low',
            'samples': 0,
            'reasoning': 'Reddit ads can work but expensive'
        }
    }

    @classmethod
    def seed_agent_strategies(cls, agent) -> Dict[str, int]:
        """
        Seed an agent's strategies with initial ROI estimates.

        Returns dict of {strategy_name: samples_added}
        """
        seeded = {}

        for strategy_name, strategy in agent.strategies.items():
            # Check if we have prior knowledge for this strategy
            if strategy_name in cls.STRATEGY_PRIORS:
                prior = cls.STRATEGY_PRIORS[strategy_name]

                # Only seed if we have samples to add
                if prior['samples'] > 0:
                    # Add initial ROI estimates (weak priors)
                    initial_rois = [prior['initial_roi']] * prior['samples']
                    strategy.roi_history.extend(initial_rois)

                    seeded[strategy_name] = prior['samples']

                    logger.info(f"Seeded {strategy_name}: {prior['initial_roi']:.1f}x ROI "
                               f"({prior['samples']} samples, {prior['confidence']} confidence)")
                    logger.debug(f"  Reasoning: {prior['reasoning']}")

        return seeded

    @classmethod
    def get_platform_advice(cls, platform: str) -> Dict:
        """Get best practices advice for a platform"""
        return cls.PLATFORM_PRIORS.get(platform, {
            'general_effectiveness': 2.0,
            'reasoning': 'Unknown platform, start cautious',
            'best_practices': ['Test carefully', 'Monitor results'],
            'avoid': ['Spam', 'Generic messages']
        })

    @classmethod
    def explain_priors(cls):
        """Print explanation of initial knowledge"""
        print("\n" + "="*80)
        print("INITIAL KNOWLEDGE (Strategy Priors)".center(80))
        print("="*80)
        print("\nThese are WEAK priors - educated guesses to give agents a head start.")
        print("Real data will QUICKLY override these if they're wrong!\n")

        print("Platform Effectiveness Estimates:")
        print("-" * 80)
        for platform, info in cls.PLATFORM_PRIORS.items():
            print(f"\n{platform.upper()}: {info['general_effectiveness']:.1f}x expected ROI")
            print(f"  Why: {info['reasoning']}")
            print(f"  Best practices: {', '.join(info['best_practices'][:2])}...")

        print("\n" + "="*80)
        print("Strategy-Specific Priors:")
        print("-" * 80)
        for strategy, prior in cls.STRATEGY_PRIORS.items():
            if prior['samples'] > 0:
                confidence_marker = {
                    'high': '🟢',
                    'medium': '🟡',
                    'low': '🟠',
                    'very_low': '🔴'
                }.get(prior['confidence'], '⚪')

                print(f"\n{confidence_marker} {strategy}:")
                print(f"   Initial ROI: {prior['initial_roi']:.1f}x")
                print(f"   Confidence: {prior['confidence']} ({prior['samples']} samples)")
                print(f"   Why: {prior['reasoning']}")

        print("\n" + "="*80)
        print("NOTE: These are starting points only!".center(80))
        print("Agents will learn from REAL data and update these beliefs.".center(80))
        print("="*80 + "\n")


# Example usage in agent creation
def create_seeded_agent(agent_id: str, initial_balance: float = 50.0):
    """
    Create an agent with seeded initial knowledge.

    This gives the agent a head start based on best practices,
    while still allowing it to learn and discover better strategies.
    """
    from ai_agent import BloomAIAgent, Specialization

    # Create agent normally
    agent = BloomAIAgent(
        agent_id=agent_id,
        initial_balance=initial_balance,
        specialization=Specialization.GENERALIST
    )

    # Seed with initial knowledge
    seeded = StrategyPriors.seed_agent_strategies(agent)

    logger.info(f"Agent '{agent_id}' created with {len(seeded)} strategies seeded")

    return agent, seeded


if __name__ == "__main__":
    # Demo the priors
    StrategyPriors.explain_priors()
