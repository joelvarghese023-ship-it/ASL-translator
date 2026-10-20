import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import time
import json
import tempfile
import cv2
import mediapipe as mp

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

# ================= SENTENCE NLP & KINEMATIC COMPILER =================
SYNONYMS = {
    # Greetings & Politeness
    "hi": "hello", "hey": "hello", "greetings": "hello", "welcome": "hello",
    "okay": "fine", "ok": "fine", "good": "fine", "great": "fine", "alright": "fine",
    "yeah": "yes", "yep": "yes", "sure": "yes",
    "nope": "no", "nah": "no", "negative": "no",
    "assist": "help", "assistance": "help", "aid": "help",
    # Verbs
    "eats": "eat", "eating": "eat", "ate": "eat", "eaten": "eat", "food": "eat", "meal": "eat", "dinner": "eat", "lunch": "eat", "breakfast": "eat",
    "drinks": "drink", "drinking": "drink", "drank": "drink", "drunk": "drink", "water": "drink", "beverage": "drink",
    "walks": "walk", "walking": "walk", "walked": "walk", "stroll": "walk",
    "dances": "dance", "dancing": "dance", "danced": "dance",
    "plays": "play", "playing": "play", "played": "play", "game": "play",
    "studies": "study", "studying": "study", "studied": "study", "learn": "study", "learning": "study",
    "works": "work", "working": "work", "worked": "work", "job": "work",
    "gives": "give", "giving": "give", "gave": "give", "given": "give",
    "goes": "go", "going": "go", "went": "go", "gone": "go", "leave": "go",
    "pulls": "pull", "pulling": "pull", "pulled": "pull",
    "cooks": "cook", "cooking": "cook", "cooked": "cook",
    "paints": "paint", "painting": "paint", "painted": "paint",
    "changes": "change", "changing": "change", "changed": "change",
    "decides": "decide", "deciding": "decide", "decided": "decide",
    "finishes": "finish", "finishing": "finish", "finished": "finish", "done": "finish",
    "forgets": "forget", "forgetting": "forget", "forgot": "forget", "forgotten": "forget",
    "wants": "want", "wanting": "want", "wanted": "want", "wish": "want",
    "needs": "need", "needing": "need", "needed": "need", "require": "need",
    "likes": "like", "liking": "like", "liked": "like", "love": "like",
    "enjoys": "enjoy", "enjoying": "enjoy", "enjoyed": "enjoy",
    "tells": "tell", "telling": "tell", "told": "tell", "say": "tell", "speak": "tell",
    "meets": "meet", "meeting": "meet", "met": "meet",
    # People & Family
    "families": "family", "household": "family",
    "mom": "mother", "mommy": "mother", "mama": "mother", "female": "woman",
    "dad": "man", "daddy": "man", "father": "man", "boy": "man", "guy": "man",
    "women": "woman", "girl": "woman", "lady": "woman",
    "men": "man", "gentleman": "man",
    "sons": "son", "kid": "son", "child": "son", "children": "son",
    "doctors": "doctor", "physician": "doctor", "medic": "doctor",
    "secretaries": "secretary", "assistant": "secretary",
    "cousins": "cousin", "relative": "cousin",
    # Objects
    "books": "book", "reading": "book",
    "computers": "computer", "laptop": "computer", "pc": "computer",
    "chairs": "chair", "seat": "chair",
    "tables": "table", "desk": "table",
    "beds": "bed", "mattress": "bed", "sleep": "bed",
    "clothes": "clothes", "clothing": "clothes", "garment": "clothes",
    "shirts": "shirt", "top": "shirt",
    "jackets": "jacket", "coat": "jacket",
    "hats": "hat", "cap": "hat",
    "papers": "paper", "document": "paper",
    "medicines": "medicine", "pill": "medicine", "drugs": "medicine",
    # Food
    "apples": "apple", "candies": "candy", "sweet": "candy", "sweets": "candy",
    "pizzas": "pizza", "fishes": "fish", "corns": "corn",
    # Animals & Places
    "birds": "bird", "cows": "cow", "cattle": "cow", "dogs": "dog", "puppy": "dog", "puppies": "dog",
    "cities": "city", "town": "city", "village": "city",
    # Time & Modifiers
    "times": "time", "clock": "time", "hour": "time",
    "years": "year", "annual": "year",
    "colors": "color",
    "correct": "right", "true": "right",
    "incorrect": "wrong", "false": "wrong",
    "lots": "many", "much": "many",
    "every": "all", "everything": "all", "everyone": "all"
}

