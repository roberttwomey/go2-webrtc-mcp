#!/usr/bin/env python3
"""
Unitree Go2 WebRTC MCP Server using FastMCP
A simple MCP server that enables natural language control of the Unitree Go2 robot
using WebRTC connections instead of ROS.
"""

import asyncio
from typing import Optional, Literal, Any, Dict
from dataclasses import dataclass
import json

from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server

# Import the WebRTC driver
try:
    from go2_webrtc_connect.go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
    from go2_webrtc_connect.go2_webrtc_driver.constants import RTC_TOPIC, SPORT_CMD
    DRIVER_AVAILABLE = True
except ImportError:
    print("Warning: go2_webrtc_connect driver not found. Please install it first.")
    print("Install with: git clone --recurse-submodules https://github.com/legion1581/go2_webrtc_connect.git")
    print("Then: cd go2_webrtc_connect && pip install -e .")
    # Fallback imports for development
    Go2WebRTCConnection = None
    WebRTCConnectionMethod = None
    RTC_TOPIC = {
        "MOTION_SWITCHER": "rt/api/motion_switcher"
    }
    SPORT_CMD = {
        "Damp": 1001,
        "BalanceStand": 1002,
        "StopMove": 1003,
        "StandUp": 1004,
        "StandDown": 1005,
        "RecoveryStand": 1006,
        "Euler": 1007,
        "Move": 1008,
        "Sit": 1009,
        "RiseSit": 1010,
        "SwitchGait": 1011,
        "Trigger": 1012,
        "BodyHeight": 1013,
        "FootRaiseHeight": 1014,
        "SpeedLevel": 1015,
        "Hello": 1016,
        "Stretch": 1017,
        "TrajectoryFollow": 1018,
        "ContinuousGait": 1019,
        "Content": 1020,
        "Wallow": 1021,
        "Dance1": 1022,
        "Dance2": 1023,
        "GetBodyHeight": 1024,
        "GetFootRaiseHeight": 1025,
        "GetSpeedLevel": 1026,
        "SwitchJoystick": 1027,
        "Pose": 1028,
        "Scrape": 1029,
        "FrontFlip": 1030,
        "LeftFlip": 1042,
        "RightFlip": 1043,
        "BackFlip": 1044,
        "FrontJump": 1031,
        "FrontPounce": 1032,
        "WiggleHips": 1033,
        "GetState": 1034,
        "EconomicGait": 1035,
        "LeadFollow": 1045,
        "FingerHeart": 1036,
        "Bound": 1304,
        "MoonWalk": 1305,
        "OnesidedStep": 1303,
        "CrossStep": 1302,
        "Handstand": 1301,
        "StandOut": 1039,
        "FreeWalk": 1045,
        "Standup": 1050,
        "CrossWalk": 1051
    }
    DRIVER_AVAILABLE = False

# ===== App state =====
@dataclass
class Go2State:
    conn: Optional[Go2WebRTCConnection] = None
    connected: bool = False

state = Go2State()
mcp = FastMCP("go2-webrtc")

# ===== Helper Functions =====

async def move_robot(x=0, y=0, z=0):
    """Move the robot with specified velocities"""
    try:
        # Ensure all values are Python native types
        x, y, z = float(x), float(y), float(z)
        print(f"Sending movement command: x={x:.3f}, y={y:.3f}, z={z:.3f}")
        
        response = await state.conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"], 
            {
                "api_id": SPORT_CMD["Move"],
                "parameter": {"x": x, "y": y, "z": z}
            }
        )
        
        # Check if the command was successful
        if response and 'data' in response and 'header' in response['data']:
            status = response['data']['header']['status']['code']
            if status == 0:
                print(f"Movement command successful: x={x:.3f}, y={y:.3f}, z={z:.3f}")
                return {"ok": True, "response": response}
            else:
                print(f"Movement command failed with status: {status}")
                print(f"Full response: {response}")
                # Check if we need to be in a different motion mode
                if status == -1:
                    print("Status -1: Command rejected. This might indicate wrong motion mode or invalid parameters.")
                return {"ok": False, "error": f"Status code: {status}", "response": response}
        else:
            print("No response received from movement command")
            print(f"Response: {response}")
            return {"ok": False, "error": "No response received", "response": response}
            
    except Exception as e:
        print(f"Error moving robot: {e}")
        import traceback
        traceback.print_exc()
        return {"ok": False, "error": str(e)}

