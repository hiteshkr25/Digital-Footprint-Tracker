import os
from PIL import Image
import imagehash

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_image(file):
    """Save uploaded image to the uploads folder."""
    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    return filename, filepath

def generate_hash(image_path):
    """Generate average perceptual hash from an image."""
    image = Image.open(image_path)
    return imagehash.average_hash(image)
