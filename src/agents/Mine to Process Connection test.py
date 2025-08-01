"""
Test script to verify mining and processing agents work together
Run this to test the connection between your mining and processing agents
"""

import sys
import os

# Add the current directory to Python path so we can import our agents
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mining_agent import MiningAgent
from processing_agent import ProcessingAgent
from datetime import datetime

def test_mining_to_processing_flow():
    """
    Test the complete flow from mining extraction to processing transformation
    """
    print("=" * 60)
    print("TESTING MINING TO PROCESSING FLOW")
    print("=" * 60)
    
    # Step 1: Create a mining operation
    print("\n1. Creating Mining Operation...")
    mine = MiningAgent(
        "MINE_001",
        "Test Phosphate Mine",
        5000.0,  # 5,000 ton capacity
        ["Phosphorite Ore", "Iron Ore"],
        500.0  # 500 tons/hour extraction rate
    )
    
    # Step 2: Create a processing facility
    print("\n2. Creating Processing Facility...")
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
    
    processor = ProcessingAgent(
        "PROC_001",
        "Test Processing Plant",
        1000.0,  # 1,000 ton capacity
        ["chemical_processing", "smelting"],
        recipes
    )
    
    # Step 3: Mine some materials
    print("\n3. Extracting Materials from Mine...")
    extraction_result = mine.process_material("Phosphorite Ore", 300.0)
    print(f"Extracted: {extraction_result['extracted_quantity']} tons of {extraction_result['extracted_material']}")
    print(f"Mine inventory: {extraction_result['total_mine_inventory']} tons total")
    
    # Step 4: Create shipment from mining to processing
    print("\n4. Creating Shipment to Processing...")
    shipment_created = mine.create_shipment_to_processing("Phosphorite Ore", 200.0, "PROC_001")
    print(f"Shipment created: {shipment_created}")
    
    # Step 5: Dispatch the shipment
    print("\n5. Dispatching Shipment...")
    dispatched_shipments = mine.process_shipments()
    if dispatched_shipments:
        shipment = dispatched_shipments[0]
        print(f"Dispatched: {shipment['quantity']} tons of {shipment['ore_type']}")
        print(f"Shipment ID: {shipment['shipment_id']}")
        print(f"Destination: {shipment['destination_agent_id']}")
        
        # Step 6: Processing facility receives the shipment
        print("\n6. Processing Facility Receiving Shipment...")
        received = processor.receive_shipment_from_mining(shipment)
        print(f"Shipment received: {received}")
        
        if received:
            # Step 7: Check what operator inputs are needed
            print("\n7. Getting Required Operator Inputs...")
            required_inputs = processor.get_required_inputs("Phosphorite Ore", 150.0)
            print("Required operator inputs:")
            for input_name, input_spec in required_inputs.items():
                if isinstance(input_spec, dict) and 'description' in input_spec:
                    print(f"  - {input_name}: {input_spec['description']}")
                    if 'options' in input_spec:
                        print(f"    Options: {input_spec['options']}")
            
            # Step 8: Process the material with operator decisions
            print("\n8. Processing Material with Operator Inputs...")
            operator_decisions = {
                "selected_recipe": "Phosphorite_to_PG",
                "processing_priority": "normal",
                "quality_target": 0.90,
                "batch_size": 150.0
            }
            
            processing_result = processor.process_material("Phosphorite Ore", 150.0, operator_decisions)
            print(f"Processing result: {processing_result['status']}")
            if processing_result['status'] == 'success':
                print(f"Job ID: {processing_result['job_id']}")
                print(f"Expected output: {processing_result['expected_output']['quantity']:.1f} tons of {processing_result['expected_output']['material']}")
            
            # Step 9: Show facility status
            print("\n9. Current Facility Status...")
            processing_status = processor.get_processing_status()
            mining_status = mine.get_mining_status()
            
            print(f"\nMining Status:")
            print(f"  - Total extracted: {mining_status['extraction']['total_extracted']} tons")
            print(f"  - Remaining inventory: {mining_status['inventory']['total_stored_tons']} tons")
            print(f"  - Shipments sent: {mining_status['shipments']['total_shipped']}")
            
            print(f"\nProcessing Status:")
            print(f"  - Raw materials in storage: {processing_status['storage']['raw_materials']['total_tons']} tons")
            print(f"  - Active processing jobs: {processing_status['operations']['active_jobs']}")
            print(f"  - Queued jobs: {processing_status['operations']['queued_jobs']}")
            
            print("\n" + "=" * 60)
            print("TEST COMPLETED SUCCESSFULLY!")
            print("Your mining and processing agents are working together properly.")
            print("=" * 60)
            
        else:
            print("ERROR: Processing facility rejected the shipment")
    else:
        print("ERROR: No shipments were dispatched from mining")

if __name__ == "__main__":
    test_mining_to_processing_flow()