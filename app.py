from flask import Flask, render_template, request
from image_handler import save_image, generate_hash
from comparator import compare_with_reference_images

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    filename = None

    if request.method == "POST":
        file = request.files.get("image")
        if file and file.filename != '':
            filename, filepath = save_image(file)
            uploaded_hash = generate_hash(filepath)
            results = compare_with_reference_images(uploaded_hash)

    return render_template("index.html", results=results, filename=filename)

if __name__ == "__main__":
    app.run(debug=True)
