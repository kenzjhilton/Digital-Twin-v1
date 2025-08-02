"""
API Module
==========

REST API and interface components for external system integration.
This module provides HTTP endpoints, input handlers, and query engines
for interacting with the supply chain simulation system.

Planned Components:
- InputHandler: Handle external inputs and operator requests
- QueryEngine: Query simulation state and historical data
- endpoints: REST API endpoints for web integration

Usage:
    from src.api import InputHandler, QueryEngine
"""

# Placeholder imports for future implementation
# from .input_handler import InputHandler
# from .query_engine import QueryEngine
# from . import endpoints

__all__ = [
    # 'InputHandler',
    # 'QueryEngine', 
    # 'endpoints'
]

# Module metadata
__version__ = "0.1.0"
__status__ = "Development"

def get_api_info():
    """Get information about available API components"""
    return {
        'module': 'api',
        'version': __version__,
        'status': __status__,
        'available_components': __all__,
        'planned_endpoints': [
            '/api/v1/simulate',
            '/api/v1/inject_material',
            '/api/v1/status',
            '/api/v1/results'
        ]
    }