import json
import os
from pathlib import Path

class DataManager:
    def __init__(self):
        self.data_dir = Path("data")
        try:
            self.data_dir.mkdir(exist_ok=True)

            self.users_file = self.data_dir / "users.json"
            self.emails_file = self.data_dir / "emails.json"
            self.queue_file = self.data_dir / "queue.json"
            
            # Initialize files if they don't exist
            self._init_file(self.users_file, {})
            self._init_file(self.emails_file, {})
            self._init_file(self.queue_file, [])
        except Exception as e:
            print(f"Error initializing DataManager: {e}")
    
    def _init_file(self, file_path, default_data):
        try:
            if not file_path.exists():
                with open(file_path, 'w') as f:
                    json.dump(default_data, f, indent=2)
        except Exception as e:
            print(f"Error initializing file {file_path}: {e}")

    def save_data(self, file_path, data):
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data to {file_path}: {e}")

    def load_data(self, file_path):
        try:
            if not file_path.exists():
                return None
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading data from {file_path}: {e}")
            return None