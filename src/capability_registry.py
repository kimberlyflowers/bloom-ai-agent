"""
CAPABILITY REGISTRY - Dynamic Discovery & Management System

Auto-discovers all of Sarah's capabilities at startup:
- Scans src/ for capability files
- Extracts callable methods
- Builds master registry with metadata
- Enables gradual activation (enabled flag)
- Provides intelligent capability selection

Usage:
    registry = CapabilityRegistry()
    await registry.initialize()

    # Query capabilities
    all_caps = registry.get_all_capabilities()
    enabled = registry.get_enabled_capabilities()
    by_category = registry.get_by_category('browser_interaction')

    # Get specific capability
    click_cap = registry.get_capability('universal_click')
"""

import os
import inspect
import importlib.util
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class Capability:
    """
    Represents a single capability Sarah can perform
    """
    name: str                    # Method name (e.g., "universal_click")
    display_name: str            # Human-readable (e.g., "Universal Click")
    description: str             # What it does
    category: str                # Category (browser_interaction, vision, learning, etc.)
    file_path: str               # Source file
    class_name: Optional[str]    # Class if it's a method, None if function
    enabled: bool                # Whether it's active
    deployed: bool               # Whether it's currently used in chat_server
    callable_ref: Optional[Callable]  # Reference to the actual function/method
    parameters: List[str]        # Required parameters
    returns: str                 # Return type description
    confidence_required: float   # Minimum confidence to use (0.0-1.0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict (excluding callable_ref for serialization)"""
        data = asdict(self)
        data.pop('callable_ref', None)  # Can't serialize functions
        return data


