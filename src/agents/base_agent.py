"""
Simple Base Supply Chain Agent - Starting Version

This file contains the foundation class that all supply chain agents inherit from.
The "blueprint" that defines what every agent can do.
"""

# Import statements - these give us access to Python features we need
from abc import ABC, abstractmethod  # ABC = Abstract Base Class (template for other classes)
from datetime import datetime        # For timestamps
from typing import Dict, List       # For type hints (makes code clearer)


# BaseAgent class - the blueprint for all supply chain agents
class BaseAgent(ABC):
    """Base class for all supply chain agents.
    Defines the basic structure and methods that all agents must implement.
    """
    def __init__(self, agent_id: str, name: str, capacity: float):
        """Initialize the agent with an ID and name.#
        Args:
            agent_id: Unique identifier (like "MINE_001")
            name: Human-readable name (like "Iron Ore Mine Alpha")
            capacity: Maximum amount this agent can hold (in kg)
            """
        # Initialize the agent with basic 4 properties
        self.agent_id = agent_id # Unique identifier for the agent
        self.name = name   # Human-readable name for the agent
        self.capacity = capacity  # Capacity of the agent (e.g., how much it can handle)
        # Initialize an empty inventory
        self.inventory: Dict[str, float] = {} # Holds items and their quantities
        self.connections: List[str] = []  # List of other agents this agent can connect with
        # Initialize the last updated timestamp
        self.created_at = datetime.now()  # When the agent was created
        # Sanity check 
        print(f"Agent {self.name} initialized with ID {self.agent_id} and capacity {self.capacity} kg.")
        
        
        