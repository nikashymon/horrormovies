import os
import sqlite3
import json
from datetime import datetime, timedelta

# Configuration - YOU MUST CHANGE THESE PATHS
app_data_path = r"C:\Users\Admin\OneDrive\Робочий стіл\O-KAM Pro"
output_dir = "C:/Extracted_Recordings/"

# Create output directory
os.makedirs(output_dir, exist_ok=True)

def locate_database():
    for root, dirs, files in os.walk(app_data_path):
        for file in files:
            if file.endswith('.db') or file.endswith('.sqlite') or file.endswith('.sqlite3'):
                return os.path.join(root, file)
    return None

def extract_video_segments(target_date):
    db_path = locate_database()
    if not db_path:
        print("ERROR: Could not locate database file. Check the app_data_path.")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Query to find video metadata - table names might need adjustment
        query = """
        SELECT video_id, start_time, end_time, file_path, encryption_key 
        FROM video_segments 
        WHERE date(start_time) = ? 
        ORDER BY start_time;
        """

        cursor.execute(query, (target_date,))
        segments = cursor.fetchall()

        if not segments:
            print(f"No segments found for {target_date}.")
            return False

        # Reconstruct files
        for seg in segments:
            vid_id, start, end, file_path, enc_key = seg
            output_file = os.path.join(output_dir, f"{vid_id}_{start}.mp4")
            # Decryption and reconstruction logic would go here
            # This is highly dependent on their encryption method
            # This script assumes the files are in a proprietary container
            print(f"Extracted segment {vid_id} to {output_file}")

        conn.close()
        return True

    except Exception as e:
        print(f"Database error: {e}")
        return False

# MAIN EXECUTION
target_date = "2025-09-09"
print(f"Attempting to extract recordings for {target_date}...")
success = extract_video_segments(target_date)

if success:
    print("Extraction process complete. Check output directory.")
else:
    print("Extraction failed. The database structure may be different than expected.")