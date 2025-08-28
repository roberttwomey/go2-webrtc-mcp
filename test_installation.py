#!/usr/bin/env python3
"""
Test script to verify the installation of the Unitree Go2 WebRTC MCP Server
"""

import sys
import importlib

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        if package_name:
            module = importlib.import_module(module_name, package_name)
        else:
            module = importlib.import_module(module_name)
        print(f"✓ {module_name} imported successfully")
        return True
    except ImportError as e:
        print(f"✗ {module_name} import failed: {e}")
        return False

def main():
    """Test all required dependencies"""
    print("=== Testing Unitree Go2 WebRTC MCP Server Installation ===\n")
    
    # Test Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("✗ Python 3.8 or higher is required")
        return False
    else:
        print("✓ Python version is compatible\n")
    
    # Test MCP dependencies
    print("Testing MCP dependencies:")
    mcp_modules = [
        "mcp.server",
        "mcp.server.models", 
        "mcp.server.stdio",
        "mcp.types"
    ]
    
    mcp_success = True
    for module in mcp_modules:
        if not test_import(module):
            mcp_success = False
    
    print()
    
    # Test WebRTC driver
    print("Testing WebRTC driver:")
    webrtc_success = test_import("go2_webrtc_driver")
    print()
    
    # Test local server
    print("Testing local server:")
    local_success = test_import("server")
    print()
    
    # Summary
    print("=== Installation Test Summary ===")
    if mcp_success and webrtc_success and local_success:
        print("✓ All dependencies are properly installed!")
        print("✓ The MCP server is ready to use!")
        return True
    else:
        print("✗ Some dependencies are missing or failed to import")
        print("\nTo fix installation issues:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Install the WebRTC driver: git clone --recurse-submodules https://github.com/legion1581/go2_webrtc_connect.git")
        print("3. Run: cd go2_webrtc_connect && pip install -e .")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
