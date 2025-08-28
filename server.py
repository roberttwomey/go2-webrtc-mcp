#!/usr/bin/env python3
"""
Unitree Go2 WebRTC MCP Server using FastMCP
A simple MCP server that enables natural language control of the Unitree Go2 robot
using WebRTC connections instead of ROS.
"""

import asyncio
from typing import Optional, Literal, Any, Dict
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server

# Import the WebRTC driver
try:
    from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
    from go2_webrtc_driver.constants import RTC_TOPIC
except ImportError:
    print("Warning: go2_webrtc_driver not found. Please install it first.")
    # Fallback imports for development
    Go2WebRTCConnection = None
    WebRTCConnectionMethod = None
    RTC_TOPIC = {}

# ===== App state =====
@dataclass
class Go2State:
    conn: Optional[Go2WebRTCConnection] = None
    connected: bool = False

state = Go2State()
mcp = FastMCP("go2-webrtc")

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

def _send(topic: str, payload: dict) -> None:
    """Send payload to topic using available driver method"""
    conn = _conn()
    if hasattr(conn, "send_api_request"):
        conn.send_api_request(topic, payload)
    elif hasattr(conn, "publish"):
        conn.publish(topic, payload)
    else:
        raise RuntimeError("Driver has neither send_api_request nor publish; check your go2_webrtc_connect version.")

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
        
        # If your build requires an explicit start/connect, uncomment:
        # maybe = getattr(state.conn, "connect", None)
        # if callable(maybe):
        #     res = maybe()
        #     if asyncio.iscoroutine(res): 
        #         await res
        
        state.connected = True
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
    Payload expected by Unitree WebRTC walk API: {x, y, yaw, duration}
    """
    try:
        walk_topic = _topic("WALK", "rt/api/walk")
        _send(walk_topic, {"x": lx, "y": ly, "yaw": yaw, "duration": duration_s})
        
        # Wait for duration then zero velocity for safety
        await asyncio.sleep(max(0.0, duration_s))
        _send(walk_topic, {"x": 0.0, "y": 0.0, "yaw": 0.0, "duration": 0.0})
        
        return {"ok": True, "topic": walk_topic, "duration": duration_s}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@mcp.tool()
async def stand() -> dict:
    """Stand/enable motors."""
    try:
        topic = _topic("STAND", "rt/api/stand")
        _send(topic, {})
        return {"ok": True, "topic": topic}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@mcp.tool()
async def sit() -> dict:
    """Sit/disable motors."""
    try:
        topic = _topic("SIT", "rt/api/sit")
        _send(topic, {})
        return {"ok": True, "topic": topic}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@mcp.tool()
async def estop() -> dict:
    """Emergency stop."""
    try:
        topic = _topic("ESTOP", "rt/api/estop")
        _send(topic, {})
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
        _send(topic, {"camera": "front", "action": "photo"})
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
        _send(topic, payload)
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

if __name__ == "__main__":
    # Run as a stdio MCP server (works with Inspector / Claude Desktop / Cursor).
    stdio_server.run(mcp)
