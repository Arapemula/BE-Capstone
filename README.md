# SkillMap Backend

Flask REST API untuk SkillMap. Service ini menangani upload CV PDF, ekstraksi teks, skill matching, quiz, rekomendasi, dashboard overview, dan penyimpanan PostgreSQL opsional.

## Local Run

```bash
pip install -r requirements.txt
flask --app src.app run --port 3001 --reload
```

Health check:

```txt
GET /health
```

## Railway

Start command:

```bash
gunicorn src.app:app --bind 0.0.0.0:$PORT
```

Environment variables:

```env
CORS_ORIGIN=https://your-frontend.vercel.app
DATABASE_URL=postgresql://user:password@host:port/db
AUTO_CREATE_TABLES=true
DATABASE_SSL=false
AI_SERVICE_URL=https://api-skillmap-ai.up.railway.app
AI_TIMEOUT_SECONDS=20
```

If `DATABASE_URL` is not configured, the API still runs with in-memory storage for demo usage.

## Main Endpoints

- `GET /health`
- `GET /api/roles`
- `POST /api/cv/upload`
- `POST /api/recommendations`
- `GET /api/dashboard/overview`
- `POST /api/leads`
