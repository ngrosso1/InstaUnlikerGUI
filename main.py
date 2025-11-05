import tkinter as tk
from gui import InstagramUnlikerGUI
import os

def main():
    root = tk.Tk()
    
    # Set window icon
    try:
        icon_path = "instaul.ico"
        if os.path.exists(icon_path):
            # Convert ICO to PNG using Pillow (PhotoImage doesn't support ICO directly)
            try:
                from PIL import Image
                
                # Open ICO and convert to PNG
                img = Image.open(icon_path)
                # Convert to RGB if needed (PhotoImage works better with RGB)
                if img.mode == 'RGBA':
                    # Create a white background for transparency
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[3] if len(img.split()) == 4 else None)
                    img = rgb_img
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save to a temporary PNG file
                png_path = "instaul_temp.png"
                img.save(png_path, "PNG")
                photo = tk.PhotoImage(file=png_path)
                root.iconphoto(True, photo)
                # Keep a reference to prevent garbage collection
                root._icon_image = photo
                # Clean up temp file after a short delay (give tkinter time to load it)
                root.after(100, lambda: os.remove(png_path) if os.path.exists(png_path) else None)
            except Exception as e:
                print(f"Could not load window icon: {e}")
        else:
            print(f"Icon file not found: {icon_path}")
    except Exception as e:
        print(f"Could not load window icon: {e}")
        
    app = InstagramUnlikerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()