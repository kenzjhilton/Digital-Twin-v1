"""
Distribution Agent - Handles warehousing and shipping of finished products

This agent represents a distribution center that:
1. Receives finished products from manufacturing
2. Stores them in warehouse inventory
3. Creates and processes shipping orders for customers
4. Tracks deliveries and performance metrics
"""

import logging 
from base_agent import BaseSupplyChainAgent # Importing the base class for supply chain agents
from typing import Dict, List # For type hinting
from datetime import datetime, timedelta # For date and time handling

# Configure logging of agent activities
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DistributionAgent(BaseSupplyChainAgent):
    """
    Distribution agent that handles warehousing and shipping of finished products.
    Inherits from BaseSupplyChainAgent to get basic agent functionality,
    then adds distribution-specific features like shipping zones and delivery tracking.
    """
    def __init__(self, agent_id: str, name: str, warehouse_capacity: float, ship_zones: List[str]):
        """
        Initialize the distribution center
        
        Args:
            agent_id: Unique identifier (like "DIST_001")
            name: Human-readable name (like "Regional Distribution Center East")
            warehouse_capacity: Maximum storage capacity in units
            ship_zones: List of zones this center can deliver to (like ["Zone_A", "Zone_B"])
        """
        # Call the base class constructor to inherit common agent properties
        super().__init__(agent_id, name, warehouse_capacity)
        
        # Shipping configuration - zones this distribution center serves
        self.shipping_zones = ship_zones or ["Zone_A", "Zone_B", "Zone_C"]
        
        # Shipment tracking dictionaries
        self.pending_shipments: Dict[str, Dict] = {}  # Orders waiting to be dispatched
        self.active_shipments: Dict[str, Dict] = {}   # Orders currently in transit
        self.shipment_history: List[Dict] = []        # Complete record of all shipments
        
        # Warehouse management
        self.current_inventory: Dict[str, float] = {}  # Current stock levels by product type
        self.last_updated = datetime.now()             # Timestamp of last inventory update
        
        # Performance tracking metrics
        self.total_shipments = 0           # Total number of shipments created
        self.average_delivery_time = timedelta()  # Average time from dispatch to delivery
        self.shipping_accuracy = 0.0       # Percentage of successful deliveries
        self.on_time_deliveries = 0        # Count of deliveries that arrived on time
        
        # Unused variables (kept for potential future use)
        self.delivery_schedule: Dict[str, datetime] = {}  # Scheduled delivery times
        self.shipment_routes: Dict[str, str] = {}          # Route assignments for shipments
        
        # Log successful initialization
        logger.info(f"Distribution center {self.name} ready to serve zones: {self.shipping_zones}")

    def process_material(self, material: str, quantity: float):
        """
        Receive finished products from manufacturing and add them to warehouse inventory
        
        This method is called when the distribution center receives products from the
        manufacturing stage. It updates inventory levels and checks warehouse capacity.
        
        Args:
            material: Type of product (like "PG", "NAP", "DAP")
            quantity: Amount received (in units)
            
        Returns:
            Dict with processing results and current warehouse status
        """
        # Log the incoming material receipt
        logger.info(f"{self.name} receiving {quantity} units of {material}")
        
        # Update the inventory - add new quantity to existing stock (or start at 0)
        self.current_inventory[material] = self.current_inventory.get(material, 0.0) + quantity
        
        # Calculate total warehouse utilization for capacity monitoring
        total_inventory = sum(self.current_inventory.values())
        
        # Warn if warehouse is getting full (90% capacity threshold)
        if total_inventory > self.capacity * 0.9:
            logger.warning(f"{self.name} warehouse is {(total_inventory/self.warehouse_capacity)*100:.1f}% full")
        
        # Return detailed status information
        return {
            "status": "success",
            "received_material": material,
            "received_quantity": quantity,
            "current_inventory": self.current_inventory[material],
            "total_inventory": total_inventory,
            "capacity_utilization_percent": round((total_inventory / self.capacity) * 100, 1)
        }
        
    def create_shipping_order(self, material: str, quantity: float, destination: str, delivery_zone: str) -> bool:
        """
        Create a new shipping order for a customer
        
        This method validates the order (checking inventory and delivery zone),
        then creates a pending shipment that can be processed later.
        
        Args:
            material: Product type to ship
            quantity: Amount to ship
            destination: Customer/location name
            delivery_zone: Geographic zone for delivery routing
            
        Returns:
            bool: True if order created successfully, False if validation failed
        """
        # Validation 1: Check if we have enough inventory to fulfill the order
        if self.current_inventory.get(material, 0) < quantity:
            logger.error(f"Cannot fulfill order: Not enough {material} in stock. Requested: {quantity}, Available: {self.current_inventory.get(material, 0)}")
            return False
        
        # Validation 2: Check if we can deliver to the requested zone
        if delivery_zone not in self.shipping_zones:
            logger.error(f"Invalid delivery zone: {delivery_zone} not served by {self.name}")
            return False
        
        # Generate unique order ID based on current number of pending shipments
        order_id = f"ORDER_{len(self.pending_shipments) + 1:04d}"
        
        # Create shipment details record
        shipping_details = {
            "order_id": order_id,
            "material": material,
            "quantity": quantity,
            "destination": destination,
            "delivery_zone": delivery_zone,
            "status": "pending",
            "created_at": datetime.now()
        }
        
        # Reserve inventory by removing it from available stock
        self.current_inventory[material] -= quantity
        
        # Add to pending shipments queue for processing
        self.pending_shipments[order_id] = shipping_details
        
        # Update shipment counter for metrics tracking
        self.total_shipments += 1
        
        # Log successful order creation
        logger.info(f"Shipping order created: {order_id} for {quantity} {material} to {destination} in zone {delivery_zone}")
        return True

    def process_shipments(self) -> List[Dict]:
        """
        Process pending shipments by dispatching them to their routes
        
        Takes up to 5 pending shipments and moves them to active status,
        assigning routes and estimated delivery times based on delivery zones.
        
        Returns:
            List[Dict]: Details of all shipments that were dispatched
        """
        dispatched_shipments = []
        
        # Check if there are any shipments to process
        if not self.pending_shipments:
            logger.info("No pending shipments to process")
            return dispatched_shipments
        
        # Process up to 5 shipments at a time (batch processing)
        order_ids = list(self.pending_shipments.keys())[:5]
        
        for order_id in order_ids:
            shipment = self.pending_shipments[order_id]
            zone = shipment["delivery_zone"]
            
            # Route assignment based on delivery zone
            # Each zone has different delivery times and route names
            if zone == "Zone_A":
                route = "Route_A"
                delivery_hours = datetime.now() + timedelta(hours=8)
            elif zone == "Zone_B":
                route = "Route_B"
                delivery_hours = datetime.now() + timedelta(hours=12)
            elif zone == "Zone_C":
                route = "Route_C"
                delivery_hours = datetime.now() + timedelta(hours=16)
            else:
                # Fallback for unknown zones
                route = "Unknown"
                delivery_hours = datetime.now() + timedelta(hours=24)
            
            # Update shipment status to dispatched
            shipment["status"] = "dispatched"
            shipment["dispatched_at"] = datetime.now()
            shipment["estimated_delivery_time"] = delivery_hours
            shipment["route"] = route
            
            # Move shipment from pending to active tracking
            self.active_shipments[order_id] = shipment
            
            # Add to delivery schedule (for future reference)
            self.delivery_schedule[order_id] = delivery_hours
            
            # Record in shipment history for metrics
            self.shipment_history.append(dict(shipment))
            
            # Add to return list for caller
            dispatched_shipments.append(dict(shipment))
            
            # Log the dispatch action
            logger.info(f"Shipment {order_id} dispatched to {shipment['destination']} via {route} at {shipment['dispatched_at']}")
        
        # Remove processed shipments from pending queue
        for order_id in order_ids:
            del self.pending_shipments[order_id]
        
        return dispatched_shipments

    def update_delivery_schedule(self, order_id: str, delivery_time: datetime, status: str, route: str) -> bool:
        """
        Update the delivery schedule and status for an active shipment
        
        This method allows external systems or operators to update shipment
        information while it's in transit.
        
        Args:
            order_id: Unique identifier of the shipment
            delivery_time: New estimated delivery time
            status: Updated status (e.g., "delayed", "on_time")
            route: Updated route information
            
        Returns:
            bool: True if update successful, False if order not found
        """
        # Validate that the order exists in active shipments
        if order_id not in self.active_shipments:
            logger.error(f"Order {order_id} not found in active shipments")
            return False
        
        # Update the delivery schedule tracking
        self.delivery_schedule[order_id] = delivery_time
        
        # Update shipment record with new information
        self.active_shipments[order_id]["status"] = status
        self.active_shipments[order_id]["route"] = route
        
        # Log the schedule update
        logger.info(f"Delivery schedule updated for {order_id}: {status} via {route} at {delivery_time}")
        return True

    def complete_shipment(self, order_id: str) -> bool:
        """
        Mark a shipment as delivered and update performance metrics
        
        This method is called when a shipment reaches its destination.
        It calculates delivery performance and updates various metrics.
        
        Args:
            order_id: Unique identifier of the delivered shipment
            
        Returns:
            bool: True if completion processed successfully, False if order not found
        """
        # Validate that the order exists in active shipments
        if order_id not in self.active_shipments:
            logger.error(f"Order {order_id} not found in active shipments")
            return False
        
        # Get shipment details for processing
        shipment = self.active_shipments[order_id]
        
        # Mark as delivered with current timestamp
        shipment["status"] = "delivered"
        shipment["delivered_at"] = datetime.now()
        
        # Calculate actual delivery time
        delivery_duration = shipment["delivered_at"] - shipment.get("dispatched_at", shipment["delivered_at"])
        shipment["delivery_time"] = delivery_duration
        
        # Check if delivery was on time (compare with estimated delivery time)
        if shipment.get("estimated_delivery_time") and shipment["delivered_at"] <= shipment["estimated_delivery_time"]:
            self.on_time_deliveries += 1
        
        # Log the successful delivery
        logger.info(f"Shipment {order_id} delivered in {delivery_duration.total_seconds() / 3600:.1f} hours")
        
        # Add completed shipment to history
        self.shipment_history.append(dict(shipment))
        
        # Remove from active shipments (no longer in transit)
        del self.active_shipments[order_id]
        
        # Update performance metrics
        # Ensure we don't divide by zero
        self.total_shipments = max(self.total_shipments, 1)
        
        # Calculate running average of delivery times
        self.average_delivery_time = (
            (self.average_delivery_time * (self.total_shipments - 1) + delivery_duration) / self.total_shipments
        )
        
        # Calculate shipping accuracy as percentage of successful deliveries
        self.shipping_accuracy = (
            sum(1 for s in self.shipment_history if s.get("status") == "delivered") / len(self.shipment_history)
        ) * 100
        
        # Log updated performance metrics
        logger.info(f"Metrics updated: Avg delivery {self.average_delivery_time}, Accuracy {self.shipping_accuracy:.1f}%")
        return True

    def get_distribution_status(self) -> Dict:
        """
        Get comprehensive status report of the distribution center
        
        This method combines base agent status with distribution-specific
        information including inventory, shipments, and performance metrics.
        
        Returns:
            Dict: Complete status report with warehouse, shipment, and performance data
        """
        # Get basic status from parent class (agent_id, name, connections, etc.)
        base_status = super().get_status()
        
        # Calculate current warehouse metrics
        total_inventory = sum(self.current_inventory.values())
        capacity_utilization = (total_inventory / self.capacity) * 100 if self.capacity else 0
        
        # Calculate shipping performance metrics
        delivered_shipments = sum(1 for s in self.shipment_history if s.get("status") == "delivered")
        total_shipments = len(self.shipment_history)
        shipping_accuracy = (delivered_shipments / total_shipments * 100) if total_shipments else 0
        on_time_delivery_percent = (self.on_time_deliveries / delivered_shipments * 100) if delivered_shipments else 0
        
        # Combine all status information into comprehensive report
        distribution_status = {
            **base_status,  # Include all base agent properties
            "shipping_zones": self.shipping_zones,
            "warehouse": {
                "total_inventory": total_inventory,
                "capacity_utilization_percent": round(capacity_utilization, 1),
                "products_in_stock": len(self.current_inventory),
            },
            "shipments": {
                "pending_orders": len(self.pending_shipments),
                "active_shipments": len(self.active_shipments),
                "total_shipments": self.total_shipments,
                "average_delivery_time_hours": round(self.average_delivery_time.total_seconds() / 3600, 2)
                    if self.total_shipments else 0,
            },
            "performance": {
                "shipping_accuracy_percent": round(shipping_accuracy, 1),
                "on_time_delivery_percent": round(on_time_delivery_percent, 1),
            }
        }
        return distribution_status

