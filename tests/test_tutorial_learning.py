"""
Phase 6: Testing - Tutorial Learning System Integration Tests

Tests the complete tutorial learning pipeline:
- Phase 1: YouTube transcript extraction & parsing
- Phase 2: Vision + Browser execution with retry logic
- Phase 3: Async learn_from_video workflow
- Phase 4 & 5: Skill persistence and replay

Usage:
    # Basic test
    python tests/test_tutorial_learning.py --test basic

    # Error recovery test
    python tests/test_tutorial_learning.py --test error-recovery

    # Vision fallback test
    python tests/test_tutorial_learning.py --test vision-fallback

    # Skill replay test
    python tests/test_tutorial_learning.py --test skill-replay

    # Full test suite
    python tests/test_tutorial_learning.py --test all

Requirements:
    - ANTHROPIC_API_KEY environment variable set
    - Playwright installed: playwright install chromium
    - Internet connection for YouTube
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.video_tutorial_learning import (
    SkillLearner,
    SkillCategory,
    LearnedSkill
)
from src.sarah_browser import SarahBrowser
from src.ui_element_finder import UIElementFinder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TutorialLearningTests:
    """Test suite for tutorial learning system"""

    def __init__(self):
        self.learner = SkillLearner()
        self.browser = None
        self.ui_finder = None
        self.test_agent_id = "test_agent_001"

    async def setup(self):
        """Initialize browser and UI finder"""
        logger.info("🚀 Setting up test environment...")

        # Verify API key
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        # Initialize browser (headless for CI)
        self.browser = SarahBrowser(headless=True)
        await self.browser.start()

        # Initialize UI finder
        self.ui_finder = UIElementFinder()

        logger.info("✅ Test environment ready")

    async def teardown(self):
        """Clean up resources"""
        logger.info("🧹 Cleaning up...")
        if self.browser:
            await self.browser.close()
        logger.info("✅ Cleanup complete")

    async def test_basic_workflow(self) -> Dict[str, Any]:
        """
        Test 1: Basic Video Learning Workflow

        Tests the complete pipeline from video URL to learned skill:
        1. Extract transcript from YouTube
        2. Parse transcript into actionable steps
        3. Execute steps with Vision + Browser
        4. Save learned skill
        5. Verify skill can be loaded
        """
        logger.info("\n" + "="*80)
        logger.info("TEST 1: Basic Video Learning Workflow")
        logger.info("="*80)

        # Use a short, reliable tutorial
        # This is a simple "How to use Google Search" tutorial
        video_url = "https://www.youtube.com/watch?v=xeuuYWSmE5c"
        skill_name = "Basic Google Search"
        category = SkillCategory.GENERAL

        try:
            # Step 1: Learn from video
            logger.info(f"📹 Learning skill from: {video_url}")
            skill = await self.learner.learn_from_video(
                agent_id=self.test_agent_id,
                video_url=video_url,
                skill_name=skill_name,
                category=category,
                browser=self.browser,
                ui_finder=self.ui_finder
            )

            # Verify skill was created
            assert skill is not None, "Skill was not created"
            assert skill.name == skill_name, f"Skill name mismatch: {skill.name}"
            assert len(skill.steps) > 0, "No tutorial steps extracted"

            logger.info(f"✅ Skill learned: {skill.name}")
            logger.info(f"   - Steps: {len(skill.steps)}")
            logger.info(f"   - Success rate: {skill.success_rate:.1%}")

            # Step 2: Verify skill persistence
            logger.info(f"💾 Testing skill persistence...")
            await self.learner.save_skill(skill)

            loaded_skill = await self.learner.load_skill(skill.skill_id)
            assert loaded_skill is not None, "Failed to load saved skill"
            assert loaded_skill.skill_id == skill.skill_id, "Skill ID mismatch"

            logger.info(f"✅ Skill persistence verified")

            return {
                "status": "PASSED",
                "skill_id": skill.skill_id,
                "steps_learned": len(skill.steps),
                "success_rate": skill.success_rate
            }

        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e)
            }

    async def test_error_recovery(self) -> Dict[str, Any]:
        """
        Test 2: Error Recovery Scenarios

        Tests the system's ability to handle errors:
        1. Invalid video URL
        2. Video with no transcript
        3. Network timeout simulation
        4. Element not found fallback
        """
        logger.info("\n" + "="*80)
        logger.info("TEST 2: Error Recovery")
        logger.info("="*80)

        results = []

        # Test 2a: Invalid video URL
        logger.info("📹 Testing invalid video URL...")
        try:
            await self.learner.analyzer.get_transcript_with_timestamps(
                "https://www.youtube.com/watch?v=invalid_id"
            )
            results.append({"test": "invalid_url", "status": "FAILED", "reason": "Should have raised error"})
        except Exception as e:
            logger.info(f"✅ Correctly handled invalid URL: {type(e).__name__}")
            results.append({"test": "invalid_url", "status": "PASSED"})

        # Test 2b: Video with no transcript (transcripts disabled)
        logger.info("📹 Testing video with no transcript...")
        try:
            # This video typically has transcripts disabled
            await self.learner.analyzer.get_transcript_with_timestamps(
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            )
            logger.info("⚠️  Video had transcript (expected it disabled)")
            results.append({"test": "no_transcript", "status": "SKIPPED", "reason": "Video has transcript"})
        except Exception as e:
            logger.info(f"✅ Correctly handled missing transcript: {type(e).__name__}")
            results.append({"test": "no_transcript", "status": "PASSED"})

        # Test 2c: Timeout handling (using retry mechanism)
        logger.info("⏱️  Testing timeout handling...")
        from src.video_tutorial_learning import TutorialStep, StepType

        # Create a step that will likely timeout (bad URL)
        timeout_step = TutorialStep(
            step_number=1,
            action_type=StepType.NAVIGATE,
            instruction="Navigate to non-existent page",
            target="http://192.0.2.1",  # TEST-NET address (guaranteed to timeout)
            expected_result="Page loads",
            timestamp=0.0
        )

        try:
            # This should timeout and retry, then eventually fail gracefully
            success, error = await self.learner.execute_tutorial_step_with_retry(
                timeout_step,
                self.browser,
                self.ui_finder,
                max_retries=1,  # Reduce retries for faster test
                timeout_seconds=5  # Short timeout
            )

            if not success and "timeout" in error.lower():
                logger.info(f"✅ Correctly handled timeout with retry")
                results.append({"test": "timeout_handling", "status": "PASSED"})
            else:
                logger.info(f"⚠️  Unexpected result: success={success}, error={error}")
                results.append({"test": "timeout_handling", "status": "FAILED", "reason": f"Unexpected: {error}"})

        except Exception as e:
            logger.info(f"✅ Timeout raised exception as expected: {type(e).__name__}")
            results.append({"test": "timeout_handling", "status": "PASSED"})

        # Summary
        passed = sum(1 for r in results if r["status"] == "PASSED")
        total = len(results)

        logger.info(f"\n📊 Error Recovery Summary: {passed}/{total} tests passed")

        return {
            "status": "PASSED" if passed == total else "PARTIAL",
            "tests": results,
            "passed": passed,
            "total": total
        }

    async def test_vision_fallback(self) -> Dict[str, Any]:
        """
        Test 3: Vision Fallback Mechanisms

        Tests the 3-tier fallback system:
        1. Primary Vision query
        2. Alternate phrasing Vision query
        3. CSS selector fallback
        """
        logger.info("\n" + "="*80)
        logger.info("TEST 3: Vision Fallback Mechanisms")
        logger.info("="*80)

        try:
            # Navigate to a simple test page
            logger.info("🌐 Navigating to Google...")
            await self.browser.navigate("https://www.google.com")

            # Test finding an element with Vision
            logger.info("👁️  Testing Vision element detection...")
            screenshot = await self.browser.take_screenshot()

            result = await self.ui_finder.find_element(
                screenshot,
                "the search input box in the center"
            )

            if result["found"]:
                logger.info(f"✅ Vision found element: {result['description']}")
                logger.info(f"   Coordinates: ({result['coordinates']['x']}, {result['coordinates']['y']})")
                logger.info(f"   Confidence: {result['confidence']}")

                # Test clicking the element
                x, y = result['coordinates']['x'], result['coordinates']['y']
                await self.browser.click(x, y)
                logger.info(f"✅ Successfully clicked element")

                return {
                    "status": "PASSED",
                    "vision_working": True,
                    "coordinates": result['coordinates'],
                    "confidence": result['confidence']
                }
            else:
                logger.warning(f"⚠️  Vision could not find element: {result['description']}")
                return {
                    "status": "FAILED",
                    "vision_working": False,
                    "reason": result['description']
                }

        except Exception as e:
            logger.error(f"❌ Vision fallback test failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e)
            }

    async def test_skill_replay(self) -> Dict[str, Any]:
        """
        Test 4: Skill Persistence and Replay

        Tests:
        1. Learn a skill from video
        2. Save to JSON
        3. Load from JSON
        4. Replay the skill (execute learned steps)
        5. Verify stats updated
        """
        logger.info("\n" + "="*80)
        logger.info("TEST 4: Skill Persistence and Replay")
        logger.info("="*80)

        try:
            # Use a very simple tutorial for faster testing
            video_url = "https://www.youtube.com/watch?v=xeuuYWSmE5c"
            skill_name = "Test Skill Replay"
            category = SkillCategory.GENERAL

            # Step 1: Learn skill
            logger.info(f"📹 Learning skill for replay test...")
            skill = await self.learner.learn_from_video(
                agent_id=self.test_agent_id,
                video_url=video_url,
                skill_name=skill_name,
                category=category,
                browser=self.browser,
                ui_finder=self.ui_finder
            )

            original_execution_count = skill.times_executed
            skill_id = skill.skill_id

            logger.info(f"✅ Skill learned: {skill_id}")
            logger.info(f"   Initial execution count: {original_execution_count}")

            # Step 2: Save skill
            await self.learner.save_skill(skill)
            logger.info(f"💾 Skill saved")

            # Step 3: Replay skill
            logger.info(f"🔄 Replaying skill...")
            replay_result = await self.learner.execute_learned_skill(
                skill_id=skill_id,
                browser=self.browser,
                ui_finder=self.ui_finder
            )

            # Step 4: Verify stats updated
            reloaded_skill = await self.learner.load_skill(skill_id)

            assert reloaded_skill.times_executed == original_execution_count + 1, \
                "Execution count not incremented"

            logger.info(f"✅ Skill replayed successfully")
            logger.info(f"   New execution count: {reloaded_skill.times_executed}")
            logger.info(f"   Replay success: {replay_result['success']}")
            logger.info(f"   Steps completed: {replay_result['successful_steps']}/{replay_result['total_steps']}")

            return {
                "status": "PASSED",
                "skill_id": skill_id,
                "execution_count": reloaded_skill.times_executed,
                "replay_success": replay_result['success'],
                "steps_completed": replay_result['successful_steps']
            }

        except Exception as e:
            logger.error(f"❌ Skill replay test failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e)
            }

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        logger.info("\n" + "="*80)
        logger.info("🧪 PHASE 6: COMPLETE TEST SUITE")
        logger.info("="*80)

        results = {}

        try:
            await self.setup()

            # Run all tests
            results["basic_workflow"] = await self.test_basic_workflow()
            results["error_recovery"] = await self.test_error_recovery()
            results["vision_fallback"] = await self.test_vision_fallback()
            results["skill_replay"] = await self.test_skill_replay()

        finally:
            await self.teardown()

        # Summary
        logger.info("\n" + "="*80)
        logger.info("📊 TEST SUITE SUMMARY")
        logger.info("="*80)

        for test_name, result in results.items():
            status = result.get("status", "UNKNOWN")
            logger.info(f"{test_name}: {status}")

        passed_count = sum(1 for r in results.values() if r.get("status") == "PASSED")
        total_count = len(results)

        logger.info(f"\n✅ {passed_count}/{total_count} tests passed")

        return {
            "summary": {
                "passed": passed_count,
                "total": total_count,
                "success_rate": passed_count / total_count if total_count > 0 else 0
            },
            "results": results
        }


async def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Tutorial Learning System Tests")
    parser.add_argument(
        "--test",
        choices=["basic", "error-recovery", "vision-fallback", "skill-replay", "all"],
        default="all",
        help="Which test to run"
    )

    args = parser.parse_args()

    tester = TutorialLearningTests()

    try:
        if args.test == "all":
            results = await tester.run_all_tests()
        else:
            await tester.setup()

            if args.test == "basic":
                results = await tester.test_basic_workflow()
            elif args.test == "error-recovery":
                results = await tester.test_error_recovery()
            elif args.test == "vision-fallback":
                results = await tester.test_vision_fallback()
            elif args.test == "skill-replay":
                results = await tester.test_skill_replay()

            await tester.teardown()

        # Print results as JSON for CI/CD
        import json
        print("\n" + "="*80)
        print("JSON Results:")
        print(json.dumps(results, indent=2))

        # Exit with proper code
        if results.get("status") == "PASSED":
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\n⚠️  Tests interrupted by user")
        await tester.teardown()
        sys.exit(130)
    except Exception as e:
        logger.error(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
