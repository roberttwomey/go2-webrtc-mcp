#!/usr/bin/env python3
import asyncio, base64, json, time
from typing import Optional, Dict, Any
import numpy as np, cv2

# === MCP (Anthropic Model Context Protocol) ===
from mcp.server.fastmcp import FastMCP, Context

# === Unitree Go2 WebRTC driver (this repo) ===
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
from go2_webrtc_driver.constants import RTC_TOPIC

# ---- config ----
FRAME_W, FRAME_H = 640, 360
MAX_LIN, MAX_ANG = 0.40, 0.80   # m/s, rad/s (safety clamps)
BURST = 0.5                     # seconds
HEARTBEAT = 2.0

app = FastMCP("go2-mcp-webrtc")
_lock = asyncio.Lock()

class Go2Session:
    def __init__(self):
        self.conn: Optional[Go2WebRTCConnection] = None
        self.latest_bgr = None
        self.lowstate = {}
        self._tasks = []

    async def connect(self, mode: str = "LocalSTA", **kw):
        if self.conn:
            return "already connected"
        # mode: LocalAP | LocalSTA | Remote (per repo)
        method = getattr(WebRTCConnectionMethod, mode)
        self.conn = Go2WebRTCConnection(method, **kw)
        await self.conn.connect()

        # subscribe camera + lowstate (topics come from repo constants)
        await self.conn.subscribe(RTC_TOPIC.FRONT_VIDEO)
        await self.conn.subscribe(RTC_TOPIC.LOWSTATE)

        self._tasks += [
            asyncio.create_task(self._pump_video()),
            asyncio.create_task(self._pump_lowstate()),
            asyncio.create_task(self._heartbeat()),
        ]
        return f"connected via {mode}"

    async def _pump_video(self):
        async for frame in self.conn.video_generator(RTC_TOPIC.FRONT_VIDEO):
            if frame is None:
                continue
            img = frame if isinstance(frame, np.ndarray) else frame[0]
            self.latest_bgr = cv2.resize(img, (FRAME_W, FRAME_H))

    async def _pump_lowstate(self):
        async for msg in self.conn.message_generator(RTC_TOPIC.LOWSTATE):
            self.lowstate = msg or {}

    async def _heartbeat(self):
        while True:
            await asyncio.sleep(HEARTBEAT)
            # no-op: keep tasks alive; good place for watchdogs

    def require(self):
        if not self.conn:
            raise RuntimeError("Not connected")

    def snapshot_b64(self):
        if self.latest_bgr is None:
            return None
        ok, buf = cv2.imencode(".jpg", self.latest_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        return base64.b64encode(buf.tobytes()).decode("ascii") if ok else None

    async def cmd_vel(self, vx, vy, wz, duration=BURST):
        self.require()
        vx = float(np.clip(vx, -MAX_LIN, MAX_LIN))
        vy = float(np.clip(vy, -MAX_LIN, MAX_LIN))
        wz = float(np.clip(wz, -MAX_ANG, MAX_ANG))
        await self.conn.publish(RTC_TOPIC.CMD_VEL, {"vx": vx, "vy": vy, "wz": wz, "duration": float(duration)})
        return {"vx": vx, "vy": vy, "wz": wz, "duration": float(duration)}

    async def action(self, name: str):
        self.require()
        n = name.lower()
        if n == "stop":
            await self.conn.publish(RTC_TOPIC.CMD_STOP, {})
        elif n == "stand":
            await self.conn.publish(RTC_TOPIC.CMD_STAND, {})
        elif n == "sit":
            await self.conn.publish(RTC_TOPIC.CMD_SIT, {})
        else:
            raise ValueError(f"unknown action: {name}")
        return {"ok": True, "action": n}

SESSION = Go2Session()

# ---- MCP tools ----
@app.tool()
async def connect_webrtc(ctx: Context, mode: str = "LocalSTA",
                         ip: Optional[str] = None,
                         serialNumber: Optional[str] = None,
                         username: Optional[str] = None,
                         password: Optional[str] = None) -> str:
    """
    Connect to Go2 over WebRTC using the repo's modes:
    mode = LocalAP | LocalSTA | Remote; pass ip/serialNumber/username/password as needed.
    """
    async with _lock:
        kw = {}
        if ip: kw["ip"] = ip
        if serialNumber: kw["serialNumber"] = serialNumber
        if username: kw["username"] = username
        if password: kw["password"] = password
        return await SESSION.connect(mode=mode, **kw)

@app.tool()
async def get_lowstate(ctx: Context) -> Dict[str, Any]:
    """Return latest low-level state."""
    return SESSION.lowstate or {}

@app.tool()
async def get_frame_jpeg_b64(ctx: Context) -> Dict[str, Any]:
    """Return base64 JPEG (640x360) of the front camera."""
    b64 = SESSION.snapshot_b64()
    return {"ok": bool(b64), "jpeg_b64": b64, "w": FRAME_W, "h": FRAME_H}

@app.tool()
async def move_body(ctx: Context, vx: float = 0, vy: float = 0, wz: float = 0, duration: float = BURST):
    """Velocity command (safety-clamped)."""
    return await SESSION.cmd_vel(vx, vy, wz, duration)

@app.tool()
async def robot_action(ctx: Context, name: str):
    """'stand' | 'sit' | 'stop'."""
    return await SESSION.action(name)

# Optional: expose the frame as a resource clients can preview
@app.resource("robot://front_camera.jpg")
async def front_jpeg():
    b64 = SESSION.snapshot_b64()
    return (base64.b64decode(b64) if b64 else b""), "image/jpeg"

# A default safety prompt assistants can load
@app.prompt()
async def driving_policy():
    return {"messages": [
        {"role": "system", "content":
         "Safety: |vx|,|vy|<=0.4 m/s, |wz|<=0.8 rad/s, bursts<=0.6 s. "
         "Stop if unsure. Re-check camera & state every burst."},
        {"role": "user", "content":
         "Use get_frame_jpeg_b64 + get_lowstate to assess; then short move_body bursts; use robot_action('stop') to halt."}
    ]}

if __name__ == "__main__":
    app.run()
