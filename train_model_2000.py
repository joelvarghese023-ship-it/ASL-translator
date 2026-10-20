import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    Input, Dense, Dropout, LayerNormalization, 
    MultiHeadAttention, GlobalAveragePooling1D, Add, Conv1D
)
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau

# Check GPU acceleration
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print(f"TensorFlow GPU Acceleration Enabled on {len(gpus)} device(s): {gpus}")
else:
    print("Running on CPU.")

FEATURE_DIR = "dataset/split_features"
CLASSES_2000_PATH = "classes_2000.json"
MAX_FRAMES = 60
NUM_FEATURES = 225

# Load 2000 class vocabulary
if os.path.exists(CLASSES_2000_PATH):
    with open(CLASSES_2000_PATH, "r") as f:
        classes = json.load(f)
else:
    train_dir = os.path.join(FEATURE_DIR, "train")
    classes = sorted([d for d in os.listdir(train_dir) if os.path.isdir(os.path.join(train_dir, d))])

NUM_CLASSES = len(classes)
label_map = {word: i for i, word in enumerate(classes)}
print(f"Loaded {NUM_CLASSES} classes for Full WLASL-2000 training.")

def normalize_sequence(sequence):
    """Centers coordinates to the nose and scales by shoulder width."""
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

def augment_sequence(sequence, noise_level=0.02):
    """Applies Spatial Jitter AND Temporal Frame Dropping for data augmentation."""
    noise = np.random.normal(0, noise_level, sequence.shape)
    mask = sequence != 0  
    sequence = sequence + (noise * mask)
    
    if np.random.rand() > 0.5:
        valid_frames = len([f for f in sequence if not np.all(f == 0)])
        if valid_frames > 15:
            drop_count = int(valid_frames * np.random.uniform(0.1, 0.25))
            drop_indices = np.random.choice(valid_frames, drop_count, replace=False)
            sequence = np.delete(sequence, drop_indices, axis=0)
            
    return sequence

def load_data(split, augment=False):
    X, y = [], []
    split_dir = os.path.join(FEATURE_DIR, split)
    if not os.path.exists(split_dir):
        return np.array([]), np.array([])
    
    for word in os.listdir(split_dir):
        if word not in label_map:
            continue
        word_dir = os.path.join(split_dir, word)
        if not os.path.isdir(word_dir):
            continue
            
        for file in os.listdir(word_dir):
            if file.endswith('.npy'):
                sequence = np.load(os.path.join(word_dir, file))
                sequence = normalize_sequence(sequence)
                
                if augment:
                    sequence = augment_sequence(sequence)
                    
                if len(sequence) > MAX_FRAMES:
                    sequence = sequence[:MAX_FRAMES]
                elif len(sequence) < MAX_FRAMES:
                    padding = np.zeros((MAX_FRAMES - len(sequence), NUM_FEATURES))
                    sequence = np.vstack((sequence, padding))
                
                X.append(sequence)
                y.append(label_map[word])
                
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int32)

print("Loading training and validation features...")
X_train, y_train = load_data('train', augment=True)
X_val, y_val = load_data('val', augment=False)
if len(X_val) == 0:
    X_val, y_val = load_data('test', augment=False)

print(f"Loaded {len(X_train)} training samples and {len(X_val)} validation samples.")

# --- SCALED DEEP TRANSFORMER ARCHITECTURE FOR 2,000 CLASSES ---
def transformer_encoder(inputs, head_size=128, num_heads=8, ff_dim=256, dropout=0.3):
    x = LayerNormalization(epsilon=1e-6)(inputs)
    x = MultiHeadAttention(key_dim=head_size, num_heads=num_heads, dropout=dropout)(x, x)
    x = Dropout(dropout)(x)
    res = Add()([x, inputs])

    x = LayerNormalization(epsilon=1e-6)(res)
    x = Dense(ff_dim, activation="relu")(x)
    x = Dropout(dropout)(x)
    x = Dense(inputs.shape[-1])(x)
    return Add()([x, res])

inputs = Input(shape=(MAX_FRAMES, NUM_FEATURES))

# Positional Encoding 1D Conv
x = Conv1D(filters=128, kernel_size=3, padding="same", activation="relu")(inputs)

# 3 Stacked Transformer Blocks
x = transformer_encoder(x, head_size=128, num_heads=8, ff_dim=256, dropout=0.3)
x = transformer_encoder(x, head_size=128, num_heads=8, ff_dim=256, dropout=0.3)
x = transformer_encoder(x, head_size=128, num_heads=8, ff_dim=256, dropout=0.3)

# Global Temporal Pooling & Dense Classification Head
x = GlobalAveragePooling1D()(x)
x = LayerNormalization(epsilon=1e-6)(x)
x = Dropout(0.4)(x)
x = Dense(256, activation="relu")(x)
x = Dropout(0.4)(x)
outputs = Dense(NUM_CLASSES, activation="softmax")(x)

model = Model(inputs, outputs)
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy', tf.keras.metrics.SparseTopKCategoricalAccuracy(k=5, name='top_5_accuracy')]
)
model.summary()

callbacks = [
    EarlyStopping(monitor='val_accuracy', patience=25, restore_best_weights=True),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=8, min_lr=1e-5),
    ModelCheckpoint("transformer_wlasl_2000.h5", monitor='val_accuracy', save_best_only=True)
]

print("Starting Full WLASL-2000 Model Training...")
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=120,
    batch_size=64,
    callbacks=callbacks
)

print("\nTraining complete! Best 2,000-class model saved as 'transformer_wlasl_2000.h5'.")
