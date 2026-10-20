import cv2
import numpy as np
import os
import mediapipe as mp

# 1. Configuration Paths
BASE_VIDEO_DIR = "dataset/split_videos"      
BASE_OUTPUT_DIR = "dataset/split_features"   

# 2. Initialize MediaPipe Holistic
mp_holistic = mp.solutions.holistic

def extract_keypoints(results):
    pose = np.array([[res.x, res.y, res.z] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*3)
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return np.concatenate([pose, lh, rh])

def process_video(video_path, output_path):
    cap = cv2.VideoCapture(video_path)
    sequence_data = []

    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert BGR (OpenCV format) to RGB (MediaPipe format)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            
            # Run MediaPipe Detection
            results = holistic.process(image)
            
            # Extract features and append
            sequence_data.append(extract_keypoints(results))
            
        cap.release()

    if len(sequence_data) > 0:
        np.save(output_path, np.array(sequence_data))
    else:
        print(f"Skipped {video_path} (No frames extracted)")

# 3. Process the Organized Directories
for split in ['train', 'val', 'test']:
    split_dir = os.path.join(BASE_VIDEO_DIR, split)
    if not os.path.exists(split_dir):
        continue
        
    for word_folder in os.listdir(split_dir):
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
                
                # Skip if already processed
                if not os.path.exists(out_path):
                    process_video(v_path, out_path)
                    print(f"Processed: {split}/{word_folder}/{file_name}")

print("Batch feature extraction complete.")