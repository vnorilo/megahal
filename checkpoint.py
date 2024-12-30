import pickle
import os
import time
import io
import zipfile

class CheckpointSaver:
    def __init__(self, filepath, time_interval=600):
        self.filepath = filepath
        self.last_saved = 0  # Initialize last save time as 0
        self.interval = time_interval

    def save_checkpoint(self, obj):
        # Check if more than the specified interval (default 600 seconds) have passed since last save
        current_time = time.time()
        if current_time - self.last_saved >= self.interval:
            # Step 1: Pickle the object into an in-memory buffer
            pickle_buffer = io.BytesIO()
            pickle.dump(obj, pickle_buffer)

            # Step 2: Zip the pickled object in-memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                pickle_buffer.seek(0)  # Rewind the pickle buffer to the start
                zipf.writestr('checkpoint.pkl', pickle_buffer.read())

            # Step 3: Save the zip data to a file on disk
            with open(self.filepath, 'wb') as f:
                f.write(zip_buffer.getvalue())

            self.last_saved = current_time
            print(f"Checkpoint saved at {time.ctime(current_time)}")

    def load_checkpoint(self):
        # Load and unzip the checkpoint from the file
        if os.path.exists(self.filepath):
            with open(self.filepath, 'rb') as file:
                zip_data = file.read()

            # Unzip the file in-memory
            with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zipf:
                with zipf.open('checkpoint.pkl') as pickle_file:
                    obj = pickle.load(pickle_file)

            print("Checkpoint loaded successfully.")
            return obj
        else:
            print("No checkpoint file found.")
            return None
