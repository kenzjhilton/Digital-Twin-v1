"""
Supply Chain Orchestrator - Automatic Agent Connections

This orchestrator automatically manages the flow between your agents,
eliminating the need for manual shipment passing. It creates a
"smart supply chain" that flows materials automatically.

Features:
- Automatic routing based on material types
- Real-time shipment tracking and delivery
- Operator input request management
- End-to-end material traceability
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import uuid

# Import your agents
from mining_agent import MiningAgent
from processing_agent import ProcessingAgent
from manufacturing_agent import ManufacturingAgent
from distribution_agent import DistributionAgent
from retail_agent import RetailAgent

# Configure logging
logging.basicConfig(level=logging.INFO) # Set to DEBUG for more detailed logs
logger = logging.getLogger(__name__) # Set up a logger for this module

@dataclass
class MaterialTrace:
    """Complete tracking record for materials as they flow through the supply chain"""
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4())) # Unique identifier for this material trace
    original_material: str = ""
    original_quantity: float = 0.0
    current_material: str = ""
    current_quantity: float = 0.0
    current_location: str = ""
    
    # Journey tracking
    journey_log: List[Dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def add_journey_step(self, stage: str, agent_id: str, operation: str, details: Dict = None):
        """Add a step to the material's journey"""
        step = {
            "timestamp": datetime.now(),
            "stage": stage,
            "agent_id": agent_id,
            "operation": operation,
            "details": details or {}
        }
        self.journey_log.append(step)
        self.last_updated = datetime.now()
        self.current_location = agent_id

