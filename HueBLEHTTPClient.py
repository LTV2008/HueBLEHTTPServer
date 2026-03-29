import requests
import json
import sys
from typing import Optional, Dict, Any

class HueLightClient:
    def __init__(self, base_url: str):
        """Initialize the client with the server base URL"""
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to the server"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=10)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=10)
            else:
                return {"success": False, "message": "Invalid HTTP method"}
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.ConnectionError:
            return {"success": False, "message": f"Connection error: Cannot reach {self.base_url}"}
        except requests.exceptions.Timeout:
            return {"success": False, "message": "Request timeout"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "message": f"Request error: {str(e)}"}
        except json.JSONDecodeError:
            return {"success": False, "message": "Invalid response from server"}
    
    def initialize(self, mac_address: str) -> bool:
        """Initialize light connection"""
        print(f"Initializing light with MAC address: {mac_address}...")
        response = self._make_request('POST', '/init', {'mac_address': mac_address})
        
        if response.get('success'):
            print(f"✓ {response.get('message')}")
            return True
        else:
            print(f"✗ {response.get('message')}")
            return False
    
    def set_power(self, state: bool) -> bool:
        """Turn light on/off"""
        state_str = "on" if state else "off"
        print(f"Turning light {state_str}...")
        response = self._make_request('POST', '/power', {'state': state})
        
        if response.get('success'):
            print(f"✓ {response.get('message')}")
            return True
        else:
            print(f"✗ {response.get('message')}")
            return False
    
    def set_brightness(self, value: int) -> bool:
        """Set brightness (0-255)"""
        if not (0 <= value <= 255):
            print("✗ Brightness must be between 0 and 255")
            return False
        
        print(f"Setting brightness to {value}...")
        response = self._make_request('POST', '/brightness', {'value': value})
        
        if response.get('success'):
            print(f"✓ {response.get('message')}")
            return True
        else:
            print(f"✗ {response.get('message')}")
            return False
    
    def set_color_temp(self, value: int) -> bool:
        """Set color temperature (153-500 mireds)"""
        if not (153 <= value <= 500):
            print("✗ Color temperature must be between 153 and 500 mireds")
            return False
        
        print(f"Setting color temperature to {value}...")
        response = self._make_request('POST', '/color_temp', {'value': value})
        
        if response.get('success'):
            print(f"✓ {response.get('message')}")
            return True
        else:
            print(f"✗ {response.get('message')}")
            return False
    
    def set_color(self, x: float, y: float) -> bool:
        """Set color using XY coordinates (0.0-1.0)"""
        if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
            print("✗ X and Y values must be between 0.0 and 1.0")
            return False
        
        print(f"Setting color to X:{x}, Y:{y}...")
        response = self._make_request('POST', '/color', {'x': x, 'y': y})
        
        if response.get('success'):
            print(f"✓ {response.get('message')}")
            return True
        else:
            print(f"✗ {response.get('message')}")
            return False
    
    def get_power(self) -> Optional[bool]:
        """Get current power state"""
        response = self._make_request('GET', '/power')
        
        if response.get('success'):
            data = response.get('data', {})
            power = data.get('power')
            state_str = "on" if power else "off"
            print(f"Power: {state_str}")
            return power
        else:
            print(f"✗ {response.get('message')}")
            return None
    
    def get_brightness(self) -> Optional[int]:
        """Get current brightness"""
        response = self._make_request('GET', '/brightness')
        
        if response.get('success'):
            data = response.get('data', {})
            brightness = data.get('brightness')
            print(f"Brightness: {brightness}")
            return brightness
        else:
            print(f"✗ {response.get('message')}")
            return None
    
    def get_color_temp(self) -> Optional[int]:
        """Get current color temperature"""
        response = self._make_request('GET', '/color_temp')
        
        if response.get('success'):
            data = response.get('data', {})
            temp = data.get('color_temperature')
            print(f"Color temperature: {temp} mireds")
            return temp
        else:
            print(f"✗ {response.get('message')}")
            return None
    
    def get_color(self) -> Optional[tuple]:
        """Get current color"""
        response = self._make_request('GET', '/color')
        
        if response.get('success'):
            data = response.get('data', {})
            x = data.get('x')
            y = data.get('y')
            print(f"Color: X:{x}, Y:{y}")
            return (x, y)
        else:
            print(f"✗ {response.get('message')}")
            return None
    
    def get_all(self) -> Optional[Dict]:
        """Get all light properties"""
        response = self._make_request('GET', '/all')
        
        if response.get('success'):
            data = response.get('data', {})
            power_str = "on" if data.get('power') else "off"
            print(f"\n=== Light Status ===")
            print(f"Power: {power_str}")
            print(f"Brightness: {data.get('brightness')}")
            print(f"Color Temperature: {data.get('color_temperature')} mireds")
            color = data.get('color', {})
            print(f"Color: X:{color.get('x')}, Y:{color.get('y')}")
            print(f"==================\n")
            return data
        else:
            print(f"✗ {response.get('message')}")
            return None
    
    def check_status(self) -> bool:
        """Check if light is initialized"""
        response = self._make_request('GET', '/status')
        initialized = response.get('initialized', False)
        status_str = "initialized" if initialized else "not initialized"
        print(f"Light status: {status_str}")
        return initialized


