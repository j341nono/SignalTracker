import tkinter as tk
import queue
import threading
from config import WIDTH, HEIGHT, WARNING_RSSI, UPDATE_INTERVAL_MS, ANIMATION_FPS
from wifi.reader import get_wifi_details_multiple_methods
from wifi.util import rssi_to_strength_color
from ui.canvas_drawer import CanvasDrawer

class WiFiVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Wi-Fi Signal Visualizer")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.canvas = tk.Canvas(root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.drawer = CanvasDrawer(self.canvas, root)

        self.rssi = None
        self.target_strength = 0.0
        self.displayed_strength = 0.0
        self.wifi_data_queue = queue.Queue()

        self.start_wifi_thread()
        self.process_wifi_queue()
        self.animate()

    def start_wifi_thread(self):
        thread = threading.Thread(target=self._wifi_worker, daemon=True)
        thread.start()

    def _wifi_worker(self):
        import time
        while True:
            ssid, rssi = get_wifi_details_multiple_methods()
            self.wifi_data_queue.put((ssid, rssi))
            time.sleep(UPDATE_INTERVAL_MS / 1000.0)

    def process_wifi_queue(self):
        try:
            while not self.wifi_data_queue.empty():
                _, new_rssi = self.wifi_data_queue.get_nowait()
                if new_rssi != self.rssi:
                    self.rssi = new_rssi
                    self.target_strength, _ = rssi_to_strength_color(self.rssi)
        except queue.Empty:
            pass
        self.root.after(100, self.process_wifi_queue)

    def animate(self):
        self.displayed_strength += (self.target_strength - self.displayed_strength) * 0.04
        self.canvas.delete("all")
        if self.rssi is None or self.rssi < WARNING_RSSI:
            self.drawer.draw_warning()
        else:
            self.drawer.draw_visuals(self.rssi)
        self.drawer.update_particles()
        self.root.after(int(1000 / ANIMATION_FPS), self.animate)