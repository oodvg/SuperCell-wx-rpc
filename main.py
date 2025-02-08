import time
import psutil
import pygetwindow as gw
from pypresence import Presence

CLIENT_ID = "ID"  


last_radar_site = None
start_time = None


weather_conditions = {
    "Tornado": "🌪️ Tornado Warning",
    "Thunderstorm": "⛈️ Severe Thunderstorm",
    "Blizzard": "❄️ Blizzard Warning",
    "Flood": "🌊 Flood Warning",
    "Hurricane": "🌀 Hurricane Warning",
    "Winter Storm": "❄️ Winter Storm Warning",
    "High Wind": "💨 High Wind Advisory"
}

def is_supercell_wx_running():
    """Check if Supercell Wx is running."""
    for process in psutil.process_iter(attrs=['name']):
        if "supercell-wx.exe" in process.info['name']:
            return True
    return False

def get_radar_site_from_title():
    """Fetch radar site and possible weather alert from Supercell Wx window title."""
    try:
        for window in gw.getWindowsWithTitle("Supercell Wx"):
            title = window.title
            
            if "Supercell Wx -" in title:
                radar_info = title.split("Supercell Wx -")[1].strip()

                if radar_info.lower() == "discord":
                    return "Unknown Radar Site", "Clear Skies ☀️"

                weather_alert = "Clear Skies ☀️"
                for key, alert_text in weather_conditions.items():
                    if key in radar_info:
                        weather_alert = alert_text
                        radar_info = radar_info.replace(key, "").strip()

                return radar_info, weather_alert
        return "Unknown Radar Site", "Clear Skies ☀️"
    except:
        return "Unknown Radar Site", "Clear Skies ☀️"

def main():
    global last_radar_site, start_time
    rpc = Presence(CLIENT_ID)

    try:
        rpc.connect()
        print("✅ Connected to Discord RPC.")
    except Exception:
        print("❌ Failed to connect to Discord RPC.")
        return

    while True:
        if is_supercell_wx_running():
            radar_site, weather_alert = get_radar_site_from_title()

           
            if radar_site != last_radar_site:
                last_radar_site = radar_site
                start_time = int(time.time())

          
            rpc.update(
                details=f"Watching Radar for {radar_site}",
                state=weather_alert,
                start=start_time,
                large_image="supercell_wx",
                large_text="Supercell WX"
            )
        else:
            rpc.clear()

        time.sleep(15)

if __name__ == "__main__":
    main()
