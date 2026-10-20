import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Dropout, LayerNormalization, MultiHeadAttention, GlobalAveragePooling1D, Add, Conv1D
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
            
        nose_x, nose_y, nose_z = frame[0], frame[1], frame[2]
        ls_x, ls_y = frame[33], frame[34]
        rs_x, rs_y = frame[36], frame[37]
        
        shoulder_width = np.sqrt((ls_x - rs_x)**2 + (ls_y - rs_y)**2)
        if shoulder_width == 0: shoulder_width = 1.0
            
        new_frame = np.zeros_like(frame)
        for i in range(0, len(frame), 3):
            if not (frame[i] == 0 and frame[i+1] == 0 and frame[i+2] == 0):
                new_frame[i] = (frame[i] - nose_x) / shoulder_width
                new_frame[i+1] = (frame[i+1] - nose_y) / shoulder_width
                new_frame[i+2] = (frame[i+2] - nose_z) / shoulder_width
                
        normalized_seq.append(new_frame)
    return np.array(normalized_seq)

def augment_sequence(sequence, noise_level=0.03):
    """Applies Spatial Jitter AND Temporal Warping (Frame Dropping)."""
    # 1. Spatial Jitter
    noise = np.random.normal(0, noise_level, sequence.shape)
    mask = sequence != 0  
    sequence = sequence + (noise * mask)
    
    # 2. Temporal Warping (Simulates faster signing speeds)
    if np.random.rand() > 0.5:
        # Find how many actual frames exist before padding
        valid_frames = len([f for f in sequence if not np.all(f == 0)])
        if valid_frames > 15:
            # Randomly drop 10% to 30% of the frames
            drop_count = int(valid_frames * np.random.uniform(0.1, 0.3))
            drop_indices = np.random.choice(valid_frames, drop_count, replace=False)
            sequence = np.delete(sequence, drop_indices, axis=0)
            
    return sequence

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
                sequence = normalize_sequence(sequence)
                
                if augment:
                    sequence = augment_sequence(sequence)
                    
                # Pad or Truncate back to MAX_FRAMES
                if len(sequence) > MAX_FRAMES:
                    sequence = sequence[:MAX_FRAMES]
                elif len(sequence) < MAX_FRAMES:
                    padding = np.zeros((MAX_FRAMES - len(sequence), NUM_FEATURES))
                    sequence = np.vstack((sequence, padding))
                
                X.append(sequence)
                y.append(label_map[word])
                
    return np.array(X), np.array(y), label_map

print("Loading and Augmenting Data...")
X_train, y_train, label_map = load_data('train', augment=True)
X_test, y_test, _ = load_data('test', augment=False)

# --- TRANSFORMER ARCHITECTURE ---

def transformer_encoder(inputs, head_size, num_heads, ff_dim, dropout=0.4):
    """Creates a single Transformer block."""
    # Attention Layer
    x = LayerNormalization(epsilon=1e-6)(inputs)
    x = MultiHeadAttention(key_dim=head_size, num_heads=num_heads, dropout=dropout)(x, x)
    x = Dropout(dropout)(x)
    res = Add()([x, inputs]) # Residual Connection

    # Feed Forward Layer
    x = LayerNormalization(epsilon=1e-6)(res)
    x = Dense(ff_dim, activation="relu")(x)
    x = Dropout(dropout)(x)
    x = Dense(inputs.shape[-1])(x)
    x = Add()([x, res])
    return x

inputs = Input(shape=(MAX_FRAMES, NUM_FEATURES))

# 1D Convolution adds "Positional Encoding" so the Transformer understands time order
x = Conv1D(filters=128, kernel_size=3, padding="same", activation="relu")(inputs)

# Stacked Transformer Blocks
x = transformer_encoder(x, head_size=128, num_heads=4, ff_dim=256, dropout=0.4)
x = transformer_encoder(x, head_size=128, num_heads=4, ff_dim=256, dropout=0.4)

# Pool the 60 frames down into a single prediction vector
x = GlobalAveragePooling1D()(x)
x = Dropout(0.5)(x)
x = Dense(128, activation="relu")(x)
x = Dropout(0.5)(x)
outputs = Dense(100, activation="softmax")(x)

model = Model(inputs, outputs)
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.summary()

callbacks = [
    EarlyStopping(monitor='val_accuracy', patience=30, restore_best_weights=True),
    ModelCheckpoint("transformer_wlasl_100.h5", monitor='val_accuracy', save_best_only=True)
]

history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=150,
    batch_size=32,
    callbacks=callbacks
)

print("Training complete. Best model saved as 'transformer_wlasl_100.h5'.")