async def send_sport_command(api_id, parameter=None):
    """Send a SPORT_MOD command with specified API ID and optional parameter"""
    try:
        payload = {"api_id": api_id}
        if parameter:
            payload["parameter"] = parameter
            
        print(f"Sending SPORT command: {payload}")
        
        response = await state.conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["SPORT_MOD"], 
            payload
        )
        
        # Check if the command was successful
        if response and 'data' in response and 'header' in response['data']:
            status = response['data']['header']['status']['code']
            if status == 0:
                print(f"SPORT command successful: {api_id}")
                return {"ok": True, "response": response}
            else:
                print(f"SPORT command failed with status: {status}")
                return {"ok": False, "error": f"Status code: {status}", "response": response}
        else:
            print("No response received from SPORT command")
            return {"ok": False, "error": "No response received", "response": response}
            
    except Exception as e:
        print(f"Error sending SPORT command: {e}")
        import traceback
        traceback.print_exc()
        return {"ok": False, "error": str(e)}

async def switch_to_mcf_mode() -> bool:
    """
    Ensure the robot is in MCF (Motion Control Framework) mode before executing movement commands.
    Returns True if successfully in MCF mode, False otherwise.
    """
    if not state.connected or not state.conn:
        return False
    
    try:
        print("Checking current motion mode...")
        # Get current motion mode
        response = await self.conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["MOTION_SWITCHER"], 
            {"api_id": 1001}
        )
        
        print(f"Motion mode response: {response}")
            
        if response and 'data' in response and 'header' in response['data']:
            status = response['data']['header']['status']['code']
            if status == 0:
                data = json.loads(response['data']['data'])
                current_mode = data['name']
                print(f"Current motion mode: {current_mode}")
                
                # Switch to MCF mode if not already
                if current_mode != "mcf":
                    print("Switching to MCF motion mode...")
                    switch_response = await self.conn.datachannel.pub_sub.publish_request_new(
                        RTC_TOPIC["MOTION_SWITCHER"], 
                        {
                            "api_id": 1002,
                            "parameter": {"name": "mcf"}
                        }
                    )
                    print(f"Switch response: {switch_response}")
                    await asyncio.sleep(5)  # Wait for mode switch
                    print("Switched to MCF mode")
                else:
                    print("Already in MCF mode")
            else:
                print(f"Failed to get motion mode, status: {status}")
        else:
            print("Invalid response format from motion mode request")

    except Exception as e:
        print(f"Error ensuring MCF mode: {e}")
        return False

def _method_from_str(name: str) -> WebRTCConnectionMethod:
    """Convert string method to WebRTCConnectionMethod enum"""
    if not WebRTCConnectionMethod:
        raise RuntimeError("WebRTC driver not available")
    
    n = name.lower()
    if n in ("localap", "ap"): 
        return WebRTCConnectionMethod.LocalAP
    if n in ("localsta", "sta", "sta-l"): 
        return WebRTCConnectionMethod.LocalSTA
    if n in ("remote", "sta-t"): 
        return WebRTCConnectionMethod.Remote
    raise ValueError(f"unknown method: {name}")

async def _ensure_disconnected():
    """Safely disconnect and cleanup connection"""
    if state.conn:
        try:
            # Some builds expose .close() / .stop()
            close = getattr(state.conn, "close", None)
            if callable(close):
                result = close()
                if asyncio.iscoroutine(result):
                    await result
            # Alternative disconnect method
            disconnect = getattr(state.conn, "disconnect", None)
            if callable(disconnect):
                result = disconnect()
                if asyncio.iscoroutine(result):
                    await result
        except Exception:
            pass
    state.conn = None
    state.connected = False

