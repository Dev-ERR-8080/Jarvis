import subprocess
import screen_brightness_control  as sbc
import platform
import os
import webbrowser
import pywhatkit
import requests
import psutil
import platform
from pathlib import Path
import os
import datetime
from dotenv import load_dotenv
from PIL import ImageGrab



load_dotenv()

    
APPS = {
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "notepad": "notepad.exe",
        "vscode": r"C:\Users\reddy\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        "spotify": r"C:\Users\reddy\AppData\Local\Microsoft\WindowsApps\Spotify.exe",
        "calculator": "calc.exe",
        "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
        "word": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Word.lnk",
        "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
        "teams": r"C:\Users\reddy\AppData\Local\Microsoft\Teams\current\Teams.exe",
        "whatsapp": r"C:\Users\reddy\AppData\Local\WhatsApp\WhatsApp.lnk",
        "quickshare": r"C:\ProgramData\Microsoft\Windows\Start Menu\Quick Share.lnk",
        "notion": r"C:\Users\reddy\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Notion.lnk",
    }


def play_youtube(query):
    pywhatkit.playonyt(query)
    
def get_time():
    return f"The time is {datetime.datetime.now().strftime('%H:%M:%S')}"

def get_date():
    return f"Today's date is {datetime.date.today().strftime('%B %d, %Y')}"

def take_screenshot(filename=None):
    """Captures a screenshot of the entire screen."""
    try:
        # Create a 'screenshots' folder if it doesn't exist
        save_path = os.path.join(os.path.expanduser('~'), 'onedrive/pictures')
        os.makedirs(save_path, exist_ok=True)

        # Generate a default filename if none is provided
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"screenshots/screenshot_{timestamp}.png"

        # Capture the screenshot and save it
        full_path = os.path.join(save_path, filename)
        
        screenshot = ImageGrab.grab()
        screenshot.save(full_path)
        return f"Screenshot saved to {filename}"
    except Exception as e:
        return f"Failed to take a screenshot: {e}"


def get_battery_status():
    """Returns the current battery percentage and status."""
    try:
        battery = psutil.sensors_battery()
        if battery:
            percent = battery.percent
            is_charging = "Charging" if battery.power_plugged else "Discharging"
            return f"Battery is at {percent}% and is {is_charging}."
        else:
            return "Could not retrieve battery status."
    except Exception as e:
        return f"Failed to get battery status: {e}"
    
def toggle_airplane_mode():
    """Toggles Airplane Mode by enabling/disabling the Wi-Fi adapter."""
    try:
        if platform.system() != 'Windows':
            return "This command is only supported on Windows."

        # Command to get the current operational status of the Wi-Fi adapter.
        get_status_cmd = "Get-NetAdapter -Name 'Wi-Fi' | Select-Object -ExpandProperty InterfaceStatus"
        result = subprocess.run(['powershell', '-Command', get_status_cmd], capture_output=True, text=True)
        
        # Check if the status is 'Up', which means the Wi-Fi is enabled.
        # This is a more reliable check than looking for a specific word in the description.
        is_up = "Up" in result.stdout.strip()
        
        # PowerShell command to toggle the Wi-Fi adapter based on its current status.
        # 'Disabled' corresponds to 'Airplane Mode On' for the Wi-Fi adapter.
        toggle_cmd = "Disable-NetAdapter -Name 'Wi-Fi' -Confirm:$false" if is_up else "Enable-NetAdapter -Name 'Wi-Fi' -Confirm:$false"
        subprocess.run(['powershell', '-Command', toggle_cmd], capture_output=True, text=True)
        
        # Return a response based on the action taken.
        return f"Airplane Mode is now {'on' if is_up else 'off'}."

    except Exception as e:
        # Provide a more specific error message if the Wi-Fi adapter isn't found.
        if "No MSFT_NetAdapter objects found" in str(e):
            return "Could not find a Wi-Fi adapter. Please check your network settings."
        return f"Failed to toggle Airplane Mode: {e}"

def set_brightness(level):
    try:
        sbc.set_brightness(level)
        return f"Brightness set to {level}%."
    except Exception as e:
        return f"Failed to set brightness using screen-brightness-control: {e}"

def run_shell(command):
    return os.system(command) 

def run_actions(action):
    action = action.lower().strip()
    if action in ("shutdown", "turn off", "power off"):
        return run_shell("shutdown /s /t 1")
    if action in ("restart", "reboot"):
        return run_shell("shutdown /r /t 1")
    if action in ("logout", "sign out"):
        return run_shell("shutdown /l")
    if action in ("sleep", "hibernate"):
        return run_shell("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    if action in ("lock", "lock screen"):
        return run_shell("rundll32.exe user32.dll,LockWorkStation")
    return f"Unknown system action: {action}"


def get_weather(location=None):

    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    if not OPENWEATHER_API_KEY:
        return "Weather API key not found. Set OPENWEATHER_API_KEY environment variable to use weather command."
    if not location:
        location = "auto:ip"  # openweathermap supports this only via other endpoints; keep simple
    # Simple approach: use city name
    q = location if location else "London"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={q}&appid={OPENWEATHER_API_KEY}&units=metric"
    resp = requests.get(url, timeout=8)
    if resp.status_code != 200:
        return f"Weather service returned {resp.status_code}"
    data = resp.json()
    return {
        "name": data.get("name", q),
        "temp_c": data["main"]["temp"],
        "weather_desc": data["weather"][0]["description"]
    }

def open_app(app_name):
    
    name = app_name.lower().strip()
    # try direct mapping
    if name in APPS:
        exe = APPS[name]
        try:
            os.startfile(exe)
            return f"Opening {name}"
        except Exception as e:
            return f"Failed to open {name}: {e}"
    # try start command (Windows)
    try:
        os.system(f"start {name}")
        return f"Attempted to open {name}"
    except Exception as e:
        return f"Could not open {name}: {e}"

def search_web(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Searching for {query}"

def get_system_stats():
    cpu = psutil.cpu_percent(interval=1)
    mem = round(psutil.virtual_memory().percent, 1)
    return cpu, mem


