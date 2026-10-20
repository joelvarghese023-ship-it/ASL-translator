import os
import time
import json
os.environ["TF_USE_LEGACY_KERAS"] = "1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from tensorflow.keras.models import load_model

app = Flask(__name__, static_folder='.', template_folder='.')
CORS(app, resources={r"/api/*": {"origins": "*"}})

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset", "split_features", "train")
STATIC_DATASET_DIR = os.path.join(BASE_DIR, "static_dataset")
CLASSES_JSON_PATH = os.path.join(BASE_DIR, "classes.json")

# 1. Load Vocab / Classes (Classes.json primary for portable Git execution)
classes = []
if os.path.exists(CLASSES_JSON_PATH):
    try:
        with open(CLASSES_JSON_PATH, "r", encoding="utf-8") as f:
            classes = json.load(f)
    except Exception as e:
        print(f"Notice: Failed to read classes.json: {e}")

if not classes and os.path.exists(DATASET_DIR):
    classes = sorted([d for d in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, d))])
elif not classes and os.path.exists(STATIC_DATASET_DIR):
    classes = sorted([f.replace(".json", "") for f in os.listdir(STATIC_DATASET_DIR) if f.endswith(".json") and f != "hello.json"])

label_map = {i: word for i, word in enumerate(classes)}

# Vocabulary Categories for UI Filtering
CATEGORIES = {
    "Greetings & Basics": ["hello", "fine", "yes", "no", "help", "now", "later", "right", "wrong", "same"],
    "Questions & Communication": ["what", "who", "how", "tell", "language", "letter", "meet", "hearing", "deaf"],
    "Actions & Verbs": ["eat", "drink", "walk", "dance", "play", "study", "work", "give", "go", "pull", "cook", "paint", "change", "decide", "finish", "forget", "want", "need", "like", "enjoy"],
    "People & Family": ["family", "mother", "son", "woman", "man", "doctor", "secretary", "cousin"],
    "Objects & Things": ["book", "computer", "chair", "table", "bed", "clothes", "shirt", "jacket", "hat", "paper", "medicine"],
    "Food & Dining": ["apple", "candy", "pizza", "fish", "corn", "drink", "eat"],
    "Time & Colors": ["time", "year", "thursday", "birthday", "thanksgiving", "black", "blue", "brown", "color", "orange", "pink", "purple", "white", "dark", "cool", "hot"],
    "Animals & Nature": ["bird", "cow", "dog", "city", "africa"],
    "Descriptions": ["full", "tall", "short", "thin", "last", "before", "many", "all"]
}

# 2. Load Models (Ensemble for maximum accuracy)
model_transformer = None
model_bilstm = None

TRANS_MODEL_PATH = os.path.join(BASE_DIR, "transformer_wlasl_100.h5")
LSTM_MODEL_PATH = os.path.join(BASE_DIR, "bilstm_wlasl_100_optimized.h5")

if os.path.exists(TRANS_MODEL_PATH):
    try:
        print(f"Loading Transformer model from {TRANS_MODEL_PATH}...")
        model_transformer = load_model(TRANS_MODEL_PATH)
        print("Transformer loaded successfully.")
    except Exception as e:
        print(f"Failed to load Transformer: {e}")

if os.path.exists(LSTM_MODEL_PATH):
    try:
        print(f"Loading BiLSTM model from {LSTM_MODEL_PATH}...")
        model_bilstm = load_model(LSTM_MODEL_PATH)
        print("BiLSTM loaded successfully.")
    except Exception as e:
        print(f"Failed to load BiLSTM: {e}")

def normalize_sequence(sequence):
    """
    Centers coordinates to the nose and scales by shoulder width.
    Matches the exact training normalization pipeline.
    """
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
    """Interpolates dropped or missing landmarks smoothly across frames."""
    df = pd.DataFrame(sequence_array).replace(0.0, np.nan)
    return df.interpolate(method='linear', limit_direction='both').fillna(0.0).to_numpy()

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "status": "online",
        "models": {
            "transformer": model_transformer is not None,
            "bilstm": model_bilstm is not None,
            "ensemble_active": (model_transformer is not None and model_bilstm is not None)
        },
        "ensemble_weights": {"transformer": 0.65, "bilstm": 0.35},
        "num_classes": len(classes),
        "input_shape": [60, 225]
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "models_loaded": {
            "transformer": model_transformer is not None,
            "bilstm": model_bilstm is not None
        }
    })

@app.route('/api/vocabulary', methods=['GET'])
@app.route('/api/classes', methods=['GET'])
def get_vocabulary():
    return jsonify({
        "count": len(classes),
        "classes": classes,
        "categories": CATEGORIES
    })

