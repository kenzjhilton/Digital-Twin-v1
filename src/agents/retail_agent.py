"""
Retail Agent - Final Customer Sales and Delivery

This agent represents retail operations that handle the final stage of the supply chain:
1. Receives finished products from distribution centers
2. Manages retail inventory and store operations
3. Processes customer orders and sales transactions
4. Handles final delivery to end customers
5. Tracks customer satisfaction and sales performance
6. Manages pricing, promotions, and market demand

The retail agent completes the end-to-end supply chain from raw materials to customer delivery.
"""

import logging
from base_agent import BaseSupplyChainAgent
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetailAgent(BaseSupplyChainAgent):
    """
    Retail agent that handles final customer sales and delivery operations.
    
    This agent represents retail stores, sales centers, or customer-facing operations
    that sell finished products directly to end customers.
    """
    
    def __init__(self, agent_id: str, name: str, store_capacity: float,
                 sales_channels: List[str], customer_zones: List[str]):
        """
        Initialize the retail operation
        
        Args:
            agent_id: Unique identifier (like "RETAIL_001")
            name: Human-readable name (like "Regional Retail Center")
            store_capacity: Maximum inventory capacity (units)
            sales_channels: List of available sales channels
                Examples: ["online", "physical_store", "wholesale", "direct_sales"]
            customer_zones: List of customer zones served
                Examples: ["residential", "commercial", "industrial", "agricultural"]
        """
        # Initialize base agent properties
        super().__init__(agent_id, name, store_capacity)
        
        # Retail configuration
        self.sales_channels = sales_channels
        self.customer_zones = customer_zones
        self.store_capacity = store_capacity
        
        # Product inventory and pricing
        self.product_inventory: Dict[str, float] = {}  # Products available for sale
        self.product_prices: Dict[str, float] = {}     # Current prices by product
        self.price_history: Dict[str, List[Dict]] = {} # Price change history
        self.product_demand: Dict[str, float] = {}     # Current demand levels
        
        # Sales operations tracking
        self.active_orders: Dict[str, Dict] = {}       # Orders being processed
        self.pending_orders: List[Dict] = []           # Orders waiting for fulfillment
        self.sales_history: List[Dict] = []            # Completed sales records
        self.customer_database: Dict[str, Dict] = {}   # Customer information
        
        # Performance metrics
        self.total_sales_revenue: float = 0.0
        self.total_units_sold: float = 0.0
        self.average_order_value: float = 0.0
        self.customer_satisfaction_score: float = 0.0
        self.inventory_turnover_rate: float = 0.0
        
        # Sales channel performance
        self.channel_performance: Dict[str, Dict] = {}
        for channel in sales_channels:
            self.channel_performance[channel] = {
                "total_sales": 0.0,
                "total_orders": 0,
                "average_order_value": 0.0,
                "customer_count": 0
            }
        
        # Customer zone analytics
        self.zone_analytics: Dict[str, Dict] = {}
        for zone in customer_zones:
            self.zone_analytics[zone] = {
                "total_customers": 0,
                "total_sales": 0.0,
                "preferred_products": {},
                "satisfaction_score": 0.0
            }
        
        # Delivery and logistics
        self.delivery_methods: List[str] = ["standard_delivery", "express_delivery", "pickup", "bulk_delivery"]
        self.delivery_tracking: Dict[str, Dict] = {}
        self.delivery_performance: Dict[str, float] = {
            "on_time_delivery_rate": 95.0,
            "delivery_satisfaction": 4.2,
            "average_delivery_time_hours": 24.0
        }
        
        # Marketing and promotions
        self.active_promotions: Dict[str, Dict] = {}
        self.seasonal_demand_multipliers: Dict[str, float] = {}
        
        logger.info(f"Retail Agent {self.name} initialized")
        logger.info(f"Sales channels: {self.sales_channels}")
        logger.info(f"Customer zones: {self.customer_zones}")
    
    def receive_shipment_from_distribution(self, shipment_data: Dict) -> bool:
        """
        Receive a shipment of finished products from distribution centers
        
        Args:
            shipment_data: Dictionary with shipment details from distribution agent
                Expected format: {
                    "order_id": "ORDER_0001",
                    "material": "Bagged_Fertilizer",
                    "quantity": 100.0,
                    "destination": "Retail Store A",
                    "delivery_zone": "Zone_A",
                    "status": "delivered"
                }
        
        Returns:
            bool: True if shipment received successfully, False if rejected
        """
        product_type = shipment_data.get("material")
        quantity = shipment_data.get("quantity", 0.0)
        
        # Validation 1: Check store capacity
        current_inventory = sum(self.product_inventory.values())
        if current_inventory + quantity > self.store_capacity:
            available_space = self.store_capacity - current_inventory
            logger.warning(f"{self.name}: Limited storage space. Can only accept {available_space} units of {quantity} requested")
            
            if available_space <= 0:
                logger.error(f"{self.name}: Store inventory full. Rejecting shipment.")
                return False
            
            quantity = available_space
        
        # Accept the shipment
        self.product_inventory[product_type] = self.product_inventory.get(product_type, 0.0) + quantity
        
        # Set initial pricing if this is a new product
        if product_type not in self.product_prices:
            self.set_initial_product_price(product_type)
        
        # Initialize demand tracking for new products
        if product_type not in self.product_demand:
            self.product_demand[product_type] = random.uniform(0.3, 0.8)  # Random initial demand
        
        logger.info(f"{self.name} received {quantity} units of {product_type}")
        logger.info(f"Store inventory now: {sum(self.product_inventory.values()):.1f} units total")
        
        return True
    
    def set_initial_product_price(self, product_type: str):
        """
        Set initial pricing for a new product based on product type
        """
        # Base pricing by product category
        base_prices = {
            "Bagged_Fertilizer": 25.0,
            "Steel_Beams": 150.0,
            "Steel_Products": 120.0,
            "Chemical_Products": 80.0,
            "Industrial_Components": 200.0
        }
        
        # Find base price or use default
        base_price = base_prices.get(product_type, 50.0)
        
        # Add some pricing variability (±15%)
        price_variation = random.uniform(0.85, 1.15)
        initial_price = base_price * price_variation
        
        self.product_prices[product_type] = round(initial_price, 2)
        
        # Initialize price history
        self.price_history[product_type] = [{
            "price": initial_price,
            "date": datetime.now(),
            "reason": "initial_pricing"
        }]
        
        logger.info(f"Set initial price for {product_type}: ${initial_price:.2f}")
    
    def get_required_inputs(self, order_details: Dict) -> Dict[str, any]:
        """
        Define what operator inputs are needed for processing customer orders
        
        Args:
            order_details: Details about the customer order
            
        Returns:
            Dictionary of required operator inputs with descriptions
        """
        product_type = order_details.get("product_type", "")
        quantity = order_details.get("quantity", 1.0)
        customer_zone = order_details.get("customer_zone", "")
        
        required_inputs = {
            "sales_channel": {
                "type": "choice",
                "options": self.sales_channels,
                "description": "Which sales channel should handle this order?",
                "required": True
            },
            "delivery_method": {
                "type": "choice",
                "options": self.delivery_methods,
                "description": "How should this order be delivered?",
                "default": "standard_delivery",
                "required": True
            },
            "pricing_strategy": {
                "type": "choice",
                "options": ["standard", "promotional", "bulk_discount", "premium"],
                "description": "What pricing strategy should be applied?",
                "default": "standard",
                "required": True
            },
            "priority_level": {
                "type": "choice",
                "options": ["standard", "high", "urgent"],
                "description": "Order processing priority level",
                "default": "standard",
                "required": True
            },
            "customer_type": {
                "type": "choice",
                "options": ["new_customer", "returning_customer", "vip_customer", "wholesale_customer"],
                "description": "What type of customer is this?",
                "default": "returning_customer",
                "required": True
            }
        }
        
        # Add zone-specific options
        if customer_zone in self.customer_zones:
            required_inputs["local_delivery_options"] = {
                "type": "choice",
                "options": ["same_day", "next_day", "scheduled"],
                "description": f"Delivery options for {customer_zone}",
                "default": "next_day",
                "required": True
            }
        
        # Add product-specific options
        if "Fertilizer" in product_type:
            required_inputs["application_season"] = {
                "type": "choice",
                "options": ["spring", "summer", "fall", "winter"],
                "description": "Intended application season (affects pricing)",
                "default": "spring",
                "required": False
            }
        
        return required_inputs
    
    def process_material(self, order_details: Dict, operator_inputs: Dict[str, any] = None):
        """
        Process a customer order (this is the main sales operation)
        
        Args:
            order_details: Customer order information
            operator_inputs: Dictionary with operator's sales decisions
            
        Returns:
            Dictionary with order processing results
        """
        # Use default inputs if none provided
        if operator_inputs is None:
            operator_inputs = {
                "sales_channel": self.sales_channels[0] if self.sales_channels else "direct_sales",
                "delivery_method": "standard_delivery",
                "pricing_strategy": "standard",
                "priority_level": "standard",
                "customer_type": "returning_customer"
            }
        
        # Extract order details
        product_type = order_details.get("product_type", "")
        quantity = order_details.get("quantity", 1.0)
        customer_id = order_details.get("customer_id", f"CUST_{random.randint(1000, 9999)}")
        customer_zone = order_details.get("customer_zone", self.customer_zones[0] if self.customer_zones else "general")
        
        # Extract operator decisions
        sales_channel = operator_inputs.get("sales_channel")
        delivery_method = operator_inputs.get("delivery_method", "standard_delivery")
        pricing_strategy = operator_inputs.get("pricing_strategy", "standard")
        priority_level = operator_inputs.get("priority_level", "standard")
        customer_type = operator_inputs.get("customer_type", "returning_customer")
        
        # Validation 1: Check product availability
        available_quantity = self.product_inventory.get(product_type, 0.0)
        if available_quantity < quantity:
            return {
                "status": "error",
                "message": f"Insufficient inventory. Available: {available_quantity}, Requested: {quantity}"
            }
        
        # Validation 2: Check if product has pricing
        if product_type not in self.product_prices:
            return {
                "status": "error",
                "message": f"No pricing available for {product_type}"
            }
        
        # Calculate pricing
        base_price = self.product_prices[product_type]
        final_price = self.calculate_order_price(base_price, quantity, pricing_strategy, customer_type)
        total_amount = final_price * quantity
        
        # Generate order ID
        order_id = f"ORDER_{self.agent_id}_{len(self.sales_history) + 1:04d}"
        
        # Reserve inventory
        self.product_inventory[product_type] -= quantity
        
        # Create order record
        order_record = {
            "order_id": order_id,
            "customer_id": customer_id,
            "customer_zone": customer_zone,
            "customer_type": customer_type,
            "product_type": product_type,
            "quantity": quantity,
            "unit_price": final_price,
            "total_amount": total_amount,
            "sales_channel": sales_channel,
            "delivery_method": delivery_method,
            "priority_level": priority_level,
            "operator_inputs": dict(operator_inputs),
            "status": "confirmed",
            "order_date": datetime.now(),
            "estimated_delivery": self.calculate_delivery_time(delivery_method, customer_zone)
        }
        
        # Add to active orders
        self.active_orders[order_id] = order_record
        
        # Update customer database
        self.update_customer_record(customer_id, customer_zone, customer_type, total_amount)
        
        # Update performance metrics
        self.update_sales_metrics(sales_channel, customer_zone, total_amount)
        
        logger.info(f"Order {order_id} processed: {quantity} units {product_type} for ${total_amount:.2f}")
        
        return {
            "status": "success",
            "order_id": order_id,
            "total_amount": total_amount,
            "unit_price": final_price,
            "estimated_delivery": order_record["estimated_delivery"],
            "confirmation_details": {
                "customer_id": customer_id,
                "product": product_type,
                "quantity": quantity,
                "delivery_method": delivery_method,
                "sales_channel": sales_channel
            }
        }
    
    def calculate_order_price(self, base_price: float, quantity: float, pricing_strategy: str, customer_type: str) -> float:
        """
        Calculate final pricing based on strategy and customer type
        """
        price = base_price
        
        # Apply pricing strategy
        strategy_multipliers = {
            "standard": 1.0,
            "promotional": 0.85,
            "bulk_discount": 0.90 if quantity > 50 else 1.0,
            "premium": 1.15
        }
        price *= strategy_multipliers.get(pricing_strategy, 1.0)
        
        # Apply customer type discounts
        customer_multipliers = {
            "new_customer": 0.95,  # 5% discount for new customers
            "returning_customer": 1.0,
            "vip_customer": 0.90,  # 10% discount for VIP
            "wholesale_customer": 0.80  # 20% discount for wholesale
        }
        price *= customer_multipliers.get(customer_type, 1.0)
        
        # Apply bulk quantity discounts
        if quantity > 100:
            price *= 0.95  # 5% discount for large orders
        elif quantity > 500:
            price *= 0.90  # 10% discount for very large orders
        
        return round(price, 2)
    
    def calculate_delivery_time(self, delivery_method: str, customer_zone: str) -> datetime:
        """
        Calculate estimated delivery time based on method and zone
        """
        base_hours = {
            "standard_delivery": 48,
            "express_delivery": 24,
            "pickup": 2,
            "bulk_delivery": 72
        }
        
        hours = base_hours.get(delivery_method, 48)
        
        # Add zone-specific delays
        zone_delays = {
            "residential": 0,
            "commercial": 4,
            "industrial": 8,
            "agricultural": 12
        }
        hours += zone_delays.get(customer_zone, 0)
        
        return datetime.now() + timedelta(hours=hours)
    
    def update_customer_record(self, customer_id: str, customer_zone: str, customer_type: str, order_value: float):
        """
        Update customer database with new order information
        """
        if customer_id not in self.customer_database:
            self.customer_database[customer_id] = {
                "customer_id": customer_id,
                "customer_zone": customer_zone,
                "customer_type": customer_type,
                "total_orders": 0,
                "total_spent": 0.0,
                "average_order_value": 0.0,
                "first_order_date": datetime.now(),
                "last_order_date": datetime.now(),
                "satisfaction_score": 4.0  # Default satisfaction
            }
        
        customer = self.customer_database[customer_id]
        customer["total_orders"] += 1
        customer["total_spent"] += order_value
        customer["average_order_value"] = customer["total_spent"] / customer["total_orders"]
        customer["last_order_date"] = datetime.now()
    
    def update_sales_metrics(self, sales_channel: str, customer_zone: str, order_value: float):
        """
        Update performance metrics for sales channels and customer zones
        """
        # Update channel performance
        if sales_channel in self.channel_performance:
            channel = self.channel_performance[sales_channel]
            channel["total_sales"] += order_value
            channel["total_orders"] += 1
            channel["average_order_value"] = channel["total_sales"] / channel["total_orders"]
        
        # Update zone analytics
        if customer_zone in self.zone_analytics:
            zone = self.zone_analytics[customer_zone]
            zone["total_sales"] += order_value
    
    def complete_delivery(self, order_id: str, delivery_feedback: Dict = None) -> bool:
        """
        Mark an order as delivered and update performance metrics
        
        Args:
            order_id: Unique identifier of the delivered order
            delivery_feedback: Optional customer feedback about delivery
            
        Returns:
            bool: True if completion processed successfully
        """
        if order_id not in self.active_orders:
            logger.error(f"Order {order_id} not found in active orders")
            return False
        
        order = self.active_orders[order_id]
        
        # Mark as delivered
        order["status"] = "delivered"
        order["delivery_date"] = datetime.now()
        order["delivery_feedback"] = delivery_feedback or {}
        
        # Calculate delivery performance
        estimated_delivery = order["estimated_delivery"]
        actual_delivery = order["delivery_date"]
        on_time = actual_delivery <= estimated_delivery
        
        order["delivered_on_time"] = on_time
        
        # Update metrics
        self.total_sales_revenue += order["total_amount"]
        self.total_units_sold += order["quantity"]
        
        # Calculate new average order value
        total_orders = len(self.sales_history) + 1
        self.average_order_value = self.total_sales_revenue / total_orders
        
        # Move to sales history
        self.sales_history.append(dict(order))
        del self.active_orders[order_id]
        
        # Update customer satisfaction if feedback provided
        if delivery_feedback and "satisfaction_rating" in delivery_feedback:
            customer_id = order["customer_id"]
            if customer_id in self.customer_database:
                old_score = self.customer_database[customer_id]["satisfaction_score"]
                new_rating = delivery_feedback["satisfaction_rating"]
                # Weighted average with existing score
                self.customer_database[customer_id]["satisfaction_score"] = (old_score * 0.8 + new_rating * 0.2)
        
        logger.info(f"Order {order_id} delivered successfully. On time: {on_time}")
        return True
    
    def get_retail_status(self) -> Dict:
        """
        Get comprehensive status report of the retail operation
        
        Returns:
            Dictionary with complete retail operation status
        """
        base_status = super().get_status()
        
        # Calculate inventory metrics
        total_inventory = sum(self.product_inventory.values())
        inventory_utilization = (total_inventory / self.store_capacity) * 100 if self.store_capacity else 0
        
        # Calculate sales performance
        total_orders = len(self.sales_history)
        delivered_orders = sum(1 for order in self.sales_history if order.get("status") == "delivered")
        order_fulfillment_rate = (delivered_orders / total_orders * 100) if total_orders else 100
        
        # Calculate customer metrics
        total_customers = len(self.customer_database)
        avg_customer_satisfaction = (
            sum(customer["satisfaction_score"] for customer in self.customer_database.values()) / total_customers
            if total_customers else 0
        )
        
        retail_status = {
            **base_status,
            "sales_channels": self.sales_channels,
            "customer_zones": self.customer_zones,
            "inventory": {
                "total_units": total_inventory,
                "capacity_utilization_percent": round(inventory_utilization, 1),
                "products_available": len(self.product_inventory),
                "by_product": dict(self.product_inventory)
            },
            "sales_performance": {
                "total_revenue": round(self.total_sales_revenue, 2),
                "total_units_sold": self.total_units_sold,
                "total_orders": total_orders,
                "average_order_value": round(self.average_order_value, 2),
                "order_fulfillment_rate_percent": round(order_fulfillment_rate, 1)
            },
            "customer_metrics": {
                "total_customers": total_customers,
                "average_satisfaction_score": round(avg_customer_satisfaction, 2),
                "repeat_customer_rate_percent": 0  # Could be calculated based on order history
            },
            "current_operations": {
                "active_orders": len(self.active_orders),
                "pending_orders": len(self.pending_orders)
            },
            "channel_performance": dict(self.channel_performance),
            "zone_analytics": dict(self.zone_analytics),
            "pricing": {
                "products_with_pricing": len(self.product_prices),
                "current_prices": dict(self.product_prices)
            }
        }
        
        return retail_status

