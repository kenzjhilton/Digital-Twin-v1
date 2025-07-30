import os

# Directories to create
dirs = [
    'src', 'src/agents', 'src/data', 'src/simulation', 'src/api', 'src/utils', 'src/visualization',
    'data', 'data/raw', 'data/processed', 'data/schemas',
    'tests', 'tests/test_agents', 'tests/test_simulation', 'tests/test_data', 'tests/test_api',
    'config', 'docs'
]

# Files to create
files = [
    'src/__init__.py', 'src/agents/__init__.py', 'src/data/__init__.py',
    'src/simulation/__init__.py', 'src/api/__init__.py', 'src/utils/__init__.py',
    'src/visualization/__init__.py', 'tests/__init__.py',
    'src/agents/base_agent.py', 'src/agents/mining_agent.py',
    'src/agents/processing_agent.py', 'src/agents/manufacturing_agent.py',
    'src/agents/distribution_agent.py', 'src/agents/retail_agent.py',
    'src/data/data_loader.py', 'src/data/data_processor.py', 'src/data/schema_validator.py',
    'src/simulation/supply_chain_simulator.py', 'src/simulation/material_tracker.py',
    'src/simulation/event_scheduler.py', 'src/api/input_handler.py',
    'src/api/query_engine.py', 'src/api/endpoints.py',
    'src/utils/config.py', 'src/utils/logging_setup.py', 'src/utils/validators.py',
    'src/visualization/dashboard.py', 'src/visualization/reporting.py',
    'config/development.yaml', 'config/production.yaml', 'config/simulation_params.yaml',
    'tests/test_agents/test_base_agent.py', 'tests/test_agents/test_mining_agent.py',
    'tests/test_simulation/test_simulator.py', 'tests/test_data/test_data_loader.py',
    'tests/conftest.py', 'docs/README.md', 'docs/API_DOCUMENTATION.md', 'docs/SETUP.md'
]

# Create directories
for dir_path in dirs:
    os.makedirs(dir_path, exist_ok=True)
    print(f"Created directory: {dir_path}")

# Create files
for file_path in files:
    with open(file_path, 'w') as f:
        f.write("")  # Create empty file
    print(f"Created file: {file_path}")

print("Project structure created successfully!")