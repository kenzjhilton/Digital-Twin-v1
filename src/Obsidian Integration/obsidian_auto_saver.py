"""
Auto-Save Simulation Results to Obsidian Vault
==============================================

This module automatically creates/updates an Obsidian vault with simulation results
every time you complete a simulated order.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class ObsidianAutoSaver:
    """
    Automatically saves simulation results to Obsidian vault after each run
    """
    
    def __init__(self, vault_path: str = None, auto_create_vault: bool = True):
        """
        Initialize auto-saver for Obsidian integration
        
        Args:
            vault_path: Path to Obsidian vault (if None, creates new vault)
            auto_create_vault: Whether to create vault if it doesn't exist
        """
        if vault_path is None:
            # Create new vault in your project directory
            vault_path = Path.cwd() / "Digital_Twin_Vault"
        
        self.vault_path = Path(vault_path)
        
        if auto_create_vault:
            self._create_new_vault()
        
        print(f"🔗 Obsidian auto-saver ready for vault: {self.vault_path}")
    
    def _create_new_vault(self):
        """Create a new Obsidian vault with proper structure"""
        # Create vault directory
        self.vault_path.mkdir(parents=True, exist_ok=True)
        
        # Create folder structure
        folders = [
            "Simulation Sessions",
            "Agents",
            "Agents/Mining",
            "Agents/Processing", 
            "Agents/Manufacturing",
            "Agents/Distribution",
            "Agents/Sales",
            "Material Flows",
            "Performance Reports",
            "Templates",
            "Attachments"
        ]
        
        for folder in folders:
            (self.vault_path / folder).mkdir(parents=True, exist_ok=True)
        
        # Create .obsidian config folder for graph view settings
        obsidian_config = self.vault_path / ".obsidian"
        obsidian_config.mkdir(exist_ok=True)
        
        # Create graph view configuration for supply chain visualization
        self._create_obsidian_config()
        
        print(f"✅ New Obsidian vault created at: {self.vault_path}")
    
    def _create_obsidian_config(self):
        """Create Obsidian configuration for optimal supply chain visualization"""
        config_dir = self.vault_path / ".obsidian"
        
        # Graph view configuration
        graph_config = {
            "collapse-filter": True,
            "search": "",
            "showTags": True,
            "showAttachments": False,
            "hideUnresolved": False,
            "showOrphans": True,
            "collapse-color-groups": True,
            "colorGroups": [
                {
                    "query": "tag:#mining",
                    "color": {"a": 1, "rgb": 14701138}
                },
                {
                    "query": "tag:#processing", 
                    "color": {"a": 1, "rgb": 14725458}
                },
                {
                    "query": "tag:#manufacturing",
                    "color": {"a": 1, "rgb": 11657298}
                },
                {
                    "query": "tag:#distribution",
                    "color": {"a": 1, "rgb": 5431378}
                },
                {
                    "query": "tag:#sales",
                    "color": {"a": 1, "rgb": 5431473}
                }
            ],
            "collapse-display": True,
            "showArrow": True,
            "textFadeMultiplier": 0,
            "nodeSizeMultiplier": 1,
            "lineSizeMultiplier": 1,
            "collapse-forces": True,
            "centerStrength": 0.518713248970312,
            "repelStrength": 10,
            "linkStrength": 1,
            "linkDistance": 250,
            "scale": 1,
            "close": True
        }
        
        with open(config_dir / "graph.json", "w") as f:
            json.dump(graph_config, f, indent=2)
        
        # App configuration
        app_config = {
            "legacyEditor": False,
            "livePreview": True,
            "showLineNumber": False,
            "spellcheck": True
        }
        
        with open(config_dir / "app.json", "w") as f:
            json.dump(app_config, f, indent=2)
    
    def save_simulation_to_vault(self, simulation_results: Dict[str, Any]) -> Dict[str, str]:
        """
        Main method: Save complete simulation results to Obsidian vault
        
        Args:
            simulation_results: Complete results from your simulation
            
        Returns:
            Dict with paths to all created notes
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        session_id = simulation_results.get('simulation_id', f"SIM_{timestamp}")
        
        created_notes = {}
        
        # 1. Create main simulation session note
        session_note = self._create_simulation_session_note(simulation_results, timestamp)
        created_notes['session'] = str(session_note)
        
        # 2. Create individual agent notes
        agent_notes = self._create_agent_notes(simulation_results, timestamp)
        created_notes.update(agent_notes)
        
        # 3. Create material flow trace note
        flow_note = self._create_material_flow_note(simulation_results, timestamp)
        created_notes['material_flow'] = str(flow_note)
        
        # 4. Create performance report
        performance_note = self._create_performance_report(simulation_results, timestamp)
        created_notes['performance'] = str(performance_note)
        
        # 5. Update index/dashboard note
        self._update_dashboard(simulation_results, timestamp, created_notes)
        
        print(f"💾 Simulation saved to Obsidian vault!")
        print(f"📁 Main session note: {session_note}")
        print(f"🔍 Open vault in Obsidian: {self.vault_path}")
        
        return created_notes
    
    def _create_simulation_session_note(self, results: Dict, timestamp: str) -> Path:
        """Create main simulation session overview note"""
        session_file = self.vault_path / "Simulation Sessions" / f"Session_{timestamp}.md"
        
        # Extract key information
        config = results.get('simulation_config', {})
        overview = config.get('overview', {})
        final_metrics = results.get('final_metrics', {})
        
        content = f"""# Simulation Session - {timestamp}

## Session Overview
- **Company**: {overview.get('company_name', 'Unknown')}
- **Operator**: {overview.get('operator_name', 'Unknown')}
- **Simulation Type**: {overview.get('simulation_type', 'Unknown')}
- **Duration**: {results.get('duration', 'Unknown')}
- **Session ID**: `{results.get('simulation_id', 'Unknown')}`

## Quick Links
- [[Mining Operation - {timestamp}|Mining Facility]]
- [[Processing Plant - {timestamp}|Processing Facility]]
- [[Manufacturing - {timestamp}|Manufacturing Facility]]
- [[Distribution - {timestamp}|Distribution Center]]
- [[Sales Operation - {timestamp}|Sales Organization]]
- [[Material Flow - {timestamp}|Material Flow Trace]]
- [[Performance Report - {timestamp}|Performance Analysis]]

## Key Performance Metrics
| Metric | Value |
|--------|-------|
| **Total Revenue** | ${final_metrics.get('total_revenue', 0):,.2f} |
| **Net Profit** | ${final_metrics.get('net_profit', 0):,.2f} |
| **Profit Margin** | {final_metrics.get('profit_margin_percent', 0):.1f}% |
| **Ore Processed** | {final_metrics.get('input_ore_tons', 0):,.0f} tons |
| **Products Manufactured** | {final_metrics.get('manufactured_products_units', 0):,.0f} units |
| **Conversion Efficiency** | {final_metrics.get('ore_to_product_conversion_rate', 0):.3f} |

## Material Flow Summary
"""
        
        # Add material flow steps
        material_flow = results.get('material_flow', [])
        for step in material_flow:
            stage = step.get('stage', '').title()
            material = step.get('material', 'Unknown')
            quantity = step.get('quantity', 0)
            location = step.get('location', 'Unknown')
            content += f"- **{stage}**: {quantity:,.1f} tons of {material} at {location}\n"
        
        content += f"""

## Tags
#simulation #supply-chain #session-{timestamp.split('_')[0]} #completed

## Related Notes
- [[Supply Chain Dashboard]]
- [[Agent Configuration Templates]]

---
*Generated automatically from Digital Twin simulation on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*
"""
        
        with open(session_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return session_file
    
    def _create_agent_notes(self, results: Dict, timestamp: str) -> Dict[str, str]:
        """Create individual notes for each agent with their configurations and results"""
        agent_notes = {}
        config = results.get('simulation_config', {})
        stages = results.get('stages', {})
        
        # Mining Agent Note
        mining_config = config.get('mining', {})
        mining_result = stages.get('mining', {})
        
        mining_note = self.vault_path / "Agents" / "Mining" / f"Mining Operation - {timestamp}.md"
        mining_content = f"""# Mining Operation - {timestamp}

## Facility Information
- **Name**: {mining_config.get('facility_name', 'Unknown')}
- **Location**: {mining_config.get('location', 'Unknown')}
- **Ore Type**: {mining_config.get('ore_type', 'Unknown')}
- **Storage Capacity**: {mining_config.get('storage_capacity', 0):,.0f} tons
- **Extraction Rate**: {mining_config.get('extraction_rate', 0):,.0f} tons/hour

## Simulation Results
- **Extracted Quantity**: {mining_result.get('quantity_extracted', 0):,.0f} tons
- **Ore Quality**: {mining_result.get('ore_quality', 0):.2f}
- **Extraction Cost**: ${mining_result.get('total_extraction_cost', 0):,.2f}

## Equipment Status
"""
        
        equipment_status = mining_config.get('equipment_status', {})
        for equipment, status in equipment_status.items():
            mining_content += f"- **{equipment}**: {status}\n"
        
        mining_content += f"""

## Connections
- Sends materials to: [[Processing Plant - {timestamp}]]
- Part of session: [[Session_{timestamp}]]

#mining #agent #extraction #ore-processing
"""
        
        with open(mining_note, 'w', encoding='utf-8') as f:
            f.write(mining_content)
        agent_notes['mining'] = str(mining_note)
        
        # Processing Agent Note
        processing_config = config.get('processing', {})
        processing_result = stages.get('processing', {})
        
        processing_note = self.vault_path / "Agents" / "Processing" / f"Processing Plant - {timestamp}.md"
        processing_content = f"""# Processing Plant - {timestamp}

## Facility Information
- **Name**: {processing_config.get('facility_name', 'Unknown')}
- **Capacity**: {processing_config.get('capacity', 0):,.0f} tons/hour
- **Target Efficiency**: {processing_config.get('target_efficiency', 0):.2f}
- **Target Quality**: {processing_config.get('target_quality', 0):.2f}

## Processing Methods
"""
        
        methods = processing_config.get('processing_methods', [])
        for method in methods:
            processing_content += f"- {method}\n"
        
        processing_content += f"""

## Simulation Results
- **Input Material**: {processing_result.get('input_material', 'Unknown')}
- **Input Quantity**: {processing_result.get('input_quantity', 0):,.0f} tons
- **Output Material**: {processing_result.get('output_material', 'Unknown')}
- **Output Quantity**: {processing_result.get('output_quantity', 0):,.1f} tons
- **Quality Achieved**: {processing_result.get('quality_achieved', 0):.2f}
- **Processing Cost**: ${processing_result.get('energy_cost', 0):,.2f}
- **Efficiency**: {processing_result.get('efficiency', 0):.2f}

## Connections
- Receives from: [[Mining Operation - {timestamp}]]
- Sends to: [[Manufacturing - {timestamp}]]
- Part of session: [[Session_{timestamp}]]

#processing #agent #transformation #chemical-processing
"""
        
        with open(processing_note, 'w', encoding='utf-8') as f:
            f.write(processing_content)
        agent_notes['processing'] = str(processing_note)
        
        # Continue with other agents...
        # (Manufacturing, Distribution, Sales notes follow similar pattern)
        
        return agent_notes
    
    def _create_material_flow_note(self, results: Dict, timestamp: str) -> Path:
        """Create material flow trace visualization note"""
        flow_file = self.vault_path / "Material Flows" / f"Material Flow - {timestamp}.md"
        
        content = f"""# Material Flow Trace - {timestamp}

## Flow Overview
This trace follows materials through the complete supply chain from raw extraction to customer delivery.

## Material Journey
```mermaid
graph LR
    A[Mining] --> B[Processing]
    B --> C[Manufacturing] 
    C --> D[Distribution]
    D --> E[Sales]
```

## Detailed Flow Steps
"""
        
        material_flow = results.get('material_flow', [])
        for i, step in enumerate(material_flow, 1):
            timestamp_step = step.get('timestamp', datetime.now()).strftime('%H:%M:%S')
            stage = step.get('stage', '').title()
            material = step.get('material', 'Unknown')
            quantity = step.get('quantity', 0)
            location = step.get('location', 'Unknown')
            
            content += f"""
### Step {i}: {stage}
- **Time**: {timestamp_step}
- **Material**: {material}
- **Quantity**: {quantity:,.1f} tons
- **Location**: {location}
- **Link**: [[{stage} Operation - {timestamp}]]
"""
        
        content += f"""

## Performance Summary
- **Total Processing Time**: {results.get('duration', 'Unknown')}
- **Material Conversion Efficiency**: {results.get('final_metrics', {}).get('ore_to_product_conversion_rate', 0):.3f}
- **End-to-End Traceability**: ✅ Complete

## Related Notes
- [[Session_{timestamp}]]
- [[Performance Report - {timestamp}]]

#material-flow #traceability #supply-chain #end-to-end
"""
        
        with open(flow_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return flow_file
    
    def _create_performance_report(self, results: Dict, timestamp: str) -> Path:
        """Create detailed performance analysis note"""
        perf_file = self.vault_path / "Performance Reports" / f"Performance Report - {timestamp}.md"
        
        final_metrics = results.get('final_metrics', {})
        
        content = f"""# Performance Report - {timestamp}

## Executive Summary
This report analyzes the operational and financial performance of the supply chain simulation.

## Financial Performance
| Metric | Value | Notes |
|--------|-------|-------|
| **Total Revenue** | ${final_metrics.get('total_revenue', 0):,.2f} | Final customer sales |
| **Total Costs** | ${final_metrics.get('total_costs', 0):,.2f} | All operational costs |
| **Net Profit** | ${final_metrics.get('net_profit', 0):,.2f} | Revenue minus costs |
| **Profit Margin** | {final_metrics.get('profit_margin_percent', 0):.1f}% | Profitability ratio |
| **Revenue per Ton** | ${final_metrics.get('revenue_per_ton_ore', 0):.2f} | Revenue efficiency |

## Operational Efficiency
| Metric | Value | Performance |
|--------|-------|-------------|
| **Raw Material Input** | {final_metrics.get('input_ore_tons', 0):,.0f} tons | Starting material |
| **Processed Output** | {final_metrics.get('processed_material_tons', 0):,.1f} tons | After processing |
| **Manufactured Products** | {final_metrics.get('manufactured_products_units', 0):,.1f} units | Finished goods |
| **Products Sold** | {final_metrics.get('sold_tons', 0):,.1f} tons | Customer delivery |
| **Conversion Rate** | {final_metrics.get('ore_to_product_conversion_rate', 0):.3f} | Overall efficiency |

## Operator Decisions Impact
"""
        
        operator_decisions = results.get('operator_decisions', [])
        for decision in operator_decisions:
            stage = decision.get('stage', '').title()
            decisions = decision.get('decisions', {})
            content += f"""
### {stage} Decisions
"""
            for key, value in decisions.items():
                content += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        
        content += f"""

## Recommendations
Based on this simulation:
- Review processing efficiency opportunities
- Analyze cost optimization potential in distribution
- Consider quality vs. efficiency trade-offs
- Evaluate pricing strategy effectiveness

## Related Analysis
- [[Session_{timestamp}]]
- [[Material Flow - {timestamp}]]

#performance #analysis #metrics #optimization
"""
        
        with open(perf_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return perf_file
    
    def _update_dashboard(self, results: Dict, timestamp: str, created_notes: Dict):
        """Update main dashboard with links to new simulation"""
        dashboard_file = self.vault_path / "Supply Chain Dashboard.md"
        
        # Create dashboard if it doesn't exist
        if not dashboard_file.exists():
            dashboard_content = """# Supply Chain Digital Twin Dashboard

## Recent Simulations
"""
        else:
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                dashboard_content = f.read()
        
        # Add new simulation to the top of recent simulations
        config = results.get('simulation_config', {})
        overview = config.get('overview', {})
        final_metrics = results.get('final_metrics', {})
        
        new_entry = f"""
### [[Session_{timestamp}|Simulation {timestamp}]]
- **Company**: {overview.get('company_name', 'Unknown')}
- **Revenue**: ${final_metrics.get('total_revenue', 0):,.2f}
- **Profit**: ${final_metrics.get('net_profit', 0):,.2f}
- **Efficiency**: {final_metrics.get('ore_to_product_conversion_rate', 0):.3f}
- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        
        # Insert new entry after "## Recent Simulations"
        lines = dashboard_content.split('\n')
        insert_index = -1
        for i, line in enumerate(lines):
            if "## Recent Simulations" in line:
                insert_index = i + 1
                break
        
        if insert_index > -1:
            lines.insert(insert_index, new_entry)
            dashboard_content = '\n'.join(lines)
        else:
            dashboard_content += new_entry
        
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(dashboard_content)


# Integration with your existing simulation system
def integrate_with_existing_simulator():
    """
    Show how to integrate with your existing EnhancedSupplyChainSimulator
    """
    
    # Add this to your main simulation class
    class EnhancedSupplyChainSimulatorWithObsidian:
        def __init__(self, obsidian_vault_path: str = None):
            # Your existing initialization
            self.operator_interface = InteractiveOperatorInterface()
            # ... rest of your existing code ...
            
            # Add Obsidian integration
            self.obsidian_saver = ObsidianAutoSaver(obsidian_vault_path)
        
        def run_interactive_simulation(self) -> Dict:
            """Enhanced version that auto-saves to Obsidian"""
            
            # Your existing simulation logic
            results = self._run_simulation_with_operator_decisions()
            
            # Auto-save to Obsidian vault after completion
            obsidian_notes = self.obsidian_saver.save_simulation_to_vault(results)
            results['obsidian_notes'] = obsidian_notes
            
            print(f"\n🔗 OBSIDIAN INTEGRATION COMPLETE!")
            print(f"📝 Notes created in vault: {self.obsidian_saver.vault_path}")
            print(f"💡 Open Obsidian and navigate to your vault to explore results!")
            
            return results


# Example usage
if __name__ == "__main__":
    # Option 1: Create new vault automatically
    auto_saver = ObsidianAutoSaver()
    
    # Option 2: Use existing vault
    # auto_saver = ObsidianAutoSaver("/path/to/your/existing/vault")
    
    # Example simulation results (replace with your actual results)
    example_results = {
        "simulation_id": "SIM_20241201_143022",
        "duration": "45 minutes",
        "simulation_config": {
            "overview": {
                "company_name": "AMX Mining Corp",
                "operator_name": "John Smith", 
                "simulation_type": "Full End-to-End"
            }
        },
        "final_metrics": {
            "total_revenue": 2500000.0,
            "net_profit": 375000.0,
            "profit_margin_percent": 15.0
        }
    }
    
    # Save to Obsidian
    notes = auto_saver.save_simulation_to_vault(example_results)
    print(f"Created notes: {notes}")