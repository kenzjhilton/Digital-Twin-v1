"""
Manufacturing Agent - Maadan Model Integration

This agent represents an industrial manufacturing facility that transforms
processed materials from mining operations into finished industrial products.

Designed for the Maadan model, this agent handles:
1. Receiving processed materials from processing facilities
2. Manufacturing finished industrial products and components
3. Managing production lines and manufacturing equipment
4. Quality control and product certification
5. Inventory management of finished goods
6. Shipping finished products to distribution centers

The agent supports various manufacturing processes typical in industrial
mining-based manufacturing operations.
"""

import logging
from base_agent import BaseSupplyChainAgent
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ManufacturingAgent(BaseSupplyChainAgent):
    """
    Manufacturing agent for Maadan model integration.
    
    This agent takes processed materials and manufactures them into finished
    industrial products through various production processes.
    """
    
    def __init__(self, agent_id: str, name: str, manufacturing_capacity: float,
                production_lines: List[str], manufacturing_recipes: Dict[str, Dict]):
        """
        Initialize the manufacturing facility
        
        Args:
            agent_id: Unique identifier (like "MFG_001")
            name: Human-readable name (like "Industrial Manufacturing Plant")
            manufacturing_capacity: Maximum production throughput per hour (units/hour)
            production_lines: List of available production line types
            manufacturing_recipes: Dict defining how to manufacture products
                Example: {
                    "PG_to_Fertilizer": {
                        "input_materials": {"PG": 1.0, "additives": 0.1},
                        "output_product": "Bagged_Fertilizer",
                        "output_quantity_ratio": 0.9,
                        "production_time_hours": 2.0,
                        "energy_cost_per_unit": 15.0,
                        "required_line": "chemical_production",
                        "quality_requirements": {"min_purity": 0.85}
                    }
                }
        """
        # Initialize base agent properties
        super().__init__(agent_id, name, manufacturing_capacity)
        
        # Manufacturing configuration
        self.production_lines = production_lines
        self.manufacturing_recipes = manufacturing_recipes
        self.manufacturing_capacity = manufacturing_capacity
        
        # Production line status and efficiency
        self.production_line_status: Dict[str, str] = {}
        self.production_line_efficiency: Dict[str, float] = {}
        
        # Initialize production lines
        for line in production_lines:
            self.production_line_status[line] = "operational"
            self.production_line_efficiency[line] = random.uniform(85.0, 98.0)
        
        # Material and product storage
        self.raw_material_inventory: Dict[str, float] = {}  # Processed materials from processing agents
        self.finished_goods_inventory: Dict[str, float] = {}  # Manufactured products
        self.material_quality_records: Dict[str, float] = {}  # Quality tracking
        self.product_certifications: Dict[str, Dict] = {}  # Product quality certifications
        
        # Manufacturing operations tracking
        self.active_production_jobs: Dict[str, Dict] = {}  # Currently running production
        self.production_queue: List[Dict] = []  # Jobs waiting to start
        self.production_history: List[Dict] = []  # Completed production records
        
        # Performance metrics
        self.total_products_manufactured: float = 0.0
        self.total_production_time: timedelta = timedelta()
        self.average_production_efficiency: float = 0.0
        self.manufacturing_costs: float = 0.0
        self.quality_control_passes: int = 0
        self.quality_control_failures: int = 0
        
        # Shipment management for outgoing products
        self.pending_product_shipments: Dict[str, Dict] = {}
        self.shipped_products: List[Dict] = []
        
        # Storage capacity allocation (60% raw materials, 40% finished goods)
        self.raw_material_capacity = self.capacity * 0.6
        self.finished_goods_capacity = self.capacity * 0.4
        
        logger.info(f"Manufacturing Agent {self.name} initialized with {len(production_lines)} production lines")
        logger.info(f"Available manufacturing recipes: {list(manufacturing_recipes.keys())}")
    
    def receive_shipment_from_processing(self, shipment_data: Dict) -> bool:
        """
        Receive a shipment of processed materials from processing facilities
        
        Args:
            shipment_data: Dictionary with shipment details from processing agent
                Expected format: {
                    "shipment_id": "Ship_PROC_001_0001",
                    "material_type": "PG",
                    "quantity": 100.0,
                    "destination_agent_id": "MFG_001",
                    "material_quality": 0.90,
                    "processing_cost": 25.50,
                    "status": "dispatched",
                    "created_at": datetime_object
                }
        
        Returns:
            bool: True if shipment received successfully, False if rejected
        """
        material_type = shipment_data.get("material_type")
        quantity = shipment_data.get("quantity", 0.0)
        quality = shipment_data.get("material_quality", 1.0)
        
        # Validation 1: Check if we can manufacture products from this material
        can_manufacture = any(
            material_type in recipe.get("input_materials", {})
            for recipe in self.manufacturing_recipes.values()
        )
        
        if not can_manufacture:
            logger.error(f"{self.name}: Cannot manufacture products from {material_type}. No recipes available.")
            return False
        
        # Validation 2: Check raw material storage capacity
        current_raw_storage = sum(self.raw_material_inventory.values())
        if current_raw_storage + quantity > self.raw_material_capacity:
            available_space = self.raw_material_capacity - current_raw_storage
            logger.warning(f"{self.name}: Limited storage space. Can only accept {available_space} units of {quantity} requested")
            
            if available_space <= 0:
                logger.error(f"{self.name}: Raw material storage full. Rejecting shipment.")
                return False
            
            quantity = available_space
        
        # Accept the shipment
        self.raw_material_inventory[material_type] = self.raw_material_inventory.get(material_type, 0.0) + quantity
        self.material_quality_records[material_type] = quality
        
        logger.info(f"{self.name} received {quantity} units of {material_type} (Quality: {quality:.2f})")
        logger.info(f"Raw material inventory now: {sum(self.raw_material_inventory.values()):.1f} units total")
        
        return True
    
    def get_required_inputs(self, recipe_name: str, quantity: float) -> Dict[str, any]:
        """
        Define what operator inputs are needed for manufacturing with this recipe
        
        Args:
            recipe_name: Name of the manufacturing recipe to use
            quantity: Planned production quantity
            
        Returns:
            Dictionary of required operator inputs with descriptions
        """
        if recipe_name not in self.manufacturing_recipes:
            return {"error": f"No manufacturing recipe available for {recipe_name}"}
        
        recipe = self.manufacturing_recipes[recipe_name]
        
        # Create input requirements based on the recipe
        required_inputs = {
            "production_priority": {
                "type": "choice",
                "options": ["urgent", "normal", "batch_production"],
                "description": "Production scheduling priority",
                "default": "normal",
                "required": True
            },
            "quality_standard": {
                "type": "choice",
                "options": ["standard", "premium", "industrial_grade"],
                "description": "Quality standard for manufactured products",
                "default": "standard",
                "required": True
            },
            "batch_size": {
                "type": "float",
                "min": 1.0,
                "max": min(quantity, self.manufacturing_capacity),
                "description": f"Production batch size (Available materials for {quantity} units)",
                "default": min(quantity, self.manufacturing_capacity * 0.7),
                "required": True
            },
            "quality_control_level": {
                "type": "choice",
                "options": ["basic", "standard", "enhanced"],
                "description": "Level of quality control testing to perform",
                "default": "standard",
                "required": True
            }
        }
        
        # Add recipe-specific inputs based on product type
        output_product = recipe.get("output_product", "")
        if "Fertilizer" in output_product:
            required_inputs["nutrient_blend"] = {
                "type": "choice",
                "options": ["standard_npk", "high_phosphorus", "balanced_mix"],
                "description": "Fertilizer nutrient blend configuration",
                "default": "standard_npk",
                "required": True
            }
        elif "Steel" in output_product:
            required_inputs["alloy_composition"] = {
                "type": "choice",
                "options": ["carbon_steel", "stainless_steel", "alloy_steel"],
                "description": "Steel alloy composition specification",
                "default": "carbon_steel",
                "required": True
            }
        
        return required_inputs
    
    def process_material(self, recipe_name: str, operator_inputs: Dict[str, any] = None):
        """
        Manufacture products using the specified recipe and operator inputs
        
        This is the core manufacturing method that creates finished products
        from processed raw materials.
        
        Args:
            recipe_name: Name of the manufacturing recipe to execute
            operator_inputs: Dictionary with operator's manufacturing decisions
            
        Returns:
            Dictionary with manufacturing results and job status
        """
        # Use default inputs if none provided
        if operator_inputs is None:
            operator_inputs = {
                "production_priority": "normal",
                "quality_standard": "standard",
                "batch_size": self.manufacturing_capacity * 0.5,
                "quality_control_level": "standard"
            }
        
        # Validation 1: Check if recipe exists
        if recipe_name not in self.manufacturing_recipes:
            return {
                "status": "error",
                "message": f"Unknown manufacturing recipe: {recipe_name}"
            }
        
        recipe = self.manufacturing_recipes[recipe_name]
        
        # Extract operator decisions
        batch_size = operator_inputs.get("batch_size", 100.0)
        priority = operator_inputs.get("production_priority", "normal")
        quality_standard = operator_inputs.get("quality_standard", "standard")
        qc_level = operator_inputs.get("quality_control_level", "standard")
        
        # Validation 2: Check if we have enough raw materials
        input_materials = recipe["input_materials"]
        for material, ratio in input_materials.items():
            required_quantity = batch_size * ratio
            available = self.raw_material_inventory.get(material, 0.0)
            
            if available < required_quantity:
                return {
                    "status": "error",
                    "message": f"Insufficient {material}. Required: {required_quantity}, Available: {available}"
                }
        
        # Validation 3: Check production line availability
        required_line = recipe.get("required_line")
        if required_line and self.production_line_status.get(required_line) != "operational":
            return {
                "status": "error",
                "message": f"Production line {required_line} is not operational"
            }
        
        # Create manufacturing job
        job_id = f"MFG_{self.agent_id}_{len(self.production_history) + 1:04d}"
        
        # Calculate production parameters
        base_output_ratio = recipe["output_quantity_ratio"]
        base_production_time = recipe["production_time_hours"]
        energy_cost = recipe["energy_cost_per_unit"]
        
        # Adjust for production line efficiency and quality standard
        line_efficiency = self.production_line_efficiency.get(required_line, 100.0) / 100.0
        actual_output_ratio = base_output_ratio * line_efficiency
        
        # Quality standard affects production time and cost
        quality_multipliers = {"standard": 1.0, "premium": 1.3, "industrial_grade": 0.8}
        quality_multiplier = quality_multipliers.get(quality_standard, 1.0)
        
        adjusted_production_time = base_production_time * quality_multiplier
        adjusted_energy_cost = energy_cost * quality_multiplier
        
        # Calculate expected outputs
        expected_output_quantity = batch_size * actual_output_ratio
        output_product = recipe["output_product"]
        
        # Reserve raw materials
        for material, ratio in input_materials.items():
            required_quantity = batch_size * ratio
            self.raw_material_inventory[material] -= required_quantity
        
        # Create production job record
        production_job = {
            "job_id": job_id,
            "recipe_name": recipe_name,
            "input_materials": {mat: batch_size * ratio for mat, ratio in input_materials.items()},
            "expected_output_product": output_product,
            "expected_output_quantity": expected_output_quantity,
            "quality_standard": quality_standard,
            "production_time_hours": adjusted_production_time,
            "energy_cost": adjusted_energy_cost * batch_size,
            "priority": priority,
            "quality_control_level": qc_level,
            "operator_inputs": dict(operator_inputs),
            "status": "queued",
            "created_at": datetime.now(),
            "started_at": None,
            "completed_at": None
        }
        
        # Add to production queue
        self.production_queue.append(production_job)
        
        # Sort queue by priority
        priority_order = {"urgent": 0, "normal": 1, "batch_production": 2}
        self.production_queue.sort(key=lambda job: priority_order.get(job["priority"], 1))
        
        logger.info(f"Manufacturing job {job_id} created: {batch_size} units → {expected_output_quantity:.1f} units {output_product}")
        
        return {
            "status": "success",
            "job_id": job_id,
            "queued_position": len(self.production_queue),
            "expected_output": {
                "product": output_product,
                "quantity": expected_output_quantity,
                "quality": quality_standard
            },
            "estimated_completion": datetime.now() + timedelta(hours=adjusted_production_time)
        }
    
    def run_manufacturing_operations(self) -> List[Dict]:
        """
        Execute queued manufacturing jobs and complete active ones
        
        Returns:
            List of completed manufacturing jobs with their results
        """
        completed_jobs = []
        current_time = datetime.now()
        
        # Complete active jobs that have finished
        finished_job_ids = []
        for job_id, job in self.active_production_jobs.items():
            estimated_completion = job["started_at"] + timedelta(hours=job["production_time_hours"])
            
            if current_time >= estimated_completion:
                # Job is complete - produce the finished products
                output_product = job["expected_output_product"]
                output_quantity = job["expected_output_quantity"]
                quality_standard = job["quality_standard"]
                qc_level = job["quality_control_level"]
                
                # Simulate quality control process
                qc_success = self.perform_quality_control(output_product, quality_standard, qc_level)
                
                if qc_success:
                    # Add some realistic variability to output (+/- 3%)
                    actual_output = output_quantity * random.uniform(0.97, 1.03)
                    
                    # Add to finished goods inventory
                    self.finished_goods_inventory[output_product] = (
                        self.finished_goods_inventory.get(output_product, 0.0) + actual_output
                    )
                    
                    # Record product certification
                    self.product_certifications[f"{output_product}_{job_id}"] = {
                        "quality_standard": quality_standard,
                        "certification_date": current_time,
                        "batch_id": job_id,
                        "quantity": actual_output
                    }
                    
                    job["status"] = "completed"
                    job["actual_output_quantity"] = actual_output
                    self.quality_control_passes += 1
                    
                    logger.info(f"Manufacturing job {job_id} completed: produced {actual_output:.1f} units {output_product}")
                else:
                    # Quality control failed - rework or discard
                    job["status"] = "quality_control_failed"
                    job["actual_output_quantity"] = 0.0
                    self.quality_control_failures += 1
                    
                    logger.warning(f"Manufacturing job {job_id} failed quality control")
                
                # Update job completion details
                job["completed_at"] = current_time
                
                # Update performance metrics
                self.total_products_manufactured += job.get("actual_output_quantity", 0.0)
                self.manufacturing_costs += job["energy_cost"]
                
                # Move to history
                self.production_history.append(dict(job))
                completed_jobs.append(dict(job))
                finished_job_ids.append(job_id)
        
        # Remove completed jobs from active list
        for job_id in finished_job_ids:
            del self.active_production_jobs[job_id]
        
        # Start new jobs if production line capacity is available
        max_concurrent_jobs = len(self.production_lines)
        while (len(self.active_production_jobs) < max_concurrent_jobs and 
               self.production_queue):
            
            # Get next job from queue
            next_job = self.production_queue.pop(0)
            
            # Check if required production line is available
            required_line = self.manufacturing_recipes[next_job["recipe_name"]].get("required_line")
            line_busy = any(
                self.manufacturing_recipes[job["recipe_name"]].get("required_line") == required_line
                for job in self.active_production_jobs.values()
            )
            
            if not line_busy and self.production_line_status.get(required_line) == "operational":
                # Start the job
                next_job["status"] = "manufacturing"
                next_job["started_at"] = current_time
                self.active_production_jobs[next_job["job_id"]] = next_job
                
                logger.info(f"Started manufacturing job {next_job['job_id']}: {next_job['recipe_name']}")
            else:
                # Put job back at front of queue if production line not available
                self.production_queue.insert(0, next_job)
                break
        
        return completed_jobs
    
    def perform_quality_control(self, product: str, quality_standard: str, qc_level: str) -> bool:
        """
        Simulate quality control process for manufactured products
        
        Returns:
            bool: True if product passes quality control, False if it fails
        """
        # Base quality control success rates
        base_rates = {"standard": 0.95, "premium": 0.90, "industrial_grade": 0.98}
        qc_multipliers = {"basic": 0.95, "standard": 1.0, "enhanced": 1.05}
        
        base_rate = base_rates.get(quality_standard, 0.95)
        qc_multiplier = qc_multipliers.get(qc_level, 1.0)
        
        success_rate = min(base_rate * qc_multiplier, 0.99)  # Cap at 99%
        
        return random.random() < success_rate
    
    def create_shipment_to_distribution(self, product_type: str, quantity: float, destination_agent_id: str) -> bool:
        """
        Create a shipment of finished products to send to distribution centers
        
        Args:
            product_type: Type of finished product to ship
            quantity: Amount to ship (units)
            destination_agent_id: ID of receiving distribution agent
            
        Returns:
            bool: True if shipment created successfully, False if validation failed
        """
        # Validation: Check if we have enough finished product
        available = self.finished_goods_inventory.get(product_type, 0.0)
        if available < quantity:
            logger.error(f"Cannot ship {quantity} units {product_type}. Available: {available}")
            return False
        
        # Generate shipment ID
        shipment_id = f"Ship_{self.agent_id}_{len(self.pending_product_shipments) + 1:04d}"
        
        # Create shipment record
        shipment_data = {
            "shipment_id": shipment_id,
            "product_type": product_type,
            "quantity": quantity,
            "destination_agent_id": destination_agent_id,
            "manufacturing_cost": self.manufacturing_costs / max(self.total_products_manufactured, 1),
            "status": "pending_pickup",
            "created_at": datetime.now()
        }
        
        # Reserve finished goods
        self.finished_goods_inventory[product_type] -= quantity
        
        # Add to pending shipments
        self.pending_product_shipments[shipment_id] = shipment_data
        
        logger.info(f"Created shipment {shipment_id}: {quantity} units {product_type} to {destination_agent_id}")
        return True
    
    def get_manufacturing_status(self) -> Dict:
        """
        Get comprehensive status report of the manufacturing facility
        
        Returns:
            Dictionary with complete manufacturing facility status
        """
        base_status = super().get_status()
        
        # Calculate storage utilization
        raw_storage_used = sum(self.raw_material_inventory.values())
        finished_storage_used = sum(self.finished_goods_inventory.values())
        
        # Calculate efficiency metrics
        avg_efficiency = (
            sum(self.production_line_efficiency.values()) / len(self.production_line_efficiency)
            if self.production_line_efficiency else 100.0
        )
        
        # Calculate quality metrics
        total_qc_tests = self.quality_control_passes + self.quality_control_failures
        qc_success_rate = (self.quality_control_passes / total_qc_tests * 100) if total_qc_tests else 100.0
        
        manufacturing_status = {
            **base_status,
            "production_lines": self.production_lines,
            "manufacturing_recipes": list(self.manufacturing_recipes.keys()),
            "storage": {
                "raw_materials": {
                    "total_units": raw_storage_used,
                    "capacity_utilization_percent": round((raw_storage_used / self.raw_material_capacity) * 100, 1),
                    "by_material": dict(self.raw_material_inventory)
                },
                "finished_goods": {
                    "total_units": finished_storage_used,
                    "capacity_utilization_percent": round((finished_storage_used / self.finished_goods_capacity) * 100, 1),
                    "by_product": dict(self.finished_goods_inventory)
                }
            },
            "operations": {
                "active_jobs": len(self.active_production_jobs),
                "queued_jobs": len(self.production_queue),
                "total_manufactured_units": self.total_products_manufactured,
                "average_line_efficiency_percent": round(avg_efficiency, 1),
                "total_manufacturing_costs": round(self.manufacturing_costs, 2)
            },
            "quality_control": {
                "success_rate_percent": round(qc_success_rate, 1),
                "total_passes": self.quality_control_passes,
                "total_failures": self.quality_control_failures
            },
            "production_lines_status": {
                "status": dict(self.production_line_status),
                "efficiency": {k: round(v, 1) for k, v in self.production_line_efficiency.items()}
            },
            "shipments": {
                "pending_outbound": len(self.pending_product_shipments),
                "total_shipped": len(self.shipped_products)
            }
        }
        
        return manufacturing_status