class SupplyChainOrchestrator:
    """
    Orchestrator that automatically manages connections between all your agents
    
    This creates the "smart supply chain" that handles material flow automatically,
    so you just need to inject materials and they flow through the entire system.
    """
    
    def __init__(self):
        """Initialize the orchestrator with empty agent registries"""
        # Agent registries
        self.mining_agents: Dict[str, MiningAgent] = {}
        self.processing_agents: Dict[str, ProcessingAgent] = {}
        self.manufacturing_agents: Dict[str, ManufacturingAgent] = {}
        self.distribution_agents: Dict[str, DistributionAgent] = {}
        self.retail_agents: Dict[str, RetailAgent] = {}
        
        # Automatic routing configuration
        self.routing_rules: Dict[str, Dict] = {
            # Define which agents handle which materials
            "ore_to_processing": {},      # ore_type -> processing_agent_id
            "processed_to_manufacturing": {},  # processed_material -> manufacturing_agent_id
            "products_to_distribution": {},    # product_type -> distribution_agent_id
            "distribution_to_retail": {}       # distribution_agent_id -> retail_agent_id
        }
        
        # Material tracking
        self.material_traces: Dict[str, MaterialTrace] = {}
        self.active_shipments: Dict[str, Dict] = {}
        
        # Operator request queue
        self.pending_operator_requests: List[Dict] = []
        
        logger.info("Supply Chain Orchestrator initialized")
    
    def register_mining_agent(self, agent: MiningAgent, ore_processing_routes: Dict[str, str] = None):
        """
        Register a mining agent and define where its ores should be processed
        
        Args:
            agent: MiningAgent instance
            ore_processing_routes: Dict mapping ore types to processing agent IDs
                Example: {"Phosphorite Ore": "PROC_001", "Iron Ore": "PROC_002"}
        """
        self.mining_agents[agent.agent_id] = agent
        
        if ore_processing_routes:
            for ore_type, processing_agent_id in ore_processing_routes.items():
                self.routing_rules["ore_to_processing"][ore_type] = processing_agent_id
        
        logger.info(f"Registered mining agent: {agent.name}")
        
    def register_processing_agent(self, agent: ProcessingAgent, 
                                processing_manufacturing_routes: Dict[str, str] = None):
        """Register processing agent and define routing to manufacturing"""
        self.processing_agents[agent.agent_id] = agent
        
        if processing_manufacturing_routes:
            for processed_material, manufacturing_agent_id in processing_manufacturing_routes.items():
                self.routing_rules["processed_to_manufacturing"][processed_material] = manufacturing_agent_id
        
        logger.info(f"Registered processing agent: {agent.name}")
    
    def register_manufacturing_agent(self, agent: ManufacturingAgent,
        product_distribution_routes: Dict[str, str] = None):
        """Register manufacturing agent and define routing to distribution"""
        self.manufacturing_agents[agent.agent_id] = agent
        
        if product_distribution_routes:
            for product_type, distribution_agent_id in product_distribution_routes.items():
                self.routing_rules["products_to_distribution"][product_type] = distribution_agent_id
        
        logger.info(f"Registered manufacturing agent: {agent.name}")
    
    def register_distribution_agent(self, agent: DistributionAgent, retail_agent_id: str = None):
        """Register distribution agent and define routing to retail"""
        self.distribution_agents[agent.agent_id] = agent
        
        if retail_agent_id:
            self.routing_rules["distribution_to_retail"][agent.agent_id] = retail_agent_id
        
        logger.info(f"Registered distribution agent: {agent.name}")
    
    def register_retail_agent(self, agent: RetailAgent):
        """Register retail agent"""
        self.retail_agents[agent.agent_id] = agent
        logger.info(f"Registered retail agent: {agent.name}")
    
    def inject_raw_materials(self, mining_agent_id: str, ore_type: str, quantity: float) -> str:
        """
        Inject raw materials into the supply chain and start automatic flow
        
        Args:
            mining_agent_id: ID of mining agent to extract from
            ore_type: Type of ore to extract
            quantity: Amount to extract
            
        Returns:
            trace_id: Unique identifier for tracking this material batch
        """
        if mining_agent_id not in self.mining_agents:
            raise ValueError(f"Mining agent {mining_agent_id} not registered")
        
        mine = self.mining_agents[mining_agent_id]
        
        # Extract materials
        extraction_result = mine.process_material(ore_type, quantity)
        
        if extraction_result['status'] != 'success':
            raise RuntimeError(f"Extraction failed: {extraction_result}")
        
        # Create material trace
        trace = MaterialTrace(
            original_material=ore_type,
            original_quantity=extraction_result['extracted_quantity'],
            current_material=ore_type,
            current_quantity=extraction_result['extracted_quantity'],
            current_location=mining_agent_id
        )
        
        trace.add_journey_step("mining", mining_agent_id, "extracted", {
            "quantity": extraction_result['extracted_quantity'],
            "quality": extraction_result['ore_quality']
        })
        
        self.material_traces[trace.trace_id] = trace
        
        # Automatically create and process shipment to next stage
        self._auto_route_from_mining(mining_agent_id, ore_type, extraction_result['extracted_quantity'], trace.trace_id)
        
        logger.info(f"Injected {quantity} tons of {ore_type} - Trace ID: {trace.trace_id}")
        return trace.trace_id
    
    def _auto_route_from_mining(self, mining_agent_id: str, ore_type: str, quantity: float, trace_id: str):
        """Automatically route materials from mining to processing"""
        # Find the right processing agent
        processing_agent_id = self.routing_rules["ore_to_processing"].get(ore_type)
        
        if not processing_agent_id or processing_agent_id not in self.processing_agents:
            logger.warning(f"No processing route defined for {ore_type}")
            return
        
        mine = self.mining_agents[mining_agent_id]
        processor = self.processing_agents[processing_agent_id]
        
        # Create shipment
        shipment_created = mine.create_shipment_to_processing(ore_type, quantity, processing_agent_id)
        
        if shipment_created:
            # Dispatch shipment
            dispatched_shipments = mine.process_shipments()
            
            if dispatched_shipments:
                shipment = dispatched_shipments[0]
                
                # Automatically deliver to processing
                received = processor.receive_shipment_from_mining(shipment)
                
                if received:
                    # Update trace
                    trace = self.material_traces[trace_id]
                    trace.add_journey_step("processing", processing_agent_id, "received", {
                        "shipment_id": shipment['shipment_id'],
                        "quantity": shipment['quantity']
                    })
                    
                    # Create operator request for processing
                    self._create_processing_request(processing_agent_id, ore_type, quantity, trace_id)
                    
                    logger.info(f"Auto-routed {ore_type} from {mining_agent_id} to {processing_agent_id}")
    
    def _create_processing_request(self, processing_agent_id: str, material_type: str, quantity: float, trace_id: str):
        """Create an operator request for processing decisions"""
        processor = self.processing_agents[processing_agent_id]
        required_inputs = processor.get_required_inputs(material_type, quantity)
        
        operator_request = {
            "request_id": str(uuid.uuid4()),
            "trace_id": trace_id,
            "agent_id": processing_agent_id,
            "agent_type": "processing",
            "operation": "process_material",
            "material_type": material_type,
            "quantity": quantity,
            "required_inputs": required_inputs,
            "created_at": datetime.now(),
            "status": "pending"
        }
        
        self.pending_operator_requests.append(operator_request)
        logger.info(f"Created operator request for processing {material_type}")
    
    def process_operator_request(self, request_id: str, operator_inputs: Dict[str, Any]) -> Dict:
        """
        Process an operator's input and continue the material flow
        
        Args:
            request_id: ID of the operator request
            operator_inputs: Operator's decisions/inputs
            
        Returns:
            Result of the processing operation
        """
        # Find the request
        request = None
        for req in self.pending_operator_requests:
            if req["request_id"] == request_id:
                request = req
                break
        
        if not request:
            return {"error": "Request not found"}
        
        # Process based on agent type
        if request["agent_type"] == "processing":
            return self._process_processing_request(request, operator_inputs)
        elif request["agent_type"] == "manufacturing":
            return self._process_manufacturing_request(request, operator_inputs)
        elif request["agent_type"] == "retail":
            return self._process_retail_request(request, operator_inputs)
        
        return {"error": "Unknown agent type"}
    
    def _process_processing_request(self, request: Dict, operator_inputs: Dict[str, Any]) -> Dict:
        """Handle processing operation and auto-route to manufacturing"""
        processor = self.processing_agents[request["agent_id"]]
        
        # Process the material
        result = processor.process_material(request["material_type"], request["quantity"], operator_inputs)
        
        if result["status"] == "success":
            # Update trace
            trace = self.material_traces[request["trace_id"]]
            trace.add_journey_step("processing", request["agent_id"], "processed", {
                "job_id": result["job_id"],
                "expected_output": result["expected_output"]
            })
            
            # Simulate processing completion and auto-route to manufacturing
            # In a real system, this would be triggered by actual job completion
            self._simulate_processing_completion(request["trace_id"], result)
            
        # Remove request from queue
        self.pending_operator_requests.remove(request)
        
        return result
    
    def _simulate_processing_completion(self, trace_id: str, processing_result: Dict):
        """Simulate processing completion and route to manufacturing"""
        # This would normally be triggered by actual job completion
        expected_output = processing_result["expected_output"]
        
        # Find manufacturing route
        manufacturing_agent_id = self.routing_rules["processed_to_manufacturing"].get(expected_output["material"])
        
        if manufacturing_agent_id and manufacturing_agent_id in self.manufacturing_agents:
            manufacturer = self.manufacturing_agents[manufacturing_agent_id]
            
            # Simulate shipment to manufacturing
            shipment_data = {
                "shipment_id": f"AUTO_{trace_id}",
                "material_type": expected_output["material"],
                "quantity": expected_output["quantity"],
                "destination_agent_id": manufacturing_agent_id,
                "material_quality": expected_output["quality"],
                "processing_cost": 100.0,
                "status": "dispatched",
                "created_at": datetime.now()
            }
            
            # Auto-deliver to manufacturing
            received = manufacturer.receive_shipment_from_processing(shipment_data)
            
            if received:
                # Update trace
                trace = self.material_traces[trace_id]
                trace.add_journey_step("manufacturing", manufacturing_agent_id, "received", shipment_data)
                trace.current_material = expected_output["material"]
                trace.current_quantity = expected_output["quantity"]
                
                logger.info(f"Auto-routed {expected_output['material']} to manufacturing")
    
    def get_material_trace(self, trace_id: str) -> Optional[MaterialTrace]:
        """Get the complete journey of a material batch"""
        return self.material_traces.get(trace_id)
    
    def get_pending_operator_requests(self) -> List[Dict]:
        """Get all pending operator requests"""
        return [req for req in self.pending_operator_requests if req["status"] == "pending"]
    
    def get_system_status(self) -> Dict:
        """Get comprehensive status of the entire supply chain system"""
        return {
            "agents": {
                "mining": len(self.mining_agents),
                "processing": len(self.processing_agents), 
                "manufacturing": len(self.manufacturing_agents),
                "distribution": len(self.distribution_agents),
                "retail": len(self.retail_agents)
            },
            "active_traces": len(self.material_traces),
            "pending_requests": len(self.get_pending_operator_requests()),
            "routing_rules": dict(self.routing_rules)
        }

