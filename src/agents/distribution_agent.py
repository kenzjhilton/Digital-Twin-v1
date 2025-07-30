import logging
from base_agent import BaseSupplyChainAgent
from typing import Dict, List
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DistributionAgent(BaseSupplyChainAgent):
    """
    Distribution agent that handles warehousing and shipping of finished products.
    """
    def __init__(self, agent_id: str, name: str, warehouse_capacity: float, ship_zones: List[str]):
        super().__init__(agent_id, name, warehouse_capacity)
        self.shipping_zones = ship_zones or ["Zone_A", "Zone_B", "Zone_C"]
        self.pending_shipments: Dict[str, Dict] = {}
        self.active_shipments: Dict[str, Dict] = {}
        self.delivery_schedule: Dict[str, datetime] = {}
        self.warehouse_capacity = warehouse_capacity
        self.current_inventory: Dict[str, float] = {}
        self.last_updated = datetime.now()
        self.shipment_history: List[Dict] = []
        self.shipment_routes: Dict[str, str] = {}
        self.total_shipments = 0
        self.average_delivery_time = timedelta()
        self.shipping_accuracy = 0.0
        self.on_time_deliveries = 0

        logger.info(f"Distribution center {self.name} ready to serve zones: {self.shipping_zones}")

    def process_material(self, material: str, quantity: float):
        logger.info(f"{self.name} receiving {quantity} units of {material}")
        self.current_inventory[material] = self.current_inventory.get(material, 0.0) + quantity
        total_inventory = sum(self.current_inventory.values())
        if total_inventory > self.warehouse_capacity * 0.9:
            logger.warning(f"{self.name} warehouse is {(total_inventory/self.warehouse_capacity)*100:.1f}% full")
        return {
            "status": "success",
            "received_material": material,
            "received_quantity": quantity,
            "current_inventory": self.current_inventory[material],
            "total_inventory": total_inventory,
            "capacity_utilization_percent": round((total_inventory / self.warehouse_capacity) * 100, 1)
        }

    def create_shipping_order(self, material: str, quantity: float, destination: str, delivery_zone: str) -> bool:
        if self.current_inventory.get(material, 0) < quantity:
            logger.error(f"Cannot fulfill order: Not enough {material} in stock. Requested: {quantity}, Available: {self.current_inventory.get(material, 0)}")
            return False
        if delivery_zone not in self.shipping_zones:
            logger.error(f"Invalid delivery zone: {delivery_zone} not served by {self.name}")
            return False
        order_id = f"ORDER_{len(self.pending_shipments) + 1:04d}"
        shipping_details = {
            "order_id": order_id,
            "material": material,
            "quantity": quantity,
            "destination": destination,
            "delivery_zone": delivery_zone,
            "status": "pending",
            "created_at": datetime.now()
        }
        self.current_inventory[material] -= quantity
        self.pending_shipments[order_id] = shipping_details
        self.total_shipments += 1
        logger.info(f"Shipping order created: {order_id} for {quantity} {material} to {destination} in zone {delivery_zone}")
        return True

    def process_shipments(self) -> List[Dict]:
        dispatched_shipments = []
        if not self.pending_shipments:
            logger.info("No pending shipments to process")
            return dispatched_shipments
        order_ids = list(self.pending_shipments.keys())[:5]
        for order_id in order_ids:
            shipment = self.pending_shipments[order_id]
            zone = shipment["delivery_zone"]
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
                route = "Unknown"
                delivery_hours = datetime.now() + timedelta(hours=24)
            shipment["status"] = "dispatched"
            shipment["dispatched_at"] = datetime.now()
            shipment["estimated_delivery_time"] = delivery_hours
            shipment["route"] = route
            self.active_shipments[order_id] = shipment
            self.delivery_schedule[order_id] = delivery_hours
            self.shipment_history.append(dict(shipment))
            dispatched_shipments.append(dict(shipment))
            logger.info(f"Shipment {order_id} dispatched to {shipment['destination']} via {route} at {shipment['dispatched_at']}")
        for order_id in order_ids:
            del self.pending_shipments[order_id]
        return dispatched_shipments

    def update_delivery_schedule(self, order_id: str, delivery_time: datetime, status: str, route: str) -> bool:
        if order_id not in self.active_shipments:
            logger.error(f"Order {order_id} not found in active shipments")
            return False
        self.delivery_schedule[order_id] = delivery_time
        self.active_shipments[order_id]["status"] = status
        self.active_shipments[order_id]["route"] = route
        logger.info(f"Delivery schedule updated for {order_id}: {status} via {route} at {delivery_time}")
        return True

    def complete_shipment(self, order_id: str) -> bool:
        if order_id not in self.active_shipments:
            logger.error(f"Order {order_id} not found in active shipments")
            return False
        shipment = self.active_shipments[order_id]
        shipment["status"] = "delivered"
        shipment["delivered_at"] = datetime.now()
        delivery_duration = shipment["delivered_at"] - shipment.get("dispatched_at", shipment["delivered_at"])
        shipment["delivery_time"] = delivery_duration
        # On-time delivery check
        if shipment.get("estimated_delivery_time") and shipment["delivered_at"] <= shipment["estimated_delivery_time"]:
            self.on_time_deliveries += 1
        logger.info(f"Shipment {order_id} delivered in {delivery_duration.total_seconds() / 3600:.1f} hours")
        self.shipment_history.append(dict(shipment))
        del self.active_shipments[order_id]
        self.total_shipments = max(self.total_shipments, 1)
        self.average_delivery_time = (
            (self.average_delivery_time * (self.total_shipments - 1) + delivery_duration) / self.total_shipments
        )
        self.shipping_accuracy = (
            sum(1 for s in self.shipment_history if s.get("status") == "delivered") / len(self.shipment_history)
        ) * 100
        logger.info(f"Metrics updated: Avg delivery {self.average_delivery_time}, Accuracy {self.shipping_accuracy:.1f}%")
        return True

    def get_distribution_status(self) -> Dict:
        base_status = super().get_status()
        total_inventory = sum(self.current_inventory.values())
        capacity_utilization = (total_inventory / self.warehouse_capacity) * 100 if self.warehouse_capacity else 0
        delivered_shipments = sum(1 for s in self.shipment_history if s.get("status") == "delivered")
        total_shipments = len(self.shipment_history)
        shipping_accuracy = (delivered_shipments / total_shipments * 100) if total_shipments else 0
        on_time_delivery_percent = (self.on_time_deliveries / delivered_shipments * 100) if delivered_shipments else 0
        distribution_status = {
            **base_status,
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
    dist_centre = DistributionAgent(
        "DIST_001",
        "Regional Distribution Center East",
        10000.0,
        ["Zone_A", "Zone_B", "Zone_C"]
    )
    dist_centre.process_material("PG", 500)
    dist_centre.process_material("NAP", 500)
    dist_centre.process_material("DAP", 500)
    dist_centre.create_shipping_order("PG", 100, "Customer A", "Zone_A")
    dist_centre.create_shipping_order("NAP", 200, "Customer B", "Zone_B")
    dist_centre.create_shipping_order("DAP", 300, "Customer C", "Zone_C")
    dispatched = dist_centre.process_shipments()
    status = dist_centre.get_distribution_status()
    print(status)
    if dispatched:
        dist_centre.complete_shipment(dispatched[0]["order_id"])
    updated_status = dist_centre.get_distribution_status()
    print(updated_status)

if __name__ == "__main__":
    demo_distribution_agent()