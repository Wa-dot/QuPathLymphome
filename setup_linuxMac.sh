#!/bin/bash

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install Python3 first."
    exit 1
fi

# Create a virtual environment
python3 -m venv pythonEnv

# Activate the virtual environment
source pythonEnv/bin/activate

# Install dependencies from requirements.txt
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Please ensure the file is in the project directory."
    deactivate
    exit 1
fi

# Inform the user that setup is complete
echo "Setup complete. The virtual environment is ready to use."
