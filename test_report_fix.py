
import sys
import os
from pathlib import Path

# Add current dir to path
sys.path.append(str(Path(__file__).parent))

from tumor_analyzer import analyze_tumor
from generate_scan_report_pdf import generate_report

class MockFile:
    def __init__(self, path):
        self.name = path

# Create a dummy image if needed, or use test_image.png if exists
test_img = "test_image.png"
if not os.path.exists(test_img):
    import cv2
    import numpy as np
    img = np.zeros((512, 512, 3), dtype=np.uint8)
    cv2.circle(img, (256, 256), 50, (255, 255, 255), -1)
    cv2.imwrite(test_img, img)

print("Analyzing tumor...")
result = analyze_tumor(MockFile(test_img))
print("Result:", result)

print("\nGenerating report...")
report_path = generate_report(result, out_dir=".")
print("Report generated at:", report_path)
