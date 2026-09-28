# Audit Agent — Frontend

Chat-style UI for the invoice auditing backend. Plain React + Vite, no Tailwind/TanStack.

## Setup

```bash
npm install
cp .env.example .env   # edit VITE_API_BASE_URL if your backend isn't on localhost:8000
npm run dev
```

Opens at http://localhost:5173

## Required: enable CORS on the backend

Since the frontend (port 5173) and backend (port 8000) run on different origins,
add this to your FastAPI `main.py` if it isn't there already:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Without this, every fetch call from the UI will fail with a CORS error in the browser console.

## How it maps to the backend

| UI action | Endpoint |
|---|---|
| Sidebar loads on start | `GET /invoices/all` |
| Click an invoice in the sidebar | `GET /invoices/{invoice_id}` |
| "New Invoice" + attach a file | `POST /invoices/upload` |
| Attach a file inside an open thread | `POST /invoices/{invoice_id}/re-audit` |
| "View file" on any bubble | `GET /invoices/version/{version_id}/file` (via `file_url` returned in the version) |

## Behavior notes

- **REJECTED** results (invoice-number mismatch on re-audit) are never persisted by the
  backend, so they're shown as a one-off bubble in the current session only — they
  disappear if you reload or switch threads, matching the backend's "nothing kept" design.
- **409 duplicate-hash** responses show as a banner above the upload bar, not as a bubble,
  since the backend rejects them before the graph even runs.
- **FAILED** results (invoice number couldn't be extracted) DO show up permanently, since
  the backend still creates a version + explanation for them.
