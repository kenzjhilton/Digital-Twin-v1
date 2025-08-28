import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class UserSessionManager:
    """Manages saving and loading user input sessions"""
    
    def __init__(self, base_path: str = "src/tests/user_sessions"):
        self.base_path = Path(base_path)
        self.session_logs_path = self.base_path / "session_logs"
        self.scenarios_path = self.base_path / "test_scenarios"
        self.configs_path = self.base_path / "operator_configs" 
        self.results_path = self.base_path / "simulation_results"
        
        # Create directories if they don't exist
        for path in [self.session_logs_path, self.scenarios_path, 
                     self.configs_path, self.results_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def save_session_log(self, session_data: Dict[str, Any], 
                        session_name: Optional[str] = None) -> str:
        """Save complete operator session"""
        
        if session_name is None:
            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            operator_name = session_data.get('operator_name', 'unknown').replace(' ', '_')
            session_name = f"session_{timestamp}_{operator_name}"
        
        filepath = self.session_logs_path / f"{session_name}.json"
        
        # Prepare data for JSON serialization
        clean_data = self._serialize_datetime_objects(session_data)
        
        with open(filepath, 'w') as f:
            json.dump(clean_data, f, indent=2)
        
        print(f"💾 Session saved: {filepath}")
        return str(filepath)
    
    def save_test_scenario(self, scenario_data: Dict[str, Any], 
                          scenario_name: str) -> str:
        """Save reusable test scenario"""
        
        filepath = self.scenarios_path / f"{scenario_name}.json"
        
        with open(filepath, 'w') as f:
            json.dump(scenario_data, f, indent=2)
        
        print(f"📋 Scenario saved: {filepath}")
        return str(filepath)
    
    def save_simulation_results(self, results_data: Dict[str, Any], 
                              results_name: Optional[str] = None) -> str:
        """Save simulation output data"""
        
        if results_name is None:
            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
            results_name = f"results_{timestamp}"
        
        filepath = self.results_path / f"{results_name}.json"
        
        clean_data = self._serialize_datetime_objects(results_data)
        
        with open(filepath, 'w') as f:
            json.dump(clean_data, f, indent=2)
        
        print(f"📊 Results saved: {filepath}")
        return str(filepath)

    def save_operator_config(self, config_data: Dict[str, Any], 
                              facility_name: str,
                              config_type: str = "generic") -> str:
        """Save an individual operator configuration under operator_configs.

        Args:
            config_data: The configuration payload to persist.
            facility_name: Used to build a readable filename.
            config_type: Subfolder to categorize configs (e.g., 'mining').

        Returns:
            The path to the saved configuration file as a string.
        """
        # Ensure a clean, filesystem-friendly stem
        safe_facility = (facility_name or "default").replace(' ', '_')
        target_dir = self.configs_path / config_type
        target_dir.mkdir(parents=True, exist_ok=True)

        filepath = target_dir / f"{safe_facility}_config.json"

        clean_data = self._serialize_datetime_objects(config_data)
        with open(filepath, 'w') as f:
            json.dump(clean_data, f, indent=2)

        print(f"⚙️  Operator config saved: {filepath}")
        return str(filepath)
    
    def load_session_log(self, session_name: str) -> Dict[str, Any]:
        """Load a saved session"""
        filepath = self.session_logs_path / f"{session_name}.json"
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def list_available_sessions(self) -> list:
        """List all saved sessions"""
        return [f.stem for f in self.session_logs_path.glob("*.json")]
    
    def _serialize_datetime_objects(self, obj):
        """Convert datetime objects to ISO strings for JSON"""
        if isinstance(obj, dict):
            return {k: self._serialize_datetime_objects(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_datetime_objects(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj
