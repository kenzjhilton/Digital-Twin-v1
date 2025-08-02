"""
Simulation Module
================

Core simulation engine components for supply chain reconstruction.
This module will contain the main simulation controllers, event scheduling,
and material tracking systems.

Planned Components:
- SupplyChainSimulator: Main simulation controller
- MaterialTracker: Track materials through the supply chain
- EventScheduler: Manage simulation timing and events

Currently Available:
- Basic simulation framework (to be implemented)

Usage:
    from src.simulation import SupplyChainSimulator, MaterialTracker
"""

# Placeholder imports for future implementation
# from .supply_chain_simulator import SupplyChainSimulator
# from .material_tracker import MaterialTracker  
# from .event_scheduler import EventScheduler

__all__ = [
    # 'SupplyChainSimulator',
    # 'MaterialTracker',
    # 'EventScheduler'
]

# Module metadata
__version__ = "0.1.0"
__status__ = "Development"

def get_simulation_info():
    """Get information about available simulation components"""
    return {
        'module': 'simulation',
        'version': __version__,
        'status': __status__,
        'available_components': __all__,
        'planned_components': [
            'SupplyChainSimulator',
            'MaterialTracker', 
            'EventScheduler'
        ]
    }