import asyncio
from bleak import BleakScanner
from flask import Flask, request, jsonify
import HueBLE
import threading

app = Flask(__name__)

# Global variables to store light connection
light = None
device = None
loop = None

async def initialize_light(mac_addr):
    """Initialize the light connection"""
    global light, device
    try:
        device = await BleakScanner.find_device_by_address(mac_addr)
        if device is None:
            return False, "Device not found. Ensure it's discoverable and paired."
        
        light = HueBLE.HueBleLight(device)
        await light.connect()
        return True, "Light connected successfully"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

async def run_light_command(command, params):
    """Execute light commands asynchronously"""
    try:
        if command == "power":
            await light.set_power(params.get("state", False))
            return True, f"Power set to {params['state']}"
        
        elif command == "brightness":
            brightness = int(params.get("value", 128))
            if not (0 <= brightness <= 255):
                return False, "Brightness must be between 0 and 255"
            await light.set_brightness(brightness)
            return True, f"Brightness set to {brightness}"
        
        elif command == "color_temp":
            temp = int(params.get("value", 250))
            if not (153 <= temp <= 500):
                return False, "Color temperature must be between 153 and 500 mireds"
            await light.set_colour_temp(temp)
            return True, f"Color temperature set to {temp}"
        
        elif command == "color":
            x = float(params.get("x", 0.5))
            y = float(params.get("y", 0.5))
            if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
                return False, "X and Y values must be between 0.0 and 1.0"
            await light.set_colour_xy(x, y)
            return True, f"Color set to X:{x}, Y:{y}"
        
        else:
            return False, "Unknown command"
    
    except Exception as e:
        return False, f"Command error: {str(e)}"

async def get_light_state(state_type):
    """Read light state asynchronously"""
    try:
        if state_type == "power":
            power = await light.poll_power_state()
            return True, {"power": power}
        
        elif state_type == "brightness":
            brightness = await light.poll_brightness()
            return True, {"brightness": brightness}
        
        elif state_type == "color_temp":
            temp = await light.poll_colour_temp()
            return True, {"color_temperature": temp}
        
        elif state_type == "color":
            xy = await light.poll_colour_xy()
            return True, {"x": xy[0], "y": xy[1]}
        
        elif state_type == "all":
            power = await light.poll_power_state()
            brightness = await light.poll_brightness()
            temp = await light.poll_colour_temp()
            xy = await light.poll_colour_xy()
            return True, {
                "power": power,
                "brightness": brightness,
                "color_temperature": temp,
                "color": {"x": xy[0], "y": xy[1]}
            }
        
        else:
            return False, "Unknown state type"
    
    except Exception as e:
        return False, f"Read error: {str(e)}"

def run_async_command(command, params):
    """Bridge between Flask and asyncio"""
    try:
        future = asyncio.run_coroutine_threadsafe(
            run_light_command(command, params), loop
        )
        success, message = future.result(timeout=10)
        return success, message
    except Exception as e:
        return False, f"Execution error: {str(e)}"

def run_async_read(state_type):
    """Bridge between Flask and asyncio for reading state"""
    try:
        future = asyncio.run_coroutine_threadsafe(
            get_light_state(state_type), loop
        )
        success, data = future.result(timeout=10)
        return success, data
    except Exception as e:
        return False, f"Read error: {str(e)}"

@app.route('/init', methods=['POST'])
def init_light():
    """Initialize light connection with MAC address"""
    try:
        data = request.get_json()
        mac_addr = data.get('mac_address')
        
        if not mac_addr:
            return jsonify({"success": False, "message": "MAC address required"}), 400
        
        future = asyncio.run_coroutine_threadsafe(
            initialize_light(mac_addr), loop
        )
        success, message = future.result(timeout=15)
        
        if success:
            return jsonify({"success": True, "message": message}), 200
        else:
            return jsonify({"success": False, "message": message}), 400
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

# ==================== WRITE ENDPOINTS ====================

