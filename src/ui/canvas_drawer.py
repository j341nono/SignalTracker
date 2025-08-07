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
        self.display_strength = 0.0
        self.target_strength = 0.0
        self.display_color = "#000000"
        self.target_color = "#000000"   

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
        self.target_strength = strength
        self.target_color = color

        self.display_strength += (self.target_strength - self.display_strength) * 0.01

        def lerp_color(c1, c2, t):
            # from tkinter import colorchooser
            def hex_to_rgb(hex_color):
                hex_color = hex_color.lstrip("#")
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            def rgb_to_hex(rgb):
                return "#%02x%02x%02x" % rgb

            rgb1 = hex_to_rgb(c1)
            rgb2 = hex_to_rgb(c2)
            rgb_interp = tuple(int(a + (b - a) * t) for a, b in zip(rgb1, rgb2))
            return rgb_to_hex(rgb_interp)

        self.display_color = lerp_color(self.display_color, self.target_color, 0.1)

        self.canvas.config(bg='black')
        arc_angle = self.display_strength * 359.9
        arc_width = 10 + self.display_strength * 20

        self.canvas.create_arc(CENTER_X-100, CENTER_Y-100, CENTER_X+100, CENTER_Y+100,
            start=90, extent=359.9, outline="#333", style='arc', width=arc_width)

        if arc_angle > 0:
            self.canvas.create_arc(CENTER_X-100, CENTER_Y-100, CENTER_X+100, CENTER_Y+100,
                start=90, extent=-arc_angle, outline=self.display_color, style='arc', width=arc_width)

        self.canvas.create_text(CENTER_X, CENTER_Y+25, text=f"{rssi or '--'} dBm",
            font=("Arial", 22), fill=self.display_color)

        if random.random() < self.display_strength * 0.5:
            self.particles.append(Particle(self.display_strength, self.display_color))


    def update_particles(self):
        for p in reversed(self.particles):
            p.update()
            if p.is_alive():
                p.draw(self.canvas, self.root)
            else:
                self.particles.remove(p)