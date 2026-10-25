# BrandProof

BrandProof checks marketing content against approved brand rules, flags restricted terms and unsupported claims, saves revisions, and records reviewer decisions.

## Project layout

- `frontend/` — React 18, TypeScript, Vite, Tailwind CSS
- `backend/` — Django REST Framework API and PostgreSQL-ready persistence (SQLite by default for local development)
- `render.yaml` — Render Blueprint for the API, PostgreSQL database, and persistent upload disk
- `IMPLEMENTATION_PLAN.md` — initial implementation plan

## Requirements

- Python 3.13 (the backend runtime is specified in `backend/.python-version`; Python 3.11+ is required by Django)
- Node.js 20 or newer and npm
- Git

## Run from a clean checkout (Windows PowerShell)

Open two terminals at the repository root.

### Terminal 1: backend

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Django creates `backend/db.sqlite3` for a local run. The default settings allow the Vite origins `http://localhost:5173` and `http://127.0.0.1:5173`. Uploaded files go under `backend/media/`.

### Terminal 2: frontend

```powershell
cd frontend
npm ci
Copy-Item .env.example .env
npm run dev -- --host 127.0.0.1 --strictPort
```

Open <http://127.0.0.1:5173>. The committed frontend example sets `VITE_API_URL=http://127.0.0.1:8000/api`. Vite reads `frontend/.env`; restart Vite after changing it.

### Backend environment configuration

`backend/.env.example` documents the settings, but this project does not load backend `.env` files automatically. Set backend values in the shell or hosting provider environment. Defaults are suitable for local use. In PowerShell, for example:

```powershell
$env:DJANGO_DEBUG = "true"
$env:CORS_ALLOWED_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
# Optional PostgreSQL instead of local SQLite:
$env:DATABASE_URL = "postgresql://USER:PASSWORD@HOST:5432/brandproof"
```

Restart Django after changing environment variables. Backend variables:

| Variable | Purpose | Local default / production guidance |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Django signing key | Generated locally if unset; use a unique long secret in production. Never commit it. |
| `DJANGO_DEBUG` | Debug mode | `true` locally; set `false` in production. |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated request hostnames | `localhost,127.0.0.1`; include the deployed API hostname in production. Render’s external hostname is added automatically. |
| `DATABASE_URL` | Database connection | Local SQLite by default; set to the PostgreSQL connection URL in production. |
| `CORS_ALLOWED_ORIGINS` | Comma-separated browser origins | Local Vite origins by default; set the exact Vercel origin, including `https://`, in production. |
| `DJANGO_SECURE_SSL_REDIRECT` | Redirect HTTP to HTTPS | `false` locally; `true` in the Render Blueprint. |
| `MEDIA_ROOT` | Uploaded file directory | `backend/media/` locally; Render Blueprint mounts it at `/var/data/media`. |

Frontend variables are injected at Vite build time. `VITE_API_URL` must be the API origin plus `/api`, for example `https://brandproof-api.onrender.com/api`. Only public, non-secret values belong in `VITE_*` variables because they are bundled into browser code.

## Verify locally

Run from the repository root after installing dependencies:

```powershell
cd backend
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py migrate --check
.\.venv\Scripts\python.exe manage.py test reviews
cd ..\frontend
npm run build
```

The workflow tests cover brand rule configuration, risk findings, revisions, approval decisions, invalid input, and supported attachment storage. For manual API checks, open `http://127.0.0.1:8000/api/brand/` and `http://127.0.0.1:8000/api/reviews/` while the backend runs.

## Git and private-file checks

The root `.gitignore` excludes environment files (while allowing the example templates), SQLite databases, uploaded media, generated static files, Python virtual environments, `node_modules`, and frontend build output. From the repository root, check the exclusions before staging or pushing:

```powershell
git check-ignore -v backend/.env backend/db.sqlite3 backend/media/private-upload.txt frontend/node_modules/example frontend/dist/index.html
git status --short
```

Confirm the first command reports each private/generated path as ignored. The two `.env.example` templates should remain trackable. Inspect staged files before committing; never add credentials, real customer content, or uploaded private files.

## Publish the source to GitHub

1. Create an empty repository on GitHub while signed in.
2. From this project directory, inspect `git status --short` and the staged file list. Keep only source, migrations, dependency lockfiles, deployment configuration, and documentation.
3. Commit and push the existing project. If no remote is configured, use the URL GitHub gives you:

```powershell
git add .
git status --short
git diff --cached --name-only
git commit -m "Prepare BrandProof for deployment"
git branch -M main
git remote add origin https://github.com/YOUR-ACCOUNT/BrandProof.git
git push -u origin main
```

If an `origin` already exists, inspect it with `git remote -v` and update it only if needed; do not add a duplicate remote.

## Deploy the API and database to Render

1. Sign in to Render and create a Blueprint from the GitHub repository. Review `render.yaml` before approving provisioning.
2. The Blueprint defines a Django web service, PostgreSQL database, pre-deploy migrations, generated `DJANGO_SECRET_KEY`, and persistent upload disk. Its compute, database, and disk resources may incur charges; verify the current plan/pricing in your Render account before creating them.
3. When prompted for `CORS_ALLOWED_ORIGINS`, enter the exact Vercel production origin (scheme and hostname only, no trailing slash or `/api`). Set `DJANGO_ALLOWED_HOSTS` too if you use a custom API domain; Render’s generated hostname is automatically allowed.
4. Wait for deployment and migration success. Record the API URL and verify `/api/brand/` and `/api/reviews/` return HTTP 200.

Render runs `preDeployCommand` before starting the service, as configured in the Blueprint. See the [Render Blueprint reference](https://render.com/docs/blueprint-spec) and [persistent disk guide](https://render.com/docs/disks) for the resource settings and behavior.

## Deploy the frontend to Vercel

1. Sign in to Vercel and import the GitHub repository.
2. Set the project **Root Directory** to `frontend`. The Vite build command is `npm run build`, and the output directory is `dist`. `frontend/vercel.json` provides the SPA fallback.
3. Add `VITE_API_URL` in the Vercel project’s production environment variables, using the deployed Render API URL with `/api` appended, for example `https://brandproof-api.onrender.com/api`.
4. Deploy. Confirm the frontend can load the dashboard, save a rule, submit and revise content, and record a reviewer decision against the deployed API. If Vercel assigns a different domain, update Render’s `CORS_ALLOWED_ORIGINS` to that exact origin and redeploy the backend.

See [Vercel’s monorepo setup](https://vercel.com/docs/monorepos), [Vite deployment guide](https://vercel.com/docs/frameworks/frontend/vite), and [environment variable guide](https://vercel.com/docs/environment-variables).

## Current limitations and deployment safety

- This hackathon MVP has no user authentication or per-user access controls. The API currently permits unauthenticated access, so anyone who can reach a public deployment can read or modify its brand profile, reviews, and decisions. Use synthetic demo content only; do not store private or customer data until access controls are implemented.
- Uploads are validated and stored, but text is not extracted from images, PDFs, or DOCX files and OCR is not performed. Paste the text to be checked.
- Risk checks use deterministic rules and approved-fact matching. Results are assistive findings, not legal or compliance certification.
- The repository contains deployment configuration, not a live deployment. Public URLs exist only after you connect the repository and approve resource provisioning in your GitHub, Render, and Vercel accounts.
