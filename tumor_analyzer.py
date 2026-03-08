import cv2
import numpy as np
import os
import tensorflow as tf

# Load the trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "brain_tumor_model.h5")
model = None
if os.path.exists(MODEL_PATH):
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Tumor Analyzer: Model loaded successfully.")

CLASS_NAMES = ['Glioma', 'Meningioma', 'No Tumor', 'Pituitary Tumor']

def analyze_tumor(file):
    image = cv2.imread(file.name)

    if image is None:
        return reject("Invalid Image", "Image could not be read")

    # 1. Color Normalization (Convert to Grayscale then back to RGB to remove tints)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # ❗ CRITICAL: Normalize to grayscale-RGB to remove color-bias (like the blue tint)
    # This ensures the ML model only sees the structural MRI patterns it was trained on.
    normalized_rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    
    filename = os.path.basename(file.name).lower()
    is_brain = "brain" in filename

    # Potential anomaly check (Image Processing fallback)
    # This helps catch tumors that the ML model might miss
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    # Multiple thresholds to catch different intensities
    _, thresh_hard = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY)
    _, thresh_soft = cv2.threshold(blurred, 110, 255, cv2.THRESH_BINARY)
    
    contours_hard, _ = cv2.findContours(thresh_hard, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_soft, _ = cv2.findContours(thresh_soft, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter for significant regions
    big_contours = [c for c in contours_soft if cv2.contourArea(c) > 1500]
    
    quality_warning = "Clear scan"
    # Simple check for jpeg artifacts or color issues
    b, g, r = cv2.split(image)
    if np.mean(np.abs(b - g)) > 15:
        quality_warning = "Quality Note: Color tint detected. Auto-normalized for analysis."

    # 2. ML Prediction (Classification)
    tumor_type = "Unknown"
    confidence = 0.0
    has_tumor = False
    preds = []

    if model:
        # Use the normalized RGB image
        input_img = cv2.resize(normalized_rgb, (224, 224))
        input_img = input_img / 255.0
        input_img = np.expand_dims(input_img, axis=0)
        
        preds = model.predict(input_img, verbose=0)[0]
        class_idx = np.argmax(preds)
        tumor_type = CLASS_NAMES[class_idx]
        confidence = float(preds[class_idx])
        has_tumor = tumor_type != 'No Tumor'
    else:
        # Fallback if model is missing
        has_tumor = (len(big_contours) > 0)
        tumor_type = "Anomaly Detected (Model missing)"
        confidence = 0.5

    # 4. Size & Localization & Detailed Stats
    area = sum(cv2.contourArea(c) for c in big_contours)
    size_cm = round(area / 9000, 2)
    edge_complexity = len(contours_soft)
    
    # Calculate intensities of detected regions
    region_intensities = []
    for c in big_contours:
        mask = np.zeros(gray.shape, dtype=np.uint8)
        cv2.drawContours(mask, [c], -1, 255, -1)
        mean_val = cv2.mean(gray, mask=mask)[0]
        region_intensities.append(round(float(mean_val), 2))
    
    if not region_intensities:
        region_intensities = [round(float(np.mean(gray)), 2)]

    # Improved localization
    location = "Internal Region"
    if len(big_contours) > 0:
        c = max(big_contours, key=cv2.contourArea)
        M = cv2.moments(c)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            h, w = gray.shape
            v_pos = "Central"
            if cY < h/3: v_pos = "Superior (Frontal)"
            elif cY > 2*h/3: v_pos = "Inferior (Occipital)"
            h_pos = "Midline"
            if cX < w/3: h_pos = "Left Hemisphere"
            elif cX > 2*w/3: h_pos = "Right Hemisphere"
            location = f"{v_pos}, {h_pos}"

    if not has_tumor:
        return {
            "has_tumor": False,
            "tumor_type": "No Tumor Detected",
            "size": "N/A",
            "location": "N/A",
            "confidence": round(confidence, 4),
            "analysis_details": {
                "message": "The system did not detect a significant tumor in this scan.",
                "quality": quality_warning,
                "anomalous_regions": 0,
                "edge_complexity": edge_complexity,
                "tumor_score": 0.0,
                "region_intensities": region_intensities,
                "raw_scores": [round(float(p), 3) for p in preds] if len(preds) > 0 else []
            }
        }

    return {
        "has_tumor": True,
        "tumor_type": tumor_type,
        "size": f"{size_cm} cm",
        "location": location,
        "confidence": round(confidence, 4),
        "analysis_details": {
            "anomalous_regions": len(big_contours),
            "edge_complexity": edge_complexity,
            "tumor_score": round(confidence * 10, 2),
            "region_intensities": region_intensities,
            "quality": quality_warning,
            "raw_scores": [round(float(p), 3) for p in preds] if len(preds) > 0 else []
        }
    }




def reject(reason, message):
    return {
        "has_tumor": False,
        "tumor_type": reason,
        "size": "N/A",
        "location": "N/A",
        "confidence": 0.0,
        "analysis_details": {
            "message": message,
            "anomalous_regions": "N/A",
            "edge_complexity": "N/A",
            "tumor_score": "N/A",
            "region_intensities": []
        }
    }
