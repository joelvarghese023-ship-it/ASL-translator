import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Bidirectional, Dense, Masking, Input
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# 1. Configuration
FEATURE_DIR = "dataset/split_features"
MAX_FRAMES = 60  # Videos longer than 60 frames will be truncated; shorter will be padded
NUM_FEATURES = 225

def load_data(split):
    """Loads, pads, and labels the .npy sequences from the specified split directory."""
    X, y = [], []
    split_dir = os.path.join(FEATURE_DIR, split)
    
    # Create a sorted list of the 100 word classes to ensure consistent integer mapping
    classes = sorted(os.listdir(split_dir))
    label_map = {word: i for i, word in enumerate(classes)}
    
    for word in classes:
        word_dir = os.path.join(split_dir, word)
        if not os.path.isdir(word_dir): continue
            
        for file in os.listdir(word_dir):
            if file.endswith('.npy'):
                # Load the sequence (Shape: [frames, 225])
                sequence = np.load(os.path.join(word_dir, file))
                
                # Padding or Truncating to MAX_FRAMES
                if len(sequence) > MAX_FRAMES:
                    sequence = sequence[:MAX_FRAMES]
                elif len(sequence) < MAX_FRAMES:
                    padding = np.zeros((MAX_FRAMES - len(sequence), NUM_FEATURES))
                    sequence = np.vstack((sequence, padding))
                
                X.append(sequence)
                y.append(label_map[word])
                
    return np.array(X), np.array(y), label_map

# 2. Load the Datasets
print("Loading Training Data...")
X_train, y_train, label_map = load_data('train')

print("Loading Validation/Test Data...")
X_test, y_test, _ = load_data('test')

print(f"Training shapes - X: {X_train.shape}, y: {y_train.shape}")
print(f"Testing shapes - X: {X_test.shape}, y: {y_test.shape}")

# 3. Build the BiLSTM Architecture
model = Sequential([
    Input(shape=(MAX_FRAMES, NUM_FEATURES)),
    
    # Masking layer tells the network to ignore the 0.0 padding frames
    Masking(mask_value=0.0),
    
    # Bidirectional LSTMs to process temporal gestures forward and backward
    Bidirectional(LSTM(64, return_sequences=True)),
    Bidirectional(LSTM(128)),
    
    # Classification Head
    Dense(64, activation='relu'),
    Dense(100, activation='softmax')  # 100 output classes
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# 4. Define Callbacks
callbacks = [
    EarlyStopping(monitor='val_accuracy', patience=15, restore_best_weights=True),
    ModelCheckpoint("bilstm_wlasl_100.h5", monitor='val_accuracy', save_best_only=True)
]

# 5. Train the Model
history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=100,
    batch_size=32,
    callbacks=callbacks
)

print("Training complete. Best model saved as 'bilstm_wlasl_100.h5'.")