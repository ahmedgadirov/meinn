#!/bin/bash

# Create necessary directories if they don't exist
mkdir -p data
mkdir -p logs

# Check if virtual environment exists and remove if so (for clean install)
if [ -d "venv_minimal" ]; then
    echo "Removing existing minimal virtual environment for clean install..."
    rm -rf venv_minimal
fi

# Create a fresh virtual environment
echo "Creating minimal virtual environment..."
python3 -m venv venv_minimal

# Ensure virtual environment was created successfully
if [ -f "venv_minimal/bin/activate" ]; then
    source venv_minimal/bin/activate
    echo "Installing minimal dependencies (no compilation required)..."
    pip install --upgrade pip
    pip install -r requirements_minimal.txt
    
    # Create any necessary adapter code for polars/pandas compatibility
    cat > src/polars_adapter.py << EOF
# polars_adapter.py
# Adapter module to make polars work as a pandas replacement
import polars as pl

# Common pandas functions mapped to polars equivalents
def read_csv(file_path, **kwargs):
    return pl.read_csv(file_path, **kwargs)

def read_json(file_path, **kwargs):
    return pl.read_json(file_path, **kwargs)

def DataFrame(data=None, **kwargs):
    if data is None:
        return pl.DataFrame()
    return pl.DataFrame(data)

# Add more adapter functions as needed
EOF

    # Create __init__.py files to ensure proper module imports
    mkdir -p src/services/chat
    mkdir -p src/services/translation
    touch src/services/__init__.py
    touch src/services/chat/__init__.py
    touch src/services/translation/__init__.py
    touch src/services/product/__init__.py
    touch src/api/__init__.py
    touch src/api/routes/__init__.py
    touch src/api/utils/__init__.py
    touch src/db/__init__.py

    # Initialize the database
    echo "Initializing database..."
    python src/db/init_db.py

    # Start the application
    echo "Starting Meinn AI (minimal version)..."
    export PORT=5050
    # Add polars adapter to Python path
    export PYTHONPATH=$PYTHONPATH:$(pwd)/src
    python src/api/main.py
else
    echo "ERROR: Failed to create virtual environment."
    exit 1
fi