STOP_WORDS = {
    'i', 'me', 'my', 'you', 'your', 'he', 'she', 'it', 'we', 'they', 'them',
    'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being',
    'the', 'a', 'an', 'to', 'of', 'in', 'on', 'at', 'by', 'for', 'with', 'about',
    'into', 'through', 'during', 'above', 'below', 'from', 'up', 'down', 'out',
    'off', 'over', 'under', 'then', 'so', 'than', 'too', 'very', 'just', 'do', 'does', 'did',
    'please', 'and'
}

def blend_motion_frames(f1, f2, steps=8):
    """Generates smooth ease-in-out transitional frames between consecutive signs."""
    blended = []
    a1 = np.array(f1, dtype=np.float32)
    a2 = np.array(f2, dtype=np.float32)
    for s in range(1, steps + 1):
        t = s / (steps + 1.0)
        alpha = 3.0 * t * t - 2.0 * t * t * t
        frame = (1.0 - alpha) * a1 + alpha * a2
        blended.append(frame.tolist())
    return blended

def parse_text_to_asl_glosses(raw_text):
    """Transforms raw English sentence into ASL gloss sequence."""
    cleaned = ''.join(c.lower() if c.isalnum() or c.isspace() else ' ' for c in raw_text)
    tokens = [w for w in cleaned.split() if w]
    glosses = []
    skipped = []
    vocab_set = set(classes)
    vocab_set.add("hello")

    for token in tokens:
        mapped = SYNONYMS.get(token, token)
        if mapped in vocab_set:
            if not glosses or glosses[-1] != mapped:
                glosses.append(mapped)
        elif token in STOP_WORDS:
            skipped.append(token)
        else:
            skipped.append(token)

    return glosses, skipped

