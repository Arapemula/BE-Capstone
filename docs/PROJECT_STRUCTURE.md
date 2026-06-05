# Struktur Proyek Backend

`BE-Capstone` adalah workspace Flask API SkillMap. Pekerjaan frontend ada di `../Capstone`.

```
BE-Capstone/
├── src/
│   ├── app.py              # Flask app dan route API
│   ├── db.py               # Koneksi database dan helper
│   ├── auth.py             # Validasi token Supabase
│   ├── repositories/       # Persistence layer dan in-memory fallback
│   ├── services/           # Business logic dan integrasi AI service
│   └── data/               # Quiz bank dan taxonomy skill
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

## Lokasi Pengerjaan

| Kebutuhan | Lokasi |
|-----------|--------|
| Tambah atau ubah endpoint API | `src/app.py` |
| Business logic yang reusable | `src/services/` |
| Akses database atau store | `src/repositories/` |
| Data statis aplikasi | `src/data/` |
| Skema database persisten | `database/schema.sql` |
| Tambah environment variable baru | `server.env.example` |

## Kontrak dengan Frontend

- Frontend mengakses service ini melalui `VITE_API_URL`
- Backend mengizinkan origin frontend melalui `CORS_ORIGIN`
- Token Supabase dikirim dari frontend sebagai header `Authorization: Bearer <token>`
- Perubahan UI frontend tidak dilakukan di repo ini

## Aturan Penempatan File

- File konfigurasi Railway tetap di root repo
- Secret disimpan di `server.env` atau environment variable provider — jangan commit kredensial asli
- Folder `.venv`, `__pycache__`, upload lokal, dan log tidak dimasukkan ke git
