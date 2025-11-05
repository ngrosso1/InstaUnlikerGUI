# styles.py
from tkinter import ttk
import os
import subprocess

def detect_dark_theme():
    """Detect if the system is using a dark theme"""
    try:
        # Try gsettings (GNOME/GTK)
        result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
                              capture_output=True, text=True, timeout=1)
        if result.returncode == 0:
            theme = result.stdout.strip().lower().strip("'\"")
            if 'dark' in theme:
                return True
        
        # Try color-scheme (newer GTK)
        result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
                              capture_output=True, text=True, timeout=1)
        if result.returncode == 0:
            scheme = result.stdout.strip().lower().strip("'\"")
            if 'dark' in scheme:
                return True
    except:
        pass
    
    # Check environment variable
    if os.environ.get('GTK_THEME', '').lower().find('dark') != -1:
        return True
    
    return False

def setup_styles(is_dark=False):
    style = ttk.Style()
    
    # Color scheme based on theme
    if is_dark:
        bg_color = '#1E1E1E'
        fg_color = '#FFFFFF'
        entry_bg = '#2D2D2D'
        text_bg = '#252525'
        border_color = '#404040'
    else:
        bg_color = '#FFFFFF'
        fg_color = '#000000'
        entry_bg = '#FAFAFA'
        text_bg = '#FAFAFA'
        border_color = '#E0E0E0'
    
    # Configure checkbox style
    style.configure('Custom.TCheckbutton',
                   background=bg_color,
                   foreground=fg_color,
                   font=('Helvetica', 10))
    
    # Configure frame style
    style.configure('Round.TFrame',
                   background=bg_color,
                   relief='flat')
    
    # Configure label style
    style.configure('Custom.TLabel',
                   background=bg_color,
                   foreground=fg_color,
                   font=('Helvetica', 10))
    
    # Configure entry style
    style.configure('Custom.TEntry',
                   padding=5,
                   relief='flat',
                   fieldbackground=entry_bg,
                   foreground=fg_color,
                   borderwidth=1)
    
    # Configure Instagram-themed button style
    style.configure('Instagram.TButton',
                   padding=10,
                   font=('Helvetica', 10, 'bold'))
    
    # Create custom button layout for Windows compatibility
    style.layout('Instagram.TButton', [
        ('Button.padding', {'children': [
            ('Button.label', {'sticky': 'nswe'})
        ], 'sticky': 'nswe'})
    ])
    
    # Set button colors for cross-platform compatibility
    style.map('Instagram.TButton',
             background=[('active', '#C1236D'), ('!active', '#DD2A7B')],
             foreground=[('active', 'white'), ('!active', 'white')])
    
    # Modern scrollbar styling
    # First, configure the base scrollbar style
    style.configure('Modern.TScrollbar',
                    background=border_color if is_dark else '#C0C0C0',
                    troughcolor=bg_color,
                    borderwidth=0,
                    arrowcolor=fg_color,
                    darkcolor=border_color if is_dark else '#E0E0E0',
                    lightcolor=border_color if is_dark else '#E0E0E0',
                    width=12)
    
    # Create custom scrollbar layout
    style.layout('Modern.TScrollbar', [
        ('Scrollbar.trough', {
            'children': [
                ('Scrollbar.uparrow', {'side': 'top', 'sticky': ''}),
                ('Scrollbar.downarrow', {'side': 'bottom', 'sticky': ''}),
                ('Scrollbar.thumb', {
                    'expand': '1',
                    'sticky': 'nswe'
                })
            ],
            'sticky': 'ns'
        })
    ])
    
    style.map('Modern.TScrollbar',
             background=[('active', '#888888' if is_dark else '#A0A0A0'),
                        ('!active', border_color if is_dark else '#C0C0C0')],
             arrowcolor=[('active', fg_color),
                        ('!active', fg_color)],
             darkcolor=[('active', border_color if is_dark else '#E0E0E0'),
                       ('!active', border_color if is_dark else '#E0E0E0')],
             lightcolor=[('active', border_color if is_dark else '#E0E0E0'),
                        ('!active', border_color if is_dark else '#E0E0E0')])
    
    return bg_color, fg_color, text_bg