def load_word_frames(word):
    """Loads landmark trajectory frames for a single ASL sign."""
    # Check static JSON first
    static_json_path = os.path.join(STATIC_DATASET_DIR, f"{word}.json")
    if os.path.exists(static_json_path):
        try:
            with open(static_json_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                return content.get("frames", [])
        except Exception:
            pass

    # Check raw npy
    word_dir = os.path.join(DATASET_DIR, word)
    if os.path.exists(word_dir):
        npy_files = [f for f in os.listdir(word_dir) if f.endswith('.npy')]
        if npy_files:
            return np.load(os.path.join(word_dir, npy_files[0])).tolist()
    return []

def assemble_english_sentence(glosses):
    """Translates sequence of ASL glosses into a grammatically natural English sentence."""
    if not glosses:
        return ""
    words = [w.lower().strip() for w in glosses if w.strip()]
    if not words:
        return ""

    # Common ASL idioms & greetings
    if "hello" in words:
        if len(words) == 1:
            return "Hello!"
        if "meet" in words:
            remainder = [w for w in words if w not in ("hello", "meet")]
            if "family" in remainder:
                return "Hello, nice to meet your family!"
            return "Hello, nice to meet you!"

    is_question = words[0] in ("what", "who", "how", "where", "why")

    singular_subjects = {
        "mother", "son", "woman", "man", "doctor", "secretary", "cousin", "family",
        "dog", "cow", "bird", "he", "she", "who", "someone", "everyone"
    }
    nouns = {
        "mother", "son", "woman", "man", "doctor", "secretary", "cousin", "family",
        "dog", "cow", "bird", "computer", "chair", "table", "bed", "book", "paper",
        "medicine", "apple", "candy", "pizza", "fish", "corn", "city", "africa", "basketball"
    }
    verbs = {
        "eat", "drink", "walk", "dance", "play", "study", "work", "give", "go",
        "pull", "cook", "paint", "change", "decide", "finish", "forget", "want",
        "need", "like", "enjoy", "tell", "meet", "help"
    }

    out = []
    last_was_singular_subj = False

    for i, w in enumerate(words):
        if i == 0:
            if w in ("what", "who", "how", "where", "why"):
                out.append(w.capitalize())
                last_was_singular_subj = (w in ("who", "what"))
                continue
            if w == "hello":
                out.append("Hello,")
                continue
            if w in nouns:
                prefix = "" if w in ("mother", "family") else "The "
                out.append(prefix + (w.capitalize() if not prefix else w))
                last_was_singular_subj = (w in singular_subjects)
                continue

        if w in verbs:
            prev_token = out[-1].lower() if out else ""
            if any(prev_token.endswith(base) or prev_token.endswith(base + "s") or prev_token.endswith(base + "es") for base in ("want", "need", "decide", "like", "forget")):
                out.append("to " + w)
                last_was_singular_subj = False
                continue
            if any(prev_token.endswith(base) or prev_token.endswith(base + "s") for base in ("enjoy",)):
                gerund = w + "ing" if not w.endswith("e") else w[:-1] + "ing"
                out.append(gerund)
                last_was_singular_subj = False
                continue
            if last_was_singular_subj:
                inflected = w + "es" if w.endswith(("ch", "sh", "s", "x", "z", "o")) else (w[:-1] + "ies" if w.endswith("y") and w[-2] not in "aeiou" else w + "s")
                out.append(inflected)
                last_was_singular_subj = False
                continue
            out.append(w)
            last_was_singular_subj = False
            continue

        if w in nouns:
            if w in ("apple", "orange"):
                out.append("an " + w)
            elif w in ("book", "computer", "pizza", "chair", "table", "jacket", "shirt", "doctor", "dog"):
                out.append("a " + w)
            elif w in ("medicine", "water", "corn", "candy", "basketball"):
                out.append(w)
            else:
                out.append(w)
            last_was_singular_subj = (w in singular_subjects)
            continue

        out.append(w)

    res = " ".join(out).strip()
    res = res.replace(" ,", ",").replace("  ", " ")
    res = res[0].upper() + res[1:] if len(res) > 0 else res
    if not res.endswith((".", "!", "?")):
        res += "?" if is_question else "."
    return res

# Endpoint 2: Text -> ASL (Motion Playback supporting words and full sentences)
@app.route('/api/get-motion', methods=['GET', 'POST'])
@app.route('/api/motion', methods=['GET', 'POST'])
@app.route('/api/translate-text', methods=['GET', 'POST'])
def get_motion():
    query = ""
    if request.method == 'POST':
        body = request.get_json(silent=True) or {}
        query = body.get('sentence', body.get('text', body.get('word', ''))).strip()
    else:
        query = request.args.get('sentence', request.args.get('text', request.args.get('word', ''))).strip()

    if not query:
        return jsonify({"error": "Please specify 'sentence', 'text', or 'word' parameter"}), 400

    glosses, skipped = parse_text_to_asl_glosses(query)
    if not glosses:
        return jsonify({
            "error": f"No recognizable sign language gestures found for '{query}'",
            "available_words": classes[:15]
        }), 404

    combined_frames = []
    word_timings = []
    current_frame = 0

    for i, word in enumerate(glosses):
        frames = load_word_frames(word)
        if not frames:
            continue

        # Add smooth transition frames if chaining from a previous word
        if combined_frames:
            transitions = blend_motion_frames(combined_frames[-1], frames[0], steps=8)
            t_start = current_frame
            t_end = current_frame + len(transitions) - 1
            word_timings.append({
                "type": "transition",
                "word": f"{glosses[i-1]} → {word}",
                "start_frame": t_start,
                "end_frame": t_end
            })
            combined_frames.extend(transitions)
            current_frame += len(transitions)

        w_start = current_frame
        w_end = current_frame + len(frames) - 1
        word_timings.append({
            "type": "sign",
            "word": word,
            "start_frame": w_start,
            "end_frame": w_end
        })
        combined_frames.extend(frames)
        current_frame += len(frames)

    return jsonify({
        "input_text": query,
        "asl_glosses": glosses,
        "skipped_words": skipped,
        "word_timings": word_timings,
        "total_frames": len(combined_frames),
        "frames": combined_frames
    })

# Endpoint 3: ASL Glosses -> English Sentence Formulator
@app.route('/api/assemble-sentence', methods=['POST'])
def assemble_sentence():
    payload = request.get_json(silent=True) or {}
    words = payload.get("words", [])
    if isinstance(words, str):
        words = words.split()
    english = assemble_english_sentence(words)
    return jsonify({
        "asl_glosses": words,
        "english_sentence": english
    })

# Endpoint 4: Video Upload -> Full ASL Transcription & Sentence Formulation
def extract_video_landmarks_and_transcribe(video_path):
    """Processes an uploaded video file using MediaPipe Holistic and transcribes ASL signs."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return [], "", [], 0, 0.0

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_vid_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    mp_holistic = mp.solutions.holistic
    frames_buffer = []

    with mp_holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        model_complexity=1
    ) as holistic:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            results = holistic.process(image_rgb)

            pose = np.array([[res.x, res.y, res.z] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33 * 3)
            lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21 * 3)
            rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21 * 3)
            kp = np.concatenate([pose, lh, rh]).tolist()
            frames_buffer.append(kp)

    cap.release()

    if not frames_buffer:
        return [], "", [], total_vid_frames, fps

    seq_len = 60
    stride = 30
    total_extracted = len(frames_buffer)
    recognized_segments = []
    recognized_words = []

    if total_extracted < seq_len:
        arr = np.array(frames_buffer, dtype=np.float32)
        indices = np.linspace(0, total_extracted - 1, seq_len)
        resampled = np.zeros((seq_len, arr.shape[1]), dtype=np.float32)
        for col in range(arr.shape[1]):
            resampled[:, col] = np.interp(indices, np.arange(total_extracted), arr[:, col])
        windows = [(0, resampled.tolist())]
    else:
        windows = []
        for start_idx in range(0, total_extracted - seq_len + 1, stride):
            windows.append((start_idx, frames_buffer[start_idx : start_idx + seq_len]))
        if (total_extracted - seq_len) % stride != 0:
            windows.append((total_extracted - seq_len, frames_buffer[-seq_len:]))

    best_candidate = None
    best_candidate_conf = 0.0
    best_candidate_sec = (0.0, round(total_extracted / max(fps, 1.0), 2))

    for start_idx, win in windows:
        norm_seq = normalize_sequence(win)
        interp_seq = interpolate_sequence(norm_seq)
        input_data = np.expand_dims(interp_seq, axis=0)

        preds = np.zeros(len(classes))
        if model_transformer is not None:
            p_trans = model_transformer.predict(input_data, verbose=0)[0]
            preds += 0.65 * p_trans
        if model_bilstm is not None:
            p_lstm = model_bilstm.predict(input_data, verbose=0)[0]
            preds += 0.35 * p_lstm

        top_idx = int(np.argmax(preds))
        top_conf = float(preds[top_idx]) * 100.0
        top_word = label_map.get(top_idx, "Unknown")
        start_sec = round(start_idx / fps, 2)
        end_sec = round(min(total_extracted, start_idx + seq_len) / fps, 2)

        if top_conf > best_candidate_conf and top_word != "Unknown":
            best_candidate = top_word
            best_candidate_conf = top_conf
            best_candidate_sec = (start_sec, end_sec)

        if top_conf >= 25.0 and top_word != "Unknown":
            if not recognized_words or recognized_words[-1] != top_word:
                recognized_words.append(top_word)
                recognized_segments.append({
                    "word": top_word,
                    "confidence": round(top_conf, 1),
                    "start_sec": start_sec,
                    "end_sec": end_sec
                })

    # Fallback to highest confidence candidate if all windows were below threshold
    if not recognized_words and best_candidate:
        recognized_words.append(best_candidate)
        recognized_segments.append({
            "word": best_candidate,
            "confidence": round(best_candidate_conf, 1),
            "start_sec": best_candidate_sec[0],
            "end_sec": best_candidate_sec[1]
        })

    english_sentence = assemble_english_sentence(recognized_words)
    return recognized_words, english_sentence, recognized_segments, total_extracted, fps

@app.route('/api/transcribe-video', methods=['POST'])
def transcribe_video():
    if 'video' not in request.files and 'file' not in request.files:
        return jsonify({"error": "No video file uploaded (provide form field 'video' or 'file')"}), 400

    uploaded_file = request.files.get('video') or request.files.get('file')
    if not uploaded_file or uploaded_file.filename == '':
        return jsonify({"error": "Empty filename provided"}), 400

    suffix = os.path.splitext(uploaded_file.filename)[1] or '.mp4'
    temp_fd, temp_path = tempfile.mkstemp(suffix=suffix)
    os.close(temp_fd)

    try:
        uploaded_file.save(temp_path)
        words, sentence, segments, total_frames, fps = extract_video_landmarks_and_transcribe(temp_path)
        duration_sec = round(total_frames / max(fps, 1.0), 2)

        return jsonify({
            "success": True,
            "filename": uploaded_file.filename,
            "duration_sec": duration_sec,
            "fps": round(fps, 2),
            "total_frames": total_frames,
            "recognized_words": words,
            "english_sentence": sentence,
            "segments": segments
        })
    except Exception as e:
        print(f"Error transcribing video: {e}")
        return jsonify({"error": f"Failed to transcribe video: {str(e)}"}), 500
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting ASL Translator Backend on http://localhost:{port} with {len(classes)} classes...")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)