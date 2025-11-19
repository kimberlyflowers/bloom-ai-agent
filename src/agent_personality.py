"""
Agent Personality Customization - Brand Voice Matching

Allows agents to speak in different personalities that match brand voice:
- Friendly Helper (casual, emoji-heavy)
- Expert Consultant (professional, formal)
- Straight-Shooter (edgy, direct)
- Educator (informative, patient)
"""

import logging
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PersonalityType(Enum):
    """Pre-configured personality types"""
    FRIENDLY_HELPER = "friendly_helper"
    EXPERT_CONSULTANT = "expert_consultant"
    STRAIGHT_SHOOTER = "straight_shooter"
    EDUCATOR = "educator"
    COMMUNITY_MEMBER = "community_member"


@dataclass
class PersonalityConfig:
    """Configuration for agent personality"""
    name: str
    description: str

    # Tone settings
    formality: float  # 0-1 (0=casual, 1=formal)
    enthusiasm: float  # 0-1 (0=subdued, 1=enthusiastic)
    directness: float  # 0-1 (0=indirect, 1=direct)

    # Style settings
    emoji_frequency: str  # 'none', 'rare', 'moderate', 'frequent'
    sentence_length: str  # 'short', 'medium', 'long'
    jargon_level: str  # 'simple', 'moderate', 'technical'

    # Content guidelines
    focus: str  # 'problem_solving', 'education', 'promotion', 'community'
    call_to_action_style: str  # 'soft', 'medium', 'strong'

    # Example phrases
    greetings: List[str]
    transitions: List[str]
    closings: List[str]


class PersonalityLibrary:
    """Library of pre-configured personalities"""

    PERSONALITIES: Dict[PersonalityType, PersonalityConfig] = {
        PersonalityType.FRIENDLY_HELPER: PersonalityConfig(
            name="Friendly Helper",
            description="Warm, approachable, emoji-using friend who wants to help",
            formality=0.2,
            enthusiasm=0.8,
            directness=0.6,
            emoji_frequency='frequent',
            sentence_length='short',
            jargon_level='simple',
            focus='problem_solving',
            call_to_action_style='soft',
            greetings=[
                "Hey! 👋",
                "Hi there!",
                "Hey friend!",
                "Hello! 😊"
            ],
            transitions=[
                "BTW,",
                "Also,",
                "Oh! And",
                "Quick tip:"
            ],
            closings=[
                "Hope this helps! 💙",
                "Let me know if you need anything else!",
                "Good luck! 🚀",
                "Happy to help anytime!"
            ]
        ),

        PersonalityType.EXPERT_CONSULTANT: PersonalityConfig(
            name="Expert Consultant",
            description="Professional, knowledgeable consultant offering expertise",
            formality=0.8,
            enthusiasm=0.4,
            directness=0.7,
            emoji_frequency='rare',
            sentence_length='medium',
            jargon_level='moderate',
            focus='education',
            call_to_action_style='medium',
            greetings=[
                "Good day,",
                "Hello,",
                "Greetings,"
            ],
            transitions=[
                "Additionally,",
                "Furthermore,",
                "It's worth noting that",
                "In my experience,"
            ],
            closings=[
                "Best regards,",
                "I hope this information proves helpful.",
                "Feel free to reach out with any questions.",
                "Wishing you success."
            ]
        ),

        PersonalityType.STRAIGHT_SHOOTER: PersonalityConfig(
            name="Straight-Shooter",
            description="Direct, no-nonsense, gets to the point quickly",
            formality=0.3,
            enthusiasm=0.6,
            directness=1.0,
            emoji_frequency='rare',
            sentence_length='short',
            jargon_level='simple',
            focus='problem_solving',
            call_to_action_style='strong',
            greetings=[
                "Listen,",
                "Real talk:",
                "Here's the deal:",
                "Cut to the chase:"
            ],
            transitions=[
                "Bottom line:",
                "Here's what matters:",
                "The key point:",
                "What you need to know:"
            ],
            closings=[
                "Done. Simple as that.",
                "That's it. Get to work.",
                "Now you know. Act on it.",
                "Stop overthinking. Start doing."
            ]
        ),

        PersonalityType.EDUCATOR: PersonalityConfig(
            name="Educator",
            description="Patient teacher who explains concepts thoroughly",
            formality=0.5,
            enthusiasm=0.6,
            directness=0.5,
            emoji_frequency='moderate',
            sentence_length='long',
            jargon_level='moderate',
            focus='education',
            call_to_action_style='soft',
            greetings=[
                "Let me explain:",
                "Great question!",
                "I'm happy to walk you through this.",
                "Let's break this down:"
            ],
            transitions=[
                "To understand this better,",
                "Here's why this matters:",
                "The key concept here is:",
                "Think of it this way:"
            ],
            closings=[
                "Does that make sense? Feel free to ask questions!",
                "I hope that clarifies things! 📚",
                "Let me know if you'd like more details on any part.",
                "Keep learning!"
            ]
        ),

        PersonalityType.COMMUNITY_MEMBER: PersonalityConfig(
            name="Community Member",
            description="Fellow community member sharing their experience",
            formality=0.2,
            enthusiasm=0.7,
            directness=0.6,
            emoji_frequency='moderate',
            sentence_length='medium',
            jargon_level='simple',
            focus='community',
            call_to_action_style='soft',
            greetings=[
                "Hey everyone!",
                "Just saw this and thought I'd chime in!",
                "Fellow creator here!",
                "I've been there!"
            ],
            transitions=[
                "What worked for me:",
                "In my experience:",
                "I found that",
                "One thing that helped me:"
            ],
            closings=[
                "Hope my experience helps!",
                "We're all in this together! 🙌",
                "Feel free to DM if you want to chat more!",
                "Good luck, friend!"
            ]
        )
    }

    @classmethod
    def get_personality(cls, personality_type: PersonalityType) -> PersonalityConfig:
        """Get a pre-configured personality"""
        return cls.PERSONALITIES[personality_type]

    @classmethod
    def list_personalities(cls) -> List[PersonalityConfig]:
        """List all available personalities"""
        return list(cls.PERSONALITIES.values())


