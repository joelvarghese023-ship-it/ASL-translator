# OmniSign 3D: Bidirectional American Sign Language (ASL) Studio

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![TensorFlow 2.16](https://img.shields.io/badge/TensorFlow-2.16-FF6F00?logo=tensorflow&logoColor=white)](https://tensorflow.org/)
[![Three.js](https://img.shields.io/badge/Three.js-r128-049EF4?logo=threedotjs&logoColor=white)](https://threejs.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Holistic-007FFF)](https://mediapipe.dev/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**OmniSign 3D** is a production-grade, bidirectional American Sign Language (ASL) translation system bridging communication between deaf and hearing communities. It provides simultaneous **Sign-to-Text** recognition via a high-accuracy neural ensemble and **Text-to-Sign** 3D motion synthesis via an expressive, stylized cartoon character ("Leo").

---

## 🌟 Key Highlights & Architecture

```mermaid
flowchart LR
    subgraph Sign2Text["Vision Recognition (Sign → Text)"]
        Cam["Webcam Stream"] --> MP["MediaPipe Holistic\n(225 Keypoints)"]
        MP --> Norm["Spatial Normalization\n& Linear Interpolation"]
        Norm --> Ensemble["Weighted Neural Ensemble\n• Transformer (65%)\n• BiLSTM (35%)"]
        Ensemble --> Pred["Top-5 Probabilities &\nLive Transcription Tape"]
        Pred --> TTS["Web Speech Audio (TTS)"]
    end

    subgraph Text2Sign["Motion Synthesis (Text → Sign)"]
        Input["Text / Word Input"] --> Engine["Kinematic Motion Engine\n(101 Static Datasets)"]
        Engine --> Interp["60 FPS Catmull-Rom\nSub-Frame Interpolation"]
        Interp --> Leo["🧑‍🎨 Cartoon Avatar 'Leo'\n• 21 Articulated Finger Joints\n• Procedural Pixar Eyes & Blinking\n• Dynamic Motion Trails"]
    end
```

### 1. 🧑‍🎨 Stylized 3D Cartoon Character ("Leo")
- **Pixar/Anime Aesthetic**: Rounded head, button nose, warm skin tone, chocolate brown hair tufts, and Pixar-style smile.
- **Natural Eye Blinking & Idle Breathing**: Irises with specular highlights, curved eyebrows, and automatic eyelid blinks every ~3.8 seconds with idle breathing physics.
- **Full 10-Finger Glove Articulation**: Crisp cartoon white gloves with **21 articulated joints and 23 bone segments per hand** for anatomically accurate finger spelling and gesture signing.
- **Avatar Selector**: Switch on-the-fly between 🧑‍🎨 **Cartoon Leo**, 🤖 **Cartoon Robo** (`avatar.glb`), and 🦾 **Cyber Hologram**.
- **Real-Time Outfit Customizer**: Change Leo's hoodie color instantly (Violet, Sky Blue, Emerald, Rose, Amber).
- **Dynamic Glowing Motion Ribbons**: Glowing fingertip trails tracing 3D trajectory arcs during signing motions.

### 2. 🧠 Neural Ensemble Recognition (Sign $\rightarrow$ Text)
- **High-Accuracy Ensemble**: Combines a Deep Spatial Transformer (65% weight) and an Optimized BiLSTM (35% weight) trained on the **WLASL-100 benchmark**, achieving **34.88% Top-1** and **67.83% Top-5** recognition accuracy.
- **Robust Coordinate Invariance**: Standardizes raw holistic landmarks with nose-centered translation, shoulder-width proportional scaling, and temporal linear interpolation for missing frames.
- **Ultra-Low Latency**: Sustained **~80ms inference latency** for smooth real-time continuous transcription.
- **Live Transcription Tape**: Automatically records high-confidence recognized gestures, provides one-click Text-to-Speech (TTS) audio playback, and allows instant click-to-replay on the 3D avatar.

### 3. 🎛️ Studio Controls & Export Tools
- **Playback Controls**: Variable playback speed (0.25x slow-mo to 2.0x), timeline scrubber, frame-by-frame stepping, and loop mode.
- **Media Capture**: Instant **PNG 3D Snapshot** export and **WebM Canvas Video Recorder** to capture signing animations.
- **Complete Keyboard Shortcuts**: Full hotkey control (`Space` play/pause, `←`/`→` frame stepping, `L` loop, `C` camera, `R` reset view, `V` vocabulary library).

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11 (recommended) or 3.10
- Modern Web Browser (Chrome, Edge, Firefox, Brave)
- Webcam (for gesture recognition)

### 1. Clone the Repository
```bash
git clone https://github.com/joelvarghese023-ship-it/ASL-translator.git
cd ASL-translator
```

### 2. Set Up Virtual Environment & Dependencies
```bash
# Create and activate virtual environment
python -m venv sign_lang_env

# On Windows:
.\sign_lang_env\Scripts\activate

# On macOS / Linux:
source sign_lang_env/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://localhost:5000
```

---

## 🖥️ Desktop OpenCV Camera Test

To run standalone real-time gesture recognition directly in an OpenCV desktop window:
```bash
python live_test.py
```
- Press `q` to quit.
- Shows real-time prediction banner, Top-5 candidate probabilities, and confidence gauge.

---

## 📡 REST API Reference

The backend exposes the following RESTful endpoints:

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/status` | `GET` | Server status, active models, ensemble weights, input shape. |
| `/api/health` | `GET` | Health check probe with server timestamp. |
| `/api/vocabulary` | `GET` | Returns list of all 100 supported sign words & category groupings. |
| `/api/predict` | `POST` | Accepts `{"landmarks": [...]}` (shape `60, 225`) and returns Top-5 predictions with latency. |
| `/api/get-motion` | `GET` / `POST` | Fetches 3D kinematic keyframe trajectories for a word or phrase (`?word=hello`). |

---

## 📚 Benchmark & Dataset

- **WLASL (World-Level American Sign Language)**: 100 benchmark classes spanning everyday signs (greetings, actions, objects, family, food, time, and descriptions).
- **Pre-Converted Static Dataset**: 101 signs included as JSON trajectories in `static_dataset/` for instant, offline 3D animation without needing the multi-gigabyte raw video dataset.

---

## ⌨️ Keyboard Shortcuts Reference

| Key | Action |
| :---: | :--- |
| <kbd>Space</kbd> | Toggle Play / Pause on 3D avatar |
| <kbd>&larr;</kbd> / <kbd>&rarr;</kbd> | Step backward / forward 1 frame |
| <kbd>L</kbd> | Toggle motion looping |
| <kbd>C</kbd> | Toggle camera video stream on/off |
| <kbd>R</kbd> | Reset 3D orbit camera perspective |
| <kbd>V</kbd> | Open / Close Vocabulary Library |
| <kbd>Esc</kbd> | Close active modal dialog |

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
