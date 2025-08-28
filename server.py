#!/usr/bin/env python3
"""
Unitree Go2 MCP Server using WebRTC
A simple MCP server that enables natural language control of the Unitree Go2 robot
using WebRTC connections instead of ROS.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Import the WebRTC driver
try:
    from go2_webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
except ImportError:
    print("Warning: go2_webrtc_driver not found. Please install it first.")
    Go2WebRTCConnection = None
    WebRTCConnectionMethod = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Go2Robot:
    """Represents a Go2 robot connection"""
    connection: Optional[Go2WebRTCConnection] = None
    is_connected: bool = False
    serial_number: Optional[str] = None
    ip_address: Optional[str] = None

class Go2WebRTCMCPServer:
    """MCP Server for controlling Unitree Go2 robot via WebRTC"""
    
    def __init__(self):
        self.server = Server("unitree-go2-webrtc-mcp-server")
        self.robot = Go2Robot()
        self.setup_tools()
    
    def setup_tools(self):
        """Setup all available tools"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List all available tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="connect_robot",
                        description="Connect to a Go2 robot using WebRTC",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "connection_method": {
                                    "type": "string",
                                    "enum": ["local_ap", "local_sta", "remote"],
                                    "description": "Connection method: local_ap (AP mode), local_sta (same network), remote (TURN server)"
                                },
                                "ip_address": {
                                    "type": "string",
                                    "description": "IP address of the robot (required for local_sta mode)"
                                },
                                "serial_number": {
                                    "type": "string",
                                    "description": "Serial number of the robot (required for remote mode)"
                                },
                                "username": {
                                    "type": "string",
                                    "description": "Unitree account username (required for remote mode)"
                                },
                                "password": {
                                    "type": "string",
                                    "description": "Unitree account password (required for remote mode)"
                                }
                            },
                            "required": ["connection_method"]
                        }
                    ),
                    Tool(
                        name="disconnect_robot",
                        description="Disconnect from the Go2 robot",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    ),
                    Tool(
                        name="move_robot",
                        description="Move the Go2 robot with specified parameters",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "action": {
                                    "type": "string",
                                    "enum": ["forward", "backward", "left", "right", "stop"],
                                    "description": "Movement action to perform"
                                },
                                "duration": {
                                    "type": "number",
                                    "description": "Duration of movement in seconds (optional)"
                                },
                                "speed": {
                                    "type": "number",
                                    "description": "Movement speed (0.0 to 1.0, optional)"
                                }
                            },
                            "required": ["action"]
                        }
                    ),
                    Tool(
                        name="robot_status",
                        description="Get the current status of the Go2 robot",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    ),
                    Tool(
                        name="execute_command",
                        description="Execute a natural language command for the Go2 robot",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "command": {
                                    "type": "string",
                                    "description": "Natural language command to execute"
                                }
                            },
                            "required": ["command"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "connect_robot":
                    return await self.connect_robot(arguments)
                elif name == "disconnect_robot":
                    return await self.disconnect_robot(arguments)
                elif name == "move_robot":
                    return await self.move_robot(arguments)
                elif name == "robot_status":
                    return await self.robot_status(arguments)
                elif name == "execute_command":
                    return await self.execute_command(arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")]
                    )
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )
    
    async def connect_robot(self, args: Dict[str, Any]) -> CallToolResult:
        """Connect to a Go2 robot"""
        if not Go2WebRTCConnection:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: WebRTC driver not available")]
            )
        
        try:
            connection_method = args.get("connection_method")
            
            if connection_method == "local_ap":
                self.robot.connection = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
            elif connection_method == "local_sta":
                ip = args.get("ip_address")
                serial = args.get("serial_number")
                if ip:
                    self.robot.connection = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, ip=ip)
                elif serial:
                    self.robot.connection = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, serialNumber=serial)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text="Error: IP address or serial number required for local_sta mode")]
                    )
            elif connection_method == "remote":
                serial = args.get("serial_number")
                username = args.get("username")
                password = args.get("password")
                if not all([serial, username, password]):
                    return CallToolResult(
                        content=[TextContent(type="text", text="Error: serial_number, username, and password required for remote mode")]
                    )
                self.robot.connection = Go2WebRTCConnection(
                    WebRTCConnectionMethod.Remote,
                    serialNumber=serial,
                    username=username,
                    password=password
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: Invalid connection method")]
                )
            
            # Attempt to connect
            await self.robot.connection.connect()
            self.robot.is_connected = True
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Successfully connected to Go2 robot using {connection_method} mode")]
            )
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Connection failed: {str(e)}")]
            )
    
    async def disconnect_robot(self, args: Dict[str, Any]) -> CallToolResult:
        """Disconnect from the Go2 robot"""
        try:
            if self.robot.connection and self.robot.is_connected:
                await self.robot.connection.disconnect()
                self.robot.connection = None
                self.robot.is_connected = False
                return CallToolResult(
                    content=[TextContent(type="text", text="Successfully disconnected from Go2 robot")]
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text="No active connection to disconnect")]
                )
        except Exception as e:
            logger.error(f"Disconnection error: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Disconnection failed: {str(e)}")]
            )
    
    async def move_robot(self, args: Dict[str, Any]) -> CallToolResult:
        """Move the Go2 robot"""
        if not self.robot.is_connected:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Robot not connected. Please connect first.")]
            )
        
        try:
            action = args.get("action")
            duration = args.get("duration", 1.0)
            speed = args.get("speed", 0.5)
            
            # Map actions to robot commands
            if action == "forward":
                await self.robot.connection.move_forward(speed, duration)
            elif action == "backward":
                await self.robot.connection.move_backward(speed, duration)
            elif action == "left":
                await self.robot.connection.turn_left(speed, duration)
            elif action == "right":
                await self.robot.connection.turn_right(speed, duration)
            elif action == "stop":
                await self.robot.connection.stop()
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: Unknown action '{action}'")]
                )
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Successfully executed {action} action")]
            )
            
        except Exception as e:
            logger.error(f"Movement error: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Movement failed: {str(e)}")]
            )
    
    async def robot_status(self, args: Dict[str, Any]) -> CallToolResult:
        """Get robot status"""
        status = {
            "connected": self.robot.is_connected,
            "connection_type": "WebRTC",
            "robot_info": "Unitree Go2"
        }
        
        if self.robot.is_connected and self.robot.connection:
            try:
                # Get basic robot information
                status["battery_level"] = "Available"  # Would need actual API call
                status["connection_status"] = "Active"
            except Exception as e:
                status["connection_status"] = f"Error: {str(e)}"
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(status, indent=2))]
        )
    
    async def execute_command(self, args: Dict[str, Any]) -> CallToolResult:
        """Execute a natural language command"""
        if not self.robot.is_connected:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Robot not connected. Please connect first.")]
            )
        
        command = args.get("command", "").lower()
        
        try:
            # Parse natural language commands
            if any(word in command for word in ["forward", "ahead", "straight"]):
                await self.robot.connection.move_forward(0.5, 2.0)
                return CallToolResult(
                    content=[TextContent(type="text", text="Moving the robot forward for 2 seconds")]
                )
            elif any(word in command for word in ["backward", "back", "reverse"]):
                await self.robot.connection.move_backward(0.5, 2.0)
                return CallToolResult(
                    content=[TextContent(type="text", text="Moving the robot backward for 2 seconds")]
                )
            elif any(word in command for word in ["left", "turn left"]):
                await self.robot.connection.turn_left(0.5, 2.0)
                return CallToolResult(
                    content=[TextContent(type="text", text="Turning the robot left for 2 seconds")]
                )
            elif any(word in command for word in ["right", "turn right"]):
                await self.robot.connection.turn_right(0.5, 2.0)
                return CallToolResult(
                    content=[TextContent(type="text", text="Turning the robot right for 2 seconds")]
                )
            elif any(word in command for word in ["stop", "halt", "pause"]):
                await self.robot.connection.stop()
                return CallToolResult(
                    content=[TextContent(type="text", text="Stopping the robot")]
                )
            elif any(word in command for word in ["dance", "spin", "rotate"]):
                # Simple dance sequence
                await self.robot.connection.turn_left(0.8, 1.0)
                await asyncio.sleep(1.0)
                await self.robot.connection.turn_right(0.8, 1.0)
                await asyncio.sleep(1.0)
                await self.robot.connection.move_forward(0.3, 1.0)
                return CallToolResult(
                    content=[TextContent(type="text", text="Executed a simple dance sequence")]
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Command not understood: '{command}'. Try using words like 'forward', 'backward', 'left', 'right', 'stop', or 'dance'.")]
                )
                
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Command execution failed: {str(e)}")]
            )

async def main():
    """Main function to run the MCP server"""
    # Create and run the server
    server_instance = Go2WebRTCMCPServer()
    
    # Run the server using stdio
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="unitree-go2-webrtc-mcp-server",
                server_version="1.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
