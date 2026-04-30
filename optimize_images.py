import os
from PIL import Image

def optimize_image(input_path):
    base, ext = os.path.splitext(input_path)
    if ext.lower() == '.webp':
        return input_path
    
    output_path = base + ".webp"
    
    try:
        with Image.open(input_path) as img:
            # Resize if width > 1920
            if img.width > 1920:
                ratio = 1920.0 / img.width
                new_height = int(img.height * ratio)
                img = img.resize((1920, new_height), Image.Resampling.LANCZOS)
                
            img.save(output_path, "webp", quality=80, method=4)
            print(f"Optimized: {input_path} -> {output_path}")
            return output_path
    except Exception as e:
        print(f"Error optimizing {input_path}: {e}")
        return input_path

images_to_optimize = [
    "graphics/logos/ALLIANCE Logo with background.png",
    "graphics/components/tokens.png",
    "graphics/components/action-report_face.png"
]

crisis_dir = "graphics/components/crisis"
if os.path.exists(crisis_dir):
    for f in os.listdir(crisis_dir):
        if f.lower().endswith(('.png', '.jpg', '.jpeg')):
            images_to_optimize.append(os.path.join(crisis_dir, f))

for img_path in images_to_optimize:
    if os.path.exists(img_path):
        optimize_image(img_path)
    else:
        print(f"Not found: {img_path}")