def _conn() -> Go2WebRTCConnection:
    """Get the current connection, raising error if not connected"""
    if not state.connected or not state.conn:
        raise RuntimeError("Not connected. Call connect() first.")
    return state.conn

def _topic(key: str, fallback: str) -> str:
    """Get topic from RTC_TOPIC mapping or use fallback"""
    # Allow using either symbolic key (e.g., "WALK") or a raw path already
    return RTC_TOPIC.get(key, key) if "/" in key else RTC_TOPIC.get(key, fallback)

async def _send_async(topic: str, payload: dict) -> None:
    """Send payload to topic using available driver method (async version)"""
    if not Go2WebRTCConnection:
        raise RuntimeError("WebRTC driver not available. Please install go2_webrtc_connect first.")
    
    conn = _conn()
    
    # The correct method is: conn.datachannel.pub_sub.publish_request_new()
    try:
        print(f"Attempting to send to topic: {topic}")
        print(f"Payload: {payload}")
        print(f"Connection object: {type(conn)}")
        print(f"Connection attributes: {[attr for attr in dir(conn) if not attr.startswith('_')]}")
        
        if hasattr(conn, 'datachannel') and hasattr(conn.datachannel, 'pub_sub'):
            print("Found datachannel.pub_sub, sending command...")
            # Use the correct method from the driver
            result = await conn.datachannel.pub_sub.publish_request_new(topic, payload)
            print(f"Command sent successfully, result: {result}")
            return result
        else:
            print("datachannel.pub_sub not found")
            print(f"datachannel attributes: {[attr for attr in dir(conn.datachannel) if not attr.startswith('_')] if hasattr(conn, 'datachannel') else 'No datachannel'}")
            raise RuntimeError("Driver connection doesn't have datachannel.pub_sub")
            
    except Exception as e:
        # Fallback: try different possible method names
        possible_methods = [
            'datachannel.pub_sub.publish_request_new',
            'send_api_request',
            'publish',
            'send',
            'send_message',
            'send_topic',
            'api_request',
            'request'
        ]
        
        for method_name in possible_methods:
            if hasattr(conn, method_name):
                method = getattr(conn, method_name)
                if callable(method):
                    try:
                        result = method(topic, payload)
                        if asyncio.iscoroutine(result):
                            await result
                        return
                    except Exception:
                        try:
                            result = method(payload, topic)
                            if asyncio.iscoroutine(result):
                                await result
                            return
                        except:
                            continue
        
        # If we get here, no method worked
        available_methods = [attr for attr in dir(conn) if not attr.startswith('_') and callable(getattr(conn, attr))]
        
        # Provide helpful error message
        error_msg = f"Driver has no compatible send/publish method for topic '{topic}'.\n"
        error_msg += f"Available methods: {available_methods}\n"
        error_msg += f"Expected method: datachannel.pub_sub.publish_request_new\n"
        error_msg += f"Error: {str(e)}\n"
        error_msg += "\nTo fix this:\n"
        error_msg += "1. Make sure go2_webrtc_connect is properly installed\n"
        error_msg += "2. Check the driver documentation for the correct method names\n"
        error_msg += "3. Update the server code to use the correct method names\n"
        
        raise RuntimeError(error_msg)

# ===== Wireless Controller Functions (adapted from ROS2 to WebRTC) =====

