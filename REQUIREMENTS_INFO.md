# Meinn Restaurant AI Assistant - Requirements Documentation

This document explains the requirements structure and run script for the Meinn project.

## Requirements Overview

The project's dependencies are organized in a single `requirements.txt` file with clearly marked sections:

1. **Core Dependencies**: Flask, FastAPI, and related web framework essentials
2. **Database**: SQLAlchemy and database adapters
3. **Language Processing**: Translation and language identification libraries
4. **Data Processing**: Options for pandas/numpy or polars
5. **Image Processing**: Pillow for image handling
6. **Utilities**: Various helper libraries
7. **Testing**: Test framework and tools

## Data Processing Options

Three options are available for data processing libraries:

1. **Standard**: Regular pandas and numpy installations (may require compiler)
2. **Binary**: Binary wheels for pandas and numpy (avoids compilation issues)
3. **Polars**: Rust-based alternative that doesn't require compilation

## Run Script Features

The unified `run.sh` script provides several features:

### Usage

```
./run.sh [standard|binary|polars]
```

If no option is provided, it will default to the binary installation option.

### Key Features

1. **Automatic Dependency Selection**: The script parses `requirements.txt` and selects the appropriate data processing option.
2. **Fallback Mechanism**: If pandas installation fails, it will automatically fall back to polars.
3. **Virtual Environment Handling**: Creates and manages virtual environments based on the selected option.
4. **Polars Adapter**: Automatically creates a compatibility layer when using polars.
5. **Project Structure**: Ensures all necessary directories and files exist.

### Examples

```bash
# Use binary wheels for pandas/numpy (default)
./run.sh

# Use standard pandas/numpy installation
./run.sh standard

# Use polars instead of pandas/numpy
./run.sh polars
```

## Previous Requirements Files

The original project had multiple requirements files:

1. `requirements.txt`: Original requirements
2. `requirements_fixed.txt`: With binary options for pandas/numpy
3. `requirements_minimal.txt`: Using polars instead of pandas

These have been consolidated into a single, well-documented `requirements.txt` file with all options.

## Previous Run Scripts

Similarly, the project had multiple run scripts:

1. `run.sh`: Original script
2. `run_fixed.sh`: Using fixed requirements
3. `run_minimal.sh`: Using minimal requirements with polars

These have been consolidated into a single unified `run.sh` script that can handle all scenarios.
