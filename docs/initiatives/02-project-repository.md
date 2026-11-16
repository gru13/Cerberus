**Level:** Initiative (split into epics, then stories)

**Purpose:** Correct, versioned Python projects that every issue builds on.

### Scope
- **Base projects:** git repos with version tags (Flask, FastAPI, Django, or plain Python).
- **Per project version:**
  - Hidden test suite: unit tests and HTTP/API checks against the running app. Kept outside the user workspace.
  - Editable-files list (for example `app/**`; not `tests/`, `conftest.py`, config files).
  - Metadata: framework, modules, size, difficulty range, run command, port, seed data, env vars (no secrets).
  - Pinned dependencies (these select which library docs to index).
- **Image store (private registry):**
  - Base image: Python + pytest + tools (versioned).
  - Project image: dependencies + correct code, one per project version.
  - Build steps are stored so each image can be rebuilt. No per-issue images.
- **Docs index:**
  - Project docs: README, module map, signatures, docstrings. **No function bodies**, so the index never holds the correct code.
  - Library docs: official docs for the pinned versions. Indexed once, shared across projects.
  - Embeddings: one fixed local model (free, same index for all users).

### Open questions
- Which 1–3 projects first, and what size?
