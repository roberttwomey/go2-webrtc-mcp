#!/usr/bin/env python3
"""
Example usage of the Unitree Go2 WebRTC MCP Server
This script demonstrates how to use the server programmatically.
"""

import asyncio
import json
from server import Go2WebRTCMCPServer

async def example_usage():
    """Example of how to use the MCP server"""
    
    # Create server instance
    server = Go2WebRTCMCPServer()
    
    print("=== Unitree Go2 WebRTC MCP Server Example ===\n")
    
    # Example 1: Connect to robot
    print("1. Connecting to robot...")
    result = await server.connect_robot({
        "connection_method": "local_sta",
        "ip_address": "192.168.8.181"  # Replace with your robot's IP
    })
    print(f"Result: {result.content[0].text}\n")
    
    # Example 2: Check robot status
    print("2. Checking robot status...")
    result = await server.robot_status({})
    print(f"Status: {result.content[0].text}\n")
    
    # Example 3: Move robot forward
    print("3. Moving robot forward...")
    result = await server.move_robot({
        "action": "forward",
        "duration": 2.0,
        "speed": 0.5
    })
    print(f"Result: {result.content[0].text}\n")
    
    # Example 4: Execute natural language command
    print("4. Executing natural language command...")
    result = await server.execute_command({
        "command": "Turn the robot left"
    })
    print(f"Result: {result.content[0].text}\n")
    
    # Example 5: Disconnect from robot
    print("5. Disconnecting from robot...")
    result = await server.disconnect_robot({})
    print(f"Result: {result.content[0].text}\n")
    
    print("=== Example completed ===")

async def test_connection_methods():
    """Test different connection methods"""
    
    server = Go2WebRTCMCPServer()
    
    print("=== Testing Connection Methods ===\n")
    
    # Test Local AP mode
    print("Testing Local AP mode...")
    try:
        result = await server.connect_robot({"connection_method": "local_ap"})
        print(f"Local AP: {result.content[0].text}")
        if "Successfully" in result.content[0].text:
            await server.disconnect_robot({})
    except Exception as e:
        print(f"Local AP failed: {e}")
    
    # Test Local STA mode with IP
    print("\nTesting Local STA mode with IP...")
    try:
        result = await server.connect_robot({
            "connection_method": "local_sta",
            "ip_address": "192.168.8.181"
        })
        print(f"Local STA (IP): {result.content[0].text}")
        if "Successfully" in result.content[0].text:
            await server.disconnect_robot({})
    except Exception as e:
        print(f"Local STA (IP) failed: {e}")
    
    # Test Local STA mode with serial number
    print("\nTesting Local STA mode with serial number...")
    try:
        result = await server.connect_robot({
            "connection_method": "local_sta",
            "serial_number": "B42D2000XXXXXXXX"  # Replace with your robot's serial
        })
        print(f"Local STA (Serial): {result.content[0].text}")
        if "Successfully" in result.content[0].text:
            await server.disconnect_robot({})
    except Exception as e:
        print(f"Local STA (Serial) failed: {e}")
    
    print("\n=== Connection method tests completed ===")

if __name__ == "__main__":
    print("Choose an example to run:")
    print("1. Basic usage example")
    print("2. Test connection methods")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(example_usage())
    elif choice == "2":
        asyncio.run(test_connection_methods())
    else:
        print("Invalid choice. Running basic example...")
        asyncio.run(example_usage())
