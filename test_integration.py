from tumor_analyzer import analyze_tumor
import os

class MockFile:
    def __init__(self, path):
        self.name = path

# Test with an image from the dataset
test_image_path = "data/Testing/glioma_tumor/image(1).jpg"
if os.path.exists(test_image_path):
    print(f"Testing with: {test_image_path}")
    result = analyze_tumor(MockFile(test_image_path))
    print(result)
else:
    print(f"Test image not found at: {test_image_path}")
