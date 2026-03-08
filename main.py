from fastapi import FastAPI, File, UploadFile, HTTPException # pyright: ignore[reportMissingImports]
import uvicorn, os # pyright: ignore[reportMissingImports]
from PIL import Image, ImageOps  # for image analysis
import numpy as np
import random
from datetime import datetime
from typing import Tuple, Dict, Any
# import cv2 optionally (binary wheels sometimes fail in some environments)
try:
    import cv2  # for more advanced image processing
except Exception:
    cv2 = None
from pathlib import Path

app = FastAPI(title="Brain Tumor Detection API")

UPLOAD_FOLDER = "uploads"
VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/upload")
async def upload_scan(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    result = analyze_scan(file_path)
    return {"file_path": file_path, "result": result}

def preprocess_image(img: Image.Image) -> Tuple[np.ndarray, Dict[str, Any]]:
    """Preprocess image and extract basic features.
    
    Args:
        img: PIL Image object
    
    Returns:
        Tuple of processed numpy array and dict of image features
    """
    # Convert to grayscale and normalize
    img_gray = ImageOps.grayscale(img)
    img_array = np.array(img_gray)
    # Normalize image to 0-255 even if cv2 is not available
    if cv2 is not None:
        normalized = cv2.normalize(img_array, None, 0, 255, cv2.NORM_MINMAX)
    else:
        mn = float(img_array.min())
        mx = float(img_array.max())
        if mx - mn > 0:
            normalized = ((img_array - mn) / (mx - mn) * 255.0).astype(np.uint8)
        else:
            normalized = img_array.astype(np.uint8)
    
    # Split image into regions (3x3 grid)
    h, w = normalized.shape
    regions = []
    region_stats = []
    
    for i in range(3):
        for j in range(3):
            region = normalized[i*h//3:(i+1)*h//3, j*w//3:(j+1)*w//3]
            regions.append(region)
            
            # Calculate region statistics
            stats = {
                'mean': region.mean(),
                'std': region.std(),
                'min': region.min(),
                'max': region.max(),
                'position': (i, j)
            }
            region_stats.append(stats)
    
    # Find regions with anomalies
    overall_mean = normalized.mean()
    overall_std = normalized.std()
    anomalous_regions = []
    
    for idx, stats in enumerate(region_stats):
        if (abs(stats['mean'] - overall_mean) > overall_std * 1.5 or
            stats['std'] > overall_std * 1.2):
            anomalous_regions.append(idx)
    
    # Edge detection / contour analysis for shape analysis (optional cv2)
    contours = []
    if cv2 is not None:
        try:
            edges = cv2.Canny(normalized.astype(np.uint8), 100, 200)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            largest_area = max([cv2.contourArea(c) for c in contours]) if contours else 0
            edge_complexity = len(contours)
        except Exception:
            contours = []
            largest_area = 0
            edge_complexity = 0
    else:
        # Fallback: estimate edge complexity with a simple gradient magnitude
        gy, gx = np.gradient(normalized.astype(float))
        grad = np.hypot(gx, gy)
        edge_complexity = int((grad > grad.mean() + grad.std()).sum() / 50)
        largest_area = 0

    features = {
        'overall_mean': overall_mean,
        'overall_std': overall_std,
        'region_stats': region_stats,
        'anomalous_regions': anomalous_regions,
        'edge_complexity': edge_complexity,
        'largest_contour_area': largest_area
    }
    
    return normalized, features

from tumor_analyzer import analyze_tumor

class MockFile:
    def __init__(self, path):
        self.name = path

def analyze_scan(path: str) -> Dict[str, Any]:
    """Analyze a medical scan image for tumor detection using the ML model from tumor_analyzer.py.
    """
    try:
        # Validate file extension
        if not Path(path).suffix.lower() in VALID_EXTENSIONS:
            raise ValueError(f"Invalid file type. Supported types: {', '.join(VALID_EXTENSIONS)}")
        
        # Use the unified tumor_analyzer logic (which uses the ML model)
        result = analyze_tumor(MockFile(path))
        
        # Ensure result matches the expected API format if slightly different
        if "error" in result:
             raise Exception(result["error"])
             
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Failed to analyze image: {str(e)}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Failed to analyze image: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
