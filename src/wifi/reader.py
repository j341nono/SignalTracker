import subprocess
import re
from config import AIRPORT_PATH

def _run_command(command, timeout=10):
    return subprocess.run(
        command, capture_output=True, text=True, check=False,
        encoding='utf-8', timeout=timeout
    )

def get_wifi_details_with_corewlan():
    import objc
    import CoreWLAN

    client = CoreWLAN.CWWiFiClient.sharedWiFiClient()
    interfaces = client.interfaces()
    if not interfaces:
        raise RuntimeError("No Wi-Fi interfaces found")

    for iface in interfaces:
        ssid = iface.ssid()
        rssi = iface.rssiValue()
        if rssi is not None:
            return ssid or "Unknown", rssi
    return None, None

def get_wifi_details_multiple_methods():
    try:
        ssid, rssi = get_wifi_details_with_corewlan()
        if ssid and rssi is not None:
            return ssid, rssi
    except Exception as e:
        print(f"CoreWLAN失敗: {e}")
    return None, None