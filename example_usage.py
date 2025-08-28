#!/usr/bin/env python3
"""
Example usage of the Unitree Go2 WebRTC MCP Server using FastMCP
This script demonstrates how to use the server programmatically.
"""

import asyncio
import json
from server import mcp, state

async def example_usage():
    """Example of how to use the MCP server"""
    
    print("=== Unitree Go2 WebRTC MCP Server Example ===\n")
    
    # Example 1: Connect to robot
    print("1. Connecting to robot...")
    result = await mcp.tools["connect"].call(
        method="LocalSTA",
        ip="192.168.4.30"  # Replace with your robot's IP
    )
    print(f"Result: {result}\n")
    
    # Example 2: Check robot status
    print("2. Checking robot status...")
    result = await mcp.tools["robot_status"].call()
    print(f"Status: {result}\n")
    
    # Example 3: Stand up
    print("3. Standing up robot...")
    result = await mcp.tools["stand"].call()
    print(f"Result: {result}\n")
    
    # Example 4: Move robot forward
    print("4. Moving robot forward...")
    result = await mcp.tools["jog"].call(
        lx=0.3,
        ly=0.0,
        yaw=0.0,
        duration_s=2.0
    )
    print(f"Result: {result}\n")
    
    # Example 5: Execute natural language command
    print("5. Executing natural language command...")
    result = await mcp.tools["execute_command"].call(
        command="Turn the robot left"
    )
    print(f"Result: {result}\n")
    
    # Example 6: Get low state
    print("6. Getting low state...")
    result = await mcp.tools["lowstate"].call()
    print(f"Result: {result}\n")
    
    # Example 7: Disconnect from robot
    print("7. Disconnecting from robot...")
    result = await mcp.tools["disconnect"].call()
    print(f"Result: {result}\n")
    
    print("=== Example completed ===")

async def test_connection_methods():
    """Test different connection methods"""
    
    print("=== Testing Connection Methods ===\n")
    
    # Test Local AP mode
    print("Testing Local AP mode...")
    try:
        result = await mcp.tools["connect"].call(method="LocalAP")
        print(f"Local AP: {result}")
        if result.get("ok"):
            await mcp.tools["disconnect"].call()
    except Exception as e:
        print(f"Local AP failed: {e}")
    
    # Test Local STA mode with IP
    print("\nTesting Local STA mode with IP...")
    try:
        result = await mcp.tools["connect"].call(
            method="LocalSTA",
            ip="192.168.8.181"
        )
        print(f"Local STA (IP): {result}")
        if result.get("ok"):
            await mcp.tools["disconnect"].call()
    except Exception as e:
        print(f"Local STA (IP) failed: {e}")
    
    # Test Local STA mode with serial number
    print("\nTesting Local STA mode with serial number...")
    try:
        result = await mcp.tools["connect"].call(
            method="LocalSTA",
            serial="B42D2000XXXXXXXX"  # Replace with your robot's serial
        )
        print(f"Local STA (Serial): {result}")
        if result.get("ok"):
            await mcp.tools["disconnect"].call()
    except Exception as e:
        print(f"Local STA (Serial) failed: {e}")
    
    print("\n=== Connection method tests completed ===")

async def test_robot_commands():
    """Test various robot commands"""
    
    print("=== Testing Robot Commands ===\n")
    
    # Connect first
    print("Connecting to robot...")
    result = await mcp.tools["connect"].call(
        method="LocalSTA",
        ip="192.168.8.181"
    )
    
    if not result.get("ok"):
        print(f"Failed to connect: {result}")
        return
    
    print("Connected successfully!\n")
    
    try:
        # Test stand
        print("Testing stand command...")
        result = await mcp.tools["stand"].call()
        print(f"Stand: {result}")
        
        # Test jog
        print("\nTesting jog command...")
        result = await mcp.tools["jog"].call(lx=0.2, duration_s=1.0)
        print(f"Jog: {result}")
        
        # Test sit
        print("\nTesting sit command...")
        result = await mcp.tools["sit"].call()
        print(f"Sit: {result}")
        
        # Test natural language
        print("\nTesting natural language command...")
        result = await mcp.tools["execute_command"].call(command="dance")
        print(f"Dance: {result}")
        
    finally:
        # Always disconnect
        print("\nDisconnecting...")
        await mcp.tools["disconnect"].call()
    
    print("\n=== Robot command tests completed ===")

if __name__ == "__main__":
    print("Choose an example to run:")
    print("1. Basic usage example")
    print("2. Test connection methods")
    print("3. Test robot commands")
    
    choice = input("Enter your choice (1, 2, or 3): ").strip()
    
    if choice == "1":
        asyncio.run(example_usage())
    elif choice == "2":
        asyncio.run(test_connection_methods())
    elif choice == "3":
        asyncio.run(test_robot_commands())
    else:
        print("Invalid choice. Running basic example...")
        asyncio.run(example_usage())
