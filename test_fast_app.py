"""
Test the fast chatbot by simulating an image upload.
"""
import sys
sys.path.insert(0, r'c:\Users\kanimozhi\Downloads\chatbot')

from fast_gradio_app import fast_analyze_and_report
from pathlib import Path

# Test with a simple image (create a dummy test image)
from PIL import Image
import numpy as np

# Create a test image
test_img = Image.new('RGB', (512, 512), color='white')
test_img_path = Path(r'c:\Users\kanimozhi\Downloads\chatbot\test_image.png')
test_img.save(test_img_path)

print("Testing fast_analyze_and_report function...")
try:
    report, prescription, qr_img, status = fast_analyze_and_report(str(test_img_path))
    print(f"\n✅ Test successful!")
    print(f"Report: {report}")
    print(f"Prescription: {prescription}")
    print(f"QR Image: {qr_img}")
    print(f"\nStatus:\n{status}")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