class MessageGenerator:
    """Generates messages in specific personality"""

    def __init__(self, personality: PersonalityConfig):
        self.personality = personality

    def generate_message(self, content: str, include_cta: bool = True) -> str:
        """
        Generate a message in this personality.

        Args:
            content: Core message content
            include_cta: Include call-to-action

        Returns:
            Formatted message matching personality
        """
        import random

        # Select greeting
        greeting = random.choice(self.personality.greetings)

        # Format content based on sentence length
        if self.personality.sentence_length == 'short':
            # Break into shorter sentences
            sentences = content.split('. ')
            content = '. '.join(sentences)
        elif self.personality.sentence_length == 'long':
            # Combine related ideas
            pass  # Content already provided

        # Add emojis if appropriate
        if self.personality.emoji_frequency == 'frequent':
            content = self._add_emojis(content, frequency=0.3)
        elif self.personality.emoji_frequency == 'moderate':
            content = self._add_emojis(content, frequency=0.1)

        # Add closing
        closing = random.choice(self.personality.closings)

        # Assemble message
        parts = [greeting, content]

        if include_cta and self.personality.call_to_action_style != 'none':
            # Add CTA based on style
            cta = self._generate_cta()
            if cta:
                parts.append(cta)

        parts.append(closing)

        # Join with appropriate spacing
        message = "\n\n".join(parts)

        return message

    def _add_emojis(self, text: str, frequency: float = 0.2) -> str:
        """Add emojis to text based on frequency"""
        emoji_map = {
            'help': '💡',
            'great': '✨',
            'work': '🚀',
            'love': '💙',
            'protect': '🛡️',
            'create': '🎨',
            'learn': '📚',
            'win': '🎉'
        }

        import random

        words = text.split()
        for i, word in enumerate(words):
            word_lower = word.lower().strip(',.!?')
            if word_lower in emoji_map and random.random() < frequency:
                words[i] = f"{word} {emoji_map[word_lower]}"

        return ' '.join(words)

    def _generate_cta(self) -> str:
        """Generate call-to-action based on personality"""
        if self.personality.call_to_action_style == 'soft':
            ctas = [
                "If you're interested, you might want to check out BLOOM.",
                "BLOOM might be helpful for this - just a thought!",
                "I've heard good things about BLOOM for this use case."
            ]
        elif self.personality.call_to_action_style == 'medium':
            ctas = [
                "I'd recommend checking out BLOOM for this.",
                "BLOOM has helped a lot of people with exactly this issue.",
                "This is exactly what BLOOM was built for."
            ]
        elif self.personality.call_to_action_style == 'strong':
            ctas = [
                "Use BLOOM. It solves this problem directly.",
                "BLOOM handles this. Stop wasting time and check it out.",
                "This is literally what BLOOM does. Try it."
            ]
        else:
            return ""

        import random
        return random.choice(ctas)

    def adapt_to_platform(self, platform: str) -> 'MessageGenerator':
        """
        Adapt personality for specific platform.

        Different platforms have different norms!
        """
        adapted_personality = PersonalityConfig(
            name=self.personality.name,
            description=self.personality.description,
            formality=self.personality.formality,
            enthusiasm=self.personality.enthusiasm,
            directness=self.personality.directness,
            emoji_frequency=self.personality.emoji_frequency,
            sentence_length=self.personality.sentence_length,
            jargon_level=self.personality.jargon_level,
            focus=self.personality.focus,
            call_to_action_style=self.personality.call_to_action_style,
            greetings=self.personality.greetings.copy(),
            transitions=self.personality.transitions.copy(),
            closings=self.personality.closings.copy()
        )

        # Platform-specific adaptations
        if platform == 'discord':
            # Discord is casual and emoji-friendly
            if adapted_personality.formality > 0.5:
                adapted_personality.formality -= 0.2
            if adapted_personality.emoji_frequency == 'rare':
                adapted_personality.emoji_frequency = 'moderate'

        elif platform == 'slack':
            # Slack is professional
            if adapted_personality.formality < 0.5:
                adapted_personality.formality += 0.2
            if adapted_personality.emoji_frequency == 'frequent':
                adapted_personality.emoji_frequency = 'moderate'

        elif platform == 'twitter':
            # Twitter is concise
            adapted_personality.sentence_length = 'short'

        elif platform == 'reddit':
            # Reddit values authenticity and detail
            adapted_personality.sentence_length = 'long'
            adapted_personality.call_to_action_style = 'soft'

        return MessageGenerator(adapted_personality)


