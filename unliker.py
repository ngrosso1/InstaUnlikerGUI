import tkinter as tk
from tkinter import ttk, messagebox
import codecs
import json
import os
from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired, LoginRequired, BadPassword
import threading
from tkinter.font import Font
import colorsys
import time

class CylindricalGradientProgressBar(tk.Canvas):
    def __init__(self, master=None, width=600, height=20, **kwargs):
        super().__init__(master, width=width, height=height, bg='#f0f0f0', highlightthickness=0, **kwargs)
        
        self.width = width
        self.height = height
        self.progress = 0
        self.gradient_colors = ['#F58529', '#DD2A7B']  # Updated gradient colors
        self.radius = height // 2  # Radius for rounded corners
        self._draw_cylindrical_progress()
    
    def _draw_cylindrical_progress(self):
        self.delete("all")
        progress_width = int((self.progress / 100) * self.width)

        # Draw the full rounded background (unfilled)
        self.create_rounded_rectangle(0, 0, self.width, self.height, radius=self.radius, fill='#dcdcdc', outline='')

        if progress_width > 0:
            # Draw a gradient within a rounded mask
            self._draw_gradient_progress(0, 0, progress_width, self.height, self.radius)

    def _draw_gradient_progress(self, x1, y1, x2, y2, radius):
        """Draws a smooth gradient inside a rounded shape"""
        steps = 50  # Number of gradient steps
        for i in range(steps):
            ratio = i / steps
            color = self._interpolate_color("#F58529", "#DD2A7B", ratio)
            
            # Calculate the x range for this slice
            x_start = x1 + (x2 - x1) * (i / steps)
            x_end = x1 + (x2 - x1) * ((i + 1) / steps)

            # Ensure we maintain rounded edges
            if x_start < radius:  # Left rounded side
                self.create_oval(x_start, y1, x_start + 2 * radius, y2, fill=color, outline=color)
            elif x_end > x2 - radius:  # Right rounded side
                self.create_oval(x_end - 2 * radius, y1, x_end, y2, fill=color, outline=color)
            else:
                # Middle straight part of progress
                self.create_rectangle(x_start, y1, x_end, y2, fill=color, outline=color)

    def _interpolate_color(self, color1, color2, ratio):
        """Blends two hex colors based on the given ratio"""
        c1 = [int(color1[i:i+2], 16) for i in (1, 3, 5)]
        c2 = [int(color2[i:i+2], 16) for i in (1, 3, 5)]
        blended = [int(c1[j] + (c2[j] - c1[j]) * ratio) for j in range(3)]
        return f'#{blended[0]:02x}{blended[1]:02x}{blended[2]:02x}'

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=10, **kwargs):
        """Draw a true rounded rectangle with filled ends"""
        self.create_arc(x1, y1, x1 + 2 * radius, y1 + 2 * radius, start=90, extent=90, **kwargs)
        self.create_arc(x2 - 2 * radius, y1, x2, y1 + 2 * radius, start=0, extent=90, **kwargs)
        self.create_arc(x1, y2 - 2 * radius, x1 + 2 * radius, y2, start=180, extent=90, **kwargs)
        self.create_arc(x2 - 2 * radius, y2 - 2 * radius, x2, y2, start=270, extent=90, **kwargs)
        self.create_rectangle(x1 + radius, y1, x2 - radius, y2, **kwargs)  # Main bar
    
    def _get_gradient_color(self, progress_ratio):
        """ Generate a smooth gradient transition """
        num_colors = len(self.gradient_colors) - 1
        index = progress_ratio * num_colors
        start_idx = int(index)
        end_idx = min(start_idx + 1, num_colors)

        # Interpolate between two adjacent colors
        ratio = index - start_idx
        start_color = self._hex_to_rgb(self.gradient_colors[start_idx])
        end_color = self._hex_to_rgb(self.gradient_colors[end_idx])

        r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)

        return f'#{r:02x}{g:02x}{b:02x}'

    def _hex_to_rgb(self, hex_color):
        """ Convert hex color to RGB """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def update_progress(self, value):
        """ Set progress (0 to 100) and redraw """
        self.progress = max(0, min(100, value))  # Ensure it's in range
        self._draw_cylindrical_progress()
        self.update_idletasks()  # Force UI refresh

class InstagramUnlikerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Unliker")
        self.root.geometry("400x600")  # Reduced window size
        
        self.root.configure(bg='#FFFFFF')
        self.setup_styles()
        
        main_frame = ttk.Frame(root, padding="10", style='Round.TFrame')  # Reduced padding
        main_frame.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        
        # Instagram Logo (Text Version)
        title_font = Font(family="Helvetica", size=18, weight="bold")  # Reduced font size
        title_label = tk.Label(main_frame, 
                             text="Instagram Unliker",
                             font=title_font,
                             foreground='#DD2A7B',
                             background='#FFFFFF')
        title_label.grid(row=0, column=0, columnspan=2, pady=10)  # Reduced padding
        
        # Username
        ttk.Label(main_frame, text="Username:", style='Custom.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(main_frame, textvariable=self.username_var, style='Custom.TEntry', width=30)
        self.username_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Password
        ttk.Label(main_frame, text="Password:", style='Custom.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(main_frame, textvariable=self.password_var, show="•", style='Custom.TEntry', width=30)
        self.password_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Like removal amount
        ttk.Label(main_frame, text="Likes to Remove:", style='Custom.TLabel').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.likes_var = tk.StringVar(value="30")
        self.likes_entry = ttk.Entry(main_frame, textvariable=self.likes_var, style='Custom.TEntry', width=30)
        self.likes_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Repeat checkbox
        self.repeat_var = tk.BooleanVar()
        self.repeat_check = ttk.Checkbutton(main_frame, 
                                          text="Repeat?", 
                                          variable=self.repeat_var,
                                          command=self.toggle_repeat_options,
                                          style='Custom.TCheckbutton')
        self.repeat_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Repeat options frame
        self.repeat_frame = ttk.Frame(main_frame, style='Round.TFrame')
        self.repeat_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.repeat_frame.grid_remove()
        
        # Number of repeats
        ttk.Label(self.repeat_frame, text="Repeats:", style='Custom.TLabel').grid(row=0, column=0, sticky=tk.W, pady=2)
        self.repeats_var = tk.StringVar(value="3")
        self.repeats_entry = ttk.Entry(self.repeat_frame, textvariable=self.repeats_var, style='Custom.TEntry', width=10)
        self.repeats_entry.grid(row=0, column=1, sticky=(tk.W), pady=2, padx=5)
        
        # Minutes between repeats
        ttk.Label(self.repeat_frame, text="Minutes Between:", style='Custom.TLabel').grid(row=1, column=0, sticky=tk.W, pady=2)
        self.interval_var = tk.StringVar(value="60")
        self.interval_entry = ttk.Entry(self.repeat_frame, textvariable=self.interval_var, style='Custom.TEntry', width=10)
        self.interval_entry.grid(row=1, column=1, sticky=(tk.W), pady=2, padx=5)
        
        # Progress
        self.progress_var = tk.StringVar(value="Ready to start...")
        ttk.Label(main_frame, textvariable=self.progress_var, style='Custom.TLabel').grid(
            row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Custom Progress bar (reduced width)
        self.progress_bar = CylindricalGradientProgressBar(
            main_frame,
            width=300,
            height=20
        )
        self.progress_bar.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10, padx=10)
        
        # Log text area (reduced height)
        self.log_text = tk.Text(main_frame, 
                               height=8,
                               width=40,
                               font=('Helvetica', 9),
                               bg='#FAFAFA',
                               relief='flat',
                               padx=5,
                               pady=5)
        self.log_text.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10, padx=10)
        
        # Custom scrollbar for log text
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.log_text.yview)
        scrollbar.grid(row=8, column=2, sticky='ns')
        self.log_text['yscrollcommand'] = scrollbar.set
        
        # Start button with explicit styling for Windows compatibility
        self.start_button = ttk.Button(main_frame, 
                                     text="Start Unliking", 
                                     command=self.start_unliking,
                                     style='Instagram.TButton')
        self.start_button.grid(row=9, column=0, columnspan=2, pady=10)
        
        # API client
        self.api = None
        self.stop_flag = False


    def to_json(self, python_object):
        """Helper method to convert Python objects to JSON"""
        if isinstance(python_object, bytes):
            return {
                '__class__': 'bytes',
                '__value__': codecs.encode(python_object, 'base64').decode()
            }
        raise TypeError(repr(python_object) + ' is not JSON serializable')

    def from_json(self, json_object):
        """Helper method to convert JSON back to Python objects"""
        if '__class__' in json_object and json_object['__class__'] == 'bytes':
            return codecs.decode(json_object['__value__'].encode(), 'base64')
        return json_object

    def on_login_callback(self, api, new_settings_file):
        """Callback method for saving login settings"""
        cache_settings = api.get_settings()
        with open(new_settings_file, 'w') as outfile:
            json.dump(cache_settings, outfile, default=self.to_json)
            self.log_message(f"SAVED: {new_settings_file}")

    def toggle_repeat_options(self):
        if self.repeat_var.get():
            self.repeat_frame.grid()
        else:
            self.repeat_frame.grid_remove()

    def setup_styles(self):
        style = ttk.Style()
        
        # Configure styles with smaller dimensions
        style.configure('Custom.TCheckbutton',
                       background='#FFFFFF',
                       font=('Helvetica', 10))
        
        style.configure('Round.TFrame',
                       background='#FFFFFF',
                       relief='flat')
        
        style.configure('Custom.TLabel',
                       background='#FFFFFF',
                       font=('Helvetica', 10))
        
        style.configure('Custom.TEntry',
                       padding=5,
                       relief='flat',
                       fieldbackground='#FAFAFA')
        
        # Modified button style for Windows compatibility
        style.configure('Instagram.TButton',
                       padding=10,
                       font=('Helvetica', 10, 'bold'))
        
        # Create a custom button layout for Windows
        style.layout('Instagram.TButton', [
            ('Button.padding', {'children': [
                ('Button.label', {'sticky': 'nswe'})
            ], 'sticky': 'nswe'})
        ])
        
        # Set button colors that work on both Windows and Linux
        style.map('Instagram.TButton',
                 background=[('active', '#C1236D'), ('!active', '#DD2A7B')],
                 foreground=[('active', 'white'), ('!active', 'white')])

    # [Previous helper methods remain unchanged]
    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    def start_unlike_process(self):
        try:
            like_removal_amount = int(self.likes_var.get())
            total_repeats = int(self.repeats_var.get()) if self.repeat_var.get() else 1
            interval_minutes = int(self.interval_var.get()) if self.repeat_var.get() else 0
            
            for repeat in range(total_repeats):
                if self.stop_flag:
                    break
                
                if repeat > 0:
                    self.log_message(f"\nWaiting {interval_minutes} minutes before next round...")
                    self.progress_var.set(f"Waiting for next round ({interval_minutes} minutes)...")
                    for minute in range(interval_minutes):
                        if self.stop_flag:
                            break
                        time.sleep(60)
                        remaining = interval_minutes - minute - 1
                        self.progress_var.set(f"Waiting: {remaining} minutes remaining...")
                        self.root.update()
                
                if self.stop_flag:
                    break
                
                self.log_message(f"\nStarting round {repeat + 1} of {total_repeats}")
                removed = 0
                self.progress_bar.update_progress(0)

                while removed < like_removal_amount and not self.stop_flag:
                    liked = self.api.liked_medias()
                    
                    for media in liked:
                        if removed >= like_removal_amount or self.stop_flag:
                            break
                            
                        try:
                            self.api.media_unlike(media.id)
                            removed += 1
                            progress = int((removed / like_removal_amount) * 100)
                            self.progress_bar.update_progress(progress)
                            self.progress_var.set(f"Round {repeat + 1}/{total_repeats}: Unliked {removed}/{like_removal_amount}")
                            self.log_message(f"Unliked post by {media.user.username}")
                            self.root.update()
                        except Exception as e:
                            self.log_message(f"Error: {str(e)}")
                            return
                    
                    if len(liked) == 0:
                        self.log_message("No more posts to unlike")
                        break
            
            self.progress_bar.update_progress(100)
            self.log_message(f"Finished all unliking rounds")
            self.progress_var.set("Complete!")
            
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
        finally:
            self.start_button["state"] = "normal"
            self.start_button["text"] = "Start Unliking"
            self.stop_flag = False

    def start_unliking(self):
        if self.start_button["text"] == "Stop":
            self.stop_flag = True
            self.start_button["text"] = "Stopping..."
            return

        self.stop_flag = False
        self.start_button["text"] = "Stop"
        self.log_text.delete(1.0, tk.END)
        self.progress_bar.update_progress(0)
        self.progress_var.set("Logging in...")
        
        settings_file = "settings.json"
        self.api = Client()
        
        if os.path.isfile(settings_file):
            self.log_message("Reusing settings...")
            with open(settings_file) as file_data:
                cached_settings = json.load(file_data, object_hook=self.from_json)
            self.api.set_settings(cached_settings)
        
        def login_process():
            try:
                self.api.login(self.username_var.get(), self.password_var.get())
                self.on_login_callback(self.api, settings_file)
                self.log_message("Login successful")
                self.start_unlike_process()
            except TwoFactorRequired:
                self.log_message("2FA required")
                self.root.after(0, self.handle_2fa)
            except BadPassword:
                self.log_message("Login failed: Incorrect password")
                messagebox.showerror("Error", "Incorrect password")
                self.start_button["state"] = "normal"
                self.start_button["text"] = "Start Unliking"
            except LoginRequired:
                self.log_message("Session expired. Please log in again")
                messagebox.showerror("Error", "Session expired. Please log in again")
                self.start_button["state"] = "normal"
                self.start_button["text"] = "Start Unliking"
            except Exception as e:
                self.log_message(f"Error: {str(e)}")
                messagebox.showerror("Error", str(e))
                self.start_button["state"] = "normal"
                self.start_button["text"] = "Start Unliking"
        
        threading.Thread(target=login_process, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = InstagramUnlikerGUI(root)
    root.mainloop()