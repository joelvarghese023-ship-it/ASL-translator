"""
generate_phase1_presentation.py
Generates the official 17-slide Phase-1 ML Mini Project Presentation PowerPoint (.pptx).
Strictly adheres to the user-uploaded white academic review template (4:3 aspect ratio, centered titles, exact section names).
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

def create_phase1_deck():
    prs = Presentation()
    # 4:3 Aspect Ratio (10 x 7.5 inches) matching the official template slides
    prs.slide_width = Inches(10.0)
    prs.slide_height = Inches(7.5)

    COLOR_BLACK = RGBColor(0, 0, 0)
    COLOR_DARK = RGBColor(30, 30, 30)
    COLOR_WHITE = RGBColor(255, 255, 255)
    COLOR_NAVY = RGBColor(26, 54, 93)

    blank_layout = prs.slide_layouts[6]

    def add_slide_with_title(title_text):
        slide = prs.slides.add_slide(blank_layout)
        # Background is clean white
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = COLOR_WHITE

        # Centered Slide Title matching template
        title_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(8.8), Inches(0.9))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.alignment = PP_ALIGN.CENTER
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.name = "Arial"
        p.font.color.rgb = COLOR_BLACK

        # Content text box
        content_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(8.4), Inches(5.8))
        c_tf = content_box.text_frame
        c_tf.word_wrap = True
        c_tf.margin_top = Inches(0.1)
        c_tf.margin_bottom = Inches(0.1)
        c_tf.margin_left = Inches(0.1)
        c_tf.margin_right = Inches(0.1)

        return slide, c_tf

    def add_bullet(tf, bold_prefix, text="", level=0, pt_size=16, space_after=6):
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        p.level = level
        p.space_after = Pt(space_after)
        p.font.name = "Arial"
        
        if bold_prefix:
            r1 = p.add_run()
            r1.text = (bold_prefix + " ") if text else bold_prefix
            r1.font.bold = True
            r1.font.size = Pt(pt_size)
            r1.font.color.rgb = COLOR_BLACK
            r1.font.name = "Arial"
            
        if text:
            r2 = p.add_run()
            r2.text = text
            r2.font.bold = False
            r2.font.size = Pt(pt_size)
            r2.font.color.rgb = COLOR_DARK
            r2.font.name = "Arial"
        return p

    def format_table(table, col_widths, headers, data, font_size=10):
        for col_idx, width in enumerate(col_widths):
            table.columns[col_idx].width = width

        # Headers
        for col_idx, text in enumerate(headers):
            cell = table.cell(0, col_idx)
            cell.text = text
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            p.font.name = "Arial"
            p.font.size = Pt(font_size + 1)
            p.font.bold = True
            p.font.color.rgb = COLOR_BLACK

        # Rows
        for row_idx, row_data in enumerate(data):
            for col_idx, val in enumerate(row_data):
                cell = table.cell(row_idx + 1, col_idx)
                cell.text = str(val)
                p = cell.text_frame.paragraphs[0]
                p.alignment = PP_ALIGN.CENTER if col_idx in [0, 1] else PP_ALIGN.LEFT
                p.font.name = "Arial"
                p.font.size = Pt(font_size)
                p.font.color.rgb = COLOR_DARK

    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    s1, tf1 = add_slide_with_title("Title Slide")
    items1 = [
        ("Project Title:", "OmniSign 3D: Real-Time American Sign Language (ASL) Recognition & Translation Studio"),
        ("Student Name:", "Joel Joe Varghese"),
        ("Roll No / Batch:", "SE - AIML - IV / Batch 2022-2026"),
        ("Course:", "Machine Learning Mini Project (Phase-1 Review)"),
        ("Guide Name:", "Dr. Joanne Gomes (Faculty In-charge, Dept. of AIML)"),
        ("Institute Name:", "St. Francis Institute of Technology (Engineering College), Mumbai")
    ]
    for prefix, body in items1:
        add_bullet(tf1, f"• {prefix}", body, level=0, pt_size=16, space_after=10)

    # =========================================================================
    # SLIDE 2: Problem Statement (Revised)
    # =========================================================================
    s2, tf2 = add_slide_with_title("Problem Statement (Revised)")
    add_bullet(tf2, "• Final Problem Definition:",
               "Over 70 million deaf individuals worldwide experience acute daily communication disenfranchisement. Most existing ML tools are limited to static alphabet recognition or require computationally prohibitive 3D CNNs that cannot run in real time on standard consumer laptops.",
               level=0, pt_size=15, space_after=8)
    
    add_bullet(tf2, "• Input → Output Clearly Defined:", "", level=0, pt_size=15, space_after=3)
    add_bullet(tf2, "  - Input:", "Live 30 FPS RGB webcam video stream capturing continuous dynamic American Sign Language gestures.", level=1, pt_size=14, space_after=2)
    add_bullet(tf2, "  - Output:", "Real-time predicted sign gloss token (Top-1 & Top-5 candidate probabilities), natural English text transcription, and spoken audio synthesis.", level=1, pt_size=14, space_after=8)

    add_bullet(tf2, "• Real-World Use Cases:", "", level=0, pt_size=15, space_after=3)
    add_bullet(tf2, "  1. Healthcare & Telehealth:", "Emergency medical consultations and clinical triages without delay.", level=1, pt_size=13.5, space_after=2)
    add_bullet(tf2, "  2. Educational Classrooms:", "Automated lecture transcription and interactive sign learning visualizer.", level=1, pt_size=13.5, space_after=2)
    add_bullet(tf2, "  3. Public Service Counters:", "Barrier-free communication at banks, airports, and civic offices.", level=1, pt_size=13.5, space_after=4)

    # =========================================================================
    # SLIDE 3: Dataset Details
    # =========================================================================
    s3, tf3 = add_slide_with_title("Dataset Details")
    add_bullet(tf3, "• Dataset Source:",
               "World-Level American Sign Language (WLASL v0.3) benchmark dataset collected by Li et al. (CVPR/WACV 2020) from 119 diverse signers across public online repositories.",
               level=0, pt_size=15, space_after=6)
    
    add_bullet(tf3, "• Number of Samples & Partitions (WLASL-100 Benchmark):", "", level=0, pt_size=15, space_after=3)
    add_bullet(tf3, "  - Total Raw Video Clips:", "2,038 video samples across 100 core conversational sign classes.", level=1, pt_size=14, space_after=2)
    add_bullet(tf3, "  - Training Set (70%):", "1,426 samples used for supervised model optimization.", level=1, pt_size=14, space_after=2)
    add_bullet(tf3, "  - Validation Set (15%):", "296 samples for hyperparameter tuning and model checkpointing.", level=1, pt_size=14, space_after=2)
    add_bullet(tf3, "  - Test Set (15%):", "316 samples held out for rigorous final generalization benchmarking.", level=1, pt_size=14, space_after=6)

    add_bullet(tf3, "• Feature Description & Data Snapshot:", "", level=0, pt_size=15, space_after=3)
    add_bullet(tf3, "  - Feature Vector:", "225 numerical floats per frame (Pose 75, Left Hand 63, Right Hand 63, Lips 24).", level=1, pt_size=14, space_after=2)
    add_bullet(tf3, "  - Temporal Window:", "Sequences resampled to fixed window T = 60 frames; tensor shape (N, 60, 225).", level=1, pt_size=14, space_after=4)

    # =========================================================================
    # SLIDE 4: Data Understanding
    # =========================================================================
    s4, tf4 = add_slide_with_title("Data Understanding")
    add_bullet(tf4, "• Types of Data:", "", level=0, pt_size=15, space_after=3)
    add_bullet(tf4, "  - Continuous Numerical Features:", "Normalized 3D Cartesian coordinates (x, y, z) representing human skeletal and hand joints.", level=1, pt_size=14, space_after=3)
    add_bullet(tf4, "  - Categorical Target Labels:", "100 discrete vocabulary classes (e.g., 'hello', 'mother', 'drink', 'help', 'walk').", level=1, pt_size=14, space_after=6)

    add_bullet(tf4, "• Missing Values & Occlusion Handling:", "", level=0, pt_size=15, space_after=3)
    add_bullet(tf4, "  - Hand Occlusion & Out-of-Frame Signs:", "During rapid signing, hand keypoints drop to (0,0,0) or null when hands drop below camera frame.", level=1, pt_size=14, space_after=3)
    add_bullet(tf4, "  - Mitigation Strategy:", "Linear temporal interpolation computes smooth trajectory paths between adjacent valid frames.", level=1, pt_size=14, space_after=6)

    add_bullet(tf4, "• Data Distribution Insights:", "", level=0, pt_size=15, space_after=3)
    add_bullet(tf4, "  - Video Duration Variance:", "Sign clips range from 15 frames (quick signs like 'no') to 90+ frames (compound signs like 'thank you').", level=1, pt_size=14, space_after=3)
    add_bullet(tf4, "  - Natural Sample Imbalance:", "Sample count per gloss varies between 12 and 35 clips across the 100 classes.", level=1, pt_size=14, space_after=4)

    # =========================================================================
    # SLIDE 5: Preprocessing Plan
    # =========================================================================
    s5, tf5 = add_slide_with_title("Preprocessing Plan")
    add_bullet(tf5, "• Step 1: Handling Missing Values & Sequence Uniformity:", "", level=0, pt_size=15, space_after=3)
    add_bullet(tf5, "  - Linear Spline Resampling:", "Linearly interpolate dropped frames and resample all video sequences to a standardized length of T = 60 frames.", level=1, pt_size=14, space_after=6)

    add_bullet(tf5, "• Step 2: Categorical Target Encoding:", "", level=0, pt_size=15, space_after=3)
    add_bullet(tf5, "  - Vocabulary Mapping:", "Mapped 100 class strings to discrete integer indices (0 to 99) stored in classes.json.", level=1, pt_size=14, space_after=3)
    add_bullet(tf5, "  - One-Hot Vector Transformation:", "Converted integer targets to shape (100,) for categorical cross-entropy loss computation.", level=1, pt_size=14, space_after=6)

    add_bullet(tf5, "• Step 3: Geometric Invariant Normalization:", "", level=0, pt_size=15, space_after=3)
    add_bullet(tf5, "  - 1. Origin Translation:", "x' = x - x_nose, y' = y - y_nose, z' = z - z_nose (anchored to nose landmark 0).", level=1, pt_size=14, space_after=3)
    add_bullet(tf5, "  - 2. Euclidean Scale Invariance:", "p'' = x' / (||p_R_shoulder - p_L_shoulder|| + ε) (invariant to user distance and body height).", level=1, pt_size=14, space_after=4)

    # =========================================================================
    # SLIDE 6: System Block Diagram
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    s6.background.fill.solid()
    s6.background.fill.fore_color.rgb = COLOR_WHITE
    tbox6 = s6.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(8.8), Inches(0.9))
    p6 = tbox6.text_frame.paragraphs[0]
    p6.text = "System Block Diagram"
    p6.alignment = PP_ALIGN.CENTER
    p6.font.size = Pt(28)
    p6.font.bold = True
    p6.font.name = "Arial"

    # Embed Figure 1
    fig1_path = "paper_assets/fig1_system_workflow.png"
    if os.path.exists(fig1_path):
        s6.shapes.add_picture(fig1_path, Inches(0.6), Inches(1.3), Inches(8.8), Inches(4.3))

    b_box6 = s6.shapes.add_textbox(Inches(0.6), Inches(5.7), Inches(8.8), Inches(1.5))
    tf6_sub = b_box6.text_frame
    tf6_sub.word_wrap = True
    add_bullet(tf6_sub, "• Input Stage:", "Live 30 FPS RGB webcam video stream.", level=0, pt_size=13, space_after=2)
    add_bullet(tf6_sub, "• Processing Stage:", "MediaPipe Holistic landmark extraction → Origin centering → Shoulder scaling → T=60 temporal resampling.", level=0, pt_size=13, space_after=2)
    add_bullet(tf6_sub, "• Model & Output Stage:", "BiLSTM / Neural Ensemble classification → Top-5 predictions → Live transcription tape & Web Speech TTS.", level=0, pt_size=13, space_after=2)

    # =========================================================================
    # SLIDE 7: UML Diagrams
    # =========================================================================
    s7, tf7 = add_slide_with_title("UML Diagrams")
    add_bullet(tf7, "• Use Case Diagram (System Interactions):", "", level=0, pt_size=15, space_after=3)
    add_bullet(tf7, "  - Primary Actors:", "Deaf Signer, Hearing User, Healthcare/Educator Facilitator.", level=1, pt_size=14, space_after=2)
    add_bullet(tf7, "  - Core Use Cases:", "1. Stream Live Webcam Video | 2. Recognize ASL Gesture | 3. Display Top-5 Predictions | 4. Play Spoken Audio (TTS) | 5. Upload Video File for Transcription | 6. Type English Sentence for 3D Sign Synthesis | 7. Browse 2,000 Sign Vocabulary.", level=1, pt_size=13.5, space_after=6)

    add_bullet(tf7, "• Activity Diagram (Execution Flow):", "", level=0, pt_size=15, space_after=3)
    add_bullet(tf7, "  - Step 1 (Initialization):", "User opens web studio; browser requests camera permissions and initializes MediaPipe Holistic worker.", level=1, pt_size=13.5, space_after=2)
    add_bullet(tf7, "  - Step 2 (Perception):", "Extract 225 landmarks per frame at 30 FPS; append into 60-frame rolling sliding buffer.", level=1, pt_size=13.5, space_after=2)
    add_bullet(tf7, "  - Step 3 (Inference & Gate):", "POST normalized tensor to /api/predict; verify confidence > 0.60 threshold.", level=1, pt_size=13.5, space_after=2)
    add_bullet(tf7, "  - Step 4 (Presentation):", "Append recognized sign token to live transcription tape; synthesize spoken English audio via Web Speech API.", level=1, pt_size=13.5, space_after=4)

    # =========================================================================
    # SLIDE 8: Algorithm Selection
    # =========================================================================
    s8, tf8 = add_slide_with_title("Algorithm Selection")
    add_bullet(tf8, "• Algorithms Shortlisted for Comparison:", "", level=0, pt_size=15, space_after=3)
    add_bullet(tf8, "  1. 1D Convolutional Neural Network (1D-CNN):", "Fast temporal convolutions, but lacks gating mechanisms to model long-range gesture context.", level=1, pt_size=14, space_after=2)
    add_bullet(tf8, "  2. Unidirectional Gated Recurrent Unit (GRU):", "Fewer parameters than LSTM, but misses backwards trajectory context.", level=1, pt_size=14, space_after=2)
    add_bullet(tf8, "  3. Bidirectional LSTM (BiLSTM):", "Selected Baseline! Captures past and future trajectory dependencies simultaneously across 60 frames.", level=1, pt_size=14, space_after=2)
    add_bullet(tf8, "  4. Spatial-Temporal Transformer:", "Multi-head self-attention captures global non-adjacent keyframe relationships.", level=1, pt_size=14, space_after=6)

    add_bullet(tf8, "• Reason for Choosing BiLSTM as Phase-1 Baseline:",
               "Sign language gestures are non-causal: the identity of a handshape at frame 10 depends fundamentally on where the hand lands at frame 50. BiLSTM processes the 60-frame sequence both forward and backward, capturing smooth continuous trajectory transitions.",
               level=0, pt_size=14, space_after=6)

    add_bullet(tf8, "• Baseline Model Architecture:",
               "2 stacked BiLSTM layers (128 units/dir = 256 per layer) + Batch Normalization + Recurrent Dropout (0.4) + Dense (128, ReLU) + Softmax (100 classes).",
               level=0, pt_size=14, space_after=4)

    # =========================================================================
    # SLIDE 9: Feature Selection
    # =========================================================================
    s9, tf9 = add_slide_with_title("Feature Selection")
    add_bullet(tf9, "• Selected Features (225 Coordinates per Frame):", "", level=0, pt_size=15, space_after=3)
    add_bullet(tf9, "  - Upper Body Pose Skeleton:", "25 landmarks × 3 (x, y, z) = 75 dimensions (nose, eyes, shoulders, elbows, wrists).", level=1, pt_size=14, space_after=2)
    add_bullet(tf9, "  - Left Hand Articulation:", "21 joints × 3 (x, y, z) = 63 dimensions (wrist, thumb, index, middle, ring, pinky).", level=1, pt_size=14, space_after=2)
    add_bullet(tf9, "  - Right Hand Articulation:", "21 joints × 3 (x, y, z) = 63 dimensions.", level=1, pt_size=14, space_after=2)
    add_bullet(tf9, "  - Lip Non-Manual Contours:", "8 mouth landmarks × 3 (x, y, z) = 24 dimensions.", level=1, pt_size=14, space_after=6)

    add_bullet(tf9, "• Technical Justification:", "", level=0, pt_size=15, space_after=3)
    add_bullet(tf9, "  - 99.8% Dimensionality Reduction:", "Compresses a 1080p RGB frame (~6.2 MB) into a 225-float vector (~900 bytes), enabling real-time CPU inference.", level=1, pt_size=14, space_after=2)
    add_bullet(tf9, "  - Invariant to Appearance:", "Completely eliminates background clutter, clothing patterns, lighting changes, and skin tone bias.", level=1, pt_size=14, space_after=6)

    add_bullet(tf9, "• Domain Knowledge Applied:",
               "Lower-body landmarks (hips, knees, ankles, feet) carry zero linguistic information in ASL and were strictly removed. Non-manual lip markers were explicitly added to disambiguate minimal pairs sharing identical hand motions.",
               level=0, pt_size=14, space_after=4)

    # =========================================================================
    # SLIDE 10: Evaluation Metrics for Project
    # =========================================================================
    s10, tf10 = add_slide_with_title("Evaluation Metrics for Project")
    add_bullet(tf10, "• Primary Evaluation Metrics Selected:", "", level=0, pt_size=15, space_after=3)
    add_bullet(tf10, "  1. Top-1 Categorical Accuracy:", "Percentage of test video clips where the highest-probability prediction exactly matches ground truth.", level=1, pt_size=14, space_after=2)
    add_bullet(tf10, "  2. Top-5 Categorical Accuracy:", "Percentage of clips where the true class is among the top 5 predicted candidates.", level=1, pt_size=14, space_after=2)
    add_bullet(tf10, "  3. Macro Precision & Recall:", "Averages precision and recall independently across all 100 classes regardless of frequency.", level=1, pt_size=14, space_after=2)
    add_bullet(tf10, "  4. Macro F1-Score:", "Harmonic mean of precision and recall, balancing false positives and false negatives.", level=1, pt_size=14, space_after=2)
    add_bullet(tf10, "  5. Inference Latency (ms):", "Execution time per 60-frame prediction on standard consumer CPU.", level=1, pt_size=14, space_after=6)

    add_bullet(tf10, "• Why These Metrics Were Chosen:", "", level=0, pt_size=15, space_after=3)
    add_bullet(tf10, "  - Multi-Class Granularity:", "In a 100-class open vocabulary, Top-5 accuracy directly reflects UI usability for candidate selection.", level=1, pt_size=14, space_after=2)
    add_bullet(tf10, "  - Robustness to Imbalance:", "Macro F1-Score prevents frequent classes from masking poor performance on rarer signs.", level=1, pt_size=14, space_after=2)
    add_bullet(tf10, "  - Real-Time Usability:", "Latency must remain under 100 ms to achieve smooth conversational interaction.", level=1, pt_size=14, space_after=4)

    # =========================================================================
    # SLIDE 11: Tools & Technologies
    # =========================================================================
    s11, tf11 = add_slide_with_title("Tools & Technologies")
    tools = [
        ("Programming Language:", "Python 3.11 (optimized for scientific computing and asynchronous IO)."),
        ("Deep Learning Frameworks:", "TensorFlow 2.16 & Keras 3.0 (recurrent layers, custom attention heads, GPU/CPU acceleration)."),
        ("Computer Vision & Perception:", "MediaPipe Holistic (v0.10.14) & OpenCV 4.8 (real-time 30 FPS facial and hand tracking)."),
        ("Numerical & Data Processing:", "NumPy, Pandas, SciPy (multidimensional tensor manipulation and spline interpolation)."),
        ("Web Framework & Backend:", "Flask 3.0 & Flask-CORS (REST API endpoints for real-time inference and motion delivery)."),
        ("Frontend & 3D Visualization:", "HTML5, CSS3, JavaScript (ES6), Three.js (r128 WebGL avatar rendering), Web Speech API (TTS)."),
        ("Version Control & Environment:", "Git, GitHub, virtualenv (sign_lang_env) on Windows 11.")
    ]
    for bold_pre, desc in tools:
        add_bullet(tf11, f"• {bold_pre}", desc, level=0, pt_size=14.5, space_after=6)

    # =========================================================================
    # SLIDE 12: Initial Implementation
    # =========================================================================
    s12, tf12 = add_slide_with_title("Initial Implementation")
    add_bullet(tf12, "• Data Loaded Successfully:", "", level=0, pt_size=15, space_after=3)
    add_bullet(tf12, "  - Complete Feature Extraction:", "Processed all 2,038 raw WLASL-100 video clips into normalized numpy arrays.", level=1, pt_size=14, space_after=2)
    add_bullet(tf12, "  - Partitions Staged:", "Structured split directories for train (1,426 samples) and validation (296 samples).", level=1, pt_size=14, space_after=6)

    add_bullet(tf12, "• Preprocessing Completed:", "", level=0, pt_size=15, space_after=3)
    add_bullet(tf12, "  - Applied nose-centering origin translation and Euclidean shoulder distance scale normalization.", level=1, pt_size=14, space_after=2)
    add_bullet(tf12, "  - Standardized all temporal gesture clips to uniform T = 60 frame windows.", level=1, pt_size=14, space_after=6)

    add_bullet(tf12, "• Baseline Model Trained (Phase-1 Milestone):", "", level=0, pt_size=15, space_after=3)
    add_bullet(tf12, "  - 2-layer stacked Bidirectional LSTM trained for 40 epochs with Adam optimizer (lr = 1e-3, cosine decay).", level=1, pt_size=14, space_after=2)
    add_bullet(tf12, "  - Model weights compiled and saved to bilstm_wlasl_100.h5 (5.28 MB footprint).", level=1, pt_size=14, space_after=2)
    add_bullet(tf12, "  - Verified end-to-end inference connectivity with live webcam stream.", level=1, pt_size=14, space_after=4)

    # =========================================================================
    # SLIDE 13: Initial Results
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    s13.background.fill.solid()
    s13.background.fill.fore_color.rgb = COLOR_WHITE
    tbox13 = s13.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(8.8), Inches(0.9))
    p13 = tbox13.text_frame.paragraphs[0]
    p13.text = "Initial Results"
    p13.alignment = PP_ALIGN.CENTER
    p13.font.size = Pt(28)
    p13.font.bold = True
    p13.font.name = "Arial"

    # Embed Figure 3 (Confusion Matrix & minimal pairs)
    fig3_path = "paper_assets/fig3_confusion_matrix.png"
    if os.path.exists(fig3_path):
        s13.shapes.add_picture(fig3_path, Inches(0.5), Inches(1.3), Inches(4.5), Inches(3.0))

    # Text summary on right side
    r_box13 = s13.shapes.add_textbox(Inches(5.2), Inches(1.3), Inches(4.3), Inches(3.0))
    tf13_r = r_box13.text_frame
    tf13_r.word_wrap = True

    add_bullet(tf13_r, "• Baseline BiLSTM Metrics:", "", level=0, pt_size=14, space_after=2)
    add_bullet(tf13_r, "  - Top-1 Validation Acc:", "31.01%", level=1, pt_size=13, space_after=1)
    add_bullet(tf13_r, "  - Top-5 Validation Acc:", "62.97%", level=1, pt_size=13, space_after=1)
    add_bullet(tf13_r, "  - Macro F1-Score:", "0.301", level=1, pt_size=13, space_after=1)
    add_bullet(tf13_r, "  - CPU Latency:", "38.1 ms / prediction", level=1, pt_size=13, space_after=3)

    # Observations below
    b_box13 = s13.shapes.add_textbox(Inches(0.5), Inches(4.5), Inches(9.0), Inches(2.8))
    tf13_b = b_box13.text_frame
    tf13_b.word_wrap = True
    add_bullet(tf13_b, "• Key Initial Observations:", "", level=0, pt_size=15, space_after=2)
    add_bullet(tf13_b, "  1. Real-Time Feasibility:", "Sub-40ms latency proves landmark-based neural inference runs comfortably on low-cost consumer CPUs without GPUs.", level=1, pt_size=13.5, space_after=2)
    add_bullet(tf13_b, "  2. Generalization Gap:", "Training accuracy reached 68.4% while validation was 31.01%, revealing overfitting caused by signer diversity and small per-class sample size.", level=1, pt_size=13.5, space_after=2)
    add_bullet(tf13_b, "  3. Minimal-Pair Ambiguity:", "Pairs sharing handshapes (e.g., 'mother' vs 'father') cause cross-confusion due to subtle contact points.", level=1, pt_size=13.5, space_after=2)

    # =========================================================================
    # SLIDE 14: Challenges Faced
    # =========================================================================
    s14, tf14 = add_slide_with_title("Challenges Faced")
    ch_items = [
        ("Data Issues:", "Small sample size (~14 training clips per sign) and substantial cross-signer stylistic variance created high risk of model overfitting."),
        ("Implementation Challenges:", "Concurrent processing of 1080p camera capture, 225-point MediaPipe landmark extraction, and neural network inference caused initial CPU latency spikes."),
        ("Occlusion Difficulties:", "Rapid signing motions caused temporary hand self-occlusions, resulting in missing keypoints in intermediate frames."),
        ("Understanding Difficulties:", "Distinguishing linguistically identical minimal pairs differing only in subtle facial touch locations (chin vs forehead) required specialized normalization.")
    ]
    for ch_title, ch_desc in ch_items:
        add_bullet(tf14, f"• {ch_title}", ch_desc, level=0, pt_size=15, space_after=8)

    # =========================================================================
    # SLIDE 15: Plan for Next Phase
    # =========================================================================
    s15, tf15 = add_slide_with_title("Plan for Next Phase")
    add_bullet(tf15, "• 1. Model Improvement & Ensemble Architecture:", "", level=0, pt_size=15, space_after=3)
    add_bullet(tf15, "  - Spatial-Temporal Transformer:", "Implement a 4-head self-attention Transformer to model global frame dependencies.", level=1, pt_size=14, space_after=2)
    add_bullet(tf15, "  - Weighted Neural Ensemble:", "Combine Transformer (65%) and BiLSTM (35%) via weighted softmax fusion to surpass 34% Top-1 accuracy.", level=1, pt_size=14, space_after=6)

    add_bullet(tf15, "• 2. UI & 3D Kinematic Deployment Plan:", "", level=0, pt_size=15, space_after=3)
    add_bullet(tf15, "  - Bidirectional 3D Studio:", "Develop interactive Three.js cartoon avatar ('Leo') with 21 articulated finger joints per hand.", level=1, pt_size=14, space_after=2)
    add_bullet(tf15, "  - 8-Frame Hermite Transition Blending:", "Implement cubic ease-in-out spline interpolation for fluid, jerk-free multi-sign animation.", level=1, pt_size=14, space_after=2)
    add_bullet(tf15, "  - Full WLASL-2000 Expansion:", "Convert all 2,000 WLASL signs into lightweight 3D kinematic trajectory files.", level=1, pt_size=14, space_after=6)

    add_bullet(tf15, "• 3. Research Paper Writing:",
               "Initiate authorship of the formal ML research paper following SFIT AIML guidelines with literature review and IEEE references.",
               level=0, pt_size=14, space_after=4)

    # =========================================================================
    # SLIDE 16: Deliverables
    # =========================================================================
    s16, tf16 = add_slide_with_title("Deliverables")
    delivs = [
        ("Deliverable 1: Dataset Files & Feature Callset:", "WLASL-100 preprocessed feature tensors (N, 60, 225) and classes.json dictionary mapping 100 conversational sign glosses."),
        ("Deliverable 2: Jupyter Notebook & Training Scripts:", "Modular training scripts (train_model.py, extract_features_parallel.py) containing data loading, 225-point preprocessing, and baseline BiLSTM model training."),
        ("Deliverable 3: GitHub Repository:", "Public version-controlled repository maintained at https://github.com/joelvarghese023-ship-it/ASL-translator.git with active branches (main, baseline-100-words)."),
        ("Deliverable 4: Block Diagram Images:", "High-resolution system architecture and 225-point holistic feature engineering diagrams (fig1_system_workflow.png, fig4_landmark_feature_map.png).")
    ]
    for d_title, d_desc in delivs:
        add_bullet(tf16, f"• {d_title}", d_desc, level=0, pt_size=15, space_after=8)

    # =========================================================================
    # SLIDE 17: References
    # =========================================================================
    s17, tf17 = add_slide_with_title("References")
    add_bullet(tf17, "• Dataset Sources:", "", level=0, pt_size=15, space_after=2)
    add_bullet(tf17, "  [1]", "D. Li, C. Rodriguez, X. Yu, and H. Li, 'Word-level Deep Sign Language Recognition from Video: A New Large-scale Dataset and Methods Benchmark,' in IEEE/CVF WACV, 2020, pp. 1459–1469.", level=1, pt_size=12, space_after=3)

    add_bullet(tf17, "• Research Papers:", "", level=0, pt_size=15, space_after=2)
    add_bullet(tf17, "  [2]", "A. Graves, A. Mohamed, and G. Hinton, 'Speech Recognition with Deep Recurrent Neural Networks,' in IEEE ICASSP, 2013, pp. 6645–6649.", level=1, pt_size=12, space_after=2)
    add_bullet(tf17, "  [3]", "A. Vaswani et al., 'Attention Is All You Need,' in Advances in Neural Information Processing Systems (NeurIPS), 2017, pp. 5998–6008.", level=1, pt_size=12, space_after=2)
    add_bullet(tf17, "  [4]", "C. Lugaresi et al., 'MediaPipe: A Framework for Building Perception Pipelines,' in IEEE/CVF CVPRW, 2019.", level=1, pt_size=12, space_after=3)

    add_bullet(tf17, "• Other Resources & Frameworks:", "", level=0, pt_size=15, space_after=2)
    add_bullet(tf17, "  [5]", "TensorFlow 2.16 & Keras Documentation (https://tensorflow.org).", level=1, pt_size=12, space_after=1)
    add_bullet(tf17, "  [6]", "Google MediaPipe Holistic API Reference (https://mediapipe.dev).", level=1, pt_size=12, space_after=1)
    add_bullet(tf17, "  [7]", "Three.js WebGL 3D Documentation (https://threejs.org).", level=1, pt_size=12, space_after=2)

    output_path = "OmniSign_3D_Phase1_Official_Template.pptx"
    prs.save(output_path)
    print(f"Phase-1 Presentation successfully created: {output_path}")

if __name__ == "__main__":
    create_phase1_deck()
