from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import platform
import subprocess
from image_handler import save_image, detect_watermark, get_sha256
from comparator import find_duplicate_images
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_to_imgbb(image_path):
    import base64
    with open(image_path, "rb") as file:
        encoded = base64.b64encode(file.read())

    response = requests.post(
        "https://api.imgbb.com/1/upload",
        data={
            "key": IMGBB_API_KEY,
            "image": encoded
        }
    )

    if response.status_code == 200:
        return response.json()["data"]["url"]
    else:
        print("ImgBB upload failed:", response.text)
        return None

def search_online(image_url):
    try:
        params = {
            "engine": "google_reverse_image",
            "image_url": image_url,
            "api_key": SERPAPI_KEY
        }
        response = requests.get("https://serpapi.com/search", params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get("image_results", [])
        else:
            print("SerpAPI error:", response.text)
            return []
    except Exception as e:
        print("Search error:", e)
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    filename = None
    match_paths = []
    online_results = []
    watermark_found = None

    if request.method == 'POST':
        file = request.files.get('image')
        folder_path = request.form.get('folder', '').strip()

        if not file or not allowed_file(file.filename):
            flash("Invalid file or no file selected.")
            return render_template('index.html')

        if not folder_path or not os.path.exists(folder_path):
            flash("Folder path is missing or does not exist.")
            return render_template('index.html')

        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)

        # Duplicate check
        uploaded_hash = get_sha256(upload_path)
        match_paths = find_duplicate_images(uploaded_hash, folder_path, upload_path)

        # Watermark detection
        watermark_found = detect_watermark(upload_path)

        # Upload to imgbb + reverse search
        public_url = upload_to_imgbb(upload_path)
        if public_url:
            online_results = search_online(public_url)
        else:
            flash("ImgBB upload failed.")

    return render_template('index.html',
                           filename=filename,
                           match_paths=match_paths,
                           online_results=online_results,
                           watermark_found=watermark_found)

@app.route('/open')
def open_file():
    path = request.args.get('path')
    if path and os.path.exists(path):
        folder = os.path.dirname(path)
        try:
            if platform.system() == "Windows":
                os.startfile(folder)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", folder])
            else:  # Linux
                subprocess.Popen(["xdg-open", folder])
        except Exception as e:
            flash(f"Failed to open folder: {e}")
    else:
        flash("Invalid or missing file path.")
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
