# SkillMap Backend

Flask REST API untuk SkillMap. Service ini menangani upload CV PDF, ekstraksi teks, skill matching, quiz, rekomendasi, dashboard overview, dan penyimpanan PostgreSQL opsional.

Repository ini adalah source of truth backend. Frontend SkillMap berjalan terpisah di `../Capstone` dan hanya berkomunikasi ke service ini lewat URL API.

## Struktur

- `src/app.py` - Flask app, route API, dan request/response handling.
- `src/db.py` - koneksi database dan utilitas persistence.
- `src/repositories` - akses data dan fallback in-memory store.
- `src/services` - business logic, analisis skill, dan client AI service.
- `src/data` - data lokal untuk taxonomy dan quiz bank.
- `database/schema.sql` - schema PostgreSQL.
- `server.env.example` - contoh environment variable lokal/deploy.
- `Procfile`, `railway.json`, `runtime.txt` - konfigurasi deploy Railway.

Panduan folder lengkap ada di [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md).

## Local Run

Create local environment file:

```powershell
Copy-Item server.env.example server.env
```

Set Supabase values in `server.env`. If `DATABASE_URL` is empty, the API still runs with in-memory storage for local testing.

For local frontend integration, keep:

```env
CORS_ORIGIN=http://localhost:5173,http://127.0.0.1:5173
```

Run the API:

```bash
pip install -r requirements.txt
flask --app src.app run --port 3001 --reload
```

Health check:

```txt
GET /health
```

Run the frontend from the separate frontend workspace:

```bash
cd ../Capstone
npm --prefix apps/web run dev
```

Frontend `.env` must point to this backend:

```env
VITE_API_URL=http://localhost:3001
```

## PostgreSQL

Use Supabase Postgres for persistent storage. In Supabase Dashboard, open **Connect** and copy a pooled Postgres connection string, then set:

```env
DATABASE_URL=postgresql://postgres.your-project-ref:your-database-password@aws-0-your-region.pooler.supabase.com:6543/postgres
DATABASE_SSL=true
```

The Flask API can create its base tables automatically when `AUTO_CREATE_TABLES=true`. The schema reference is also available in `database/schema.sql`.

## Supabase Auth

Backend token validation uses your Supabase project URL and anon key:

```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
```

## Railway

Start command:

```bash
gunicorn src.app:app --bind 0.0.0.0:$PORT
```

Environment variables:

```env
CORS_ORIGIN=https://capstone-odwh.vercel.app
DATABASE_URL=postgresql://user:password@host:port/db
AUTO_CREATE_TABLES=true
DATABASE_SSL=true
DEFAULT_USER_NAME=SkillMap User
DEFAULT_USER_EMAIL=local-user@skillmap.internal
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
AI_SERVICE_URL=https://api-skillmap-ai.up.railway.app
AI_TIMEOUT_SECONDS=20
OPENROUTER_API_KEY=optional-key-for-ai-generated-career-fit-quiz
OPENROUTER_MODEL=deepseek/deepseek-v4-flash:free
```

Set the frontend deployment variable to the Railway backend URL:

```env
VITE_API_URL=https://your-backend-domain.up.railway.app
```

For Vercel backend deployments, set the same `CORS_ORIGIN` value in the backend project's Environment Variables and redeploy. Do not include a trailing slash in the URL.

## Main Endpoints

- `GET /health`
- `GET /api/profile`
- `GET /api/profile/cv-analyses`
- `POST /api/cvs`
- `GET /api/quiz-questions`
- `POST /api/career-fit-quizzes`
- `POST /api/quiz-attempts`
- `POST /api/career-results`
- `POST /api/recommendations`
- `GET /api/dashboard-snapshots/overview`
- `GET /api/users/:userId/dashboard-snapshot`
- `POST /api/leads`
- `GET /api/project-requirements`

Legacy aliases such as `POST /api/cv/upload` and `POST /api/quiz/submit` remain available for compatibility.
