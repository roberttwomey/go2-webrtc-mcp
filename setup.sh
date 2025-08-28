#!/bin/bash

# Unitree Go2 WebRTC MCP Server Setup Script (FastMCP)
# This script automates the installation and setup process using conda

set -e

echo "=== Unitree Go2 WebRTC MCP Server Setup (FastMCP) ==="
echo ""

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "Error: conda is not installed. Please install conda first."
    echo "You can install Miniconda from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Check conda version
CONDA_VERSION=$(conda --version)
echo "Found conda: $CONDA_VERSION"

# Check if conda environment already exists
if conda env list | grep -q "bff-mcp"; then
    echo "Conda environment 'bff-mcp' already exists."
    read -p "Do you want to remove it and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing environment..."
        conda env remove -n bff-mcp
    else
        echo "Using existing environment."
    fi
fi

# Create conda environment if it doesn't exist
if ! conda env list | grep -q "bff-mcp"; then
    echo ""
    echo "Creating conda environment 'bff-mcp' with Python 3.10..."
    conda create -n bff-mcp python=3.10 -y
fi

# Activate conda environment
echo ""
echo "Activating conda environment 'bff-mcp'..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate bff-mcp

# Verify Python version in conda environment
PYTHON_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python version in conda environment: $PYTHON_VERSION"

# Check if pip is available in conda environment
if ! command -v pip &> /dev/null; then
    echo "Error: pip is not available in conda environment. Installing pip..."
    conda install pip -y
fi

echo ""
echo "Installing Python dependencies in conda environment..."

# Install Python dependencies
pip install -r requirements.txt

echo ""
echo "Installing go2_webrtc_connect driver..."

# Clone and install the WebRTC driver
if [ ! -d "go2_webrtc_connect" ]; then
    git clone --recurse-submodules https://github.com/legion1581/go2_webrtc_connect.git
fi

cd go2_webrtc_connect
pip install -e .
cd ..

echo ""
echo "Setting up MCP configuration..."

# Create MCP configuration directory if it doesn't exist
MCP_CONFIG_DIR="$HOME/.config/mcp"
mkdir -p "$MCP_CONFIG_DIR"

# Copy MCP configuration
cp mcp.json "$MCP_CONFIG_DIR/"

echo ""
echo "Testing installation..."

# Test the installation
python test_installation.py

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "The FastMCP server has been installed in conda environment 'bff-mcp'."
echo ""
echo "IMPORTANT: Always activate the conda environment before using the server:"
echo "conda activate bff-mcp"
echo ""
echo "To use with Claude Desktop:"
echo "1. Open Claude Desktop"
echo "2. Go to Settings > MCP Servers"
echo "3. Update the server configuration to use conda:"
echo "   {"
echo "     \"mcpServers\": {"
echo "       \"go2-webrtc\": {"
echo "         \"command\": \"conda\","
echo "         \"args\": [\"run\", \"-n\", \"bff-mcp\", \"python\", \"server.py\"]"
echo "       }"
echo "     }"
echo "   }"
echo ""
echo "To test the server:"
echo "conda activate bff-mcp"
echo "python example_usage.py"
echo ""
echo "To run the MCP server:"
echo "conda activate bff-mcp"
echo "python server.py"
echo ""
echo "To test with MCP Inspector:"
echo "conda activate bff-mcp"
echo "pip install 'mcp[cli]'"
echo "mcp dev server.py"
echo ""
echo "Configuration files are located at: $MCP_CONFIG_DIR"
echo ""
echo "For more information, see the README.md file."
echo ""
echo "To deactivate the conda environment when done:"
echo "conda deactivate"