class CapabilityRegistry:
    """
    Auto-discovers and manages all of Sarah's capabilities

    Scans the codebase at startup to build a complete registry of:
    - Browser interactions (clicking, navigation, etc.)
    - Vision & analysis capabilities
    - Learning systems
    - Communication integrations (Twitter, Email, etc.)
    - Automation workflows
    - And more...

    Each capability has metadata (category, enabled status, etc.)
    """

    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.dirname(os.path.abspath(__file__))
        self.capabilities: Dict[str, Capability] = {}
        self.categories: Dict[str, List[str]] = {}  # category -> [capability_names]

        # Define which capabilities are currently deployed in chat_server
        self.deployed_capabilities = {
            'universal_click', 'navigate', 'search_google', 'screenshot',
            'click_by_description', 'universal_cookie_detector',
            'accessibility_click', 'stealth_click_button',
            'analyze_vision_context', 'parse_user_intent', 'plan_actions',
            'locate_element', 'verify_element_interaction',
            'click_element', 'execute_parallel',
            'get_relevant_patterns', 'extract_pattern_from_experience',
            'get_autonomous_response', 'start_autonomous_learning_session'
        }

    async def initialize(self):
        """
        Initialize the registry by scanning the codebase
        Call this at startup
        """
        logger.info("🔍 Initializing Capability Registry...")

        # Scan all capability files
        await self._scan_capabilities()

        # Build category index
        self._build_category_index()

        logger.info(f"✅ Registry initialized: {len(self.capabilities)} capabilities found")
        logger.info(f"   📊 Enabled: {len(self.get_enabled_capabilities())}")
        logger.info(f"   📊 Deployed: {len([c for c in self.capabilities.values() if c.deployed])}")
        logger.info(f"   📊 Available: {len([c for c in self.capabilities.values() if not c.enabled])}")

    async def _scan_capabilities(self):
        """Scan src/ directory for capability files and extract methods"""

        # Define capability file patterns
        capability_files = [
            # Core Browser & Interaction
            'sarah_browser.py',
            'sarah_improved_clicking.py',
            'sarah_ui_navigation.py',
            'advanced_browser_control.py',

            # Vision & AI
            'vision_action_reasoner.py',
            'visual_capabilities.py',
            'visual_learning.py',

            # Learning Systems
            'autonomous_learning_engine.py',
            'colony_learning.py',
            'learning_replay.py',
            'video_tutorial_learning.py',

            # Foundation
            'foundation/universal_element_locator.py',
            'foundation/universal_interactor.py',
            'foundation/parallel_execution_engine.py',

            # Communication (Available but not deployed)
            'email_integration.py',
            'twitter_integration.py',
            'slack_integration.py',
            'discord_integration.py',
            'telegram_integration.py',
            'reddit_integration.py',

            # Automation
            'autonomous_gmail_setup.py',
            'gmail_account_creator.py',
            'gohighlevel_automation.py',

            # Analytics
            'ai_insights.py',
            'performance_analytics.py',
            'ab_testing.py',
        ]

        for file_name in capability_files:
            file_path = os.path.join(self.base_path, file_name)
            if os.path.exists(file_path):
                await self._extract_capabilities_from_file(file_path, file_name)
            else:
                logger.debug(f"⚠️ File not found: {file_name}")

    async def _extract_capabilities_from_file(self, file_path: str, file_name: str):
        """Extract capabilities (async methods) from a Python file"""
        try:
            # Import the module
            spec = importlib.util.spec_from_file_location("temp_module", file_path)
            if not spec or not spec.loader:
                return

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Determine category from file name
            category = self._determine_category(file_name)

            # Extract classes and their methods
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj):
                    # Extract methods from class
                    for method_name, method in inspect.getmembers(obj):
                        if self._is_capability_method(method_name, method):
                            capability = self._create_capability(
                                method_name, method, category, file_name,
                                class_name=name
                            )
                            self.capabilities[capability.name] = capability

                elif inspect.isfunction(obj):
                    # Standalone async function
                    if self._is_capability_method(name, obj):
                        capability = self._create_capability(
                            name, obj, category, file_name
                        )
                        self.capabilities[capability.name] = capability

        except Exception as e:
            logger.warning(f"⚠️ Could not extract from {file_name}: {e}")

    def _is_capability_method(self, name: str, obj: Any) -> bool:
        """Determine if a method/function is a capability"""
        # Skip private methods
        if name.startswith('_'):
            return False

        # Must be async or callable
        if not (inspect.iscoroutinefunction(obj) or callable(obj)):
            return False

        # Skip common non-capability methods
        skip_methods = {'__init__', '__str__', '__repr__', 'close', 'cleanup'}
        if name in skip_methods:
            return False

        return True

    def _create_capability(
        self,
        method_name: str,
        method: Callable,
        category: str,
        file_name: str,
        class_name: Optional[str] = None
    ) -> Capability:
        """Create a Capability object from a method"""

        # Extract parameters
        sig = inspect.signature(method)
        parameters = [
            param.name for param in sig.parameters.values()
            if param.name not in ['self', 'cls']
        ]

        # Get docstring
        doc = inspect.getdoc(method) or "No description available"
        description = doc.split('\n')[0][:200]  # First line, max 200 chars

        # Determine if deployed
        deployed = method_name in self.deployed_capabilities

        # Create display name
        display_name = method_name.replace('_', ' ').title()

        # Determine enabled status
        # Start with deployed capabilities enabled, others disabled
        enabled = deployed

        # Determine confidence threshold based on category
        confidence_map = {
            'browser_interaction': 0.7,
            'vision_analysis': 0.8,
            'learning': 0.6,
            'communication': 0.9,  # Higher threshold for external comms
            'automation': 0.85,
        }
        confidence_required = confidence_map.get(category, 0.7)

        return Capability(
            name=method_name,
            display_name=display_name,
            description=description,
            category=category,
            file_path=file_name,
            class_name=class_name,
            enabled=enabled,
            deployed=deployed,
            callable_ref=method,
            parameters=parameters,
            returns="Dict[str, Any]",  # Most return dicts
            confidence_required=confidence_required
        )

    def _determine_category(self, file_name: str) -> str:
        """Determine capability category from file name"""
        category_map = {
            'sarah_browser': 'browser_interaction',
            'sarah_improved_clicking': 'browser_interaction',
            'sarah_ui_navigation': 'browser_interaction',
            'advanced_browser_control': 'browser_interaction',

            'vision_action_reasoner': 'vision_analysis',
            'visual_capabilities': 'vision_analysis',
            'visual_learning': 'learning',

            'autonomous_learning': 'learning',
            'colony_learning': 'learning',
            'learning_replay': 'learning',
            'video_tutorial': 'learning',

            'universal_element_locator': 'element_location',
            'universal_interactor': 'element_interaction',
            'parallel_execution': 'execution_engine',

            'email': 'communication',
            'twitter': 'communication',
            'slack': 'communication',
            'discord': 'communication',
            'telegram': 'communication',
            'reddit': 'communication',

            'gmail': 'automation',
            'gohighlevel': 'automation',

            'insights': 'analytics',
            'performance': 'analytics',
            'ab_testing': 'analytics',
        }

        for key, category in category_map.items():
            if key in file_name.lower():
                return category

        return 'other'

    def _build_category_index(self):
        """Build index of capabilities by category"""
        self.categories = {}
        for cap_name, cap in self.capabilities.items():
            if cap.category not in self.categories:
                self.categories[cap.category] = []
            self.categories[cap.category].append(cap_name)

    # ===== QUERY METHODS =====

    def get_all_capabilities(self) -> List[Capability]:
        """Get all registered capabilities"""
        return list(self.capabilities.values())

    def get_enabled_capabilities(self) -> List[Capability]:
        """Get only enabled capabilities"""
        return [cap for cap in self.capabilities.values() if cap.enabled]

    def get_deployed_capabilities(self) -> List[Capability]:
        """Get capabilities currently deployed in chat_server"""
        return [cap for cap in self.capabilities.values() if cap.deployed]

    def get_available_capabilities(self) -> List[Capability]:
        """Get capabilities available but not enabled"""
        return [cap for cap in self.capabilities.values() if not cap.enabled]

    def get_by_category(self, category: str) -> List[Capability]:
        """Get all capabilities in a category"""
        cap_names = self.categories.get(category, [])
        return [self.capabilities[name] for name in cap_names]

    def get_capability(self, name: str) -> Optional[Capability]:
        """Get a specific capability by name"""
        return self.capabilities.get(name)

    def search_capabilities(self, query: str) -> List[Capability]:
        """Search capabilities by name or description"""
        query_lower = query.lower()
        results = []
        for cap in self.capabilities.values():
            if (query_lower in cap.name.lower() or
                query_lower in cap.description.lower() or
                query_lower in cap.display_name.lower()):
                results.append(cap)
        return results

    # ===== MANAGEMENT METHODS =====

    def enable_capability(self, name: str) -> bool:
        """Enable a capability"""
        cap = self.capabilities.get(name)
        if cap:
            cap.enabled = True
            logger.info(f"✅ Enabled capability: {name}")
            return True
        return False

    def disable_capability(self, name: str) -> bool:
        """Disable a capability"""
        cap = self.capabilities.get(name)
        if cap:
            cap.enabled = False
            logger.info(f"⏸️ Disabled capability: {name}")
            return True
        return False

    def enable_category(self, category: str) -> int:
        """Enable all capabilities in a category"""
        count = 0
        for cap_name in self.categories.get(category, []):
            if self.enable_capability(cap_name):
                count += 1
        logger.info(f"✅ Enabled {count} capabilities in category '{category}'")
        return count

    # ===== STATS & REPORTING =====

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            'total_capabilities': len(self.capabilities),
            'enabled': len(self.get_enabled_capabilities()),
            'deployed': len([c for c in self.capabilities.values() if c.deployed]),
            'available': len(self.get_available_capabilities()),
            'categories': {
                cat: len(names) for cat, names in self.categories.items()
            }
        }

    def print_summary(self):
        """Print a summary of the registry"""
        stats = self.get_stats()

        print("\n" + "="*60)
        print("📊 CAPABILITY REGISTRY SUMMARY")
        print("="*60)
        print(f"Total Capabilities: {stats['total_capabilities']}")
        print(f"✅ Enabled: {stats['enabled']}")
        print(f"🚀 Deployed: {stats['deployed']}")
        print(f"💤 Available: {stats['available']}")
        print("\nBy Category:")
        for category, count in sorted(stats['categories'].items()):
            print(f"  {category}: {count}")
        print("="*60 + "\n")

    def export_registry(self) -> Dict[str, Any]:
        """Export registry to dict (for saving/loading)"""
        return {
            'capabilities': {
                name: cap.to_dict()
                for name, cap in self.capabilities.items()
            },
            'stats': self.get_stats()
        }


