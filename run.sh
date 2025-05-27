#!/bin/bash

# Meinn Restaurant AI Assistant - Unified Run Script
# Usage: ./run.sh [standard|binary|polars]
# If no option is provided, will try binary installation first, then fallback to polars

# Default to binary option if none specified
DATA_OPTION=${1:-binary}

echo "==== Meinn Restaurant AI Assistant ===="
echo "Starting with data processing option: $DATA_OPTION"

# Create necessary directories
mkdir -p data logs

# Prepare virtual environment name
VENV_NAME="venv"
if [ "$DATA_OPTION" == "polars" ]; then
    VENV_NAME="venv_polars"
fi

# Create temporary requirements file with selected option uncommented
TMP_REQUIREMENTS="requirements_tmp.txt"
cp requirements.txt "$TMP_REQUIREMENTS"

# Uncomment the appropriate data processing option
if [ "$DATA_OPTION" == "standard" ]; then
    # Uncomment standard pandas/numpy
    sed -i '/Option 1: Standard/,/Option 2:/ s/^# \(pandas\|numpy\)/\1/' "$TMP_REQUIREMENTS"
    # Comment out binary and polars options
    sed -i '/Option 2: Binary/,/Option 3:/ s/^pandas/# pandas/' "$TMP_REQUIREMENTS"
    sed -i '/Option 2: Binary/,/Option 3:/ s/^numpy/# numpy/' "$TMP_REQUIREMENTS"
    sed -i '/Option 3: Alternative/,/===== IMAGE/ s/^polars/# polars/' "$TMP_REQUIREMENTS"
    sed -i '/Option 3: Alternative/,/===== IMAGE/ s/^pyarrow/# pyarrow/' "$TMP_REQUIREMENTS"
elif [ "$DATA_OPTION" == "binary" ]; then
    # Binary is already uncommented by default, comment out others
    sed -i '/Option 1: Standard/,/Option 2:/ s/^pandas/# pandas/' "$TMP_REQUIREMENTS"
    sed -i '/Option 1: Standard/,/Option 2:/ s/^numpy/# numpy/' "$TMP_REQUIREMENTS"
    sed -i '/Option 3: Alternative/,/===== IMAGE/ s/^polars/# polars/' "$TMP_REQUIREMENTS"
    sed -i '/Option 3: Alternative/,/===== IMAGE/ s/^pyarrow/# pyarrow/' "$TMP_REQUIREMENTS"
elif [ "$DATA_OPTION" == "polars" ]; then
    # Uncomment polars/pyarrow
    sed -i '/Option 3: Alternative/,/===== IMAGE/ s/^# \(polars\|pyarrow\)/\1/' "$TMP_REQUIREMENTS"
    # Comment out pandas/numpy options
    sed -i '/Option 1: Standard/,/Option 2:/ s/^pandas/# pandas/' "$TMP_REQUIREMENTS"
    sed -i '/Option 1: Standard/,/Option 2:/ s/^numpy/# numpy/' "$TMP_REQUIREMENTS"
    sed -i '/Option 2: Binary/,/Option 3:/ s/^pandas/# pandas/' "$TMP_REQUIREMENTS"
    sed -i '/Option 2: Binary/,/Option 3:/ s/^numpy/# numpy/' "$TMP_REQUIREMENTS"
else
    echo "Invalid option: $DATA_OPTION. Using binary option as default."
    DATA_OPTION="binary"
fi

echo "Using $DATA_OPTION data processing libraries."

# Initialize or recreate virtual environment
if [ -d "$VENV_NAME" ]; then
    echo "Found existing $VENV_NAME environment."
    
    # Activate existing environment
    if [ -f "$VENV_NAME/bin/activate" ]; then
        source "$VENV_NAME/bin/activate"
        echo "Updating dependencies in existing environment..."
        pip install --upgrade pip
        pip install -r "$TMP_REQUIREMENTS"
    else
        echo "ERROR: Virtual environment exists but activate script not found."
        echo "Removing and recreating environment..."
        rm -rf "$VENV_NAME"
        python3 -m venv "$VENV_NAME"
        source "$VENV_NAME/bin/activate"
        pip install --upgrade pip
        pip install -r "$TMP_REQUIREMENTS"
    fi
else
    echo "Creating new virtual environment: $VENV_NAME"
    python3 -m venv "$VENV_NAME"
    
    if [ -f "$VENV_NAME/bin/activate" ]; then
        source "$VENV_NAME/bin/activate"
        echo "Installing dependencies..."
        pip install --upgrade pip
        pip install -r "$TMP_REQUIREMENTS"
    else
        echo "ERROR: Failed to create virtual environment. Using system Python."
    fi
fi

# Check if pandas installation succeeded
if [ "$DATA_OPTION" == "standard" ] || [ "$DATA_OPTION" == "binary" ]; then
    if ! python -c "import pandas" &> /dev/null; then
        echo "WARNING: pandas installation failed. Falling back to polars..."
        DATA_OPTION="polars"
        
        # Update temp requirements for polars
        cp requirements.txt "$TMP_REQUIREMENTS"
        sed -i '/Option 3: Alternative/,/===== IMAGE/ s/^# \(polars\|pyarrow\)/\1/' "$TMP_REQUIREMENTS"
        sed -i '/Option 1: Standard/,/Option 2:/ s/^pandas/# pandas/' "$TMP_REQUIREMENTS"
        sed -i '/Option 1: Standard/,/Option 2:/ s/^numpy/# numpy/' "$TMP_REQUIREMENTS"
        sed -i '/Option 2: Binary/,/Option 3:/ s/^pandas/# pandas/' "$TMP_REQUIREMENTS"
        sed -i '/Option 2: Binary/,/Option 3:/ s/^numpy/# numpy/' "$TMP_REQUIREMENTS"
        
        # Install polars
        pip install -r "$TMP_REQUIREMENTS"
    fi
fi

# Create polars adapter if using polars
if [ "$DATA_OPTION" == "polars" ]; then
    echo "Creating polars adapter for pandas compatibility..."
    mkdir -p src
    cat > src/polars_adapter.py << EOF
# polars_adapter.py - Adapter module to make polars work as a pandas replacement
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
fi

# Create __init__.py files to ensure proper module imports
mkdir -p src/services/chat src/services/translation src/services/product
touch src/services/__init__.py src/services/chat/__init__.py 
touch src/services/translation/__init__.py src/services/product/__init__.py
touch src/api/__init__.py src/api/routes/__init__.py src/api/utils/__init__.py src/db/__init__.py

# Cleanup temp files
rm -f "$TMP_REQUIREMENTS"

# Initialize the database
echo "Initializing database..."
python src/db/init_db.py

# Start the application
echo "Starting Meinn AI..."
export PORT=5050

# Add polars adapter to Python path if using polars
if [ "$DATA_OPTION" == "polars" ]; then
    export PYTHONPATH=$PYTHONPATH:$(pwd)/src
fi

# Print final setup information
echo "==== Configuration ===="
echo "Data processing: $DATA_OPTION"
echo "Environment: $VENV_NAME"
echo "Port: $PORT"
echo "===================="

# Start the application
python src/api/main.py
