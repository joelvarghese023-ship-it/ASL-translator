import json
import os
import shutil

# Configuration
JSON_PATH = "dataset/WLASL_v0.3.json"
SOURCE_VIDEO_DIR = "dataset/videos"
BASE_OUTPUT_DIR = "dataset/split_videos"
NUM_CLASSES = 2000  # Expand to full WLASL-2000 benchmark dataset

def organize_directories():
    with open(JSON_PATH, 'r') as f:
        wlasl_data = json.load(f)

    # Slice the words
    subset_data = wlasl_data[:NUM_CLASSES]
    sorted_count = 0
    skipped_count = 0

    print(f"Organizing {len(subset_data)} classes into train, val, and test splits...")

    for label_idx, item in enumerate(subset_data):
        gloss = item['gloss']
        
        for instance in item['instances']:
            video_id = instance['video_id']
            split = instance['split'] # 'train', 'val', or 'test'
            
            src_file = os.path.join(SOURCE_VIDEO_DIR, f"{video_id}.mp4")
            
            if os.path.exists(src_file):
                dest_dir = os.path.join(BASE_OUTPUT_DIR, split, gloss)
                os.makedirs(dest_dir, exist_ok=True)
                dest_file = os.path.join(dest_dir, f"{video_id}.mp4")
                
                if os.path.exists(dest_file):
                    skipped_count += 1
                    continue

                try:
                    os.link(src_file, dest_file) # Fast zero-copy NTFS hardlink
                except Exception:
                    shutil.copy(src_file, dest_file)
                sorted_count += 1

    print(f"Directory organization complete!")
    print(f"Newly sorted: {sorted_count} videos | Already sorted: {skipped_count} | Output: '{BASE_OUTPUT_DIR}'.")

if __name__ == "__main__":
    organize_directories()
