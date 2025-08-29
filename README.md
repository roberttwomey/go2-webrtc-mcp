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
- **Conda Environment Support**: Optional conda environment for dependency isolation

## Prerequisites

- Python 3.8 or higher (or conda for environment management)
- Unitree Go2 robot (AIR/PRO/EDU models supported)
- Network connection to the robot

## Installation

### Option 1: Standard Installation (Recommended)

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

### Option 2: Conda Environment Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd unitree-go2-webrtc-mcp-server
   ```

2. **Run the automated setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   This will:
   - Create a conda environment named `bff-mcp`
   - Install all dependencies in the isolated environment
   - Set up MCP configuration
   - Test the installation

3. **Activate the conda environment:**
   ```bash
   conda activate bff-mcp
   ```

### Option 3: Manual Conda Environment

1. **Create conda environment:**
   ```bash
   conda env create -f environment.yml
   ```

2. **Activate the environment:**
   ```bash
   conda activate bff-mcp
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

#### Standard Python Installation
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

#### Conda Environment Installation
If using the conda environment, use this configuration instead:

```json
{
    "mcpServers": {
        "go2-webrtc": {
            "command": "conda",
            "args": [
                "run", 
                "-n", 
                "bff-mcp", 
                "python", 
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

#### Basic Control Tools

##### 1. `connect`
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

##### 2. `disconnect`
Disconnect from the currently connected robot.

##### 3. `jog`
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

##### 4. `stand`
Stand up/enable motors.

##### 5. `sit`
Sit down/disable motors.

##### 6. `estop`
Emergency stop.

##### 7. `lowstate`
Get cached low-level state from the robot.

##### 8. `multistate`
Get cached multi-state (brightness, bodyHeight, etc.).

##### 9. `front_photo`
Request a front-camera photo.

##### 10. `publish`
Raw passthrough to any WebRTC API topic.

##### 11. `robot_status`
Get the current status of the Go2 robot.

##### 12. `execute_command`
Execute natural language commands.

**Parameters:**
- `command` (required): Natural language command

**Example:**
```json
{
    "command": "Move the robot forward"
}
```

#### Wireless Controller Tools (ROS2 Compatibility)

These tools replicate the functionality from the reference [unitree-go2-mcp-server](https://github.com/lpigeon/unitree-go2-mcp-server) repository, adapted from ROS2 to WebRTC:

##### 13. `wireless_controller_publish`
Publish wireless controller message via WebRTC (adapted from ROS2).

**Parameters:**
- `lx` (optional): Left stick X axis (-1 ~ 1) -> robot move left and right
- `ly` (optional): Left stick Y axis (-1 ~ 1) -> robot move forward and backward
- `rx` (optional): Right stick X axis (-1 ~ 1) -> robot rotate left and right
- `ry` (optional): Right stick Y axis (-1 ~ 1) -> robot rotate up and down
- `keys` (optional): Button state
- `duration` (optional): Movement duration in seconds

**Example:**
```json
{
    "lx": 0.0,
    "ly": 0.5,
    "rx": 0.0,
    "ry": 0.0,
    "keys": 0,
    "duration": 2.0
}
```

##### 14. `stand_up_from_fall`
Stand up from a fall position.

##### 15. `stretch`
Execute stretch movement.

##### 16. `shake_hands`
Execute shake hands movement.

##### 17. `love`
Execute love movement.

##### 18. `pounce`
Execute pounce movement.

##### 19. `jump_forward`
Execute jump forward movement.

##### 20. `sit_down`
Execute sit down movement.

##### 21. `greet`
Execute greet movement.

##### 22. `dance`
Execute dance movement.

##### 23. `stop_movement`
Stop all movement.

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

#### Standard Python
```bash
# Run as stdio MCP server
python3 server.py

# Or with specific transport
python3 server.py stdio
```

#### Conda Environment
```bash
# Activate environment first
conda activate bff-mcp

# Run as stdio MCP server
python server.py

# Or with specific transport
python server.py stdio
```

### Testing

#### Standard Python
```bash
# Test installation
python3 test_installation.py

# Test FastMCP tools specifically
python3 test_fastmcp.py

# Run examples
python3 example_usage.py
```

#### Conda Environment
```bash
# Activate environment first
conda activate bff-mcp

# Test installation
python test_installation.py

# Test FastMCP tools specifically
python test_fastmcp.py

# Run examples
python example_usage.py
```

### Understanding FastMCP Tools

The FastMCP server registers tools as Python functions that can be imported and called directly. Each tool function is decorated with `@mcp.tool()` and can be used in two ways:

1. **As MCP tools** (when the server is running as an MCP server)
2. **As Python functions** (when imported and called directly)

#### Tool Functions Available:

```python
from server import (
    connect, disconnect, jog, stand, sit, estop,
    lowstate, multistate, front_photo, publish,
    robot_status, execute_command
)

# Example usage:
result = await connect(method="LocalSTA", ip="192.168.4.30")
result = await robot_status()
result = await execute_command("Move forward")
```

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure you've installed the WebRTC driver correctly
2. **Connection Failed**: Verify your robot is powered on and connected to the network
3. **Permission Denied**: Ensure you have the necessary permissions to run Python scripts
4. **FastMCP Error**: Make sure you have `mcp[cli]` installed
5. **Conda Environment Issues**: Always activate the environment with `conda activate bff-mcp`

### Driver Method Errors

If you encounter errors like:
```
'Driver has no compatible send/publish method'
```

This means the `go2_webrtc_connect` driver has different method names than expected. Here's how to fix it:

#### Step 1: Install/Reinstall the Driver
```bash
# Run the automated installer
python3 install_driver.py

# Or manually:
git clone --recurse-submodules https://github.com/legion1581/go2_webrtc_connect.git
cd go2_webrtc_connect
pip install -e .
cd ..
```

#### Step 2: Debug the Driver
```bash
# Check what methods are available
python3 debug_driver.py
```

#### Step 3: Update Method Names (if needed)
If the debug shows different method names, you may need to update the server code. Common alternatives:
- `send_api_request` → `send`
- `send_api_request` → `publish`
- `send_api_request` → `api_request`

#### Step 4: Check Driver Version
Different versions of the driver may have different APIs. Check the [go2_webrtc_connect repository](https://github.com/legion1581/go2_webrtc_connect) for the latest documentation.

### Debug Mode

The server includes comprehensive error handling and returns structured responses with `ok` and `error` fields for easy debugging.

### Conda Environment Management

```bash
# List environments
conda env list

# Activate environment
conda activate bff-mcp

# Deactivate environment
conda deactivate

# Remove environment (if needed)
conda env remove -n bff-mcp

# Recreate environment
conda env create -f environment.yml
```

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