def print_help():
    """Print help message"""
    help_text = """
=== Hue Light CLI Client ===

Usage: python3 HueBLEHTTPClient.py <command> [options]

Commands:
  init <mac_address>          Initialize light with MAC address
  on                          Turn light on
  off                         Turn light off
  brightness <0-255>          Set brightness
  temp <153-500>              Set color temperature (mireds)
  color <x> <y>               Set color (XY coordinates, 0.0-1.0)
  get-power                   Get current power state
  get-brightness              Get current brightness
  get-temp                    Get current color temperature
  get-color                   Get current color
  get-all                     Get all properties
  status                      Check if light is initialized
  help                        Show this help message

Examples:
  python3 HueBLEHTTPClient.py init AA:BB:CC:DD:EE:FF
  python3 HueBLEHTTPClient.py on
  python3 HueBLEHTTPClient.py brightness 200
  python3 HueBLEHTTPClient.py temp 250
  python3 HueBLEHTTPClient.py color 0.5 0.3
  python3 HueBLEHTTPClient.py get-all

Note: Set the SERVER_URL variable to match your server address
(default: http://localhost:5000)
    """
    print(help_text)


def main():
    # Configuration - change this to your server address
    SERVER_URL = "http://localhost:5000"
    
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    client = HueLightClient(SERVER_URL)
    
    try:
        if command == 'help':
            print_help()
        
        elif command == 'init':
            if len(sys.argv) < 3:
                print("✗ MAC address required: python3 HueBLEHTTPClient.py init <mac_address>")
                sys.exit(1)
            mac_address = sys.argv[2]
            client.initialize(mac_address)
        
        elif command == 'on':
            client.set_power(True)
        
        elif command == 'off':
            client.set_power(False)
        
        elif command == 'brightness':
            if len(sys.argv) < 3:
                print("✗ Brightness value required: python3 HueBLEHTTPClient.py brightness <0-255>")
                sys.exit(1)
            brightness = int(sys.argv[2])
            client.set_brightness(brightness)
        
        elif command == 'temp':
            if len(sys.argv) < 3:
                print("✗ Temperature value required: python3 HueBLEHTTPClient.py temp <153-500>")
                sys.exit(1)
            temp = int(sys.argv[2])
            client.set_color_temp(temp)
        
        elif command == 'color':
            if len(sys.argv) < 4:
                print("✗ X and Y coordinates required: python3 HueBLEHTTPClient.py color <x> <y>")
                sys.exit(1)
            x = float(sys.argv[2])
            y = float(sys.argv[3])
            client.set_color(x, y)
        
        elif command == 'get-power':
            client.get_power()
        
        elif command == 'get-brightness':
            client.get_brightness()
        
        elif command == 'get-temp':
            client.get_color_temp()
        
        elif command == 'get-color':
            client.get_color()
        
        elif command == 'get-all':
            client.get_all()
        
        elif command == 'status':
            client.check_status()
        
        else:
            print(f"✗ Unknown command: {command}")
            print("Use 'python3 HueBLEHTTPClient.py help' for available commands")
            sys.exit(1)
    
    except ValueError as e:
        print(f"✗ Invalid argument: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n✗ Interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    main()


