"""
Data Module
===========

Data loading, processing, and validation components.
This module handles Excel/CSV file imports, data transformation,
and schema validation for supply chain reconstruction.

Planned Components:
- DataLoader: Load data from various file formats
- DataProcessor: Clean and transform raw data
- SchemaValidator: Validate data against expected schemas

Usage:
    from src.data import DataLoader, DataProcessor
    
    loader = DataLoader()
    data = loader.load_excel('client_data.xlsx')
"""

# Placeholder imports for future implementation
# from .data_loader import DataLoader
# from .data_processor import DataProcessor
# from .schema_validator import SchemaValidator

__all__ = [
    # 'DataLoader',
    # 'DataProcessor',
    # 'SchemaValidator'
]

# Module metadata
__version__ = "0.1.0"
__status__ = "Development"

# Supported file formats
SUPPORTED_FORMATS = [
    '.xlsx', '.xls',  # Excel files
    '.csv',           # CSV files  
    '.json',          # JSON files
    '.xml'            # XML files
]

def get_data_info():
    """Get information about data handling capabilities"""
    return {
        'module': 'data',
        'version': __version__,
        'status': __status__,
        'supported_formats': SUPPORTED_FORMATS,
        'available_components': __all__
    }