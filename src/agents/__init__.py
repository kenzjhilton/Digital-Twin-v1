"""
Supply Chain Agents Package

This package contains all the supply chain agents for the reconstruction system.
Each agent represents a different stage in the supply chain process.

Agents:
- BaseSupplyChainAgent: Abstract base class for all agents
- MiningAgent: Handles raw material extraction
- ProcessingAgent: Transforms raw materials into refined products
- ManufacturingAgent: Creates finished products from processed materials
- DistributionAgent: Manages warehousing and shipping
- RetailAgent: Handles final sales and customer delivery

Usage:
    from agents import MiningAgent, ProcessingAgent, DistributionAgent
    
    # Create agents
    mine = MiningAgent("MINE_001", "Iron Mine", 5000, ["Iron Ore"], 100)
    processor = ProcessingAgent("PROC_001", "Steel Plant", 1000, ["smelting"], recipes)
    distributor = DistributionAgent("DIST_001", "Regional Center", 2000, ["Zone_A"])
"""

# Import all agent classes to make them available at package level
from base_agent import BaseSupplyChainAgent
from mining_agent import MiningAgent
from processing_agent import ProcessingAgent
from distribution_agent import DistributionAgent

# These will be available once you create them
try:
    from .manufacturing_agent import ManufacturingAgent
except ImportError:
    ManufacturingAgent = None
    
try:
    from .retail_agent import RetailAgent
except ImportError:
    RetailAgent = None

# Package metadata
__version__ = "0.1.0"
__author__ = "Kenz"
__description__ = "Supply Chain Reconstruction Agents"

# Define what gets imported with "from agents import *"
__all__ = [
    "BaseSupplyChainAgent",
    "MiningAgent", 
    "ProcessingAgent",
    "DistributionAgent",
    "ManufacturingAgent",  # Will be None until you create it
    "RetailAgent",         # Will be None until you create it
]

# Agent registry for tracking all available agent types
AGENT_TYPES = {
    "mining": MiningAgent,
    "processing": ProcessingAgent,
    "distribution": DistributionAgent,
    "manufacturing": ManufacturingAgent,  # Will be None initially
    "retail": RetailAgent,                # Will be None initially
}

# Remove None entries from the registry
AGENT_TYPES = {k: v for k, v in AGENT_TYPES.items() if v is not None}

def get_available_agent_types():
    """
    Return a list of currently available agent types
    
    Returns:
        List[str]: List of agent type names that are available
    """
    return list(AGENT_TYPES.keys())

def create_agent(agent_type: str, *args, **kwargs):
    """
    Factory function to create agents by type name
    
    Args:
        agent_type: Type of agent to create ('mining', 'processing', etc.)
        *args, **kwargs: Arguments to pass to the agent constructor
        
    Returns:
        Agent instance of the specified type
        
    Raises:
        ValueError: If agent_type is not recognized
    """
    if agent_type not in AGENT_TYPES:
        available = ", ".join(get_available_agent_types())
        raise ValueError(f"Unknown agent type '{agent_type}'. Available types: {available}")
    
    agent_class = AGENT_TYPES[agent_type]
    return agent_class(*args, **kwargs)

def get_agent_info():
    """
    Get information about all available agent types
    
    Returns:
        Dict: Information about each agent type
    """
    info = {}
    for agent_type, agent_class in AGENT_TYPES.items():
        if agent_class:
            info[agent_type] = {
                "class_name": agent_class.__name__,
                "description": agent_class.__doc__.split('\n')[0] if agent_class.__doc__ else "No description",
                "available": True
            }
        else:
            info[agent_type] = {
                "class_name": f"{agent_type.title()}Agent",
                "description": "Not yet implemented",
                "available": False
            }
    return info

# Logging setup for the package
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())