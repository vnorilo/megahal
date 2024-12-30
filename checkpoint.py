import pickle
import os
import time

class CheckpointSaver:
    def __init__(self, filepath, time_interval=600):
        self.filepath = filepath
        self.last_saved = 0  # Initialize last save time as 0
        self.interval = time_interval

    def save_checkpoint(self, obj):
        # Check if more than 10 minutes (600 seconds) have passed since last save
        current_time = time.time()
        if current_time - self.last_saved >= self.interval:
            with open(self.filepath, 'wb') as file:
                pickle.dump(obj, file)
            self.last_saved = current_time
            print(f"Checkpoint saved at {time.ctime(current_time)}")

    def load_checkpoint(self):
        # Load checkpoint from file
        if os.path.exists(self.filepath):
            with open(self.filepath, 'rb') as file:
                obj = pickle.load(file)
            print("Checkpoint loaded successfully.")
            return obj
        else:
            print("No checkpoint file found.")
            return None    
