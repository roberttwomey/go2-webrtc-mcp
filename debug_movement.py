#!/usr/bin/env python3
"""
Debug script to test movement commands
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def debug_movement():
    """Debug movement commands with proper sequence"""
    
    print("=== Debugging Movement Commands ===\n")
    
    try:
        # Import after path setup
        from server import connect, stand, move_robot, disconnect
        
        # Connect to robot
        print("1. Connecting to robot...")
        result = await connect(method="LocalSTA", ip="192.168.4.30")
        print(f"Connect result: {result}")
        
        if not result.get("ok"):
            print("Failed to connect!")
            return
        
        await asyncio.sleep(2)
        
        print("\n2. Standing up...")
        result = await stand()
        print(f"Stand result: {result}")
        await asyncio.sleep(5)  # Wait for robot to stand
        
        print("\n3. Testing small forward movement (0.3)...")
        result = await move_robot(x=0.3, y=0.0, z=0.0)
        print(f"Small forward movement result: {result}")
        await asyncio.sleep(3)
        
        print("\n4. Testing small turn (0.2)...")
        result = await move_robot(x=0.0, y=0.0, z=0.2)
        print(f"Small turn result: {result}")
        await asyncio.sleep(3)
        
        print("\n5. Testing stop...")
        result = await move_robot(x=0.0, y=0.0, z=0.0)
        print(f"Stop result: {result}")
        await asyncio.sleep(2)
        
        print("\n6. Disconnecting...")
        result = await disconnect()
        print(f"Disconnect result: {result}")
        
    except Exception as e:
        print(f"Error during debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_movement())
