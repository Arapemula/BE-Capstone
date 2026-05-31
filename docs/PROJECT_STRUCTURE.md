# Backend Project Structure

`BE-Capstone` is the authoritative Flask API workspace. Frontend work belongs in `../Capstone`.

```txt
BE-Capstone/
|-- src/
|   |-- app.py              # Flask app and API routes
|   |-- db.py               # Database connection and helpers
|   |-- repositories/       # Persistence layer and in-memory fallback
|   |-- services/           # Business logic and AI service integration
|   `-- data/               # Quiz bank and skill taxonomies
|-- database/
|   `-- schema.sql          # PostgreSQL schema
|-- docs/                   # Backend documentation
|-- Procfile                # Railway start command
|-- railway.json            # Railway configuration
|-- runtime.txt             # Python runtime version
|-- requirements.txt        # Python dependencies
|-- server.env.example      # Environment variable template
`-- README.md
```

## Where To Work

- Add or update API endpoints in `src/app.py`.
- Put reusable business logic in `src/services`.
- Put database/store access in `src/repositories`.
- Update local static app data in `src/data`.
- Update persistent schema in `database/schema.sql`.
- Add environment variables to `server.env.example` when they are required by the app.

## Separate Frontend Contract

- The frontend reaches this service through `VITE_API_URL`.
- This backend allows the frontend origin through `CORS_ORIGIN`.
- Supabase auth tokens are sent from the frontend as `Authorization: Bearer <token>`.
- Do not make frontend UI changes in this repository.

## Placement Rules

- Keep Railway files at the repository root.
- Keep secrets in `server.env` or provider-managed environment variables; do not commit real credentials.
- Keep generated folders such as `.venv`, `__pycache__`, uploads, and logs out of git.
