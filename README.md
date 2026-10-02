# ⚡ ComicCraft AI — Complete Setup Guide

## VS Code Setup, Installation & Running Instructions

---

## 📁 Project Structure

```
ComicCraftAi/
├── app/
│   ├── __init__.py         # Package init
│   ├── config.py           # App settings & env variables
│   ├── main.py             # FastAPI app entry point
│   ├── routes.py           # All API routes
│   ├── schemas.py          # Pydantic request/response models
│   ├── gemini_flash.py     # Gemini 1.5 Flash — comic outline generator
│   ├── gemini_pro.py       # Gemini 1.5 Pro — narration & dialogue writer
│   ├── image_generator.py  # Stable Diffusion image generator (HF API)
│   ├── layout_builder.py   # Combines panels into structured layout
│   └── exporters.py        # PDF export with FPDF
├── templates/
│   ├── index.html          # Homepage (comic creation form)
│   ├── comic_preview.html  # Comic preview page (all panels)
│   ├── export_success.html # Export success confirmation page
│   ├── test_image.html     # Developer image test page
│   └── error.html          # Error page
├── static/
│   ├── css/
│   │   └── style.css       # Global stylesheet (dark theme)
│   ├── js/
│   │   └── main.js         # Frontend JavaScript
│   ├── img/
│   │   └── placeholder.png # Fallback image
│   ├── panels/             # Generated panel images (auto-created)
│   └── exports/            # Generated PDFs (auto-created)
├── .env                    # Your API keys (never commit!)
├── .env.example            # Template for .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Prerequisites

- Python 3.9+
- VS Code with Python extension
- A Google Gemini API Key
- A Hugging Face API Token

---

## 🚀 Installation Steps

### Step 1 — Get API Keys

**Google Gemini API Key:**
1. Visit https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

**Hugging Face API Token:**
1. Visit https://huggingface.co/settings/tokens
2. Click "New token" → set to "Read"
3. Copy the token

---

### Step 2 — Open in VS Code

```bash
code /home/logeswaran-a/Desktop/ComicCraftAi
```

Or: File → Open Folder → select `ComicCraftAi`

---

### Step 3 — Set Up Environment Variables

Copy the example file and add your keys:

```bash
cp .env.example .env
```

Edit `.env`:
```env
GEMINI_API_KEY=AIza...your_actual_key_here
HF_API_KEY=hf_...your_actual_token_here
```

---

### Step 4 — Create & Activate Virtual Environment

**In VS Code Terminal (Ctrl+`):**

```bash
# Create virtual environment
python3 -m venv env

# Activate (Linux/macOS)
source env/bin/activate

# Activate (Windows)
env\Scripts\activate
```

**Select Python Interpreter in VS Code:**
- Press `Ctrl+Shift+P`
- Type "Python: Select Interpreter"
- Choose `./env/bin/python`

---

### Step 5 — Install Dependencies

```bash
pip install -r requirements.txt
```

Expected install time: 2–5 minutes

---

### Step 6 — Run the Application

```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO: ComicCraft AI — Starting up
INFO: Homepage:   http://127.0.0.1:8000
INFO: API Docs:   http://127.0.0.1:8000/docs
INFO: Uvicorn running on http://127.0.0.1:8000
```

---

## 🌐 Access the Application

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:8000 | Homepage — Comic creation form |
| http://127.0.0.1:8000/docs | FastAPI Swagger API documentation |
| http://127.0.0.1:8000/redoc | ReDoc API documentation |
| http://127.0.0.1:8000/test-image | Test image generation |

---

## 🎯 How to Use

1. **Open** http://127.0.0.1:8000
2. **Fill in the form:**
   - Story Prompt (e.g., "A brave fox exploring an enchanted forest")
   - Main Character Name (e.g., "Finn")
   - Setting (Forest, Space, City, etc.)
   - Story Tone (Dramatic, Funny, Poetic, etc.)
   - Art Style (Anime, Comic Book, Pixel Art, Realistic)
3. **Click** "Generate My Comic"
4. **Wait** 1–3 minutes for AI generation
5. **Preview** your 5-panel comic
6. **Download** as PDF

---

## 🧪 Testing the API

### Test via Swagger UI:
1. Open http://127.0.0.1:8000/docs
2. Click `POST /generate-comic/json`
3. Click "Try it out"
4. Enter:
```json
{
  "prompt": "A brave fox exploring an enchanted forest",
  "character": "Finn",
  "setting": "forest",
  "tone": "dramatic",
  "art_style": "anime"
}
```
5. Click "Execute"

### Test via curl:
```bash
curl -X POST http://127.0.0.1:8000/generate-comic/json \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A brave fox exploring an enchanted forest",
    "character": "Finn",
    "setting": "forest",
    "tone": "dramatic",
    "art_style": "anime"
  }'
```

### Test image generation:
```
http://127.0.0.1:8000/test-image?img_prompt=anime fox in enchanted forest
```

---

## 🔧 VS Code Launch Configuration

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "ComicCraft FastAPI",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload", "--port", "8000"],
      "jinja": true,
      "justMyCode": true,
      "envFile": "${workspaceFolder}/.env"
    }
  ]
}
```

Then press **F5** to launch with debugger.

---

## 🛠️ API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Homepage |
| POST | `/generate` | Form-based comic generation |
| POST | `/generate-comic/json` | JSON API comic generation |
| GET | `/export-success` | Export success page |
| GET | `/download-pdf?pdf_path=...` | Download PDF |
| GET | `/test-image?img_prompt=...` | Test image generation |
| GET | `/docs` | Swagger API docs |
| GET | `/redoc` | ReDoc API docs |

---

## ⚠️ Troubleshooting

### "GEMINI_API_KEY not set"
→ Make sure your `.env` file has the correct key

### "HF API 503 - Model loading"
→ The free HF tier cold-starts. Wait 30s and try again

### Images showing as placeholder
→ Check your HF_API_KEY is valid and has "read" permissions

### "Module not found"
→ Ensure venv is activated: `source env/bin/activate`

### Port already in use
→ Kill existing process: `pkill -f uvicorn` or use different port:
```bash
uvicorn app.main:app --reload --port 8001
```

---

## 📦 Tech Stack

| Technology | Purpose |
|-----------|---------|
| FastAPI | Web framework & API |
| Uvicorn | ASGI server |
| Jinja2 | HTML template rendering |
| Gemini 1.5 Flash | Comic panel outline generation |
| Gemini 1.5 Pro | Story narration & dialogue |
| Stable Diffusion (HF API) | Comic-style image generation |
| FPDF2 | PDF export |
| Pillow | Image processing |
| python-dotenv | Environment variable loading |

---

*Built with ❤️ using Google Gemini AI + Stable Diffusion*
