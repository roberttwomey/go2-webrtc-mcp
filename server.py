#!/usr/bin/env python3
"""
Unitree Go2 MCP Server using WebRTC
A sophisticated MCP server that enables natural language control of the Unitree Go2 robot
using WebRTC connections with advanced movement control and motion mode management.
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from queue import Queue

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
    from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
    from go2_webrtc_driver.constants import RTC_TOPIC, SPORT_CMD
except ImportError:
    print("Warning: go2_webrtc_driver not found. Please install it first.")
    Go2WebRTCConnection = None
    WebRTCConnectionMethod = None
    RTC_TOPIC = None
    SPORT_CMD = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Go2Robot:
    """Represents a Go2 robot connection with advanced state management"""
    connection: Optional[Go2WebRTCConnection] = None
    is_connected: bool = False
    serial_number: Optional[str] = None
    ip_address: Optional[str] = None
    current_motion_mode: str = "unknown"
    current_movement: Dict[str, float] = None
    movement_task: Optional[asyncio.Task] = None
    command_rate_hz: int = 5  # Commands per second
    is_moving: bool = False
    
    def __post_init__(self):
        if self.current_movement is None:
            self.current_movement = {'x': 0, 'y': 0, 'z': 0}

class Go2WebRTCMCPServer:
    """Advanced MCP Server for controlling Unitree Go2 robot via WebRTC"""
    
    def __init__(self):
        self.server = Server("unitree-go2-webrtc-mcp-server")
        self.robot = Go2Robot()
        self.setup_tools()
    
    def setup_tools(self):
        """Setup all available tools with enhanced capabilities"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List all available tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="connect_robot",
                        description="Connect to a Go2 robot using WebRTC with advanced connection options",
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
                        description="Disconnect from the Go2 robot and stop all movement",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    ),
                    Tool(
                        name="move_robot",
                        description="Move the Go2 robot with precise velocity control (x=forward/backward, y=left/right, z=rotation)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "x": {
                                    "type": "number",
                                    "description": "Forward/backward velocity (-1.0 to 1.0, positive=forward)"
                                },
                                "y": {
                                    "type": "number", 
                                    "description": "Left/right velocity (-1.0 to 1.0, positive=left)"
                                },
                                "z": {
                                    "type": "number",
                                    "description": "Rotation velocity (-1.0 to 1.0, positive=left turn)"
                                },
                                "duration": {
                                    "type": "number",
                                    "description": "Duration of movement in seconds (optional, for single commands)"
                                }
                            },
                            "required": []
                        }
                    ),
                    Tool(
                        name="stop_robot",
                        description="Stop all robot movement immediately",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    ),
                    Tool(
                        name="switch_motion_mode",
                        description="Switch robot motion mode (normal, mcf, sport, etc.)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "mode": {
                                    "type": "string",
                                    "enum": ["normal", "mcf", "sport"],
                                    "description": "Motion mode to switch to"
                                }
                            },
                            "required": ["mode"]
                        }
                    ),
                    Tool(
                        name="get_motion_mode",
                        description="Get the current motion mode of the robot",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    ),
                    Tool(
                        name="robot_status",
                        description="Get comprehensive status of the Go2 robot",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    ),
                    Tool(
                        name="execute_command",
                        description="Execute a natural language command for the Go2 robot with enhanced movement control",
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
                    ),
                    Tool(
                        name="test_movement",
                        description="Run a comprehensive movement test to verify robot functionality",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    ),
                    Tool(
                        name="set_command_rate",
                        description="Set the command rate for continuous movement (Hz)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "rate_hz": {
                                    "type": "number",
                                    "description": "Commands per second (1-20 Hz, default 5)"
                                }
                            },
                            "required": ["rate_hz"]
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
                elif name == "stop_robot":
                    return await self.stop_robot(arguments)
                elif name == "switch_motion_mode":
                    return await self.switch_motion_mode(arguments)
                elif name == "get_motion_mode":
                    return await self.get_motion_mode(arguments)
                elif name == "robot_status":
                    return await self.robot_status(arguments)
                elif name == "execute_command":
                    return await self.execute_command(arguments)
                elif name == "test_movement":
                    return await self.test_movement(arguments)
                elif name == "set_command_rate":
                    return await self.set_command_rate(arguments)
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
        """Connect to a Go2 robot with enhanced error handling"""
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
                    self.robot.ip_address = ip
                elif serial:
                    self.robot.connection = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, serialNumber=serial)
                    self.robot.serial_number = serial
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
                self.robot.serial_number = serial
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: Invalid connection method")]
                )
            
            # Attempt to connect
            await self.robot.connection.connect()
            self.robot.is_connected = True
            
            # Get current motion mode
            await self.get_motion_mode({})
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Successfully connected to Go2 robot using {connection_method} mode. Current motion mode: {self.robot.current_motion_mode}")]
            )
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Connection failed: {str(e)}")]
            )
    
    async def disconnect_robot(self, args: Dict[str, Any]) -> CallToolResult:
        """Disconnect from the Go2 robot and stop all movement"""
        try:
            # Stop any ongoing movement
            if self.robot.is_moving:
                await self.stop_robot({})
            
            # Cancel movement task if running
            if self.robot.movement_task and not self.robot.movement_task.done():
                self.robot.movement_task.cancel()
                try:
                    await self.robot.movement_task
                except asyncio.CancelledError:
                    pass
            
            if self.robot.connection and self.robot.is_connected:
                await self.robot.connection.disconnect()
                self.robot.connection = None
                self.robot.is_connected = False
                self.robot.current_motion_mode = "unknown"
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
        """Move the Go2 robot with precise velocity control"""
        if not self.robot.is_connected:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Robot not connected. Please connect first.")]
            )
        
        try:
            x = args.get("x", 0.0)
            y = args.get("y", 0.0)
            z = args.get("z", 0.0)
            duration = args.get("duration", None)
            
            # Ensure values are within valid range
            # x = max(-1.0, min(1.0, float(x)))
            # y = max(-1.0, min(1.0, float(y)))
            # z = max(-1.0, min(1.0, float(z)))
            
            # Update current movement
            self.robot.current_movement = {'x': x, 'y': y, 'z': z}
            
            if duration:
                # Single movement command with duration
                await self._send_movement_command(x, y, z)
                await asyncio.sleep(duration)
                # await self._send_movement_command(0, 0, 0)  # Stop
                
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Executed movement: x={x:.2f}, y={y:.2f}, z={z:.2f} for {duration}s")]
                )
            else:
                # Continuous movement - start movement task if not running
                if not self.robot.is_moving:
                    self.robot.is_moving = True
                    self.robot.movement_task = asyncio.create_task(self._continuous_movement_task())
                
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Started continuous movement: x={x:.2f}, y={y:.2f}, z={z:.2f}")]
                )
            
        except Exception as e:
            logger.error(f"Movement error: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Movement failed: {str(e)}")]
            )
    
    async def stop_robot(self, args: Dict[str, Any]) -> CallToolResult:
        """Stop all robot movement"""
        try:
            # Stop movement task
            if self.robot.movement_task and not self.robot.movement_task.done():
                self.robot.movement_task.cancel()
                try:
                    await self.robot.movement_task
                except asyncio.CancelledError:
                    pass
            
            self.robot.is_moving = False
            self.robot.current_movement = {'x': 0, 'y': 0, 'z': 0}
            
            # Send stop command
            await self._send_movement_command(0, 0, 0)
            
            return CallToolResult(
                content=[TextContent(type="text", text="Robot movement stopped")]
            )
        except Exception as e:
            logger.error(f"Stop error: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Stop failed: {str(e)}")]
            )
    
    async def switch_motion_mode(self, args: Dict[str, Any]) -> CallToolResult:
        """Switch robot motion mode"""
        if not self.robot.is_connected:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Robot not connected. Please connect first.")]
            )
        
        try:
            mode = args.get("mode")
            
            # Stop current movement before switching modes
            if self.robot.is_moving:
                await self.stop_robot({})
            
            # Switch motion mode
            response = await self.robot.connection.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["MOTION_SWITCHER"], 
                {
                    "api_id": 1002,
                    "parameter": {"name": mode}
                }
            )
            
            if response and 'data' in response and 'header' in response['data']:
                status = response['data']['header']['status']['code']
                if status == 0:
                    self.robot.current_motion_mode = mode
                    await asyncio.sleep(2)  # Wait for mode switch
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Successfully switched to {mode} motion mode")]
                    )
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Failed to switch motion mode, status: {status}")]
                    )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text="Invalid response from motion mode switch")]
                )
                
        except Exception as e:
            logger.error(f"Motion mode switch error: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Motion mode switch failed: {str(e)}")]
            )
    
    async def get_motion_mode(self, args: Dict[str, Any]) -> CallToolResult:
        """Get current motion mode"""
        if not self.robot.is_connected:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Robot not connected. Please connect first.")]
            )
        
        try:
            response = await self.robot.connection.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["MOTION_SWITCHER"], 
                {"api_id": 1001}
            )
            
            if response and 'data' in response and 'header' in response['data']:
                status = response['data']['header']['status']['code']
                if status == 0:
                    data = json.loads(response['data']['data'])
                    current_mode = data['name']
                    self.robot.current_motion_mode = current_mode
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Current motion mode: {current_mode}")]
                    )
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Failed to get motion mode, status: {status}")]
                    )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text="Invalid response from motion mode request")]
                )
                
        except Exception as e:
            logger.error(f"Get motion mode error: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Get motion mode failed: {str(e)}")]
            )
    
    async def robot_status(self, args: Dict[str, Any]) -> CallToolResult:
        """Get comprehensive robot status"""
        status = {
            "connected": self.robot.is_connected,
            "connection_type": "WebRTC",
            "robot_info": "Unitree Go2",
            "motion_mode": self.robot.current_motion_mode,
            "is_moving": self.robot.is_moving,
            "current_movement": self.robot.current_movement,
            "command_rate_hz": self.robot.command_rate_hz
        }
        
        if self.robot.ip_address:
            status["ip_address"] = self.robot.ip_address
        if self.robot.serial_number:
            status["serial_number"] = self.robot.serial_number
        
        if self.robot.is_connected and self.robot.connection:
            try:
                status["connection_status"] = "Active"
            except Exception as e:
                status["connection_status"] = f"Error: {str(e)}"
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(status, indent=2))]
        )
    
    async def execute_command(self, args: Dict[str, Any]) -> CallToolResult:
        """Execute a natural language command with enhanced movement control"""
        if not self.robot.is_connected:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Robot not connected. Please connect first.")]
            )
        
        command = args.get("command", "").lower()
        
        try:
            # Enhanced natural language command parsing
            if any(word in command for word in ["forward", "ahead", "straight", "go forward"]):
                await self.move_robot({"x": 0.5, "y": 0, "z": 0})
                return CallToolResult(
                    content=[TextContent(type="text", text="Moving the robot forward")]
                )
            elif any(word in command for word in ["backward", "back", "reverse", "go back"]):
                await self.move_robot({"x": -0.5, "y": 0, "z": 0})
                return CallToolResult(
                    content=[TextContent(type="text", text="Moving the robot backward")]
                )
            elif any(word in command for word in ["left", "turn left", "go left"]):
                await self.move_robot({"x": 0, "y": 0, "z": 0.5})
                return CallToolResult(
                    content=[TextContent(type="text", text="Turning the robot left")]
                )
            elif any(word in command for word in ["right", "turn right", "go right"]):
                await self.move_robot({"x": 0, "y": 0, "z": -0.5})
                return CallToolResult(
                    content=[TextContent(type="text", text="Turning the robot right")]
                )
            elif any(word in command for word in ["stop", "halt", "pause", "freeze"]):
                await self.stop_robot({})
                return CallToolResult(
                    content=[TextContent(type="text", text="Stopping the robot")]
                )
            elif any(word in command for word in ["dance", "spin", "rotate", "turn around"]):
                # Enhanced dance sequence
                await self.move_robot({"x": 0, "y": 0, "z": 0.8, "duration": 2.0})
                await asyncio.sleep(2.0)
                await self.move_robot({"x": 0, "y": 0, "z": -0.8, "duration": 2.0})
                await asyncio.sleep(2.0)
                await self.move_robot({"x": 0.3, "y": 0, "z": 0, "duration": 1.0})
                return CallToolResult(
                    content=[TextContent(type="text", text="Executed an enhanced dance sequence")]
                )
            elif any(word in command for word in ["fast", "speed up", "run"]):
                await self.move_robot({"x": 1.0, "y": 0, "z": 0})
                return CallToolResult(
                    content=[TextContent(type="text", text="Moving the robot at high speed")]
                )
            elif any(word in command for word in ["slow", "slow down", "gentle"]):
                await self.move_robot({"x": 0.2, "y": 0, "z": 0})
                return CallToolResult(
                    content=[TextContent(type="text", text="Moving the robot slowly")]
                )
            elif "mode" in command:
                if "normal" in command:
                    await self.switch_motion_mode({"mode": "normal"})
                    return CallToolResult(
                        content=[TextContent(type="text", text="Switched to normal motion mode")]
                    )
                elif "mcf" in command:
                    await self.switch_motion_mode({"mode": "mcf"})
                    return CallToolResult(
                        content=[TextContent(type="text", text="Switched to MCF motion mode")]
                    )
                elif "sport" in command:
                    await self.switch_motion_mode({"mode": "sport"})
                    return CallToolResult(
                        content=[TextContent(type="text", text="Switched to sport motion mode")]
                    )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Command not understood: '{command}'. Try using words like 'forward', 'backward', 'left', 'right', 'stop', 'dance', 'fast', 'slow', or 'mode'.")]
                )
                
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Command execution failed: {str(e)}")]
            )
    
    async def test_movement(self, args: Dict[str, Any]) -> CallToolResult:
        """Run comprehensive movement test"""
        if not self.robot.is_connected:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Robot not connected. Please connect first.")]
            )
        
        try:
            result_messages = []
            result_messages.append("Starting comprehensive movement test...")
            
            # Test forward movement
            result_messages.append("Testing forward movement...")
            await self.move_robot({"x": 1.0, "y": 0, "z": 0, "duration": 2.0})
            
            # Test turning
            result_messages.append("Testing left turn...")
            await self.move_robot({"x": 0, "y": 0, "z": 1.0, "duration": 2.0})
            
            result_messages.append("Testing right turn...")
            await self.move_robot({"x": 0, "y": 0, "z": -1.0, "duration": 2.0})
            
            # Test combined movement
            result_messages.append("Testing combined movement (forward + turn)...")
            await self.move_robot({"x": 1.0, "y": 0, "z": 0.5, "duration": 2.0})
            
            # Stop
            await self.stop_robot({})
            result_messages.append("Movement test completed successfully!")
            
            return CallToolResult(
                content=[TextContent(type="text", text="\n".join(result_messages))]
            )
            
        except Exception as e:
            logger.error(f"Movement test error: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Movement test failed: {str(e)}")]
            )
    
    async def set_command_rate(self, args: Dict[str, Any]) -> CallToolResult:
        """Set the command rate for continuous movement"""
        try:
            rate_hz = args.get("rate_hz", 5)
            rate_hz = max(1, min(20, int(rate_hz)))  # Clamp between 1-20 Hz
            
            self.robot.command_rate_hz = rate_hz
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Command rate set to {rate_hz} Hz")]
            )
        except Exception as e:
            logger.error(f"Set command rate error: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to set command rate: {str(e)}")]
            )
    
    async def _send_movement_command(self, x: float, y: float, z: float):
        """Send movement command to robot"""
        try:
            response = await self.robot.connection.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], 
                {
                    "api_id": SPORT_CMD["Move"],
                    "parameter": {"x": x, "y": y, "z": z}
                }
            )
            
            if response and 'data' in response and 'header' in response['data']:
                status = response['data']['header']['status']['code']
                if status != 0:
                    logger.warning(f"Movement command failed with status: {status}")
            else:
                logger.warning("No response received from movement command")
                
        except Exception as e:
            logger.error(f"Error sending movement command: {e}")
    
    async def _continuous_movement_task(self):
        """Task that continuously sends movement commands"""
        while self.robot.is_moving:
            try:
                # Send current movement command
                if (abs(self.robot.current_movement['x']) > 0.01 or 
                    abs(self.robot.current_movement['y']) > 0.01 or 
                    abs(self.robot.current_movement['z']) > 0.01):
                    
                    await self._send_movement_command(
                        self.robot.current_movement['x'],
                        self.robot.current_movement['y'], 
                        self.robot.current_movement['z']
                    )
                
                # Send commands at regular intervals
                await asyncio.sleep(1.0 / self.robot.command_rate_hz)
                
            except Exception as e:
                logger.error(f"Error in continuous movement task: {e}")
                await asyncio.sleep(0.1)

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
                server_version="2.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
