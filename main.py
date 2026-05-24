from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from playwright.sync_api import sync_playwright
from google import genai
from PIL import Image
import json
import os
import base64
import shutil
from pdf2image import convert_from_path

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/root/.cache/ms-playwright"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_PATH = os.path.join(BASE_DIR, "screenshot.png")

PROMPT = """
You are a senior UX and accessibility expert. Analyze this website screenshot and return ONLY valid JSON with this exact structure, no markdown, no explanation:

{
    "overall_score": <number 1-10>,
    "issues": [
        {
            "type": "<visual|usability|accessibility|performance>",
            "severity": "<high|medium|low>",
            "description": "<one clear sentence>"
        }
    ],
    "positives": ["<short phrase>", "<short phrase>"]
}

Be critical, specific, and professional. Limit to 5 issues max and 4 positives max.
"""

def take_screenshot(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        try:
            page.click("text=Close", timeout=2000)
        except:
            pass
        try:
            page.click("[aria-label='Close']", timeout=2000)
        except:
            pass
        page.wait_for_timeout(2000)
        page.screenshot(path=SCREENSHOT_PATH, full_page=True)
        browser.close()

def take_screenshot_local(file_path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()

        def block_requests(route):
            if route.request.url.startswith("http"):
                route.abort()
            else:
                route.continue_()

        context.route("**/*", block_requests)
        page = context.new_page()
        page.goto(f"file:///{file_path}", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        page.screenshot(path=SCREENSHOT_PATH, full_page=True)
        browser.close()

def analyze_screenshot():
    client = genai.Client(api_key=GEMINI_API_KEY)
    image = Image.open(SCREENSHOT_PATH)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[PROMPT, image]
    )

    raw = response.text.strip()
    clean = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)

def find_index(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower() == "index.html":
                return os.path.join(root, file).replace("\\", "/")
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".html"):
                return os.path.join(root, file).replace("\\", "/")
    return None

@app.route("/")
def index():
    return send_file(os.path.join(BASE_DIR, "index.html"))

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "Missing url"}), 400

    try:
        take_screenshot(url)
        report = analyze_screenshot()
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/screenshot", methods=["GET"])
def get_screenshot():
    try:
        with open(SCREENSHOT_PATH, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return jsonify({"image": encoded})
    except:
        return jsonify({"error": "No screenshot found"}), 404

@app.route("/analyze-folder", methods=["POST"])
def analyze_folder():
    files = request.files.getlist("files")

    if not files:
        return jsonify({"error": "Missing files"}), 400

    try:
        folder_path = os.path.join(BASE_DIR, "uploaded_project")
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        os.makedirs(folder_path)

        for file in files:
            file_dest = os.path.join(folder_path, file.filename)
            os.makedirs(os.path.dirname(file_dest), exist_ok=True)
            file.save(file_dest)

        index_path = find_index(folder_path)
        if not index_path:
            return jsonify({"error": "No index.html found in uploaded folder"}), 400

        take_screenshot_local(index_path)
        report = analyze_screenshot()
        return jsonify(report)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/analyze-image", methods=["POST"])
def analyze_image():
    file = request.files.get("image")

    if not file:
        return jsonify({"error": "Missing image"}), 400

    try:
        ext = os.path.splitext(file.filename)[1].lower()
        upload_path = os.path.join(BASE_DIR, "uploaded_screenshot" + ext)
        file.save(upload_path)

        if ext == ".pdf":
            pages = convert_from_path(upload_path, dpi=150)

            total_height = sum(p.height for p in pages)
            max_width = max(p.width for p in pages)

            stitched = Image.new("RGB", (max_width, total_height), (255, 255, 255))
            y = 0
            for page in pages:
                stitched.paste(page, (0, y))
                y += page.height
            stitched.save(SCREENSHOT_PATH, "PNG")

        else:
            img = Image.open(upload_path)
            img.save(SCREENSHOT_PATH, "PNG")

        report = analyze_screenshot()
        return jsonify(report)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/analyze-file", methods=["POST"])
def analyze_file():
    file = request.files.get("file")

    if not file:
        return jsonify({"error": "Missing file"}), 400

    try:
        file_path = os.path.join(BASE_DIR, "uploaded.html")
        file.save(file_path)
        take_screenshot_local(file_path)
        report = analyze_screenshot()
        return jsonify(report)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)