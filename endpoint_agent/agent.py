import time
import requests
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Custom Imports ---
from detector.extractor import extract_text_from_file
from detector.detectors import find_patterns, sha256_of_bytes

# --- !! UPDATE THESE PATHS !! ---
# Use forward slashes '/' or raw strings r"..."
path_to_watch = r"D:\Jaimeet\Information Security Lab\dlp_test_folder"
QUARANTINE_DIR = r"D:\Jaimeet\Information Security Lab\dlp_quarantine"
# --- !! UPDATE THESE PATHS !! ---

API_URL = "http://127.0.0.1:5000/log_event"

def process_file(filepath):
    """
    Main function to process a single file: extract text, find patterns,
    log to server, and quarantine if sensitive.
    """
    try:
        if not os.path.exists(filepath):
            return # File might have been moved already
            
        print(f"Processing: {filepath}")
        
        # 1. Extract text from the file
        text = extract_text_from_file(filepath)
        
        # 2. Find patterns
        matches = find_patterns(text)
        
        if matches:
            print(f"  Matches found: {matches}")
            
            # 3. Log to central server
            try:
                log_data = {
                    "event_type": "dlp_violation",
                    "channel": "endpoint",
                    "filepath": filepath,
                    "matches": matches,
                    "action_taken": "quarantined"
                }
                requests.post(API_URL, json=log_data)
                print(f"  Event logged to server.")
            except Exception as e:
                print(f"  Could not log to server: {e}")

            # 4. Quarantine the file
            if not os.path.exists(QUARANTINE_DIR):
                os.makedirs(QUARANTINE_DIR)
            
            filename = os.path.basename(filepath)
            quarantine_path = os.path.join(QUARANTINE_DIR, filename)
            
            os.rename(filepath, quarantine_path)
            print(f"  Quarantined file to: {quarantine_path}")
            
        else:
            print(f"  No matches found in: {filepath}")

    except Exception as e:
        print(f"Error processing file {filepath}: {e}")

class FileChangeHandler(FileSystemEventHandler):
    """
    Event handler that calls process_file() on new or modified files.
    """
    def on_created(self, event):
        if not event.is_directory:
            print(f"File created: {event.src_path}")
            process_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            print(f"File modified: {event.src_path}")
            process_file(event.src_path)

# --- Main execution ---
if __name__ == "__main__":
    print(f"Starting endpoint agent.")
    print(f"Watching folder: {path_to_watch}")
    print(f"Quarantine dir: {QUARANTINE_DIR}")
    
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=True)
    
    observer.start()
    print("Agent started. Waiting for file changes...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
