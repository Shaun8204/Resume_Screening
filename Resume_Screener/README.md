# Resume Screener

Local development quick start

Backend (FastAPI):

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend (Vite + React):

```bash
cd frontend
npm install
npm run dev
```

You can also run using docker-compose (backend only):

```bash
docker compose up --build
```

API
- `POST /screen` - form data `job_description` (string), `files` (multipart many). Returns ranked list of matches.


Embeddings
- The backend uses `sentence-transformers` (local) to compute semantic embeddings by default. Install `sentence-transformers` and `torch` in the backend virtualenv:

```bash
pip install -r requirements.txt
```

- If `sentence-transformers` is not available the server falls back to TF-IDF vectors for lightweight local testing.

