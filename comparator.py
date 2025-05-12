import os
from image_handler import generate_hash

REFERENCE_FOLDER = 'static/reference_images'
os.makedirs(REFERENCE_FOLDER, exist_ok=True)

def compare_with_reference_images(uploaded_hash):
    """Compare uploaded image hash with reference images and return similarity scores."""
    results = []
    print("Comparing uploaded image with reference images...")

    for filename in os.listdir(REFERENCE_FOLDER):
        if filename.lower().endswith(('jpg', 'jpeg', 'png')):
            ref_path = os.path.join(REFERENCE_FOLDER, filename)
            try:
                ref_hash = generate_hash(ref_path)
                hamming_distance = uploaded_hash - ref_hash
                similarity_score = 100 - (hamming_distance / 64 * 100)
                results.append((filename, round(similarity_score, 2)))
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    return results
