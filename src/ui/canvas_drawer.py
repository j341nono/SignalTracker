from config import CENTER_X, CENTER_Y, WARNING_RSSI
from wifi.util import rssi_to_strength_color
from ui.particle import Particle
import random

class CanvasDrawer:
    def __init__(self, canvas, root):
        self.canvas = canvas
        self.root = root
        self.warning_angle = 0
        self.particles = []

    def draw_warning(self):
        self.canvas.config(bg='#1a0024')
        self.warning_angle = (self.warning_angle + 0.3) % 360
        self.canvas.create_arc(CENTER_X-120, CENTER_Y-120, CENTER_X+120, CENTER_Y+120,
            start=self.warning_angle, extent=300, style='arc', outline="#8a2be2", width=6, dash=(15,20))
        self.canvas.create_text(CENTER_X, CENTER_Y-15, text="OFFLINE",
            font=("Arial Nova", 40, "bold"), fill="#e0e0e0")
        self.canvas.create_text(CENTER_X, CENTER_Y+30, text="Wi-Fi接続を確認してください",
            font=("Hiragino Sans", 16), fill="#a0a0a0")
        self.particles.clear()

    def draw_visuals(self, rssi):
        strength, color = rssi_to_strength_color(rssi)
        self.canvas.config(bg='black')
        arc_angle = strength * 359.9
        arc_width = 10 + strength * 20
        self.canvas.create_arc(CENTER_X-100, CENTER_Y-100, CENTER_X+100, CENTER_Y+100,
            start=90, extent=359.9, outline="#333", style='arc', width=arc_width)
        if arc_angle > 0:
            self.canvas.create_arc(CENTER_X-100, CENTER_Y-100, CENTER_X+100, CENTER_Y+100,
                start=90, extent=-arc_angle, outline=color, style='arc', width=arc_width)
        self.canvas.create_text(CENTER_X, CENTER_Y+25, text=f"{rssi or '--'} dBm",
            font=("Arial", 22), fill=color)
        if random.random() < strength * 0.5:
            self.particles.append(Particle(strength, color))

    def update_particles(self):
        for p in reversed(self.particles):
            p.update()
            if p.is_alive():
                p.draw(self.canvas, self.root)
            else:
                self.particles.remove(p)