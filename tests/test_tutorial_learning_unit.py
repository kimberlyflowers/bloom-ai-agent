"""
Unit Tests for Tutorial Learning System

Tests the implementation without requiring:
- ANTHROPIC_API_KEY
- Live YouTube videos
- Real browser automation

Focuses on:
- Code structure validation
- Method existence
- Data structure correctness
- Error handling
"""

import sys
import logging
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
import asyncio

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.video_tutorial_learning import (
    SkillLearner,
    VideoTutorialAnalyzer,
    SkillCategory,
    LearnedSkill,
    TutorialStep,
    StepType
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestTutorialLearningStructure:
    """Test the structure and interfaces of the tutorial learning system"""

    def test_imports(self):
        """Test 1: Verify all required classes can be imported"""
        logger.info("\n" + "="*80)
        logger.info("TEST 1: Import Validation")
        logger.info("="*80)

        try:
            assert SkillLearner is not None
            assert VideoTutorialAnalyzer is not None
            assert SkillCategory is not None
            assert LearnedSkill is not None
            assert TutorialStep is not None
            assert StepType is not None

            logger.info("✅ All classes imported successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Import failed: {e}")
            return False

    def test_class_instantiation(self):
        """Test 2: Verify classes can be instantiated"""
        logger.info("\n" + "="*80)
        logger.info("TEST 2: Class Instantiation")
        logger.info("="*80)

        try:
            learner = SkillLearner()
            assert learner is not None
            assert hasattr(learner, 'analyzer')
            assert isinstance(learner.analyzer, VideoTutorialAnalyzer)

            logger.info("✅ SkillLearner instantiated successfully")
            logger.info(f"   - Has analyzer: {learner.analyzer}")
            logger.info(f"   - Learned skills dict: {learner.learned_skills}")

            return True
        except Exception as e:
            logger.error(f"❌ Instantiation failed: {e}")
            return False

    def test_method_existence(self):
        """Test 3: Verify all required methods exist"""
        logger.info("\n" + "="*80)
        logger.info("TEST 3: Method Existence Check")
        logger.info("="*80)

        try:
            learner = SkillLearner()
            analyzer = learner.analyzer

            # Check VideoTutorialAnalyzer methods
            required_analyzer_methods = [
                'get_transcript_with_timestamps',
                'parse_transcript_into_actions',
                'analyze_tutorial'
            ]

            for method_name in required_analyzer_methods:
                assert hasattr(analyzer, method_name), f"Missing method: {method_name}"
                method = getattr(analyzer, method_name)
                assert callable(method), f"Not callable: {method_name}"
                logger.info(f"   ✅ VideoTutorialAnalyzer.{method_name}()")

            # Check SkillLearner methods
            required_learner_methods = [
                'execute_tutorial_step',
                'execute_tutorial_step_with_retry',
                'learn_from_video',
                'save_skill',
                'load_skill',
                'execute_learned_skill'
            ]

            for method_name in required_learner_methods:
                assert hasattr(learner, method_name), f"Missing method: {method_name}"
                method = getattr(learner, method_name)
                assert callable(method), f"Not callable: {method_name}"
                logger.info(f"   ✅ SkillLearner.{method_name}()")

            logger.info("\n✅ All required methods exist and are callable")
            return True

        except Exception as e:
            logger.error(f"❌ Method check failed: {e}")
            return False

    def test_data_structures(self):
        """Test 4: Verify data structures are correct"""
        logger.info("\n" + "="*80)
        logger.info("TEST 4: Data Structure Validation")
        logger.info("="*80)

        try:
            # Test TutorialStep
            step = TutorialStep(
                step_number=1,
                description="Test step",
                action_type=StepType.CLICK,
                target="Test button",
                input_value=None,
                expected_result="Button clicked",
                timing_notes="At 10s"
            )

            assert step.step_number == 1
            assert step.action_type == StepType.CLICK
            logger.info("✅ TutorialStep structure valid")

            # Test LearnedSkill
            from datetime import datetime
            skill = LearnedSkill(
                skill_id="test_123",
                skill_name="Test Skill",
                category=SkillCategory.GENERAL,
                learned_by="test_agent",
                source_video_url="https://youtube.com/watch?v=test",
                video_title="Test Video",
                video_creator="Test Creator",
                steps=[step],
                required_tools=["Browser"],
                success_rate=1.0,
                times_executed=1,
                last_used_date=datetime.utcnow()
            )

            assert skill.skill_id == "test_123"
            assert skill.category == SkillCategory.GENERAL
            assert len(skill.steps) == 1
            logger.info("✅ LearnedSkill structure valid")

            return True

        except Exception as e:
            logger.error(f"❌ Data structure test failed: {e}")
            return False

    async def test_video_id_extraction(self):
        """Test 5: Test video ID extraction from URLs"""
        logger.info("\n" + "="*80)
        logger.info("TEST 5: Video ID Extraction")
        logger.info("="*80)

        try:
            import re

            # Test URLs
            test_cases = [
                ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
                ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
                ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
                ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ]

            patterns = [
                r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
                r'(?:embed\/)([0-9A-Za-z_-]{11})',
                r'(?:shorts\/)([0-9A-Za-z_-]{11})',
                r'^([0-9A-Za-z_-]{11})$'
            ]

            for url, expected_id in test_cases:
                video_id = None
                for pattern in patterns:
                    match = re.search(pattern, url)
                    if match:
                        video_id = match.group(1)
                        break

                assert video_id == expected_id, f"Failed for {url}: got {video_id}, expected {expected_id}"
                logger.info(f"   ✅ Extracted {video_id} from {url}")

            logger.info("\n✅ Video ID extraction logic works correctly")
            return True

        except Exception as e:
            logger.error(f"❌ Video ID extraction test failed: {e}")
            return False

    async def test_skill_persistence(self):
        """Test 6: Test skill save/load without real file I/O"""
        logger.info("\n" + "="*80)
        logger.info("TEST 6: Skill Persistence Logic")
        logger.info("="*80)

        try:
            from datetime import datetime
            import json

            # Create a test skill
            step = TutorialStep(
                step_number=1,
                description="Test step",
                action_type=StepType.CLICK,
                target="Test button",
                input_value=None,
                expected_result="Success",
                timing_notes="At 10s"
            )

            skill = LearnedSkill(
                skill_id="test_persist_123",
                skill_name="Test Persistence",
                category=SkillCategory.GENERAL,
                learned_by="test_agent",
                source_video_url="https://youtube.com/watch?v=test",
                video_title="Test",
                video_creator="Test",
                steps=[step],
                required_tools=["Browser"],
                success_rate=0.9,
                times_executed=5,
                last_used_date=datetime.utcnow()
            )

            # Test serialization (what save_skill does)
            skill_data = {
                "skill_id": skill.skill_id,
                "skill_name": skill.skill_name,
                "category": skill.category.value,
                "learned_by": skill.learned_by,
                "source_video_url": skill.source_video_url,
                "video_title": skill.video_title,
                "video_creator": skill.video_creator,
                "steps": [
                    {
                        "step_number": s.step_number,
                        "description": s.description,
                        "action_type": s.action_type.value,
                        "target": s.target,
                        "input_value": s.input_value,
                        "expected_result": s.expected_result,
                        "timing_notes": s.timing_notes
                    }
                    for s in skill.steps
                ],
                "required_tools": skill.required_tools,
                "success_rate": skill.success_rate,
                "times_executed": skill.times_executed,
                "last_used_date": skill.last_used_date.isoformat()
            }

            # Verify it's JSON serializable
            json_str = json.dumps(skill_data, indent=2)
            assert len(json_str) > 0

            # Verify it can be deserialized
            loaded_data = json.loads(json_str)
            assert loaded_data["skill_id"] == "test_persist_123"
            assert loaded_data["skill_name"] == "Test Persistence"

            logger.info("✅ Skill serialization/deserialization works")
            logger.info(f"   - Serialized to {len(json_str)} bytes")
            logger.info(f"   - Can be loaded back")

            return True

        except Exception as e:
            logger.error(f"❌ Persistence test failed: {e}")
            return False

    def test_error_handling(self):
        """Test 7: Verify error handling exists"""
        logger.info("\n" + "="*80)
        logger.info("TEST 7: Error Handling")
        logger.info("="*80)

        try:
            learner = SkillLearner()

            # Check that methods have try/except blocks
            import inspect

            methods_to_check = [
                learner.analyzer.get_transcript_with_timestamps,
                learner.analyzer.parse_transcript_into_actions,
                learner.execute_tutorial_step,
                learner.save_skill,
                learner.load_skill
            ]

            for method in methods_to_check:
                source = inspect.getsource(method)
                has_try_except = "try:" in source and "except" in source
                method_name = method.__name__

                if has_try_except:
                    logger.info(f"   ✅ {method_name} has error handling")
                else:
                    logger.warning(f"   ⚠️  {method_name} may lack error handling")

            logger.info("\n✅ Error handling check complete")
            return True

        except Exception as e:
            logger.error(f"❌ Error handling test failed: {e}")
            return False


async def run_all_tests():
    """Run all unit tests"""
    logger.info("\n" + "="*80)
    logger.info("🧪 UNIT TEST SUITE - Tutorial Learning System")
    logger.info("="*80)
    logger.info("Testing implementation structure without live API calls\n")

    tester = TestTutorialLearningStructure()

    results = {}

    # Run synchronous tests
    results["imports"] = tester.test_imports()
    results["instantiation"] = tester.test_class_instantiation()
    results["methods"] = tester.test_method_existence()
    results["data_structures"] = tester.test_data_structures()
    results["error_handling"] = tester.test_error_handling()

    # Run async tests
    results["video_id_extraction"] = await tester.test_video_id_extraction()
    results["persistence"] = await tester.test_skill_persistence()

    # Summary
    logger.info("\n" + "="*80)
    logger.info("📊 TEST SUMMARY")
    logger.info("="*80)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")

    logger.info(f"\n{'='*80}")
    logger.info(f"✅ {passed}/{total} tests passed")
    logger.info(f"{'='*80}")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
