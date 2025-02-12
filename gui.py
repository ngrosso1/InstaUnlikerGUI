import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import threading
from tkinter.font import Font
from progress_bar import CylindricalGradientProgressBar
from api_handler import APIHandler
from styles import setup_styles
from utils import json_encoder, json_decoder
import time

class InstagramUnlikerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Unliker")
        self.root.geometry("400x600")
        self.root.configure(bg='#FFFFFF')
        setup_styles()
        
        self.setup_main_frame()
        self.setup_title()
        self.setup_input_fields()
        self.setup_repeat_options()
        self.setup_progress_elements()
        self.setup_log_area()
        self.setup_start_button()
        
        self.api_handler = APIHandler(self.log_message, self.update_progress)
        self.stop_flag = False

    def setup_main_frame(self):
        self.main_frame = ttk.Frame(self.root, padding="10", style='Round.TFrame')
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def setup_title(self):
        title_font = Font(family="Helvetica", size=18, weight="bold")
        title_label = tk.Label(self.main_frame, 
                             text="Instagram Unliker",
                             font=title_font,
                             foreground='#DD2A7B',
                             background='#FFFFFF')
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

    def setup_input_fields(self):
        # Username
        ttk.Label(self.main_frame, text="Username:", style='Custom.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(self.main_frame, textvariable=self.username_var, style='Custom.TEntry', width=30)
        self.username_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Password
        ttk.Label(self.main_frame, text="Password:", style='Custom.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(self.main_frame, textvariable=self.password_var, show="•", style='Custom.TEntry', width=30)
        self.password_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Like removal amount
        ttk.Label(self.main_frame, text="Likes to Remove:", style='Custom.TLabel').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.likes_var = tk.StringVar(value="30")
        self.likes_entry = ttk.Entry(self.main_frame, textvariable=self.likes_var, style='Custom.TEntry', width=30)
        self.likes_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

    def setup_repeat_options(self):
        self.repeat_var = tk.BooleanVar()
        self.repeat_check = ttk.Checkbutton(self.main_frame, 
                                          text="Repeat?", 
                                          variable=self.repeat_var,
                                          command=self.toggle_repeat_options,
                                          style='Custom.TCheckbutton')
        self.repeat_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.setup_repeat_frame()

    def setup_repeat_frame(self):
        self.repeat_frame = ttk.Frame(self.main_frame, style='Round.TFrame')
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

    def setup_progress_elements(self):
        self.progress_var = tk.StringVar(value="Ready to start...")
        ttk.Label(self.main_frame, textvariable=self.progress_var, style='Custom.TLabel').grid(
            row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.progress_bar = CylindricalGradientProgressBar(
            self.main_frame,
            width=300,
            height=20
        )
        self.progress_bar.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10, padx=10)

    def setup_log_area(self):
        self.log_text = tk.Text(self.main_frame, 
                               height=8,
                               width=40,
                               font=('Helvetica', 9),
                               bg='#FAFAFA',
                               relief='flat',
                               padx=5,
                               pady=5)
        self.log_text.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10, padx=10)
        
        scrollbar = ttk.Scrollbar(self.main_frame, orient='vertical', command=self.log_text.yview)
        scrollbar.grid(row=8, column=2, sticky='ns')
        self.log_text['yscrollcommand'] = scrollbar.set

    def setup_start_button(self):
        self.start_button = ttk.Button(self.main_frame, 
                                     text="Start Unliking", 
                                     command=self.start_unliking,
                                     style='Instagram.TButton')
        self.start_button.grid(row=9, column=0, columnspan=2, pady=10)

    def toggle_repeat_options(self):
        if self.repeat_var.get():
            self.repeat_frame.grid()
        else:
            self.repeat_frame.grid_remove()

    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

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
        self.log_text.delete(1.0, tk.END)
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