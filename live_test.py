import cv2
import numpy as np
import mediapipe as mp
from tensorflow.keras.models import load_model
import os

# 1. Load the Optimized Model
model = load_model('bilstm_wlasl_100_optimized.h5')
classes = sorted(os.listdir("dataset/split_features/train"))
label_map = {i: word for i, word in enumerate(classes)}

# 2. Initialize MediaPipe
mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)

def extract_keypoints(results):
    pose = np.array([[res.x, res.y, res.z] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*3)
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return np.concatenate([pose, lh, rh])

def normalize_frame(frame):
    """Applies the exact same spatial normalization used during training."""
    if np.all(frame == 0):
        return frame
        
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
            
    return new_frame

# 3. Real-Time Loop
sequence = []
current_prediction = "Waiting..."
threshold = 0.6  # Raised threshold since the optimized model is more confident

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    # MediaPipe Prediction
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = holistic.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Draw Landmarks
    mp.solutions.drawing_utils.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
    mp.solutions.drawing_utils.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
    mp.solutions.drawing_utils.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

    # Sequence Logic with Normalization
    keypoints = extract_keypoints(results)
    normalized_keypoints = normalize_frame(keypoints)
    
    sequence.append(normalized_keypoints)
    sequence = sequence[-60:] 

    if len(sequence) == 60:
        res = model.predict(np.expand_dims(sequence, axis=0), verbose=0)[0]
        if res[np.argmax(res)] > threshold:
            current_prediction = label_map[np.argmax(res)]

    # Display Overlay
    cv2.rectangle(image, (0,0), (640, 40), (0, 0, 0), -1)
    cv2.putText(image, f'Prediction: {current_prediction}', (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow('Live ASL Translator', image)

    # Press 'q' to quit
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()