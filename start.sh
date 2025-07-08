#!/bin/bash

echo "Starting Server Inventory Management System..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the application
echo
echo "Starting Flask application..."
echo "Access the application at: http://localhost:5000"
echo "Default admin credentials: admin/admin123"
echo

cd backend
python app.py