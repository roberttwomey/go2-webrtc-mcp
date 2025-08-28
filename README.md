# Unitree Go2 WebRTC MCP Server using FastMCP

A simple Model Context Protocol (MCP) server that enables natural language control of the Unitree Go2 robot using WebRTC connections instead of ROS. This server uses FastMCP for a clean, modern implementation that provides an intuitive interface for controlling your Go2 robot through natural language commands interpreted by an LLM.

## Features

- **FastMCP Implementation**: Uses the modern FastMCP pattern for clean, maintainable code
- **WebRTC Connection**: Uses the official Unitree WebRTC driver for reliable robot communication
- **No ROS Required**: Works without ROS installation or configuration
- **Multiple Connection Methods**: Supports AP mode, local network, and remote TURN server connections
- **Natural Language Control**: Execute robot commands using simple English phrases
- **MCP Integration**: Seamlessly integrates with MCP-compatible AI assistants
- **Safety Features**: Auto-zero velocity after movement commands

## Prerequisites

- Python 3.8 or higher
- Unitree Go2 robot (AIR/PRO/EDU models supported)
- Network connection to the robot

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd unitree-go2-webrtc-mcp-server
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install the WebRTC driver:**
   ```bash
   git clone --recurse-submodules https://github.com/legion1581/go2_webrtc_connect.git
   cd go2_webrtc_connect
   pip install -e .
   cd ..
   ```

## Configuration

### MCP Client Configuration

Add the following to your MCP client configuration file (e.g., `mcp.json`):

```json
{
    "mcpServers": {
        "go2-webrtc": {
            "command": "python3",
            "args": [
                "server.py"
            ],
            "env": {
                "PYTHONPATH": "."
            }
        }
    }
}
```

### Connection Methods

The server supports three connection methods:

1. **Local AP Mode**: Robot creates its own WiFi network
   - Use `method: "LocalAP"`
   - No additional parameters needed

2. **Local STA Mode**: Robot and client on same network
   - Use `method: "LocalSTA"`
   - Provide either `ip` or `serial`

3. **Remote Mode**: Connect through Unitree's TURN server
   - Use `method: "Remote"`
   - Requires `serial`, `username`, and `password`

## Usage

### Available Tools

The FastMCP server provides the following tools:

#### 1. `connect`
Connect to a Go2 robot using WebRTC.

**Parameters:**
- `method` (required): "LocalAP", "LocalSTA", or "Remote"
- `ip` (optional): Robot's IP address for LocalSTA mode
- `serial` (optional): Robot's serial number
- `username` (optional): Unitree account username for Remote mode
- `password` (optional): Unitree account password for Remote mode

**Example:**
```json
{
    "method": "LocalSTA",
    "ip": "192.168.8.181"
}
```

#### 2. `disconnect`
Disconnect from the currently connected robot.

#### 3. `jog`
Move the robot with velocity control.

**Parameters:**
- `lx` (optional): Forward/backward velocity in m/s (default: 0.3)
- `ly` (optional): Left/right velocity in m/s (default: 0.0)
- `yaw` (optional): Yaw rotation velocity in rad/s (default: 0.0)
- `duration_s` (optional): Movement duration in seconds (default: 1.0)

**Example:**
```json
{
    "lx": 0.5,
    "yaw": 0.3,
    "duration_s": 2.0
}
```

#### 4. `stand`
Stand up/enable motors.

#### 5. `sit`
Sit down/disable motors.

#### 6. `estop`
Emergency stop.

#### 7. `lowstate`
Get cached low-level state from the robot.

#### 8. `multistate`
Get cached multi-state (brightness, bodyHeight, etc.).

#### 9. `front_photo`
Request a front-camera photo.

#### 10. `publish`
Raw passthrough to any WebRTC API topic.

#### 11. `robot_status`
Get the current status of the Go2 robot.

#### 12. `execute_command`
Execute natural language commands.

**Parameters:**
- `command` (required): Natural language command

**Example:**
```json
{
    "command": "Move the robot forward"
}
```

### Natural Language Commands

The server understands various natural language phrases:

- **Movement**: "forward", "ahead", "straight", "backward", "back", "reverse"
- **Turning**: "left", "turn left", "right", "turn right"
- **Control**: "stop", "halt", "pause"
- **Special**: "dance", "spin", "rotate"
- **Posture**: "stand up", "stand", "enable", "sit down", "sit", "disable"

## Examples

### Basic Usage Flow

1. **Connect to robot:**
   ```
   Connect to my Go2 robot using local network mode with IP 192.168.8.181
   ```

2. **Stand up:**
   ```
   Make the robot stand up
   ```

3. **Move robot:**
   ```
   Move the robot forward for 3 seconds
   ```

4. **Execute complex command:**
   ```
   Have the robot dance for me
   ```

5. **Check status:**
   ```
   What's the current status of my robot?
   ```

6. **Disconnect:**
   ```
   Disconnect from the robot
   ```

### Claude Desktop Integration

If using Claude Desktop, you can control your robot with natural language:

- "Connect to my Go2 robot and make it stand up"
- "Turn the robot left and then stop it"
- "Execute a dance sequence on the robot"
- "What's the current state of my robot?"

### Testing with MCP Inspector

You can test the server locally using the MCP Inspector:

```bash
# Install MCP CLI
pip install "mcp[cli]"

# Run the server with inspector
mcp dev server.py

# In the inspector, call tools like:
# connect(method="LocalSTA", ip="192.168.8.181")
# stand()
# jog(lx=0.2, yaw=0.3, duration_s=1.5)
# sit()
# front_photo()
```

## Development

### Running the Server

```bash
# Run as stdio MCP server
python3 server.py

# Or with specific transport
python3 server.py stdio
```

### Testing

```bash
# Test installation
python3 test_installation.py

# Run examples
python3 example_usage.py
```

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure you've installed the WebRTC driver correctly
2. **Connection Failed**: Verify your robot is powered on and connected to the network
3. **Permission Denied**: Ensure you have the necessary permissions to run Python scripts
4. **FastMCP Error**: Make sure you have `mcp[cli]` installed

### Debug Mode

The server includes comprehensive error handling and returns structured responses with `ok` and `error` fields for easy debugging.

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [go2_webrtc_connect](https://github.com/legion1581/go2_webrtc_connect) - The WebRTC driver implementation
- [unitree-go2-mcp-server](https://github.com/lpigeon/unitree-go2-mcp-server) - Original MCP server inspiration
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) - Modern MCP server implementation
- TheRoboVerse community for support and feedback

## Support

If you encounter any issues or have questions, please:
1. Check the troubleshooting section
2. Review the existing issues
3. Create a new issue with detailed information about your problem

---

**Note**: This server requires the Unitree Go2 robot to be running compatible firmware (1.1.1-1.1.7 or 1.0.19-1.0.25).