@app.route('/power', methods=['POST'])
def set_power():
    """Control light on/off"""
    try:
        if light is None:
            return jsonify({"success": False, "message": "Light not initialized"}), 400
        
        data = request.get_json()
        state = data.get('state')
        
        if state is None:
            return jsonify({"success": False, "message": "State parameter required (true/false)"}), 400
        
        success, message = run_async_command("power", {"state": state})
        status_code = 200 if success else 400
        return jsonify({"success": success, "message": message}), status_code
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/brightness', methods=['POST'])
def set_brightness():
    """Set light brightness (0-255)"""
    try:
        if light is None:
            return jsonify({"success": False, "message": "Light not initialized"}), 400
        
        data = request.get_json()
        value = data.get('value')
        
        if value is None:
            return jsonify({"success": False, "message": "Value parameter required (0-255)"}), 400
        
        success, message = run_async_command("brightness", {"value": value})
        status_code = 200 if success else 400
        return jsonify({"success": success, "message": message}), status_code
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/color_temp', methods=['POST'])
def set_color_temp():
    """Set color temperature (153-500 mireds)"""
    try:
        if light is None:
            return jsonify({"success": False, "message": "Light not initialized"}), 400
        
        data = request.get_json()
        value = data.get('value')
        
        if value is None:
            return jsonify({"success": False, "message": "Value parameter required (153-500)"}), 400
        
        success, message = run_async_command("color_temp", {"value": value})
        status_code = 200 if success else 400
        return jsonify({"success": success, "message": message}), status_code
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/color', methods=['POST'])
def set_color():
    """Set color using XY coordinates (0.0-1.0)"""
    try:
        if light is None:
            return jsonify({"success": False, "message": "Light not initialized"}), 400
        
        data = request.get_json()
        x = data.get('x')
        y = data.get('y')
        
        if x is None or y is None:
            return jsonify({"success": False, "message": "X and Y parameters required (0.0-1.0)"}), 400
        
        success, message = run_async_command("color", {"x": x, "y": y})
        status_code = 200 if success else 400
        return jsonify({"success": success, "message": message}), status_code
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

# ==================== READ ENDPOINTS ====================

@app.route('/power', methods=['GET'])
def get_power():
    """Get current power state (on/off)"""
    try:
        if light is None:
            return jsonify({"success": False, "message": "Light not initialized"}), 400
        
        success, data = run_async_read("power")
        status_code = 200 if success else 400
        return jsonify({"success": success, "data": data if success else None, "message": data if not success else ""}), status_code
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/brightness', methods=['GET'])
def get_brightness():
    """Get current brightness (0-255)"""
    try:
        if light is None:
            return jsonify({"success": False, "message": "Light not initialized"}), 400
        
        success, data = run_async_read("brightness")
        status_code = 200 if success else 400
        return jsonify({"success": success, "data": data if success else None, "message": data if not success else ""}), status_code
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/color_temp', methods=['GET'])
def get_color_temp():
    """Get current color temperature (153-500 mireds)"""
    try:
        if light is None:
            return jsonify({"success": False, "message": "Light not initialized"}), 400
        
        success, data = run_async_read("color_temp")
        status_code = 200 if success else 400
        return jsonify({"success": success, "data": data if success else None, "message": data if not success else ""}), status_code
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/color', methods=['GET'])
def get_color():
    """Get current color (XY coordinates)"""
    try:
        if light is None:
            return jsonify({"success": False, "message": "Light not initialized"}), 400
        
        success, data = run_async_read("color")
        status_code = 200 if success else 400
        return jsonify({"success": success, "data": data if success else None, "message": data if not success else ""}), status_code
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/all', methods=['GET'])
def get_all():
    """Get all light properties at once"""
    try:
        if light is None:
            return jsonify({"success": False, "message": "Light not initialized"}), 400
        
        success, data = run_async_read("all")
        status_code = 200 if success else 400
        return jsonify({"success": success, "data": data if success else None, "message": data if not success else ""}), status_code
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/status', methods=['GET'])
def status():
    """Check if light is initialized"""
    if light is None:
        return jsonify({"initialized": False, "message": "Light not initialized"}), 200
    return jsonify({"initialized": True, "message": "Light ready"}), 200

def run_asyncio_loop():
    """Run asyncio event loop in a separate thread"""
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()

if __name__ == "__main__":
    # Start asyncio loop in background thread
    asyncio_thread = threading.Thread(daemon=True, target=run_asyncio_loop)
    asyncio_thread.start()
    
    print("Starting HTTP server on http://localhost:5000 or your computer's local ip on port 5000")
    print("First, POST to /init with your MAC address")
    app.run(debug=False, host='0.0.0.0', port=5000)
