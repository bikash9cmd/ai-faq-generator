# AI FAQ Generator

Generate a clean set of frequently asked questions and answers from a topic, a block of pasted text, or any public web page. A FastAPI backend calls Google Gemini with a strict JSON schema, so every answer is grounded in the content you supply, and a React front end lets you tune the output and regenerate any single FAQ you don't like.

## Features

- **Three input types:** a topic, pasted text (up to 50,000 characters), or a URL that is fetched and cleaned with BeautifulSoup.
- **Configurable output:** choose 1 to 10 FAQs, the output language and the tone (for example Professional or Friendly).
- **Grounded answers:** the prompt tells the model to use only the supplied content, and the response is validated against a Pydantic schema.
- **Regenerate one FAQ** without redoing the whole set.
- **History:** every generation is saved to a local SQLite database and listed at `/history`.
- **Safe URL fetching:** only `http`/`https`, internal and localhost addresses are blocked, with a 2 MB size limit and a 10 s timeout.
- **Rate limiting:** 10 requests per minute per IP on the generation endpoints (slowapi).

## Tech stack

| Layer | Tools |
|---|---|
| Backend | Python, FastAPI, Pydantic, pydantic-settings, slowapi |
| LLM | Google Gemini via the `google-genai` SDK |
| Scraping | requests, BeautifulSoup |
| Storage | SQLite |
| Frontend | React 19, Vite |
| Prototype | Jupyter notebook (`AI_FAQ_Generator_Prototype.ipynb`) |

## Project structure

```text
app/
  main.py               FastAPI app, routes, CORS, rate limiting
  faq_generator.py      Prompts and Gemini calls
  content_extractor.py  Safe URL fetching and text extraction
  database.py           SQLite history
  models.py             Request and response schemas
  config.py             Settings loaded from .env
frontend/               React + Vite UI
AI_FAQ_Generator_Prototype.ipynb   Original notebook prototype
```

## Getting started

### Prerequisites

- Python 3.11+
- Node.js 20+
- A Google Gemini API key ([get one here](https://aistudio.google.com/app/apikey))

### 1. Backend

```bash
git clone https://github.com/bikash9cmd/ai-faq-generator.git
cd ai-faq-generator

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install fastapi uvicorn slowapi pydantic-settings google-genai requests beautifulsoup4 python-dotenv

cp .env.example .env               # then put your key in GEMINI_API_KEY
uvicorn app.main:app --reload      # http://127.0.0.1:8000, docs at /docs
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev                        # http://localhost:5173
```

The frontend expects the API at `http://127.0.0.1:8000` (set in `frontend/src/App.jsx`).

## API

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/generate-faq` | Generate FAQs from a topic, text or URL |
| POST | `/regenerate-faq` | Regenerate one FAQ by its index |
| GET | `/history` | Past generations from SQLite |

Example request:

```bash
curl -X POST http://127.0.0.1:8000/generate-faq \
  -H "Content-Type: application/json" \
  -d '{"source_type": "topic", "source": "AWS Lambda cold starts", "faq_count": 5, "language": "English", "tone": "Professional"}'
```

## Configuration

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | yes | Google Gemini API key, read from `.env` |

## Author

**Bikash Kushwaha** · [GitHub](https://github.com/bikash9cmd)

## License

Released under the [MIT License](LICENSE).
