#!/bin/bash

# Create necessary directories if they don't exist
mkdir -p data
mkdir -p logs

# Initialize virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    # Ensure virtual environment was created successfully
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo "Installing dependencies from requirements_fixed.txt..."
        pip install --upgrade pip  # Ensure pip is updated
        pip install -r requirements_fixed.txt
    else
        echo "ERROR: Failed to create virtual environment. Using system Python."
        # Continue without virtual environment
    fi
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    # Check if pandas is installed correctly
    if ! python -c "import pandas" &> /dev/null; then
        echo "Installing dependencies from requirements_fixed.txt..."
        pip install --upgrade pip
        pip install -r requirements_fixed.txt
    fi
else
    echo "WARNING: Virtual environment exists but activate script not found. Using system Python."
fi

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
echo "Starting Meinn AI..."
export PORT=5050
python src/api/main.py
