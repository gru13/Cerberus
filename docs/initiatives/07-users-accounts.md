**Level:** Initiative (split into epics, then stories)

**Purpose:** Identity, keys, progress.

### Scope
- **Login:** email or GitHub OAuth.
- **Provider profiles:** provider, base URL, model, key. Key encrypted at rest, never logged, never sent back to the browser. "Test connection" button.
- **Modes:** practice; exam (self-assessment in local mode; admin-assigned in hosted mode).
- **History:** past runs, progress per category and difficulty.

### Open questions
- Login method.
- Leaderboards?

### Deployment modes (to discuss later)
See [0001 — Deployment modes](../decisions/0001-deployment-modes.md). This initiative covers both:
- **Local:** no login, one default org and user, local provider profiles and history.
- **Hosted:** OIDC/email login, orgs, groups, roles (`learner`, `admin`), key policy (user key or org key with budget), admin pages, exam assignment.
