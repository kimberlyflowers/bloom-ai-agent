"""
INTELLIGENT SELECTOR - Dynamic Capability Routing

Enables Sarah's LLM to see available capabilities and intelligently choose
the right one based on user intent.

Replaces hardcoded routing (if intent == 'navigate') with dynamic selection.

Usage:
    selector = IntelligentSelector(capability_registry, anthropic_api_key)
    result = await selector.select_capability(user_message, context)

    if result['success']:
        capability = result['capability']
        # Execute the selected capability
"""

import logging
import json
import asyncio
from typing import Dict, Any, Optional, List
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class IntelligentSelector:
    """
    LLM-powered capability selector that routes user intent to the right capability

    Core Principle: Dynamic selection over hardcoded routing
    - User says "tweet this" → Selects twitter_integration capability
    - User says "search for videos" → Selects universal_click + navigate
    - User says "learn how to do X" → Selects autonomous_learning_engine
    """

    def __init__(self, capability_registry, anthropic_api_key: str):
        """
        Args:
            capability_registry: CapabilityRegistry instance with all available capabilities
            anthropic_api_key: Anthropic API key for LLM calls
        """
        self.registry = capability_registry
        self.anthropic = Anthropic(api_key=anthropic_api_key)

    async def select_capability(
        self,
        user_message: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Select the best capability to handle user's intent

        Args:
            user_message: What the user wants Sarah to do
            context: Optional context (current_url, screenshot, previous_action, etc.)

        Returns:
            {
                'success': bool,
                'capability': Capability object,
                'reasoning': str,
                'confidence': float,
                'parameters': dict,  # Suggested parameters for the capability
                'alternative_capabilities': List[Capability]  # Backup options
            }
        """
        try:
            context = context or {}

            logger.info(f"🧠 Intelligent Selector: Analyzing user intent...")
            logger.info(f"   💬 Message: {user_message[:100]}")

            # Get enabled capabilities from registry
            enabled_capabilities = self.registry.get_enabled_capabilities()

            if not enabled_capabilities:
                logger.warning("⚠️ No enabled capabilities found in registry")
                return {
                    'success': False,
                    'reasoning': 'No capabilities available',
                    'confidence': 0.0
                }

            # Build capability catalog for LLM
            capability_catalog = self._build_capability_catalog(enabled_capabilities)

            # Call LLM to select best capability
            response = await asyncio.to_thread(
                self.anthropic.messages.create,
                model="claude-sonnet-4-5-20250929",  # Claude Sonnet 4.5 (Sep 2025)
                max_tokens=1000,
                temperature=0,  # Deterministic for capability selection
                messages=[{
                    'role': 'user',
                    'content': self._build_selection_prompt(
                        user_message,
                        capability_catalog,
                        context
                    )
                }]
            )

            # Parse LLM response
            response_text = response.content[0].text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
            response_text = response_text.strip()

            result = json.loads(response_text)

            # Validate and enrich result
            if result.get('success') and result.get('capability_name'):
                capability = self.registry.get_capability(result['capability_name'])

                if capability:
                    # Check if confidence meets threshold
                    confidence = result.get('confidence', 0.0)

                    if confidence < capability.confidence_required:
                        logger.warning(
                            f"⚠️ Confidence {confidence:.2f} below required "
                            f"{capability.confidence_required:.2f} for {capability.name}"
                        )
                        return {
                            'success': False,
                            'reasoning': f"Confidence too low (need {capability.confidence_required:.2f})",
                            'confidence': confidence
                        }

                    # Get alternative capabilities
                    alternatives = []
                    for alt_name in result.get('alternatives', []):
                        alt_cap = self.registry.get_capability(alt_name)
                        if alt_cap:
                            alternatives.append(alt_cap)

                    logger.info(f"✅ Selected: {capability.display_name} ({capability.category})")
                    logger.info(f"   🎯 Confidence: {confidence:.2f}")
                    logger.info(f"   💡 Reasoning: {result.get('reasoning', '')[:100]}")

                    return {
                        'success': True,
                        'capability': capability,
                        'reasoning': result.get('reasoning', ''),
                        'confidence': confidence,
                        'parameters': result.get('parameters', {}),
                        'alternative_capabilities': alternatives
                    }
                else:
                    logger.error(f"❌ Selected capability '{result['capability_name']}' not found in registry")
                    return {
                        'success': False,
                        'reasoning': f"Capability {result['capability_name']} not found",
                        'confidence': 0.0
                    }
            else:
                logger.warning(f"❌ No suitable capability found: {result.get('reasoning')}")
                return {
                    'success': False,
                    'reasoning': result.get('reasoning', 'No capability matched'),
                    'confidence': 0.0
                }

        except Exception as e:
            logger.error(f"❌ Intelligent Selector error: {e}")
            return {
                'success': False,
                'reasoning': f"Selection error: {str(e)}",
                'confidence': 0.0
            }

    def _build_capability_catalog(self, capabilities: List) -> str:
        """Build a structured catalog of capabilities for the LLM"""
        catalog_lines = []

        # Group by category
        by_category = {}
        for cap in capabilities:
            if cap.category not in by_category:
                by_category[cap.category] = []
            by_category[cap.category].append(cap)

        # Format catalog
        for category, caps in sorted(by_category.items()):
            catalog_lines.append(f"\n**{category.upper().replace('_', ' ')}:**")
            for cap in caps:
                catalog_lines.append(
                    f"  - `{cap.name}`: {cap.description[:150]}"
                )
                if cap.parameters:
                    catalog_lines.append(f"    Parameters: {', '.join(cap.parameters[:5])}")

        return '\n'.join(catalog_lines)

    def _build_selection_prompt(
        self,
        user_message: str,
        capability_catalog: str,
        context: Dict[str, Any]
    ) -> str:
        """Build the prompt for capability selection"""

        current_url = context.get('current_url', 'Unknown')
        previous_action = context.get('previous_action', 'None')

        return f"""You are Sarah's Intelligent Capability Selector. Your job is to analyze user intent and select the BEST capability to handle their request.

**USER MESSAGE:** {user_message}

**CURRENT CONTEXT:**
- URL: {current_url}
- Previous action: {previous_action}

**AVAILABLE CAPABILITIES:**
{capability_catalog}

**YOUR TASK:**
Analyze the user's intent and select the SINGLE BEST capability to handle this request.

**SELECTION CRITERIA:**
1. **Semantic Match**: Does the capability's purpose match user intent?
2. **Context Fit**: Is this capability appropriate for current context (URL, page state)?
3. **Confidence**: How certain are you this is the right capability? (0.0-1.0)
4. **Parameters**: What parameters should be passed to this capability?

**EXAMPLES:**

User: "Search for cat videos"
→ Select: `universal_click` with parameters {{"description": "search box"}}
→ Reasoning: Need to click search box first, then we can search

User: "Tweet this screenshot"
→ Select: `send_tweet` with parameters {{"text": "...", "image": "..."}}
→ Reasoning: Direct Twitter posting capability, user wants to tweet

User: "Navigate to YouTube"
→ Select: `navigate` with parameters {{"url": "youtube.com"}}
→ Reasoning: Clear navigation intent

User: "What should I learn next?"
→ Select: `get_autonomous_response` with parameters {{"question": "what should I learn next?"}}
→ Reasoning: Autonomous learning query, needs learning engine

User: "Click the video about dogs"
→ Select: `universal_click` with parameters {{"description": "video about dogs"}}
→ Reasoning: Specific click target identified

**IMPORTANT RULES:**
- If user wants to GO somewhere → select `navigate`
- If user wants to CLICK something → select `universal_click` or `click_by_description`
- If user wants to SEARCH → select `universal_click` (to click search box) or `search_google`
- If user asks LEARNING questions → select `get_autonomous_response` or `start_autonomous_learning_session`
- If user wants COMMUNICATION → select appropriate integration (send_tweet, send_email, etc.)
- If UNSURE → select the safest/most general capability with lower confidence

**RETURN FORMAT (JSON only):**
{{
    "success": true,
    "capability_name": "universal_click",
    "reasoning": "User wants to click a specific element, universal_click is the best choice",
    "confidence": 0.9,
    "parameters": {{
        "description": "search box"
    }},
    "alternatives": ["click_by_description", "search_google"]
}}

If NO capability matches:
{{
    "success": false,
    "reasoning": "No capability can handle weather queries yet",
    "confidence": 0.0
}}

**ANALYZE THE USER MESSAGE AND SELECT:**"""

    async def select_multiple_capabilities(
        self,
        user_message: str,
        context: Dict[str, Any] = None,
        max_capabilities: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Select multiple capabilities for complex multi-step tasks

        Example:
            User: "Go to YouTube and search for cat videos"
            → Returns: [navigate, universal_click]
        """
        try:
            logger.info(f"🧠 Intelligent Selector: Finding {max_capabilities} capabilities for multi-step task")

            context = context or {}
            enabled_capabilities = self.registry.get_enabled_capabilities()
            capability_catalog = self._build_capability_catalog(enabled_capabilities)

            response = await asyncio.to_thread(
                self.anthropic.messages.create,
                model="claude-sonnet-4-5-20250929",  # Claude Sonnet 4.5 (Sep 2025)
                max_tokens=1500,
                temperature=0,
                messages=[{
                    'role': 'user',
                    'content': f"""Select UP TO {max_capabilities} capabilities to handle this multi-step request.

**USER MESSAGE:** {user_message}

**AVAILABLE CAPABILITIES:**
{capability_catalog}

Return JSON array with ordered steps:
[
    {{
        "step": 1,
        "capability_name": "navigate",
        "reasoning": "First go to YouTube",
        "confidence": 0.95,
        "parameters": {{"url": "youtube.com"}}
    }},
    {{
        "step": 2,
        "capability_name": "universal_click",
        "reasoning": "Then click search box",
        "confidence": 0.85,
        "parameters": {{"description": "search box"}}
    }}
]

If single-step task, return array with one item.
"""
                }]
            )

            response_text = response.content[0].text.strip()
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
            response_text = response_text.strip()

            steps = json.loads(response_text)

            # Enrich with capability objects
            results = []
            for step in steps:
                capability = self.registry.get_capability(step.get('capability_name'))
                if capability:
                    results.append({
                        'success': True,
                        'step': step.get('step'),
                        'capability': capability,
                        'reasoning': step.get('reasoning', ''),
                        'confidence': step.get('confidence', 0.0),
                        'parameters': step.get('parameters', {})
                    })

            logger.info(f"✅ Selected {len(results)} capabilities for multi-step task")
            return results

        except Exception as e:
            logger.error(f"❌ Multi-capability selection error: {e}")
            return []

    def get_capability_by_category(self, category: str) -> List:
        """Get all enabled capabilities in a category"""
        all_caps = self.registry.get_by_category(category)
        return [cap for cap in all_caps if cap.enabled]


# ===== DEMO/TEST =====

async def demo():
    """Demo the intelligent selector"""
    from src.capability_registry import get_registry
    import os

    # Get registry
    registry = await get_registry()

    # Create selector
    api_key = os.getenv('ANTHROPIC_API_KEY')
    selector = IntelligentSelector(registry, api_key)

    # Test cases
    test_cases = [
        "Search for cat videos",
        "Go to YouTube",
        "Click the video about cooking",
        "What should I learn next?",
        "Tweet this screenshot",
        "Navigate to reddit.com and search for funny memes"
    ]

    print("\n" + "="*60)
    print("🧠 INTELLIGENT SELECTOR DEMO")
    print("="*60)

    for test_message in test_cases:
        print(f"\n📝 User: {test_message}")

        result = await selector.select_capability(test_message)

        if result['success']:
            cap = result['capability']
            print(f"✅ Selected: {cap.display_name} ({cap.category})")
            print(f"   🎯 Confidence: {result['confidence']:.2f}")
            print(f"   💡 Reasoning: {result['reasoning'][:100]}")
            if result.get('parameters'):
                print(f"   📋 Parameters: {result['parameters']}")
        else:
            print(f"❌ No capability found: {result['reasoning']}")

    # Test multi-step
    print("\n" + "="*60)
    print("🔢 MULTI-STEP SELECTION TEST")
    print("="*60)

    multi_test = "Go to YouTube and search for cat videos"
    print(f"\n📝 User: {multi_test}")

    results = await selector.select_multiple_capabilities(multi_test)

    for result in results:
        print(f"\nStep {result['step']}: {result['capability'].display_name}")
        print(f"   💡 {result['reasoning']}")
        print(f"   📋 {result['parameters']}")


if __name__ == "__main__":
    asyncio.run(demo())
