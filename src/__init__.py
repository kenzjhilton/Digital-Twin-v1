"""
Supply Chain Reconstruction System
==================================

A comprehensive Python-based supply chain reconstruction and simulation system
that enables end-to-end tracking and analysis of materials flow from raw
extraction to customer delivery.

This package provides:
- Agent-based supply chain modeling (Mining, Processing, Manufacturing, Distribution, Retail)
- Real-time simulation and material tracking
- Operator input integration at decision points
- Data loading from Excel/CSV sources
- Performance analytics and reporting
- Interactive dashboard capabilities

Usage:
    from src import SupplyChainSimulator, agents
    from src.simulation import MaterialTracker
    from src.visualization import Dashboard

Example:
    # Quick start simulation
    simulator = SupplyChainSimulator()
    results = simulator.run_full_simulation()
    
    # Or use individual agents
    mine = agents.MiningAgent("MINE_001", "Main Mine", 10000, ["Iron Ore"], 500)
    processor = agents.ProcessingAgent("PROC_001", "Steel Plant", 5000, ["smelting"], recipes)

Author: Kenz
Project: Supply Chain Reconstruction
Version: 1.0.0
"""

import sys
import logging
from pathlib import Path

# Package metadata
__version__ = "1.0.0"
__author__ = "Kenz"
__email__ = "your.email@example.com"
__description__ = "Supply Chain Reconstruction and Simulation System"
__license__ = "MIT"

# Add current directory to Python path for imports
_current_dir = Path(__file__).parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))

# Configure package-level logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Core imports - agents package
try:
    from . import agents
    from .agents import (
        BaseSupplyChainAgent,
        MiningAgent,
        ProcessingAgent,
        ManufacturingAgent,
        DistributionAgent,
        RetailAgent
    )
    _agents_available = True
except ImportError as e:
    logging.warning(f"Agents module import failed: {e}")
    agents = None
    _agents_available = False

# Simulation imports
try:
    from . import simulation
    # Import specific simulation components when they're implemented
    # from .simulation import SupplyChainSimulator, MaterialTracker, EventScheduler
    _simulation_available = True
except ImportError as e:
    logging.warning(f"Simulation module import failed: {e}")
    simulation = None
    _simulation_available = False

# Data handling imports
try:
    from . import data
    # from .data import DataLoader, DataProcessor, SchemaValidator
    _data_available = True
except ImportError as e:
    logging.warning(f"Data module import failed: {e}")
    data = None
    _data_available = False

# API imports
try:
    from . import api
    # from .api import InputHandler, QueryEngine, endpoints
    _api_available = True
except ImportError as e:
    logging.warning(f"API module import failed: {e}")
    api = None
    _api_available = False

# Utilities imports
try:
    from . import utils
    # from .utils import config, logging_setup, validators
    _utils_available = True
except ImportError as e:
    logging.warning(f"Utils module import failed: {e}")
    utils = None
    _utils_available = False

# Visualization imports
try:
    from . import visualization
    # from .visualization import Dashboard, reporting
    _visualization_available = True
except ImportError as e:
    logging.warning(f"Visualization module import failed: {e}")
    visualization = None
    _visualization_available = False

# Import the main simulator from agents folder if available
try:
    from .agents.sim import SupplyChainSimulator
    _main_simulator_available = True
except ImportError as e:
    logging.warning(f"Main simulator import failed: {e}")
    SupplyChainSimulator = None
    _main_simulator_available = False

# Import orchestrator if available
try:
    from .agents.SC_orchestrator import SupplyChainOrchestrator, MaterialTrace
    _orchestrator_available = True
except ImportError as e:
    logging.warning(f"Orchestrator import failed: {e}")
    SupplyChainOrchestrator = None
    MaterialTrace = None
    _orchestrator_available = False

# Define what gets imported with "from src import *"
__all__ = [
    # Core classes
    'SupplyChainSimulator',
    'SupplyChainOrchestrator', 
    'MaterialTrace',
    
    # Agent classes
    'BaseSupplyChainAgent',
    'MiningAgent',
    'ProcessingAgent', 
    'ManufacturingAgent',
    'DistributionAgent',
    'RetailAgent',
    
    # Modules
    'agents',
    'simulation',
    'data',
    'api',
    'utils',
    'visualization',
    
    # Package info
    '__version__',
    '__author__',
    '__description__',
]

