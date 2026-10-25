# BrandProof implementation plan

## Project inspection

- The project directory is empty: there is no existing frontend, backend, database configuration, test suite, or repository-specific guidance.
- Build a clear two-part project: `backend/` for Django REST Framework and `frontend/` for React, TypeScript, Vite, and Tailwind CSS.

## Architecture and delivery sequence

1. **Runnable foundation** — add Django project settings, environment-based PostgreSQL configuration with SQLite fallback, Vite setup, Tailwind setup, and local run instructions.
2. **Persistent brand profile** — model approved facts, restricted words, required phrases, and brand colours; expose validated REST endpoints and seed a usable default profile.
3. **Review workflow** — accept pasted copy plus supported attachments, persist review and uploaded files, evaluate restricted terms, required phrases, and unverified promotional claims against approved facts.
4. **Actionable findings** — return each finding with category, severity, explanation, matched evidence, and a suggested correction.
5. **Revision and approval** — keep immutable snapshots when content changes and support approve, reject, or request-changes decisions with reviewer notes.
6. **Dashboard UX** — provide navigation, overview metrics, guideline editing, content intake, risk radar, findings, revision history, and reviewer controls.
7. **Verification** — add backend tests for input validation, risk checks, revisions, and decisions; run available checks after dependencies are installed.

## Initial implementation scope

Implement steps 1–6 in the first code pass, including a functional end-to-end path from editing guidelines to reviewing content and recording a workflow decision. Support `.txt`, `.md`, `.pdf`, `.docx`, `.png`, `.jpg`, `.jpeg`, and `.webp` upload types. Image OCR and full PDF/DOCX text extraction are follow-on capabilities; the first pass stores supported files and uses pasted text as the analyzable content.

## Commands requiring approval

- Installing Python and Node dependencies requires network access and may modify the local environment. Ask for approval before running package installation commands.
- Starting local development servers is optional and can be done after dependencies are installed.
