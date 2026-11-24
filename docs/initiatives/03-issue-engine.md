**Level:** Initiative · **Status:** Designed

**Purpose:** Create, review, validate, version, and serve bugs. An issue is a **diff + project version**. The database is the source of truth; public issues export as JSONL to the `cerberus-issues` repo.

**Creation:** UI (author mode) and harnesses through **MCP** (Claude Code, Codex, Cursor). No CLI.
**Builds on:** #2 (images, editable/read-only patterns, `run-tests`, JUnit, `project.version.build`), #1 (Monaco, shared chat panel), #4 (dev box sessions), #5 (shared LLM usage and cost control).
**Hands off to #4:** the run package.


## Epic 3.1 — Issue model and storage

Fields, tables, and categories.

| Story | Description | Done when |
|---|---|---|
| 3.1.1 Issue fields | slug, title, project, project_version, patch, report (expected / actual / steps / optional trace), expected_failures, category, difficulty 1-5, area, hints, source (human / llm / mcp + author or model), parent version, org_id, visibility (public / private). | Field spec documented. |
| 3.1.2 Issue database tables | `issues`, `issue_versions`, `issue_validations`, `issue_reviews`, `authoring_sessions`. All with `org_id`. | Migrations exist. |
| 3.1.3 Issue category list | 17 categories with descriptions in `docs/issue-categories.md`: off-by-one, wrong-condition, none-handling, wrong-api-usage, type-coercion, string-handling, date-time, sorting-ordering, query-logic, validation-missing, state-mutation, async-await, http-status, routing, template-ui, config, cross-layer. | List published; extendable by PR. |

## Epic 3.2 — Issue Authoring API

One backend used by the UI, MCP, and the built-in generator.

| Story | Description | Done when |
|---|---|---|
| 3.2.1 Authoring sessions | Start a session on a project version: dev box from the image plus a clean copy kept outside the workspace. Idle timeout; close on submit or cancel. | A session opens and closes cleanly. |
| 3.2.2 Authoring file operations | list / read / write / search, editable files only. Writes to read-only files are rejected. | Read-only files cannot change through the API. |
| 3.2.3 Authoring tests and diff | `run-tests` with per-test result (pass / failure / error). Diff = clean copy vs workspace (`diff -ruN`), editable files only. | Diff and test results are available at any time. |
| 3.2.4 Submit draft | Fields + diff create a draft. Failing tests are auto-filled from the last run. Validation starts. | Draft created and validation starts automatically. |
| 3.2.5 Authoring API auth and limits | HTTPS only. Local: localhost with a generated local certificate. Hosted: per-user token and `author` role check. Rate limits per session. | Calls without TLS or without auth (hosted) are rejected. |

## Epic 3.3 — Author mode UI

Create issues in the web IDE: edit, test, review the diff, fill the form.

