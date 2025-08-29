#!/usr/bin/env python3
"""
Example usage of the Unitree Go2 WebRTC MCP Server using FastMCP
This script demonstrates how to use the server programmatically.
"""

import asyncio
import json
from server import (
    mcp, state, connect, disconnect, jog, stand, balance_stand, sit, estop, 
    lowstate, multistate, front_photo, publish, robot_status, execute_command,
    # New wireless controller tools
    wireless_controller_publish, stand_up_from_fall, stretch,
    shake_hands, love, pounce, jump_forward, sit_down,
    greet, dance, stop_movement
)

async def example_usage():
    """Example of how to use the MCP server"""
    
    print("=== Unitree Go2 WebRTC MCP Server Example ===\n")
    
    # Example 1: Connect to robot
    print("1. Connecting to robot...")
    result = await connect(
        method="LocalSTA",
        ip="192.168.4.30"  # Replace with your robot's IP
    )
    print(f"Result: {result}\n")
    await asyncio.sleep(2)  # Pause between commands
    
    # Example 2: Check robot status
    print("2. Checking robot status...")
    result = await robot_status()
    print(f"Status: {result}\n")
    await asyncio.sleep(2)  # Pause between commands
    
    # Example 3: Stand up
    print("3. Standing up robot...")
    result = await stand()
    print(f"Result: {result}\n")
    await asyncio.sleep(2)  # Longer pause after stand command
    
    # Example 4: Balance stand
    print("4. Balancing robot...")
    result = await balance_stand()
    print(f"Result: {result}\n")
    await asyncio.sleep(2)  # Longer pause after stand command
    

    # # Example 3.5: Sit down
    # print("3.5 Sitting down...")
    # result = await sit()
    # print(f"Result: {result}\n")
    # await asyncio.sleep(2)  # Longer pause after stand command

    # Example 4: Move robot forward
    print("4. Moving robot forward...")
    result = await jog(
        lx=0.3,
        ly=0.0,
        yaw=0.0,
        duration_s=2.0
    )
    print(f"Result: {result}\n")
    await asyncio.sleep(2)  # Pause between commands
    
    # Example 5: Execute natural language command
    print("5. Executing natural language command...")
    result = await execute_command(
        command="Turn the robot left"
    )
    print(f"Result: {result}\n")
    await asyncio.sleep(2)  # Pause between commands
    
    # Example 6: Get low state
    print("6. Getting low state...")
    result = await lowstate()
    print(f"Result: {result}\n")
    await asyncio.sleep(2)  # Pause between commands
    
    # Example 7: Disconnect from robot
    print("7. Disconnecting from robot...")
    result = await disconnect()
    print(f"Result: {result}\n")
    
    print("=== Example completed ===")

async def test_wireless_controller():
    """Test wireless controller functions"""
    
    print("=== Testing Wireless Controller Functions ===\n")
    
    # Connect first
    print("Connecting to robot...")
    result = await connect(
        method="LocalSTA",
        ip="192.168.4.30"
    )
    
    if not result.get("ok"):
        print(f"Failed to connect: {result}")
        return
    
    print("Connected successfully!\n")
    
    try:
        # Test wireless controller publish
        print("Testing wireless controller publish...")
        result = await wireless_controller_publish(
            lx=0.0, ly=0.3, rx=0.0, ry=0.0, keys=0, duration=1.0
        )
        print(f"Wireless controller: {result}")
        await asyncio.sleep(3)  # Pause between commands
        
        # Test stand up from fall
        print("\nTesting stand up from fall...")
        result = await stand_up_from_fall()
        print(f"Stand up from fall: {result}")
        await asyncio.sleep(3)  # Pause between commands
        
        # Test stretch
        print("\nTesting stretch...")
        result = await stretch()
        print(f"Stretch: {result}")
        await asyncio.sleep(3)  # Pause between commands
        
        # Test shake hands
        print("\nTesting shake hands...")
        result = await shake_hands()
        print(f"Shake hands: {result}")
        await asyncio.sleep(3)  # Pause between commands
        
        # Test love
        print("\nTesting love...")
        result = await love()
        print(f"Love: {result}")
        await asyncio.sleep(3)  # Pause between commands
        
        # Test pounce
        print("\nTesting pounce...")
        result = await pounce()
        print(f"Pounce: {result}")
        await asyncio.sleep(3)  # Pause between commands
        
        # Test jump forward
        print("\nTesting jump forward...")
        result = await jump_forward()
        print(f"Jump forward: {result}")
        await asyncio.sleep(3)  # Pause between commands
        
        # Test sit down
        print("\nTesting sit down...")
        result = await sit_down()
        print(f"Sit down: {result}")
        await asyncio.sleep(3)  # Pause between commands
        
        # Test greet
        print("\nTesting greet...")
        result = await greet()
        print(f"Greet: {result}")
        await asyncio.sleep(3)  # Pause between commands
        
        # Test dance
        print("\nTesting dance...")
        result = await dance()
        print(f"Dance: {result}")
        await asyncio.sleep(3)  # Pause between commands
        
        # Test stop movement
        print("\nTesting stop movement...")
        result = await stop_movement()
        print(f"Stop movement: {result}")
        await asyncio.sleep(2)  # Pause before disconnect
        
    finally:
        # Always disconnect
        print("\nDisconnecting...")
        await disconnect()
    
    print("\n=== Wireless controller tests completed ===")