def demo_orchestrated_supply_chain():
    """
    Demo showing how the orchestrator creates automatic connections
    """
    print("🔗 ORCHESTRATED SUPPLY CHAIN DEMO")
    print("=" * 50)
    
    # Create orchestrator
    orchestrator = SupplyChainOrchestrator()
    
    # Create agents (same as your existing agents)
    mine = MiningAgent("MINE_001", "Auto Mine", 10000.0, ["Phosphorite Ore"], 800.0)
    
    processing_recipes = {
        "Phosphorite_to_PG": {
            "input_material": "Phosphorite Ore",
            "output_material": "PG", 
            "conversion_ratio": 0.82,
            "processing_time_hours": 3.0,
            "energy_cost_per_ton": 40.0,
            "required_method": "chemical_processing"
        }
    }
    processor = ProcessingAgent("PROC_001", "Auto Processor", 600.0, ["chemical_processing"], processing_recipes)
    
    # Register agents with automatic routing
    orchestrator.register_mining_agent(mine, {"Phosphorite Ore": "PROC_001"})
    orchestrator.register_processing_agent(processor, {"PG": "MFG_001"})
    
    print("✅ Agents registered with automatic routing")
    
    # Inject materials - they will automatically flow through the system!
    trace_id = orchestrator.inject_raw_materials("MINE_001", "Phosphorite Ore", 500.0)
    print(f"📤 Injected materials - Trace ID: {trace_id}")
    
    # Check pending operator requests
    pending = orchestrator.get_pending_operator_requests()
    print(f"📋 Pending operator requests: {len(pending)}")
    
    # Process the first operator request
    if pending:
        request = pending[0]
        operator_inputs = {
            "selected_recipe": "Phosphorite_to_PG",
            "processing_priority": "normal",
            "quality_target": 0.90,
            "batch_size": 400.0
        }
        
        result = orchestrator.process_operator_request(request["request_id"], operator_inputs)
        print(f"⚗️ Processing result: {result['status']}")
    
    # Show material trace
    trace = orchestrator.get_material_trace(trace_id)
    if trace:
        print(f"\n🔍 Material Journey for {trace.original_material}:")
        for step in trace.journey_log:
            print(f"  {step['timestamp'].strftime('%H:%M:%S')} - {step['stage']}: {step['operation']}")
    
    # Show system status
    status = orchestrator.get_system_status()
    print(f"\n📊 System Status: {status}")

if __name__ == "__main__":
    demo_orchestrated_supply_chain()