async def _wireless_controller_publish(lx: float, ly: float, rx: float, ry: float, keys: int, duration: float = 0) -> dict:
    """
    Publish wireless controller message via WebRTC.
    Adapted from ROS2 WirelessController to WebRTC commands.
    
    Message fields:
      - float32 lx : left stick x axis (-1 ~ 1) -> robot move left and right
      - float32 ly : left stick y axis (-1 ~ 1) -> robot move forward and backward
      - float32 rx : right stick x axis (-1 ~ 1) -> robot rotate left and right
      - float32 ry : right stick y axis (-1 ~ 1) -> robot rotate up and down
      - uint16 keys : button state
    """
    try:
        # Ensure MCF mode is active
        await switch_to_mcf_mode()
        
        # Map wireless controller to robot movement
        # For WebRTC, we'll use the SPORT_MOD API with the controller values
        
        # Convert controller values to robot movement
        # lx: left/right movement, ly: forward/backward, rx: yaw rotation
        result = await move_robot(
            x=ly,  # forward/backward from left stick Y
            y=lx,  # left/right from left stick X
            z=rx   # rotation from right stick X
        )
        
        # If duration specified, wait for the duration
        if duration > 0:
            await asyncio.sleep(duration)
        
        return {"ok": result.get("ok", False), "topic": "SPORT_MOD", "keys": keys, "response": result.get("response")}
        
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def _customised_movements(keys: int, duration: float = 0.5) -> dict:
    """Execute custom movements based on key codes using proper SPORT_CMD values"""
    try:
        # Ensure MCF mode is active
        await switch_to_mcf_mode()
        
        sport_topic = _topic("SPORT_MOD", "rt/api/sport_mod")
        
        # Map key codes to specific SPORT_CMD movements
        if keys == 0:  # Stop
            result = await send_sport_command(SPORT_CMD["StopMove"])
            return {"ok": result.get("ok", False), "action": "stop", "keys": keys, "response": result.get("response")}
        elif keys == 257:  # Jump forward - use FrontJump
            result = await send_sport_command(SPORT_CMD["FrontJump"])
            return {"ok": result.get("ok", False), "action": "jump_forward", "keys": keys, "response": result.get("response")}
        elif keys == 258:  # Greet - use Hello
            result = await send_sport_command(SPORT_CMD["Hello"])
            return {"ok": result.get("ok", False), "action": "greet", "keys": keys, "response": result.get("response")}
        elif keys == 272:  # Stretch
            result = await send_sport_command(SPORT_CMD["Stretch"])
            return {"ok": result.get("ok", False), "action": "stretch", "keys": keys, "response": result.get("response")}
        elif keys == 513:  # Sit down
            result = await send_sport_command(SPORT_CMD["Sit"])
            return {"ok": result.get("ok", False), "action": "sit_down", "keys": keys, "response": result.get("response")}
        elif keys == 514:  # Dance - use Dance1
            result = await send_sport_command(SPORT_CMD["Dance1"])
            return {"ok": result.get("ok", False), "action": "dance", "keys": keys, "response": result.get("response")}
        elif keys == 528:  # Shake hands - use Hello
            result = await send_sport_command(SPORT_CMD["Hello"])
            return {"ok": result.get("ok", False), "action": "shake_hands", "keys": keys, "response": result.get("response")}
        elif keys == 1025:  # Pounce - use FrontPounce
            result = await send_sport_command(SPORT_CMD["FrontPounce"])
            return {"ok": result.get("ok", False), "action": "pounce", "keys": keys, "response": result.get("response")}
        elif keys == 1056:  # Stand up from fall - use RecoveryStand
            result = await send_sport_command(SPORT_CMD["RecoveryStand"])
            return {"ok": result.get("ok", False), "action": "stand_up_from_fall", "keys": keys, "response": result.get("response")}
        elif keys == 2064:  # Love - use FingerHeart
            result = await send_sport_command(SPORT_CMD["FingerHeart"])
            return {"ok": result.get("ok", False), "action": "love", "keys": keys, "response": result.get("response")}
        else:
            # Default to stop movement
            result = await send_sport_command(SPORT_CMD["StopMove"])
            return {"ok": result.get("ok", False), "action": "stop", "keys": keys, "response": result.get("response")}
            
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ===== MCP tools =====

