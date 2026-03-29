## Requirements

🐍 Python 3.11+

📶 Bleak 0.19.0+

📶 bleak-retry-connector

💡[HueBLE](https://github.com/flip-dots/HueBLE)

## Installation

```bash
pip install flask bleak
```
[HueBLE](https://github.com/flip-dots/HueBLE) is already included

## Supported Operating Systems

🐧 Linux (BlueZ)

Ubuntu Desktop

Debian with GNOME Desktop Enviroment
    
Arch (HomeAssistant OS)
    
🏢 Windows

Windows 10 and 11

💾 Mac OSX

Maybe?

## Usage Examples

### 1. Initialize the light (do this first)
```bash
curl -X POST http://localhost:5000/init \
  -H "Content-Type: application/json" \
  -d '{"mac_address": "AA:BB:CC:DD:EE:FF"}'
```

### 2. Turn light on
```bash
curl -X POST http://localhost:5000/power \
  -H "Content-Type: application/json" \
  -d '{"state": true}'
```

### 3. Set brightness
```bash
curl -X POST http://localhost:5000/brightness \
  -H "Content-Type: application/json" \
  -d '{"value": 200}'
```

### 4. Set color temperature
```bash
curl -X POST http://localhost:5000/color_temp \
  -H "Content-Type: application/json" \
  -d '{"value": 250}'
```

### 5. Set color
```bash
curl -X POST http://localhost:5000/color \
  -H "Content-Type: application/json" \
  -d '{"x": 0.4, "y": 0.5}'
```

### 6. Check status
```bash
curl http://localhost:5000/status
```
## Other GET Endpoints

### Read power state
```bash
curl http://localhost:5000/power
```
**Response:**
```json
{
  "success": true,
  "data": {
    "power": true
  }
}
```

### Read brightness
```bash
curl http://localhost:5000/brightness
```
**Response:**
```json
{
  "success": true,
  "data": {
    "brightness": 200
  }
}
```

### Read color temperature
```bash
curl http://localhost:5000/color_temp
```
**Response:**
```json
{
  "success": true,
  "data": {
    "color_temperature": 250
  }
}
```

### Read color
```bash
curl http://localhost:5000/color
```
**Response:**
```json
{
  "success": true,
  "data": {
    "x": 0.4,
    "y": 0.5
  }
}
```

### Read all properties at once
```bash
curl http://localhost:5000/all
```
**Response:**
```json
{
  "success": true,
  "data": {
    "power": true,
    "brightness": 200,
    "color_temperature": 250,
    "color": {
      "x": 0.4,
      "y": 0.5
    }
  }
}
```

The server will run on `http://localhost:5000` and wait for requests. Each endpoint automatically handles the asyncio bridging, so you can make requests in any order without worrying about the event loop.
