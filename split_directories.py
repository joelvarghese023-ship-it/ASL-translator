import json
import os
import shutil

# Configuration
JSON_PATH = "dataset/WLASL_v0.3.json"
SOURCE_VIDEO_DIR = "dataset/videos"
BASE_OUTPUT_DIR = "dataset/split_videos"
NUM_CLASSES = 100  # Only sort the top 100 words to keep it manageable

def organize_directories():
    with open(JSON_PATH, 'r') as f:
        wlasl_data = json.load(f)

    # Slice the top words
    subset_data = wlasl_data[:NUM_CLASSES]
    copied_count = 0

    for label_idx, item in enumerate(subset_data):
        gloss = item['gloss']  # The English word
        
        for instance in item['instances']:
            video_id = instance['video_id']
            split = instance['split'] # 'train', 'val', or 'test'
            
            # Check for the raw video file
            src_file = os.path.join(SOURCE_VIDEO_DIR, f"{video_id}.mp4")
            
            if os.path.exists(src_file):
                # Create the target directory (e.g., dataset/split_videos/train/book/)
                dest_dir = os.path.join(BASE_OUTPUT_DIR, split, gloss)
                os.makedirs(dest_dir, exist_ok=True)
                
                # Copy the file to its new organized folder
                dest_file = os.path.join(dest_dir, f"{video_id}.mp4")
                shutil.copy(src_file, dest_file)
                copied_count += 1

    print(f"Directory-wise bifurcation complete!")
    print(f"Successfully sorted {copied_count} videos into '{BASE_OUTPUT_DIR}'.")

if __name__ == "__main__":
    organize_directories()