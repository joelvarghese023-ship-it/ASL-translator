import os
import time
os.environ["TF_USE_LEGACY_KERAS"] = "1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import cv2
import numpy as np
import mediapipe as mp
import pandas as pd
from tensorflow.keras.models import load_model

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Load Classes & Models
CLASSES_JSON = os.path.join(BASE_DIR, "classes.json")
CLASSES_DIR = os.path.join(BASE_DIR, "dataset", "split_features", "train")
STATIC_DIR = os.path.join(BASE_DIR, "static_dataset")

classes = []
if os.path.exists(CLASSES_JSON):
    import json
    with open(CLASSES_JSON, "r", encoding="utf-8") as f:
        classes = json.load(f)
elif os.path.exists(CLASSES_DIR):
    classes = sorted([d for d in os.listdir(CLASSES_DIR) if os.path.isdir(os.path.join(CLASSES_DIR, d))])
elif os.path.exists(STATIC_DIR):
    classes = sorted([f.replace(".json", "") for f in os.listdir(STATIC_DIR) if f.endswith(".json") and f != "hello.json"])

label_map = {i: word for i, word in enumerate(classes)}

TRANS_PATH = os.path.join(BASE_DIR, "transformer_wlasl_100.h5")
LSTM_PATH = os.path.join(BASE_DIR, "bilstm_wlasl_100_optimized.h5")

model_trans = None
model_lstm = None

if os.path.exists(TRANS_PATH):
    print(f"Loading Transformer: {TRANS_PATH}")
    model_trans = load_model(TRANS_PATH)
if os.path.exists(LSTM_PATH):
    print(f"Loading BiLSTM: {LSTM_PATH}")
    model_lstm = load_model(LSTM_PATH)

print(f"Loaded {len(classes)} classes. Ready for live testing!")

# 2. MediaPipe Holistic Setup
mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

def extract_keypoints(results):
    pose = np.array([[res.x, res.y, res.z] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*3)
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return np.concatenate([pose, lh, rh])

def normalize_sequence(sequence):
    normalized_seq = []
    for frame in sequence:
        if np.all(frame == 0):
            normalized_seq.append(frame)
            continue
        nose_x, nose_y, nose_z = frame[0], frame[1], frame[2]
        ls_x, ls_y = frame[33], frame[34]
        rs_x, rs_y = frame[36], frame[37]
        shoulder_width = np.sqrt((ls_x - rs_x)**2 + (ls_y - rs_y)**2)
        if shoulder_width == 0: 
            shoulder_width = 1.0
            
        new_frame = np.zeros_like(frame)
        for i in range(0, len(frame), 3):
            if not (frame[i] == 0 and frame[i+1] == 0 and frame[i+2] == 0):
                new_frame[i] = (frame[i] - nose_x) / shoulder_width
                new_frame[i+1] = (frame[i+1] - nose_y) / shoulder_width
                new_frame[i+2] = (frame[i+2] - nose_z) / shoulder_width
        normalized_seq.append(new_frame)
    return np.array(normalized_seq)

def interpolate_sequence(sequence_array):
    df = pd.DataFrame(sequence_array).replace(0.0, np.nan)
    return df.interpolate(method='linear', limit_direction='both').fillna(0.0).to_numpy()

# 3. Live Capture Loop
sequence = []
top_preds = [("Initializing...", 0.0)]
threshold = 0.50
fps_history = []
prev_time = time.time()

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("\nStarting camera. Press 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    # Flip horizontally for natural mirror feel
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # FPS Calc
    curr_time = time.time()
    fps = 1.0 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 30.0
    prev_time = curr_time
    fps_history.append(fps)
    if len(fps_history) > 30: fps_history.pop(0)
    avg_fps = sum(fps_history) / len(fps_history)

    # MediaPipe Processing
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image_rgb.flags.writeable = False
    results = holistic.process(image_rgb)
    image_rgb.flags.writeable = True

    # Draw Landmarks
    mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                             mp_drawing.DrawingSpec(color=(80, 110, 10), thickness=2, circle_radius=2),
                             mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=2, circle_radius=1))
    mp_drawing.draw_landmarks(frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                             mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=3),
                             mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2))
    mp_drawing.draw_landmarks(frame, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                             mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=3),
                             mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))

    # Feature Buffering
    keypoints = extract_keypoints(results)
    sequence.append(keypoints)
    sequence = sequence[-60:]

    # Predict every 5 frames when buffer is full
    if len(sequence) == 60 and len(sequence) % 5 == 0:
        seq_array = np.array(sequence)
        smoothed = interpolate_sequence(seq_array)
        normalized = normalize_sequence(smoothed)
        inp = np.expand_dims(normalized, axis=0)

        if model_trans is not None and model_lstm is not None:
            p_t = model_trans.predict(inp, verbose=0)[0]
            p_l = model_lstm.predict(inp, verbose=0)[0]
            preds = 0.65 * p_t + 0.35 * p_l
        elif model_trans is not None:
            preds = model_trans.predict(inp, verbose=0)[0]
        else:
            preds = model_lstm.predict(inp, verbose=0)[0]

        top_indices = np.argsort(preds)[::-1][:3]
        top_preds = [(label_map.get(int(i), "Unknown"), float(preds[i])) for i in top_indices]

    # Render Glassmorphism Style HUD Overlay
    hud_overlay = frame.copy()
    cv2.rectangle(hud_overlay, (20, 20), (450, 190), (15, 23, 42), -1)
    cv2.rectangle(hud_overlay, (20, 20), (450, 190), (59, 130, 246), 2)
    cv2.addWeighted(hud_overlay, 0.85, frame, 0.15, 0, frame)

    # Title & FPS
    cv2.putText(frame, "ASL Ensemble Recognizer", (35, 50), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"FPS: {avg_fps:.1f} | Buffer: {len(sequence)}/60", (260, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (148, 163, 184), 1)

    # Top-1 Banner
    best_word, best_conf = top_preds[0]
    badge_color = (34, 197, 94) if best_conf >= threshold else (148, 163, 184)
    cv2.putText(frame, f"{best_word.upper()}", (35, 95), cv2.FONT_HERSHEY_DUPLEX, 1.1, badge_color, 2)
    cv2.putText(frame, f"{best_conf*100:.1f}%", (360, 95), cv2.FONT_HERSHEY_DUPLEX, 0.8, badge_color, 2)

    # Confidence Bar
    bar_width = int(400 * min(best_conf, 1.0))
    cv2.rectangle(frame, (35, 110), (435, 118), (30, 41, 59), -1)
    if bar_width > 0:
        cv2.rectangle(frame, (35, 110), (35 + bar_width, 118), badge_color, -1)

    # Candidates 2 and 3
    if len(top_preds) > 1:
        w2, c2 = top_preds[1]
        cv2.putText(frame, f"2. {w2}: {c2*100:.1f}%", (35, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (203, 213, 225), 1)
    if len(top_preds) > 2:
        w3, c3 = top_preds[2]
        cv2.putText(frame, f"3. {w3}: {c3*100:.1f}%", (35, 172), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (148, 163, 184), 1)

    cv2.imshow("Real-Time ASL Ensemble Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
holistic.close()