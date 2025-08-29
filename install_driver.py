#!/usr/bin/env python3
"""
Installation and troubleshooting script for go2_webrtc_connect driver
"""

import os
import subprocess
import sys

def install_driver():
    """Install the go2_webrtc_connect driver"""
    
    print("=== Installing go2_webrtc_connect driver ===\n")
    
    # Check if already installed
    try:
        import go2_webrtc_driver
        print("✓ go2_webrtc_connect appears to be already installed")
        return True
    except ImportError:
        print("✗ go2_webrtc_connect not found, installing...")
    
    # Clone the repository
    if not os.path.exists("go2_webrtc_connect"):
        print("Cloning go2_webrtc_connect repository...")
        try:
            subprocess.run([
                "git", "clone", "--recurse-submodules", 
                "https://github.com/legion1581/go2_webrtc_connect.git"
            ], check=True)
            print("✓ Repository cloned successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to clone repository: {e}")
            return False
    else:
        print("✓ Repository already exists")
    
    # Install the driver
    print("Installing driver...")
    try:
        os.chdir("go2_webrtc_connect")
        subprocess.run(["pip", "install", "-e", "."], check=True)
        os.chdir("..")
        print("✓ Driver installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install driver: {e}")
        os.chdir("..")
        return False

def test_driver():
    """Test if the driver is working correctly"""
    
    print("\n=== Testing go2_webrtc_connect driver ===\n")
    
    try:
        from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
        print("✓ Successfully imported Go2WebRTCConnection and WebRTCConnectionMethod")
        
        # Test creating a connection object
        conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
        print("✓ Successfully created connection object")
        
        # List available methods
        methods = [attr for attr in dir(conn) if not attr.startswith('_')]
        print(f"✓ Available methods: {methods}")
        
        # Look for send/publish methods
        send_methods = [m for m in methods if 'send' in m.lower() or 'publish' in m.lower()]
        if send_methods:
            print(f"✓ Found send/publish methods: {send_methods}")
        else:
            print("⚠ No obvious send/publish methods found")
            print("Available methods that might be relevant:")
            for method in methods:
                if any(word in method.lower() for word in ['api', 'request', 'call', 'command']):
                    print(f"  - {method}")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing driver: {e}")
        return False

def main():
    """Main installation and testing function"""
    
    print("go2_webrtc_connect Driver Installation and Testing\n")
    
    # Try to install if not already installed
    if not install_driver():
        print("\nInstallation failed. Please try manually:")
        print("1. git clone --recurse-submodules https://github.com/legion1581/go2_webrtc_connect.git")
        print("2. cd go2_webrtc_connect")
        print("3. pip install -e .")
        return False
    
    # Test the driver
    if not test_driver():
        print("\nDriver test failed. Please check the installation.")
        return False
    
    print("\n=== Installation and testing completed successfully! ===")
    print("You can now run the MCP server.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
