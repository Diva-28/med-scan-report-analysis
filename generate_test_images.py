import numpy as np
from PIL import Image, ImageDraw
import random
import os

def create_test_image(width=512, height=512, has_tumor=False, tumor_size=None, location=None):
    """Create a simulated brain scan test image"""
    # Create base "brain" image
    img = Image.new('L', (width, height), color=50)
    draw = ImageDraw.Draw(img)
    
    # Draw basic brain shape
    brain_width = int(width * 0.8)
    brain_height = int(height * 0.9)
    x1 = (width - brain_width) // 2
    y1 = (height - brain_height) // 2
    x2 = x1 + brain_width
    y2 = y1 + brain_height
    
    # Fill brain with texture
    for i in range(1000):
        x = random.randint(x1, x2)
        y = random.randint(y1, y2)
        size = random.randint(5, 20)
        brightness = random.randint(100, 200)
        draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], fill=brightness)
    
    if has_tumor:
        # Add simulated tumor
        if tumor_size is None:
            tumor_size = random.randint(30, 80)
        
        if location is None:
            tumor_x = random.randint(x1 + tumor_size, x2 - tumor_size)
            tumor_y = random.randint(y1 + tumor_size, y2 - tumor_size)
        else:
            # Parse location string to determine position
            if 'left' in location.lower():
                tumor_x = x1 + width//4
            else:
                tumor_x = x2 - width//4
                
            if 'frontal' in location.lower():
                tumor_y = y1 + height//4
            elif 'temporal' in location.lower():
                tumor_y = y1 + height//2
            else:
                tumor_y = y2 - height//4
        
        # Draw tumor with irregular shape and different intensity
        for i in range(50):
            offset_x = random.gauss(0, tumor_size//4)
            offset_y = random.gauss(0, tumor_size//4)
            size = random.randint(tumor_size//2, tumor_size)
            brightness = random.randint(220, 250)
            draw.ellipse([
                tumor_x + offset_x - size//2, 
                tumor_y + offset_y - size//2,
                tumor_x + offset_x + size//2, 
                tumor_y + offset_y + size//2
            ], fill=brightness)
    
    return img

def main():
    # Create test images directory
    os.makedirs("test_images", exist_ok=True)
    
    # Create normal scans
    for i in range(3):
        img = create_test_image(has_tumor=False)
        img.save(f"test_images/normal_scan_{i+1}.png")
    
    # Create scans with tumors in different locations
    tumor_cases = [
        {"location": "Left frontal lobe", "size": 60},
        {"location": "Right temporal lobe", "size": 45},
        {"location": "Left occipital lobe", "size": 30},
    ]
    
    for i, case in enumerate(tumor_cases):
        img = create_test_image(
            has_tumor=True,
            tumor_size=case["size"],
            location=case["location"]
        )
        img.save(f"test_images/tumor_scan_{i+1}.png")

if __name__ == "__main__":
    main()