def demo_retail_agent():
    """
    Demonstration showing how the RetailAgent works with distribution agent outputs
    """
    # Create retail operation
    retailer = RetailAgent(
        "RETAIL_001",
        "Regional Retail Center",
        2000.0,  # 2,000 unit capacity
        ["online", "physical_store", "wholesale"],
        ["residential", "commercial", "agricultural"]
    )
    
    # Simulate receiving shipment from distribution
    distribution_shipment = {
        "order_id": "ORDER_0001",
        "material": "Bagged_Fertilizer",
        "quantity": 500.0,
        "destination": "Regional Retail Center",
        "delivery_zone": "Zone_A",
        "status": "delivered"
    }
    
    # Receive the shipment
    retailer.receive_shipment_from_distribution(distribution_shipment)
    
    # Simulate customer order
    customer_order = {
        "product_type": "Bagged_Fertilizer",
        "quantity": 25.0,
        "customer_id": "CUST_1001",
        "customer_zone": "agricultural"
    }
    
    # Get operator input requirements
    required_inputs = retailer.get_required_inputs(customer_order)
    print("Retail operator inputs required:")
    for input_name, input_spec in required_inputs.items():
        print(f"- {input_name}: {input_spec.get('description', 'No description')}")
    
    # Process customer order with operator inputs
    operator_decisions = {
        "sales_channel": "physical_store",
        "delivery_method": "standard_delivery",
        "pricing_strategy": "standard",
        "priority_level": "standard",
        "customer_type": "returning_customer",
        "application_season": "spring"
    }
    
    result = retailer.process_material(customer_order, operator_decisions)
    print(f"\nOrder processing result: {result}")
    
    if result["status"] == "success":
        # Simulate delivery completion
        delivery_feedback = {
            "satisfaction_rating": 4.5,
            "delivery_notes": "On time delivery, good product quality"
        }
        
        retailer.complete_delivery(result["order_id"], delivery_feedback)
        print(f"Order {result['order_id']} delivered successfully")
    
    # Show retail status
    status = retailer.get_retail_status()
    print(f"\nRetail Operation Status:")
    print(f"Total revenue: ${status['sales_performance']['total_revenue']}")
    print(f"Units sold: {status['sales_performance']['total_units_sold']}")
    print(f"Customer satisfaction: {status['customer_metrics']['average_satisfaction_score']}/5.0")
    print(f"Inventory utilization: {status['inventory']['capacity_utilization_percent']}%")

if __name__ == "__main__":
    demo_retail_agent()