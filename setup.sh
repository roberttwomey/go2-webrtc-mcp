#!/bin/bash

# Unitree Go2 WebRTC MCP Server Setup Script
# This script automates the installation and setup process

set -e

echo "=== Unitree Go2 WebRTC MCP Server Setup ==="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Found Python version: $PYTHON_VERSION"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo ""
echo "Installing Python dependencies..."

# Install Python dependencies
pip3 install -r requirements.txt

echo ""
echo "Installing go2_webrtc_connect driver..."

# Clone and install the WebRTC driver
if [ ! -d "go2_webrtc_connect" ]; then
    git clone --recurse-submodules https://github.com/legion1581/go2_webrtc_connect.git
fi

cd go2_webrtc_connect
pip3 install -e .
cd ..

echo ""
echo "Setting up MCP configuration..."

# Create MCP configuration directory if it doesn't exist
MCP_CONFIG_DIR="$HOME/.config/mcp"
mkdir -p "$MCP_CONFIG_DIR"

# Copy MCP configuration
cp mcp.json "$MCP_CONFIG_DIR/"

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "The MCP server has been installed and configured."
echo ""
echo "To use with Claude Desktop:"
echo "1. Open Claude Desktop"
echo "2. Go to Settings > MCP Servers"
echo "3. Add the server configuration from mcp.json"
echo ""
echo "To test the server:"
echo "python3 example_usage.py"
echo ""
echo "To run the MCP server:"
echo "python3 server.py"
echo ""
echo "Configuration files are located at: $MCP_CONFIG_DIR"
echo ""
echo "For more information, see the README.md file."