if __name__ == "__main__":
    # Demo the personality system
    print("=" * 80)
    print("AGENT PERSONALITY CUSTOMIZATION - DEMO".center(80))
    print("=" * 80)

    # Show all personalities
    print("\n1. AVAILABLE PERSONALITIES")
    print("-" * 80)

    for personality_type in PersonalityType:
        personality = PersonalityLibrary.get_personality(personality_type)
        print(f"\n{personality.name}:")
        print(f"  Description: {personality.description}")
        print(f"  Formality: {personality.formality:.1f}/1.0")
        print(f"  Enthusiasm: {personality.enthusiasm:.1f}/1.0")
        print(f"  Directness: {personality.directness:.1f}/1.0")
        print(f"  Emoji Use: {personality.emoji_frequency}")
        print(f"  Focus: {personality.focus}")

    # Generate sample messages
    print("\n2. SAMPLE MESSAGES (Same Content, Different Personalities)")
    print("-" * 80)

    content = "I noticed you mentioned IP theft concerns. Watermarking can help protect your creative work and track unauthorized use."

    for personality_type in PersonalityType:
        personality = PersonalityLibrary.get_personality(personality_type)
        generator = MessageGenerator(personality)
        message = generator.generate_message(content, include_cta=True)

        print(f"\n{personality.name.upper()}:")
        print("-" * 40)
        print(message)

    # Show platform adaptation
    print("\n3. PLATFORM ADAPTATION (Friendly Helper)")
    print("-" * 80)

    friendly = PersonalityLibrary.get_personality(PersonalityType.FRIENDLY_HELPER)
    base_generator = MessageGenerator(friendly)

    platforms = ['discord', 'slack', 'twitter', 'reddit']

    for platform in platforms:
        adapted = base_generator.adapt_to_platform(platform)
        message = adapted.generate_message(content, include_cta=False)

        print(f"\n{platform.upper()}:")
        print("-" * 40)
        print(message[:150] + "..." if len(message) > 150 else message)

    print("\n" + "=" * 80)
    print("KEY BENEFITS".center(80))
    print("=" * 80)
    print("""
1. BRAND ALIGNMENT
   - Agents speak in your brand voice
   - Consistent tone across all platforms
   - Customizable to match your style

2. PLATFORM OPTIMIZATION
   - Discord: Casual, emoji-friendly
   - Slack: Professional, business-focused
   - Twitter: Concise, engaging
   - Reddit: Detailed, authentic

3. AUDIENCE MATCHING
   - Friendly Helper: General consumers
   - Expert Consultant: B2B, enterprises
   - Straight-Shooter: Action-oriented audiences
   - Educator: Learning-focused communities

4. EASY CUSTOMIZATION
   - Choose from 5 pre-built personalities
   - Or create custom personality configs
   - Adapt automatically to platforms

RECOMMENDATION: Use Friendly Helper for Discord/Telegram,
                Expert Consultant for Slack/LinkedIn,
                Community Member for Reddit
    """)
    print("=" * 80)
