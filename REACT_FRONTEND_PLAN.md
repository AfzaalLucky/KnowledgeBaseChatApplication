# Knowledge Base Chat — React + TypeScript Frontend Implementation Plan

Status: planning document. Written against the codebase as of commit `234e1e0`.

---

## Part A — Current State Analysis

### A.1 What exists today

| File | Role | Notes |
|---|---|---|
| `app/main.py` | FastAPI app | 3 routes: `GET /`, `POST /chat`, `POST /ingest`. No CORS, no static file serving, no `/api` prefix. |
| `app/config.py` | Hardcoded settings | `QDRANT_URL`, `COLLECTION_NAME`, model names, SQL connection string — all literals, no `.env`. |
| `app/db.py` | SQL Server access | `get_conn()` opens a new `pyodbc` connection per call. `init_db()` creates `Documents(id, filename, uploaded_at)` and `Chunks(id, doc_id, content, qdrant_id)`. No read/update/delete queries exist anywhere — nothing lists or updates a document today. |
| `app/qdrant_client.py` | Vector DB client | Single collection `kb_chat`, vector size hardcoded to `768` (matches `nomic-embed-text`). |
| `app/ingest.py` | Ingestion pipeline | **PDF only** — uses `PyPDFLoader` directly, ignores `app/utils.py` entirely. Takes a `file_path` already sitting on disk; does not receive uploaded bytes. Loops synchronously calling `embed()` per chunk (one Ollama call per chunk, no batching/async). |
| `app/retriever.py` | Semantic search | Returns a bare `list[str]` of chunk text — no score, no document/page attribution surfaced to the API response beyond what `/chat` re-wraps. |
| `app/ollama_client.py` | LLM calls | `embed()` and `chat()` are both synchronous, non-streaming (`ollama.chat(..., stream=False)` implicitly). |
| `app/utils.py` | PDF/DOCX/TXT text loader | **Dead code.** Nothing imports `load_file`. This is the file you have selected — it's a complete, unused alternate ingestion path. |
| `app/generate_handbook.py` | Dev fixture generator | Produces a sample PDF for manual testing. Not part of the runtime app. |
| `docker-compose.yml` | Qdrant only | The `app` service is defined but there's no `Dockerfile` referenced build context beyond the default; SQL Server and Ollama are assumed to run on the host, not composed. |

### A.2 Gaps against the required features

| Required feature | Current state |
|---|---|
| Document upload (multipart) | Does not exist. `/ingest` takes a path string the *server* reads — the client never sends file bytes. |
| Multi-format support (PDF/DOCX/TXT) | `utils.py` has the logic; `ingest.py` doesn't use it. Only PDF works end-to-end today. |
| Document listing / status / chunk count | No endpoint, no query, no `status` or `chunk_count` column in `Documents`. |
| Streaming chat | `ollama_client.chat()` is a single blocking call returning a full string; no `StreamingResponse` anywhere. |
| CORS for a separate frontend origin | Not configured — any browser-based frontend on a different port will be blocked today. |
| Input validation on ingestion | None. `file_path` is passed straight to `PyPDFLoader` with no extension/size/existence checks, and it's attacker-controlled. |

### A.3 Security note worth fixing regardless of the frontend work

`POST /ingest` currently accepts `{"file_path": "<any string>"}` and reads that path off the server's local filesystem with no allow-listing (`app/main.py:45-47`, `app/ingest.py:21`). Any client that can reach the API can ask it to ingest arbitrary server-local files (e.g. `C:\Windows\System32\drivers\etc\hosts` read as garbled text, or worse, any file readable by the process). This plan replaces that endpoint with a real multipart upload where the server — not the client — decides the storage path, which closes this off as a side effect. Flagging it now because it's a real bug independent of the frontend work.

---

## Part B — Frontend Technology & Architecture Decisions

