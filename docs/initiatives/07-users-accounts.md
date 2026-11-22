**Level:** Initiative · **Status:** Designed

**Purpose:** Identity, preferences, keys, tokens, and exams in both deployment modes. Local mode is built now. Hosted mode is designed now and parked (decision 0001).
**Builds on:** #190 (core tables, LocalAuth, secrets, tokens, events), #5 (test connection, budgets, exam-mode rules), #6 (results, stats), #1 (settings UI; hosted UI 1.12 parked).

**Covered elsewhere:** `orgs` / `users` / `memberships` tables and local seed (#190 8.2.4), `LocalAuth` and `require_role` (#190 8.3.2), key encryption and token hashing (#190 8.7), stats and skill profile (#6.5), settings screens (#1.11).

## Key design points

1. **One exam model.** A local self-exam and a hosted assigned exam are the same `exams` record. Only the creator and the assignment differ. Exam rules are built once.
2. **No passwords.** Hosted login uses OIDC or an email magic link.
3. **Portable data.** Export runs, results, chats, and settings (never keys); import on another machine.


## Epic 7.1 — Local account

Profile, provider profiles, tokens, and data export for the local user. Build now.

| Story | Description | Done when |
|---|---|---|
| 7.1.1 Profile and preferences | Display name; theme, editor font and size, keybindings, autosave delay. | Preferences apply across sessions. |
| 7.1.2 LLM provider profiles API | Create, edit, delete; default profile; text model and code model (#5.2.3). Keys encrypted by #190, tested by #5.1.7, edited in #1.11.1. | The tutor uses the default profile. |
| 7.1.3 Personal tokens | Create, list, revoke MCP tokens with scopes (authoring tools). Shown once. | Claude Code connects with a token; revoke stops it at once. |
| 7.1.4 My data | Export all as a zip (runs, results, chats, settings; no keys); import on another machine; delete all. | Export, then import on a fresh install, restores history. |

## Epic 7.2 — Exams

One exam model for local self-exams and hosted assigned exams.

| Story | Description | Done when |
|---|---|---|
| 7.2.1 Exam model | `exams`: title, issue selection (fixed, or random from a difficulty and category set), time limit, hint limit, tutor policy, practice check off, reveal policy. `exam_attempts` links attempts to runs. | One record type covers both modes. |
| 7.2.2 Self-exam (local) | Presets such as "30 min, difficulty 3, Python". Results are separate from practice and count as exams in the skill profile. | A user takes a timed exam alone. |
| 7.2.3 Exam rules | Server-side timer with auto-submit at the end; hint limit; no "Check my fix"; original diff shown after submit (local) or after the exam window (hosted). | Rules hold even when the browser tab is closed. |
| 7.2.4 Hosted exam assignment - parked | Exam window, assigned groups, random equal-difficulty set (calibrated, #6.5.3) or a fixed issue, late policy. | Placeholder. |
| 7.2.5 Exam results dashboard - parked | Results per group and per issue; CSV export. | Placeholder. |

## Epic 7.3 — Hosted identity (parked)

Login and sessions for hosted mode. No passwords.

| Story | Description | Done when |
|---|---|---|
| 7.3.1 OIDC login - parked | `OidcAuth`: Google, Microsoft, Keycloak, any OIDC provider. | Placeholder. |
| 7.3.2 Email magic link - parked | Login link by email. Cerberus stores no passwords. | Placeholder. |
| 7.3.3 Sessions - parked | Cookie sessions in Postgres; logout; list and revoke sessions; idle and absolute timeout. | Placeholder. |
| 7.3.4 Account linking - parked | The same email across providers is one user. | Placeholder. |

## Epic 7.4 — Orgs, groups, and roles (parked)

Organizations, membership, groups, and private content for hosted mode.

| Story | Description | Done when |
|---|---|---|
| 7.4.1 Orgs - parked | Create org, org settings, auto-join by email domain (e.g. `@college.edu`). | Placeholder. |
| 7.4.2 Membership and invites - parked | Invite link or email; roles learner, author, admin; role change. | Placeholder. |
| 7.4.3 Groups - parked | Classes or teams; assign practice sets and exams. | Placeholder. |
| 7.4.4 Private org content - parked | Org repositories (multi-repo `ContentSource`) and private issues (#3), visible only in the org. | Placeholder. |

## Epic 7.5 — Key policy and quotas (parked)

Org keys, model policy, budgets, and sandbox quotas for hosted mode.

| Story | Description | Done when |
|---|---|---|
| 7.5.1 Org key - parked | `OrgKey`: admin sets allowed providers and models; budgets per user and per group (#5.2.2). | Placeholder. |
| 7.5.2 Sandbox quotas - parked | Concurrent sessions per user, CPU minutes per day (WorkerPool, #4.7). | Placeholder. |

## Epic 7.6 — Admin, audit, and privacy

Audit view now; admin pages, retention, and data rights for hosted mode.

| Story | Description | Done when |
|---|---|---|
| 7.6.1 Audit view | Every admin action (issue approve or reject, role change, settings change, exam edit) emits an event. Read-only admin view with filters. | Each approval shows who did it and when. |
| 7.6.2 Admin pages - parked | Users, groups, usage and cost, running sandboxes. | Placeholder. |
| 7.6.3 Data retention - parked | Retention per org for chats, events, snapshots; purge job. | Placeholder. |
| 7.6.4 User data rights - parked | Export and delete for a hosted user (reuses 7.1.4). | Placeholder. |

## Order

```
7.1.1 -> 7.1.2 -> 7.1.3 -> 7.2.1 -> 7.2.3 -> 7.2.2 -> 7.6.1 -> 7.1.4   (local, build now)
-> hosted (parked): 7.3 -> 7.4 -> 7.5 -> 7.2.4-7.2.5 -> 7.6.2-7.6.4
```

**First milestone:** set preferences and an OpenRouter profile -> create an MCP token -> take a 30-minute self-exam (timer auto-submits, hints are limited, result saved as an exam) -> export your data.

## Decisions

- Hosted login: OIDC and email magic link. No passwords. GitHub OAuth later.
- One exam model for local and hosted.
- Hosted exams use a random issue from a calibrated equal-difficulty set by default; a fixed issue is an option.
- No leaderboards by default. An optional practice-only group leaderboard is parked.
- Hosted exams show the original diff after the exam window closes.
- Local mode has one user. Groups use hosted mode.
- Self-exams count as exams in the skill profile.

## Log events

`user.login|logout`, `user.token.create|revoke`, `user.data.export|import|delete`, `exam.create|start|submit|expire`, `admin.action`
