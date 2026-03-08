# MindClear AI

**Mental load manager** — turn a messy brain dump into structured tasks. Paste your thoughts; get a clear task list with categories, priorities, and deadlines.

---

## About

When your head is full of scattered to-dos (“call mom, pay rent, dentist next week”), organizing them is tedious. MindClear AI lets you paste that stream of consciousness and get back a structured list: tasks, categories (Work, Personal, Health, Finance), priorities (High/Medium/Low), and optional due dates. You can filter, mark items done, delete them, and revisit past brain dumps.

---

## Features

- **Brain dump** — Paste free-form text; the app turns it into tasks (local parser by default, or optional AI).
- **Task dashboard** — List tasks, filter by category/priority/status, mark complete, delete.
- **History** — View past brain dumps and their task lists.
- **Free to run** — Works with no API keys using a built-in parser; optional Hugging Face for smarter parsing.

---

## Tech stack

| Layer      | Stack |
|-----------|--------|
| Frontend  | React, Vite, Tailwind CSS |
| Backend   | FastAPI, SQLAlchemy, Pydantic |
| Database  | PostgreSQL (Neon/Supabase) or SQLite (dev) |
| Deploy    | Backend → Render / Railway · Frontend → Vercel |

---

## Getting started

### Prerequisites

- Python 3.10+
- Node.js 18+
- (Optional) PostgreSQL for production

### Installation

1. **Clone the repo**

   ```bash
   git clone https://github.com/your-username/MindClear-AI.git
   cd MindClear-AI
   ```

2. **Backend**

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

3. **Frontend**

   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Environment**

   Copy `.env.example` to `.env` in the project root and adjust if needed. Defaults work for local dev (SQLite, local parser).

---

## Running the app

**Terminal 1 — backend**

```bash
source .venv/bin/activate
python -m uvicorn backend.app.main:app --reload
```

**Terminal 2 — frontend**

```bash
cd frontend && npm run dev
```

Open **http://localhost:5173**. The frontend proxies `/api` to the backend.

---

## Environment variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database URL | `sqlite:///./dev.db` |
| `CORS_ORIGINS` | Allowed frontend origins (comma-separated) | `http://localhost:5173,http://localhost:3000` |
| `USE_HUGGINGFACE` | Use Hugging Face for task extraction | `false` |
| `HUGGINGFACE_API_TOKEN` | Required if `USE_HUGGINGFACE=true` | — |
| `HUGGINGFACE_MODEL` | Model name (Hugging Face) | `google/gemma-2-9b-it` |

For production frontend (e.g. Vercel), set `VITE_API_URL` to your backend URL.

---

## Project structure

```
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app, CORS, routes
│   │   ├── config.py         # Settings (Pydantic)
│   │   ├── database.py       # SQLAlchemy engine & session
│   │   ├── models.py         # Conversion, Task
│   │   ├── schemas.py        # Pydantic request/response
│   │   ├── ai_service.py     # Brain-dump → tasks
│   │   └── routers/          # analyze, tasks, conversions
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/              # API client
│   │   ├── components/       # UI components
│   │   └── pages/            # Home, Dashboard
│   └── package.json
├── .env.example
├── Procfile                  # For Render/Railway
├── requirements.txt          # Backend deps (for deploy from root)
└── README.md
```

---

## Deployment

- **Database:** Create a Postgres project on [Neon](https://neon.tech) or [Supabase](https://supabase.com) and set `DATABASE_URL`.
- **Backend:** Deploy to [Render](https://render.com) or [Railway](https://railway.app) with build `pip install -r requirements.txt` and start `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`. Set `CORS_ORIGINS` to your frontend URL.
- **Frontend:** Deploy to [Vercel](https://vercel.com) with root directory `frontend`, and set `VITE_API_URL` to your backend URL.

---

## License

MIT.
