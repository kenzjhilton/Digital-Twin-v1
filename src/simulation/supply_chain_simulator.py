"""
Complete Supply Chain Simulation System
========================================

This system integrates all your agents and provides a complete end-to-end 
simulation from raw material injection to customer delivery, with support
for Excel data input and operator decision points.

Usage:
    python complete_simulation.py
"""

from pandas import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import random
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SupplyChainSimulator:
    """
    Complete supply chain simulation system that integrates all agents
    and provides end-to-end material flow with Excel data support.
    """
    
    def __init__(self):
        """Initialize the simulation system"""
        self.agents = {}
        self.material_traces = {}
        self.simulation_data = {}
        self.operator_requests = []
        self.simulation_results = []
        
        # Initialize agents (these would import from your actual agent files)
        self._initialize_agents()
        
        logger.info("Supply Chain Simulator initialized")
    
    def _initialize_agents(self):
        """Initialize all supply chain agents with realistic parameters"""
        
        # Mining Agent - Phosphate extraction
        self.agents['mining'] = {
            'agent_id': 'MINE_AMX_001',
            'name': 'AMX Phosphate Mine',
            'capacity': 500000.0,  # 500K ton capacity
            'ore_types': ['Phosphorite Ore'],
            'extraction_rate': 15000.0,  # 15K tons/hour
            'ore_reserves': {'Phosphorite Ore': 2000000.0},  # 2M tons reserves
            'ore_quality': {'Phosphorite Ore': 0.85},
            'current_inventory': {'Phosphorite Ore': 0.0}
        }
        
        # Processing Agent - Convert ore to PG (Phosphoric Acid Grade)
        self.agents['processing'] = {
            'agent_id': 'PROC_AMX_001', 
            'name': 'AMX Phosphoric Acid Plant',
            'capacity': 200000.0,  # 200K ton capacity
            'processing_methods': ['chemical_processing', 'beneficiation'],
            'recipes': {
                'Phosphorite_to_PG': {
                    'input_material': 'Phosphorite Ore',
                    'output_material': 'PG',
                    'conversion_ratio': 0.82,  # 82% conversion efficiency
                    'processing_time_hours': 3.5,
                    'energy_cost_per_ton': 45.0,
                    'required_method': 'chemical_processing'
                }
            },
            'raw_storage': {},
            'processed_storage': {}
        }
        
        # Manufacturing Agent - Convert PG to finished fertilizer products
        self.agents['manufacturing'] = {
            'agent_id': 'MFG_AMX_001',
            'name': 'AMX Fertilizer Manufacturing Plant',
            'capacity': 150000.0,  # 150K units/hour
            'production_lines': ['chemical_production', 'bagging_line', 'bulk_loading'],
            'recipes': {
                'PG_to_DAP': {
                    'input_materials': {'PG': 1.0, 'ammonia': 0.15, 'additives': 0.03},
                    'output_product': 'DAP_Fertilizer',
                    'output_quantity_ratio': 0.94,
                    'production_time_hours': 2.8,
                    'energy_cost_per_unit': 22.0,
                    'required_line': 'chemical_production'
                },
                'PG_to_TSP': {
                    'input_materials': {'PG': 1.0, 'phosphoric_acid': 0.12, 'additives': 0.02},
                    'output_product': 'TSP_Fertilizer', 
                    'output_quantity_ratio': 0.91,
                    'production_time_hours': 3.2,
                    'energy_cost_per_unit': 26.0,
                    'required_line': 'chemical_production'
                }
            },
            'raw_inventory': {},
            'finished_goods': {}
        }
        
        # Distribution Agent - Export and logistics hub
        self.agents['distribution'] = {
            'agent_id': 'DIST_AMX_001',
            'name': 'AMX Export Terminal - Jubail',
            'capacity': 300000.0,  # 300K ton capacity
            'shipping_zones': ['Asia_Pacific', 'Europe', 'Americas', 'Africa', 'Middle_East'],
            'current_inventory': {},
            'pending_shipments': {},
            'export_routes': {
                'Asia_Pacific': ['China', 'India', 'Japan', 'South Korea'],
                'Europe': ['Germany', 'France', 'Netherlands', 'Turkey'],
                'Americas': ['Brazil', 'USA', 'Argentina', 'Mexico'],
                'Africa': ['Morocco', 'Egypt', 'South Africa', 'Nigeria'],
                'Middle_East': ['UAE', 'Iraq', 'Kuwait', 'Jordan']
            }
        }
        
        # Retail Agent - International customers and markets
        self.agents['retail'] = {
            'agent_id': 'RETAIL_AMX_001',
            'name': 'AMX International Sales',
            'capacity': 1000000.0,  # 1M unit capacity
            'sales_channels': ['bulk_export', 'container_export', 'domestic_sales'],
            'customer_zones': ['agricultural', 'industrial', 'government'],
            'inventory': {},
            'sales_history': []
        }
        
        logger.info("All agents initialized with realistic AMX parameters")
    
    def load_excel_data(self, excel_path: str) -> Dict[str, Any]:
        """
        Load and parse Excel data for simulation
        
        Args:
            excel_path: Path to the Excel file
            
        Returns:
            Dictionary with parsed production and export data
        """
        try:
            # Read Excel file
            xl = pd.ExcelFile(excel_path)
            logger.info(f"Loading Excel data from: {excel_path}")
            logger.info(f"Available sheets: {xl.sheet_names}")
            
            data = {'production': [], 'exports': [], 'raw_sheets': {}}
            
            # Store raw sheets for reference
            for sheet_name in xl.sheet_names:
                data['raw_sheets'][sheet_name] = xl.parse(sheet_name)
            
            # Parse production data (looking for P2O5 production)
            main_sheet = xl.parse(xl.sheet_names[0])
            
            # Find production row
            production_rows = main_sheet[
                main_sheet.iloc[:, 0].astype(str).str.contains(
                    r'Production.*P2O5', case=False, na=False, regex=True
                )
            ]
            
            if not production_rows.empty:
                prod_row = production_rows.iloc[0]
                for col in prod_row.index[2:]:  # Skip text columns
                    try:
                        year = int(float(col))
                        value = prod_row[col]
                        if pd.notnull(value) and value > 0:
                            data['production'].append({
                                'year': year,
                                'p2o5_ktons': float(value),
                                'ore_tons_estimated': float(value) * 3.2  # Estimate raw ore needed
                            })
                    except (ValueError, TypeError):
                        continue
            
            # Parse export data if available
            if 'break down export' in xl.sheet_names:
                export_sheet = xl.parse('break down export')
                years = [int(c) for c in export_sheet.columns if str(c).isdigit()]
                
                current_country = None
                for _, row in export_sheet.iterrows():
                    if pd.notnull(row.get('TRADITIONAL PRODUCTS')):
                        current_country = str(row['TRADITIONAL PRODUCTS']).strip()
                    
                    product = str(row.get('Unnamed: 1', '')).strip()
                    if product.lower() in {'product', 'tons', 'usd'} or not product:
                        continue
                    
                    for year in years:
                        tons_val = pd.to_numeric(row[year], errors='coerce')
                        if pd.notnull(tons_val) and tons_val > 0:
                            data['exports'].append({
                                'country': current_country,
                                'product': product,
                                'year': int(year),
                                'tons': float(tons_val)
                            })
            
            # Sort data chronologically
            data['production'] = sorted(data['production'], key=lambda x: x['year'])
            data['exports'] = sorted(data['exports'], key=lambda x: x['year'])
            
            logger.info(f"Loaded {len(data['production'])} production records")
            logger.info(f"Loaded {len(data['exports'])} export records")
            
            return data
            
        except Exception as e:
            logger.error(f"Error loading Excel data: {e}")
            return self._get_demo_data()
    
    def _get_demo_data(self) -> Dict[str, Any]:
        """Generate demo data if Excel file is not available"""
        logger.info("Using demo data for simulation")
        
        return {
            'production': [
                {'year': 2023, 'p2o5_ktons': 850, 'ore_tons_estimated': 2720},
                {'year': 2024, 'p2o5_ktons': 920, 'ore_tons_estimated': 2944},
                {'year': 2025, 'p2o5_ktons': 1000, 'ore_tons_estimated': 3200}
            ],
            'exports': [
                {'country': 'China', 'product': 'DAP', 'year': 2024, 'tons': 150000},
                {'country': 'India', 'product': 'TSP', 'year': 2024, 'tons': 120000},
                {'country': 'Brazil', 'product': 'DAP', 'year': 2024, 'tons': 80000},
                {'country': 'Turkey', 'product': 'TSP', 'year': 2024, 'tons': 60000}
            ]
        }
    
    def create_operator_request(self, stage: str, operation: str, context: Dict) -> str:
        """Create an operator input request"""
        request_id = f"REQ_{len(self.operator_requests):04d}"
        
        request = {
            'request_id': request_id,
            'stage': stage,
            'operation': operation,
            'context': context,
            'status': 'pending',
            'created_at': datetime.now(),
            'required_inputs': self._get_required_inputs(stage, operation, context)
        }
        
        self.operator_requests.append(request)
        logger.info(f"Created operator request {request_id} for {stage} - {operation}")
        
        return request_id
    
    def _get_required_inputs(self, stage: str, operation: str, context: Dict) -> Dict:
        """Define required operator inputs based on stage and operation"""
        
        if stage == 'processing' and operation == 'transform_ore':
            return {
                'recipe_selection': {
                    'type': 'choice',
                    'options': ['Phosphorite_to_PG'],
                    'description': 'Select processing recipe',
                    'required': True
                },
                'quality_target': {
                    'type': 'float',
                    'min': 0.70,
                    'max': 0.95,
                    'description': 'Target quality grade (0.70-0.95)',
                    'default': 0.85,
                    'required': True
                },
                'batch_size': {
                    'type': 'float',
                    'min': 1000,
                    'max': context.get('available_quantity', 50000),
                    'description': f"Batch size (max: {context.get('available_quantity', 50000)} tons)",
                    'default': min(20000, context.get('available_quantity', 20000)),
                    'required': True
                },
                'processing_priority': {
                    'type': 'choice',
                    'options': ['urgent', 'normal', 'batch_optimize'],
                    'description': 'Processing priority level',
                    'default': 'normal',
                    'required': True
                }
            }
        
        elif stage == 'manufacturing' and operation == 'produce_fertilizer':
            return {
                'product_type': {
                    'type': 'choice',
                    'options': ['DAP_Fertilizer', 'TSP_Fertilizer'],
                    'description': 'Select fertilizer product to manufacture',
                    'required': True
                },
                'quality_standard': {
                    'type': 'choice',
                    'options': ['export_grade', 'premium', 'standard'],
                    'description': 'Product quality standard',
                    'default': 'export_grade',
                    'required': True
                },
                'production_rate': {
                    'type': 'choice',
                    'options': ['maximum', 'optimal', 'conservative'],
                    'description': 'Production rate setting',
                    'default': 'optimal',
                    'required': True
                },
                'packaging_type': {
                    'type': 'choice',
                    'options': ['bulk', '50kg_bags', '1000kg_bags'],
                    'description': 'Product packaging configuration',
                    'default': 'bulk',
                    'required': True
                }
            }
        
        elif stage == 'distribution' and operation == 'prepare_export':
            return {
                'destination_country': {
                    'type': 'choice',
                    'options': context.get('available_countries', ['China', 'India', 'Brazil']),
                    'description': 'Export destination country',
                    'required': True
                },
                'shipping_method': {
                    'type': 'choice',
                    'options': ['bulk_carrier', 'container_ship', 'break_bulk'],
                    'description': 'Shipping method selection',
                    'default': 'bulk_carrier',
                    'required': True
                },
                'delivery_schedule': {
                    'type': 'choice',
                    'options': ['immediate', 'scheduled', 'seasonal_optimal'],
                    'description': 'Delivery timing preference',
                    'default': 'scheduled',
                    'required': True
                }
            }
        
        elif stage == 'retail' and operation == 'customer_sales':
            return {
                'pricing_strategy': {
                    'type': 'choice',
                    'options': ['market_rate', 'competitive', 'premium'],
                    'description': 'Pricing strategy for this sale',
                    'default': 'market_rate',
                    'required': True
                },
                'payment_terms': {
                    'type': 'choice',
                    'options': ['cash_advance', 'letter_of_credit', 'open_account'],
                    'description': 'Payment terms with customer',
                    'default': 'letter_of_credit',
                    'required': True
                },
                'delivery_terms': {
                    'type': 'choice',
                    'options': ['FOB', 'CFR', 'CIF'],
                    'description': 'International delivery terms',
                    'default': 'CFR',
                    'required': True
                }
            }
        
        return {}
    
    def process_operator_input(self, request_id: str, operator_inputs: Dict) -> Dict:
        """Process operator inputs and continue simulation"""
        
        # Find the request
        request = None
        for req in self.operator_requests:
            if req['request_id'] == request_id:
                request = req
                break
        
        if not request:
            return {'error': 'Request not found'}
        
        # Validate inputs
        validation_result = self._validate_inputs(request['required_inputs'], operator_inputs)
        if not validation_result['valid']:
            return {'error': f"Invalid inputs: {validation_result['errors']}"}
        
        # Process based on stage
        result = {}
        if request['stage'] == 'processing':
            result = self._process_ore_transformation(request, operator_inputs)
        elif request['stage'] == 'manufacturing':
            result = self._process_manufacturing(request, operator_inputs)
        elif request['stage'] == 'distribution':
            result = self._process_distribution(request, operator_inputs)
        elif request['stage'] == 'retail':
            result = self._process_retail_sales(request, operator_inputs)
        
        # Update request status
        request['status'] = 'completed'
        request['operator_inputs'] = operator_inputs
        request['result'] = result
        request['completed_at'] = datetime.now()
        
        return result
    
    def _validate_inputs(self, required_inputs: Dict, operator_inputs: Dict) -> Dict:
        """Validate operator inputs against requirements"""
        errors = []
        
        for input_name, spec in required_inputs.items():
            if spec.get('required', False) and input_name not in operator_inputs:
                errors.append(f"Missing required input: {input_name}")
                continue
            
            if input_name in operator_inputs:
                value = operator_inputs[input_name]
                input_type = spec.get('type')
                
                if input_type == 'choice' and value not in spec.get('options', []):
                    errors.append(f"Invalid choice for {input_name}: {value}")
                elif input_type == 'float':
                    try:
                        float_val = float(value)
                        min_val = spec.get('min')
                        max_val = spec.get('max')
                        if min_val is not None and float_val < min_val:
                            errors.append(f"{input_name} below minimum: {float_val} < {min_val}")
                        if max_val is not None and float_val > max_val:
                            errors.append(f"{input_name} above maximum: {float_val} > {max_val}")
                    except ValueError:
                        errors.append(f"Invalid numeric value for {input_name}: {value}")
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def _process_ore_transformation(self, request: Dict, inputs: Dict) -> Dict:
        """Process ore transformation in processing stage"""
        context = request['context']
        recipe = inputs['recipe_selection']
        batch_size = float(inputs['batch_size'])
        quality_target = float(inputs['quality_target'])
        
        # Get processing recipe
        recipe_data = self.agents['processing']['recipes'][recipe]
        
        # Calculate outputs
        conversion_ratio = recipe_data['conversion_ratio'] * quality_target
        output_quantity = batch_size * conversion_ratio
        processing_time = recipe_data['processing_time_hours']
        energy_cost = recipe_data['energy_cost_per_ton'] * batch_size
        
        # Update agent inventories
        input_material = recipe_data['input_material']
        output_material = recipe_data['output_material']
        
        # Remove from raw storage, add to processed storage
        if input_material not in self.agents['processing']['raw_storage']:
            self.agents['processing']['raw_storage'][input_material] = context['available_quantity']
        
        self.agents['processing']['raw_storage'][input_material] -= batch_size
        
        if output_material not in self.agents['processing']['processed_storage']:
            self.agents['processing']['processed_storage'][output_material] = 0
        
        self.agents['processing']['processed_storage'][output_material] += output_quantity
        
        result = {
            'status': 'success',
            'input_consumed': {input_material: batch_size},
            'output_produced': {output_material: output_quantity},
            'processing_time_hours': processing_time,
            'energy_cost': energy_cost,
            'quality_achieved': quality_target,
            'efficiency': conversion_ratio
        }
        
        logger.info(f"Processing completed: {batch_size} tons {input_material} → {output_quantity:.1f} tons {output_material}")
        
        return result
    
    def _process_manufacturing(self, request: Dict, inputs: Dict) -> Dict:
        """Process manufacturing stage"""
        product_type = inputs['product_type']
        quality_standard = inputs['quality_standard']
        
        # Find appropriate recipe
        recipe_name = f"PG_to_{product_type.split('_')[0]}"
        recipe_data = self.agents['manufacturing']['recipes'].get(recipe_name)
        
        if not recipe_data:
            return {'error': f'No recipe found for {product_type}'}
        
        # Calculate available input materials
        available_pg = self.agents['processing']['processed_storage'].get('PG', 0)
        max_production = available_pg / recipe_data['input_materials']['PG']
        
        # Use 80% of available materials
        production_quantity = max_production * 0.8
        
        # Calculate outputs
        output_quantity = production_quantity * recipe_data['output_quantity_ratio']
        production_time = recipe_data['production_time_hours']
        
        # Quality adjustments
        quality_multipliers = {'export_grade': 1.1, 'premium': 1.05, 'standard': 1.0}
        quality_mult = quality_multipliers.get(quality_standard, 1.0)
        adjusted_time = production_time * quality_mult
        energy_cost = recipe_data['energy_cost_per_unit'] * output_quantity * quality_mult
        
        # Update inventories
        for material, ratio in recipe_data['input_materials'].items():
            consumed = production_quantity * ratio
            if material == 'PG':
                self.agents['processing']['processed_storage']['PG'] -= consumed
            # For additives, assume unlimited supply
        
        # Add to finished goods
        if product_type not in self.agents['manufacturing']['finished_goods']:
            self.agents['manufacturing']['finished_goods'][product_type] = 0
        
        self.agents['manufacturing']['finished_goods'][product_type] += output_quantity
        
        result = {
            'status': 'success',
            'product_manufactured': product_type,
            'quantity_produced': output_quantity,
            'quality_standard': quality_standard,
            'production_time_hours': adjusted_time,
            'energy_cost': energy_cost,
            'input_materials_consumed': {k: production_quantity * v for k, v in recipe_data['input_materials'].items()}
        }
        
        logger.info(f"Manufacturing completed: {output_quantity:.1f} units {product_type} ({quality_standard})")
        
        return result
    
    def _process_distribution(self, request: Dict, inputs: Dict) -> Dict:
        """Process distribution and export preparation"""
        destination = inputs['destination_country']
        shipping_method = inputs['shipping_method']
        
        # Calculate available products for export
        available_products = self.agents['manufacturing']['finished_goods'].copy()
        
        # Select product for export (prefer DAP for most countries)
        export_products = {}
        for product, quantity in available_products.items():
            if quantity > 0:
                export_quantity = min(quantity * 0.7, 50000)  # Export up to 70% or 50K tons
                export_products[product] = export_quantity
                
                # Update inventories
                self.agents['manufacturing']['finished_goods'][product] -= export_quantity
                
                if product not in self.agents['distribution']['current_inventory']:
                    self.agents['distribution']['current_inventory'][product] = 0
                self.agents['distribution']['current_inventory'][product] += export_quantity
        
        # Calculate shipping details
        shipping_costs = {'bulk_carrier': 25, 'container_ship': 45, 'break_bulk': 35}
        cost_per_ton = shipping_costs.get(shipping_method, 30)
        total_quantity = sum(export_products.values())
        total_shipping_cost = total_quantity * cost_per_ton
        
        # Estimate delivery time
        delivery_times = {'immediate': 14, 'scheduled': 21, 'seasonal_optimal': 35}
        delivery_days = delivery_times.get(inputs['delivery_schedule'], 21)
        
        result = {
            'status': 'success',
            'destination_country': destination,
            'export_products': export_products,
            'total_quantity_tons': total_quantity,
            'shipping_method': shipping_method,
            'shipping_cost_usd': total_shipping_cost,
            'estimated_delivery_days': delivery_days,
            'export_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        logger.info(f"Distribution prepared: {total_quantity:.1f} tons to {destination} via {shipping_method}")
        
        return result
    
    def _process_retail_sales(self, request: Dict, inputs: Dict) -> Dict:
        """Process retail sales and customer delivery"""
        pricing_strategy = inputs['pricing_strategy']
        payment_terms = inputs['payment_terms']
        delivery_terms = inputs['delivery_terms']
        
        # Calculate available inventory for sale
        available_inventory = self.agents['distribution']['current_inventory'].copy()
        
        # Calculate pricing
        base_prices = {'DAP_Fertilizer': 320, 'TSP_Fertilizer': 285}  # USD per ton
        pricing_multipliers = {'market_rate': 1.0, 'competitive': 0.95, 'premium': 1.08}
        
        sales_records = []
        total_revenue = 0
        
        for product, quantity in available_inventory.items():
            if quantity > 0:
                base_price = base_prices.get(product, 300)
                final_price = base_price * pricing_multipliers.get(pricing_strategy, 1.0)
                
                # Sell 90% of available inventory
                sold_quantity = quantity * 0.9
                revenue = sold_quantity * final_price
                total_revenue += revenue
                
                sales_records.append({
                    'product': product,
                    'quantity_tons': sold_quantity,
                    'price_per_ton_usd': final_price,
                    'total_revenue_usd': revenue
                })
                
                # Update inventory
                self.agents['distribution']['current_inventory'][product] -= sold_quantity
                
                # Add to retail sales history
                if product not in self.agents['retail']['inventory']:
                    self.agents['retail']['inventory'][product] = 0
                self.agents['retail']['inventory'][product] += sold_quantity
        
        result = {
            'status': 'success',
            'sales_records': sales_records,
            'total_revenue_usd': total_revenue,
            'payment_terms': payment_terms,
            'delivery_terms': delivery_terms,
            'pricing_strategy': pricing_strategy,
            'sale_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        logger.info(f"Retail sales completed: ${total_revenue:,.2f} revenue from {len(sales_records)} products")
        
        return result
    
    def run_full_simulation(self, data_source: str = None) -> Dict:
        """
        Run complete end-to-end simulation
        
        Args:
            data_source: Path to Excel file or None for demo data
            
        Returns:
            Complete simulation results
        """
        logger.info("Starting complete supply chain simulation")
        
        # Load data
        if data_source:
            simulation_data = self.load_excel_data(data_source)
        else:
            simulation_data = self._get_demo_data()
        
        self.simulation_data = simulation_data
        
        # Use first production record for simulation
        if simulation_data['production']:
            production_record = simulation_data['production'][0]
            ore_quantity = production_record['ore_tons_estimated']
        else:
            ore_quantity = 100000  # Default 100K tons
        
        simulation_results = {
            'simulation_id': f"SIM_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'start_time': datetime.now(),
            'input_data': simulation_data,
            'stages': {},
            'material_flow': [],
            'operator_decisions': [],
            'final_results': {}
        }
        
        # STAGE 1: MINING - Inject raw materials
        logger.info(f"STAGE 1: Mining - Extracting {ore_quantity} tons of Phosphorite Ore")
        
        # Update mining agent inventory
        self.agents['mining']['current_inventory']['Phosphorite Ore'] = ore_quantity
        
        mining_result = {
            'extracted_material': 'Phosphorite Ore',
            'quantity_extracted': ore_quantity,
            'ore_quality': self.agents['mining']['ore_quality']['Phosphorite Ore'],
            'extraction_cost_per_ton': 15.0,
            'total_extraction_cost': ore_quantity * 15.0
        }
        
        simulation_results['stages']['mining'] = mining_result
        simulation_results['material_flow'].append({
            'stage': 'mining',
            'timestamp': datetime.now(),
            'material': 'Phosphorite Ore',
            'quantity': ore_quantity,
            'location': 'MINE_AMX_001'
        })
        
        # STAGE 2: PROCESSING - Create operator request
        logger.info("STAGE 2: Processing - Creating operator request for ore transformation")
        
        processing_request_id = self.create_operator_request(
            'processing', 
            'transform_ore',
            {
                'available_quantity': ore_quantity,
                'ore_type': 'Phosphorite Ore',
                'ore_quality': mining_result['ore_quality']
            }
        )
        
        # Auto-process with optimal settings for demo
        processing_inputs = {
            'recipe_selection': 'Phosphorite_to_PG',
            'quality_target': 0.87,
            'batch_size': min(ore_quantity, 25000),  # Process in 25K ton batches
            'processing_priority': 'normal'
        }
        
        processing_result = self.process_operator_input(processing_request_id, processing_inputs)
        simulation_results['stages']['processing'] = processing_result
        simulation_results['operator_decisions'].append({
            'stage': 'processing',
            'request_id': processing_request_id,
            'inputs': processing_inputs,
            'result': processing_result
        })
        
        if processing_result.get('status') == 'success':
            pg_quantity = processing_result['output_produced']['PG']
            simulation_results['material_flow'].append({
                'stage': 'processing',
                'timestamp': datetime.now(),
                'material': 'PG',
                'quantity': pg_quantity,
                'location': 'PROC_AMX_001'
            })
        
        # STAGE 3: MANUFACTURING - Create operator request
        logger.info("STAGE 3: Manufacturing - Creating operator request for fertilizer production")
        
        manufacturing_request_id = self.create_operator_request(
            'manufacturing',
            'produce_fertilizer',
            {
                'available_pg': self.agents['processing']['processed_storage'].get('PG', 0),
                'target_products': ['DAP_Fertilizer', 'TSP_Fertilizer']
            }
        )
        
        # Auto-process with export-grade DAP for demo
        manufacturing_inputs = {
            'product_type': 'DAP_Fertilizer',
            'quality_standard': 'export_grade',
            'production_rate': 'optimal',
            'packaging_type': 'bulk'
        }
        
        manufacturing_result = self.process_operator_input(manufacturing_request_id, manufacturing_inputs)
        simulation_results['stages']['manufacturing'] = manufacturing_result
        simulation_results['operator_decisions'].append({
            'stage': 'manufacturing',
            'request_id': manufacturing_request_id,
            'inputs': manufacturing_inputs,
            'result': manufacturing_result
        })
        
        if manufacturing_result.get('status') == 'success':
            product_quantity = manufacturing_result['quantity_produced']
            simulation_results['material_flow'].append({
                'stage': 'manufacturing',
                'timestamp': datetime.now(),
                'material': manufacturing_result['product_manufactured'],
                'quantity': product_quantity,
                'location': 'MFG_AMX_001'
            })
        
        # STAGE 4: DISTRIBUTION - Create operator request
        logger.info("STAGE 4: Distribution - Creating operator request for export preparation")
        
        # Use export data if available
        export_countries = []
        if simulation_data['exports']:
            export_countries = list(set([exp['country'] for exp in simulation_data['exports']]))
        else:
            export_countries = ['China', 'India', 'Brazil', 'Turkey']
        
        distribution_request_id = self.create_operator_request(
            'distribution',
            'prepare_export',
            {
                'available_products': self.agents['manufacturing']['finished_goods'].copy(),
                'available_countries': export_countries
            }
        )
        
        # Auto-process with China as destination for demo
        distribution_inputs = {
            'destination_country': export_countries[0] if export_countries else 'China',
            'shipping_method': 'bulk_carrier',
            'delivery_schedule': 'scheduled'
        }
        
        distribution_result = self.process_operator_input(distribution_request_id, distribution_inputs)
        simulation_results['stages']['distribution'] = distribution_result
        simulation_results['operator_decisions'].append({
            'stage': 'distribution',
            'request_id': distribution_request_id,
            'inputs': distribution_inputs,
            'result': distribution_result
        })
        
        if distribution_result.get('status') == 'success':
            export_quantity = distribution_result['total_quantity_tons']
            simulation_results['material_flow'].append({
                'stage': 'distribution',
                'timestamp': datetime.now(),
                'material': 'Export_Ready_Products',
                'quantity': export_quantity,
                'location': 'DIST_AMX_001'
            })
        
        # STAGE 5: RETAIL - Create operator request
        logger.info("STAGE 5: Retail - Creating operator request for customer sales")
        
        retail_request_id = self.create_operator_request(
            'retail',
            'customer_sales',
            {
                'available_inventory': self.agents['distribution']['current_inventory'].copy(),
                'export_destination': distribution_result.get('destination_country', 'China')
            }
        )
        
        # Auto-process with market rate pricing for demo
        retail_inputs = {
            'pricing_strategy': 'market_rate',
            'payment_terms': 'letter_of_credit',
            'delivery_terms': 'CFR'
        }
        
        retail_result = self.process_operator_input(retail_request_id, retail_inputs)
        simulation_results['stages']['retail'] = retail_result
        simulation_results['operator_decisions'].append({
            'stage': 'retail',
            'request_id': retail_request_id,
            'inputs': retail_inputs,
            'result': retail_result
        })
        
        if retail_result.get('status') == 'success':
            total_revenue = retail_result['total_revenue_usd']
            simulation_results['material_flow'].append({
                'stage': 'retail',
                'timestamp': datetime.now(),
                'material': 'Customer_Sales',
                'quantity': total_revenue,
                'location': 'RETAIL_AMX_001'
            })
        
        # FINAL RESULTS SUMMARY
        simulation_results['end_time'] = datetime.now()
        simulation_results['duration'] = simulation_results['end_time'] - simulation_results['start_time']
        
        # Calculate overall performance metrics
        final_metrics = {
            'input_ore_tons': ore_quantity,
            'pg_produced_tons': processing_result.get('output_produced', {}).get('PG', 0),
            'fertilizer_produced_tons': manufacturing_result.get('quantity_produced', 0),
            'exported_tons': distribution_result.get('total_quantity_tons', 0),
            'total_revenue_usd': retail_result.get('total_revenue_usd', 0),
            'ore_to_fertilizer_conversion_rate': 0,
            'revenue_per_ton_ore': 0,
            'total_costs_usd': 0
        }
        
        # Calculate conversion rates and efficiency
        if final_metrics['input_ore_tons'] > 0:
            final_metrics['ore_to_fertilizer_conversion_rate'] = (
                final_metrics['fertilizer_produced_tons'] / final_metrics['input_ore_tons']
            )
            final_metrics['revenue_per_ton_ore'] = (
                final_metrics['total_revenue_usd'] / final_metrics['input_ore_tons']
            )
        
        # Calculate total costs
        costs = [
            mining_result.get('total_extraction_cost', 0),
            processing_result.get('energy_cost', 0),
            manufacturing_result.get('energy_cost', 0),
            distribution_result.get('shipping_cost_usd', 0)
        ]
        final_metrics['total_costs_usd'] = sum(costs)
        final_metrics['net_profit_usd'] = final_metrics['total_revenue_usd'] - final_metrics['total_costs_usd']
        final_metrics['profit_margin_percent'] = (
            (final_metrics['net_profit_usd'] / final_metrics['total_revenue_usd'] * 100)
            if final_metrics['total_revenue_usd'] > 0 else 0
        )
        
        simulation_results['final_results'] = final_metrics
        
        logger.info("Complete supply chain simulation finished successfully")
        logger.info(f"Results: {final_metrics['input_ore_tons']} tons ore → "
                   f"{final_metrics['fertilizer_produced_tons']:.1f} tons fertilizer → "
                   f"${final_metrics['total_revenue_usd']:,.2f} revenue")
        
        return simulation_results
    
    def print_simulation_summary(self, results: Dict):
        """Print a comprehensive simulation summary"""
        
        print("=" * 80)
        print("COMPLETE SUPPLY CHAIN SIMULATION RESULTS")
        print("=" * 80)
        
        print(f"Simulation ID: {results['simulation_id']}")
        print(f"Duration: {results['duration']}")
        print()
        
        print("MATERIAL FLOW SUMMARY:")
        print("-" * 40)
        for flow in results['material_flow']:
            timestamp = flow['timestamp'].strftime('%H:%M:%S')
            print(f"{timestamp} | {flow['stage']:12} | {flow['material']:20} | {flow['quantity']:>10,.1f}")
        print()
        
        print("OPERATOR DECISIONS MADE:")
        print("-" * 40)
        for decision in results['operator_decisions']:
            print(f"Stage: {decision['stage']}")
            print(f"  Request ID: {decision['request_id']}")
            print(f"  Key Inputs: {decision['inputs']}")
            print(f"  Result: {decision['result']['status']}")
            print()
        
        print("STAGE-BY-STAGE RESULTS:")
        print("-" * 40)
        
        # Mining
        mining = results['stages']['mining']
        print(f"🔨 MINING:")
        print(f"  Extracted: {mining['quantity_extracted']:,.0f} tons {mining['extracted_material']}")
        print(f"  Quality: {mining['ore_quality']:.2f}")
        print(f"  Cost: ${mining['total_extraction_cost']:,.2f}")
        print()
        
        # Processing
        processing = results['stages']['processing']
        if processing.get('status') == 'success':
            print(f"⚗️  PROCESSING:")
            for material, qty in processing['output_produced'].items():
                print(f"  Produced: {qty:,.1f} tons {material}")
            print(f"  Quality: {processing['quality_achieved']:.2f}")
            print(f"  Efficiency: {processing['efficiency']:.1%}")
            print(f"  Cost: ${processing['energy_cost']:,.2f}")
            print()
        
        # Manufacturing
        manufacturing = results['stages']['manufacturing']
        if manufacturing.get('status') == 'success':
            print(f"🏭 MANUFACTURING:")
            print(f"  Product: {manufacturing['product_manufactured']}")
            print(f"  Quantity: {manufacturing['quantity_produced']:,.1f} tons")
            print(f"  Standard: {manufacturing['quality_standard']}")
            print(f"  Cost: ${manufacturing['energy_cost']:,.2f}")
            print()
        
        # Distribution
        distribution = results['stages']['distribution']
        if distribution.get('status') == 'success':
            print(f"📦 DISTRIBUTION:")
            print(f"  Destination: {distribution['destination_country']}")
            print(f"  Total Export: {distribution['total_quantity_tons']:,.1f} tons")
            print(f"  Shipping: {distribution['shipping_method']}")
            print(f"  Cost: ${distribution['shipping_cost_usd']:,.2f}")
            print()
        
        # Retail
        retail = results['stages']['retail']
        if retail.get('status') == 'success':
            print(f"🛒 RETAIL:")
            print(f"  Total Revenue: ${retail['total_revenue_usd']:,.2f}")
            print(f"  Payment Terms: {retail['payment_terms']}")
            print(f"  Delivery Terms: {retail['delivery_terms']}")
            print()
        
        print("FINAL PERFORMANCE METRICS:")
        print("-" * 40)
        metrics = results['final_results']
        print(f"Raw Material Input:      {metrics['input_ore_tons']:>12,.0f} tons")
        print(f"PG Produced:             {metrics['pg_produced_tons']:>12,.1f} tons")
        print(f"Fertilizer Produced:     {metrics['fertilizer_produced_tons']:>12,.1f} tons")
        print(f"Products Exported:       {metrics['exported_tons']:>12,.1f} tons")
        print(f"Conversion Rate:         {metrics['ore_to_fertilizer_conversion_rate']:>12.1%}")
        print()
        print(f"Total Revenue:           ${metrics['total_revenue_usd']:>12,.2f}")
        print(f"Total Costs:             ${metrics['total_costs_usd']:>12,.2f}")
        print(f"Net Profit:              ${metrics['net_profit_usd']:>12,.2f}")
        print(f"Profit Margin:           {metrics['profit_margin_percent']:>12.1f}%")
        print(f"Revenue per Ton Ore:     ${metrics['revenue_per_ton_ore']:>12.2f}")
        print()
        
        print("=" * 80)
    
    def get_pending_requests(self) -> List[Dict]:
        """Get all pending operator requests"""
        return [req for req in self.operator_requests if req['status'] == 'pending']
    
    def get_agent_status(self, agent_type: str) -> Dict:
        """Get current status of a specific agent"""
        return self.agents.get(agent_type, {})


def main():
    """Main function to demonstrate the complete simulation system"""
    
    # Create simulator
    simulator = SupplyChainSimulator()
    
    print("🏭 SUPPLY CHAIN RECONSTRUCTION SYSTEM")
    print("=====================================")
    print()
    
    # Check for Excel file
    excel_path = "AMX MOTHER FILE 2.xlsx"
    
    try:
        # Try to run with Excel data
        results = simulator.run_full_simulation(excel_path)
        print("✅ Simulation completed using Excel data")
    except:
        # Fallback to demo data
        print("📊 Excel file not found, using demo data")
        results = simulator.run_full_simulation()
        print("✅ Simulation completed using demo data")
    
    print()
    
    # Print comprehensive results
    simulator.print_simulation_summary(results)
    
    # Show any pending operator requests
    pending = simulator.get_pending_requests()
    if pending:
        print(f"⏳ Pending operator requests: {len(pending)}")
        for req in pending:
            print(f"  - {req['request_id']}: {req['stage']} - {req['operation']}")
    
    return results


if __name__ == "__main__":
    simulation_results = main()