# ===== SINGLETON INSTANCE =====

_registry_instance: Optional[CapabilityRegistry] = None


async def get_registry() -> CapabilityRegistry:
    """Get or create the global registry instance"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = CapabilityRegistry()
        await _registry_instance.initialize()
    return _registry_instance


# ===== DEMO/TEST =====

async def demo():
    """Demo the capability registry"""
    registry = await get_registry()

    # Print summary
    registry.print_summary()

    # Show enabled capabilities
    print("\n✅ ENABLED CAPABILITIES:")
    for cap in registry.get_enabled_capabilities()[:10]:  # First 10
        print(f"  - {cap.display_name} ({cap.category})")
        print(f"    {cap.description[:80]}...")

    # Show available but not enabled
    print("\n💤 AVAILABLE CAPABILITIES (Not Enabled):")
    for cap in registry.get_available_capabilities()[:5]:  # First 5
        print(f"  - {cap.display_name} ({cap.category})")
        print(f"    {cap.description[:80]}...")

    # Search example
    print("\n🔍 SEARCH RESULTS for 'click':")
    results = registry.search_capabilities('click')
    for cap in results[:5]:
        print(f"  - {cap.display_name} (enabled: {cap.enabled})")

    # Category example
    print("\n📂 BROWSER INTERACTION CAPABILITIES:")
    browser_caps = registry.get_by_category('browser_interaction')
    for cap in browser_caps[:5]:
        print(f"  - {cap.display_name} (enabled: {cap.enabled})")


if __name__ == "__main__":
    asyncio.run(demo())
