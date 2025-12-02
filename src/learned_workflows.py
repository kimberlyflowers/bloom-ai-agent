"""
LEARNED WORKFLOWS - Sarah's Muscle Memory 💪

Stores and replays UI workflows Sarah learns from tutorials.

Example:
    Sarah watches "How to edit in CapCut"
    → Learns 15 steps (click buttons, import files, add effects)
    → Stores as reusable workflow
    → Can execute "edit_video_in_capcut()" without rewatching tutorial

This is the difference between:
- AI Advisor: "You should use CapCut to edit" ❌
- AI Agent: *Actually opens CapCut and edits video* ✅
"""

import json
import logging
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import base64
from io import BytesIO

logger = logging.getLogger(__name__)

# Storage directory for learned workflows
WORKFLOWS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'learned_workflows')
os.makedirs(WORKFLOWS_DIR, exist_ok=True)


@dataclass
class WorkflowStep:
    """
    Single step in a learned workflow

    Example:
        instruction: "Click the New Project button"
        action: "click"
        target: "New Project button"
        location: {"x": 150, "y": 200}
        element_description: "Blue button in top-left with text 'New Project'"
        screenshot_ref: "step_001.png"
    """
    step_number: int
    instruction: str  # What the tutorial said to do
    action: str  # click, type, drag, select, wait
    target: str  # What element to interact with
    location: Optional[Dict[str, int]] = None  # {"x": 150, "y": 200}
    text_input: Optional[str] = None  # For typing actions
    element_description: str = ""  # How to find this element
    screenshot_ref: Optional[str] = None  # Reference screenshot filename
    timestamp: float = 0.0  # When this step occurs in tutorial video
    verification: Optional[str] = None  # What should happen after this step

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON storage"""
        return asdict(self)


class LearnedWorkflow:
    """
    Complete workflow learned from a UI tutorial

    Example:
        name: "create_heygen_avatar_video"
        tool: "HeyGen"
        description: "How to create AI avatar videos in HeyGen"
        steps: [WorkflowStep(...), WorkflowStep(...), ...]
        source_video: "https://youtube.com/watch?v=..."
    """

    def __init__(
        self,
        name: str,
        tool: str,
        description: str = "",
        source_video: str = ""
    ):
        self.name = name
        self.tool = tool
        self.description = description
        self.source_video = source_video
        self.steps: List[WorkflowStep] = []
        self.learned_at = datetime.now().isoformat()
        self.last_used = None
        self.success_count = 0
        self.failure_count = 0

    def add_step(
        self,
        instruction: str,
        action: str,
        target: str,
        location: Optional[Dict[str, int]] = None,
        text_input: Optional[str] = None,
        element_description: str = "",
        screenshot_ref: Optional[str] = None,
        timestamp: float = 0.0,
        verification: Optional[str] = None
    ) -> WorkflowStep:
        """
        Add a step to the workflow

        Args:
            instruction: Tutorial instruction (e.g., "Click New Project")
            action: Action type (click, type, drag, select, wait)
            target: What to interact with (e.g., "New Project button")
            location: Coordinates if needed {"x": 150, "y": 200}
            text_input: Text to type (for 'type' actions)
            element_description: How to find element (for future reference)
            screenshot_ref: Filename of reference screenshot
            timestamp: When this occurs in tutorial video
            verification: Expected result after this step

        Returns:
            The created WorkflowStep
        """
        step = WorkflowStep(
            step_number=len(self.steps) + 1,
            instruction=instruction,
            action=action,
            target=target,
            location=location,
            text_input=text_input,
            element_description=element_description,
            screenshot_ref=screenshot_ref,
            timestamp=timestamp,
            verification=verification
        )

        self.steps.append(step)
        logger.info(f"📝 Added step {step.step_number}: {instruction}")
        return step

    async def replay(self, browser, progress_callback=None) -> Dict[str, Any]:
        """
        Execute the learned workflow

        Args:
            browser: SarahBrowser instance
            progress_callback: Optional callback for progress updates

        Returns:
            Dict with execution results
        """
        logger.info(f"🎬 Replaying workflow: {self.name} ({len(self.steps)} steps)")

        if progress_callback:
            await progress_callback(f"Starting workflow: {self.description}")

        results = {
            'workflow': self.name,
            'success': True,
            'completed_steps': 0,
            'failed_steps': 0,
            'errors': []
        }

        for step in self.steps:
            logger.info(f"📍 Step {step.step_number}/{len(self.steps)}: {step.instruction}")

            if progress_callback:
                await progress_callback(f"Step {step.step_number}: {step.instruction}")

            try:
                # Execute the step based on action type
                if step.action == 'click':
                    await self._execute_click(browser, step)

                elif step.action == 'type':
                    await self._execute_type(browser, step)

                elif step.action == 'wait':
                    await self._execute_wait(browser, step)

                elif step.action == 'navigate':
                    await self._execute_navigate(browser, step)

                elif step.action == 'select':
                    await self._execute_select(browser, step)

                else:
                    logger.warning(f"⚠️ Unknown action type: {step.action}")

                results['completed_steps'] += 1

                # Small delay between steps
                import asyncio
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"❌ Step {step.step_number} failed: {e}")
                results['failed_steps'] += 1
                results['errors'].append(f"Step {step.step_number}: {str(e)}")
                results['success'] = False

                # Continue to next step (don't abort entire workflow)
                continue

        # Update usage stats
        self.last_used = datetime.now().isoformat()
        if results['success']:
            self.success_count += 1
        else:
            self.failure_count += 1

        # Save updated stats
        self.save()

        logger.info(f"🏁 Workflow complete: {results['completed_steps']}/{len(self.steps)} steps succeeded")
        return results

    async def _execute_click(self, browser, step: WorkflowStep):
        """Execute a click action"""
        if step.location:
            # Click at specific coordinates
            await browser.page.mouse.click(step.location['x'], step.location['y'])
        else:
            # Use universal_click with target description
            await browser.universal_click(step.target)

    async def _execute_type(self, browser, step: WorkflowStep):
        """Execute a type action"""
        if step.text_input:
            await browser.page.keyboard.type(step.text_input)

    async def _execute_wait(self, browser, step: WorkflowStep):
        """Execute a wait action"""
        import asyncio
        wait_time = step.location.get('seconds', 2) if step.location else 2
        await asyncio.sleep(wait_time)

    async def _execute_navigate(self, browser, step: WorkflowStep):
        """Execute a navigation action"""
        if step.text_input:  # URL stored in text_input
            await browser.navigate(step.text_input)

    async def _execute_select(self, browser, step: WorkflowStep):
        """Execute a select action"""
        # Use universal_click to select the item
        await browser.universal_click(step.target)

    def save(self) -> bool:
        """
        Save workflow to disk

        Returns:
            True if saved successfully
        """
        try:
            filepath = os.path.join(WORKFLOWS_DIR, f"{self.name}.json")

            workflow_data = {
                'name': self.name,
                'tool': self.tool,
                'description': self.description,
                'source_video': self.source_video,
                'learned_at': self.learned_at,
                'last_used': self.last_used,
                'success_count': self.success_count,
                'failure_count': self.failure_count,
                'steps': [step.to_dict() for step in self.steps]
            }

            with open(filepath, 'w') as f:
                json.dump(workflow_data, f, indent=2)

            logger.info(f"💾 Saved workflow: {filepath}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save workflow: {e}")
            return False

    @staticmethod
    def load(workflow_name: str) -> Optional['LearnedWorkflow']:
        """
        Load workflow from disk

        Args:
            workflow_name: Name of the workflow to load

        Returns:
            LearnedWorkflow instance or None if not found
        """
        try:
            filepath = os.path.join(WORKFLOWS_DIR, f"{workflow_name}.json")

            if not os.path.exists(filepath):
                logger.warning(f"⚠️ Workflow not found: {workflow_name}")
                return None

            with open(filepath, 'r') as f:
                data = json.load(f)

            workflow = LearnedWorkflow(
                name=data['name'],
                tool=data['tool'],
                description=data['description'],
                source_video=data['source_video']
            )

            workflow.learned_at = data['learned_at']
            workflow.last_used = data.get('last_used')
            workflow.success_count = data.get('success_count', 0)
            workflow.failure_count = data.get('failure_count', 0)

            # Load steps
            for step_data in data['steps']:
                workflow.steps.append(WorkflowStep(**step_data))

            logger.info(f"📂 Loaded workflow: {workflow_name} ({len(workflow.steps)} steps)")
            return workflow

        except Exception as e:
            logger.error(f"❌ Failed to load workflow: {e}")
            return None

    @staticmethod
    def list_all() -> List[str]:
        """
        List all saved workflows

        Returns:
            List of workflow names
        """
        try:
            workflows = []
            for filename in os.listdir(WORKFLOWS_DIR):
                if filename.endswith('.json'):
                    workflows.append(filename[:-5])  # Remove .json extension
            return sorted(workflows)
        except Exception as e:
            logger.error(f"❌ Failed to list workflows: {e}")
            return []

    def __repr__(self) -> str:
        return f"LearnedWorkflow(name='{self.name}', tool='{self.tool}', steps={len(self.steps)})"


class WorkflowManager:
    """
    Manager for all learned workflows

    Provides easy access to workflows and analytics
    """

    @staticmethod
    def get_workflow(name: str) -> Optional[LearnedWorkflow]:
        """Get a specific workflow"""
        return LearnedWorkflow.load(name)

    @staticmethod
    def list_workflows() -> List[Dict[str, Any]]:
        """
        List all workflows with metadata

        Returns:
            List of dicts with workflow info
        """
        workflows = []
        for name in LearnedWorkflow.list_all():
            workflow = LearnedWorkflow.load(name)
            if workflow:
                workflows.append({
                    'name': workflow.name,
                    'tool': workflow.tool,
                    'description': workflow.description,
                    'steps': len(workflow.steps),
                    'learned_at': workflow.learned_at,
                    'success_count': workflow.success_count,
                    'failure_count': workflow.failure_count
                })
        return workflows

    @staticmethod
    def get_workflows_for_tool(tool: str) -> List[LearnedWorkflow]:
        """
        Get all workflows for a specific tool

        Args:
            tool: Tool name (e.g., "CapCut", "HeyGen", "Canva")

        Returns:
            List of workflows for that tool
        """
        workflows = []
        for name in LearnedWorkflow.list_all():
            workflow = LearnedWorkflow.load(name)
            if workflow and workflow.tool.lower() == tool.lower():
                workflows.append(workflow)
        return workflows

    @staticmethod
    def delete_workflow(name: str) -> bool:
        """Delete a workflow"""
        try:
            filepath = os.path.join(WORKFLOWS_DIR, f"{name}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"🗑️ Deleted workflow: {name}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Failed to delete workflow: {e}")
            return False
