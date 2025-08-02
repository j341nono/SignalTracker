import tkinter as tk
import subprocess
import math
import random
import colorsys
import threading
import queue
import re

WIDTH, HEIGHT = 600, 600
CENTER_X, CENTER_Y = WIDTH / 2, HEIGHT / 2
STRONG_RSSI = -30
WEAK_RSSI = -90
WARNING_RSSI = -85
UPDATE_INTERVAL_MS = 2000
ANIMATION_FPS = 60

AIRPORT_PATH = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"

class WiFiVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Wi-Fi Signal Visualizer")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.configure(bg='black')
        self.canvas = tk.Canvas(root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.ssid = None
        self.rssi = None
        self.target_strength = 0.0
        self.displayed_strength = 0.0
        self.particles = []
        self.warning_angle = 0
        self.wifi_data_queue = queue.Queue()
        self.start_wifi_update_thread()
        self.process_wifi_queue()
        self.animate()

    def start_wifi_update_thread(self):
        thread = threading.Thread(target=self._wifi_update_worker, daemon=True)
        thread.start()

    def _wifi_update_worker(self):
        import time
        while True:
            ssid, rssi = self.get_wifi_details_multiple_methods()
            self.wifi_data_queue.put((ssid, rssi))
            time.sleep(UPDATE_INTERVAL_MS / 1000.0)

    def process_wifi_queue(self):
        try:
            new_ssid, new_rssi = None, None
            while not self.wifi_data_queue.empty():
                new_ssid, new_rssi = self.wifi_data_queue.get_nowait()
            if new_ssid is not None:
                if self.ssid != new_ssid or self.rssi != new_rssi:
                    print(f"Wi-Fi状態更新: SSID={new_ssid}, RSSI={new_rssi}")
                    self.ssid = new_ssid
                    self.rssi = new_rssi
                    self.target_strength, _ = self.rssi_to_strength_color(self.rssi)
        except queue.Empty:
            pass
        self.root.after(100, self.process_wifi_queue)

    def get_wifi_details_with_corewlan(self):
        import objc
        import CoreWLAN

        print("CoreWLANにアクセスします")
        client = CoreWLAN.CWWiFiClient.sharedWiFiClient()
        interfaces = client.interfaces()

        print(f"検出されたインターフェース: {interfaces}")

        if not interfaces:
            raise RuntimeError("No Wi-Fi interfaces found")

        for iface in interfaces:
            print(f"インターフェース: {iface.interfaceName()}")
            ssid = iface.ssid()
            rssi = iface.rssiValue()
            print(f"SSID: {ssid}, RSSI: {rssi}")
            
            # SSIDがNoneでもRSSIがあれば使う
            if rssi is not None:
                return ssid or "Unknown", rssi

        raise RuntimeError("No usable Wi-Fi interface found")



    def get_wifi_details_multiple_methods(self):
        try:
            ssid, rssi = self.get_wifi_details_with_corewlan()
            if ssid and rssi is not None:
                # print(f"CoreWLANから取得成功: SSID={ssid}, RSSI={rssi}")
                return ssid, rssi
        except Exception as e:
            print(f"CoreWLAN失敗: {e}")
        
        print("CoreWLANから取得できなかったため、代替手段は未使用です。")
        return None, None


    def _run_command(self, command, timeout=10):
        return subprocess.run(
            command, capture_output=True, text=True, check=False,
            encoding='utf-8', timeout=timeout
        )

    def method_airport(self):
        """【修正】airportコマンドの正しいフルパスを使用する"""
        process = self._run_command([AIRPORT_PATH, "-I"])
        if process.returncode != 0: return None, None
        output = process.stdout
        ssid_match = re.search(r'^\s*SSID: (.+)$', output, re.MULTILINE)
        rssi_match = re.search(r'^\s*agrCtlRSSI: (.+)$', output, re.MULTILINE)
        if ssid_match and rssi_match:
            ssid = ssid_match.group(1).strip()
            rssi_str = rssi_match.group(1).strip()
            if rssi_str.lstrip('-').isdigit():
                return ssid, int(rssi_str)
        return None, None

    def method_system_profiler(self):
        """最後の手段としてsystem_profilerから情報を解析する"""
        process = self._run_command(["system_profiler", "SPNetworkDataType"], timeout=15)
        if process.returncode != 0: return None, None
        output = process.stdout
        ssid, rssi = None, None
        
        # Wi-Fiインターフェースのセクションを探す
        wifi_sections = re.finditer(r'Wi-Fi:\s+Hardware Port: Wi-Fi, Device: en\d(.*?)(?=^\w)', output, re.DOTALL | re.MULTILINE)
        for section in wifi_sections:
            section_text = section.group(1)
            # 現在接続中のネットワーク情報を探す
            current_network_match = re.search(r'Current Network Information:(.+?)(?=^\s{4}\w)', section_text, re.DOTALL | re.MULTILINE)
            if current_network_match:
                network_info = current_network_match.group(1)
                ssid_match = re.search(r'^\s*([^\n]+):', network_info.strip(), re.MULTILINE)
                if ssid_match:
                    ssid = ssid_match.group(1).strip()
                rssi_match = re.search(r'Signal / Noise: ([-–\d]+) dBm', network_info)
                if rssi_match:
                    rssi_str = rssi_match.group(1).replace('–', '-')
                    if rssi_str.lstrip('-').isdigit():
                        rssi = int(rssi_str)
                # 両方見つかったら終了
                if ssid and rssi:
                    return ssid, rssi
        return ssid, rssi

    # --- アニメーション関連（変更なし） ---
    def rssi_to_strength_color(self, rssi):
        if rssi is None: return 0.0, "#555555"
        rssi_clamped = max(WEAK_RSSI, min(rssi, STRONG_RSSI))
        strength = (rssi_clamped - WEAK_RSSI) / (STRONG_RSSI - WEAK_RSSI)
        hue = strength * 0.33
        rgb = colorsys.hsv_to_rgb(hue, 1, 1)
        return strength, f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"

    def create_particles(self, strength, color):
        if strength < 0.1:
            return
        particle_count = int(strength * strength * 15)
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            # 中心から少し外れたところから始める（中心を避ける）
            offset = random.uniform(40, 100)
            start_x = CENTER_X + math.cos(angle) * offset
            start_y = CENTER_Y + math.sin(angle) * offset

            speed = random.uniform(0.1, 0.5) * (0.5 + strength)  # ゆっくり
            radius = random.uniform(1.5, 3.0)
            life = random.randint(100, 160)

            self.particles.append({
                'x': start_x,
                'y': start_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'radius': radius,
                'life': life,
                'max_life': life,
                'color': color
            })


    def draw_warning(self):
        self.canvas.config(bg='#1a0024')
        self.warning_angle = (self.warning_angle + 0.3) % 360
        self.canvas.create_arc(CENTER_X-120, CENTER_Y-120, CENTER_X+120, CENTER_Y+120, start=self.warning_angle, extent=300, style=tk.ARC, outline="#8a2be2", width=6, dash=(15, 20))
        self.canvas.create_arc(CENTER_X-90, CENTER_Y-90, CENTER_X+90, CENTER_Y+90, start=-self.warning_angle*1.2, extent=300, style=tk.ARC, outline="#4b0082", width=3, dash=(5, 10))
        self.canvas.create_text(CENTER_X, CENTER_Y-15, text="OFFLINE", font=("Arial Nova", 40, "bold"), fill="#e0e0e0")
        self.canvas.create_text(CENTER_X, CENTER_Y+30, text="Wi-Fi接続を確認してください", font=("Hiragino Sans", 16), fill="#a0a0a0")

    def draw_visuals(self, strength, color):
        self.canvas.config(bg='black')
        arc_angle = strength * 359.9
        arc_width = 10 + strength * 20
        self.canvas.create_arc(CENTER_X-100, CENTER_Y-100, CENTER_X+100, CENTER_Y+100, start=90, extent=359.9, outline="#333", style=tk.ARC, width=arc_width)
        if arc_angle > 0:
            self.canvas.create_arc(CENTER_X-100, CENTER_Y-100, CENTER_X+100, CENTER_Y+100, start=90, extent=-arc_angle, outline=color, style=tk.ARC, width=arc_width)
        
        # SSID表示を非表示に
        # self.canvas.create_text(CENTER_X, CENTER_Y-20, text=self.ssid or "N/A", font=("Arial", 28, "bold"), fill="white")
        
        self.canvas.create_text(CENTER_X, CENTER_Y+25, text=f"{self.rssi or '--'} dBm", font=("Arial", 22), fill=color)
        if random.random() < strength * 0.5:
            self.create_particles(strength, color)


    def animate(self):
        self.displayed_strength += (self.target_strength - self.displayed_strength) * 0.04
        self.canvas.delete("all")
        if self.rssi is None or self.rssi < WARNING_RSSI:
            if self.rssi is None: self.target_strength = 0.0
            self.draw_warning()
            self.particles.clear()
        else:
            _, color = self.rssi_to_strength_color(self.rssi)
            self.draw_visuals(self.displayed_strength, color)
        for p in reversed(self.particles):
            p['x'] += p['vx']; p['y'] += p['vy']; p['life'] -= 1
            if p['life'] <= 0: self.particles.remove(p); continue
            alpha = p['life'] / p['max_life']
            try:
                r, g, b = self.root.winfo_rgb(p['color'])
                faded_color = f"#{int(r/256*alpha):02x}{int(g/256*alpha):02x}{int(b/256*alpha):02x}"
                self.canvas.create_oval(p['x']-p['radius'], p['y']-p['radius'], p['x']+p['radius'], p['y']+p['radius'], fill=faded_color, outline="")
            except tk.TclError:
                pass # 色がtkで解釈できない形式の場合のエラーを無視
        self.root.after(int(1000/ANIMATION_FPS), self.animate)

if __name__ == '__main__':
    root = tk.Tk()
    app = WiFiVisualizer(root)
    root.mainloop()