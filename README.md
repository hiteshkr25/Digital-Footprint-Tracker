🖼️ Image Tracking System
The Image Tracking System is a cybersecurity-focused web application that allows users to:

✅ Upload an image
✅ Find exact duplicates on their local system using SHA-256 hash matching
✅ Detect potential watermarks using OpenCV
✅ Perform an online reverse image search using ImgBB and SerpAPI
✅ Download a report of the results in PDF format
✅ Open matching file locations directly from the web interface

🚀 Features
Exact Duplicate Detection: Uses SHA-256 hashing to find exact copies of the uploaded image in a selected folder.

Watermark Detection: Detects if the uploaded image contains watermarks using edge detection.

Reverse Image Search: Uploads the image to ImgBB, then uses SerpAPI to find similar images online.

Interactive Results: Clickable file paths for local matches (opens file explorer) and clickable links for online results.

Download PDF Report: Export the search results for offline reference.

🛠️ Technologies Used
Python 3.x

Flask (Web framework)

OpenCV (Watermark detection)

imagehash (SHA-256 hash matching)

ImgBB API (Image hosting for reverse search)

SerpAPI (Google reverse image search)

HTML, CSS, JavaScript (Frontend)

📂 Project Structure
php
Copy
Edit
Image_Tracking_System/
├── app.py                 # Main Flask backend
├── comparator.py          # Local duplicate search logic (SHA-256)
├── image_handler.py       # Watermark detection, hashing
├── templates/
│   └── index.html         # Frontend HTML template
├── static/
│   └── uploads/           # Folder to store uploaded images
├── requirements.txt       # Required dependencies
└── README.md              # Project documentation
💻 Setup & Run Locally
1️⃣ Clone the repository:

bash
Copy
Edit
git clone https://github.com/yourusername/Image-Tracking-System.git
cd Image-Tracking-System
2️⃣ Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
3️⃣ Set up your .env file:

ini
Copy
Edit
IMGBB_API_KEY=your_imgbb_api_key
SERPAPI_KEY=your_serpapi_key
4️⃣ Run the application:

bash
Copy
Edit
python app.py
5️⃣ Open the web browser:

cpp
Copy
Edit
http://127.0.0.1:5000/
🌐 Usage
1️⃣ Upload an image file.
2️⃣ Provide a folder path to search for duplicates.
3️⃣ View:

Local matches (clickable links to open folder)

Watermark detection result

Online reverse search results

Download report as PDF

📌 Future Scope
User authentication

Advanced similarity detection (AI models)

Multi-folder search

Free alternatives for reverse image search APIs

🤝 Team
Arjun (Team Lead) – Flask Backend, API Integration

Priya – SHA-256 Logic, UI Design, PDF Export

Rohan – Watermark Detection, Folder Opening, UI Testing

🛡️ License
This project is for academic and educational purposes. Contact for permission to use or modify.
