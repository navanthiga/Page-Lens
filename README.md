# PageLens — AI-Powered UI Auditor

> Your users judge your UI in **0.05 seconds** — make sure it holds up.

PageLens is an AI-powered UI/UX audit tool that analyzes any website or design file and returns a structured report of accessibility failures, visual issues, and usability blind spots — before your users find them.

---

## What it does

Paste a URL, upload your HTML project, or drop in a screenshot. PageLens takes a full-page screenshot, sends it to Google Gemini's vision model, and returns a scored audit report with categorized issues and positives.

---

## Features

- **URL analysis** — paste any live website URL and get an instant audit
- **HTML file & folder upload** — analyze your project before deployment
- **Screenshot & PDF upload** — drop in a screenshot or a printed PDF for analysis
- **AI-powered reports** — powered by Google Gemini Vision
- **Structured JSON output** — overall score, categorized issues by severity, and positives
- **Clean frontend** — professional UI with issue severity badges and score visualization

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Browser Automation | Playwright + Chromium |
| AI Vision Model | Google Gemini 2.5 Flash |
| Image Processing | Pillow, pdf2image |
| Frontend | HTML, CSS, Vanilla JS |

---

## Project Structure

```
pagelens/
├── main.py          # Flask server with all API routes
├── index.html       # Frontend UI
├── requirements.txt # Python dependencies
├── Procfile         # Server start command
├── .env             # API keys (not committed)
└── .gitignore
```

---

## Getting Started

### Prerequisites

- Python 3.8+
- A [Google Gemini API key](https://aistudio.google.com)
- Poppler (for PDF support) — [Windows install guide](https://github.com/oschwartz10612/poppler-windows/releases)

### Installation

**1. Clone the repo**
```bash
git clone https://github.com/yourusername/pagelens.git
cd pagelens
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
playwright install chromium
```

**3. Set up your API key**

Create a `.env` file in the root folder:
```
GEMINI_API_KEY=your-gemini-api-key-here
```

**4. Run the server**
```bash
python main.py
```

**5. Open in browser**
```
http://127.0.0.1:5000
```

---

## API Routes

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Serves the frontend |
| `POST` | `/analyze` | Analyze a live URL |
| `POST` | `/analyze-folder` | Analyze uploaded HTML file or folder |
| `POST` | `/analyze-image` | Analyze a screenshot or PDF |
| `GET` | `/screenshot` | Returns the last captured screenshot |

---

## How it works

```
User Input (URL / File / Screenshot)
        ↓
Playwright captures full-page screenshot
        ↓
Screenshot sent to Gemini Vision API
        ↓
Gemini returns structured JSON audit
        ↓
Frontend renders scored report
```

---

## Sample Report Output

```json
{
  "overall_score": 5,
  "issues": [
    {
      "type": "visual",
      "severity": "high",
      "description": "Excessive visual clutter with too many competing promotional banners."
    },
    {
      "type": "accessibility",
      "severity": "medium",
      "description": "Low contrast text on bright yellow backgrounds causes visual fatigue."
    }
  ],
  "positives": [
    "Clear and prominent search bar",
    "Consistent color scheme across sections"
  ]
}
```

---

## Limitations

- Template-based frontends (Jinja, Django, PHP) won't render correctly via file upload — use the screenshot tab instead
- Sites with heavy ad tracking may timeout on URL analysis
- Gemini free tier has usage limits — check [Google AI Studio](https://aistudio.google.com) for quota details

---

## Built with

This project was built as a learning project to practice:
- Vision Language Model (VLM) prompt engineering
- Python Flask backend development
- Browser automation with Playwright
- Structured AI output design
- Full-stack integration

---

## License

MIT