| Concern | Choice | Why |
|---|---|---|
| Build tool | **Vite** | Fast dev server, native TS/ESM, trivial proxy config to FastAPI during dev. |
| Framework | **React 18 + TypeScript** (strict mode) | As required. |
| Routing | **react-router-dom v6** | Two real pages (Documents, Chat) plus room to grow; no need for a meta-framework (Next.js) since this ships behind FastAPI, not as its own server. |
| Server-state / data fetching | **TanStack Query (React Query)** | Gives caching, polling (`refetchInterval` for processing-status), retries, and loading/error states for free — avoids hand-rolled `useEffect` fetch logic. |
| Client/UI state | **React Context + `useState`**, escalate to **Zustand** only if chat state gets shared across routes | Keep it minimal; there's no complex global state here (no auth, no multi-user session). |
| Styling | **Tailwind CSS + shadcn/ui (Radix primitives)** | Fast to build a clean, consistent design system; accessible primitives (dialog, toast, dropdown) out of the box; fully themeable via CSS variables for light/dark. |
| Icons | **lucide-react** | Matches shadcn/ui conventions. |
| Forms/validation | **react-hook-form + zod** | Upload form (file type/size) and chat input validation. |
| HTTP client | **native `fetch`** wrapped in a small typed client | Avoids an axios dependency; `fetch` handles streaming (`ReadableStream`) natively, which matters for the chat stream. |
| Testing | **Vitest + React Testing Library** (unit/component), **Playwright** (E2E: upload → list → chat) | Matches Vite tooling, no extra config layer. |
| Package manager | **pnpm** (or npm if the user prefers — flag as a choice, not fixed) | Not load-bearing; npm works identically for this plan. |

### Backend-side decisions this implies

- All new/changed routes live under an `/api` prefix (`/api/documents`, `/api/chat`) so the SPA can be served from `/` in production without route collisions.
- `CORSMiddleware` added for the Vite dev origin (`http://localhost:5173`) and the production origin.
- Settings move from hardcoded literals in `config.py` to `pydantic-settings` reading a `.env` file, so `ALLOWED_ORIGINS`, `MAX_UPLOAD_SIZE_MB`, `UPLOAD_DIR` etc. are configurable without code changes.
- Ingestion becomes an explicit multi-step pipeline (save → parse → chunk → embed → persist) with a `status` column, run via `BackgroundTasks` so the upload request returns immediately (202) instead of blocking on embedding calls.

---

## Part C — Step-by-Step Plan

### Step 1 — Existing project analysis
Covered above in Part A. No code changes in this step. **Test:** N/A — this is the baseline the rest of the plan is checked against.

### Step 2 — Frontend technology & architecture decisions
Covered in Part B. Deliverable: this document, reviewed/approved before scaffolding.

### Step 3 — React/TypeScript project setup

- **New files:** `frontend/` directory, created via `npm create vite@latest frontend -- --template react-ts`, then: `vite.config.ts`, `tsconfig.json`, `tailwind.config.ts`, `postcss.config.js`, `.eslintrc.cjs`, `.prettierrc`, `.env.development`, `.env.production`.
- **Dependencies:** `react`, `react-dom`, `react-router-dom`, `@tanstack/react-query`, `tailwindcss`, `class-variance-authority`, `clsx`, `tailwind-merge`, `lucide-react`, `react-hook-form`, `zod`, `@hookform/resolvers`. Dev deps: `typescript`, `vite`, `@vitejs/plugin-react`, `eslint`, `prettier`, `vitest`, `@testing-library/react`, `@testing-library/jest-dom`.
- **`vite.config.ts`:** dev server proxy — `/api` → `http://localhost:8000` — so the frontend calls relative `/api/...` paths in both dev and prod.
- **Backend changes:** none yet.
- **Edge cases:** Node version pinning (`.nvmrc`) to avoid Vite version mismatches; ensure `frontend/` is added to the repo's `.gitignore` for `node_modules`/`dist`.
- **Test:** `npm run dev` serves the Vite starter page at `localhost:5173`; `npm run build` produces `frontend/dist` without errors.

