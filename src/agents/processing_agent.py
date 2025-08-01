"""
Processing Agent - Handles transformation of raw materials into refined products

This agent represents a processing facility that:
1. Receives raw ore shipments from mining operations
2. Transforms ore into refined materials using various processing methods
3. Manages processing equipment and efficiency
4. Ships refined materials to manufacturing or distribution
5. Tracks material transformation ratios and costs

The processing agent is the crucial link between raw extraction and finished products.
"""

import logging
from base_agent import BaseSupplyChainAgent
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProcessingAgent(BaseSupplyChainAgent):
    """
    Processing agent that transforms raw materials into refined products.
    
    This agent inherits from your BaseSupplyChainAgent and adds processing-specific
    capabilities like transformation recipes, processing equipment, and quality control.
    """
    
    def __init__(self, agent_id: str, name: str, processing_capacity: float, 
        processing_methods: List[str], transformation_recipes: Dict[str, Dict]):
        """
        Initialize the processing facility
        
        Args:
            agent_id: Unique identifier (like "PROC_001")
            name: Human-readable name (like "AMX Processing Plant Alpha")
            processing_capacity: Maximum throughput per hour (tons/hour)
            processing_methods: List of available processing techniques
            transformation_recipes: Dict defining how to transform materials
        """
        # Initialize base agent properties
        super().__init__(agent_id, name, processing_capacity)
        
        # Processing configuration
        self.processing_methods = processing_methods
        self.transformation_recipes = transformation_recipes
        self.processing_capacity = processing_capacity
        
        # Processing equipment status - each method has its own equipment
        self.equipment_status: Dict[str, str] = {}
        self.equipment_efficiency: Dict[str, float] = {}
        
        # Initialize equipment for each processing method
        for method in processing_methods:
            self.equipment_status[method] = "operational"
            self.equipment_efficiency[method] = random.uniform(85.0, 100.0)
        
        # Material handling and storage
        self.raw_material_storage: Dict[str, float] = {}
        self.processed_material_storage: Dict[str, float] = {}
        self.material_quality_grades: Dict[str, float] = {}
        
        # Processing operations tracking
        self.active_processing_jobs: Dict[str, Dict] = {}
        self.processing_queue: List[Dict] = []
        self.processing_history: List[Dict] = []
        
        # Performance metrics
        self.total_materials_processed: float = 0.0
        self.total_processing_time: timedelta = timedelta()
        self.average_conversion_efficiency: float = 0.0
        self.energy_consumption: float = 0.0
        self.processing_costs: float = 0.0
        
        # Shipment management for outgoing materials
        self.pending_outbound_shipments: Dict[str, Dict] = {}
        self.shipped_materials: List[Dict] = []
        
        # Initialize storage capacity allocation (75% raw, 25% processed)
        self.raw_storage_capacity = self.capacity * 0.75
        self.processed_storage_capacity = self.capacity * 0.25
        
        logger.info(f"Processing Agent {self.name} initialized with {len(processing_methods)} processing methods")
        logger.info(f"Available transformations: {list(transformation_recipes.keys())}")
    
    def receive_shipment_from_mining(self, shipment_data: Dict) -> bool:
        """
        Receive a shipment from a mining agent and add it to raw material storage.
        """
        ore_type = shipment_data.get("ore_type")
        quantity = shipment_data.get("quantity", 0.0)
        quality = shipment_data.get("ore_quality", 1.0)
        
        # Validation 1: Check if we can handle this ore type
        can_process = any(
            recipe["input_material"] == ore_type 
            for recipe in self.transformation_recipes.values()
        )
        
        if not can_process:
            logger.error(f"{self.name}: Cannot process {ore_type}. No recipes available.")
            return False
        
        # Validation 2: Check raw material storage capacity
        current_raw_storage = sum(self.raw_material_storage.values())
        if current_raw_storage + quantity > self.raw_storage_capacity:
            available_space = self.raw_storage_capacity - current_raw_storage
            logger.warning(f"{self.name}: Limited storage space. Can only accept {available_space} tons of {quantity} requested")
            
            if available_space <= 0:
                logger.error(f"{self.name}: Raw material storage full. Rejecting shipment.")
                return False
            
            quantity = available_space
        
        # Accept the shipment
        self.raw_material_storage[ore_type] = self.raw_material_storage.get(ore_type, 0.0) + quantity
        self.material_quality_grades[ore_type] = quality
        
        logger.info(f"{self.name} received {quantity} tons of {ore_type} (Quality: {quality:.2f})")
        logger.info(f"Raw material storage now: {sum(self.raw_material_storage.values()):.1f} tons total")
        
        return True
    
    def get_required_inputs(self, material_type: str, quantity: float) -> Dict[str, any]:
        """
        Define what operator inputs are needed for processing this material.
        """
        # Find applicable recipes for this material
        applicable_recipes = [
            (recipe_name, recipe_data) 
            for recipe_name, recipe_data in self.transformation_recipes.items()
            if recipe_data["input_material"] == material_type
        ]
        
        if not applicable_recipes:
            return {"error": f"No processing recipes available for {material_type}"}
        
        # Create input requirements based on available recipes
        required_inputs = {
            "selected_recipe": {
                "type": "choice",
                "options": [recipe_name for recipe_name, _ in applicable_recipes],
                "description": f"Choose processing method for {material_type}",
                "required": True
            },
            "processing_priority": {
                "type": "choice", 
                "options": ["urgent", "normal", "batch_when_full"],
                "description": "When should this processing job be scheduled?",
                "default": "normal",
                "required": True
            },
            "quality_target": {
                "type": "float",
                "min": 0.5,
                "max": 1.0,
                "description": "Target quality grade for processed material (0.5-1.0)",
                "default": 0.85,
                "required": True
            },
            "batch_size": {
                "type": "float",
                "min": 1.0,
                "max": min(quantity, self.processing_capacity),
                "description": f"How many tons to process in this batch? (Available: {quantity})",
                "default": min(quantity, self.processing_capacity * 0.5),
                "required": True
            }
        }
        
        return required_inputs
    
    def process_material(self, material_type: str, quantity: float, operator_inputs: Dict[str, any] = None):
        """
        Transform raw materials into processed materials using operator-specified parameters.
        """
        # Use default inputs if none provided
        if operator_inputs is None:
            operator_inputs = {
                "selected_recipe": list(self.transformation_recipes.keys())[0],
                "processing_priority": "normal",
                "quality_target": 0.85,
                "batch_size": min(quantity, self.processing_capacity * 0.5)
            }
        
        # Extract operator decisions
        selected_recipe = operator_inputs.get("selected_recipe")
        batch_size = operator_inputs.get("batch_size", quantity)
        quality_target = operator_inputs.get("quality_target", 0.85)
        priority = operator_inputs.get("processing_priority", "normal")
        
        # Validation 1: Check if recipe exists
        if selected_recipe not in self.transformation_recipes:
            return {
                "status": "error",
                "message": f"Unknown recipe: {selected_recipe}"
            }
        
        recipe = self.transformation_recipes[selected_recipe]
        
        # Validation 2: Check if we have enough raw material
        available_material = self.raw_material_storage.get(material_type, 0.0)
        if available_material < batch_size:
            return {
                "status": "error", 
                "message": f"Insufficient {material_type}. Available: {available_material}, Requested: {batch_size}"
            }
        
        # Validation 3: Check equipment availability
        required_method = recipe.get("required_method")
        if (required_method and 
            self.equipment_status.get(required_method) != "operational"):
            return {
                "status": "error",
                "message": f"Equipment for {required_method} is not operational"
            }
        
        # Create processing job
        job_id = f"JOB_{self.agent_id}_{len(self.processing_history) + 1:04d}"
        
        # Calculate processing parameters
        base_conversion_ratio = recipe["conversion_ratio"]
        processing_time = recipe["processing_time_hours"]
        energy_cost = recipe["energy_cost_per_ton"]
        
        # Adjust for equipment efficiency and quality target
        equipment_efficiency = self.equipment_efficiency.get(required_method, 100.0) / 100.0
        actual_conversion_ratio = base_conversion_ratio * equipment_efficiency
        
        # Quality target affects processing time and cost
        quality_multiplier = quality_target / 0.85
        adjusted_processing_time = processing_time * quality_multiplier
        adjusted_energy_cost = energy_cost * quality_multiplier
        
        # Calculate expected outputs
        expected_output_quantity = batch_size * actual_conversion_ratio
        expected_output_material = recipe["output_material"]
        
        # Reserve raw materials
        self.raw_material_storage[material_type] -= batch_size
        
        # Create processing job record
        processing_job = {
            "job_id": job_id,
            "recipe_name": selected_recipe,
            "input_material": material_type,
            "input_quantity": batch_size,
            "expected_output_material": expected_output_material,
            "expected_output_quantity": expected_output_quantity,
            "target_quality": quality_target,
            "processing_time_hours": adjusted_processing_time,
            "energy_cost": adjusted_energy_cost * batch_size,
            "priority": priority,
            "operator_inputs": dict(operator_inputs),
            "status": "queued",
            "created_at": datetime.now(),
            "started_at": None,
            "completed_at": None
        }
        
        # Add to processing queue
        self.processing_queue.append(processing_job)
        
        # Sort queue by priority
        priority_order = {"urgent": 0, "normal": 1, "batch_when_full": 2}
        self.processing_queue.sort(key=lambda job: priority_order.get(job["priority"], 1))
        
        logger.info(f"Processing job {job_id} created: {batch_size} tons {material_type} -> {expected_output_quantity:.1f} tons {expected_output_material}")
        
        return {
            "status": "success",
            "job_id": job_id,
            "queued_position": len(self.processing_queue),
            "expected_output": {
                "material": expected_output_material,
                "quantity": expected_output_quantity,
                "quality": quality_target
            },
            "estimated_completion": datetime.now() + timedelta(hours=adjusted_processing_time)
        }
    
    def run_processing_operations(self) -> List[Dict]:
        """
        Execute queued processing jobs and complete active ones.
        """
        completed_jobs = []
        current_time = datetime.now()
        
        # Complete active jobs that have finished
        finished_job_ids = []
        for job_id, job in self.active_processing_jobs.items():
            estimated_completion = job["started_at"] + timedelta(hours=job["processing_time_hours"])
            
            if current_time >= estimated_completion:
                # Job is complete - produce the output materials
                output_material = job["expected_output_material"]
                output_quantity = job["expected_output_quantity"]
                target_quality = job["target_quality"]
                
                # Add some realistic variability to output (+/- 5%)
                actual_output = output_quantity * random.uniform(0.95, 1.05)
                actual_quality = target_quality * random.uniform(0.95, 1.05)
                
                # Add to processed material storage
                self.processed_material_storage[output_material] = (
                    self.processed_material_storage.get(output_material, 0.0) + actual_output
                )
                self.material_quality_grades[output_material] = actual_quality
                
                # Update job record with completion
                job["status"] = "completed"
                job["completed_at"] = current_time
                job["actual_output_quantity"] = actual_output
                job["actual_quality"] = actual_quality
                
                # Update performance metrics
                self.total_materials_processed += job["input_quantity"]
                self.processing_costs += job["energy_cost"]
                
                # Move to history
                self.processing_history.append(dict(job))
                completed_jobs.append(dict(job))
                finished_job_ids.append(job_id)
                
                logger.info(f"Processing job {job_id} completed: produced {actual_output:.1f} tons {output_material}")
        
        # Remove completed jobs from active list
        for job_id in finished_job_ids:
            del self.active_processing_jobs[job_id]
        
        # Start new jobs if equipment capacity is available
        max_concurrent_jobs = len(self.processing_methods)
        while (len(self.active_processing_jobs) < max_concurrent_jobs and 
            self.processing_queue):
            
            # Get next job from queue
            next_job = self.processing_queue.pop(0)
            
            # Check if required equipment is available
            required_method = self.transformation_recipes[next_job["recipe_name"]].get("required_method")
            equipment_busy = any(
                job.get("required_method") == required_method 
                for job in self.active_processing_jobs.values()
            )
            
            if not equipment_busy and self.equipment_status.get(required_method) == "operational":
                # Start the job
                next_job["status"] = "processing"
                next_job["started_at"] = current_time
                self.active_processing_jobs[next_job["job_id"]] = next_job
                
                logger.info(f"Started processing job {next_job['job_id']}: {next_job['input_quantity']} tons {next_job['input_material']}")
            else:
                # Put job back at front of queue if equipment not available
                self.processing_queue.insert(0, next_job)
                break
        
        return completed_jobs
    
    def get_processing_status(self) -> Dict:
        """
        Get comprehensive status report of the processing facility.
        """
        base_status = super().get_status()
        
        # Calculate storage utilization
        raw_storage_used = sum(self.raw_material_storage.values())
        processed_storage_used = sum(self.processed_material_storage.values())
        
        # Calculate efficiency metrics
        avg_efficiency = (
            sum(self.equipment_efficiency.values()) / len(self.equipment_efficiency)
            if self.equipment_efficiency else 100.0
        )
        
        processing_status = {
            **base_status,
            "processing_methods": self.processing_methods,
            "transformation_recipes": list(self.transformation_recipes.keys()),
            "storage": {
                "raw_materials": {
                    "total_tons": raw_storage_used,
                    "capacity_utilization_percent": round((raw_storage_used / self.raw_storage_capacity) * 100, 1),
                    "by_material": dict(self.raw_material_storage)
                },
                "processed_materials": {
                    "total_tons": processed_storage_used,
                    "capacity_utilization_percent": round((processed_storage_used / self.processed_storage_capacity) * 100, 1),
                    "by_material": dict(self.processed_material_storage)
                }
            },
            "operations": {
                "active_jobs": len(self.active_processing_jobs),
                "queued_jobs": len(self.processing_queue),
                "total_processed_tons": self.total_materials_processed,
                "average_equipment_efficiency_percent": round(avg_efficiency, 1),
                "total_processing_costs": round(self.processing_costs, 2)
            },
            "equipment": {
                "status": dict(self.equipment_status),
                "efficiency": {k: round(v, 1) for k, v in self.equipment_efficiency.items()}
            },
            "shipments": {
                "pending_outbound": len(self.pending_outbound_shipments),
                "total_shipped": len(self.shipped_materials)
            }
        }
        
        return processing_status

