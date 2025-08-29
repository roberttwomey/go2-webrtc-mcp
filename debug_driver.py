#!/usr/bin/env python3
"""
Debug script to inspect the go2_webrtc_connect driver
"""

import sys

def debug_driver():
    """Debug the go2_webrtc_connect driver to see available methods"""
    
    print("=== Debugging go2_webrtc_connect driver ===\n")
    
    try:
        # Try to import the driver
        print("1. Testing imports...")
        
        try:
            from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
            print("✓ Successfully imported Go2WebRTCConnection and WebRTCConnectionMethod")
        except ImportError as e:
            print(f"✗ Import error: {e}")
            return False
        
        try:
            from go2_webrtc_driver.constants import RTC_TOPIC
            print("✓ Successfully imported RTC_TOPIC")
            print(f"  RTC_TOPIC keys: {list(RTC_TOPIC.keys()) if RTC_TOPIC else 'Empty'}")
        except ImportError as e:
            print(f"✗ RTC_TOPIC import error: {e}")
        
        print("\n2. Inspecting Go2WebRTCConnection class...")
        
        # Get all methods and attributes
        methods = [attr for attr in dir(Go2WebRTCConnection) if not attr.startswith('_')]
        print(f"Available methods/attributes ({len(methods)}):")
        for method in sorted(methods):
            print(f"  - {method}")
        
        print("\n3. Looking for send/publish methods...")
        send_methods = [m for m in methods if 'send' in m.lower() or 'publish' in m.lower()]
        if send_methods:
            print(f"Found potential send/publish methods: {send_methods}")
        else:
            print("No obvious send/publish methods found")
        
        print("\n4. Looking for API methods...")
        api_methods = [m for m in methods if 'api' in m.lower()]
        if api_methods:
            print(f"Found API-related methods: {api_methods}")
        else:
            print("No obvious API methods found")
        
        print("\n5. Looking for movement methods...")
        movement_methods = [m for m in methods if any(word in m.lower() for word in ['move', 'walk', 'stand', 'sit', 'jog'])]
        if movement_methods:
            print(f"Found movement-related methods: {movement_methods}")
        else:
            print("No obvious movement methods found")
        
        print("\n6. Testing connection creation...")
        try:
            # Try to create a connection object (without actually connecting)
            conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
            print("✓ Successfully created connection object")
            
            # Check methods on the instance
            instance_methods = [attr for attr in dir(conn) if not attr.startswith('_')]
            print(f"Instance methods ({len(instance_methods)}):")
            for method in sorted(instance_methods):
                print(f"  - {method}")
            
            # Look for send/publish methods on instance
            instance_send_methods = [m for m in instance_methods if 'send' in m.lower() or 'publish' in m.lower()]
            if instance_send_methods:
                print(f"\nInstance send/publish methods: {instance_send_methods}")
            
        except Exception as e:
            print(f"✗ Error creating connection: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_driver()
    sys.exit(0 if success else 1)
