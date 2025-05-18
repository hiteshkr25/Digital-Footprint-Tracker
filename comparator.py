import os
from image_handler import get_sha256

def find_duplicate_images(target_hash, root_folder, uploaded_path):
    match_paths = []
    target_size = os.path.getsize(uploaded_path)

    for root, dirs, files in os.walk(root_folder):
        for name in files:
            if not name.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            filepath = os.path.join(root, name)

            try:
                if os.path.getsize(filepath) != target_size:
                    continue
                if get_sha256(filepath) == target_hash:
                    match_paths.append(filepath)
            except Exception:
                continue

    return match_paths
