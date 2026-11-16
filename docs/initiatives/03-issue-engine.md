**Level:** Initiative (split into epics, then stories)

**Purpose:** Create, validate, version, and serve bugs.

### Scope
- **Issue:** a versioned diff on one project version. A project version can have many issues.
- **Issue version fields:** patch, bug report, failing hidden tests, category (off-by-one, None handling, wrong API use, logic, config, routing, ...), difficulty, hint ladder, linked docs, source (human/LLM), validation record.
- **Creation (hybrid):**
  - Human: admin writes patch and bug report.
  - LLM: proposes a mutation from the category list (platform key for the pool, user key for on-demand).
- **Validator (in sandbox):**
  - Apply patch → expected tests fail.
  - Reverse patch → all tests pass.
  - Lint and import check. The diff touches editable files only.
- **Serving a run:** pick from the pool or generate new (with timeout, fall back to the pool). Combine several issues only if the patches apply cleanly and touch different areas.
- **Lifecycle:** draft → validated → verified → active → retired.
- **Logs:** one entry per lifecycle step only.

### Open questions
- On a new base project version: re-validate issues automatically, or keep them pinned?
- Rules for combining issues.
