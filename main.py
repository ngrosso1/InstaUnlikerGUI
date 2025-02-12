import tkinter as tk
from gui import InstagramUnlikerGUI
import os

def main():
    root = tk.Tk()
    
    # Set window icon
    try:
        # For the window icon
        root.iconphoto(True, tk.PhotoImage(file="instaul.ico"))
    except:
        print("Could not load window icon")
        
    app = InstagramUnlikerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()