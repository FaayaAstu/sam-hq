#!/bin/bash

# Check if we're in the correct directory
if [ ! -f "setup.py" ]; then
    echo "Error: Please run this script from the root directory of the project"
    exit 1
fi

# Step 1: Install core SAM-HQ package
echo "Installing core SAM-HQ package..."
pip install -e . || {
    echo "Error: Failed to install SAM-HQ package"
    exit 1
}

# Verify the package is installed
echo "Verifying SAM-HQ installation..."
python -c "import segment_anything" || {
    echo "Error: SAM-HQ package is not properly installed"
    exit 1
}

# Step 2: Install FastAPI application
echo "Setting up FastAPI application..."
cd supervisely_integration || {
    echo "Error: Failed to change to supervisely_integration directory"
    exit 1
}

# Run the Python setup script
PYTHONPATH=$PYTHONPATH:.. python setup_app.py || {
    echo "Error: Failed to setup FastAPI application"
    exit 1
}

# Return to root directory
cd ..

echo "Setup completed successfully!"
echo ""
echo "To start the FastAPI server:"
echo "1. cd supervisely_integration/serve"
echo "2. python -m uvicorn main:app --reload"
echo ""
echo "The server will be available at: http://localhost:8000" 