@mcp.tool()
async def connect(
    method: Literal["LocalAP","LocalSTA","Remote"]="LocalSTA",
    ip: Optional[str]=None,
    serial: Optional[str]=None,
    username: Optional[str]=None,
    password: Optional[str]=None
) -> dict:
    """
    Connect to the Go2 via WebRTC (AP / STA-L / Remote). 
    Provide either ip or serial. Remote may require username/password.
    """
    if not Go2WebRTCConnection:
        return {"ok": False, "error": "WebRTC driver not available"}
    
    await _ensure_disconnected()
    kwargs: Dict[str, Any] = {}
    if ip: 
        kwargs["ip"] = ip
    if serial: 
        kwargs["serialNumber"] = serial
    if username: 
        kwargs["username"] = username
    if password: 
        kwargs["password"] = password

    try:
        state.conn = Go2WebRTCConnection(_method_from_str(method), **kwargs)
        
        # Connect to the WebRTC service (required as shown in sportmode.py)
        await state.conn.connect()
        
        state.connected = True

        # Ensure MCF mode is active
        await switch_to_mcf_mode()

        return {"ok": True, "method": method, **kwargs}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@mcp.tool()
async def disconnect() -> dict:
    """Disconnect from the robot."""
    await _ensure_disconnected()
    return {"ok": True}

@mcp.tool()
async def jog(lx: float=0.3, ly: float=0.0, yaw: float=0.0, duration_s: float=1.0) -> dict:
    """
    Command body-frame velocity for a duration, then auto-zero.
    Uses SPORT_MOD topic with Move command as shown in sportmode.py
    """
    try:
        # Ensure MCF mode is active
        # await switch_to_mcf_mode()

        # Use SPORT_MOD topic with Move command
        sport_topic = _topic("SPORT_MOD", "rt/api/sport_mod")
        
        # Send movement command using helper function
        result = await move_robot(x=lx, y=ly, z=yaw)
        
        # Wait for the specified duration
        await asyncio.sleep(max(0.0, duration_s))
        
        return {"ok": result.get("ok", False), "topic": "SPORT_MOD", "duration": duration_s, "response": result.get("response")}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@mcp.tool()
async def stand() -> dict:
    """Stand/enable motors."""
    try:
        # Ensure MCF mode is active
        await switch_to_mcf_mode()

        # Use SPORT_MOD topic with StandUp command
        result = await send_sport_command(SPORT_CMD["StandUp"])
        return {"ok": result.get("ok", False), "topic": "SPORT_MOD", "response": result.get("response")}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@mcp.tool()
async def sit() -> dict:
    """Sit/disable motors."""
    try:
        # Ensure MCF mode is active
        await switch_to_mcf_mode()

        # Use SPORT_MOD topic with Sit command
        result = await send_sport_command(SPORT_CMD["Sit"])
        return {"ok": result.get("ok", False), "topic": "SPORT_MOD", "response": result.get("response")}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@mcp.tool()
async def liedown() -> dict:
    """Lie down/stand down."""
    try:
        # Ensure MCF mode is active
        await switch_to_mcf_mode()

        # Use SPORT_MOD topic with StandDown command
        result = await send_sport_command(SPORT_CMD["StandDown"])
        return {"ok": result.get("ok", False), "topic": "SPORT_MOD", "response": result.get("response")}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@mcp.tool()
async def estop() -> dict:
    """Emergency stop."""
    try:
        topic = _topic("ESTOP", "rt/api/estop")
        await _send_async(topic, {})
        return {"ok": True, "topic": topic}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@mcp.tool()
async def lowstate() -> dict:
    """Return cached low-level state (as exposed by the driver)."""
    try:
        data = getattr(_conn(), "low_state", None)
        return {"ok": True, "lowstate": data}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@mcp.tool()
async def multistate() -> dict:
    """Return cached multi-state (brightness, bodyHeight, etc.)."""
    try:
        data = getattr(_conn(), "multi_state", None)
        return {"ok": True, "multistate": data}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@mcp.tool()
async def front_photo() -> dict:
    """
    Ask the videohub for a front-camera photo (JPEG).
    Topic key FRONT_PHOTO_REQ normally maps to 'rt/api/videohub/request'.
    """
    try:
        topic = _topic("FRONT_PHOTO_REQ", "rt/api/videohub/request")
        await _send_async(topic, {"camera": "front", "action": "photo"})
        return {"ok": True, "topic": topic}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@mcp.tool()
