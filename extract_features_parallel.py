import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import sys
import time
import json
import cv2
import numpy as np
import multiprocessing as mp

# Configuration Paths
BASE_VIDEO_DIR = "dataset/split_videos"
BASE_OUTPUT_DIR = "dataset/split_features"
STATIC_OUTPUT_DIR = "static_dataset"

_worker_holistic = None

def init_worker():
    """Initializes MediaPipe Holistic once per worker process."""
    global _worker_holistic
    import mediapipe as mpipe
    _worker_holistic = mpipe.solutions.holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        model_complexity=1
    )

def extract_keypoints(results):
    pose = np.array([[res.x, res.y, res.z] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33 * 3)
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21 * 3)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21 * 3)
    return np.concatenate([pose, lh, rh])

def process_single_video(item):
    """Worker task: processes one video file and extracts 225-dim landmarks."""
    global _worker_holistic
    v_path, out_path, word, is_train = item

    if os.path.exists(out_path):
        return True, word, False

    cap = cv2.VideoCapture(v_path)
    sequence_data = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = _worker_holistic.process(image)
        sequence_data.append(extract_keypoints(results))

    cap.release()

    if len(sequence_data) > 0:
        arr = np.array(sequence_data, dtype=np.float32)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        np.save(out_path, arr)

        # Simultaneously generate 3D trajectory JSON for Cartoon Leo if missing
        static_json_path = os.path.join(STATIC_OUTPUT_DIR, f"{word}.json")
        if is_train and not os.path.exists(static_json_path):
            try:
                with open(static_json_path, "w", encoding="utf-8") as f:
                    json.dump({"word": word, "frames": arr.tolist()}, f)
            except Exception:
                pass
        return True, word, True
    return False, word, False

def main():
    os.makedirs(STATIC_OUTPUT_DIR, exist_ok=True)

    print("Scanning split_videos directory for tasks...")
    tasks = []
    
    for split in ['train', 'val', 'test']:
        split_dir = os.path.join(BASE_VIDEO_DIR, split)
        if not os.path.exists(split_dir):
            continue

        for word_folder in sorted(os.listdir(split_dir)):
            word_dir = os.path.join(split_dir, word_folder)
            if not os.path.isdir(word_dir):
                continue

            out_word_dir = os.path.join(BASE_OUTPUT_DIR, split, word_folder)
            os.makedirs(out_word_dir, exist_ok=True)

            for video_file in os.listdir(word_dir):
                if video_file.endswith(".mp4"):
                    v_path = os.path.join(word_dir, video_file)
                    file_name = os.path.splitext(video_file)[0]
                    out_path = os.path.join(out_word_dir, f"{file_name}.npy")
                    
                    if not os.path.exists(out_path):
                        tasks.append((v_path, out_path, word_folder, split == 'train'))

    total_tasks = len(tasks)
    print(f"Total videos to extract: {total_tasks}")

    if total_tasks == 0:
        print("All features already extracted!")
        return

    # Use 16 parallel workers (optimized for 24-core Intel Ultra 9)
    num_workers = min(16, max(1, mp.cpu_count() - 4))
    print(f"Launching {num_workers} parallel MediaPipe worker processes...")

    start_time = time.time()
    completed = 0
    extracted = 0

    with mp.Pool(processes=num_workers, initializer=init_worker) as pool:
        for success, word, newly_saved in pool.imap_unordered(process_single_video, tasks, chunksize=4):
            completed += 1
            if newly_saved:
                extracted += 1

            if completed % 25 == 0 or completed == total_tasks:
                elapsed = time.time() - start_time
                rate = completed / max(elapsed, 0.001)
                remaining = (total_tasks - completed) / max(rate, 0.001)
                pct = (completed / total_tasks) * 100.0
                print(f"[{completed}/{total_tasks}] ({pct:.1f}%) | Speed: {rate:.1f} vid/sec | ETA: {remaining/60:.1f} min | Latest: {word}", flush=True)

    total_elapsed = time.time() - start_time
    print(f"\nAll feature extraction finished in {total_elapsed/60:.1f} minutes! Total new: {extracted}")

if __name__ == '__main__':
    mp.freeze_support()
    main()
