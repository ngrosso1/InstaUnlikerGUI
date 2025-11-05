import tkinter as tk
import colorsys

class CylindricalGradientProgressBar(tk.Canvas):
    def __init__(self, master=None, width=600, height=20, bg_color='#FFFFFF', **kwargs):
        # Determine background color for progress bar based on theme
        if bg_color == '#1E1E1E':
            # Dark theme - Canvas should match the app background
            canvas_bg = bg_color  # Use the same bg_color instead of '#2D2D2D'
            progress_bg = '#404040'
        else:
            # Light theme
            canvas_bg = bg_color  # Use the same bg_color
            progress_bg = '#F0F0F0'
        
        super().__init__(master, width=width, height=height, bg=canvas_bg, highlightthickness=0, **kwargs)
        
        self.width = width
        self.height = height
        self.progress = 0
        self.gradient_colors = ['#F58529', '#DD2A7B']
        self.radius = height // 2
        self.progress_bg = progress_bg
        self._draw_cylindrical_progress()
    
    def _draw_cylindrical_progress(self):
        self.delete("all")
        
        # Draw a subtle background track for the entire width
        self.create_rounded_rectangle(0, 0, self.width, self.height, radius=self.radius, fill=self.progress_bg, outline='')
        
        # Calculate and draw the actual progress
        progress_width = int((self.progress / 100) * self.width)
        if progress_width > 0:
            self._draw_gradient_progress(0, 0, progress_width, self.height, self.radius)

    def _draw_gradient_progress(self, x1, y1, x2, y2, radius):
        steps = 50
        for i in range(steps):
            ratio = i / steps
            color = self._interpolate_color("#F58529", "#DD2A7B", ratio)
            x_start = x1 + (x2 - x1) * (i / steps)
            x_end = x1 + (x2 - x1) * ((i + 1) / steps)
            
            if x_start < radius:
                self.create_oval(x_start, y1, x_start + 2 * radius, y2, fill=color, outline=color)
            elif x_end > x2 - radius:
                self.create_oval(x_end - 2 * radius, y1, x_end, y2, fill=color, outline=color)
            else:
                self.create_rectangle(x_start, y1, x_end, y2, fill=color, outline=color)

    def _interpolate_color(self, color1, color2, ratio):
        c1 = [int(color1[i:i+2], 16) for i in (1, 3, 5)]
        c2 = [int(color2[i:i+2], 16) for i in (1, 3, 5)]
        blended = [int(c1[j] + (c2[j] - c1[j]) * ratio) for j in range(3)]
        return f'#{blended[0]:02x}{blended[1]:02x}{blended[2]:02x}'

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=10, **kwargs):
        self.create_arc(x1, y1, x1 + 2 * radius, y1 + 2 * radius, start=90, extent=90, **kwargs)
        self.create_arc(x2 - 2 * radius, y1, x2, y1 + 2 * radius, start=0, extent=90, **kwargs)
        self.create_arc(x1, y2 - 2 * radius, x1 + 2 * radius, y2, start=180, extent=90, **kwargs)
        self.create_arc(x2 - 2 * radius, y2 - 2 * radius, x2, y2, start=270, extent=90, **kwargs)
        self.create_rectangle(x1 + radius, y1, x2 - radius, y2, **kwargs)

    def update_progress(self, value):
        self.progress = max(0, min(100, value))
        self._draw_cylindrical_progress()
        self.update_idletasks()