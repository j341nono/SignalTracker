import colorsys
from config import STRONG_RSSI, WEAK_RSSI

def rssi_to_strength_color(rssi):
    if rssi is None:
        return 0.0, "#555555"
    rssi_clamped = max(WEAK_RSSI, min(rssi, STRONG_RSSI))
    strength = (rssi_clamped - WEAK_RSSI) / (STRONG_RSSI - WEAK_RSSI)
    hue = strength * 0.33
    rgb = colorsys.hsv_to_rgb(hue, 1, 1)
    return strength, f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"