# Endpoint 1: ASL -> Text (Inference with Ensemble & Top-K)
@app.route('/api/predict', methods=['POST'])
def predict():
    t_start = time.time()
    payload = request.get_json(silent=True) or {}
    data = payload.get("landmarks")
    
    if not data or len(data) == 0:
        return jsonify({"error": "No landmark sequence provided"}), 400

    try:
        seq = np.array(data, dtype=np.float32)
    except Exception as e:
        return jsonify({"error": f"Failed to parse landmarks array: {str(e)}"}), 400

    if seq.ndim != 2 or seq.shape[1] != 225:
        return jsonify({"error": f"Invalid landmark shape {seq.shape}. Expected (N, 225)"}), 400
    
    # Handle length adjustments to 60 frames
    if len(seq) > 60:
        seq = seq[-60:]
    elif len(seq) < 60:
        padding = np.zeros((60 - len(seq), 225), dtype=np.float32)
        seq = np.vstack((seq, padding))

    # 1. Temporal Interpolation
    smoothed = interpolate_sequence(seq)
    
    # 2. Spatial Normalization (Centers to nose, scales to shoulder width)
    normalized = normalize_sequence(smoothed)
    input_tensor = np.expand_dims(normalized, axis=0)

    # 3. Model Inference (Ensemble for maximum accuracy)
    preds = None
    if model_transformer is not None and model_bilstm is not None:
        p_trans = model_transformer.predict(input_tensor, verbose=0)[0]
        p_lstm = model_bilstm.predict(input_tensor, verbose=0)[0]
        # Weighted Ensemble: 65% Transformer + 35% BiLSTM
        preds = 0.65 * p_trans + 0.35 * p_lstm
    elif model_transformer is not None:
        preds = model_transformer.predict(input_tensor, verbose=0)[0]
    elif model_bilstm is not None:
        preds = model_bilstm.predict(input_tensor, verbose=0)[0]
    else:
        return jsonify({"error": "No trained model currently available on server"}), 503

    # 4. Top-K Ranking
    top_indices = np.argsort(preds)[::-1][:5]
    top_predictions = [
        {
            "word": label_map.get(int(idx), f"Class {idx}"),
            "confidence": float(preds[idx]),
            "percent": round(float(preds[idx]) * 100, 1)
        }
        for idx in top_indices
    ]

    best_idx = int(top_indices[0])
    best_confidence = float(preds[best_idx])
    latency_ms = round((time.time() - t_start) * 1000, 1)

    return jsonify({
        "prediction": label_map.get(best_idx, "Unknown"),
        "confidence": best_confidence,
        "percent": round(best_confidence * 100, 1),
        "top_predictions": top_predictions,
        "latency_ms": latency_ms
    })

# Endpoint 2: Text -> ASL (Motion Playback supporting words and sentences)
@app.route('/api/get-motion', methods=['GET', 'POST'])
@app.route('/api/motion', methods=['GET', 'POST'])
def get_motion():
    query = ""
    if request.method == 'POST':
        body = request.get_json(silent=True) or {}
        query = body.get('word', body.get('sentence', '')).strip().lower()
    else:
        query = request.args.get('word', '').strip().lower()
        if not query:
            query = request.args.get('sentence', '').strip().lower()

    if not query:
        return jsonify({"error": "Please specify 'word' or 'sentence' query parameter"}), 400

    words = [w for w in query.replace(',', ' ').replace('.', ' ').split() if w]
    result_motions = []

    for word in words:
        # Check static JSON first (fastest)
        static_json_path = os.path.join(STATIC_DATASET_DIR, f"{word}.json")
        if os.path.exists(static_json_path):
            import json
            with open(static_json_path, 'r') as f:
                content = json.load(f)
                result_motions.append(content)
                continue

        # Check raw npy in train folder
        word_dir = os.path.join(DATASET_DIR, word)
        if os.path.exists(word_dir):
            npy_files = [f for f in os.listdir(word_dir) if f.endswith('.npy')]
            if npy_files:
                sequence = np.load(os.path.join(word_dir, npy_files[0])).tolist()
                result_motions.append({"word": word, "frames": sequence})

    if not result_motions:
        return jsonify({
            "error": f"No signs found matching query: '{query}'",
            "available_words": classes[:15]
        }), 404

    if len(result_motions) == 1:
        return jsonify(result_motions[0])
    else:
        return jsonify({
            "sentence": " ".join(words),
            "words": [m["word"] for m in result_motions],
            "motions": result_motions
        })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting ASL Translator Backend on http://localhost:{port} with {len(classes)} classes...")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)