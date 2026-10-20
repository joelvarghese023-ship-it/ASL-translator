import os
import numpy as np
import json

DATASET_DIR = "dataset/split_features/train"
OUTPUT_DIR = "static_dataset"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for word in os.listdir(DATASET_DIR):
    word_dir = os.path.join(DATASET_DIR, word)
    if not os.path.isdir(word_dir): continue
    
    npy_files = [f for f in os.listdir(word_dir) if f.endswith('.npy')]
    if not npy_files: continue
    
    # Load the first recorded sequence for this word
    seq = np.load(os.path.join(word_dir, npy_files[0])).tolist()
    
    # Save as a web-readable JSON file
    with open(os.path.join(OUTPUT_DIR, f"{word}.json"), "w") as f:
        json.dump({"word": word, "frames": seq}, f)

print(f"Conversion complete. JSON files saved to /{OUTPUT_DIR}")