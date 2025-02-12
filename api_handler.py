from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired, LoginRequired, BadPassword
import json
import os
from tkinter import messagebox
import time
from utils import json_encoder, json_decoder

class APIHandler:
    def __init__(self, log_callback, progress_callback):
        self.log_callback = log_callback
        self.progress_callback = progress_callback
        self.api = None

    def save_settings(self, settings_file):
        cache_settings = self.api.get_settings()
        with open(settings_file, 'w') as outfile:
            json.dump(cache_settings, outfile, default=json_encoder)
            self.log_callback(f"SAVED: {settings_file}")

    def unlike_posts(self, like_removal_amount, total_repeats, interval_minutes, get_stop_flag, root):
        try:
            for repeat in range(total_repeats):
                if get_stop_flag():
                    break
                
                if repeat > 0:
                    self.log_callback(f"\nWaiting {interval_minutes} minutes before next round...")
                    self.progress_callback(0, f"Waiting for next round ({interval_minutes} minutes)...")
                    for minute in range(interval_minutes):
                        if get_stop_flag():
                            break
                        time.sleep(60)
                        remaining = interval_minutes - minute - 1
                        self.progress_callback(0, f"Waiting: {remaining} minutes remaining...")
                        root.update()
                
                if get_stop_flag():
                    break
                
                self.log_callback(f"\nStarting round {repeat + 1} of {total_repeats}")
                removed = 0
                self.progress_callback(0)

                while removed < like_removal_amount and not get_stop_flag():
                    liked = self.api.liked_medias()
                    
                    for media in liked:
                        if removed >= like_removal_amount or get_stop_flag():
                            break
                            
                        try:
                            self.api.media_unlike(media.id)
                            removed += 1
                            progress = int((removed / like_removal_amount) * 100)
                            self.progress_callback(progress, f"Round {repeat + 1}/{total_repeats}: Unliked {removed}/{like_removal_amount}")
                            self.log_callback(f"Unliked post by {media.user.username}")
                            root.update()
                        except Exception as e:
                            self.log_callback(f"Error: {str(e)}")
                            return
                    
                    if len(liked) == 0:
                        self.log_callback("No more posts to unlike")
                        break
            
            self.progress_callback(100, "Complete!")
            self.log_callback(f"Finished all unliking rounds")
            
        except Exception as e:
            self.log_callback(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))

    def handle_2fa(self, code):
        try:
            self.api.two_factor_login(code)
            self.log_callback("2FA successful")
            return True
        except Exception as e:
            self.log_callback(f"2FA failed: {str(e)}")
            return False

    def start_process(self, username, password, like_amount, repeat_enabled, total_repeats, 
                     interval_minutes, get_stop_flag, root, start_button):
        settings_file = "settings.json"
        self.api = Client()
        
        if os.path.isfile(settings_file):
            self.log_callback("Reusing settings...")
            with open(settings_file) as file_data:
                cached_settings = json.load(file_data, object_hook=json_decoder)
            self.api.set_settings(cached_settings)
        
        try:
            self.api.login(username, password)
            self.save_settings(settings_file)
            self.log_callback("Login successful")
            self.unlike_posts(like_amount, total_repeats, interval_minutes, get_stop_flag, root)
            
        except TwoFactorRequired:
            self.log_callback("2FA required")
            # Note: GUI needs to handle requesting 2FA code from user
            
        except BadPassword:
            self.log_callback("Login failed: Incorrect password")
            messagebox.showerror("Error", "Incorrect password")
            
        except LoginRequired:
            self.log_callback("Session expired. Please log in again")
            messagebox.showerror("Error", "Session expired. Please log in again")
            
        except Exception as e:
            self.log_callback(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
            
        finally:
            start_button["state"] = "normal"
            start_button["text"] = "Start Unliking"