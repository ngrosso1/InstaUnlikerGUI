# styles.py
from tkinter import ttk

def setup_styles():
    style = ttk.Style()
    
    # Configure checkbox style
    style.configure('Custom.TCheckbutton',
                   background='#FFFFFF',
                   font=('Helvetica', 10))
    
    # Configure frame style
    style.configure('Round.TFrame',
                   background='#FFFFFF',
                   relief='flat')
    
    # Configure label style
    style.configure('Custom.TLabel',
                   background='#FFFFFF',
                   font=('Helvetica', 10))
    
    # Configure entry style
    style.configure('Custom.TEntry',
                   padding=5,
                   relief='flat',
                   fieldbackground='#FAFAFA')
    
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