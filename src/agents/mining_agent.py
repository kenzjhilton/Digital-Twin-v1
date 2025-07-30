"""
Mining Agent - Handles raw material extraction from mining operations

This agent represents a mining operation that:
1. Extracts raw materials from mineral deposits
2. Manages mining equipment and operations
3. Tracks extraction rates and ore quality
4. Sends extracted materials to processing facilities
"""

import logging
from base_agent import BaseSupplyChainAgent  # Importing the base class for supply chain agents
from typing import Dict, List  # For type hinting
from datetime import datetime, timedelta  # For date and time handling
import random  # For simulating mining variability

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MiningAgent(BaseSupplyChainAgent):
    """
    Mining agent that handles extraction of raw materials from mineral deposits.
    Inherits from BaseSupplyChainAgent to get basic agent functionality,
    then adds mining-specific features like extraction rates and ore types.
    """
    
    def __init__(self, agent_id: str, name: str, mine_capacity: int, ore_types: List[str], extraction_rate: float):
        """
        Initialize the mining agent with specific parameters.

        :param agent_id: Unique identifier for the agent
        :param name: Name of the mining operation
        :param mine_capacity: Maximum capacity of the mine in tons
        :param ore_types: List of ore types that can be extracted
        :param extraction_rate: Rate at which ore is extracted (tons per hour)
        """
        # Call the base class constructor to initialize common properties
        super().__init__(agent_id, name)
        
        # Initialize mining-specific properties
        
        # Mining operation configuration
        self.ore_types = ore_types 
        self.extraction_rate = extraction_rate
        self.mine_capacity = mine_capacity
        # Mining equipment status 
        self.equipment_status = Dict[str, str]{
            "Drilling Equipment": "Operational",
            "Excavation Equipment": "Operational",
            "Transport Equipment": "Operational",
            "Crushing Equipment": "Operational",
            "Monitoring Equipment": "Operational",
            "Safety Equipment": "Operational",
            "Maintenance Equipment": "Operational",
            "Storage Facilities": "Operational",
        }
        self.equipment_efficiency = 100.0  # Percentage efficiency
        
        # Extraction tracking
        self.extraction_history: List[Dict]= []  # List to track extraction history
        self.daily_extraction_target: Dict[str, float] = self.extraction_rate * 24 # Daily extraction totals
        self.current_shift_extraction: float = 0.0 # Current shift extraction total
        self.total_extracted: float = 0.0  # Total extracted ore
        self.last_extraction_time: datetime = datetime.now() # Last extraction timestamp
        
        # Ore quality and reserves tracking
        self.ore_reserves: Dict[str, float] = {}  # Remaining reserves by ore type
        self.ore_quality: Dict[str, float] = {}   # Quality grades by ore type
        self.extraction_costs: Dict[str, float] = {}  # Cost per ton by ore type
        
        # Initialize ore reserves and quality
        for ore in self.ore_types:
            self.ore_reserves[ore] = random.uniform(1000, 5000) # Random reserves between 1000 and 5000 tons
            self.ore_quality[ore] = random.uniform(0.5, 1.0) # Random quality between 0.5 and 1.0
            self.extraction_costs[ore] = random.uniform(10, 50)  # Random cost per ton between $10 and $50
        
        # Performance metrics
        self.operational_hours = 24.0 # Total operational hours
        self.downtime_hours = 8.0 # Scheduled downtime for maintenance
        self.equipment_breakdowns = 3 # Number of equipment breakdowns in the last month
        # Maintenance tracking
        self.last_maintenance = datetime.now() - timedelta(days=30)  # Last maintenance date 30 days ago
        self.next_maintenance_due = self.last_maintenance + timedelta(days=30) # Next maintenance due in 30 days 
        self.maintenance_history: List[Dict] = [] # List to track maintenance history
        self.maintenance_costs: Dict[str, float] = {} # Costs associated with maintenance 
        self.maintenance_costs["Drilling Equipment"] = random.uniform(500, 2000)  # Random cost between $500 and $2000
        self.maintenance_costs["Excavation Equipment"] = random.uniform(500, 2000)  # Random cost between $500 and $2000
        self.maintenance_costs["Transport Equipment"] = random.uniform(500, 2000)  # Random cost between $500 and $2000
        self.maintenance_costs["Crushing Equipment"] = random.uniform(500, 2000)  # Random cost between $500 and $2000
        self.maintenance_costs["Monitoring Equipment"] = random.uniform(500, 2000)  # Random cost between $500 and $2000
        self.maintenance_costs["Safety Equipment"] = random.uniform(500, 2000)  # Random cost between $500 and $2000
        self.maintenance_costs["Maintenance Equipment"] = random.uniform(500, 2000)  # Random cost between $500 and $2000  
        self.maintenance_costs["Storage Facilities"] = random.uniform(500, 2000)  # Random cost between $500 and $2000
        
        # Material Output tracking - this will be used to track what materials are sent downstream
        self.pending_shipments: Dict[str, Dict] = {}  # Pending shipments by ore type 
        self.shipped_materials: List[Dict] = []       # History of materials sent downstream
        self.shipment_costs: Dict[str, float] = {}    # Costs associated with shipments
        
        # Log the initialization
        self.created_at = datetime.now()  # When the agent was created
        self.updated_at = self.created_at
        logger.info(f"Initialized Mining Agent: {self.name} (ID: {self.agent_id}) with capacity {self.mine_capacity} tons and extraction rate {self.extraction_rate} tons/hour.")
        logger.info(f"Ore types available: {self.ore_types}")
        logger.info(f"Initial ore reserves: {self.ore_reserves}")
        logger.info(f"Initial ore quality: {self.ore_quality}")
        logger.info(f"Initial extraction costs: {self.extraction_costs}")
        
    def process_material(self, material: str, quantity: float = 0.0):
        """Extract raw materials from the mine (this is the main mining operation)
        
        Unlike other agents that receive materials, the mining agent CREATES materials
        by extracting them from the ground. This method simulates mining operations.
        
        Args:
            material: Type of ore to extract (optional - if None, extracts based on availability)
            quantity: Amount to extract (optional - if None, uses standard extraction rate)
            
        Returns:
            Dict with extraction results and current mine status
        """
        # Check if the material is valid
        if material and material not in self.ore_types:
            logger.error(f"Invalid material type: {material}. Available types: {self.ore_types}")
            return {"status": "error", "message": f"Invalid material type: {material}"}
        else:material = material or random.choice(self.ore_types)
        # Determine quantity to extract
        if quantity:
        extraction_amount = min(quantity, self.extraction_rate)
        