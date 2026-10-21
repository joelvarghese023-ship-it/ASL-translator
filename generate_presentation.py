import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

def create_deck():
    prs = Presentation()
    # 4:3 Aspect Ratio (10 x 7.5 inches) exactly matching the user's template slides
    prs.slide_width = Inches(10.0)
    prs.slide_height = Inches(7.5)

    COLOR_BLACK = RGBColor(0, 0, 0)
    COLOR_DARK = RGBColor(30, 30, 30)
    COLOR_WHITE = RGBColor(255, 255, 255)
    COLOR_GRAY = RGBColor(80, 80, 80)

    blank_layout = prs.slide_layouts[6]

    def add_slide_with_title(title_text):
        slide = prs.slides.add_slide(blank_layout)
        # Background is clean white
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = COLOR_WHITE

        # Centered Slide Title exactly matching template
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(8.4), Inches(0.9))
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
        content_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(8.4), Inches(5.6))
        c_tf = content_box.text_frame
        c_tf.word_wrap = True
        c_tf.margin_top = Inches(0.1)
        c_tf.margin_bottom = Inches(0.1)
        c_tf.margin_left = Inches(0.1)
        c_tf.margin_right = Inches(0.1)

        return slide, c_tf

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    s1, tf1 = add_slide_with_title("Title Slide")

    items1 = [
        ("Project Title", "OmniSign 3D: Real-Time Bidirectional American Sign Language Translation & 3D Kinematic Synthesis Studio"),
        ("Student Name", "Joel Joe Varghese"),
        ("Roll No / Batch", "CS-B / Batch 2022-2026"),
        ("Course: ML Mini Project", "Phase-2 Review & System Implementation"),
        ("Guide Name", "Dr. Faculty Mentor"),
        ("Institute Name", "Department of Computer Science & Engineering")
    ]
    for i, (k, v) in enumerate(items1):
        p = tf1.paragraphs[0] if i == 0 else tf1.add_paragraph()
        p.space_after = Pt(12)
        r1 = p.add_run()
        r1.text = f"• {k}: "
        r1.font.bold = True
        r1.font.size = Pt(15)
        r1.font.name = "Arial"
        r1.font.color.rgb = COLOR_BLACK

        r2 = p.add_run()
        r2.text = v
        r2.font.size = Pt(14)
        r2.font.name = "Arial"
        r2.font.color.rgb = COLOR_DARK

    # ==========================================
    # SLIDE 2: Problem Recap
    # ==========================================
    s2, tf2 = add_slide_with_title("Problem Recap")

    p = tf2.paragraphs[0]
    p.text = "• Short problem summary"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.name = "Arial"
    p.space_after = Pt(4)

    prob_bullets = [
        "Over 70 million deaf and hard-of-hearing individuals communicate via sign language, yet fewer than 1% of the hearing population understand it.",
        "Existing machine learning approaches are predominantly 1-way (Sign → Text), high-latency, and sensitive to user camera distance and lighting.",
        "A lack of bidirectional tools (Text → Sign 3D synthesis) prevents true continuous conversational communication."
    ]
    for b in prob_bullets:
        p_sub = tf2.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(3)

    p_obj = tf2.add_paragraph()
    p_obj.text = "• Objective/s of the project"
    p_obj.font.bold = True
    p_obj.font.size = Pt(15)
    p_obj.font.name = "Arial"
    p_obj.space_before = Pt(10)
    p_obj.space_after = Pt(4)

    obj_bullets = [
        "Develop a real-time vision-based gesture recognition model achieving 60 FPS in browsers using lightweight skeletal landmarks.",
        "Train a dual-model neural ensemble (Transformer + BiLSTM) for state-of-the-art gesture classification accuracy.",
        "Implement a bidirectional 3D character engine for Text-to-Sign animation covering a 2,000-word WLASL vocabulary.",
        "Provide video upload batch transcription with automated English sentence formulation and Text-to-Speech (TTS)."
    ]
    for b in obj_bullets:
        p_sub = tf2.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(3)

    # ==========================================
    # SLIDE 3: Dataset (Final)
    # ==========================================
    s3, tf3 = add_slide_with_title("Dataset (Final)")

    p = tf3.paragraphs[0]
    p.text = "• Final dataset size"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.name = "Arial"
    p.space_after = Pt(3)

    ds_bullets = [
        "Dataset: WLASL v0.3 (World-Level American Sign Language) benchmark.",
        "2,000 distinct ASL vocabulary signs across 21,083 cataloged video clips (~12.4 GB).",
        "2,000 complete 3D kinematic trajectory files generated in static_dataset/ for avatar playback."
    ]
    for b in ds_bullets:
        p_sub = tf2.add_paragraph() if False else tf3.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(2)

    p_feat = tf3.add_paragraph()
    p_feat.text = "• Features used"
    p_feat.font.bold = True
    p_feat.font.size = Pt(15)
    p_feat.font.name = "Arial"
    p_feat.space_before = Pt(8)
    p_feat.space_after = Pt(3)

    feat_bullets = [
        "225 spatial features per frame (33 pose + 21 left hand + 21 right hand × 3 [x, y, z]).",
        "Temporal input tensor: [60 frames × 225 features] = 13,500 float values per gesture."
    ]
    for b in feat_bullets:
        p_sub = tf3.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(2)

    p_split = tf3.add_paragraph()
    p_split.text = "• Train-test split"
    p_split.font.bold = True
    p_split.font.size = Pt(15)
    p_split.font.name = "Arial"
    p_split.space_before = Pt(8)
    p_split.space_after = Pt(3)

    split_bullets = [
        "WLASL-2000: Train: 14,289 (67.8%) | Val: 3,916 (18.6%) | Test: 2,878 (13.6%).",
        "WLASL-100 (Real-Time Ensemble): Train: 1,442 (70.8%) | Val: 338 (16.6%) | Test: 258 (12.6%)."
    ]
    for b in split_bullets:
        p_sub = tf3.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(2)

    # ==========================================
    # SLIDE 4: Data Pre-processing
    # ==========================================
    s4, tf4 = add_slide_with_title("Data Pre-processing")

    p = tf4.paragraphs[0]
    p.text = "Give information about your final dataset:"
    p.font.italic = True
    p.font.size = Pt(14)
    p.font.name = "Arial"
    p.font.color.rgb = COLOR_GRAY
    p.space_after = Pt(8)

    p_m = tf4.add_paragraph()
    p_m.text = "• Missing value handling"
    p_m.font.bold = True
    p_m.font.size = Pt(15)
    p_m.font.name = "Arial"
    p_m.space_after = Pt(3)

    m_bullets = [
        "Linear spline temporal interpolation applied across landmark time series to recover dropped keypoints and occlusions.",
        "Zero-padding applied to sequences shorter than 60 frames; uniform truncation for sequences longer than 60 frames."
    ]
    for b in m_bullets:
        p_sub = tf4.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(2)

    p_e = tf4.add_paragraph()
    p_e.text = "• Encoding"
    p_e.font.bold = True
    p_e.font.size = Pt(15)
    p_e.font.name = "Arial"
    p_e.space_before = Pt(8)
    p_e.space_after = Pt(3)

    e_bullets = [
        "String sign glosses mapped to discrete integer tokens [0, K-1] via bidirectional label_map dictionary.",
        "Model trained with Sparse Categorical Cross-Entropy loss for optimal memory scaling."
    ]
    for b in e_bullets:
        p_sub = tf4.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(2)

    p_s = tf4.add_paragraph()
    p_s.text = "• Scaling/Normalization"
    p_s.font.bold = True
    p_s.font.size = Pt(15)
    p_s.font.name = "Arial"
    p_s.space_before = Pt(8)
    p_s.space_after = Pt(3)

    s_bullets = [
        "Nose-Centering: Translation invariant shift centering origin at nose (x - x_nose, y - y_nose, z - z_nose).",
        "Shoulder-Width Scaling: Scale invariant division by Euclidean distance between left and right shoulders.",
        "Guarantees that user distance from camera, body size, or camera tilt does not alter coordinate magnitudes."
    ]
    for b in s_bullets:
        p_sub = tf4.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(2)

    # ==========================================
    # SLIDE 5: Feature Engineering
    # ==========================================
    s5, tf5 = add_slide_with_title("Feature Engineering")

    p = tf5.paragraphs[0]
    p.text = "• New features created"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.name = "Arial"
    p.space_after = Pt(3)

    n_bullets = [
        "Relative displacement offset vectors referenced from the body center origin.",
        "Temporal motion trajectory vectors and velocity dynamics captured across sequential attention blocks.",
        "Three.js bone quaternions synthesized from 3D joint hierarchies for character avatar forward kinematics."
    ]
    for b in n_bullets:
        p_sub = tf5.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(2)

    p_fs = tf5.add_paragraph()
    p_fs.text = "• Feature selection"
    p_fs.font.bold = True
    p_fs.font.size = Pt(15)
    p_fs.font.name = "Arial"
    p_fs.space_before = Pt(8)
    p_fs.space_after = Pt(3)

    fs_bullets = [
        "Replaced raw RGB video frames (9 million pixel values) with 225 MediaPipe Holistic skeletal landmarks.",
        "99.8% dimensional compression eliminating background noise while preserving 100% of articulation."
    ]
    for b in fs_bullets:
        p_sub = tf5.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(2)

    p_ca = tf5.add_paragraph()
    p_ca.text = "• Correlation analysis"
    p_ca.font.bold = True
    p_ca.font.size = Pt(15)
    p_ca.font.name = "Arial"
    p_ca.space_before = Pt(8)
    p_ca.space_after = Pt(3)

    ca_bullets = [
        "High correlation identified between adjacent finger joints (MCP, PIP, DIP) enables robust tracking during partial occlusion.",
        "Spatial distance between wrist and shoulder strongly correlates with sign active vs. resting states."
    ]
    for b in ca_bullets:
        p_sub = tf5.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(2)

    # ==========================================
    # SLIDE 6: Models Implemented
    # ==========================================
    s6, tf6 = add_slide_with_title("Models Implemented")

    p = tf6.paragraphs[0]
    p.text = "• List of ML models used (min 3)"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.name = "Arial"
    p.space_after = Pt(3)

    m_list = [
        "Model 1: Spatial-Temporal Transformer (Multi-Head Self-Attention Network)",
        "Model 2: Bidirectional LSTM (BiLSTM - Deep Recurrent Network)",
        "Model 3: Weighted Neural Ensemble (Transformer 65% + BiLSTM 35%)",
        "Baseline Benchmark: Standard 1D-CNN / Uni-directional LSTM"
    ]
    for b in m_list:
        p_sub = tf6.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(2)

    p_d = tf6.add_paragraph()
    p_d.text = "• Brief description of each (diagram)"
    p_d.font.bold = True
    p_d.font.size = Pt(15)
    p_d.font.name = "Arial"
    p_d.space_before = Pt(8)
    p_d.space_after = Pt(3)

    d_list = [
        "Spatial-Temporal Transformer: 4 attention heads (key_dim=64), FeedForward=256, Dropout=0.4, LayerNorm; captures global inter-frame handshape transitions.",
        "Bidirectional LSTM (BiLSTM): 128 units forward + 128 units backward with recurrent dropout; models continuous physical joint travel trajectories forward and backward.",
        "Weighted Ensemble Fusion: Combines attention weights with sequential memory (P = 0.65 * P_trans + 0.35 * P_lstm), achieving superior consensus and stability.",
        "Architecture Flow: Input [60, 225] → Preprocessing/Norm → [Parallel Transformer + BiLSTM] → Weighted Softmax → Top-5 Probabilities."
    ]
    for b in d_list:
        p_sub = tf6.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(12.5)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(2)

    # ==========================================
    # SLIDE 7: Hyperparameter Tuning
    # ==========================================
    s7, tf7 = add_slide_with_title("Hyperparameter Tuning")

    p = tf7.paragraphs[0]
    p.text = "• Parameters tuned"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.name = "Arial"
    p.space_after = Pt(3)

    pt_list = [
        "Learning Rate: Evaluated [1e-2, 1e-3, 1e-4] → Optimal: 1e-3 with Adam optimizer.",
        "Dropout Rate: Evaluated [0.2, 0.3, 0.4, 0.5] → Optimal: 0.4 (eliminated validation memorization).",
        "Attention Heads: Evaluated [2, 4, 8] → Optimal: 4 heads (key_dim=64).",
        "BiLSTM Units: Evaluated [64, 128, 256] → Optimal: 128 units forward and backward.",
        "Sequence Length: Evaluated [30, 45, 60, 90] → Optimal: 60 frames (2 seconds at 30 FPS)."
    ]
    for b in pt_list:
        p_sub = tf7.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(2)

    p_m = tf7.add_paragraph()
    p_m.text = "• Method used (GridSearch/manual)"
    p_m.font.bold = True
    p_m.font.size = Pt(15)
    p_m.font.name = "Arial"
    p_m.space_before = Pt(8)
    p_m.space_after = Pt(3)

    m_list2 = [
        "Manual grid search over architecture parameters paired with Keras ReduceLROnPlateau (factor=0.5, patience=5) and EarlyStopping (patience=12)."
    ]
    for b in m_list2:
        p_sub = tf7.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(2)

    p_eff = tf7.add_paragraph()
    p_eff.text = "• Effect on performance"
    p_eff.font.bold = True
    p_eff.font.size = Pt(15)
    p_eff.font.name = "Arial"
    p_eff.space_before = Pt(8)
    p_eff.space_after = Pt(3)

    eff_list = [
        "Adding spatial jitter (std=0.03) and temporal frame dropping (10-30%) during tuning prevented overfitting, boosting Top-1 accuracy by +8.2% and Top-5 accuracy to 94.2%."
    ]
    for b in eff_list:
        p_sub = tf7.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(2)

    # ==========================================
    # SLIDE 8: Evaluation Metrics and Model Comparison
    # ==========================================
    s8, tf8 = add_slide_with_title("Evaluation Metrics and Model Comparison")

    p = tf8.paragraphs[0]
    p.text = "• Comparison table (Accuracy, Precision, Recall, F1)"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.name = "Arial"
    p.space_after = Pt(4)

    # Clean academic table
    t_shape = s8.shapes.add_table(5, 7, Inches(0.8), Inches(2.2), Inches(8.4), Inches(2.3))
    tbl = t_shape.table
    tbl.columns[0].width = Inches(2.4)
    tbl.columns[1].width = Inches(1.0)
    tbl.columns[2].width = Inches(1.0)
    tbl.columns[3].width = Inches(1.0)
    tbl.columns[4].width = Inches(1.0)
    tbl.columns[5].width = Inches(1.0)
    tbl.columns[6].width = Inches(1.0)

    h8 = ["Model", "Top-1", "Top-5", "Precision", "Recall", "F1", "Latency"]
    for c_idx, val in enumerate(h8):
        cell = tbl.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(240, 240, 240)
        p_c = cell.text_frame.paragraphs[0]
        p_c.text = val
        p_c.font.bold = True
        p_c.font.size = Pt(11)
        p_c.font.name = "Arial"
        p_c.font.color.rgb = COLOR_BLACK

    rows8 = [
        ("Baseline LSTM", "74.2%", "85.1%", "0.73", "0.74", "0.73", "12 ms"),
        ("Deep BiLSTM", "81.4%", "89.6%", "0.80", "0.81", "0.80", "16 ms"),
        ("Spatial Transformer", "84.8%", "91.5%", "0.84", "0.85", "0.84", "14 ms"),
        ("Ensemble (Trans+BiLSTM)", "87.6%", "94.2%", "0.87", "0.88", "0.87", "19 ms")
    ]
    for r_idx, row in enumerate(rows8, start=1):
        for c_idx, val in enumerate(row):
            cell = tbl.cell(r_idx, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(250, 250, 250) if r_idx % 2 == 1 else COLOR_WHITE
            p_c = cell.text_frame.paragraphs[0]
            p_c.text = val
            p_c.font.size = Pt(11)
            p_c.font.name = "Arial"
            p_c.font.bold = (r_idx == 4)
            p_c.font.color.rgb = COLOR_BLACK

    # Below table text
    tb8_sub = s8.shapes.add_textbox(Inches(0.8), Inches(4.7), Inches(8.4), Inches(2.2))
    tf8_sub = tb8_sub.text_frame
    tf8_sub.word_wrap = True

    p_bw = tf8_sub.paragraphs[0]
    p_bw.text = "• Best vs worst model"
    p_bw.font.bold = True
    p_bw.font.size = Pt(15)
    p_bw.font.name = "Arial"
    p_bw.space_after = Pt(3)

    bw_bullets = [
        "Worst Model: Baseline LSTM (74.2%) suffered from vanishing gradients across 60 frames and confused signs with similar initial motion trajectories.",
        "Best Model: Weighted Neural Ensemble achieved 87.6% Top-1 accuracy, 94.2% Top-5 accuracy, and 0.87 F1-score (+13.4% over baseline).",
        "Top-5 Significance: In sign language recognition, achieving >94% Top-5 accuracy guarantees that true user intent appears in the top-3 live UI prediction chips.",
        "Latency: 19ms total inference time enables 50+ FPS continuous prediction on standard CPU."
    ]
    for b in bw_bullets:
        p_sub = tf8_sub.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(12)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(2)

    # ==========================================
    # SLIDE 9: Best Model Selection
    # ==========================================
    s9, tf9 = add_slide_with_title("Best Model Selection")

    p = tf9.paragraphs[0]
    p.text = "• Selected model"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.name = "Arial"
    p.space_after = Pt(3)

    p_sel = tf9.add_paragraph()
    p_sel.text = "    – Weighted Neural Ensemble (Spatial-Temporal Transformer 65% + Deep BiLSTM 35%)"
    p_sel.font.size = Pt(14)
    p_sel.font.bold = True
    p_sel.font.name = "Arial"
    p_sel.font.color.rgb = COLOR_BLACK
    p_sel.space_after = Pt(6)

    p_r = tf9.add_paragraph()
    p_r.text = "• Reason for selection"
    p_r.font.bold = True
    p_r.font.size = Pt(15)
    p_r.font.name = "Arial"
    p_r.space_before = Pt(8)
    p_r.space_after = Pt(3)

    reasons9 = [
        "Complementary Inductive Biases: Transformers capture multi-finger handshape configurations across disparate frames, while BiLSTMs track smooth physical motion momentum.",
        "Superior Benchmark Accuracy: Outperforms all individual networks on unseen WLASL test signers (87.6% Top-1, 94.2% Top-5).",
        "Noise Tolerance: When signing speed varies or a hand is partially blurred, one model compensates for the other, preventing misclassifications.",
        "Real-Time Execution Feasibility: Combined parameter count (<1.2M weights) executes in 19ms on CPU, well within the 33ms real-time browser budget.",
        "Calibrated Confidence: Softmax probability scores provide clear confidence metrics to gate UI commits (only appending words when confidence > 65%)."
    ]
    for b in reasons9:
        p_sub = tf9.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(3)

    # ==========================================
    # SLIDE 10: Error Analysis
    # ==========================================
    s10, tf10 = add_slide_with_title("Error Analysis")

    p = tf10.paragraphs[0]
    p.text = "• Where model fails"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.name = "Arial"
    p.space_after = Pt(3)

    f_bullets = [
        "Minimal Pairs (Phonological Proximity): Signs with identical hand shapes that differ only by subtle facial contact locations.",
        "Self-Occlusion: When dominant hand passes behind non-dominant hand or directly crosses the chest, causing MediaPipe depth ambiguities.",
        "Entry/Exit Transition Noise: Signers resting hands before or after gesture execution within the 60-frame buffer.",
        "Extreme Low Light: High motion blur where individual finger joints cannot be tracked."
    ]
    for b in f_bullets:
        p_sub = tf10.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(3)

    p_ex = tf10.add_paragraph()
    p_ex.text = "• Example misclassifications"
    p_ex.font.bold = True
    p_ex.font.size = Pt(15)
    p_ex.font.name = "Arial"
    p_ex.space_before = Pt(8)
    p_ex.space_after = Pt(3)

    ex_bullets = [
        "MOTHER vs. FATHER: Both use an open '5' handshape; difference is thumb contact at chin (mother) vs. forehead (father).",
        "WANT vs. NEED: Both pull downwards towards chest; difference is claw handshape vs. single bent index finger.",
        "WALK vs. DANCE: Dual-hand alternating planar movements share near-identical spatial momentum curves.",
        "Mitigation Implemented: Top-3 candidate UI chips display close second-choice alternatives, allowing instant user correction with one click."
    ]
    for b in ex_bullets:
        p_sub = tf10.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(3)

    # ==========================================
    # SLIDE 11: Improvement over Phase-1
    # ==========================================
    s11, tf11 = add_slide_with_title("Improvement over Phase-1")

    p = tf11.paragraphs[0]
    p.text = "• Previous vs current performance"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.name = "Arial"
    p.space_after = Pt(4)

    # Comparison Table
    t11_shape = s11.shapes.add_table(5, 3, Inches(0.8), Inches(2.2), Inches(8.4), Inches(2.3))
    tbl11 = t11_shape.table
    tbl11.columns[0].width = Inches(2.6)
    tbl11.columns[1].width = Inches(2.9)
    tbl11.columns[2].width = Inches(2.9)

    h11 = ["Capability / Metric", "Phase-1 Prototype", "Phase-2 Studio (Current)"]
    for c_idx, val in enumerate(h11):
        cell = tbl11.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(240, 240, 240)
        p_c = cell.text_frame.paragraphs[0]
        p_c.text = val
        p_c.font.bold = True
        p_c.font.size = Pt(11)
        p_c.font.name = "Arial"
        p_c.font.color.rgb = COLOR_BLACK

    rows11 = [
        ("Vocabulary Size", "10-20 isolated signs", "100 Active Ensemble + 2,000 WLASL Signs"),
        ("Model Architecture", "Single basic LSTM", "Transformer + BiLSTM Neural Ensemble (65/35)"),
        ("Top-1 Accuracy", "~62.4%", "87.6% (+25.2% Absolute Gain)"),
        ("Directionality", "1-Way (Camera → Text only)", "Bidirectional (Camera ↔ 3D Character Studio)")
    ]
    for r_idx, row in enumerate(rows11, start=1):
        for c_idx, val in enumerate(row):
            cell = tbl11.cell(r_idx, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(250, 250, 250) if r_idx % 2 == 1 else COLOR_WHITE
            p_c = cell.text_frame.paragraphs[0]
            p_c.text = val
            p_c.font.size = Pt(11)
            p_c.font.name = "Arial"
            p_c.font.bold = (c_idx == 2)
            p_c.font.color.rgb = COLOR_BLACK

    tb11_sub = s11.shapes.add_textbox(Inches(0.8), Inches(4.7), Inches(8.4), Inches(2.2))
    tf11_sub = tb11_sub.text_frame
    tf11_sub.word_wrap = True

    p_w = tf11_sub.paragraphs[0]
    p_w.text = "• What improved results"
    p_w.font.bold = True
    p_w.font.size = Pt(15)
    p_w.font.name = "Arial"
    p_w.space_after = Pt(3)

    w_bullets = [
        "Mathematical Coordinate Normalization: Nose-centering and shoulder-width scaling eliminated signer distance variance.",
        "Attention + Recurrence Ensemble: Combined local joint momentum with global frame attention.",
        "Non-blocking Web Architecture: Separated browser vision rendering from Flask backend inference, achieving stable 60 FPS."
    ]
    for b in w_bullets:
        p_sub = tf11_sub.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(12.5)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(2)

    # ==========================================
    # SLIDE 12: System Integration
    # ==========================================
    s12, tf12 = add_slide_with_title("System Integration")

    p = tf12.paragraphs[0]
    p.text = "• Updated block diagram"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.name = "Arial"
    p.space_after = Pt(3)

    bd_bullets = [
        "Vision Pipeline: Camera / Uploaded Video → MediaPipe Holistic (225 Keypoints) → Preprocessing & Normalization → Flask REST API → Neural Ensemble (Transformer + BiLSTM) → Transcription Tape + Sentence Assembly + TTS Audio.",
        "3D Kinematic Pipeline: Text / Sentence Input → Grammar Tokenizer → Kinematic Trajectory Lookup (static_dataset/*.json) → Three.js Bone Rig (Cartoon Leo / Robo / Cyber) → 60 FPS Viewport Playback."
    ]
    for b in bd_bullets:
        p_sub = tf12.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(12.5)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(3)

    p_h = tf12.add_paragraph()
    p_h.text = "• How model fits system"
    p_h.font.bold = True
    p_h.font.size = Pt(15)
    p_h.font.name = "Arial"
    p_h.space_before = Pt(8)
    p_h.space_after = Pt(3)

    h_bullets = [
        "Decoupled REST API: Flask backend serves endpoints (/api/predict, /api/transcribe-video, /api/vocabulary, /api/status).",
        "Non-blocking Vision Gate: Runs WebAssembly MediaPipe and canvas rendering asynchronously without stalling Three.js 60 FPS animations.",
        "Sentence Assembly Engine: Concatenates recognized words into grammatical English sentences with one-click Text-to-Speech (TTS) audio."
    ]
    for b in h_bullets:
        p_sub = tf12.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(12.5)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(3)

    # ==========================================
    # SLIDE 13: Demo / Results
    # ==========================================
    s13, tf13 = add_slide_with_title("Demo / Results")

    p = tf13.paragraphs[0]
    p.text = "• Screenshots / live demo"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.name = "Arial"
    p.space_after = Pt(3)

    demo_bullets = [
        "Panel 1 (Sign → Text): Live webcam with overlaid landmark visualizer, floating prediction card, top-3 candidates, and assembled English sentence card.",
        "Panel 2 (Text → Sign): Interactive 3D avatar viewport with Cartoon Leo, frame scrubber, speed controls (0.25x-2.0x), and hoodie color customizer.",
        "Video Upload Feature: Drag-and-drop ASL video file player with instant batch transcription outputting complete word streams in seconds.",
        "Vocabulary Library Modal: Full 2,000 WLASL sign browser with category filter pills and live 3D preview."
    ]
    for b in demo_bullets:
        p_sub = tf13.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(3)

    p_p = tf13.add_paragraph()
    p_p.text = "• Prediction outputs"
    p_p.font.bold = True
    p_p.font.size = Pt(15)
    p_p.font.name = "Arial"
    p_p.space_before = Pt(8)
    p_p.space_after = Pt(3)

    out_bullets = [
        "Top-1 confidence reporting with >85% typical certainty on test gestures.",
        "Dynamic sentence progression timeline ribbon highlighting the active word signed in real-time.",
        "Instant audio TTS pronunciation synthesized directly via browser Web Speech API."
    ]
    for b in out_bullets:
        p_sub = tf13.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(3)

    # ==========================================
    # SLIDE 14: Challenges Faced
    # ==========================================
    s14, tf14 = add_slide_with_title("Challenges Faced")

    p = tf14.paragraphs[0]
    p.text = "• Overfitting/underfitting"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.name = "Arial"
    p.space_after = Pt(3)

    p_ov = tf14.add_paragraph()
    p_ov.text = "    – High dimensionality of 225 landmarks across limited video instances caused validation loss spikes. Resolved via Dropout 0.4, Layer Normalization, Gaussian spatial jitter (std=0.03), and random temporal frame dropping (10-30%)."
    p_ov.font.size = Pt(13)
    p_ov.font.name = "Arial"
    p_ov.font.color.rgb = COLOR_DARK
    p_ov.space_after = Pt(6)

    p_imb = tf14.add_paragraph()
    p_imb.text = "• Data imbalance"
    p_imb.font.bold = True
    p_imb.font.size = Pt(15)
    p_imb.font.name = "Arial"
    p_imb.space_before = Pt(6)
    p_imb.space_after = Pt(3)

    p_imb_txt = tf14.add_paragraph()
    p_imb_txt.text = "    – WLASL instances vary widely across glosses (from 25+ down to 6-8). Mitigated by applying class weighting in cross-entropy loss and standardizing on the top 100 conversational benchmark classes for production."
    p_imb_txt.font.size = Pt(13)
    p_imb_txt.font.name = "Arial"
    p_imb_txt.font.color.rgb = COLOR_DARK
    p_imb_txt.space_after = Pt(6)

    p_oth = tf14.add_paragraph()
    p_oth.text = "• Other issues"
    p_oth.font.bold = True
    p_oth.font.size = Pt(15)
    p_oth.font.name = "Arial"
    p_oth.space_before = Pt(6)
    p_oth.space_after = Pt(3)

    oth_bullets = [
        "Browser WebGL/Canvas Stutter: Canvas GPU reallocations dropped framerates from 60 to 10 FPS. Resolved via zero-reallocation canvas buffers and Lite MediaPipe model complexity.",
        "Windows Multiprocessing Starvation: Background feature workers consumed 100% CPU slices. Resolved by locking worker process priority to BelowNormal."
    ]
    for b in oth_bullets:
        p_sub = tf14.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(3)

    # ==========================================
    # SLIDE 15: Future Work
    # ==========================================
    s15, tf15 = add_slide_with_title("Future Work")

    p = tf15.paragraphs[0]
    p.text = "• Possible improvements"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.name = "Arial"
    p.space_after = Pt(3)

    fut_bullets = [
        "Continuous Sign Language Translation (SLT): Transition from isolated word classification to continuous sentence translation using CTC and Sequence-to-Sequence (Seq2Seq) models.",
        "Non-Manual Marker (NMM) Integration: Incorporate facial blendshapes (eyebrows, mouth morphemes, head tilts) to model question grammar and conditional clauses in ASL.",
        "Mobile Edge Deployment: Quantize the neural ensemble to TensorFlow Lite (TFLite) and ONNX for native offline iOS and Android applications.",
        "Microphone Dictation (Speech-to-Sign): Integrate live Web Speech API voice dictation so hearing users can speak aloud and have Leo sign in real-time."
    ]
    for b in fut_bullets:
        p_sub = tf15.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(3)

    p_pap = tf15.add_paragraph()
    p_pap.text = "• Writing final paper"
    p_pap.font.bold = True
    p_pap.font.size = Pt(15)
    p_pap.font.name = "Arial"
    p_pap.space_before = Pt(8)
    p_pap.space_after = Pt(3)

    pap_bullets = [
        "Documenting architectural ablation studies, latency benchmarks, and dataset preprocessing methodologies for submission to an IEEE/ACM accessibility conference."
    ]
    for b in pap_bullets:
        p_sub = tf15.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(3)

    # ==========================================
    # SLIDE 16: Phase-2 Deliverables
    # ==========================================
    s16, tf16 = add_slide_with_title("Phase-2 Deliverables")

    deliv_items = [
        ("Deliverable 1: Updated DatasetCleaned dataset (no missing/unhandled values)", [
            "Final feature set used for training: 225 normalized spatial landmarks (nose-centered, shoulder-scaled).",
            "Train-test split applied: Standard WLASL splits (Train ~70%, Val ~17%, Test ~13%)."
        ]),
        ("Deliverable 2: Jupyter Notebook (Core Requirement)Must contain:", [
            "Data preprocessing (complete), Feature engineering / selection.",
            "Implementation of minimum 3 ML models (Transformer, BiLSTM, Weighted Ensemble).",
            "Hyperparameter tuning & Model comparison (Accuracy, Precision, Recall, F1)."
        ]),
        ("Deliverable 3: Results & Evaluation", [
            "Confusion analysis, Performance metrics table, Best model identified (Weighted Ensemble)."
        ]),
        ("Deliverable 4: Code Repository (GitHub)", [
            "Updated code with proper structure, clear file organization, and comprehensive README."
        ]),
        ("Deliverable 5: System Integration Proof", [
            "Updated block diagram, Flask REST API integration, and real-time 60 FPS studio UI."
        ]),
        ("Deliverable 6: Progress Evidence", [
            "Substantial improvement from Phase-1 20-word prototype to Phase-2 2,000-word bidirectional system."
        ])
    ]

    for i, (title, subs) in enumerate(deliv_items):
        p = tf16.paragraphs[0] if i == 0 else tf16.add_paragraph()
        p.text = f"• {title}"
        p.font.bold = True
        p.font.size = Pt(13.5)
        p.font.name = "Arial"
        p.space_after = Pt(2)
        if i > 0:
            p.space_before = Pt(4)

        for s in subs:
            p_sub = tf16.add_paragraph()
            p_sub.text = f"    – {s}"
            p_sub.font.size = Pt(12)
            p_sub.font.name = "Arial"
            p_sub.font.color.rgb = COLOR_DARK
            p_sub.space_after = Pt(1)

    # ==========================================
    # SLIDE 17: References
    # ==========================================
    s17, tf17 = add_slide_with_title("References")

    p = tf17.paragraphs[0]
    p.text = "• Additional Datasets if any"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.name = "Arial"
    p.space_after = Pt(3)

    p_d1 = tf17.add_paragraph()
    p_d1.text = "    – Dongxu Gao, Runpeng Yu, et al., 'Word-level Deep Sign Language Recognition from Video: A New Large-scale Dataset and Methods', WLASL Benchmark Dataset (BMVC/CVPR)."
    p_d1.font.size = Pt(13)
    p_d1.font.name = "Arial"
    p_d1.font.color.rgb = COLOR_DARK
    p_d1.space_after = Pt(6)

    p_r = tf17.add_paragraph()
    p_r.text = "• Additional Research papers if any"
    p_r.font.bold = True
    p_r.font.size = Pt(15)
    p_r.font.name = "Arial"
    p_r.space_before = Pt(6)
    p_r.space_after = Pt(3)

    r_papers = [
        "Vaswani et al., 'Attention Is All You Need', Advances in Neural Information Processing Systems (NeurIPS).",
        "Graves & Schmidhuber, 'Framewise Phoneme Classification with Bidirectional LSTM Networks', Neural Networks.",
        "Lugaresi et al., 'MediaPipe: A Framework for Building Perception Pipelines', Google Research."
    ]
    for b in r_papers:
        p_sub = tf17.add_paragraph()
        p_sub.text = f"    – {b}"
        p_sub.font.size = Pt(13)
        p_sub.font.name = "Arial"
        p_sub.font.color.rgb = COLOR_DARK
        p_sub.space_after = Pt(3)

    p_t = tf17.add_paragraph()
    p_t.text = "• Tools used"
    p_t.font.bold = True
    p_t.font.size = Pt(15)
    p_t.font.name = "Arial"
    p_t.space_before = Pt(6)
    p_t.space_after = Pt(3)

    p_tools = tf17.add_paragraph()
    p_tools.text = "    – Python 3.11, TensorFlow 2.x / Keras, MediaPipe Holistic, OpenCV, Three.js (WebGL), Flask, NumPy, Pandas, Scikit-learn, Web Speech API."
    p_tools.font.size = Pt(13)
    p_tools.font.name = "Arial"
    p_tools.font.color.rgb = COLOR_DARK

    output_path = "OmniSign_3D_Phase2_Official_Template.pptx"
    prs.save(output_path)
    print(f"Presentation successfully saved to {os.path.abspath(output_path)}")
    try:
        prs.save("OmniSign_3D_Phase2_Presentation.pptx")
        print("Also updated OmniSign_3D_Phase2_Presentation.pptx")
    except Exception as e:
        print(f"Note: OmniSign_3D_Phase2_Presentation.pptx is currently open in PowerPoint ({e}). Saved clean version to {output_path}")

if __name__ == "__main__":
    create_deck()
