import time
import psutil
import pygetwindow as gw
from pypresence import Presence
import requests
import logging


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

CLIENT_ID = "ID"  
NWS_API_URL = "https://api.weather.gov/alerts/active?event=Tornado%20Warning"


update_interval = 15  # seconds

def is_supercell_wx_running():
    """Check if Supercell Wx is running."""
    return any(process.info['name'].lower() == "supercell-wx.exe" for process in psutil.process_iter(attrs=['name']))

def get_radar_site_from_title():
    """Fetch radar site from Supercell Wx window title."""
    for window in gw.getWindowsWithTitle("Supercell Wx"):
        title = window.title
        if " - " in title:
            site = title.split(" - ")[-1].strip()
            return site if site.lower() != "discord" else "Unknown Radar Site"
    return "Unknown Radar Site"

def fetch_tornado_warnings():
    """Fetch active Tornado Warnings from NWS API."""
    try:
        response = requests.get(NWS_API_URL, timeout=45)
        response.raise_for_status()
        data = response.json()
        count = len(data.get("features", []))
        return f"Radar Indicated Tornado [{count}]" if count > 0 else ""
    except Exception as e:
        logger.error(f"Failed to fetch tornado warnings: {e}")
        return ""

def update_rpc(rpc, radar_site):
    """Update Discord Rich Presence."""
    tornado_warning = fetch_tornado_warnings()
    status_message = "Weather Monitoring"

    if tornado_warning:
        status_message = "Tornado Warning Issued"

    try:
        rpc.update(
            details=f"Watching Radar for {radar_site}",
            state=status_message,
            large_image="supercell_wx",
            large_text="Supercell WX",
            party_size=[1, 1]  # MAX IS 100 DUE TO RPC API is [1, 100] is MAX
        )
    except Exception as e:
        logger.error(f"Failed to update RPC: {e}")

def main():
    rpc = Presence(CLIENT_ID)

    while True:
        if is_supercell_wx_running():
            try:
                rpc.connect()
                logger.info("✅ Connected to Discord RPC.")
                break
            except Exception as e:
                logger.error(f"❌ Failed to connect to Discord RPC. Retrying... Error: {e}")
                time.sleep(15)
        else:
            logger.info("⚠️ Supercell Wx not running. Waiting...")
            time.sleep(15)

    while True:
        if is_supercell_wx_running():
            radar_site = get_radar_site_from_title()
            update_rpc(rpc, radar_site)
        else:
            logger.info("⚠️ Supercell Wx is not running. Waiting...")
            rpc.clear()

        time.sleep(update_interval)

if __name__ == "__main__":
    main()