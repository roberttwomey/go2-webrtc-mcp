#!/usr/bin/env python3
"""
Test script to debug movement commands
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_movement():
    """Test basic movement commands"""
    
    print("=== Testing Movement Commands ===\n")
    
    try:
        # Import after path setup
        from server import connect, jog, stand, sit, disconnect, liedown
        
        # Connect to robot
        print("1. Connecting to robot...")
        result = await connect(method="LocalSTA", ip="192.168.4.30")
        print(f"Connect result: {result}")
        
        if not result.get("ok"):
            print("Failed to connect!")
            return
        
        print("\n2. Standing up...")
        result = await stand()
        print(f"Stand result: {result}")
        await asyncio.sleep(3)
        
        print("\n3. Testing forward movement...")
        result = await jog(lx=2.0, ly=0.0, yaw=0.0, duration_s=2.0)
        print(f"Forward movement result: {result}")
        await asyncio.sleep(3)
        
        print("\n4. Testing turn...")
        result = await jog(lx=0.0, ly=0.0, yaw=1.5, duration_s=2.0)
        print(f"Turn result: {result}")
        await asyncio.sleep(3)
        
        # print("\n5. Sitting down...")
        # result = await sit()
        # print(f"Sit result: {result}")
        # await asyncio.sleep(2)
        
        print("\n5. lie down...")
        result = await liedown()
        print(f"Sit result: {result}")
        await asyncio.sleep(2)

        print("\n6. Disconnecting...")
        result = await disconnect()
        print(f"Disconnect result: {result}")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_movement())
