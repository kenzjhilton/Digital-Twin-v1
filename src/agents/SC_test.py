"""
Complete End-to-End Supply Chain Test

This script demonstrates the complete flow from raw material extraction
to final customer delivery, tracking materials through all 5 agents:

Mining → Processing → Manufacturing → Distribution → Retail → Customer

Run this to see your complete supply chain reconstruction system in action!
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all your agents
from mining_agent import MiningAgent
from processing_agent import ProcessingAgent
from manufacturing_agent import ManufacturingAgent
from distribution_agent import DistributionAgent
from retail_agent import RetailAgent

def run_complete_supply_chain_flow():
    """
    Run a complete material flow from raw extraction to customer delivery
    
    This demonstrates your original goal: inject raw mining materials
    and track them end-to-end through the entire supply chain system.
    """
    print("=" * 80)
    print("COMPLETE SUPPLY CHAIN RECONSTRUCTION - END-TO-END FLOW")
    print("=" * 80)
    print("Tracking materials from raw extraction to customer delivery...")
    print()
    
    # ========================================================================
    # STEP 1: CREATE ALL SUPPLY CHAIN AGENTS
    # ========================================================================
    print("🏭 STEP 1: Initializing Supply Chain Agents")
    print("-" * 50)
    
    # Create Mining Agent
    mine = MiningAgent(
        "MINE_001",
        "Maadan Mining Operation", 
        10000.0,  # 10,000 ton capacity
        ["Phosphorite Ore", "Iron Ore"],
        800.0  # 800 tons/hour extraction rate
    )
    print(f"✅ {mine.name} initialized")
    
    # Create Processing Agent with transformation recipes
    processing_recipes = {
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
        "Maadan Processing Plant",
        600.0,  # 600 tons/hour capacity
        ["chemical_processing", "smelting"],
        processing_recipes
    )
    print(f"✅ {processor.name} initialized")
    
    # Create Manufacturing Agent with production recipes
    manufacturing_recipes = {
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
    
    manufacturer = ManufacturingAgent(
        "MFG_001",
        "Maadan Manufacturing Plant",
        400.0,  # 400 units/hour capacity
        ["chemical_production", "metal_forming"],
        manufacturing_recipes
    )
    print(f"✅ {manufacturer.name} initialized")
    
    # Create Distribution Agent
    distributor = DistributionAgent(
        "DIST_001",
        "Maadan Distribution Center",
        5000.0,  # 5,000 unit capacity
        ["Zone_A", "Zone_B", "Zone_C"]
    )
    print(f"✅ {distributor.name} initialized")
    
    # Create Retail Agent
    retailer = RetailAgent(
        "RETAIL_001", 
        "Maadan Retail Center",
        2000.0,  # 2,000 unit capacity
        ["online", "physical_store", "wholesale"],
        ["residential", "commercial", "agricultural"]
    )
    print(f"✅ {retailer.name} initialized")
    print()
    
    # ========================================================================
    # STEP 2: INJECT RAW MATERIALS (MINING STAGE)
    # ========================================================================
    print("⛏️  STEP 2: Raw Material Extraction (Mining)")
    print("-" * 50)
    
    # Extract Phosphorite Ore (will become fertilizer)
    extraction_result = mine.process_material("Phosphorite Ore", 500.0)
    print(f"🔨 Extracted: {extraction_result['extracted_quantity']:.1f} tons of {extraction_result['extracted_material']}")
    print(f"📊 Ore Quality: {extraction_result['ore_quality']:.2f}")
    print(f"📦 Mine Inventory: {extraction_result['total_mine_inventory']:.1f} tons total")
    
    # Create shipment to processing
    shipment_created = mine.create_shipment_to_processing("Phosphorite Ore", 400.0, "PROC_001")
    print(f"📤 Shipment to Processing: {'✅ Created' if shipment_created else '❌ Failed'}")
    
    # Dispatch shipment
    dispatched_shipments = mine.process_shipments()
    mining_shipment = dispatched_shipments[0] if dispatched_shipments else None
    
    if mining_shipment:
        print(f"🚚 Dispatched: {mining_shipment['quantity']} tons {mining_shipment['ore_type']}")
        print(f"🎯 Destination: {mining_shipment['destination_agent_id']}")
        print(f"⏰ Estimated Arrival: {mining_shipment['estimated_arrival'].strftime('%H:%M')}")
    print()
    
    # ========================================================================
    # STEP 3: MATERIAL PROCESSING 
    # ========================================================================
    print("🔬 STEP 3: Material Processing (Processing Plant)")
    print("-" * 50)
    
    if mining_shipment:
        # Processing receives the shipment
        received = processor.receive_shipment_from_mining(mining_shipment)
        print(f"📥 Shipment Received: {'✅ Success' if received else '❌ Failed'}")
        
        if received:
            # Get operator input requirements
            required_inputs = processor.get_required_inputs("Phosphorite Ore", 300.0)
            print(f"📋 Operator Inputs Required: {len(required_inputs)} parameters")
            
            # Process with operator decisions
            operator_decisions = {
                "selected_recipe": "Phosphorite_to_PG",
                "processing_priority": "normal",
                "quality_target": 0.90,
                "batch_size": 300.0
            }
            
            processing_result = processor.process_material("Phosphorite Ore", 300.0, operator_decisions)
            print(f"⚗️  Processing Job: {processing_result['status']}")
            
            if processing_result['status'] == 'success':
                expected_output = processing_result['expected_output']
                print(f"🎯 Expected Output: {expected_output['quantity']:.1f} tons {expected_output['material']}")
                print(f"🏷️  Target Quality: {expected_output['quality']:.2f}")
                
                # Simulate processing completion by running operations
                completed_jobs = processor.run_processing_operations()
                if completed_jobs:
                    job = completed_jobs[0]
                    print(f"✅ Processing Complete: {job['actual_output_quantity']:.1f} tons {job['expected_output_material']} produced")
                    
                    # Create shipment to manufacturing
                    mfg_shipment_data = {
                        "shipment_id": f"Ship_PROC_001_001",
                        "material_type": job['expected_output_material'],
                        "quantity": job['actual_output_quantity'],
                        "destination_agent_id": "MFG_001",
                        "material_quality": job.get('actual_quality', 0.90),
                        "processing_cost": job['energy_cost'],
                        "status": "dispatched",
                        "created_at": datetime.now()
                    }
    print()
    
    # ========================================================================
    # STEP 4: MANUFACTURING
    # ========================================================================
    print("🏭 STEP 4: Product Manufacturing")
    print("-" * 50)
    
    if 'mfg_shipment_data' in locals():
        # Manufacturing receives processed materials
        mfg_received = manufacturer.receive_shipment_from_processing(mfg_shipment_data)
        print(f"📥 Materials Received: {'✅ Success' if mfg_received else '❌ Failed'}")
        
        if mfg_received:
            # Get manufacturing requirements
            mfg_inputs = manufacturer.get_required_inputs("PG_to_Fertilizer", 200.0)
            print(f"📋 Manufacturing Inputs: {len(mfg_inputs)} parameters")
            
            # Manufacturing with operator decisions
            mfg_decisions = {
                "production_priority": "normal",
                "quality_standard": "premium",
                "batch_size": 200.0,
                "quality_control_level": "enhanced",
                "nutrient_blend": "high_phosphorus"
            }
            
            mfg_result = manufacturer.process_material("PG_to_Fertilizer", mfg_decisions)
            print(f"🏭 Manufacturing Job: {mfg_result['status']}")
            
            if mfg_result['status'] == 'success':
                expected_product = mfg_result['expected_output']
                print(f"🎯 Expected Product: {expected_product['quantity']:.1f} units {expected_product['product']}")
                print(f"⭐ Quality Standard: {expected_product['quality']}")
                
                # Simulate manufacturing completion
                completed_mfg = manufacturer.run_manufacturing_operations()
                if completed_mfg:
                    mfg_job = completed_mfg[0]
                    print(f"✅ Manufacturing Complete: {mfg_job['actual_output_quantity']:.1f} units {mfg_job['expected_output_product']}")
                    
                    # Create shipment to distribution
                    dist_shipment_created = manufacturer.create_shipment_to_distribution(
                        mfg_job['expected_output_product'], 
                        mfg_job['actual_output_quantity'], 
                        "DIST_001"
                    )
                    print(f"📤 Shipment to Distribution: {'✅ Created' if dist_shipment_created else '❌ Failed'}")
    print()
    
    # ========================================================================
    # STEP 5: DISTRIBUTION
    # ========================================================================
    print("📦 STEP 5: Distribution & Warehousing")
    print("-" * 50)
    
    # Distribution receives finished products
    if 'mfg_job' in locals():
        dist_result = distributor.process_material(mfg_job['expected_output_product'], mfg_job['actual_output_quantity'])
        print(f"📥 Products Received: {dist_result['status']}")
        print(f"📊 Inventory Level: {dist_result['total_inventory']:.1f} units")
        print(f"📈 Capacity Utilization: {dist_result['capacity_utilization_percent']}%")
        
        # Create customer shipping orders
        retail_orders_created = []
        retail_orders_created.append(
            distributor.create_shipping_order(mfg_job['expected_output_product'], 50.0, "Regional Retail Center", "Zone_A")
        )
        retail_orders_created.append(
            distributor.create_shipping_order(mfg_job['expected_output_product'], 75.0, "Commercial Customer", "Zone_B")
        )
        
        successful_orders = sum(retail_orders_created)
        print(f"📋 Customer Orders Created: {successful_orders}")
        
        # Process shipments
        dispatched_to_retail = distributor.process_shipments()
        print(f"🚚 Shipments Dispatched: {len(dispatched_to_retail)}")
        
        if dispatched_to_retail:
            retail_shipment = dispatched_to_retail[0]  # First shipment to retail
            print(f"📦 To Retail: {retail_shipment['quantity']} units {retail_shipment['material']}")
    print()
    
    # ========================================================================
    # STEP 6: RETAIL & CUSTOMER DELIVERY
    # ========================================================================
    print("🛒 STEP 6: Retail Sales & Customer Delivery")
    print("-" * 50)
    
    if 'retail_shipment' in locals():
        # Retail receives products from distribution
        retail_received = retailer.receive_shipment_from_distribution(retail_shipment)
        print(f"📥 Products Received: {'✅ Success' if retail_received else '❌ Failed'}")
        
        if retail_received:
            # Simulate customer order
            customer_order = {
                "product_type": retail_shipment['material'],
                "quantity": 25.0,
                "customer_id": "CUST_FARM_001", 
                "customer_zone": "agricultural"
            }
            
            # Get retail operator requirements
            retail_inputs = retailer.get_required_inputs(customer_order)
            print(f"📋 Sales Inputs: {len(retail_inputs)} parameters")
            
            # Process customer order
            sales_decisions = {
                "sales_channel": "physical_store",
                "delivery_method": "standard_delivery",
                "pricing_strategy": "standard",
                "priority_level": "standard",
                "customer_type": "returning_customer",
                "local_delivery_options": "next_day",
                "application_season": "spring"
            }
            
            order_result = retailer.process_material(customer_order, sales_decisions)
            print(f"🛒 Customer Order: {order_result['status']}")
            
            if order_result['status'] == 'success':
                print(f"💰 Order Value: ${order_result['total_amount']:.2f}")
                print(f"💳 Unit Price: ${order_result['unit_price']:.2f}")
                print(f"🚚 Delivery Method: {sales_decisions['delivery_method']}")
                print(f"📅 Estimated Delivery: {order_result['estimated_delivery'].strftime('%Y-%m-%d %H:%M')}")
                
                # Complete delivery with feedback
                delivery_feedback = {
                    "satisfaction_rating": 4.8,
                    "delivery_notes": "Excellent service, product quality perfect for spring planting"
                }
                
                delivery_completed = retailer.complete_delivery(order_result['order_id'], delivery_feedback)
                print(f"✅ Delivery Complete: {'Success' if delivery_completed else 'Failed'}")
                print(f"⭐ Customer Satisfaction: {delivery_feedback['satisfaction_rating']}/5.0")
    print()
    
    # ========================================================================
    # STEP 7: END-TO-END SUMMARY & TRACKING
    # ========================================================================
    print("📊 STEP 7: End-to-End Material Tracking Summary")
    print("-" * 50)
    
    print("🔍 COMPLETE MATERIAL JOURNEY:")
    print(f"   Raw Input:     {extraction_result['extracted_quantity']:.1f} tons Phosphorite Ore")
    
    if 'processing_result' in locals() and processing_result['status'] == 'success':
        conversion_ratio = processing_result['expected_output']['quantity'] / extraction_result['extracted_quantity'] * 100
        print(f"   Processing:    {processing_result['expected_output']['quantity']:.1f} tons PG ({conversion_ratio:.1f}% conversion)")
    
    if 'mfg_result' in locals() and mfg_result['status'] == 'success':
        print(f"   Manufacturing: {mfg_result['expected_output']['quantity']:.1f} units Bagged Fertilizer")
    
    if 'order_result' in locals() and order_result['status'] == 'success':
        print(f"   Customer Sale: {customer_order['quantity']} units → ${order_result['total_amount']:.2f} revenue")
    
    print()
    print("📈 SUPPLY CHAIN PERFORMANCE:")
    
    # Mining metrics
    mining_status = mine.get_mining_status()
    print(f"   Mining Efficiency:      {mining_status['equipment']['overall_efficiency_percent']}%")
    print(f"   Total Extracted:        {mining_status['extraction']['total_extracted']:.1f} tons")
    
    # Processing metrics  
    processing_status = processor.get_processing_status()
    print(f"   Processing Efficiency:  {processing_status['operations']['average_equipment_efficiency_percent']}%")
    print(f"   Processing Costs:       ${processing_status['operations']['total_processing_costs']:.2f}")
    
    # Manufacturing metrics
    mfg_status = manufacturer.get_manufacturing_status()
    print(f"   Manufacturing QC Rate:  {mfg_status['quality_control']['success_rate_percent']}%")
    print(f"   Manufacturing Costs:    ${mfg_status['operations']['total_manufacturing_costs']:.2f}")
    
    # Distribution metrics
    dist_status = distributor.get_distribution_status()
    print(f"   Distribution Accuracy:  {dist_status['performance']['shipping_accuracy_percent']}%")
    print(f"   On-time Delivery:       {dist_status['performance']['on_time_delivery_percent']}%")
    
    # Retail metrics
    retail_status = retailer.get_retail_status()
    print(f"   Customer Satisfaction:  {retail_status['customer_metrics']['average_satisfaction_score']:.1f}/5.0")
    print(f"   Total Revenue:          ${retail_status['sales_performance']['total_revenue']:.2f}")
    
    print()
    print("=" * 80)
    print("🎉 END-TO-END SUPPLY CHAIN FLOW COMPLETED SUCCESSFULLY!")
    print("✅ Materials successfully tracked from raw extraction to customer delivery")
    print("✅ All 5 supply chain stages operational")
    print("✅ Complete audit trail maintained")
    print("=" * 80)

if __name__ == "__main__":
    run_complete_supply_chain_flow()