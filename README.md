# Real-Time ASL Translator (MediaPipe + Transformers)

A lightweight, real-time American Sign Language (ASL) recognition system that translates live webcam gestures into English text. 

Traditional sign language translation models often rely on computationally heavy 3D-CNNs to process raw video pixels, making them impossible to run on standard local hardware. This project bypasses raw video entirely. It acts as a spatiotemporal dimensionality reduction pipeline, using MediaPipe to extract 3D skeletal landmarks and a custom Transformer neural network to classify the temporal sequence of those coordinates. 

The current model is trained to recognize the 100 most common words from the Word-Level American Sign Language (WLASL-100) dataset and is optimized for low-latency CPU inference.

## Key Features & Pipeline

* **3D Feature Extraction:** Utilizes MediaPipe Holistic to extract 75 specific joints per frame (33 pose, 21 left-hand, 21 right-hand). A 60-frame video is flattened into a lightweight `(60, 225)` mathematical matrix, stripping away background noise and lighting conditions.
* **Reference-Based Spatial Normalization:** To prevent the model from overfitting to a specific camera distance or a signer's body type, the pipeline dynamically anchors every frame's coordinates to the nose (translation invariance) and scales all points by the signer's shoulder width (size invariance).
* **Temporal Data Augmentation:** The training pipeline applies spatial Gaussian jitter and random temporal frame-dropping (time warping). This forces the network to recognize the geometric shape of the sign regardless of whether it is performed slowly or at double speed.
* **Transformer Architecture:** Replaced a baseline BiLSTM (which suffered from vanishing gradients on 60-frame sequences) with a modern Transformer. A `Conv1D` layer encodes chronological order, while Multi-Head Attention blocks analyze all 60 frames simultaneously to calculate which micro-movements carry the most semantic weight.
* **Inference Optimization:** The real-time loop uses a 60-frame rolling window with linear interpolation to mathematically estimate and patch missing hand coordinates when MediaPipe drops tracking.

## Performance
* **Baseline BiLSTM:** ~14.7% validation accuracy (suffered from severe overfitting on raw absolute coordinates).
* **Optimized Transformer:** **~30.6% validation accuracy** across 100 classes. The integration of 50% Dropout layers, spatial normalization, and temporal augmentation successfully forced the model to generalize the physical mechanics of the signs.
