import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Bidirectional, Dense, Masking, Input, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

FEATURE_DIR = "dataset/split_features"
MAX_FRAMES = 60
NUM_FEATURES = 225

def normalize_sequence(sequence):
    """Centers coordinates to the nose and scales by shoulder width."""
    normalized_seq = []
    for frame in sequence:
        if np.all(frame == 0):
            normalized_seq.append(frame)
            continue
            
        # Nose is index 0 (x, y, z)
        nose_x, nose_y, nose_z = frame[0], frame[1], frame[2]
        
        # Left shoulder (index 11) & Right shoulder (index 12)
        ls_x, ls_y = frame[33], frame[34]
        rs_x, rs_y = frame[36], frame[37]
        
        # Calculate shoulder width for uniform scaling
        shoulder_width = np.sqrt((ls_x - rs_x)**2 + (ls_y - rs_y)**2)
        if shoulder_width == 0: 
            shoulder_width = 1.0
            
        new_frame = np.zeros_like(frame)
        for i in range(0, len(frame), 3):
            # Only normalize validly detected landmarks
            if not (frame[i] == 0 and frame[i+1] == 0 and frame[i+2] == 0):
                new_frame[i] = (frame[i] - nose_x) / shoulder_width
                new_frame[i+1] = (frame[i+1] - nose_y) / shoulder_width
                new_frame[i+2] = (frame[i+2] - nose_z) / shoulder_width
                
        normalized_seq.append(new_frame)
    return np.array(normalized_seq)

def augment_sequence(sequence, noise_level=0.03):
    """Injects random spatial jitter to simulate different camera angles."""
    noise = np.random.normal(0, noise_level, sequence.shape)
    mask = sequence != 0  # Do not add noise to padded zeroes
    return sequence + (noise * mask)

def load_data(split, augment=False):
    X, y = [], []
    split_dir = os.path.join(FEATURE_DIR, split)
    classes = sorted(os.listdir(split_dir))
    label_map = {word: i for i, word in enumerate(classes)}
    
    for word in classes:
        word_dir = os.path.join(split_dir, word)
        if not os.path.isdir(word_dir): continue
            
        for file in os.listdir(word_dir):
            if file.endswith('.npy'):
                sequence = np.load(os.path.join(word_dir, file))
                
                # Apply Normalization
                sequence = normalize_sequence(sequence)
                
                # Apply Augmentation (Training Only)
                if augment:
                    sequence = augment_sequence(sequence)
                    
                # Pad or Truncate
                if len(sequence) > MAX_FRAMES:
                    sequence = sequence[:MAX_FRAMES]
                elif len(sequence) < MAX_FRAMES:
                    padding = np.zeros((MAX_FRAMES - len(sequence), NUM_FEATURES))
                    sequence = np.vstack((sequence, padding))
                
                X.append(sequence)
                y.append(label_map[word])
                
    return np.array(X), np.array(y), label_map

print("Loading Training Data (Applying Normalization & Jitter)...")
X_train, y_train, label_map = load_data('train', augment=True)

print("Loading Validation/Test Data (Normalization only)...")
X_test, y_test, _ = load_data('test', augment=False)

# Build the Optimized Architecture
model = Sequential([
    Input(shape=(MAX_FRAMES, NUM_FEATURES)),
    Masking(mask_value=0.0),
    
    Bidirectional(LSTM(128, return_sequences=True)),
    Dropout(0.5), # Force network to generalize
    Bidirectional(LSTM(256)),
    Dropout(0.5),
    
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(100, activation='softmax')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.summary()

callbacks = [
    EarlyStopping(monitor='val_accuracy', patience=25, restore_best_weights=True),
    ModelCheckpoint("bilstm_wlasl_100_optimized.h5", monitor='val_accuracy', save_best_only=True)
]

history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=150,
    batch_size=32,
    callbacks=callbacks
)

print("Training complete. Best model saved as 'bilstm_wlasl_100_optimized.h5'.")