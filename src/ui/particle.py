import math
import random
from config import CENTER_X, CENTER_Y

class Particle:
    def __init__(self, strength, color):
        angle = random.uniform(0, 2 * math.pi)
        offset = random.uniform(40, 100)
        self.x = CENTER_X + math.cos(angle) * offset
        self.y = CENTER_Y + math.sin(angle) * offset
        self.vx = math.cos(angle) * random.uniform(0.1, 0.5) * (0.5 + strength)
        self.vy = math.sin(angle) * random.uniform(0.1, 0.5) * (0.5 + strength)
        self.radius = random.uniform(1.5, 3.0)
        self.life = self.max_life = random.randint(100, 160)
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.98
        self.vy *= 0.98
        self.radius *= 0.99
        self.life -= 1

    def is_alive(self):
        return self.life > 0

    def draw(self, canvas, root):
        alpha = (self.life / self.max_life) ** 2
        if alpha <= 0.01:
            return
        try:
            r, g, b = root.winfo_rgb(self.color)
            faded_color = f"#{int(r / 256 * alpha):02x}{int(g / 256 * alpha):02x}{int(b / 256 * alpha):02x}"
            canvas.create_oval(
                self.x - self.radius, self.y - self.radius,
                self.x + self.radius, self.y + self.radius,
                fill=faded_color, outline=""
            )
        except:
            pass
