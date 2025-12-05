import json
from pathlib import Path
from typing import Dict, Optional, Any
import logging

class UIMapLoader:
    """Load and manage UI element maps for different applications"""

    def __init__(self):
        self.maps_dir = Path(__file__).parent
        self.loaded_maps = {}
        self.logger = logging.getLogger(__name__)

    def load_map(self, app_name: str) -> Optional[Dict[str, Any]]:
        """Load UI map for specific application"""
        if app_name in self.loaded_maps:
            return self.loaded_maps[app_name]

        map_path = self.maps_dir / app_name / "map.json"

        if not map_path.exists():
            self.logger.debug(f"No UI map found for {app_name}")
            return None

        try:
            with open(map_path, 'r') as f:
                ui_map = json.load(f)
                self.loaded_maps[app_name] = ui_map
                self.logger.info(f"✅ Loaded UI map for {app_name}")
                return ui_map
        except Exception as e:
            self.logger.error(f"Error loading UI map for {app_name}: {e}")
            return None

    def get_element(self, app_name: str, category: str, element_name: str) -> Optional[Dict[str, Any]]:
        """Get specific element details from UI map"""
        ui_map = self.load_map(app_name)
        if not ui_map:
            return None

        try:
            return ui_map.get(category, {}).get(element_name)
        except Exception:
            return None

    def get_workflow(self, app_name: str, workflow_name: str) -> Optional[Dict[str, Any]]:
        """Get workflow steps from UI map"""
        ui_map = self.load_map(app_name)
        if not ui_map:
            return None

        return ui_map.get("common_workflows", {}).get(workflow_name)

    def has_map(self, app_name: str) -> bool:
        """Check if UI map exists for application"""
        map_path = self.maps_dir / app_name / "map.json"
        return map_path.exists()

    def get_interaction_type(self, app_name: str, element_name: str) -> Optional[str]:
        """
        Get interaction type for element.
        Returns: 'navigation', 'sidebar', 'modal', or 'inline'
        """
        ui_map = self.load_map(app_name)
        if not ui_map:
            return None

        # Search all categories for the element
        for category, elements in ui_map.items():
            if category in ["interaction_patterns", "common_workflows", "visual_patterns", "speed_optimization"]:
                continue

            if isinstance(elements, dict):
                for elem_key, elem_data in elements.items():
                    if elem_key == element_name and isinstance(elem_data, dict):
                        return elem_data.get("interaction_type")

        return None

# Global instance
ui_map_loader = UIMapLoader()