async def test_connection_methods():
    """Test different connection methods"""
    
    print("=== Testing Connection Methods ===\n")
    
    # # Test Local AP mode
    # print("Testing Local AP mode...")
    # try:
    #     result = await connect(method="LocalAP")
    #     print(f"Local AP: {result}")
    #     if result.get("ok"):
    #         await disconnect()
    # except Exception as e:
    #     print(f"Local AP failed: {e}")
    
    # Test Local STA mode with IP
    print("Testing Local STA mode with IP...")
    try:
        result = await connect(
            method="LocalSTA",
            ip="192.168.4.30"
        )
        print(f"Local STA (IP): {result}")
        if result.get("ok"):
            await disconnect()
    except Exception as e:
        print(f"Local STA (IP) failed: {e}")
    
    # # Test Local STA mode with serial number
    # print("\nTesting Local STA mode with serial number...")
    # try:
    #     result = await connect(
    #         method="LocalSTA",
    #         serial="B42D2000XXXXXXXX"  # Replace with your robot's serial
    #     )
    #     print(f"Local STA (Serial): {result}")
    #     if result.get("ok"):
    #         await disconnect()
    # except Exception as e:
    #     print(f"Local STA (Serial) failed: {e}")
    
    # print("\n=== Connection method tests completed ===")

async def test_robot_commands():
    """Test various robot commands"""
    
    print("=== Testing Robot Commands ===\n")
    
    # Connect first
    print("Connecting to robot...")
    result = await connect(
        method="LocalSTA",
        ip="192.168.4.30"
    )
    
    if not result.get("ok"):
        print(f"Failed to connect: {result}")
        return
    
    print("Connected successfully!\n")
    
    try:
        # Test stand
        print("Testing stand command...")
        result = await stand()
        print(f"Stand: {result}")
        await asyncio.sleep(3)  # Pause between commands
        
        # Test jog
        print("\nTesting jog command...")
        result = await jog(lx=0.2, duration_s=1.0)
        print(f"Jog: {result}")
        await asyncio.sleep(3)  # Pause between commands
        
        # Test sit
        print("\nTesting sit command...")
        result = await sit()
        print(f"Sit: {result}")
        await asyncio.sleep(3)  # Pause between commands
        
        # Test natural language
        print("\nTesting natural language command...")
        result = await execute_command(command="dance")
        print(f"Dance: {result}")
        await asyncio.sleep(2)  # Pause before disconnect
        
    finally:
        # Always disconnect
        print("\nDisconnecting...")
        await disconnect()
    
    print("\n=== Robot command tests completed ===")

if __name__ == "__main__":
    print("Choose an example to run:")
    print("1. Basic usage example")
    print("2. Test connection methods")
    print("3. Test robot commands")
    print("4. Test wireless controller functions")
    
    choice = input("Enter your choice (1, 2, 3, or 4): ").strip()
    
    if choice == "1":
        asyncio.run(example_usage())
    elif choice == "2":
        asyncio.run(test_connection_methods())
    elif choice == "3":
        asyncio.run(test_robot_commands())
    elif choice == "4":
        asyncio.run(test_wireless_controller())
    else:
        print("Invalid choice. Running basic example...")
        asyncio.run(example_usage())