# Remove None entries from __all__
__all__ = [item for item in __all__ if globals().get(item) is not None]

def get_package_info():
    """
    Get comprehensive package information and availability status
    
    Returns:
        dict: Package information including available modules and versions
    """
    return {
        'package_info': {
            'name': 'Supply Chain Reconstruction System',
            'version': __version__,
            'author': __author__,
            'description': __description__,
            'license': __license__
        },
        'module_availability': {
            'agents': _agents_available,
            'simulation': _simulation_available, 
            'data': _data_available,
            'api': _api_available,
            'utils': _utils_available,
            'visualization': _visualization_available,
            'main_simulator': _main_simulator_available,
            'orchestrator': _orchestrator_available
        },
        'available_agents': [
            'BaseSupplyChainAgent',
            'MiningAgent', 
            'ProcessingAgent',
            'ManufacturingAgent',
            'DistributionAgent',
            'RetailAgent'
        ] if _agents_available else [],
        'core_classes': [
            cls for cls in ['SupplyChainSimulator', 'SupplyChainOrchestrator']
            if globals().get(cls) is not None
        ]
    }

def create_simple_simulation(ore_quantity=1000):
    """
    Quick helper function to create and run a basic simulation
    
    Args:
        ore_quantity (float): Amount of raw ore to inject (tons)
        
    Returns:
        dict: Simulation results
    """
    if not _main_simulator_available:
        raise ImportError("SupplyChainSimulator not available. Check agents.sim module.")
    
    simulator = SupplyChainSimulator()
    return simulator.run_full_simulation()

def get_available_agents():
    """
    Get list of available agent classes
    
    Returns:
        dict: Available agent classes with their descriptions
    """
    if not _agents_available:
        return {}
    
    return {
        'MiningAgent': 'Handles raw material extraction from mining operations',
        'ProcessingAgent': 'Transforms raw materials into refined products', 
        'ManufacturingAgent': 'Creates finished products from processed materials',
        'DistributionAgent': 'Manages warehousing and shipping of finished products',
        'RetailAgent': 'Handles final customer sales and delivery'
    }

def setup_logging(level=logging.INFO):
    """
    Set up package-wide logging configuration
    
    Args:
        level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/supply_chain.log') if Path('logs').exists() else logging.NullHandler()
        ]
    )

# Auto-setup logging if logs directory exists
if Path('logs').exists():
    setup_logging()

# Package initialization message
def _print_welcome():
    """Print welcome message when package is imported"""
    available_modules = sum([
        _agents_available,
        _simulation_available,
        _main_simulator_available,
        _orchestrator_available
    ])
    
    print(f"🏭 Supply Chain Reconstruction System v{__version__}")
    print(f"📦 {available_modules}/6 modules available")
    
    if _main_simulator_available:
        print("✅ Ready to run simulations!")
        print("   Quick start: from src import create_simple_simulation")
    else:
        print("⚠️  Main simulator not available - check module imports")

# Print welcome message on import (comment out for production)
# _print_welcome()

# Export configuration for different use cases
class Config:
    """Package configuration settings"""
    
    # Default simulation parameters
    DEFAULT_ORE_QUANTITY = 1000
    DEFAULT_PROCESSING_EFFICIENCY = 0.85
    DEFAULT_MANUFACTURING_QUALITY = "standard"
    
    # File paths
    DATA_DIR = Path("data")
    CONFIG_DIR = Path("config") 
    LOGS_DIR = Path("logs")
    EXPORTS_DIR = Path("data/exports")
    
    # Agent defaults
    AGENT_DEFAULTS = {
        'mining': {
            'capacity': 10000,
            'extraction_rate': 500,
            'ore_types': ['Phosphorite Ore']
        },
        'processing': {
            'capacity': 5000,
            'methods': ['chemical_processing']
        },
        'manufacturing': {
            'capacity': 3000,
            'lines': ['chemical_production']
        },
        'distribution': {
            'capacity': 15000,
            'zones': ['Zone_A', 'Zone_B', 'Zone_C']
        },
        'retail': {
            'capacity': 8000,
            'channels': ['online', 'physical_store']
        }
    }

# Make Config available at package level
config = Config()