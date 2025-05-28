from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, make_response
from werkzeug.utils import secure_filename
import os
import platform
import subprocess
from image_handler import save_image, detect_watermark, get_sha256
from comparator import find_duplicate_images
import requests
from dotenv import load_dotenv
from flask import send_file
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime


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

@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' https://cdnjs.cloudflare.com; style-src 'self' https://fonts.googleapis.com https://cdnjs.cloudflare.com; font-src 'self' https://fonts.gstatic.com; connect-src 'self'; img-src 'self' data:;"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response

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
        try:
            # Validate path to avoid directory traversal
            safe_base = os.path.abspath('.')
            full_path = os.path.abspath(path)
            if not full_path.startswith(safe_base):
                return "Invalid path", 400

            if platform.system() == "Windows":
                subprocess.Popen(f'explorer /select,"{full_path}"')
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", "-R", full_path])
            else:
                subprocess.Popen(["xdg-open", os.path.dirname(full_path)])
            return '', 200
        except Exception as e:
            print("Error opening folder:", e)
            return "Failed to open folder", 500
    else:
        print("Invalid path or path does not exist.")
        return "Invalid path", 400
    
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io

@app.route('/download_report')
def download_report():
    filename = request.args.get('filename')
    match_paths = request.args.get('match_paths')
    watermark_found = request.args.get('watermark_found')
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Create the PDF in memory
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "Image Analysis Report")

    # Add the uploaded image
    try:
        img_reader = ImageReader(image_path)
        c.drawImage(img_reader, 50, height - 300, width=200, preserveAspectRatio=True, mask='auto')
    except Exception as e:
        print("Image error:", e)

    # Add watermark info
    c.setFont("Helvetica", 12)
    y = height - 320
    c.drawString(50, y, f"Watermark Found: {'Yes' if watermark_found == 'True' else 'No'}")
    y -= 20

    # Add duplicate matches
    c.drawString(50, y, "Duplicate Matches Found:")
    y -= 20
    if match_paths:
        for path in match_paths.split(';'):
            if y < 50:
                c.showPage()
                y = height - 50
            c.drawString(70, y, f"- {path}")
            y -= 20
    else:
        c.drawString(70, y, "No matches found.")

    c.showPage()
    c.save()

    pdf_buffer.seek(0)

    return send_file(pdf_buffer, as_attachment=True, download_name="report.pdf", mimetype="application/pdf")



if __name__ == '__main__':
    app.run(debug=True)
