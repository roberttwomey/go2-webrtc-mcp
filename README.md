# Unitree Go2 WebRTC MCP Server

A simple Model Context Protocol (MCP) server that enables natural language control of the Unitree Go2 robot using WebRTC connections instead of ROS. This server provides an intuitive interface for controlling your Go2 robot through natural language commands interpreted by an LLM.

## Features

- **WebRTC Connection**: Uses the official Unitree WebRTC driver for reliable robot communication
- **No ROS Required**: Works without ROS installation or configuration
- **Multiple Connection Methods**: Supports AP mode, local network, and remote TURN server connections
- **Natural Language Control**: Execute robot commands using simple English phrases
- **MCP Integration**: Seamlessly integrates with MCP-compatible AI assistants

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
        "unitree-go2-webrtc-mcp-server": {
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
   - Use `connection_method: "local_ap"`
   - No additional parameters needed

2. **Local STA Mode**: Robot and client on same network
   - Use `connection_method: "local_sta"`
   - Provide either `ip_address` or `serial_number`

3. **Remote Mode**: Connect through Unitree's TURN server
   - Use `connection_method: "remote"`
   - Requires `serial_number`, `username`, and `password`

## Usage

### Available Tools

The MCP server provides the following tools:

#### 1. `connect_robot`
Connect to a Go2 robot using WebRTC.

**Parameters:**
- `connection_method` (required): "local_ap", "local_sta", or "remote"
- `ip_address` (optional): Robot's IP address for local_sta mode
- `serial_number` (optional): Robot's serial number
- `username` (optional): Unitree account username for remote mode
- `password` (optional): Unitree account password for remote mode

**Example:**
```json
{
    "connection_method": "local_sta",
    "ip_address": "192.168.8.181"
}
```

#### 2. `disconnect_robot`
Disconnect from the currently connected robot.

#### 3. `move_robot`
Move the robot with specific parameters.

**Parameters:**
- `action` (required): "forward", "backward", "left", "right", or "stop"
- `duration` (optional): Movement duration in seconds
- `speed` (optional): Movement speed (0.0 to 1.0)

**Example:**
```json
{
    "action": "forward",
    "duration": 3.0,
    "speed": 0.7
}
```

#### 4. `robot_status`
Get the current status of the robot.

#### 5. `execute_command`
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

## Examples

### Basic Usage Flow

1. **Connect to robot:**
   ```
   Connect to my Go2 robot using local network mode with IP 192.168.8.181
   ```

2. **Move robot:**
   ```
   Make the robot move forward for 3 seconds
   ```

3. **Execute complex command:**
   ```
   Have the robot dance for me
   ```

4. **Check status:**
   ```
   What's the current status of my robot?
   ```

5. **Disconnect:**
   ```
   Disconnect from the robot
   ```

### Claude Desktop Integration

If using Claude Desktop, you can control your robot with natural language:

- "Connect to my Go2 robot and make it move forward"
- "Turn the robot left and then stop it"
- "Execute a dance sequence on the robot"
- "What's the battery level of my robot?"

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure you've installed the WebRTC driver correctly
2. **Connection Failed**: Verify your robot is powered on and connected to the network
3. **Permission Denied**: Ensure you have the necessary permissions to run Python scripts

### Debug Mode

Enable debug logging by modifying the logging level in `server.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [go2_webrtc_connect](https://github.com/legion1581/go2_webrtc_connect) - The WebRTC driver implementation
- [unitree-go2-mcp-server](https://github.com/lpigeon/unitree-go2-mcp-server) - Original MCP server inspiration
- TheRoboVerse community for support and feedback

## Support

If you encounter any issues or have questions, please:
1. Check the troubleshooting section
2. Review the existing issues
3. Create a new issue with detailed information about your problem

---

**Note**: This server requires the Unitree Go2 robot to be running compatible firmware (1.1.1-1.1.7 or 1.0.19-1.0.25).
