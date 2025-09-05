"""
Enhanced Interactive Supply Chain Simulation System
===================================================

This system integrates all your agents and provides a complete end-to-end 
simulation from raw material injection to customer delivery, with REAL operator
input prompts at each decision point including distribution center names, 
product selections, and all key operational parameters.

Usage:
    python enhanced_supply_chain_simulator.py
"""

import logging 
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import random
from pathlib import Path 
import json
import sys
import os
import importlib.util

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InteractiveOperatorInterface:
    """Enhanced operator interface for collecting real inputs with validation"""
    
    def __init__(self, obsidian_vault_path: str = None):
        self.session_data = {
            'operator_name': None,
            'company_name': None,
            'session_start': datetime.now(),
            'decisions_made': []
        }
        # Initialize Obsidian saver (robust import regardless of folder name/spacing)
        self.obsidian_saver = self._init_obsidian_saver(obsidian_vault_path)
        self.clear_screen()

    def _init_obsidian_saver(self, vault_path: Optional[str]):
        """Import and construct ObsidianAutoSaver even if folder has spaces."""
        # Try loading from file path: src/Obsidian Integration/obsidian_auto_saver.py
        this_dir = Path(__file__).resolve().parents[1]
        spaced_dir = this_dir / 'Obsidian Integration'
        underscored_dir = this_dir / 'Obsidian_Integration'
        candidate_file = None
        if (spaced_dir / 'obsidian_auto_saver.py').exists():
            candidate_file = spaced_dir / 'obsidian_auto_saver.py'
        elif (underscored_dir / 'obsidian_auto_saver.py').exists():
            candidate_file = underscored_dir / 'obsidian_auto_saver.py'

        ObsidianAutoSaver = None
        if candidate_file is not None:
            spec = importlib.util.spec_from_file_location('obsidian_auto_saver', str(candidate_file))
            module = importlib.util.module_from_spec(spec)
            assert spec and spec.loader
            spec.loader.exec_module(module)  # type: ignore[attr-defined]
            ObsidianAutoSaver = getattr(module, 'ObsidianAutoSaver', None)

        # Fallback to package import if available
        if ObsidianAutoSaver is None:
            try:
                from src.Obsidian_Integration.obsidian_auto_saver import ObsidianAutoSaver as PkgSaver  # type: ignore
                ObsidianAutoSaver = PkgSaver
            except Exception:
                pass

        if ObsidianAutoSaver is None:
            raise ImportError("Could not import ObsidianAutoSaver. Ensure obsidian_auto_saver.py exists.")

        return ObsidianAutoSaver(vault_path)
    
    def clear_screen(self):
        """Clear the terminal screen for better UX"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def start_session(self):
        """Initialize operator session with company details"""
        print("🏭 INTERACTIVE SUPPLY CHAIN SIMULATION SYSTEM")
        print("=" * 60)
        print("Welcome to the Supply Chain Reconstruction Platform!")
        print("This system will guide you through setting up and running")
        print("a complete supply chain simulation from raw materials to customers.")
        print()
        
        # Get operator and company information
        self.session_data['operator_name'] = input("👤 Enter your name: ").strip()
        self.session_data['company_name'] = input("🏢 Enter your company name: ").strip()
        
        if not self.session_data['operator_name']:
            self.session_data['operator_name'] = "Supply Chain Operator"
        if not self.session_data['company_name']:
            self.session_data['company_name'] = "Industrial Company"
        
        print(f"\nWelcome, {self.session_data['operator_name']} from {self.session_data['company_name']}!")
        print("You will make key decisions at each stage of the supply chain.")
        input("\nPress Enter to begin the simulation setup...")
        self.clear_screen()
    
    def get_simulation_overview_inputs(self) -> Dict[str, Any]:
        """Get high-level simulation parameters"""
        print("📊 SIMULATION OVERVIEW SETUP")
        print("=" * 40)
        
        # Simulation scope
        print("What type of supply chain simulation would you like to run?")
        simulation_types = [
            "Mining to Manufacturing (Phosphate/Fertilizer)",
            "Mining to Steel Production", 
            "Full End-to-End (Mining to Customer)",
            "Custom Supply Chain"
        ]
        
        sim_type = self._get_choice("Select simulation type", simulation_types)
        
        # Time horizon
        time_horizons = ["1 Month", "3 Months", "6 Months", "1 Year", "Custom"]
        time_horizon = self._get_choice("Select simulation time horizon", time_horizons)
        
        if time_horizon == "Custom":
            custom_months = self._get_float_input("Enter simulation duration in months", min_val=1, max_val=60, default=6)
            time_horizon = f"{custom_months} Months"
        
        # Geographic scope
        print("\nWhere is your supply chain operation located?")
        regions = ["Middle East (Saudi Arabia/UAE)", "North America", "Europe", "Asia Pacific", "South America", "Other"]
        region = self._get_choice("Select primary region", regions)
        
        overview = {
            'simulation_type': sim_type,
            'time_horizon': time_horizon,
            'primary_region': region,
            'company_name': self.session_data['company_name'],
            'operator_name': self.session_data['operator_name']
        }
        
        self._log_decision('simulation_overview', overview)
        return overview
    
    def get_mining_facility_setup(self) -> Dict[str, Any]:
        """Get detailed mining facility configuration"""
        print("\n⛏️  MINING FACILITY CONFIGURATION")
        print("=" * 40)
        
        # Mining facility details
        facility_name = input("Enter mining facility name (e.g., 'Al-Kharsaah Mine'): ").strip()
        if not facility_name:
            facility_name = f"{self.session_data['company_name']} Mine"
        
        location = input("Enter mine location (e.g., 'Northern Province, Saudi Arabia'): ").strip()
        if not location:
            location = "Industrial Zone"
        
        # Ore selection with descriptions
        print("\nSelect the primary ore/mineral you extract:")
        ore_options = [
            ("Phosphorite Ore", "For fertilizer production (P2O5 content)"),
            ("Iron Ore", "For steel and metal production"),  
            ("Bauxite", "For aluminum production"),
            ("Copper Ore", "For copper and electrical applications"),
            ("Gold Ore", "Precious metal extraction"),
            ("Limestone", "For cement and construction materials")
        ]
        
        for i, (ore, desc) in enumerate(ore_options, 1):
            print(f"  {i}. {ore} - {desc}")
        
        ore_choice = self._get_indexed_choice("Select ore type", [ore for ore, _ in ore_options])
        
        # Mining capacity and rates
        print(f"\nConfiguring extraction parameters for {ore_choice}:")
        
        capacity = self._get_float_input(
            "Total mine storage capacity (tons)", 
            min_val=10000, max_val=10000000, default=500000
        )
        
        extraction_rate = self._get_float_input(
            "Hourly extraction rate (tons/hour)", 
            min_val=50, max_val=50000, default=2000
        )
        
        # Reserve estimates
        reserves = self._get_float_input(
            "Estimated total reserves (tons)", 
            min_val=capacity, max_val=100000000, default=5000000
        )
        
        # Quality parameters
        ore_quality = self._get_float_input(
            f"Average {ore_choice} quality grade (0.1-1.0)", 
            min_val=0.1, max_val=1.0, default=0.85
        )
        
        # Extraction quantity for this simulation
        quantity = self._get_float_input(
            "Quantity to extract for this simulation (tons)", 
            min_val=1000, max_val=capacity, default=100000
        )
        
        # Equipment configuration
        print(f"\nMining equipment status:")
        equipment_status = {}
        equipment_types = ["Drilling Equipment", "Excavation Equipment", "Transport Equipment", "Crushing Equipment"]
        
        for equipment in equipment_types:
            status_options = ["Operational", "Maintenance Required", "Under Repair"]
            status = self._get_choice(f"{equipment} status", status_options, default="Operational")
            equipment_status[equipment] = status
        
        mining_config = {
            'facility_name': facility_name,
            'location': location,
            'ore_type': ore_choice,
            'storage_capacity': capacity,
            'extraction_rate': extraction_rate,
            'total_reserves': reserves,
            'ore_quality': ore_quality,
            'extraction_quantity': quantity,
            'equipment_status': equipment_status
        }
        
        self._log_decision('mining_setup', mining_config)
        return mining_config
    
    def get_processing_facility_setup(self) -> Dict[str, Any]:
        """Get processing facility configuration"""
        print("\n⚗️  PROCESSING FACILITY CONFIGURATION")
        print("=" * 40)
        
        # Processing facility details
        facility_name = input("Enter processing facility name (e.g., 'Jubail Processing Complex'): ").strip()
        if not facility_name:
            facility_name = f"{self.session_data['company_name']} Processing Plant"
        
        # Processing methods based on ore type
        print("Select available processing methods:")
        methods = [
            "Chemical Processing (Acid treatment, beneficiation)",
            "Physical Processing (Crushing, grinding, separation)", 
            "Thermal Processing (Smelting, roasting)",
            "Beneficiation (Flotation, magnetic separation)",
            "Hydrometallurgy (Leaching, extraction)"
        ]
        
        selected_methods = []
        for i, method in enumerate(methods, 1):
            print(f"  {i}. {method}")
        
        print("Select multiple methods (enter numbers separated by commas, e.g., '1,2,4'):")
        method_input = input("Enter method numbers: ").strip()
        
        if method_input:
            try:
                method_indices = [int(x.strip()) - 1 for x in method_input.split(',')]
                selected_methods = [methods[i] for i in method_indices if 0 <= i < len(methods)]
            except:
                selected_methods = [methods[0]]  # Default to first method
        
        if not selected_methods:
            selected_methods = [methods[0]]
        
        # Processing capacity
        capacity = self._get_float_input(
            "Processing facility capacity (tons/hour)", 
            min_val=100, max_val=100000, default=5000
        )
        
        # Recipe configuration
        print(f"\nConfigure processing recipes:")
        
        target_efficiency = self._get_float_input(
            "Target conversion efficiency (0.5-0.95)", 
            min_val=0.5, max_val=0.95, default=0.82
        )
        
        quality_target = self._get_float_input(
            "Target output quality (0.7-0.98)", 
            min_val=0.7, max_val=0.98, default=0.87
        )
        
        processing_time = self._get_float_input(
            "Average processing time per batch (hours)", 
            min_val=1, max_val=24, default=4
        )
        
        processing_config = {
            'facility_name': facility_name,
            'processing_methods': selected_methods,
            'capacity': capacity,
            'target_efficiency': target_efficiency,
            'target_quality': quality_target,
            'processing_time_hours': processing_time
        }
        
        self._log_decision('processing_setup', processing_config)
        return processing_config
    
    def get_manufacturing_facility_setup(self) -> Dict[str, Any]:
        """Get manufacturing facility configuration"""
        print("\n🏭 MANUFACTURING FACILITY CONFIGURATION")
        print("=" * 40)
        
        # Manufacturing facility details
        facility_name = input("Enter manufacturing facility name (e.g., 'Industrial Manufacturing Complex'): ").strip()
        if not facility_name:
            facility_name = f"{self.session_data['company_name']} Manufacturing Plant"
        
        # Product selection
        print("Select products to manufacture:")
        product_options = [
            ("DAP Fertilizer", "Di-Ammonium Phosphate fertilizer"),
            ("TSP Fertilizer", "Triple Super Phosphate fertilizer"),
            ("MAP Fertilizer", "Mono-Ammonium Phosphate fertilizer"), 
            ("NPK Compound", "Nitrogen-Phosphorus-Potassium compound"),
            ("Steel Products", "Steel beams, rebar, structural steel"),
            ("Industrial Chemicals", "Phosphoric acid, sulfuric acid"),
            ("Custom Product", "Specify your own product")
        ]
        
        for i, (product, desc) in enumerate(product_options, 1):
            print(f"  {i}. {product} - {desc}")
        
        product_choice = self._get_indexed_choice("Select primary product", [p for p, _ in product_options])
        
        if product_choice == "Custom Product":
            custom_product = input("Enter your custom product name: ").strip()
            if custom_product:
                product_choice = custom_product
        
        # Production lines
        print(f"\nProduction line configuration for {product_choice}:")
        line_types = [
            "Chemical Production Line",
            "Bagging and Packaging Line", 
            "Bulk Loading Line",
            "Quality Control Line",
            "Blending and Mixing Line"
        ]
        
        selected_lines = []
        for i, line in enumerate(line_types, 1):
            use_line = input(f"Include {line}? (y/n) [y]: ").strip().lower()
            if use_line in ['', 'y', 'yes']:
                selected_lines.append(line)
        
        if not selected_lines:
            selected_lines = [line_types[0]]  # At least one line
        
        # Manufacturing capacity
        capacity = self._get_float_input(
            "Manufacturing capacity (units/hour)", 
            min_val=100, max_val=100000, default=3000
        )
        
        # Quality standards
        quality_standards = ["Export Grade", "Premium", "Standard", "Industrial Grade"]
        quality_standard = self._get_choice("Default quality standard", quality_standards)
        
        # Production efficiency
        efficiency = self._get_float_input(
            "Target production efficiency (0.8-0.98)", 
            min_val=0.8, max_val=0.98, default=0.94
        )
        
        manufacturing_config = {
            'facility_name': facility_name,
            'primary_product': product_choice,
            'production_lines': selected_lines,
            'capacity': capacity,
            'quality_standard': quality_standard,
            'production_efficiency': efficiency
        }
        
        self._log_decision('manufacturing_setup', manufacturing_config)
        return manufacturing_config
    
    def get_distribution_center_setup(self) -> Dict[str, Any]:
        """Get comprehensive distribution center configuration"""
        print("\n📦 DISTRIBUTION CENTER CONFIGURATION")
        print("=" * 40)
        
        # Distribution center details
        center_name = input("Enter distribution center name (e.g., 'Jubail Export Terminal'): ").strip()
        if not center_name:
            center_name = f"{self.session_data['company_name']} Distribution Center"
        
        location = input("Enter distribution center location (e.g., 'Jubail Industrial City, Saudi Arabia'): ").strip()
        if not location:
            location = "Industrial Port"
        
        # Storage capacity
        storage_capacity = self._get_float_input(
            "Warehouse storage capacity (tons)", 
            min_val=1000, max_val=1000000, default=50000
        )
        
        # Export destinations
        print(f"\nConfigure export destinations:")
        print("Select countries/regions you export to:")
        
        country_regions = {
            "Asia Pacific": ["China", "India", "Japan", "South Korea", "Australia", "Singapore"],
            "Europe": ["Germany", "France", "Netherlands", "Turkey", "UK", "Italy"],
            "Americas": ["USA", "Brazil", "Argentina", "Mexico", "Canada"],
            "Africa": ["Morocco", "Egypt", "South Africa", "Nigeria", "Kenya"],
            "Middle East": ["UAE", "Iraq", "Kuwait", "Jordan", "Qatar"]
        }
        
        selected_destinations = {}
        
        for region, countries in country_regions.items():
            print(f"\n{region}:")
            for i, country in enumerate(countries, 1):
                print(f"  {i}. {country}")
            
            export_to_region = input(f"Export to {region}? (y/n): ").strip().lower()
            if export_to_region in ['y', 'yes']:
                country_input = input(f"Enter country numbers for {region} (comma-separated, e.g., 1,3,4): ").strip()
                
                if country_input:
                    try:
                        country_indices = [int(x.strip()) - 1 for x in country_input.split(',')]
                        selected_countries = [countries[i] for i in country_indices if 0 <= i < len(countries)]
                        if selected_countries:
                            selected_destinations[region] = selected_countries
                    except:
                        pass
        
        # Default destinations if none selected
        if not selected_destinations:
            selected_destinations = {"Asia Pacific": ["China", "India"]}
        
        # Shipping methods
        print(f"\nAvailable shipping methods:")
        shipping_methods = [
            "Bulk Carrier Ships",
            "Container Ships", 
            "Rail Transport",
            "Road Transport (Trucks)",
            "Pipeline Transport"
        ]
        
        selected_shipping = []
        for i, method in enumerate(shipping_methods, 1):
            use_method = input(f"Use {method}? (y/n) [y]: ").strip().lower()
            if use_method in ['', 'y', 'yes']:
                selected_shipping.append(method)
        
        if not selected_shipping:
            selected_shipping = [shipping_methods[0]]
        
        # Port/terminal facilities
        port_facilities = []
        facility_types = ["Loading Berths", "Bulk Handling Equipment", "Container Terminals", "Rail Connections"]
        
        for facility in facility_types:
            has_facility = input(f"Have {facility}? (y/n) [y]: ").strip().lower()
            if has_facility in ['', 'y', 'yes']:
                port_facilities.append(facility)
        
        distribution_config = {
            'center_name': center_name,
            'location': location,
            'storage_capacity': storage_capacity,
            'export_destinations': selected_destinations,
            'shipping_methods': selected_shipping,
            'port_facilities': port_facilities
        }
        
        self._log_decision('distribution_setup', distribution_config)
        return distribution_config
    
    def get_sales_organization_setup(self) -> Dict[str, Any]:
        """Get sales and customer management configuration"""
        print("\n🛒 SALES ORGANIZATION CONFIGURATION")
        print("=" * 40)
        
        # Sales organization details
        org_name = input("Enter sales organization name (e.g., 'International Sales Division'): ").strip()
        if not org_name:
            org_name = f"{self.session_data['company_name']} Sales"
        
        # Sales channels
        print(f"\nSelect sales channels:")
        channels = [
            "Bulk Export Sales",
            "Container Export Sales", 
            "Domestic Market Sales",
            "Spot Market Trading",
            "Long-term Contracts",
            "Government Sales",
            "Direct Customer Sales"
        ]
        
        selected_channels = []
        for i, channel in enumerate(channels, 1):
            use_channel = input(f"Use {channel}? (y/n) [y]: ").strip().lower()
            if use_channel in ['', 'y', 'yes']:
                selected_channels.append(channel)
        
        if not selected_channels:
            selected_channels = [channels[0]]
        
        # Customer types
        print(f"\nTarget customer types:")
        customer_types = [
            "Agricultural Cooperatives",
            "Industrial Manufacturers", 
            "Government Agencies",
            "Trading Companies",
            "Retail Distributors",
            "Construction Companies"
        ]
        
        target_customers = []
        for i, customer in enumerate(customer_types, 1):
            target = input(f"Target {customer}? (y/n) [y]: ").strip().lower()
            if target in ['', 'y', 'yes']:
                target_customers.append(customer)
        
        if not target_customers:
            target_customers = [customer_types[0]]
        
        # Pricing strategy
        pricing_strategies = [
            "Market Rate Pricing",
            "Competitive Pricing", 
            "Premium Pricing",
            "Cost-Plus Pricing",
            "Contract-Based Pricing"
        ]
        pricing_strategy = self._get_choice("Select primary pricing strategy", pricing_strategies)
        
        # Sales targets
        monthly_target = self._get_float_input(
            "Monthly sales target (tons)", 
            min_val=1000, max_val=500000, default=25000
        )
        
        target_margin = self._get_float_input(
            "Target profit margin (%)", 
            min_val=5, max_val=50, default=15
        )
        
        # Payment terms
        payment_terms = ["Cash in Advance", "Letter of Credit", "Open Account", "Documentary Collection"]
        preferred_payment = self._get_choice("Preferred payment terms", payment_terms)
        
        sales_config = {
            'organization_name': org_name,
            'sales_channels': selected_channels,
            'target_customers': target_customers,
            'pricing_strategy': pricing_strategy,
            'monthly_sales_target': monthly_target,
            'target_profit_margin': target_margin,
            'preferred_payment_terms': preferred_payment
        }
        
        self._log_decision('sales_setup', sales_config)
        return sales_config
    
    def get_operational_decisions(self, stage: str, request: Dict) -> Dict[str, Any]:
        """Get real-time operational decisions during simulation"""
        print(f"\n🎯 OPERATIONAL DECISION REQUIRED - {stage.upper()}")
        print("=" * 50)
        print(f"Request ID: {request.get('request_id', 'N/A')}")
        print(f"Stage: {stage}")
        print(f"Context: {request.get('operation', 'Processing required')}")
        print()
        
        decisions = {}
        
        if stage == 'processing':
            decisions = self._get_processing_operational_decisions(request)
        elif stage == 'manufacturing':
            decisions = self._get_manufacturing_operational_decisions(request)
        elif stage == 'distribution':
            decisions = self._get_distribution_operational_decisions(request)
        elif stage == 'retail':
            decisions = self._get_retail_operational_decisions(request)
        
        # Confirmation
        print(f"\n📋 DECISION SUMMARY:")
        for key, value in decisions.items():
            print(f"  {key}: {value}")
        
        confirm = input(f"\nConfirm these decisions? (y/n) [y]: ").strip().lower()
        if confirm in ['', 'y', 'yes']:
            self._log_decision(f'{stage}_operational', decisions)
            return decisions
        else:
            print("Decision cancelled. Please restart this decision point.")
            return self.get_operational_decisions(stage, request)
    
    def _get_processing_operational_decisions(self, request: Dict) -> Dict[str, Any]:
        """Get processing operational decisions"""
        material = request.get('material_type', 'Unknown Material')
        quantity = request.get('quantity', 0)
        
        print(f"Processing Decision Required:")
        print(f"Material: {material}")
        print(f"Available Quantity: {quantity:,.0f} tons")
        print()
        
        decisions = {}
        
        # Processing recipe
        recipes = ["Standard Processing", "High Quality Processing", "Fast Processing", "Efficient Processing"]
        decisions['processing_recipe'] = self._get_choice("Select processing method", recipes)
        
        # Quality target
        decisions['quality_target'] = self._get_float_input(
            "Target output quality (0.7-0.95)", 
            min_val=0.7, max_val=0.95, default=0.87
        )
        
        # Batch size
        max_batch = min(quantity, 50000)
        decisions['batch_size'] = self._get_float_input(
            f"Processing batch size (max: {max_batch:,.0f} tons)", 
            min_val=1000, max_val=max_batch, default=min(25000, max_batch)
        )
        
        # Priority
        priorities = ["Urgent", "Normal", "Batch Optimize"]
        decisions['priority'] = self._get_choice("Processing priority", priorities, default="Normal")
        
        return decisions
    
    def _get_manufacturing_operational_decisions(self, request: Dict) -> Dict[str, Any]:
        """Get manufacturing operational decisions"""
        print(f"Manufacturing Decision Required:")
        print()
        
        decisions = {}
        
        # Product selection
        products = ["DAP Fertilizer", "TSP Fertilizer", "NPK Compound", "Industrial Grade"]
        decisions['product_type'] = self._get_choice("Select product to manufacture", products)
        
        # Quality standard
        quality_levels = ["Export Grade", "Premium", "Standard", "Industrial"]
        decisions['quality_standard'] = self._get_choice("Select quality standard", quality_levels)
        
        # Production rate
        production_rates = ["Maximum", "Optimal", "Conservative"]
        decisions['production_rate'] = self._get_choice("Select production rate", production_rates, default="Optimal")
        
        # Batch size
        decisions['batch_size'] = self._get_float_input(
            "Production batch size (tons)", 
            min_val=1000, max_val=100000, default=20000
        )
        
        # Packaging
        packaging_options = ["Bulk", "50kg Bags", "1000kg Bags", "Custom Packaging"]
        decisions['packaging'] = self._get_choice("Select packaging type", packaging_options)
        
        return decisions
    
    def _get_distribution_operational_decisions(self, request: Dict) -> Dict[str, Any]:
        """Get distribution operational decisions"""
        print(f"Distribution Decision Required:")
        print()
        
        decisions = {}
        
        # Select destination from configured ones
        available_destinations = ["China", "India", "Brazil", "Germany", "UAE"]
        decisions['destination_country'] = self._get_choice("Select export destination", available_destinations)
        
        # Shipping method
        shipping_methods = ["Bulk Carrier", "Container Ship", "Combined Transport"]
        decisions['shipping_method'] = self._get_choice("Select shipping method", shipping_methods)
        
        # Delivery schedule
        schedules = ["Immediate", "Scheduled", "Seasonal Optimal", "Cost Optimal"]
        decisions['delivery_schedule'] = self._get_choice("Select delivery schedule", schedules, default="Scheduled")
        
        # Allocation percentage
        decisions['allocation_percent'] = self._get_float_input(
            "Percentage of inventory to allocate for this shipment", 
            min_val=10, max_val=100, default=70
        )
        
        return decisions
    
    def _get_retail_operational_decisions(self, request: Dict) -> Dict[str, Any]:
        """Get retail operational decisions"""
        print(f"Sales Decision Required:")
        print()
        
        decisions = {}
        
        # Customer type
        customer_types = ["Agricultural Coop", "Industrial Manufacturer", "Trading Company", "Government Agency"]
        decisions['customer_type'] = self._get_choice("Select customer type", customer_types)
        
        # Pricing approach
        pricing_approaches = ["Market Rate", "Competitive Price", "Premium Price", "Contract Price"]
        decisions['pricing_approach'] = self._get_choice("Select pricing approach", pricing_approaches)
        
        # Sales channel
        channels = ["Bulk Export", "Container Export", "Domestic Sales", "Spot Market"]
        decisions['sales_channel'] = self._get_choice("Select sales channel", channels)
        
        # Payment terms
        payment_terms = ["Cash Advance", "Letter of Credit", "Open Account", "Documentary Collection"]
        decisions['payment_terms'] = self._get_choice("Select payment terms", payment_terms, default="Letter of Credit")
        
        # Sales quantity
        decisions['sales_quantity'] = self._get_float_input(
            "Quantity to sell (tons)", 
            min_val=100, max_val=100000, default=10000
        )
        
        return decisions
    
    def _get_choice(self, prompt: str, options: List[str], default: str = None) -> str:
        """Get a choice from operator with validation"""
        while True:
            print(f"\n{prompt}:")
            for i, option in enumerate(options, 1):
                marker = " (default)" if option == default else ""
                print(f"  {i}. {option}{marker}")
            
            if default:
                choice_input = input(f"Enter choice (1-{len(options)}) or press Enter for default: ").strip()
                if not choice_input and default:
                    return default
            else:
                choice_input = input(f"Enter choice (1-{len(options)}): ").strip()
            
            try:
                choice_num = int(choice_input)
                if 1 <= choice_num <= len(options):
                    return options[choice_num - 1]
                else:
                    print(f"❌ Please enter a number between 1 and {len(options)}")
            except ValueError:
                print("❌ Please enter a valid number")
    
    def _get_indexed_choice(self, prompt: str, options: List[str]) -> str:
        """Get indexed choice (simplified version of _get_choice)"""
        return self._get_choice(prompt, options)
    
    def _get_float_input(self, prompt: str, min_val: float = None, max_val: float = None, default: float = None) -> float:
        """Get float input from operator with validation"""
        while True:
            range_info = ""
            if min_val is not None and max_val is not None:
                range_info = f" ({min_val:,.0f}-{max_val:,.0f})"
            elif min_val is not None:
                range_info = f" (min: {min_val:,.0f})"
            elif max_val is not None:
                range_info = f" (max: {max_val:,.0f})"
            
            default_info = f" [default: {default:,.0f}]" if default is not None else ""
            
            user_input = input(f"{prompt}{range_info}{default_info}: ").strip()
            
            if not user_input and default is not None:
                return default
            
            try:
                value = float(user_input)
                
                if min_val is not None and value < min_val:
                    print(f"❌ Value must be at least {min_val:,.0f}")
                    continue
                
                if max_val is not None and value > max_val:
                    print(f"❌ Value must be at most {max_val:,.0f}")
                    continue
                
                return value
                
            except ValueError:
                print("❌ Please enter a valid number")
    
    def _log_decision(self, stage: str, decision: Dict):
        """Log operator decision for audit trail"""
        log_entry = {
            'stage': stage,
            'timestamp': datetime.now(),
            'operator': self.session_data['operator_name'],
            'decision': decision
        }
        self.session_data['decisions_made'].append(log_entry)
    
    def save_session_log(self, filename: str = None):
        """Save session directly to Obsidian vault only"""
        # Convert session data to simulation results format for Obsidian
        simulation_results = {
            'simulation_id': f"SIM_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'start_time': self.session_data['session_start'],
            'end_time': datetime.now(),
            'duration': str(datetime.now() - self.session_data['session_start']),
            'simulation_config': {
                'overview': {
                    'company_name': self.session_data['company_name'],
                    'operator_name': self.session_data['operator_name'],
                    'simulation_type': 'Interactive Configuration'
                }
            },
            'operator_decisions': self.session_data['decisions_made'],
            'final_metrics': {},
            'material_flow': [],
            'stages': {}
        }

        # Save only to Obsidian
        obsidian_notes = self.obsidian_saver.save_simulation_to_vault(simulation_results)

        print(f"📁 Session saved to Obsidian vault: {self.obsidian_saver.vault_path}")
        print(f"🔍 Open in Obsidian to view your session notes!")

        return obsidian_notes


class EnhancedSupplyChainSimulator:
    """
    Enhanced supply chain simulation system with complete operator interaction
    """
    
    def __init__(self, obsidian_vault_path: str = None):
        """Initialize the enhanced simulation system"""
        self.operator_interface = InteractiveOperatorInterface(obsidian_vault_path)
        self.simulation_config = {}
        self.agents = {}
        self.material_traces = {}
        self.operator_requests = []
        self.simulation_results = []
        
        logger.info("Enhanced Supply Chain Simulator initialized")
    
    def run_interactive_simulation(self) -> Dict:
        """
        Run complete interactive simulation with operator inputs at each stage
        """
        print("🚀 STARTING INTERACTIVE SUPPLY CHAIN SIMULATION")
        print("=" * 60)
        
        # Start operator session
        self.operator_interface.start_session()
        
        # Phase 1: Get simulation overview
        overview = self.operator_interface.get_simulation_overview_inputs()
        self.simulation_config['overview'] = overview
        
        # Phase 2: Configure all facilities
        self._configure_all_facilities()
        
        # Phase 3: Initialize agents with operator configurations
        self._initialize_agents_from_config()
        
        # Phase 4: Run simulation with operational decisions
        simulation_results = self._run_simulation_with_operator_decisions()
        
        # Phase 5: Generate comprehensive results
        final_results = self._generate_final_results(simulation_results)
        
        # Save full results to Obsidian vault
        try:
            obsidian_notes = self.operator_interface.obsidian_saver.save_simulation_to_vault(final_results)
            final_results['obsidian_notes'] = obsidian_notes
        except Exception as e:
            logger.exception("Failed to save results to Obsidian vault: %s", e)
        
        return final_results
    
    def _configure_all_facilities(self):
        """Configure all facilities with operator inputs"""
        
        # Mining facility configuration
        mining_config = self.operator_interface.get_mining_facility_setup()
        self.simulation_config['mining'] = mining_config
        
        # Processing facility configuration  
        processing_config = self.operator_interface.get_processing_facility_setup()
        self.simulation_config['processing'] = processing_config
        
        # Manufacturing facility configuration
        manufacturing_config = self.operator_interface.get_manufacturing_facility_setup()
        self.simulation_config['manufacturing'] = manufacturing_config
        
        # Distribution center configuration
        distribution_config = self.operator_interface.get_distribution_center_setup()
        self.simulation_config['distribution'] = distribution_config
        
        # Sales organization configuration
        sales_config = self.operator_interface.get_sales_organization_setup()
        self.simulation_config['sales'] = sales_config
        
        print("\n✅ ALL FACILITIES CONFIGURED")
        print("Ready to start simulation with your custom supply chain!")
        input("Press Enter to begin material flow simulation...")
    
    def _initialize_agents_from_config(self):
        """Initialize all agents using operator configurations"""
        
        # Mining Agent
        mining_cfg = self.simulation_config['mining']
        self.agents['mining'] = {
            'agent_id': 'MINE_001',
            'name': mining_cfg['facility_name'],
            'location': mining_cfg['location'],
            'capacity': mining_cfg['storage_capacity'],
            'ore_types': [mining_cfg['ore_type']],
            'extraction_rate': mining_cfg['extraction_rate'],
            'ore_reserves': {mining_cfg['ore_type']: mining_cfg['total_reserves']},
            'ore_quality': {mining_cfg['ore_type']: mining_cfg['ore_quality']},
            'current_inventory': {mining_cfg['ore_type']: 0.0},
            'equipment_status': mining_cfg['equipment_status']
        }
        
        # Processing Agent
        processing_cfg = self.simulation_config['processing']
        self.agents['processing'] = {
            'agent_id': 'PROC_001',
            'name': processing_cfg['facility_name'],
            'capacity': processing_cfg['capacity'],
            'processing_methods': processing_cfg['processing_methods'],
            'target_efficiency': processing_cfg['target_efficiency'],
            'target_quality': processing_cfg['target_quality'],
            'recipes': {
                f"{mining_cfg['ore_type']}_processing": {
                    'input_material': mining_cfg['ore_type'],
                    'output_material': f"Processed_{mining_cfg['ore_type'].replace(' ', '_')}",
                    'conversion_ratio': processing_cfg['target_efficiency'],
                    'processing_time_hours': processing_cfg['processing_time_hours'],
                    'energy_cost_per_ton': 45.0,
                    'required_method': processing_cfg['processing_methods'][0] if processing_cfg['processing_methods'] else 'chemical_processing'
                }
            },
            'raw_storage': {},
            'processed_storage': {}
        }
        
        # Manufacturing Agent
        manufacturing_cfg = self.simulation_config['manufacturing']
        processed_material = f"Processed_{mining_cfg['ore_type'].replace(' ', '_')}"
        
        self.agents['manufacturing'] = {
            'agent_id': 'MFG_001',
            'name': manufacturing_cfg['facility_name'],
            'capacity': manufacturing_cfg['capacity'],
            'production_lines': manufacturing_cfg['production_lines'],
            'primary_product': manufacturing_cfg['primary_product'],
            'quality_standard': manufacturing_cfg['quality_standard'],
            'recipes': {
                f"{processed_material}_to_{manufacturing_cfg['primary_product'].replace(' ', '_')}": {
                    'input_materials': {processed_material: 1.0, 'additives': 0.05},
                    'output_product': manufacturing_cfg['primary_product'],
                    'output_quantity_ratio': manufacturing_cfg['production_efficiency'],
                    'production_time_hours': 3.0,
                    'energy_cost_per_unit': 25.0,
                    'required_line': manufacturing_cfg['production_lines'][0] if manufacturing_cfg['production_lines'] else 'chemical_production'
                }
            },
            'raw_inventory': {},
            'finished_goods': {}
        }
        
        # Distribution Agent
        distribution_cfg = self.simulation_config['distribution']
        self.agents['distribution'] = {
            'agent_id': 'DIST_001',
            'name': distribution_cfg['center_name'],
            'location': distribution_cfg['location'],
            'capacity': distribution_cfg['storage_capacity'],
            'export_destinations': distribution_cfg['export_destinations'],
            'shipping_methods': distribution_cfg['shipping_methods'],
            'port_facilities': distribution_cfg['port_facilities'],
            'current_inventory': {},
            'pending_shipments': {}
        }
        
        # Sales Agent
        sales_cfg = self.simulation_config['sales']
        self.agents['sales'] = {
            'agent_id': 'SALES_001',
            'name': sales_cfg['organization_name'],
            'sales_channels': sales_cfg['sales_channels'],
            'target_customers': sales_cfg['target_customers'],
            'pricing_strategy': sales_cfg['pricing_strategy'],
            'monthly_target': sales_cfg['monthly_sales_target'],
            'target_margin': sales_cfg['target_profit_margin'],
            'payment_terms': sales_cfg['preferred_payment_terms'],
            'inventory': {},
            'sales_history': []
        }
        
        logger.info("All agents initialized with operator configurations")
    
    def _run_simulation_with_operator_decisions(self) -> Dict:
        """Run simulation with real-time operator decisions"""
        
        simulation_results = {
            'simulation_id': f"SIM_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'start_time': datetime.now(),
            'stages': {},
            'material_flow': [],
            'operator_decisions': [],
            'final_results': {}
        }
        
        mining_cfg = self.simulation_config['mining']
        ore_type = mining_cfg['ore_type']
        extraction_quantity = mining_cfg['extraction_quantity']
        
        print(f"\n🔨 STAGE 1: MINING EXTRACTION")
        print("=" * 40)
        print(f"Extracting {extraction_quantity:,.0f} tons of {ore_type}")
        print(f"From: {mining_cfg['facility_name']}")
        
        # Update mining agent
        self.agents['mining']['current_inventory'][ore_type] = extraction_quantity
        
        mining_result = {
            'extracted_material': ore_type,
            'quantity_extracted': extraction_quantity,
            'ore_quality': mining_cfg['ore_quality'],
            'extraction_cost_per_ton': 15.0,
            'total_extraction_cost': extraction_quantity * 15.0,
            'facility_name': mining_cfg['facility_name']
        }
        
        simulation_results['stages']['mining'] = mining_result
        simulation_results['material_flow'].append({
            'stage': 'mining',
            'timestamp': datetime.now(),
            'material': ore_type,
            'quantity': extraction_quantity,
            'location': mining_cfg['facility_name']
        })
        
        input("Press Enter to proceed to Processing stage...")
        
        # STAGE 2: PROCESSING with operator decisions
        print(f"\n⚗️ STAGE 2: PROCESSING")
        print("=" * 40)
        
        processing_request = {
            'request_id': 'PROC_REQ_001',
            'material_type': ore_type,
            'quantity': extraction_quantity,
            'operation': 'material_processing'
        }
        
        processing_decisions = self.operator_interface.get_operational_decisions('processing', processing_request)
        
        # Process materials based on operator decisions
        processing_result = self._execute_processing(processing_request, processing_decisions)
        simulation_results['stages']['processing'] = processing_result
        simulation_results['operator_decisions'].append({
            'stage': 'processing',
            'decisions': processing_decisions,
            'result': processing_result
        })
        
        if processing_result['status'] == 'success':
            processed_material = processing_result['output_material']
            processed_quantity = processing_result['output_quantity']
            
            simulation_results['material_flow'].append({
                'stage': 'processing',
                'timestamp': datetime.now(),
                'material': processed_material,
                'quantity': processed_quantity,
                'location': self.simulation_config['processing']['facility_name']
            })
        
        input("Press Enter to proceed to Manufacturing stage...")
        
        # STAGE 3: MANUFACTURING with operator decisions
        print(f"\n🏭 STAGE 3: MANUFACTURING")
        print("=" * 40)
        
        manufacturing_request = {
            'request_id': 'MFG_REQ_001',
            'available_material': processed_material,
            'quantity': processed_quantity,
            'operation': 'product_manufacturing'
        }
        
        manufacturing_decisions = self.operator_interface.get_operational_decisions('manufacturing', manufacturing_request)
        
        # Manufacturing execution
        manufacturing_result = self._execute_manufacturing(manufacturing_request, manufacturing_decisions)
        simulation_results['stages']['manufacturing'] = manufacturing_result
        simulation_results['operator_decisions'].append({
            'stage': 'manufacturing',
            'decisions': manufacturing_decisions,
            'result': manufacturing_result
        })
        
        if manufacturing_result['status'] == 'success':
            finished_product = manufacturing_result['product_type']
            finished_quantity = manufacturing_result['quantity_produced']
            
            simulation_results['material_flow'].append({
                'stage': 'manufacturing',
                'timestamp': datetime.now(),
                'material': finished_product,
                'quantity': finished_quantity,
                'location': self.simulation_config['manufacturing']['facility_name']
            })
        
        input("Press Enter to proceed to Distribution stage...")
        
        # STAGE 4: DISTRIBUTION with operator decisions
        print(f"\n📦 STAGE 4: DISTRIBUTION")
        print("=" * 40)
        
        distribution_request = {
            'request_id': 'DIST_REQ_001',
            'available_products': {finished_product: finished_quantity},
            'operation': 'export_preparation'
        }
        
        distribution_decisions = self.operator_interface.get_operational_decisions('distribution', distribution_request)
        
        # Distribution execution
        distribution_result = self._execute_distribution(distribution_request, distribution_decisions)
        simulation_results['stages']['distribution'] = distribution_result
        simulation_results['operator_decisions'].append({
            'stage': 'distribution',
            'decisions': distribution_decisions,
            'result': distribution_result
        })
        
        if distribution_result['status'] == 'success':
            export_quantity = distribution_result['export_quantity']
            
            simulation_results['material_flow'].append({
                'stage': 'distribution',
                'timestamp': datetime.now(),
                'material': 'Export Ready Products',
                'quantity': export_quantity,
                'location': self.simulation_config['distribution']['center_name']
            })
        
        input("Press Enter to proceed to Sales stage...")
        
        # STAGE 5: SALES with operator decisions
        print(f"\n🛒 STAGE 5: SALES & CUSTOMER DELIVERY")
        print("=" * 40)
        
        sales_request = {
            'request_id': 'SALES_REQ_001',
            'available_inventory': {finished_product: export_quantity},
            'operation': 'customer_sales'
        }
        
        sales_decisions = self.operator_interface.get_operational_decisions('retail', sales_request)
        
        # Sales execution
        sales_result = self._execute_sales(sales_request, sales_decisions)
        simulation_results['stages']['sales'] = sales_result
        simulation_results['operator_decisions'].append({
            'stage': 'sales',
            'decisions': sales_decisions,
            'result': sales_result
        })
        
        if sales_result['status'] == 'success':
            total_revenue = sales_result['total_revenue']
            
            simulation_results['material_flow'].append({
                'stage': 'sales',
                'timestamp': datetime.now(),
                'material': 'Customer Sales',
                'quantity': sales_result['quantity_sold'],
                'location': self.simulation_config['sales']['organization_name']
            })
        
        simulation_results['end_time'] = datetime.now()
        simulation_results['duration'] = simulation_results['end_time'] - simulation_results['start_time']
        
        return simulation_results
    
    def _execute_processing(self, request: Dict, decisions: Dict) -> Dict:
        """Execute processing based on operator decisions"""
        
        processing_cfg = self.simulation_config['processing']
        input_quantity = request['quantity']
        
        # Apply operator decisions
        quality_target = decisions['quality_target']
        batch_size = decisions['batch_size']
        
        # Calculate outputs based on configuration and decisions
        base_efficiency = processing_cfg['target_efficiency']
        actual_efficiency = base_efficiency * quality_target
        output_quantity = batch_size * actual_efficiency
        
        # Update agent inventories
        ore_type = request['material_type']
        processed_material = f"Processed_{ore_type.replace(' ', '_')}"
        
        self.agents['processing']['raw_storage'][ore_type] = input_quantity
        self.agents['processing']['raw_storage'][ore_type] -= batch_size
        self.agents['processing']['processed_storage'][processed_material] = output_quantity
        
        processing_time = processing_cfg['processing_time_hours']
        energy_cost = batch_size * 45.0
        
        result = {
            'status': 'success',
            'input_material': ore_type,
            'input_quantity': batch_size,
            'output_material': processed_material,
            'output_quantity': output_quantity,
            'quality_achieved': quality_target,
            'processing_time_hours': processing_time,
            'energy_cost': energy_cost,
            'efficiency': actual_efficiency,
            'facility_name': processing_cfg['facility_name']
        }
        
        print(f"✅ Processing Complete:")
        print(f"   Input: {batch_size:,.0f} tons {ore_type}")
        print(f"   Output: {output_quantity:,.1f} tons {processed_material}")
        print(f"   Quality: {quality_target:.2f}")
        print(f"   Cost: ${energy_cost:,.2f}")
        
        return result
    
    def _execute_manufacturing(self, request: Dict, decisions: Dict) -> Dict:
        """Execute manufacturing based on operator decisions"""
        
        manufacturing_cfg = self.simulation_config['manufacturing']
        available_material = request['available_material']
        available_quantity = request['quantity']
        
        # Apply operator decisions
        product_type = decisions['product_type']
        quality_standard = decisions['quality_standard']
        batch_size = decisions['batch_size']
        
        # Use available quantity or batch size, whichever is smaller
        production_input = min(available_quantity, batch_size)
        
        # Calculate production output
        base_efficiency = manufacturing_cfg['production_efficiency']
        
        # Quality adjustments
        quality_multipliers = {"Export Grade": 0.95, "Premium": 0.92, "Standard": 0.94, "Industrial": 0.97}
        quality_factor = quality_multipliers.get(quality_standard, 0.94)
        
        actual_efficiency = base_efficiency * quality_factor
        output_quantity = production_input * actual_efficiency
        
        # Update agent inventories
        self.agents['manufacturing']['raw_inventory'][available_material] = available_quantity
        self.agents['manufacturing']['raw_inventory'][available_material] -= production_input
        self.agents['manufacturing']['finished_goods'][product_type] = output_quantity
        
        production_time = 3.5
        energy_cost = output_quantity * 25.0
        
        result = {
            'status': 'success',
            'input_material': available_material,
            'input_quantity': production_input,
            'product_type': product_type,
            'quantity_produced': output_quantity,
            'quality_standard': quality_standard,
            'production_time_hours': production_time,
            'energy_cost': energy_cost,
            'efficiency': actual_efficiency,
            'facility_name': manufacturing_cfg['facility_name']
        }
        
        print(f"✅ Manufacturing Complete:")
        print(f"   Input: {production_input:,.0f} tons {available_material}")
        print(f"   Output: {output_quantity:,.1f} units {product_type}")
        print(f"   Quality: {quality_standard}")
        print(f"   Cost: ${energy_cost:,.2f}")
        
        return result
    
    def _execute_distribution(self, request: Dict, decisions: Dict) -> Dict:
        """Execute distribution based on operator decisions"""
        
        distribution_cfg = self.simulation_config['distribution']
        available_products = request['available_products']
        
        # Apply operator decisions
        destination = decisions['destination_country']
        shipping_method = decisions['shipping_method']
        allocation_percent = decisions['allocation_percent']
        
        # Calculate export quantities
        total_available = sum(available_products.values())
        export_quantity = total_available * (allocation_percent / 100)
        
        # Update agent inventories
        for product, quantity in available_products.items():
            allocated = quantity * (allocation_percent / 100)
            self.agents['distribution']['current_inventory'][product] = quantity - allocated
        
        # Calculate shipping costs
        shipping_cost_per_ton = {"Bulk Carrier": 25, "Container Ship": 45, "Combined Transport": 35}
        cost_per_ton = shipping_cost_per_ton.get(shipping_method, 30)
        total_shipping_cost = export_quantity * cost_per_ton
        
        # Delivery time estimation
        delivery_estimates = {"Immediate": 14, "Scheduled": 21, "Seasonal Optimal": 35, "Cost Optimal": 28}
        delivery_days = delivery_estimates.get(decisions['delivery_schedule'], 21)
        
        result = {
            'status': 'success',
            'destination_country': destination,
            'export_quantity': export_quantity,
            'shipping_method': shipping_method,
            'shipping_cost': total_shipping_cost,
            'estimated_delivery_days': delivery_days,
            'allocation_percent': allocation_percent,
            'center_name': distribution_cfg['center_name']
        }
        
        print(f"✅ Distribution Complete:")
        print(f"   Export to: {destination}")
        print(f"   Quantity: {export_quantity:,.1f} tons")
        print(f"   Method: {shipping_method}")
        print(f"   Cost: ${total_shipping_cost:,.2f}")
        print(f"   Delivery: {delivery_days} days")
        
        return result
    
    def _execute_sales(self, request: Dict, decisions: Dict) -> Dict:
        """Execute sales based on operator decisions"""
        
        sales_cfg = self.simulation_config['sales']
        available_inventory = request['available_inventory']
        
        # Apply operator decisions
        customer_type = decisions['customer_type']
        pricing_approach = decisions['pricing_approach']
        sales_quantity = decisions['sales_quantity']
        
        # Use available inventory or requested quantity, whichever is smaller
        total_available = sum(available_inventory.values())
        actual_sales_quantity = min(total_available, sales_quantity)
        
        # Calculate pricing
        base_prices = {"DAP Fertilizer": 320, "TSP Fertilizer": 285, "NPK Compound": 350}
        
        # Get base price for first product (simplified)
        first_product = list(available_inventory.keys())[0]
        base_price = base_prices.get(first_product, 300)
        
        # Apply pricing strategy
        pricing_multipliers = {
            "Market Rate": 1.0, "Competitive Price": 0.95, 
            "Premium Price": 1.08, "Contract Price": 0.98
        }
        price_multiplier = pricing_multipliers.get(pricing_approach, 1.0)
        final_price = base_price * price_multiplier
        
        # Calculate revenue
        total_revenue = actual_sales_quantity * final_price
        
        # Update agent inventories
        for product, quantity in available_inventory.items():
            sold_from_product = min(quantity, actual_sales_quantity)
            self.agents['sales']['inventory'][product] = quantity - sold_from_product
            actual_sales_quantity -= sold_from_product
            if actual_sales_quantity <= 0:
                break
        
        result = {
            'status': 'success',
            'customer_type': customer_type,
            'pricing_approach': pricing_approach,
            'sales_channel': decisions['sales_channel'],
            'payment_terms': decisions['payment_terms'],
            'quantity_sold': sales_quantity,
            'unit_price': final_price,
            'total_revenue': total_revenue,
            'organization_name': sales_cfg['organization_name']
        }
        
        print(f"✅ Sales Complete:")
        print(f"   Customer: {customer_type}")
        print(f"   Quantity: {sales_quantity:,.0f} tons")
        print(f"   Price: ${final_price:.2f}/ton")
        print(f"   Revenue: ${total_revenue:,.2f}")
        print(f"   Payment: {decisions['payment_terms']}")
        
        return result
    
    def _generate_final_results(self, simulation_results: Dict) -> Dict:
        """Generate comprehensive final results"""
        
        print(f"\n📊 GENERATING FINAL RESULTS")
        print("=" * 40)
        
        # Extract key metrics from simulation stages
        mining = simulation_results['stages'].get('mining', {})
        processing = simulation_results['stages'].get('processing', {})
        manufacturing = simulation_results['stages'].get('manufacturing', {})
        distribution = simulation_results['stages'].get('distribution', {})
        sales = simulation_results['stages'].get('sales', {})
        
        # Calculate overall performance metrics
        final_metrics = {
            'input_ore_tons': mining.get('quantity_extracted', 0),
            'processed_material_tons': processing.get('output_quantity', 0),
            'manufactured_products_units': manufacturing.get('quantity_produced', 0),
            'exported_tons': distribution.get('export_quantity', 0),
            'sold_tons': sales.get('quantity_sold', 0),
            'total_revenue': sales.get('total_revenue', 0),
            'ore_to_product_conversion_rate': 0,
            'revenue_per_ton_ore': 0,
            'total_costs': 0,
            'net_profit': 0,
            'profit_margin_percent': 0
        }
        
        # Calculate conversion rates
        if final_metrics['input_ore_tons'] > 0:
            final_metrics['ore_to_product_conversion_rate'] = (
                final_metrics['manufactured_products_units'] / final_metrics['input_ore_tons']
            )
            final_metrics['revenue_per_ton_ore'] = (
                final_metrics['total_revenue'] / final_metrics['input_ore_tons']
            )
        
        # Calculate total costs
        costs = [
            mining.get('total_extraction_cost', 0),
            processing.get('energy_cost', 0),
            manufacturing.get('energy_cost', 0),
            distribution.get('shipping_cost', 0)
        ]
        final_metrics['total_costs'] = sum(costs)
        final_metrics['net_profit'] = final_metrics['total_revenue'] - final_metrics['total_costs']
        
        if final_metrics['total_revenue'] > 0:
            final_metrics['profit_margin_percent'] = (
                final_metrics['net_profit'] / final_metrics['total_revenue'] * 100
            )
        
        # Add final metrics to simulation results
        simulation_results['final_metrics'] = final_metrics
        simulation_results['simulation_config'] = self.simulation_config
        
        # Print summary
        self._print_final_summary(simulation_results)

        print(f"\n💾 SAVING SIMULATION DATA TO OBSIDIAN")
        print("=" * 40)

        # Save only to Obsidian vault
        obsidian_notes = self.operator_interface.obsidian_saver.save_simulation_to_vault(
            simulation_results
        )
        simulation_results['obsidian_notes'] = obsidian_notes
        
        # Optional scenario saving (disabled: no local scenario manager available)
        # Keeping UX message to indicate completion
        print(f"📁 All data saved successfully to Obsidian vault!")
      
        return simulation_results
    
    def _print_final_summary(self, results: Dict):
        """Print comprehensive simulation summary"""
        
        print("\n" + "=" * 80)
        print("🏆 INTERACTIVE SUPPLY CHAIN SIMULATION COMPLETE")
        print("=" * 80)
        
        overview = self.simulation_config['overview']
        print(f"Company: {overview['company_name']}")
        print(f"Operator: {overview['operator_name']}")
        print(f"Simulation Type: {overview['simulation_type']}")
        print(f"Duration: {results['duration']}")
        print()
        
        print("🏗️  FACILITY CONFIGURATION:")
        print("-" * 40)
        print(f"Mining: {self.simulation_config['mining']['facility_name']}")
        print(f"Processing: {self.simulation_config['processing']['facility_name']}")
        print(f"Manufacturing: {self.simulation_config['manufacturing']['facility_name']}")
        print(f"Distribution: {self.simulation_config['distribution']['center_name']}")
        print(f"Sales: {self.simulation_config['sales']['organization_name']}")
        print()
        
        print("📈 MATERIAL FLOW SUMMARY:")
        print("-" * 40)
        for flow in results['material_flow']:
            timestamp = flow['timestamp'].strftime('%H:%M:%S')
            stage = flow['stage'].upper().ljust(12)
            material = flow['material'].ljust(25)
            quantity = f"{flow['quantity']:>10,.1f}"
            print(f"{timestamp} | {stage} | {material} | {quantity}")
        print()
        
        print("🎯 OPERATOR DECISIONS SUMMARY:")
        print("-" * 40)
        for decision in results['operator_decisions']:
            stage = decision['stage'].upper()
            print(f"{stage}:")
            for key, value in decision['decisions'].items():
                print(f"  {key}: {value}")
            print()
        
        print("💰 FINANCIAL PERFORMANCE:")
        print("-" * 40)
        metrics = results['final_metrics']
        print(f"Total Revenue:           ${metrics['total_revenue']:>12,.2f}")
        print(f"Total Costs:             ${metrics['total_costs']:>12,.2f}")
        print(f"Net Profit:              ${metrics['net_profit']:>12,.2f}")
        print(f"Profit Margin:           {metrics['profit_margin_percent']:>12.1f}%")
        print(f"Revenue per Ton Ore:     ${metrics['revenue_per_ton_ore']:>12.2f}")
        print()
        
        print("⚡ OPERATIONAL EFFICIENCY:")
        print("-" * 40)
        print(f"Raw Material Input:      {metrics['input_ore_tons']:>12,.0f} tons")
        print(f"Processed Output:        {metrics['processed_material_tons']:>12,.1f} tons")
        print(f"Manufactured Products:   {metrics['manufactured_products_units']:>12,.1f} units")
        print(f"Products Exported:       {metrics['exported_tons']:>12,.1f} tons")
        print(f"Products Sold:           {metrics['sold_tons']:>12,.1f} tons")
        print(f"Conversion Efficiency:   {metrics['ore_to_product_conversion_rate']:>12.2f}")
        print()
        
        print("=" * 80)
        print("✅ Your custom supply chain simulation has been completed successfully!")
        print("📁 All decisions and results have been saved to your session log.")
        print("=" * 80)


def main():
    try:
        print("🏭 SUPPLY CHAIN SIMULATOR - OBSIDIAN INTEGRATION")
        print("=" * 60)
        print("📝 All simulation data will be saved to your Obsidian vault")
        print("🚫 No local files will be created in the repository")
        print()
        
        # Optional: Let user specify vault location
        vault_choice = input("Use default vault location? (y/n) [y]: ").strip().lower()
        vault_path = None
        
        if vault_choice in ['n', 'no']:
            custom_path = input("Enter custom Obsidian vault path: ").strip()
            if custom_path:
                vault_path = custom_path
        
        # Create enhanced simulator with Obsidian-only mode
        simulator = EnhancedSupplyChainSimulator(vault_path)
        results = simulator.run_interactive_simulation()
        simulator._print_final_summary(results)
        print("\n✅ Saved to Obsidian vault.")
        return 0
    
def run_demo_with_prompts():
    """Run a quick demo that shows the operator input prompts"""
    
    print("🚀 SUPPLY CHAIN OPERATOR INPUT DEMO")
    print("=" * 50)
    print("This demo shows you all the operator input prompts")
    print("without running the full simulation.")
    print()
    
    interface = InteractiveOperatorInterface()
    interface.start_session()
    
    # Show all the input prompts
    overview = interface.get_simulation_overview_inputs()
    print(f"\n✅ Overview configured: {overview['simulation_type']}")
    
    mining = interface.get_mining_facility_setup()
    print(f"✅ Mining configured: {mining['facility_name']}")
    
    processing = interface.get_processing_facility_setup()
    print(f"✅ Processing configured: {processing['facility_name']}")
    
    manufacturing = interface.get_manufacturing_facility_setup()
    print(f"✅ Manufacturing configured: {manufacturing['facility_name']}")
    
    distribution = interface.get_distribution_center_setup()
    print(f"✅ Distribution configured: {distribution['center_name']}")
    
    sales = interface.get_sales_organization_setup()
    print(f"✅ Sales configured: {sales['organization_name']}")
    
    print(f"\n🎯 DEMO COMPLETE!")
    print("Your supply chain configuration:")
    print(f"  Company: {overview['company_name']}")
    print(f"  Mining: {mining['facility_name']} ({mining['ore_type']})")
    print(f"  Processing: {processing['facility_name']}")
    print(f"  Manufacturing: {manufacturing['facility_name']} ({manufacturing['primary_product']})")
    print(f"  Distribution: {distribution['center_name']}")
    print(f"  Sales: {sales['organization_name']}")
    
    # Save demo configuration
    interface.save_session_log("demo_configuration.json")

def quick_start_guide():
    """Print quick start guide for operators"""
    
    print("📚 SUPPLY CHAIN SIMULATOR - QUICK START GUIDE")
    print("=" * 60)
    print()
    print("🎯 WHAT THIS SYSTEM DOES:")
    print("- Recreates your complete supply chain from raw materials to customers")
    print("- Asks YOU to make real operational decisions at each stage")
    print("- Tracks materials end-to-end through your custom supply chain")
    print("- Provides detailed performance and financial analysis")
    print()
    print("🏗️  STAGES YOU'LL CONFIGURE:")
    print("1. Mining Facility      - Ore extraction and mining operations")
    print("2. Processing Plant     - Transform raw ore into processed materials")
    print("3. Manufacturing        - Create finished products from processed materials")
    print("4. Distribution Center  - Export preparation and logistics")
    print("5. Sales Organization   - Customer sales and delivery")
    print()
    print("⚙️  DECISIONS YOU'LL MAKE:")
    print("- Facility names and locations")
    print("- Production capacities and rates")
    print("- Product types and quality standards")
    print("- Export destinations and shipping methods")
    print("- Pricing strategies and customer types")
    print("- Real-time operational decisions during simulation")
    print()
    print("📊 WHAT YOU'LL GET:")
    print("- Complete material flow tracking")
    print("- Financial performance analysis")
    print("- Operational efficiency metrics")
    print("- Detailed decision audit trail")
    print("- Exportable results and session logs")
    print()
    print("🚀 TO START:")
    print("python enhanced_supply_chain_simulator.py")
    print()
    print("💡 TIP: Have your company details ready:")
    print("- Company name and locations")
    print("- Production targets and capacities")
    print("- Export destinations and customer types")
    print("- Current operational parameters")
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Interactive Supply Chain Simulator')
    parser.add_argument('--demo', action='store_true', help='Run input prompts demo only')
    parser.add_argument('--guide', action='store_true', help='Show quick start guide')
    parser.add_argument('--full', action='store_true', help='Run full interactive simulation')
    
    args = parser.parse_args()
    
    if args.guide:
        quick_start_guide()
    elif args.demo:
        run_demo_with_prompts()
    elif args.full or len(sys.argv) == 1:
        # Default to full simulation
        main()
    else:
        print("Use --guide for instructions, --demo for input preview, or --full for complete simulation")