async def publish(topic_or_key: str, payload: dict) -> dict:
    """
    Raw passthrough to any WebRTC API topic. Accepts a symbolic key (from RTC_TOPIC)
    or a full 'rt/.../...' path.
    """
    try:
        topic = RTC_TOPIC.get(topic_or_key, topic_or_key)
        await _send_async(topic, payload)
        return {"ok": True, "topic": topic, "payload": payload}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@mcp.tool()
async def robot_status() -> dict:
    """Get the current status of the Go2 robot."""
    try:
        status = {
            "connected": state.connected,
            "connection_type": "WebRTC",
            "robot_info": "Unitree Go2"
        }
        
        if state.connected and state.conn:
            # Try to get additional status info
            try:
                # Get basic robot information if available
                if hasattr(state.conn, "low_state"):
                    status["low_state_available"] = True
                if hasattr(state.conn, "multi_state"):
                    status["multi_state_available"] = True
                status["connection_status"] = "Active"
            except Exception as e:
                status["connection_status"] = f"Error: {str(e)}"
        
        return {"ok": True, "status": status}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@mcp.tool()
async def execute_command(command: str) -> dict:
    """
    Execute a natural language command for the Go2 robot.
    Parses common commands and maps them to appropriate robot actions.
    """
    if not state.connected:
        return {"ok": False, "error": "Robot not connected. Please connect first."}
    
    command_lower = command.lower()
    
    try:
        # Parse natural language commands
        if any(word in command_lower for word in ["forward", "ahead", "straight"]):
            await jog(lx=0.5, ly=0.0, yaw=0.0, duration_s=2.0)
            return {"ok": True, "action": "Moving robot forward for 2 seconds"}
            
        elif any(word in command_lower for word in ["backward", "back", "reverse"]):
            await jog(lx=-0.5, ly=0.0, yaw=0.0, duration_s=2.0)
            return {"ok": True, "action": "Moving robot backward for 2 seconds"}
            
        elif any(word in command_lower for word in ["left", "turn left"]):
            await jog(lx=0.0, ly=0.0, yaw=0.5, duration_s=2.0)
            return {"ok": True, "action": "Turning robot left for 2 seconds"}
            
        elif any(word in command_lower for word in ["right", "turn right"]):
            await jog(lx=0.0, ly=0.0, yaw=-0.5, duration_s=2.0)
            return {"ok": True, "action": "Turning robot right for 2 seconds"}
            
        elif any(word in command_lower for word in ["stop", "halt", "pause"]):
            await jog(lx=0.0, ly=0.0, yaw=0.0, duration_s=0.0)
            return {"ok": True, "action": "Stopping robot"}
            
        elif any(word in command_lower for word in ["dance", "spin", "rotate"]):
            # Simple dance sequence
            await jog(lx=0.0, ly=0.0, yaw=0.8, duration_s=1.0)
            await asyncio.sleep(1.0)
            await jog(lx=0.0, ly=0.0, yaw=-0.8, duration_s=1.0)
            await asyncio.sleep(1.0)
            await jog(lx=0.3, ly=0.0, yaw=0.0, duration_s=1.0)
            return {"ok": True, "action": "Executed dance sequence"}
            
        elif any(word in command_lower for word in ["stand up", "stand", "enable"]):
            await stand()
            return {"ok": True, "action": "Robot standing up"}
            
        elif any(word in command_lower for word in ["sit down", "sit", "disable"]):
            await sit()
            return {"ok": True, "action": "Robot sitting down"}
            
        else:
            return {
                "ok": False, 
                "error": f"Command not understood: '{command}'. Try: forward, backward, left, right, stop, dance, stand, sit"
            }
            
    except Exception as e:
        return {"ok": False, "error": f"Command execution failed: {str(e)}"}

# ===== Wireless Controller MCP Tools (replicating the reference functions) =====