### Step 4 — UI/UX and design-system implementation

- **New files:** `src/styles/globals.css` (Tailwind directives + CSS variable theme tokens for light/dark), `src/components/ui/*` (Button, Input, Card, Badge, Dialog, Toast, Spinner, Table, Skeleton — via `shadcn/ui` CLI, which generates these as owned source files, not a dependency), `src/lib/utils.ts` (the `cn()` class-merge helper shadcn/ui expects).
- **Design tokens:** consistent spacing scale (Tailwind defaults), a small type scale (headings + body + mono for code/errors), a neutral base palette with one accent color, `prefers-color-scheme` dark mode support via a `dark:` class strategy.
- **Dependencies:** `tailwindcss`, `tailwindcss-animate`, `@radix-ui/*` primitives (pulled in per-component by the shadcn/ui CLI as needed — e.g. `@radix-ui/react-dialog`, `@radix-ui/react-toast`).
- **Edge cases:** shadcn/ui components are copied into the repo (not npm-installed as a monolith), so keep them in `src/components/ui/` and treat them as project code — safe to modify.
- **Test:** Storybook is overkill here; instead build a throwaway `/design-preview` route during development that renders every primitive, delete it before shipping.

### Step 5 — FastAPI API analysis and required changes

- **Modify:** `app/main.py` — add `CORSMiddleware`, mount routers under `/api`, remove the raw `file_path`-based `/ingest`.
- **New files:**
  - `app/settings.py` — `pydantic-settings` `BaseSettings` class replacing `app/config.py` literals (`ALLOWED_ORIGINS`, `UPLOAD_DIR`, `MAX_UPLOAD_MB`, `SQL_CONNECTION`, `QDRANT_URL`, etc., sourced from `.env`).
  - `app/routers/documents.py` — upload, list, get, delete, status.
  - `app/routers/chat.py` — `/api/chat` (non-streaming, kept for simplicity/compat) and `/api/chat/stream` (SSE-style streaming).
  - `app/schemas.py` — Pydantic request/response models (see Step 6/11/13 for shapes).
- **Dependencies:** `pydantic-settings`, `python-multipart` (required by FastAPI for `UploadFile` form parsing — currently absent from `requirements.txt`).
- **Backend endpoint surface after this step:**

  | Method | Path | Purpose |
  |---|---|---|
  | `POST` | `/api/documents` | Upload a file (multipart), returns `202` with `status=pending` |
  | `GET` | `/api/documents` | List documents (supports `?search=`) |
  | `GET` | `/api/documents/{id}` | Single document detail incl. status/chunk count |
  | `DELETE` | `/api/documents/{id}` | Remove document (SQL rows + Qdrant points + file) |
  | `POST` | `/api/chat` | Ask a question, full response |
  | `POST` | `/api/chat/stream` | Ask a question, token-by-token stream |
  | `GET` | `/api/health` | Liveness for the frontend to show a connectivity banner |

- **Test:** hit each route with `httpx`/`curl` against `/docs` (Swagger still auto-generates) before wiring any frontend code.

### Step 6 — Document upload implementation

- **Modify:** `app/ingest.py` — change `ingest_file(file_path)` to `ingest_document(doc_id: int, stored_path: str, ext: str)`, called from a background task, not directly from the request handler.
- **New:** in `app/routers/documents.py`, `POST /api/documents`:
  1. Validate `UploadFile.content_type`/extension against an allow-list (`.pdf`, `.docx`, `.txt`).
  2. Validate size by streaming to disk with a cap (reject over `MAX_UPLOAD_MB`, e.g. 25MB) rather than trusting `Content-Length`.
  3. Generate a safe stored filename: `f"{uuid4()}_{sanitize(original_filename)}"` written under `data/documents/` — never trust the client-provided filename for the actual path (mirrors the fix for the Step-1 vulnerability).
  4. Insert a `Documents` row with `status='pending'` immediately, return its id.
  5. Schedule `BackgroundTasks.add_task(ingest_document, doc_id, stored_path, ext)`.
