"""
Visualization Module
===================

Dashboard, reporting, and visualization components for supply chain analysis.
This module provides interactive dashboards, charts, and report generation
capabilities.

Planned Components:
- Dashboard: Interactive web-based dashboard
- reporting: Generate PDF/Excel reports from simulation results
- charts: Create various chart types for data visualization

Usage:
    from src.visualization import Dashboard, generate_report
    
    dashboard = Dashboard()
    dashboard.run()
"""

# Placeholder imports for future implementation
# from .dashboard import Dashboard
# from .reporting import generate_report, ReportGenerator
# from .charts import create_flow_chart, create_performance_chart

__all__ = [
    # 'Dashboard',
    # 'generate_report',
    # 'ReportGenerator',
    # 'create_flow_chart',
    # 'create_performance_chart'
]

# Module metadata
__version__ = "0.1.0"
__status__ = "Development"

# Supported visualization types
CHART_TYPES = [
    'material_flow',
    'performance_metrics',
    'cost_breakdown',
    'timeline_analysis',
    'bottleneck_analysis'
]

def get_visualization_info():
    """Get information about visualization capabilities"""
    return {
        'module': 'visualization',
        'version': __version__,
        'status': __status__,
        'supported_charts': CHART_TYPES,
        'available_components': __all__
    }