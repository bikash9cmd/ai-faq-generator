# AI FAQ Generator

> **Tech stack:** Python · FastAPI · React · Google Gemini (LLM)

Generate clear, ready-to-publish FAQs from a topic, a block of pasted text or a webpage URL. A FastAPI backend calls Google Gemini with a structured JSON schema, and a React + Vite frontend lets you pick the number of questions, language and tone, regenerate any single FAQ and browse past results.

## Features

- Three input modes: **topic**, **pasted text** or **URL** (the page is fetched and cleaned with BeautifulSoup)
- 1 to 10 FAQs per request, in any language and tone (Professional, Friendly and so on)
- Regenerate one FAQ without redoing the whole set
- Structured output validated with Pydantic, so the API always returns `{ "faqs": [{ "question", "answer" }] }`
- History of generated FAQs stored in SQLite
- Rate limiting (10 requests per minute per IP) with SlowAPI
- URL validation that blocks private and loopback addresses (SSRF protection)
- Prototype notebook showing the prompt design and experiments

## Tech stack

| Layer | Tools |
| --- | --- |
| Backend | Python, FastAPI, Uvicorn, Pydantic, SlowAPI, SQLite |
| LLM | Google Gemini via the `google-genai` SDK |
| Frontend | React 19, Vite |
| Prototyping | Jupyter Notebook |

## Project structure

```
.
├── app/
│   ├── main.py               # FastAPI app, routes, CORS, rate limiting
│   ├── faq_generator.py      # Gemini prompts for generating / regenerating FAQs
│   ├── content_extractor.py  # Safe URL fetching and text extraction
│   ├── database.py           # SQLite history
│   ├── models.py             # Pydantic request/response models
│   └── config.py             # Settings loaded from .env
├── frontend/                 # React + Vite UI
├── AI_FAQ_Generator_Prototype.ipynb
├── requirements.txt          # Backend dependencies
├── requirements-notebook.txt # Backend + Jupyter for the notebook
└── .env.example
```

## Getting started

### 1. Backend

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # then put your key in GEMINI_API_KEY
uvicorn app.main:app --reload --port 8000
```

API docs are available at http://127.0.0.1:8000/docs.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev                        # http://localhost:5173
```

The frontend calls the API at `http://127.0.0.1:8000`.

## API

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `POST` | `/generate-faq` | Generate FAQs from a topic, text or URL |
| `POST` | `/regenerate-faq` | Regenerate one FAQ by index |
| `GET` | `/history` | Previously generated FAQs |

Example request:

```bash
curl -X POST http://127.0.0.1:8000/generate-faq \
  -H "Content-Type: application/json" \
  -d '{"source_type": "topic", "source": "Amazon S3 storage classes", "faq_count": 5, "language": "English", "tone": "Professional"}'
```

## Environment variables

| Name | Description |
| --- | --- |
| `GEMINI_API_KEY` | Google Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey) |

Never commit your real `.env` file; it is already in `.gitignore`.
