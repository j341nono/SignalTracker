import tkinter as tk
from app.controller import WiFiVisualizer

if __name__ == '__main__':
    root = tk.Tk()
    app = WiFiVisualizer(root)
    root.mainloop()