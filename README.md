# SkillMap — Backend

Flask REST API untuk SkillMap. Service ini menangani upload CV (PDF), ekstraksi teks, skill matching, quiz karier, rekomendasi jalur belajar, ringkasan dashboard, dan penyimpanan ke PostgreSQL.

Repo ini adalah source of truth backend. Frontend berjalan terpisah di `../Capstone` dan berkomunikasi ke service ini melalui URL API.

## Struktur Folder

```
BE-Capstone/
├── src/
│   ├── app.py              # Flask app, route API, dan request/response handling
│   ├── db.py               # Koneksi database dan utilitas persistence
│   ├── auth.py             # Validasi token Supabase
│   ├── repositories/       # Akses data dan fallback in-memory
│   ├── services/           # Business logic, analisis skill, dan client AI
│   └── data/               # Taxonomy skill lokal dan quiz bank
├── database/
│   └── schema.sql          # Skema PostgreSQL
├── docs/                   # Dokumentasi backend
├── Procfile                # Perintah start Railway
├── railway.json            # Konfigurasi Railway
├── runtime.txt             # Versi Python runtime
├── requirements.txt        # Dependensi Python
├── server.env.example      # Template environment variable
└── README.md
```

## Menjalankan Secara Lokal

Buat file environment lokal:

```powershell
Copy-Item server.env.example server.env
```

Isi nilai Supabase di `server.env`. Jika `DATABASE_URL` dikosongkan, API tetap berjalan menggunakan penyimpanan in-memory untuk keperluan pengujian lokal.

Untuk integrasi dengan frontend lokal, pastikan nilai berikut ada:

```env
CORS_ORIGIN=http://localhost:5173,http://127.0.0.1:5173
```

Jalankan API:

```bash
pip install -r requirements.txt
flask --app src.app run --port 3001 --reload
```

Health check:

```
GET /health
```

Jalankan frontend dari workspace terpisah:

```bash
cd ../Capstone
npm --prefix apps/web run dev
```

File `.env` frontend harus mengarah ke backend ini:

```env
VITE_API_URL=http://localhost:3001
```

## PostgreSQL

Gunakan Supabase Postgres sebagai penyimpanan persisten. Buka **Connect** di Supabase Dashboard, salin connection string pooled, lalu isi:

```env
DATABASE_URL=postgresql://postgres.your-project-ref:your-database-password@aws-0-your-region.pooler.supabase.com:6543/postgres
DATABASE_SSL=true
```

Flask API dapat membuat tabel secara otomatis jika `AUTO_CREATE_TABLES=true`. Referensi skema tersedia di `database/schema.sql`.

## Supabase Auth

Validasi token backend menggunakan project URL dan anon key Supabase:

```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
```

## Deploy ke Railway

Start command:

```bash
gunicorn src.app:app --bind 0.0.0.0:$PORT
```

Environment variable yang dibutuhkan:

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
OPENROUTER_MODEL=deepseek/deepseek-v4-flash
```

Set variabel berikut di sisi frontend untuk mengarah ke backend Railway:

```env
VITE_API_URL=https://your-backend-domain.up.railway.app
```

Untuk deployment backend di Vercel, set nilai `CORS_ORIGIN` yang sama di environment variable project backend dan redeploy. Jangan tambahkan trailing slash di URL.

## Endpoint Utama

| Method | Endpoint |
|--------|----------|
| GET | `/health` |
| GET | `/api/profile` |
| GET | `/api/profile/cv-analyses` |
| POST | `/api/cvs` |
| GET | `/api/quiz-questions` |
| POST | `/api/career-fit-quizzes` |
| POST | `/api/quiz-attempts` |
| POST | `/api/career-results` |
| POST | `/api/recommendations` |
| GET | `/api/dashboard-snapshots/overview` |
| GET | `/api/users/:userId/dashboard-snapshot` |
| POST | `/api/leads` |
| GET | `/api/project-requirements` |

Alias lama seperti `POST /api/cv/upload` dan `POST /api/quiz/submit` masih tersedia untuk kompatibilitas.