def demo_manufacturing_agent():
    """
    Demonstration showing how the ManufacturingAgent works with processing agent outputs
    """
    # Define manufacturing recipes for Maadan model
    recipes = {
        "PG_to_Fertilizer": {
            "input_materials": {"PG": 1.0, "additives": 0.05},
            "output_product": "Bagged_Fertilizer",
            "output_quantity_ratio": 0.95,
            "production_time_hours": 2.5,
            "energy_cost_per_unit": 18.0,
            "required_line": "chemical_production",
            "quality_requirements": {"min_purity": 0.85}
        },
        "Steel_to_Products": {
            "input_materials": {"Steel Billet": 1.0},
            "output_product": "Steel_Beams",
            "output_quantity_ratio": 0.88,
            "production_time_hours": 4.0,
            "energy_cost_per_unit": 35.0,
            "required_line": "metal_forming",
            "quality_requirements": {"min_strength": 0.90}
        }
    }
    
    # Create manufacturing facility
    manufacturer = ManufacturingAgent(
        "MFG_001",
        "Industrial Manufacturing Plant",
        200.0,  # 200 units/hour capacity
        ["chemical_production", "metal_forming", "packaging"],
        recipes
    )
    
    # Simulate receiving shipment from processing
    processing_shipment = {
        "shipment_id": "Ship_PROC_001_0001",
        "material_type": "PG",
        "quantity": 100.0,
        "destination_agent_id": "MFG_001",
        "material_quality": 0.90,
        "processing_cost": 35.50,
        "status": "dispatched",
        "created_at": datetime.now()
    }
    
    # Receive the shipment
    manufacturer.receive_shipment_from_processing(processing_shipment)
    
    # Get operator input requirements
    required_inputs = manufacturer.get_required_inputs("PG_to_Fertilizer", 80.0)
    print("Manufacturing operator inputs required:")
    for input_name, input_spec in required_inputs.items():
        print(f"- {input_name}: {input_spec.get('description', 'No description')}")
    
    # Manufacture products with operator inputs
    operator_decisions = {
        "production_priority": "normal",
        "quality_standard": "premium", 
        "batch_size": 80.0,
        "quality_control_level": "enhanced",
        "nutrient_blend": "high_phosphorus"
    }
    
    result = manufacturer.process_material("PG_to_Fertilizer", operator_decisions)
    print(f"\nManufacturing result: {result}")
    
    # Run manufacturing operations (simulate production)
    completed = manufacturer.run_manufacturing_operations()
    print(f"Completed manufacturing jobs: {len(completed)}")
    
    # Show facility status
    status = manufacturer.get_manufacturing_status()
    print(f"\nManufacturing Facility Status:")
    print(f"Raw materials in storage: {status['storage']['raw_materials']['total_units']} units")
    print(f"Finished goods ready: {status['storage']['finished_goods']['total_units']} units")
    print(f"Quality control success rate: {status['quality_control']['success_rate_percent']}%")

if __name__ == "__main__":
    demo_manufacturing_agent()