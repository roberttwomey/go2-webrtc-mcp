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
        "ip_address": "192.168.4.30"  # Replace with your robot's IP
    })
    print(f"Result: {result.content[0].text}\n")
    await asyncio.sleep(3)

    # Example 2: Check robot status
    print("2. Checking robot status...")
    result = await server.robot_status({})
    print(f"Status: {result.content[0].text}\n")
    await asyncio.sleep(3)

    # Example 3: Move robot forward
    print("3. Moving robot forward...")
    result = await server.move_robot({
        "x": 0.3,
        "duration": 2.0,
    })
    print(f"Result: {result.content[0].text}\n")
    await asyncio.sleep(3)

    # Example 4: Execute natural language command
    print("4. Executing natural language command...")
    result = await server.execute_command({
        "command": "Turn the robot left"
    })
    print(f"Result: {result.content[0].text}\n")
    await asyncio.sleep(3)
    # Example 5: Disconnect from robot
    print("5. Disconnecting from robot...")
    result = await server.disconnect_robot({})
    print(f"Result: {result.content[0].text}\n")
    await asyncio.sleep(3)

    print("=== Example completed ===")


if __name__ == "__main__":
    asyncio.run(example_usage())
