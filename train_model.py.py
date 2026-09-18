import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.utils import to_categorical

# 1. Setup Variables
sequence_length = 30 
features = 225       
actions = np.array(['hello', 'thanks', 'iloveyou'])
num_classes = len(actions)

print("Generating synthetic data for local testing...")

# 2. Generate Dummy Data
samples_per_action = 100 
total_samples = samples_per_action * num_classes
X = np.random.rand(total_samples, sequence_length, features)

y = np.repeat(np.arange(num_classes), samples_per_action)
y = to_categorical(y).astype(int) 

# 3. Build the LSTM Neural Network
print("Building model architecture...")
model = Sequential()
model.add(LSTM(64, return_sequences=True, activation='relu', input_shape=(sequence_length, features)))
model.add(Dropout(0.2))
model.add(LSTM(128, return_sequences=False, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(64, activation='relu'))
model.add(Dense(num_classes, activation='softmax')) 

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])

# 4. Train the Model 
print("Training the model...")
model.fit(X, y, epochs=50, batch_size=16, validation_split=0.2)

# 5. Save the standard Keras model
print("Saving model...")
model.save('model.h5')
print("Success! Saved as model.h5")