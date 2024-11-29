#!/bin/bash

# Set the project directory and venv paths
PROJECT_DIR="./Desktop/pi ocr"
VENV_DIR="$PROJECT_DIR/venv"

# Create requirements.txt if it doesn't exist
create_requirements() {
    cat > "$PROJECT_DIR/requirements.txt" << EOF
opencv-python==4.8.0
numpy==1.24.3
pytesseract==0.3.10
Pillow==10.0.0
fuzzywuzzy==0.18.0
python-Levenshtein==0.21.1
EOF
    echo "Created requirements.txt file"
}

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Creating project directory..."
    mkdir -p "$PROJECT_DIR"
fi

# Navigate to project directory
cd "$PROJECT_DIR" || {
    echo "Error: Failed to change to project directory!"
    exit 1
}

# Check if requirements.txt exists, if not create it
if [ ! -f "requirements.txt" ]; then
    echo "Requirements.txt not found. Creating..."
    create_requirements
fi

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating new environment..."
    python3 -m venv "$VENV_DIR"
    
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment!"
        exit 1
    fi
    echo "Virtual environment created successfully"
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment!"
    exit 1
fi

# Install/Update requirements
echo "Installing/Updating requirements..."
pip install -r requirements.txt

# Check if final_version.py exists
if [ ! -f "final_version.py" ]; then
    echo "Error: final_version.py not found!"
    deactivate
    exit 1
fi

# Run the Python script
echo "Starting OCR program..."
python3 final_version.py

# Deactivate the virtual environment when done
deactivate