@mcp.tool()
async def wireless_controller_publish(
    lx: float = 0.0, 
    ly: float = 0.0, 
    rx: float = 0.0, 
    ry: float = 0.0, 
    keys: int = 0, 
    duration: float = 0.0
) -> dict:
    """
    Publish wireless controller message via WebRTC.
    
    Parameters:
    - lx: left stick x axis (-1 ~ 1) -> robot move left and right
    - ly: left stick y axis (-1 ~ 1) -> robot move forward and backward  
    - rx: right stick x axis (-1 ~ 1) -> robot rotate left and right
    - ry: right stick y axis (-1 ~ 1) -> robot rotate up and down
    - keys: button state
    - duration: movement duration in seconds
    """
    return await _wireless_controller_publish(lx, ly, rx, ry, keys, duration)

@mcp.tool()
async def stand_up_from_fall() -> dict:
    """Stand up from a fall position."""
    return await _customised_movements(keys=1056)

@mcp.tool()
async def stretch() -> dict:
    """Execute stretch movement."""
    result = await _customised_movements(keys=1056)  # Stand up first
    if result.get("ok"):
        await asyncio.sleep(0.5)
        return await _customised_movements(keys=272)
    return result

@mcp.tool()
async def shake_hands() -> dict:
    """Execute shake hands movement."""
    result = await _customised_movements(keys=1056)  # Stand up first
    if result.get("ok"):
        await asyncio.sleep(0.5)
        return await _customised_movements(keys=528)
    return result

@mcp.tool()
async def love() -> dict:
    """Execute love movement."""
    result = await _customised_movements(keys=1056)  # Stand up first
    if result.get("ok"):
        await asyncio.sleep(0.5)
        return await _customised_movements(keys=2064)
    return result

@mcp.tool()
async def pounce() -> dict:
    """Execute pounce movement."""
    result = await _customised_movements(keys=1056)  # Stand up first
    if result.get("ok"):
        await asyncio.sleep(0.5)
        return await _customised_movements(keys=1025)
    return result

@mcp.tool()
async def jump_forward() -> dict:
    """Execute jump forward movement."""
    result = await _customised_movements(keys=1056)  # Stand up first
    if result.get("ok"):
        await asyncio.sleep(0.5)
        return await _customised_movements(keys=257)
    return result

@mcp.tool()
async def sit_down() -> dict:
    """Execute sit down movement."""
    result = await _customised_movements(keys=1056)  # Stand up first
    if result.get("ok"):
        await asyncio.sleep(0.5)
        return await _customised_movements(keys=513)
    return result

@mcp.tool()
async def greet() -> dict:
    """Execute greet movement."""
    result = await _customised_movements(keys=1056)  # Stand up first
    if result.get("ok"):
        await asyncio.sleep(0.5)
        return await _customised_movements(keys=258)
    return result

@mcp.tool()
async def dance() -> dict:
    """Execute dance movement."""
    result = await _customised_movements(keys=1056)  # Stand up first
    if result.get("ok"):
        await asyncio.sleep(0.5)
        return await _customised_movements(keys=514)
    return result

@mcp.tool()
async def stop_movement() -> dict:
    """Stop all movement."""
    return await _customised_movements(keys=0, duration=0.3)

@mcp.tool()
async def stop() -> dict:
    """Stop all movement."""
    try:
        # Ensure normal mode is active
        await switch_to_mcf_mode()
        
        # Use SPORT_MOD topic with StopMove command
        result = await send_sport_command(SPORT_CMD["StopMove"])
        return {"ok": result.get("ok", False), "topic": "SPORT_MOD", "response": result.get("response")}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@mcp.tool()
async def balance_stand() -> dict:
    """Enter balance stand mode."""
    try:
        # Ensure MCF mode is active
        await switch_to_mcf_mode()
        
        # Use SPORT_MOD topic with BalanceStand command
        result = await send_sport_command(SPORT_CMD["BalanceStand"])
        return {"ok": result.get("ok", False), "topic": "SPORT_MOD", "response": result.get("response")}
    except Exception as e:
        return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    # Run as a stdio MCP server (works with Inspector / Claude Desktop / Cursor).
    stdio_server.run(mcp)
