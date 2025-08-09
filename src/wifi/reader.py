import subprocess
import re
from config import AIRPORT_PATH

def _run_command(command, timeout=10):
    return subprocess.run(
        command, capture_output=True, text=True, check=False,
        encoding='utf-8', timeout=timeout
    )

def get_wifi_details_with_corewlan():
    from CoreWLAN import CWInterface
    interfaces = CWInterface.interface()
    if not interfaces:
        raise RuntimeError("No Wi-Fi interfaces found")

    interface_name = interfaces.interfaceName()
    # ssid = interfaces.ssid()
    try:
        cmd = [
            "networksetup",
            "-listpreferredwirelessnetworks",
            interface_name
        ]
        output = subprocess.check_output(cmd, text=True)
        lines = output.strip().split("\n")
        if len(lines) >= 2:
            ssid = lines[1].strip()
    except Exception:
        ssid = None
    rssi = interfaces.rssiValue()

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


def debug():
    from CoreWLAN import CWInterface
    interface = CWInterface.interface()
    rssi = interface.rssiValue()                   # 電波強度 (dBm)
    ssid = interface.ssid()                        # ネットワーク名（SSID）
    noise = interface.noiseMeasurement()           # ノイズレベル (dBm)
    transmit_rate = interface.transmitRate()       # 通信速度 (Mbps)
    interface_name = interface.interfaceName()     # インターフェース名（例: "en0"）
    country_code = interface.countryCode()         # 国コード（例: "JP"）
    bssid = interface.bssid()                      # 接続中のAPのMACアドレス
    config = interface.configuration()

    print("===== Wi-Fi 情報 =====")
    print(f"Interface: {interface_name}")
    print(f"SSID: {ssid}")
    print(f"BSSID: {bssid}")
    print(f"RSSI: {rssi} dBm")
    print(f"Noise: {noise} dBm")
    print(f"Transmit Rate: {transmit_rate} Mbps")
    print(f"Country Code: {country_code}")
    print(f"conf: {config}")


    # print(f"Wi-FiのRSSI: {get_rssi()} dBm")

def debug_2():
    from CoreWLAN import CWInterface
    interface = CWInterface.interface()
    ssid_data = interface.ssidData()
    if ssid_data is not None:
        ssid = ssid_data.bytes().tobytes().decode("utf-8")
    else:
        ssid = None

    print(f"SSID: {ssid}")


if __name__ == "__main__":
    output = debug()
    # output = debug_2()