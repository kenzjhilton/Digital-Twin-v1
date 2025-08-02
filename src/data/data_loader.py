"""
Excel Data Loader for Supply Chain Reconstruction
=================================================

Loads and processes client's historical data to configure the supply chain system.
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SupplyChainDataLoader:
    """Load and process client Excel data for supply chain reconstruction"""
    
    def __init__(self, excel_path: str):
        """
        Initialize data loader with client Excel file
        
        Args:
            excel_path: Path to client's Excel file
        """
        self.excel_path = Path(excel_path)
        self.raw_data = {}
        self.processed_data = {}
        
        if not self.excel_path.exists():
            raise FileNotFoundError(f"Excel file not found: {excel_path}")
        
        logger.info(f"Initialized data loader for: {excel_path}")
    
    def load_all_sheets(self) -> Dict:
        """Load all sheets from the Excel file"""
        try:
            xl = pd.ExcelFile(self.excel_path)
            
            for sheet_name in xl.sheet_names:
                self.raw_data[sheet_name] = xl.parse(sheet_name)
                logger.info(f"Loaded sheet: {sheet_name}")
            
            return self.raw_data
        
        except Exception as e:
            logger.error(f"Error loading Excel file: {e}")
            raise
    
    def extract_production_data(self) -> List[Dict]:
        """Extract historical production data"""
        production_records = []
        
        # Look for production data in various sheet formats
        for sheet_name, df in self.raw_data.items():
            if 'production' in sheet_name.lower() or 'output' in sheet_name.lower():
                # Process production sheet
                for _, row in df.iterrows():
                    # Extract year columns (assuming years are column headers)
                    for col in df.columns:
                        if str(col).isdigit() and len(str(col)) == 4:  # Year columns
                            year = int(col)
                            value = row[col]
                            
                            if pd.notnull(value) and value > 0:
                                production_records.append({
                                    'year': year,
                                    'product': str(row.iloc[0]) if pd.notnull(row.iloc[0]) else 'Unknown',
                                    'quantity': float(value),
                                    'unit': 'tons',  # Assume tons, could be refined
                                    'source_sheet': sheet_name
                                })
        
        self.processed_data['production'] = production_records
        logger.info(f"Extracted {len(production_records)} production records")
        return production_records
    
    def extract_export_data(self) -> List[Dict]:
        """Extract export/sales data"""
        export_records = []
        
        for sheet_name, df in self.raw_data.items():
            if 'export' in sheet_name.lower() or 'sales' in sheet_name.lower():
                current_country = None
                
                for _, row in df.iterrows():
                    # Country identification
                    first_col = str(row.iloc[0]) if pd.notnull(row.iloc[0]) else ''
                    if first_col and not first_col.lower() in ['product', 'tons', 'usd']:
                        current_country = first_col.strip()
                    
                    # Product identification
                    product = str(row.iloc[1]) if len(row) > 1 and pd.notnull(row.iloc[1]) else ''
                    if not product or product.lower() in ['product', 'tons', 'usd']:
                        continue
                    
                    # Extract yearly data
                    for col in df.columns:
                        if str(col).isdigit() and len(str(col)) == 4:
                            year = int(col)
                            value = pd.to_numeric(row[col], errors='coerce')
                            
                            if pd.notnull(value) and value > 0:
                                export_records.append({
                                    'year': year,
                                    'country': current_country,
                                    'product': product,
                                    'quantity': float(value),
                                    'unit': 'tons',
                                    'source_sheet': sheet_name
                                })
        
        self.processed_data['exports'] = export_records
        logger.info(f"Extracted {len(export_records)} export records")
        return export_records
    
    def configure_agents_from_data(self) -> Dict:
        """Configure agent parameters based on historical data"""
        config = {
            'mining': self._configure_mining(),
            'processing': self._configure_processing(),
            'manufacturing': self._configure_manufacturing(),
            'distribution': self._configure_distribution(),
            'retail': self._configure_retail()
        }
        
        return config
    
    def _configure_mining(self) -> Dict:
        """Configure mining agent based on production data"""
        production_data = self.processed_data.get('production', [])
        
        if not production_data:
            return {
                'capacity': 500000.0,
                'extraction_rate': 2000.0,
                'ore_types': ['Phosphorite Ore']
            }
        
        # Calculate max annual production to size mine
        max_annual = max([p['quantity'] for p in production_data], default=100000)
        
        # Size mine for 1.5x peak production
        mine_capacity = max_annual * 1.5
        daily_rate = max_annual / 365
        hourly_rate = daily_rate / 24
        
        # Determine ore types from production data
        ore_types = list(set([p['product'] for p in production_data if 'ore' in p['product'].lower()]))
        if not ore_types:
            ore_types = ['Phosphorite Ore']  # Default
        
        return {
            'capacity': mine_capacity,
            'extraction_rate': hourly_rate,
            'ore_types': ore_types,
            'historical_peak': max_annual
        }
    
    def _configure_processing(self) -> Dict:
        """Configure processing based on production data"""
        # Processing capacity should handle mining output
        mining_config = self._configure_mining()
        
        return {
            'capacity': mining_config['capacity'] * 0.7,  # 70% of mining capacity
            'processing_methods': ['chemical_processing', 'beneficiation'],
            'efficiency': 0.82  # Based on typical phosphate processing
        }
    
    def _configure_manufacturing(self) -> Dict:
        """Configure manufacturing based on product mix"""
        production_data = self.processed_data.get('production', [])
        
        # Identify product types
        products = [p['product'] for p in production_data]
        fertilizer_products = [p for p in products if any(term in p.lower() for term in ['dap', 'tsp', 'fertilizer'])]
        
        processing_config = self._configure_processing()
        
        return {
            'capacity': processing_config['capacity'] * 0.6,  # 60% of processing
            'production_lines': ['chemical_production', 'bagging_line'],
            'product_mix': fertilizer_products or ['DAP_Fertilizer', 'TSP_Fertilizer']
        }
    
    def _configure_distribution(self) -> Dict:
        """Configure distribution based on export data"""
        export_data = self.processed_data.get('exports', [])
        
        # Extract destination countries/regions
        countries = list(set([e['country'] for e in export_data if e['country']]))
        
        # Map to shipping zones
        zones = []
        for country in countries:
            if country in ['China', 'India', 'Japan', 'South Korea']:
                zones.append('Asia_Pacific')
            elif country in ['Germany', 'France', 'Netherlands', 'Turkey']:
                zones.append('Europe')
            elif country in ['Brazil', 'USA', 'Argentina', 'Mexico']:
                zones.append('Americas')
            elif country in ['Morocco', 'Egypt', 'South Africa']:
                zones.append('Africa')
            else:
                zones.append('Middle_East')
        
        zones = list(set(zones)) or ['Asia_Pacific', 'Europe', 'Americas']
        
        # Size warehouse for export volumes
        max_export = max([e['quantity'] for e in export_data], default=50000)
        
        return {
            'capacity': max_export * 2,  # 2x peak export volume
            'shipping_zones': zones,
            'export_countries': countries
        }
    
    def _configure_retail(self) -> Dict:
        """Configure retail based on customer mix"""
        export_data = self.processed_data.get('exports', [])
        
        # Determine sales channels based on export patterns
        sales_channels = ['bulk_export', 'container_export']
        if any('domestic' in str(e.get('country', '')).lower() for e in export_data):
            sales_channels.append('domestic_sales')
        
        # Customer zones based on product types
        customer_zones = ['agricultural', 'industrial']
        if any('government' in str(e.get('product', '')).lower() for e in export_data):
            customer_zones.append('government')
        
        # Size retail capacity
        max_sales = max([e['quantity'] for e in export_data], default=100000)
        
        return {
            'capacity': max_sales * 3,  # 3x peak sales volume
            'sales_channels': sales_channels,
            'customer_zones': customer_zones,
            'export_focus': True
        }
    
    def generate_simulation_scenario(self, target_year: int = None) -> Dict:
        """Generate a simulation scenario based on historical data"""
        if target_year is None:
            # Use most recent year with data
            years = [p['year'] for p in self.processed_data.get('production', [])]
            target_year = max(years) if years else 2024
        
        # Get production target for the year
        year_production = [p for p in self.processed_data.get('production', []) if p['year'] == target_year]
        
        if year_production:
            total_production = sum([p['quantity'] for p in year_production])
            # Estimate raw ore needed (assuming 3:1 ratio for phosphate)
            raw_ore_needed = total_production * 3.2
        else:
            raw_ore_needed = 100000  # Default
        
        # Get export targets
        year_exports = [e for e in self.processed_data.get('exports', []) if e['year'] == target_year]
        export_targets = {}
        for export in year_exports:
            country = export['country']
            if country not in export_targets:
                export_targets[country] = {}
            export_targets[country][export['product']] = export['quantity']
        
        return {
            'target_year': target_year,
            'raw_ore_injection': raw_ore_needed,
            'production_targets': {p['product']: p['quantity'] for p in year_production},
            'export_targets': export_targets,
            'agent_config': self.configure_agents_from_data()
        }
    
    def create_supply_chain_from_data(self, system_class):
        """Create and configure a supply chain system using historical data"""
        # Load and process all data
        self.load_all_sheets()
        self.extract_production_data()
        self.extract_export_data()
        
        # Get configuration
        config = self.configure_agents_from_data()
        
        # Create system with data-driven configuration
        system = system_class()
        
        # Update agent configurations
        if hasattr(system, 'mine'):
            mining_config = config['mining']
            system.mine.capacity = mining_config['capacity']
            system.mine.extraction_rate = mining_config['extraction_rate']
            system.mine.ore_types = mining_config['ore_types']
        
        if hasattr(system, 'distributor'):
            dist_config = config['distribution']
            system.distributor.capacity = dist_config['capacity']
            system.distributor.shipping_zones = dist_config['shipping_zones']
        
        logger.info("Supply chain system configured from historical data")
        return system, config


def load_client_data_and_run(excel_path: str, ore_quantity: float = None):
    """
    Complete function to load client data and run simulation
    
    Args:
        excel_path: Path to client's Excel file
        ore_quantity: Amount of ore to inject (if None, uses data-driven amount)
    """
    from supply_chain_runner import CompleteSupplyChainSystem
    
    # Load client data
    loader = SupplyChainDataLoader(excel_path)
    
    # Create scenario
    scenario = loader.generate_simulation_scenario()
    
    # Use data-driven ore quantity if not specified
    if ore_quantity is None:
        ore_quantity = scenario['raw_ore_injection']
    
    print("📊 CLIENT DATA LOADED")
    print("=" * 50)
    print(f"Target Year: {scenario['target_year']}")
    print(f"Recommended Ore Injection: {ore_quantity:,.0f} tons")
    print(f"Production Targets: {len(scenario['production_targets'])} products")
    print(f"Export Targets: {len(scenario['export_targets'])} countries")
    print()
    
    # Create and configure system
    system, config = loader.create_supply_chain_from_data(CompleteSupplyChainSystem)
    
    # Run simulation
    results = system.run_complete_simulation("Phosphorite Ore", ore_quantity)
    
    # Add scenario data to results
    results['client_scenario'] = scenario
    results['agent_configuration'] = config
    
    return results


# Example usage
if __name__ == "__main__":
    # Load client data and run simulation
    try:
        excel_file = "AMX MOTHER FILE 2.xlsx"  # Your client's file
        results = load_client_data_and_run(excel_file)
        
        print("\n✅ SIMULATION COMPLETED WITH CLIENT DATA")
        print(f"Trace ID: {results['simulation_info']['trace_id']}")
        print(f"Duration: {results['simulation_info']['duration']}")
        
    except FileNotFoundError:
        print("❌ Client Excel file not found. Running with demo data.")
        
        # Fallback to demo simulation
        from supply_chain_runner import CompleteSupplyChainSystem
        system = CompleteSupplyChainSystem()
        results = system.run_complete_simulation()