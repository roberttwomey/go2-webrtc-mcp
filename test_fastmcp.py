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
            robot_status, execute_command,
            # New wireless controller tools
            wireless_controller_publish, stand_up_from_fall, stretch,
            shake_hands, love, pounce, jump_forward, sit_down,
            greet, dance, stop_movement
        )
        
        print("✓ Successfully imported all FastMCP tools")
        print(f"✓ FastMCP server: {mcp}")
        print(f"✓ Robot state: {state}")
        
        # Test that tools are callable
        basic_tools = [
            connect, disconnect, jog, stand, sit, estop, 
            lowstate, multistate, front_photo, publish, 
            robot_status, execute_command
        ]
        
        wireless_tools = [
            wireless_controller_publish, stand_up_from_fall, stretch,
            shake_hands, love, pounce, jump_forward, sit_down,
            greet, dance, stop_movement
        ]
        
        all_tools = basic_tools + wireless_tools
        
        print(f"\n✓ Found {len(all_tools)} MCP tools:")
        print("\nBasic Tools:")
        for tool in basic_tools:
            print(f"  - {tool.__name__}: {callable(tool)}")
        
        print("\nWireless Controller Tools:")
        for tool in wireless_tools:
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