- **Request/response shape:**
  ```
  POST /api/documents  (multipart/form-data, field "file")
  → 202 { "id": 17, "filename": "handbook.pdf", "status": "pending" }
  ```
- **Frontend:** `src/api/documents.ts::uploadDocument(file, onProgress?)` using `fetch` with a `FormData` body; `XMLHttpRequest` only if upload-progress percentage is required (native `fetch` doesn't expose upload progress — use `XHR` or `fetch` with a `ReadableStream` wrapper if progress bars matter; otherwise plain `fetch` is enough).
- **Edge cases:** duplicate filenames (stored name is UUID-prefixed, so no collision); zero-byte files; corrupted PDFs that fail `PyPDFLoader` (must be caught in the background task and recorded as `status='failed'` with an error message, not crash silently); concurrent uploads of the same logical document.
- **Test:** upload each supported type via `curl -F "file=@sample.pdf"`; upload an oversized file and confirm `413`; upload a `.exe` and confirm `415`.

### Step 7 — Document storage and validation

- **New:** `app/storage.py` — `save_upload(upload: UploadFile) -> tuple[str, int]` (stored path, byte size), enforcing the allow-list and size cap, ensuring `data/documents/` exists (`os.makedirs(..., exist_ok=True)`, mirroring what `generate_handbook.py` already does ad hoc).
- **Validation rules:** extension allow-list is the primary gate (`.pdf`, `.docx`, `.txt`); content-sniffing (e.g. checking PDF magic bytes `%PDF-`) is a good defense-in-depth addition since extensions are trivially spoofable — worth adding given `/ingest`'s current path-trust bug.
- **Backend:** `Documents` table gains columns — see Step 5's schema note, formalized here:
  ```sql
  ALTER TABLE Documents ADD file_type NVARCHAR(20) NULL;
  ALTER TABLE Documents ADD file_size_bytes BIGINT NULL;
  ALTER TABLE Documents ADD status NVARCHAR(20) NOT NULL DEFAULT 'pending';
  ALTER TABLE Documents ADD chunk_count INT NULL;
  ALTER TABLE Documents ADD error_message NVARCHAR(MAX) NULL;
  ALTER TABLE Documents ADD updated_at DATETIME NULL;
  ```
  Apply via a small migration step inside `init_db()` (guarded `IF NOT EXISTS (SELECT * FROM sys.columns ...)` checks, consistent with the existing `IF NOT EXISTS` table-creation style) rather than introducing a migration framework for a 2-table schema.
- **Edge cases:** disk full during save; path traversal in original filename (`../../evil`) — always derive the stored name, never join the client's filename directly into a path.
- **Test:** unit test `save_upload` with a mocked `UploadFile`; assert traversal attempts (`../../x.pdf`) never escape `data/documents/`.

### Step 8 — Document parsing and chunking

- **Modify:** `app/ingest.py` to dispatch by extension using LangChain loaders uniformly, retiring `app/utils.py`'s manual text extraction (which loses page/paragraph metadata that `PyPDFLoader` currently preserves):
  - `.pdf` → `PyPDFLoader` (existing)
  - `.docx` → `Docx2txtLoader` (new, from `langchain_community.document_loaders`)
  - `.txt` → `TextLoader` (new, from `langchain_community.document_loaders`)
- **Delete:** `app/utils.py` once its logic is fully superseded — it's currently unreachable code; either delete it or repurpose it, don't leave both paths.
- **Chunking:** keep the existing `RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100, ...)` — reuse as-is, it's format-agnostic once documents are normalized to LangChain `Document` objects.
- **Backend:** `ingest_document()` updates `Documents.status` at each phase (`processing` → `completed`/`failed`) and writes `chunk_count` + `error_message` on completion.
- **Dependencies:** `docx2txt` (required by `Docx2txtLoader`); `python-docx` can be dropped once `utils.py` is removed (it's currently only used there).
- **Edge cases:** empty `.txt` files (zero chunks — mark `completed` with `chunk_count=0`, not `failed`); DOCX with only images/tables and no extractable text; extremely large documents producing thousands of chunks (consider a per-document chunk cap or a warning surfaced in the UI, not a hard requirement).
- **Test:** ingest one sample of each format (reuse `generate_handbook.py`'s PDF; add a small `.docx`/`.txt` fixture) and assert `chunk_count > 0` and `status == 'completed'`.

### Step 9 — Embedding and Qdrant integration

- **No structural change needed** — `app/qdrant_client.py` and the `embed()`/upsert loop in `ingest.py` already work; reuse as-is, just called from the new `ingest_document()`.
- **Minor improvement:** batch embedding calls where the Ollama client supports it, or at minimum keep the current per-chunk loop but make `ingest_document` an `async def` run via `BackgroundTasks` so it doesn't tie up a worker thread for the whole request lifecycle (it already won't block the response since it's backgrounded post-202).
- **Backend:** payload stored per point already includes `text`, `page`, `document` — add `doc_id` (the SQL `Documents.id`) to the Qdrant payload so deletes (Step 6) can filter Qdrant points by `doc_id` without a SQL join through `Chunks.qdrant_id` for every point individually (or keep the current `Chunks.qdrant_id` join approach — either works; storing `doc_id` in the payload makes `DELETE /api/documents/{id}` a single `qdrant.delete(filter=doc_id==X)` call instead of N point-id deletes).
- **Test:** after ingestion, query Qdrant directly (`client.scroll(collection_name=..., scroll_filter=Filter(must=[FieldCondition(key="document", match=MatchValue(value=doc_name))]))`) and confirm point count matches `chunk_count`.

### Step 10 — MS SQL metadata integration

- **New:** `app/repositories/documents.py` (or extend `app/db.py`) with the actual CRUD queries that don't exist today: `list_documents(search: str | None)`, `get_document(id)`, `update_document_status(id, status, chunk_count=None, error=None)`, `delete_document(id)`.
- **Backend:** these back the `GET`/`DELETE` routes from Step 5.
- **Edge cases:** `pyodbc` connection-per-call pattern (current `get_conn()`) is fine at this scale but doesn't pool — acceptable for a single-user local app; flag as a future improvement (connection pooling / `sqlalchemy`) rather than solving it now, since it's out of scope for the frontend integration.
- **Test:** integration test hitting a real local SQL Server test database (or a `KnowledgeBase_test` DB) exercising insert → list → status update → delete.

### Step 11 — Document management / listing page

- **New files:** `src/pages/DocumentsPage.tsx`, `src/components/documents/DocumentList.tsx`, `DocumentCard.tsx` (or `DocumentTable.tsx` for a denser view), `DocumentUploadDialog.tsx`, `DocumentStatusBadge.tsx`, `DocumentSearchBar.tsx`, `src/hooks/useDocuments.ts`, `useUploadDocument.ts`, `src/types/document.ts`.
- **`useDocuments`:** `useQuery(['documents', search], () => api.listDocuments(search))`; add `refetchInterval: (data) => data?.some(d => ['pending','processing'].includes(d.status)) ? 2000 : false` so rows with in-flight processing auto-refresh without a manual poll loop.
- **`useUploadDocument`:** `useMutation` calling `POST /api/documents`, on success `queryClient.invalidateQueries(['documents'])`.
- **Columns/fields shown:** filename, type badge, formatted size (`formatBytes` util), upload date (`formatDate`), status badge (pending/processing/completed/failed with color coding), chunk count (or "—" while pending), row action to delete.
- **Responsive behavior:** table layout on desktop, stacked cards on mobile (Tailwind `hidden md:table` / `md:hidden` pattern, or a single component that switches layout via CSS grid).
- **States:** skeleton rows while loading, empty state ("No documents yet — upload one to get started" with the upload CTA inline), inline error banner with retry if the list fetch fails, toast notifications on upload success/failure.
- **Backend:** none beyond Step 5/10.
- **Test:** RTL test mounting `DocumentsPage` with a mocked query client — assert skeleton → list render, assert search filters client-visible rows (if filtering client-side) or triggers a refetch (if server-side via `?search=`); Playwright E2E: upload a real file, see it appear as `pending`, poll until `completed`.

### Step 12 — Chat widget implementation

- **New files:** `src/components/chat/ChatWidget.tsx` (self-contained, embeddable — takes no required props, manages its own message state), `ChatMessageList.tsx`, `ChatMessage.tsx` (renders role-based bubble + optional sources list), `ChatInput.tsx`, `TypingIndicator.tsx`, `src/pages/ChatPage.tsx` (thin wrapper placing `ChatWidget` full-page), `src/types/chat.ts`.
- **Design:** `ChatWidget` is built as a standalone component specifically so it can later be dropped onto the `DocumentsPage` or anywhere else (matches the "reusable chat widget" requirement) — no page-level routing logic lives inside it.
- **State shape:** local `useState<ChatMessage[]>` inside the widget (or a small `useChat` hook) — `{ id, role: 'user'|'assistant', content, sources?, status: 'sending'|'streaming'|'done'|'error' }[]`.
- **Test:** RTL test — type a question, submit, assert a user bubble appears immediately and an assistant bubble appears after the mocked API resolves.

### Step 13 — Chat API integration

- **New:** `src/api/chat.ts::sendMessage(question)` (non-streaming, calls `POST /api/chat`) and `streamMessage(question, onToken)` (calls `POST /api/chat/stream`, reads `response.body.getReader()`, decodes chunks, and invokes `onToken` per fragment).
- **Backend — streaming endpoint (`app/routers/chat.py`):**
  ```python
  @router.post("/chat/stream")
  async def chat_stream(req: ChatRequest):
      docs = search(req.question)
      context = "\n\n".join(d.text for d in docs)
      def generate():
          for part in ollama.chat(model=CHAT_MODEL, messages=[...], stream=True):
              yield part["message"]["content"]
      return StreamingResponse(generate(), media_type="text/plain")
  ```
  Note: use plain chunked `text/plain` streaming rather than strict SSE (`text/event-stream`) — the browser's `EventSource` API cannot send a POST body, and this endpoint needs to send the question in the body, so a manually-parsed `fetch` stream is simpler than reimplementing SSE framing over POST.
- **Response shape (non-streaming `/api/chat`):**
  ```json
  { "answer": "...", "sources": [{ "document": "handbook.pdf", "page": 3, "text": "..." }] }
  ```
  (Upgrade from the current bare `sources: string[]` so the UI can show attribution, which requires `retriever.search()` to return structured hits instead of `list[str]` — modify `app/retriever.py` accordingly.)
- **Edge cases:** empty knowledge base (no Qdrant points yet) → return a clear "no documents indexed" answer rather than an empty context silently sent to the model; Ollama unreachable → surface a distinct error state, not a generic 500; very long questions — client-side length cap with a visible counter.
- **Test:** mock `fetch` in RTL for the non-streaming path; for streaming, test the `ReadableStream` parsing logic in isolation with a fake stream; E2E test against the real backend with Ollama running.

### Step 14 — Loading, error, and processing states

- **Pattern:** every data-fetching hook returns TanStack Query's `{ data, isLoading, isError, error }` and every component consuming it renders three branches: skeleton/spinner, error banner (with retry button calling `refetch()`), and content. No bespoke loading booleans scattered through components.
- **New:** `src/components/ui/ErrorBanner.tsx`, `src/components/ui/Skeleton.tsx` (or shadcn's), a shared `src/lib/errors.ts` mapping backend error shapes (FastAPI's default `{"detail": "..."}` for `HTTPException`) to user-facing messages.
- **Backend:** ensure all routers raise `HTTPException` with meaningful `detail` strings and correct status codes (400 validation, 404 not found, 413 too large, 415 unsupported type, 500 unexpected) so the frontend's error mapping has something consistent to key off.
- **Test:** force each error path (kill the backend mid-request, upload an invalid file, ask a question with an empty KB) and confirm the UI shows the right state, not a blank screen or unhandled promise rejection.

### Step 15 — Responsive design

- **Approach:** mobile-first Tailwind classes throughout; a persistent left nav collapses to a bottom tab bar or hamburger drawer under `md:`; the documents table collapses to cards under `md:`; chat widget takes full viewport height with a sticky input on mobile (`100dvh` to handle mobile browser chrome correctly, not plain `100vh`).
- **New:** `src/components/layout/AppShell.tsx`, `Sidebar.tsx`/`MobileNav.tsx`.
- **Test:** Playwright with viewport presets (375×667 mobile, 768×1024 tablet, 1440×900 desktop) asserting nav and document list layout at each breakpoint; manual check in Chrome DevTools device toolbar.

### Step 16 — Security and input validation

- **Backend:**
  - CORS locked to explicit origins from `.env`, not `"*"`.
  - File upload validated by extension allow-list + magic-byte sniffing + size cap (Steps 6–7).
  - The path-traversal-via-client-supplied-path bug (`/ingest`) is eliminated by removing that endpoint in favor of the upload flow.
  - Parameterized queries are already used throughout `db.py`/new repositories (`?` placeholders) — keep this convention, never string-format SQL.
  - Question length cap on `/api/chat` to bound context-window/cost exposure.
  - Consider a basic API key header (`X-API-Key`) checked via a FastAPI dependency if this will ever be reachable outside localhost — flagged as optional since the current app has zero auth and adding a full auth system is beyond what was asked for; worth an explicit decision with the user before deployment.
- **Frontend:** never render assistant/document content as raw HTML (`dangerouslySetInnerHTML`) — render as plain text/markdown-sanitized (if markdown rendering is added later, use a sanitizing renderer like `react-markdown` with no raw-HTML plugin enabled); client-side file validation mirrors server rules (fail fast, but server remains the source of truth).
- **Test:** attempt path traversal in a filename, attempt an oversized upload, attempt a non-allow-listed extension with a spoofed `Content-Type`, confirm all are rejected server-side even if a modified client would try to bypass client-side checks.

### Step 17 — Testing strategy

| Layer | Tool | Scope |
|---|---|---|
| Backend unit | `pytest` | `storage.py` validation, chunking, repository queries (mocked/local test DB) |
| Backend integration | `pytest` + `httpx.AsyncClient` | Full upload → status → chat round trip against real Qdrant + SQL Server test instances |
| Frontend unit/component | Vitest + RTL | Hooks (`useDocuments`, `useChat`), components in isolation with mocked API |
| Frontend E2E | Playwright | Upload a document, watch it reach `completed`, ask a question referencing it, confirm the answer/sources render |

- **New:** `app/tests/` (currently no test directory exists at all — this repo has zero automated tests today, worth calling out explicitly), `frontend/src/**/*.test.tsx`, `frontend/e2e/*.spec.ts`.
- **Dependencies:** `pytest`, `pytest-asyncio`, `httpx` (backend); `vitest`, `@testing-library/react`, `@playwright/test` (frontend).

### Step 18 — Integration testing

- **Scenario coverage:** cold start (empty DB/Qdrant) → upload each supported format → verify listing shows correct metadata → verify chat answers reference the right document → delete a document → verify it's gone from both SQL and Qdrant and no longer retrievable.
- **Environment:** a `docker-compose.override.yml` or dedicated test compose file spinning up Qdrant + a disposable SQL Server container (`mcr.microsoft.com/mssql/server`) so integration tests don't require a developer's local SQL Server install.
- **Test:** run this as a CI job (see Step 20) on every PR touching `app/` or `frontend/src/api`.

### Step 19 — Performance considerations

- **Backend:** background-task ingestion (Step 6) keeps upload requests fast regardless of document size; consider capping concurrent background ingestions if multiple large files are uploaded at once (a simple in-process semaphore is enough at this scale — no need for a task queue like Celery unless usage grows).
- **Frontend:** TanStack Query's caching avoids redundant re-fetches; virtualize the document list only if it's expected to grow into the hundreds+ (not needed at current scale — don't add `react-window` preemptively); code-split routes via `React.lazy` so the Documents and Chat pages don't share one bundle unnecessarily.
- **Streaming:** token-by-token rendering should batch DOM updates (e.g. accumulate into a ref and flush on `requestAnimationFrame`) rather than calling `setState` per token, to avoid excessive re-renders on fast local Ollama responses.
- **Test:** Lighthouse pass on both pages; manually verify chat streaming feels responsive with a local `llama3.2` model.

### Step 20 — Production build and deployment

- **Build:** `frontend && npm run build` → `frontend/dist`.
- **Serving choice:** mount the built SPA from FastAPI itself for a single-process deployment:
  ```python
  app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")
  @app.get("/{full_path:path}")
  async def spa_fallback(full_path: str):
      return FileResponse("frontend/dist/index.html")
  ```
  registered *after* all `/api/*` routers so API routes take precedence. This avoids standing up a separate nginx container for what is currently a single-machine, Docker-Compose-based app — add a dedicated static host later only if the deployment topology changes.
- **Modify:** `docker-compose.yml` — add a build step (or a multi-stage `Dockerfile`: stage 1 `node:20` builds the frontend, stage 2 `python` image copies `frontend/dist` alongside the FastAPI app).
- **Config:** production `.env` sets `ALLOWED_ORIGINS` to the real deployed origin (no `localhost:5173` in prod).
- **Test:** `docker compose up --build`, confirm the SPA loads at the container's exposed port and `/api/health` responds; confirm a hard refresh on a client-side route (e.g. `/documents`) doesn't 404 (validates the SPA fallback route).

### Step 21 — Final verification and acceptance checklist

- [ ] Upload PDF, DOCX, and TXT files — all reach `status: completed` with correct `chunk_count`.
- [ ] Document list shows filename, type, size, upload date, status, chunk count; search filters correctly; responsive at mobile/tablet/desktop widths.
- [ ] Chat answers cite retrieved chunks/documents; streaming renders incrementally; empty-KB and Ollama-down states show clear errors, not crashes.
- [ ] Old `/ingest` (raw file-path) endpoint is removed; no code path accepts a server-side file path from client input.
- [ ] `app/utils.py`'s dead code is either deleted or actually wired in — no orphaned logic left behind.
- [ ] CORS restricted to known origins; file upload validated by type/size/magic-bytes; SQL queries all parameterized.
- [ ] Backend and frontend test suites pass in CI; integration test covers upload→list→chat→delete end to end.
- [ ] `docker compose up --build` serves the full app (frontend + API) from one command, matching the project's existing deployment style.
- [ ] README updated to reflect the new endpoints, the frontend dev/build commands, and the removal of the old `/ingest` contract.

---

## Open decisions to confirm before implementation starts

1. **Auth:** the app currently has none. Should the React frontend assume a single trusted local user (matching today's posture), or is a lightweight API key/login expected as part of this work?
2. **Package manager:** pnpm vs npm for `frontend/` — no functional difference for this plan, but affects lockfile conventions.
3. **Streaming transport:** plain chunked `text/plain` streaming (proposed above) vs. a WebSocket — chunked streaming is simpler and sufficient for one-way token streaming; WebSocket only pays off if bidirectional features (typing indicators, multi-turn interrupts) are planned later.