def demo_processing_agent():
    """
    Demonstration showing how the ProcessingAgent works with mining agent outputs
    """
    # Define transformation recipes for common mining outputs
    recipes = {
        "Phosphorite_to_PG": {
            "input_material": "Phosphorite Ore",
            "output_material": "PG",
            "conversion_ratio": 0.82,
            "processing_time_hours": 3.0,
            "energy_cost_per_ton": 40.0,
            "required_method": "chemical_processing"
        },
        "Iron_to_Steel": {
            "input_material": "Iron Ore", 
            "output_material": "Steel Billet",
            "conversion_ratio": 0.75,
            "processing_time_hours": 4.5,
            "energy_cost_per_ton": 65.0,
            "required_method": "smelting"
        }
    }
    
    # Create processing facility
    processor = ProcessingAgent(
        "PROC_001",
        "AMX Processing Plant Alpha",
        500.0,
        ["chemical_processing", "smelting", "refining"],
        recipes
    )
    
    # Simulate receiving shipment from mining
    mining_shipment = {
        "shipment_id": "Ship_MINE_001_0001",
        "ore_type": "Phosphorite Ore",
        "quantity": 150.0,
        "destination_agent_id": "PROC_001",
        "ore_quality": 0.85,
        "extraction_cost": 25.50,
        "status": "dispatched",
        "estimated_arrival": datetime.now()
    }
    
    # Receive the shipment
    processor.receive_shipment_from_mining(mining_shipment)
    
    # Get operator input requirements
    required_inputs = processor.get_required_inputs("Phosphorite Ore", 100.0)
    print("Operator inputs required:")
    for input_name, input_spec in required_inputs.items():
        print(f"- {input_name}: {input_spec.get('description', 'No description')}")
    
    # Process material with operator inputs
    operator_decisions = {
        "selected_recipe": "Phosphorite_to_PG",
        "processing_priority": "normal", 
        "quality_target": 0.90,
        "batch_size": 100.0
    }
    
    result = processor.process_material("Phosphorite Ore", 100.0, operator_decisions)
    print(f"\nProcessing result: {result}")
    
    # Show facility status
    status = processor.get_processing_status()
    print(f"\nProcessing Facility Status:")
    print(f"Raw materials in storage: {status['storage']['raw_materials']['total_tons']} tons")
    print(f"Processed materials ready: {status['storage']['processed_materials']['total_tons']} tons")
    print(f"Active processing jobs: {status['operations']['active_jobs']}")

if __name__ == "__main__":
    demo_processing_agent()