| Story | Description | Done when |
|---|---|---|
| 3.3.1 Project picker and authoring session | Pick project and version; open an authoring session in the IDE. | Author lands in the editor with clean code. |
| 3.3.2 Edit and test in author mode | Monaco editor, run-tests button, live pass/fail. | Author breaks code and sees failing tests. |
| 3.3.3 Diff review view | Monaco diff view (inline / side by side, + / -) per file, changed-file list. | Diff looks like the VS Code source control view. |
| 3.3.4 Issue form | Title, report, category, difficulty, hints. Failing tests auto-filled. Submit. | A complete draft is submitted from the UI. |
| 3.3.5 Author assistant panel (optional) | Shared chat component (#1) in author-assistant mode. Uses the same API tools, with the cost meter and budget from #5. | Author can ask for a bug idea, report, or hints. |

## Epic 3.4 — MCP server and skill

Connect Claude Code, Codex, Cursor, and other harnesses to author issues.

| Story | Description | Done when |
|---|---|---|
| 3.4.1 MCP server (HTTPS) | Wraps the Authoring API. Streamable HTTP over HTTPS only (local certificate on localhost; TLS + token in hosted). Every tool call is logged. | Claude Code connects over HTTPS and lists the tools. |
| 3.4.2 MCP tools: discovery | `list_projects`, `get_project` (README, tree, editable patterns, tasks), `list_categories`, `list_issues` (avoid duplicates), `get_issue`. | A harness can explore before authoring. |
| 3.4.3 MCP tools: session | `start_authoring(project, version?)`, `get_session`, `cancel_session`. | Sessions are controlled through MCP. |
| 3.4.4 MCP tools: code | `list_files`, `read_file(path, lines?)`, `search(pattern, glob?)`, `write_file`, `edit_file(path, old, new)`, `reset_file` (back to clean copy). | Edits are limited to editable files. |
| 3.4.5 MCP tools: tests and diff | `run_tests` (pass/failure/error per test + summary), `get_diff`, `check_patch` (static rules), `get_coverage(file?)` when available. | Harness can self-check before submit. |
| 3.4.6 MCP tools: submit and status | `submit_issue(fields)`, `get_validation(id)`, `update_issue(id, fields)` (drafts only), `list_my_drafts`. | Full loop: create, validate, fix, resubmit. |
| 3.4.7 MCP tools: update issues | `list_needs_update(project)`, `start_update(issue_id)` (old intent + new code), then the code/test/submit tools. | Affected issues can be fixed through MCP. |
| 3.4.8 Authoring skill | Skill file in this repo under `skills/`: rules (minimal, realistic, no syntax errors, caught by a test, report shows symptom), categories, flow, good and bad examples. | A harness produces drafts that pass validation. |
| 3.4.9 MCP setup guide | Config snippets for Claude Code, Codex, Cursor (HTTPS URL, token, local certificate trust). | An author connects in under 2 minutes. |
| 3.4.10 MCP safety `guided` | MCP cannot approve or activate. No access outside the session or to the network. Rate limits on tool calls. | Review stays in the UI only. |

## Epic 3.5 — Issue validation

Prove each issue is real, caught by tests, and reversible.

| Story | Description | Done when |
|---|---|---|
| 3.5.1 Static patch checks | Editable and not read-only files only; applies cleanly; <= 3 files, <= 30 lines; no added or deleted files. | Rejected with a reason. |
| 3.5.2 Test checks `guided` | `--network none`. Baseline: all pass. With patch: >= 1 failure, <= 50% failing, only `<failure>` never `<error>` (no syntax/import errors), matches expected_failures, 3 identical runs. Reversed: all pass. | Validation record saved. |
| 3.5.3 Validation queue | One at a time locally; worker pool in hosted. Progress in UI. ~5 min max. | Queue visible. |
| 3.5.4 Validation logs | `issue.validate.pass\|fail` with reason (STE100). | Each outcome is logged. |

## Epic 3.6 — Review and lifecycle

Every issue is reviewed before it is served.

| Story | Description | Done when |
|---|---|---|
| 3.6.1 Issue status flow | draft -> validated -> in-review -> active -> stale/retired, plus rejected and needs-update. All issues are reviewed in both modes. | Transitions are enforced and logged. |
| 3.6.2 Review screen | Monaco diff view, report, failing tests, hints, source (UI / MCP / generator). Approve / Edit / Reject with reason. | No issue is active without approval. |
| 3.6.3 Issue difficulty | Seed from author or LLM; adjust by files and lines changed and distance from the failing test; user data later (#6). | Stored per version. |
| 3.6.4 Show issue origin after submit | After a learner submits, show how the issue was made (UI author, MCP harness, or generator) and its category. | Origin shows on the result screen. |

## Epic 3.7 — Built-in LLM generator

Our own generator, as one more client of the Authoring API.

| Story | Description | Done when |
|---|---|---|
| 3.7.1 Issue generator `guided` | Uses the same Authoring API tools. Input: project, category, area, difficulty. Up to 3 retries with the validation reason. | Valid drafts for seed projects. |
| 3.7.2 Generated hints and report `guided` | Author hints optional; LLM fills gaps (>= 3, vague to specific). Report shows the symptom. | Every active issue has hints. |
| 3.7.3 Generator target areas `guided` | Prefer covered functions when coverage data exists. | No untested targets when coverage exists. |
| 3.7.4 Generator cost rules `guided` | Uses the shared LLM usage component (#5): model routing, prompt caching, session budget, cost meter. | Cost shows for each generation. |

## Epic 3.8 — Carry-over and updates

Keep issues working when a project changes.

| Story | Description | Done when |
|---|---|---|
| 3.8.1 Impact check `guided` | On a new project version: changed files between versions vs files in the patch. No overlap = unaffected; else affected. | Every issue is classified. |
| 3.8.2 Automatic carry-over `guided` | Unaffected: quick re-validate, auto-active; old version becomes stale. | No human work needed. |
| 3.8.3 Affected issue handling `guided` | `patch --fuzz=2` + full validation. Pass -> in-review; fail -> needs-update. | Flags are correct. |
| 3.8.4 Update issue feature `guided` | In UI or MCP: edit by hand, regenerate with LLM (same intent), or retire. Then validate and review. | A broken issue can be fixed. |

## Epic 3.9 — Issue sharing

Public JSONL dataset in GitHub.

| Story | Description | Done when |
|---|---|---|
| 3.9.1 Create cerberus-issues repo | Public dataset repo with the safety rules. | Repo is protected. |
| 3.9.2 Issue export | One JSONL file per issue; active public issues only; private issues never exported. | Running it twice gives no diff. |
| 3.9.3 Issue import on sync | Pull with content sync; load as validated; re-validate locally before active. | Imported issues work locally. |
| 3.9.4 Publish issues to GitHub | "Publish to GitHub" (UI) and MCP `publish_issues`: export, branch `data/<date>-<id>`, commit changed JSONL only, PR labelled `data` with `Part of #<n>` to the standing "Dataset updates" issue. In `cerberus-issues`, the linked-issue check accepts `Part of #<n>` only for an open issue with the `data` label. | One PR with only changed files; check passes. |

## Epic 3.10 — Serving issues

Give each run a validated issue and hand it to the sandbox.

| Story | Description | Done when |
|---|---|---|
| 3.10.1 Issue picking `guided` | Project, mode, difficulty, categories, user history (no repeats). Pool first; generate on demand; fall back to pool. | A run always gets an issue or a clear error. |
| 3.10.2 Pool pre-fill | 3 per project. Off by default in local mode; cost estimate before turning on. Generated issues still need review. | Opt-in works. |
| 3.10.3 Run package | `{project_version_id, image, patches[], reports[], editable[], readonly[]}` handed to #4. | #4 gets everything in one object. |
| 3.10.4 Combine issues - parked | Non-overlapping patches with combined validation. | Placeholder. |

## Order

```
3.1 -> 3.5.1-3.5.2 (validator, hand-made patch on flask-notes) -> 3.2 (Authoring API)
-> 3.4.1-3.4.6 (MCP: author issues with Claude Code before the UI exists)
-> 3.6.1-3.6.2 (review) -> 3.10.1, 3.10.3 (serve one issue)
-> 3.3 (author mode UI, after #1 and #4) -> 3.4.7-3.4.10 -> 3.7 (generator)
-> 3.8 (carry-over) -> 3.5.3-3.5.4 -> 3.10.2 -> 3.9 (sharing, publish) -> 3.6.3-3.6.4
```

**First milestone:** an issue authored through MCP on `flask-notes`, validated, reviewed, and served as a run package.

## Decisions

- UI and MCP only. No CLI. MCP is the main harness connection.
- MCP and the Authoring API use HTTPS only (local certificate on localhost).
- The database is the source of truth; JSONL export to `cerberus-issues`; hosted orgs can keep private issues.
- Publishing to GitHub goes through a PR labelled `data` that references a standing "Dataset updates" issue.
- Every issue is reviewed. MCP cannot approve.
- Syntax-error bugs are blocked (`<error>` vs `<failure>` in JUnit).
- Limits: <= 3 files, <= 30 lines, <= 50 % failing; pool of 3 (off by default locally).
- Unaffected issues carry over automatically; affected issues use "Update issue".
- The built-in generator uses the same API. Cost control comes from #5.
- Learners see the issue origin after submit.
- The authoring skill lives in this repo under `skills/`.
- Hosted mode has an `author` role.
- Combining issues is parked.

## Log events

`issue.session.start|end`, `issue.propose`, `issue.generate.fail`, `issue.validate.pass|fail`, `issue.review.approve|reject`, `issue.activate`, `issue.stale`, `issue.carryover.pass|fail`, `issue.needs_update`, `issue.retire`, `issue.export`, `issue.import`, `issue.serve`, `mcp.tool.call`
