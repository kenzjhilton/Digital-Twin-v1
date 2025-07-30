"""
Simple Base Supply Chain Agent - Starting Version

This file contains the foundation class that all supply chain agents inherit from.
Think of it as the "blueprint" that defines what every agent can do.
"""

# Import statements - these give us access to Python features we need
from abc import ABC, abstractmethod  # ABC = Abstract Base Class (template for other classes)
from datetime import datetime        # For timestamps
from typing import Dict, List       # For type hints (makes code clearer)


class BaseSupplyChainAgent(ABC):
    """
    Base class for all supply chain agents
    
    This is an abstract class - you can't create it directly.
    Instead, specific agents (MiningAgent, ProcessingAgent, etc.) inherit from this.
    
    Think of this as the "common DNA" that all agents share.
    """
    
    def __init__(self, agent_id: str, name: str, capacity: float):
        """
        Initialize the agent with an ID and name
        
        Args:
            agent_id: Unique identifier (like "MINE_001")
            name: Human-readable name (like "Iron Ore Mine Alpha")
            capacity: Maximum amount this agent can hold (in kg)
        """
        # Initialize the agent with basic properties
        self.agent_id = agent_id  # Unique identifier for the agent
        self.name = name          # Human-readable name for the agent
        self.capacity = capacity  # Capacity of the agent (e.g., how much it can handle)
        
        # Initialize an empty inventory
        self.inventory: Dict[str, float] = {}  # Holds items and their quantities
        self.connections: List[str] = []       # List of other agents this agent can connect with
        
        # Initialize the last updated timestamp
        self.created_at = datetime.now()  # When the agent was created
        
        # Sanity check
        print(f"Agent {self.name} initialized with ID {self.agent_id} and capacity {self.capacity} kg.")
    
    def add_connection(self, agent_id: str):
        """
        Connect this agent to another agent in the supply chain
        
        For example: Mining Agent → Processing Agent → Manufacturing Agent
        
        Args:
            agent_id: The ID of the agent to connect to (like "PROC_001")
        """
        # Add the agent ID to our connections list
        self.connections.append(agent_id)
        print(f"Agent {self.name} connected to agent {agent_id}.")
    
    @abstractmethod
    def process_material(self, material: str, quantity: float):
        """
        Process materials - MUST be implemented by each specific agent type
        
        This is abstract because each agent processes materials differently:
        - Mining agent: extracts raw ore
        - Processing agent: refines ore into metal
        - Manufacturing agent: turns metal into products
        
        Args:
            material: The material to process
            quantity: Amount to process
            
        Returns:
            The processed material (format depends on agent type)
        """
        pass  # This will be implemented by specific agent classes
    
    def get_status(self):
        """
        Get basic status information about this agent
        
        Returns:
            Dictionary with current agent status
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "inventory": self.inventory,
            "capacity": self.capacity,
            "created_at": self.created_at,
            "connections": self.connections
        }