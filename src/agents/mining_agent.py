"""
Mining Agent - Handles raw material extraction from mining operations

This agent represents a mining operation that:
1. Extracts raw materials from mineral deposits
2. Manages mining equipment and operations
3. Tracks extraction rates and ore quality
4. Sends extracted materials to processing facilities
"""

getcwd()

import logging
from base_agent import BaseSupplyChainAgent  # Importing the base class for supply chain agents
from typing import Dict, List  # For type hinting
from datetime import datetime, timedelta  # For date and time handling
import random  # For simulating mining variability
import os 

getcwd = os.getcwd()  # Get the current working directory
print(f"Current working directory: {getcwd}")
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MiningAgent(BaseSupplyChainAgent):
    """
    Mining agent that handles extraction of raw materials from mineral deposits.
    Inherits from BaseSupplyChainAgent to get basic agent functionality,
    then adds mining-specific features like extraction rates and ore types.
    """
    
    def __init__(self, agent_id: str, name: str, mine_capacity: float, ore_types: List[str], extraction_rate: float):       
        """
        Initialize the mining agent with specific parameters.
        :param agent_id: Unique identifier for the agent
        :param name: Name of the mining operation
        :param mine_capacity: Maximum capacity of the mine in tons
        :param ore_types: List of ore types that can be extracted
        :param extraction_rate: Rate at which ore is extracted (tons per hour)
        """
        # Call the base class constructor to initialize common properties
        super().__init__(agent_id, name, mine_capacity)        
        
        # Mining operation configuration
        self.ore_types = ore_types 
        self.extraction_rate = extraction_rate
        self.mine_capacity = mine_capacity
        # Mining equipment status 
        self.equipment_status: Dict[str, str] = {
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
        
    def process_material(self, material: str = None, quantity: float = None):
        """
        Extract raw materials from the mine (this is the main mining operation)
        
        Unlike other agents that receive materials, the mining agent CREATES materials
        by extracting them from the ground. This method simulates mining operations.
        
        Args:
            material: Type of ore to extract (optional - if None, extracts based on availability)
            quantity: Amount to extract (optional - if None, uses standard extraction rate)
            
        Returns:
            Dict with extraction results and current mine status
        """
        # Determine what ore to extract
        if material and material in self.ore_types:
            target_ore = material
        else:
            # Choose ore type with highest reserves if not specified
            target_ore = max(self.ore_reserves.items(), key=lambda x: x[1])[0]
        
        # Determine extraction quantity
        if quantity:
            extraction_amount = min(quantity, self.extraction_rate)
        else:
            # Standard hourly extraction with some variability (±20%)
            base_extraction = self.extraction_rate
            variability_factor = random.uniform(0.8, 1.2) # Random factor between 0.8 and 1.2
            extraction_amount = base_extraction * variability_factor * (self.equipment_efficiency / 100) # Adjust for equipment efficiency
        
        # Check if we have enough reserves
        if self.ore_reserves[target_ore] < extraction_amount:
            available = self.ore_reserves[target_ore]
            logger.warning(f"{self.name}: Limited reserves for {target_ore}. Extracting {available} tons instead of {extraction_amount}")
            extraction_amount = available
        
        # Check mine storage capacity
        current_inventory_total = sum(self.inventory.values())
        remaining_capacity = self.mine_capacity - current_inventory_total
        
        if extraction_amount > remaining_capacity:
            logger.warning(f"{self.name}: Storage near capacity. Extracting {remaining_capacity} tons instead of {extraction_amount}")
            extraction_amount = remaining_capacity
        
        # Perform the extraction
        if extraction_amount > 0:
            # Update reserves (ore is removed from ground)
            self.ore_reserves[target_ore] -= extraction_amount
            
            # Add to mine inventory (extracted ore stored at mine)
            self.inventory[target_ore] = self.inventory.get(target_ore, 0.0) + extraction_amount 
            
            # Update tracking metrics
            self.current_shift_extraction += extraction_amount
            self.total_extracted += extraction_amount
            self.operational_hours += 1.0 # Increment operational hours for each extraction operation
            
            # Record extraction in history
            extraction_record = {
                "timestamp": datetime.now(),
                "ore_type": target_ore,
                "quantity_extracted": extraction_amount,
                "ore_quality": self.ore_quality[target_ore],
                "extraction_cost": self.extraction_costs[target_ore],
                "equipment_efficiency": self.equipment_efficiency,
                "remaining_reserves": self.ore_reserves[target_ore]
            }
            self.extraction_history.append(extraction_record)
            
            # Log successful extraction
            logger.info(f"{self.name} extracted {extraction_amount:.1f} tons of {target_ore}")
            logger.info(f"Mine inventory now: {sum(self.inventory.values()):.1f} tons total")
            
        # Return extraction results
        return {
            "status": "success" if extraction_amount > 0 else "limited_extraction",
            "extracted_material": target_ore,
            "extracted_quantity": extraction_amount,
            "ore_quality": self.ore_quality[target_ore],
            "current_inventory": self.inventory.get(target_ore, 0.0),
            "total_mine_inventory": sum(self.inventory.values()),
            "capacity_utilization_percent": round((sum(self.inventory.values()) / self.mine_capacity) * 100, 1),
            "remaining_reserves": self.ore_reserves[target_ore],
            "equipment_efficiency": self.equipment_efficiency
        }
    def create_shipment_to_processing(self, ore_type: str, quantity: float, destination_agent_id: str) -> bool:
        """
        Create a shipment of extracted ore to send to processing facilities
        
        This prepares extracted ore for transport to the next stage in the supply chain.
        
        Args:
            ore_type: Type of ore to ship
            quantity: Amount to ship (in tons)
            destination_agent_id: ID of the processing agent to receive the ore
            
        Returns:
            bool: True if shipment created successfully, False if validation failed
        """
        # Validation 1: Check if we have enough of this ore type in inventory
        if self.inventory.get(ore_type, 0) < quantity:
            available = self.inventory.get(ore_type, 0)
            logger.error(f"Cannot create shipment: Not enough {ore_type} in inventory. Requested: {quantity}, Available: {available}")
            return False
        
        # Validation 2: Check if ore type is valid for this mine
        if ore_type not in self.ore_types:
            logger.error(f"Invalid ore type: {ore_type}. This mine produces: {self.ore_types}")
            return False
        
        # Generate unique shipment ID
        shipment_id = f"Ship_{self.agent_id}_{len(self.pending_shipments) + 1:04d}"
        
        # Create shipment details record
        shipment_details = {
            "shipment_id": shipment_id,
            "ore_type": ore_type,
            "quantity": quantity,
            "destination_agent_id": destination_agent_id,
            "ore_quality": self.ore_quality[ore_type],
            "extraction_cost": self.extraction_costs[ore_type],
            "status": "pending_pickup",
            "created_at": datetime.now()
        }
        
        # Reserve inventory by removing it from available stock
        self.inventory[ore_type] -= quantity
        
        # Add to pending shipments queue
        self.pending_shipments[shipment_id] = shipment_details
        
        # Log successful shipment creation
        logger.info(f"Shipment created: {shipment_id} for {quantity} tons of {ore_type} to {destination_agent_id}")
        return True
    def process_shipments(self) -> List[Dict]:
        """
        Process pending shipments by loading them for transport
        
        This simulates loading extracted ore onto trucks/trains for delivery
        to processing facilities.
        
        Returns:
            List[Dict]: Details of all shipments that were dispatched
        """
        dispatched_shipments = []
        
        # Check if there are any shipments to process
        if not self.pending_shipments:
            logger.info("No pending shipments to process")
            return dispatched_shipments
        
        # Process all pending shipments (mines typically load everything available)
        shipment_ids = list(self.pending_shipments.keys())
        
        for shipment_id in shipment_ids:
            shipment = self.pending_shipments[shipment_id]
            
            # Update shipment status to dispatched
            shipment["status"] = "dispatched"
            shipment["dispatched_at"] = datetime.now()
            
            # Estimate transport time based on distance (simplified)
            # In real implementation, this would consider actual logistics
            transport_time = random.uniform(2, 8)  # 2-8 hours transport time
            estimated_arrival = datetime.now() + timedelta(hours=transport_time)
            shipment["estimated_arrival"] = estimated_arrival
            
            # Add to shipped materials history
            self.shipped_materials.append(dict(shipment))
            dispatched_shipments.append(dict(shipment))
            
            # Log the dispatch
            logger.info(f"Shipment {shipment_id} dispatched: {shipment['quantity']} tons {shipment['ore_type']} to {shipment['destination_agent_id']}")
        
        # Clear pending shipments (all have been dispatched)
        self.pending_shipments.clear()
        
        return dispatched_shipments
    def update_equipment_status(self, equipment: str, status: str, efficiency: float = None) -> bool:
        """
        Update the status and efficiency of mining equipment
        
        This allows operators to report equipment problems or maintenance completion.
        
        Args:
            equipment: Name of equipment (excavator, crusher, conveyor, trucks)
            status: New status (operational, maintenance, breakdown)
            efficiency: New efficiency percentage (optional)
            
        Returns:
            bool: True if update successful, False if equipment not found
        """
        if equipment not in self.equipment_status:
            logger.error(f"Unknown equipment: {equipment}. Available: {list(self.equipment_status.keys())}")
            return False
        
        # Update equipment status
        old_status = self.equipment_status[equipment]
        self.equipment_status[equipment] = status
        
        # Update efficiency if provided
        if efficiency is not None:
            self.equipment_efficiency = efficiency
        
        # Track breakdowns for metrics
        if status == "breakdown" and old_status != "breakdown":
            self.equipment_breakdowns += 1
        
        # Log equipment status change
        logger.info(f"Equipment {equipment} status changed from {old_status} to {status}")
        if efficiency:
            logger.info(f"Equipment efficiency updated to {efficiency}%")
        
        return True

    def get_mining_status(self) -> Dict:
        """
        Get comprehensive status report of the mining operation
        
        This method combines base agent status with mining-specific information
        including reserves, equipment status, and extraction performance.
        
        Returns:
            Dict: Complete status report with reserves, extraction, and equipment data
        """
        # Get basic status from parent class
        base_status = super().get_status()
        
        # Calculate current operational metrics
        total_inventory = sum(self.inventory.values())
        capacity_utilization = (total_inventory / self.mine_capacity) * 100 if self.mine_capacity else 0
        
        # Calculate extraction performance
        total_reserves = sum(self.ore_reserves.values())
        extraction_efficiency = (self.operational_hours / (self.operational_hours + self.downtime_hours) * 100) if (self.operational_hours + self.downtime_hours) > 0 else 100
        
        # Combine all status information
        mining_status = {
            **base_status,  # Include all base agent properties
            "ore_types": self.ore_types,
            "extraction": {
                "rate_tons_per_hour": self.extraction_rate,
                "current_shift_extracted": self.current_shift_extraction,
                "total_extracted": self.total_extracted,
                "daily_target": self.daily_extraction_target,
                "extraction_efficiency_percent": round(extraction_efficiency, 1)
            },
            "inventory": {
                "total_stored_tons": total_inventory,
                "capacity_utilization_percent": round(capacity_utilization, 1),
                "by_ore_type": dict(self.inventory)
            },
            "reserves": {
                "total_remaining_tons": total_reserves,
                "by_ore_type": dict(self.ore_reserves),
                "ore_quality": dict(self.ore_quality)
            },
            "equipment": {
                "status": dict(self.equipment_status),
                "overall_efficiency_percent": self.equipment_efficiency,
                "breakdowns_count": self.equipment_breakdowns,
                "operational_hours": self.operational_hours,
                "downtime_hours": self.downtime_hours
            },
            "shipments": {
                "pending_shipments": len(self.pending_shipments),
                "total_shipped": len(self.shipped_materials),
                "last_shipment": self.shipped_materials[-1] if self.shipped_materials else None
            }
        }
        
        return mining_status
def demo_mining_agent():
    """
    Demonstration function showing how to use the MiningAgent
    This function creates a mining operation, extracts materials,
    creates shipments, and demonstrates the complete workflow.
    """
    # Create a new mining operation
    AMX_mine = MiningAgent(
        "MINE_001",
        "AMX PG Mine",
        24000.0,  # 24,000 ton storage capacity
        ["Phosphorite Ore", "Gold", "Copper Ore", "Iron Ore", "Bauxite Ore"],
        1000.0  # 1000 tons per hour extraction rate
    )

    # Simulate mining operations for several hours
    logger.info("=== Starting Mining Operations ===")

    # Extract different types of ore (use smaller amounts that fit in capacity)
    AMX_mine.process_material("Phosphorite Ore", 2000)  # Extract 2000 tons of Phosphorite Ore
    AMX_mine.process_material("Gold", 1000)             # Extract 1000 tons of Gold
    AMX_mine.process_material("Copper Ore", 1500)      # Extract 1500 tons of Copper Ore
    AMX_mine.process_material("Iron Ore", 2000)         # Extract 2000 tons of Iron Ore
    AMX_mine.process_material("Bauxite Ore", 1000)     # Extract 1000 tons of Bauxite Ore

    # Show current mining status
    status = AMX_mine.get_mining_status()
    print("Current Mining Status:")
    print(f"Total extracted: {status['extraction']['total_extracted']} tons")
    print(f"Inventory: {status['inventory']['total_stored_tons']} tons stored")
    print(f"Capacity utilization: {status['inventory']['capacity_utilization_percent']}%")

    # Show what's actually in inventory before creating shipments
    print("\nCurrent Inventory by Ore Type:")
    for ore_type, quantity in AMX_mine.inventory.items():
        print(f"- {ore_type}: {quantity} tons")

    # Create shipments to processing facilities (use EXACT ore type names from inventory)
    logger.info("=== Creating Shipments ===")

    # Only create shipments for ore types that actually exist in inventory
    if "Iron Ore" in AMX_mine.inventory and AMX_mine.inventory["Iron Ore"] >= 150:
        AMX_mine.create_shipment_to_processing("Iron Ore", 150, "PROC_001")

    if "Copper Ore" in AMX_mine.inventory and AMX_mine.inventory["Copper Ore"] >= 75:
        AMX_mine.create_shipment_to_processing("Copper Ore", 75, "PROC_002")

    if "Phosphorite Ore" in AMX_mine.inventory and AMX_mine.inventory["Phosphorite Ore"] >= 200:
        AMX_mine.create_shipment_to_processing("Phosphorite Ore", 200, "PROC_003")

    if "Gold" in AMX_mine.inventory and AMX_mine.inventory["Gold"] >= 50:
        AMX_mine.create_shipment_to_processing("Gold", 50, "PROC_004")

    if "Bauxite Ore" in AMX_mine.inventory and AMX_mine.inventory["Bauxite Ore"] >= 100:
        AMX_mine.create_shipment_to_processing("Bauxite Ore", 100, "PROC_005")

    # Show pending shipments
    if AMX_mine.pending_shipments:
        print("\nPending Shipments:")
        for shipment_id, details in AMX_mine.pending_shipments.items():
            print(f"- {shipment_id}: {details['quantity']} tons {details['ore_type']} to {details['destination_agent_id']}")
    else:
        print("\nNo pending shipments created")

    # Process shipments (dispatch them)
    dispatched = AMX_mine.process_shipments()
    if dispatched:
        print(f"\nDispatched {len(dispatched)} shipments:")
        for shipment in dispatched:
            print(f"- {shipment['quantity']} tons {shipment['ore_type']} to {shipment['destination_agent_id']}")
    else:
        print("\nNo shipments were dispatched")

    # Update equipment status (simulate maintenance) - use correct equipment name
    equipment_names = list(AMX_mine.equipment_status.keys())
    if equipment_names:
        AMX_mine.update_equipment_status(equipment_names[0], "maintenance", 85.0)

    # Show final status
    final_status = AMX_mine.get_mining_status()
    print(f"\nFinal Status:")
    print(f"Equipment efficiency: {final_status['equipment']['overall_efficiency_percent']}%")
    print(f"Pending shipments: {final_status['shipments']['pending_shipments']}")
    print(f"Total shipped: {final_status['shipments']['total_shipped']}")

    # Show remaining inventory after shipments
    print(f"\nRemaining Inventory:")
    for ore_type, quantity in AMX_mine.inventory.items():
        print(f"- {ore_type}: {quantity} tons")

# Run the demo if this file is executed directly
if __name__ == "__main__":
    demo_mining_agent()