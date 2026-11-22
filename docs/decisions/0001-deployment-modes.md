# 0001 — Deployment modes: local and hosted

- **Status:** Accepted
- **Date:** 2026-11-18
- **Decider:** gru13

## Context

Cerberus starts as a single-user, open-source app that runs on the user's own machine. Later, colleges and companies will host it on their own network for many users. Adding multi-user support to a single-user design later is costly (database tables, auth, sandbox limits). We design for both modes now and build the local mode first.

## Decision

Cerberus has two deployment modes, selected by one setting:

```
CERBERUS_MODE=local | hosted
```

| Area | Local (single user) | Hosted (college / company) |
|---|---|---|
| Users | One person on their machine | Many learners and admins |
| Auth | None (auto-login as the local user) | OIDC SSO (Google, Microsoft, Keycloak) or email |
| Database | Postgres (Docker) | Postgres |
| Images | Built locally after content sync | Built by CI, pushed to a registry, pulled by workers |
| Sandbox | Local Docker | Worker pool with per-user quotas |
| LLM key | User's own key | User's own key or org key with per-user budget |
| Content | `cerberus-content` | `cerberus-content` + org private repos |
| Exams | Self-assessment | Admin creates exams, assigns groups, sees results |

### Rules that apply from day one

1. **Tenancy columns.** Every table has `org_id` and `user_id`. Local mode uses one default org and one default user.
2. **Roles.** `learner`, `author`, and `admin` exist from the start. The local user has all three. `author` can create and update issues; only `admin` (or the local user) approves them.
3. **Same database.** Postgres in both modes. One migration set.
4. **Logs.** Every log entry has `org_id` and `user_id` when known.
5. **Mode checks.** Only the provider factories read `CERBERUS_MODE`. Other code uses the interfaces below.

### Interfaces (two implementations each)

| Interface | Local implementation (build now) | Hosted implementation (later) |
|---|---|---|
| `AuthProvider` | `LocalAuth` | `OidcAuth` |
| `ImageProvider` | `LocalBuild` | `RegistryPull` |
| `SandboxExecutor` | `LocalDocker` | `WorkerPool` |
| `KeyProvider` | `UserKey` | `OrgKey` (with budget) |
| `ContentSource` | single repo | list of repos |

## Consequences

- The first release stays small: only local implementations are built.
- Hosted mode is an addition, not a rewrite.
- Initiative #2: image build sits behind `ImageProvider`; registry is a parked story.
- Initiative #7: covers both modes (auth, orgs, groups, roles, key policy, admin, exam assignment). To be discussed later.
- A small cost now: every query filters by `org_id`.
