# policy_loop.py
import asyncio, json, requests
from mcp.client.session import Session

VLM_URL   = "http://localhost:11434/v1/chat/completions"  # OpenAI-compatible endpoint
VLM_MODEL = "qwen2.5-vl-7b"

SYS = ("Return STRICT JSON only: {\"vx\":float,\"vy\":float,\"wz\":float,\"duration\":float}. "
       "Keep |vx|<=0.3, |wz|<=0.6, duration<=0.6. If obstacle likely or unsure, return zeros.")

def ask_vlm(img_b64, lowstate, goal):
    payload = {
      "model": VLM_MODEL,
      "messages": [
        {"role": "system", "content": SYS},
        {"role": "user", "content": [
          {"type":"text","text": f"Goal: {goal}\nLowstate: {json.dumps(lowstate)[:1500]}"},
          {"type":"image_url","image_url":{"url": f"data:image/jpeg;base64,{img_b64}"}}
        ]}
      ],
      "temperature": 0.0
    }
    r = requests.post(VLM_URL, json=payload, timeout=60)
    r.raise_for_status()
    txt = r.json()["choices"][0]["message"]["content"]
    s, e = txt.find("{"), txt.rfind("}")
    return json.loads(txt[s:e+1]) if s >= 0 else {"vx":0,"vy":0,"wz":0,"duration":0.3}

async def main():
    # launch MCP server as a child, or connect to a running one
    async with Session.launch(command=["python", "go2_mcp_webrtc.py"]) as s:
        # pick one: LocalAP (direct), LocalSTA (LAN), Remote (TURN)
        await s.tools.call("connect_webrtc", {"mode":"LocalSTA", "ip":"192.168.4.30"})
        await s.tools.call("robot_action", {"name":"stand"})

        goal = "Face the visible tag or person and stay ~1.0 m away."
        while True:
            frame = await s.tools.call("get_frame_jpeg_b64", {})
            if not frame.get("ok"): 
                await asyncio.sleep(0.1); continue
            low = await s.tools.call("get_lowstate", {})

            action = ask_vlm(frame["jpeg_b64"], low, goal)
            for k in ("vx","vy","wz","duration"):
                action.setdefault(k, 0.0)
            print("VLM action:", action)
            await s.tools.call("move_body", action)
            await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main())
