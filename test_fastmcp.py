#!/usr/bin/env python3
"""
Simple test script to verify FastMCP tools are working correctly
"""

import asyncio
import sys

async def test_fastmcp_tools():
    """Test that FastMCP tools can be imported and called"""
    
    print("=== Testing FastMCP Tools ===\n")
    
    try:
        # Import the tools
        from server import (
            mcp, state, connect, disconnect, jog, stand, sit, 
            estop, lowstate, multistate, front_photo, publish, 
            robot_status, execute_command
        )
        
        print("✓ Successfully imported all FastMCP tools")
        print(f"✓ FastMCP server: {mcp}")
        print(f"✓ Robot state: {state}")
        
        # Test that tools are callable
        tools = [
            connect, disconnect, jog, stand, sit, estop, 
            lowstate, multistate, front_photo, publish, 
            robot_status, execute_command
        ]
        
        print(f"\n✓ Found {len(tools)} MCP tools:")
        for tool in tools:
            print(f"  - {tool.__name__}: {callable(tool)}")
        
        # Test robot_status (should work without connection)
        print("\nTesting robot_status tool...")
        result = await robot_status()
        print(f"Result: {result}")
        
        print("\n=== FastMCP Tools Test Passed! ===")
        return True
        
    except Exception as e:
        print(f"✗ FastMCP Tools Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_fastmcp_tools())
    sys.exit(0 if success else 1)
