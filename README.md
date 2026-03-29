Requirements

    🐍 Python 3.11+
    📶 Bleak 0.19.0+
    📶 bleak-retry-connector

Supported Operating Systems

    🐧 Linux (BlueZ)
        Ubuntu Desktop
        Arch (HomeAssistant OS)
    🏢 Windows
        Windows 10
    💾 Mac OSX
        Maybe?

Usage

1. Initialize the light (do this first)

curl -X POST http://localhost:5000/init \
  -H "Content-Type: application/json" \
  -d '{"mac_address": "[insert mac address]"}'

2. Turn light on

curl -X POST http://localhost:5000/power \
  -H "Content-Type: application/json" \
  -d '{"state": true}'
  
curl -X POST http://localhost:5000/power \
  -H "Content-Type: application/json" \
  -d '{"state": false}'

3. Set brightness

curl -X POST http://localhost:5000/brightness \
  -H "Content-Type: application/json" \
  -d '{"value": 200}'

4. Set color temperature

curl -X POST http://localhost:5000/color_temp \
  -H "Content-Type: application/json" \
  -d '{"value": 250}'

5. Set color

curl -X POST http://localhost:5000/color \
  -H "Content-Type: application/json" \
  -d '{"x": 0.4, "y": 0.5}'

6. Check status

curl http://localhost:5000/status

New GET Endpoints
Read power state
bash

curl http://localhost:5000/power

Response:
json

{
  "success": true,
  "data": {
    "power": true
  }
}

Read brightness
bash

curl http://localhost:5000/brightness

Response:
json

{
  "success": true,
  "data": {
    "brightness": 200
  }
}

Read color temperature
bash

curl http://localhost:5000/color_temp

Response:
json

{
  "success": true,
  "data": {
    "color_temperature": 250
  }
}

Read color
bash

curl http://localhost:5000/color

Response:
json

{
  "success": true,
  "data": {
    "x": 0.4,
    "y": 0.5
  }
}

Read all properties at once
bash

curl http://localhost:5000/all

Response:
json

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
