import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import threading
from tkinter.font import Font
from progress_bar import CylindricalGradientProgressBar
from api_handler import APIHandler
from styles import setup_styles, detect_dark_theme
from utils import json_encoder, json_decoder
import time

class InstagramUnlikerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Unliker")
        self.root.geometry("1300x700")
        self.root.minsize(900, 600)
        
        # Detect dark theme and setup styles
        self.is_dark = detect_dark_theme()
        self.bg_color, self.fg_color, self.text_bg = setup_styles(self.is_dark)
        self.root.configure(bg=self.bg_color)
        
        self.setup_main_frame()
        self.setup_title()
        self.setup_left_panel()
        self.setup_right_panel()
        
        self.api_handler = APIHandler(self.log_message, self.update_progress)
        self.stop_flag = False

    def setup_main_frame(self):
        self.main_frame = ttk.Frame(self.root, padding="15", style='Round.TFrame')
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        # Configure two columns for left and right panels
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1, minsize=300)

    def setup_title(self):
        title_font = Font(family="Helvetica", size=18, weight="bold")
        title_label = tk.Label(self.main_frame, 
                             text="Instagram Unliker",
                             font=title_font,
                             foreground='#DD2A7B',
                             background=self.bg_color)
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

    def setup_left_panel(self):
        # Left panel for input fields
        left_panel = ttk.Frame(self.main_frame, style='Round.TFrame')
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_panel.grid_columnconfigure(1, weight=1)
        
        # Username
        ttk.Label(left_panel, text="Username:", style='Custom.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(left_panel, textvariable=self.username_var, style='Custom.TEntry', width=25)
        self.username_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.username_entry.bind('<Return>', lambda e: self.start_unliking())
        self.username_entry.bind('<Down>', lambda e: self.password_entry.focus())
        
        # Password
        ttk.Label(left_panel, text="Password:", style='Custom.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(left_panel, textvariable=self.password_var, show="•", style='Custom.TEntry', width=25)
        self.password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.password_entry.bind('<Return>', lambda e: self.start_unliking())
        self.password_entry.bind('<Up>', lambda e: self.username_entry.focus())
        self.password_entry.bind('<Down>', lambda e: self.likes_entry.focus())
        
        # Like removal amount
        ttk.Label(left_panel, text="Likes to Remove:", style='Custom.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.likes_var = tk.StringVar(value="30")
        self.likes_entry = ttk.Entry(left_panel, textvariable=self.likes_var, style='Custom.TEntry', width=25)
        self.likes_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.likes_entry.bind('<Return>', lambda e: self.start_unliking())
        self.likes_entry.bind('<Up>', lambda e: self.password_entry.focus())
        
        # Repeat options
        self.setup_repeat_options(left_panel)
        
        # Start button
        self.setup_start_button(left_panel)

    def setup_repeat_options(self, parent):
        self.repeat_var = tk.BooleanVar()
        self.repeat_check = ttk.Checkbutton(parent, 
                                          text="Repeat?", 
                                          variable=self.repeat_var,
                                          command=self.toggle_repeat_options,
                                          style='Custom.TCheckbutton')
        self.repeat_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.setup_repeat_frame(parent)

    def setup_repeat_frame(self, parent):
        self.repeat_frame = ttk.Frame(parent, style='Round.TFrame')
        self.repeat_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.repeat_frame.grid_remove()
        self.repeat_frame.grid_columnconfigure(1, weight=1)
        
        # Number of repeats
        ttk.Label(self.repeat_frame, text="Repeats:", style='Custom.TLabel').grid(row=0, column=0, sticky=tk.W, pady=2)
        self.repeats_var = tk.StringVar(value="3")
        self.repeats_entry = ttk.Entry(self.repeat_frame, textvariable=self.repeats_var, style='Custom.TEntry', width=10)
        self.repeats_entry.grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)
        self.repeats_entry.bind('<Return>', lambda e: self.start_unliking())
        self.repeats_entry.bind('<Up>', lambda e: self.likes_entry.focus())
        self.repeats_entry.bind('<Down>', lambda e: self.interval_entry.focus())
        
        # Minutes between repeats
        ttk.Label(self.repeat_frame, text="Minutes Between:", style='Custom.TLabel').grid(row=1, column=0, sticky=tk.W, pady=2)
        self.interval_var = tk.StringVar(value="60")
        self.interval_entry = ttk.Entry(self.repeat_frame, textvariable=self.interval_var, style='Custom.TEntry', width=10)
        self.interval_entry.grid(row=1, column=1, sticky=tk.W, pady=2, padx=5)
        self.interval_entry.bind('<Return>', lambda e: self.start_unliking())
        self.interval_entry.bind('<Up>', lambda e: self.repeats_entry.focus())

    def setup_right_panel(self):
        # Right panel for progress and log
        right_panel = ttk.Frame(self.main_frame, style='Round.TFrame')
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)
        
        # Progress elements at the top
        self.setup_progress_elements(right_panel)
        
        # Log area below
        self.setup_log_area(right_panel)

    def setup_progress_elements(self, parent):
        progress_frame = ttk.Frame(parent, style='Round.TFrame')
        progress_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="Ready to start...")
        progress_label = ttk.Label(progress_frame, textvariable=self.progress_var, style='Custom.TLabel')
        progress_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.progress_bar = CylindricalGradientProgressBar(
            progress_frame,
            width=300,
            height=20,
            bg_color=self.bg_color
        )
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 0))

    def setup_log_area(self, parent):
        log_frame = ttk.Frame(parent, style='Round.TFrame')
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)
        
        # Label for log area
        log_label = ttk.Label(log_frame, text="Activity Log", style='Custom.TLabel')
        log_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(log_frame, style='Round.TFrame')
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(text_frame, 
                               height=10,
                               width=30,
                               font=('Helvetica', 9),
                               bg=self.text_bg,
                               fg=self.fg_color,
                               relief='flat',
                               padx=5,
                               pady=5,
                               state='disabled',
                               insertbackground=self.fg_color)  # Make it read-only
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.log_text.yview, style='Modern.TScrollbar')
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.log_text['yscrollcommand'] = scrollbar.set

    def setup_start_button(self, parent):
        self.start_button = ttk.Button(parent, 
                                     text="Start Unliking", 
                                     command=self.start_unliking,
                                     style='Instagram.TButton')
        self.start_button.grid(row=5, column=0, columnspan=2, pady=15, sticky=(tk.W, tk.E))

    def toggle_repeat_options(self):
        if self.repeat_var.get():
            self.repeat_frame.grid()
        else:
            self.repeat_frame.grid_remove()

    def log_message(self, message):
        # Enable text widget to insert, then disable again
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def update_progress(self, value, message=None):
        self.progress_bar.update_progress(value)
        if message:
            self.progress_var.set(message)

    def start_unliking(self):
        if self.start_button["text"] == "Stop":
            self.stop_flag = True
            self.start_button["text"] = "Stopping..."
            return

        self.stop_flag = False
        self.start_button["text"] = "Stop"
        # Enable text widget to clear, then disable again
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        self.update_progress(0, "Logging in...")

        threading.Thread(
            target=self.api_handler.start_process,
            args=(
                self.username_var.get(),
                self.password_var.get(),
                int(self.likes_var.get()),
                self.repeat_var.get(),
                int(self.repeats_var.get()) if self.repeat_var.get() else 1,
                int(self.interval_var.get()) if self.repeat_var.get() else 0,
                lambda: self.stop_flag,
                self.root,
                self.start_button
            ),
            daemon=True
        ).start()