def demo_distribution_agent():
    """
    Demonstration function showing how to use the DistributionAgent
    
    This function creates a distribution center, processes materials,
    creates shipping orders, and demonstrates the complete workflow.
    """
    # Create a new distribution center
    dist_centre = DistributionAgent(
        "DIST_001",
        "Regional Distribution Center East",
        10000.0,  # 10,000 unit warehouse capacity
        ["Zone_A", "Zone_B", "Zone_C"]
    )
    
    # Simulate receiving finished products from manufacturing
    dist_centre.process_material("PG", 500)   # Phosphate Granules
    dist_centre.process_material("NAP", 500)  # Nitrogen-Ammonium-Phosphate
    dist_centre.process_material("DAP", 500)  # Diammonium Phosphate
    
    # Create customer shipping orders
    dist_centre.create_shipping_order("PG", 100, "Customer A", "Zone_A")
    dist_centre.create_shipping_order("NAP", 200, "Customer B", "Zone_B")
    dist_centre.create_shipping_order("DAP", 300, "Customer C", "Zone_C")
    
    # Process the pending shipments (dispatch them)
    logger.info("Processing shipments...")
    dispatched = dist_centre.process_shipments()
    
    # Show current status
    status = dist_centre.get_distribution_status()
    print("Current Distribution Status:")
    print(status)
    
    # Complete the first shipment if any were dispatched
    if dispatched:
        dist_centre.complete_shipment(dispatched[0]["order_id"]) 
    
    # Show updated status after delivery
    updated_status = dist_centre.get_distribution_status()
    print("\nUpdated Status after first delivery:")
    print(updated_status)

# Run the demo if this file is executed directly
if __name__ == "__main__":
    demo_distribution_agent()