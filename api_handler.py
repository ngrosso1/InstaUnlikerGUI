from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired, LoginRequired, BadPassword
from pydantic import ValidationError
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
        total_skipped = 0  # Track total skipped across all rounds
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
                round_skipped = 0
                self.progress_callback(0)

                while removed < like_removal_amount and not get_stop_flag():
                    liked = []
                    validation_error_occurred = False
                    skipped_in_batch = 0
                    target_reached = False
                    
                    # Try to get liked media - wrap in try-except to handle validation errors
                    try:
                        # Try to get the list - if validation error occurs during parsing,
                        # we might be able to catch it during iteration instead
                        liked = self.api.liked_medias()
                    except ValidationError as e:
                        # Pydantic validation error - this happens when instagrapi tries to parse the response
                        validation_error_occurred = True
                        error_msg = str(e)
                        # Check for various validation error types
                        if ("clips_metadata" in error_msg or "audio_ranking_info" in error_msg or 
                            "original_sound_info" in error_msg or "image_versions2" in error_msg or
                            "scans_profile" in error_msg):
                            self.log_callback("Warning: Validation error detected (likely Reels with missing metadata)")
                            
                            # Try to access raw API response to get media IDs before parsing
                            try:
                                # Try to use private API method to get raw data
                                user_id = self.api.user_id
                                # Attempt to get liked feed using lower-level API
                                raw_response = self.api.private_request(
                                    "feed/liked/",
                                    params={"max_id": ""}
                                )
                                
                                # Extract media IDs from raw response
                                if raw_response and 'items' in raw_response:
                                    items = raw_response.get('items', [])
                                    self.log_callback(f"Found {len(items)} liked media items in raw response")
                                    
                                    # Process raw items to extract media IDs
                                    for item in items:
                                        if removed >= like_removal_amount or get_stop_flag():
                                            break
                                        
                                        try:
                                            # Try to get media ID from raw item
                                            media_id = item.get('id') or item.get('pk') or item.get('media_id')
                                            
                                            if media_id:
                                                try:
                                                    self.api.media_unlike(media_id)
                                                    removed += 1
                                                    # Calculate progress, ensuring it reaches 100% when target is reached
                                                    progress = min(100, int((removed / like_removal_amount) * 100))
                                                    if removed >= like_removal_amount:
                                                        progress = 100
                                                    self.progress_callback(progress, f"Round {repeat + 1}/{total_repeats}: Unliked {removed}/{like_removal_amount}")
                                                    username = item.get('user', {}).get('username', 'Unknown')
                                                    self.log_callback(f"Unliked post by {username}")
                                                    root.update()
                                                    
                                                    # Check if we've reached the target and break immediately
                                                    if removed >= like_removal_amount:
                                                        self.progress_callback(100, "Complete!")
                                                        break
                                                except Exception as unlike_err:
                                                    skipped_in_batch += 1
                                                    round_skipped += 1
                                                    total_skipped += 1
                                                    self.log_callback(f"Skipped video (ID: {media_id}) - unable to unlike")
                                            else:
                                                skipped_in_batch += 1
                                                round_skipped += 1
                                                total_skipped += 1
                                                self.log_callback(f"Skipped item - no media ID found")
                                        except Exception as item_err:
                                            skipped_in_batch += 1
                                            round_skipped += 1
                                            total_skipped += 1
                                            self.log_callback(f"Skipped item due to error")
                                    
                                    if skipped_in_batch > 0:
                                        self.log_callback(f"Skipped {skipped_in_batch} video(s) with validation errors")
                                    
                                    # Check if we've reached the target
                                    if removed >= like_removal_amount:
                                        # Update progress to 100% and break out of both loops
                                        self.progress_callback(100, "Complete!")
                                        target_reached = True
                                        break
                                    
                                    # Continue to next iteration to check for more items
                                    continue
                                
                                # If target was reached, break from outer while loop
                                if target_reached:
                                    break
                                else:
                                    self.log_callback("Unable to extract media from raw API response")
                            except Exception as raw_err:
                                # Raw API access failed, fall through to error handling
                                pass
                            
                            # If we couldn't get raw data, count this as a failure
                            self.log_callback("Unable to retrieve media list due to validation errors.")
                            self.log_callback("This typically means all or most liked media have metadata issues.")
                            self.log_callback("Consider updating instagrapi or manually unliking problematic Reels.")
                            
                            # Since we can't determine exact count, we'll note that validation errors occurred
                            # but we can't accurately count skipped items
                            if removed == 0:
                                self.log_callback("Cannot proceed - unable to fetch liked media due to validation errors")
                                break
                            continue
                        else:
                            self.log_callback(f"Validation error: {error_msg[:150]}")
                        liked = []
                    except Exception as e:
                        error_msg = str(e)
                        self.log_callback(f"Error fetching liked media: {error_msg[:150]}")
                        liked = []
                    
                    # If we got items, process them
                    if len(liked) == 0:
                        if removed == 0 and not validation_error_occurred:
                            self.log_callback("No more posts to unlike or unable to fetch liked media")
                        break
                    
                    valid_media_count = 0
                    batch_skipped = 0
                    
                    # Process each media item individually, catching validation errors
                    for idx, media in enumerate(liked):
                        if removed >= like_removal_amount or get_stop_flag():
                            break
                        
                        media_id = None
                        username = "Unknown"
                        item_skipped = False
                        
                        # Wrap the entire item processing in try-except to catch any validation errors
                        try:
                            # First, try to get the media ID (most important)
                            try:
                                media_id = media.id
                            except (ValidationError, AttributeError) as e:
                                # Try to get ID from alternative attributes
                                try:
                                    if hasattr(media, 'pk'):
                                        media_id = media.pk
                                    elif hasattr(media, '__dict__'):
                                        # Try to find ID in attributes
                                        for attr in ['id', 'pk', 'media_id']:
                                            if hasattr(media, attr):
                                                try:
                                                    media_id = getattr(media, attr)
                                                    break
                                                except (ValidationError, AttributeError):
                                                    continue
                                except:
                                    pass
                            
                            if not media_id:
                                item_skipped = True
                                batch_skipped += 1
                                round_skipped += 1
                                total_skipped += 1
                                self.log_callback(f"Skipping video {idx + 1} - unable to get media ID")
                                continue
                            
                            # Try to get username (optional, for logging)
                            try:
                                if hasattr(media, 'user') and media.user:
                                    username = media.user.username
                            except (ValidationError, AttributeError):
                                # Username is optional, continue without it
                                pass
                            
                            # Attempt to unlike even if we had validation errors getting metadata
                            if media_id:
                                try:
                                    self.api.media_unlike(media_id)
                                    removed += 1
                                    valid_media_count += 1
                                    # Calculate progress, ensuring it reaches 100% when target is reached
                                    progress = min(100, int((removed / like_removal_amount) * 100))
                                    if removed >= like_removal_amount:
                                        progress = 100
                                    self.progress_callback(progress, f"Round {repeat + 1}/{total_repeats}: Unliked {removed}/{like_removal_amount}")
                                    self.log_callback(f"Unliked post by {username}")
                                    root.update()
                                    
                                    # Check if we've reached the target and break immediately
                                    if removed >= like_removal_amount:
                                        self.progress_callback(100, "Complete!")
                                        target_reached = True
                                        break
                                except Exception as e:
                                    # Error during unliking
                                    error_msg = str(e)
                                    if "validation" in error_msg.lower() or "clips_metadata" in error_msg.lower():
                                        item_skipped = True
                                        batch_skipped += 1
                                        round_skipped += 1
                                        total_skipped += 1
                                        self.log_callback(f"Skipped video {idx + 1} (validation error during unlike)")
                                    else:
                                        self.log_callback(f"Error unliking video {idx + 1}: {error_msg[:100]}")
                        
                        except ValidationError as e:
                            # Catch any validation errors we missed
                            item_skipped = True
                            batch_skipped += 1
                            round_skipped += 1
                            total_skipped += 1
                            self.log_callback(f"Skipped video {idx + 1} due to validation error")
                            continue
                        except Exception as e:
                            # Other unexpected errors
                            error_msg = str(e)
                            if "validation" in error_msg.lower():
                                item_skipped = True
                                batch_skipped += 1
                                round_skipped += 1
                                total_skipped += 1
                                self.log_callback(f"Skipped video {idx + 1} due to validation error")
                            else:
                                self.log_callback(f"Error processing video {idx + 1}: {error_msg[:100]}")
                    
                    if batch_skipped > 0:
                        self.log_callback(f"Skipped {batch_skipped} video(s) with validation errors in this batch")
                    
                    if valid_media_count == 0 and round_skipped == len(liked) and len(liked) > 0:
                        self.log_callback("All media items in this batch had validation errors. Stopping.")
                        break
                    
                    # Check if target was reached and break from while loop
                    if removed >= like_removal_amount:
                        self.progress_callback(100, "Complete!")
                        target_reached = True
                        break
            
            # Final progress update (ensure it reaches 100% if target was reached)
            if removed >= like_removal_amount:
                self.progress_callback(100, "Complete!")
            summary = f"Finished all unliking rounds"
            if total_skipped > 0:
                summary += f" - {total_skipped} video(s) skipped due to validation errors"
            self.log_callback(summary)
            
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