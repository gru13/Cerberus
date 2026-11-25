# Cerberus

Debugging practice and exam platform: a web IDE loads a correct base project plus one versioned issue patch; the user fixes the bug; a guardrailed LLM tutor (user's own API key) helps with Socratic hints and documentation.

Status: design complete; build not started. Design index: `docs/README.md`. Agree each design topic (and any change to it) with the user before writing code.

## Logging rules (mandatory for all code)

1. Write every log message in ASD-STE100 Simplified Technical English:
   - Use approved words with one meaning each. Use short sentences (max 20 words).
   - Use active voice and present tense. One instruction or fact per sentence.
   - Example: "The sandbox starts the test run." Not: "Test run is being kicked off by sandbox."
2. Use structured logs (JSON lines). Each entry has:
   - `ts`, `level`, `msg` (STE100 sentence)
   - `event` (dotted name, e.g. `issue.validate.fail`)
   - `subject` {type, id}, `predicate` (verb), `object` {type, id} → a triple for the knowledge graph / ontology
   - `run_id`, `user_id`, `project_version`, `issue_version` when known
   - `trace_id` for correlation
3. Log every issue lifecycle step so the full cycle is traceable:
   `issue.propose → issue.apply → issue.validate (fail-before / pass-after) → issue.verify → run.start → run.edit → run.test → run.hint → run.submit → run.score → issue.retire`
4. Use a fixed vocabulary of entity types (Project, ProjectVersion, Issue, IssueVersion, Run, User, Test, Hint, File) and verbs. Add new terms to `docs/ontology.md` before use.
5. Never log secrets: no API keys, tokens, passwords, or full user code. Log hashes or ids.

## Build log (mandatory for every session)

- Keep the log small and useful. Append one JSON line to `logs/build.jsonl` **only** for:
  - a design decision (`decision.record`)
  - a milestone: an initiative, epic, or story moves status (`work.status`)
  - a failure that changes the approach (`*.fail`)
- Do not log routine file edits, commits, or pushes. Git history holds them.
- Add the commit hash in a `commit` field when known. Use `trace_id` = `session-<date>`.
- Commit the build log with the change it describes, then push.

## Work tracking

- Board: GitHub Project "Cerberus Workboard" (https://github.com/users/gru13/projects/4).
- Hierarchy: Initiative → Epic → Story (labels `initiative`, `epic`, `story`; epics are sub-issues of initiatives, stories of epics). Every item except an initiative has a parent. Chores and design records go under Initiative 0 "Project management" (#377).
- Status (same meaning at every level): Designing (owner decides) → Backlog (designed, not scheduled) → Ready (current phase) → In progress → In review (PR open, owner merges) → Done. Parked = hosted mode or later.
- Fields: `Initiative` (0–8) and `Phase` (P0–P6, Later; from the build order in `docs/README.md`). Set both on every new item.
- Assignee = needs the owner: assign gru13 to `guided` stories, items In review, and items that need an owner decision. Leave other items unassigned.
- Views: **My work** (assigned to the owner, not Done or Parked), **Roadmap** (all open work), **Done**.
- When a PR opens, move its issue to In review and assign gru13. When it merges, move it to Done.
- Built by: when a story reaches Done, set `Built by` (Claude 100% / gru13 100% / gru13 + Claude) and `Claude %` (0–100, Claude's share of the code). gru13's stories are 0 unless Claude wrote part of the code. Also add a one-line "Built by" comment on the issue.
- Initiative details live in `docs/initiatives/` and in the issue body. Keep both in sync.

## Code style (mandatory)

- Follow `docs/code-style.md` for all code. The short form:
  - Every function has a full typed signature and a header: one summary line, then `Functional:` and `Technical:` lines (plus `Limits:`, `Errors:`, `Why:` when relevant). Functions of 3 lines or fewer need only the summary.
  - One intent per file, stated on the first line (`Intent: ...`). Warn above 200 lines; above 300 lines, split or add `Why:`. Functions are at most 70 lines.
  - Python: Pydantic v2 models for all structured data; errors subclass `CerberusError` with a fixed code and STE100 message; never raise built-in exceptions or catch broadly.
  - Rust: `thiserror`, no `unwrap`/`expect`/`panic!` outside tests, `unsafe` forbidden.
- Run the `api: check` task before every PR.

## Dev tasks (mandatory)

- `.vscode/tasks.json` lists every developer command: CLI commands, checks, and scripts.
- When a PR adds or changes a command, add or update its task in the same PR. Name tasks `<area>: <action>` (for example `api: test`).
- Keep `<area>: check` equal to the CI steps for that area.

## Guided work (label `guided`)

- The owner builds `guided` stories personally to learn: security, performance, and core systems (about 40% of the effort). The list is in `docs/README.md` (Ownership): sandbox and Rust agent, realtime and persistence, AI safety, data integrity and the bug generator, platform security.
- Claude builds the rest (about 60%): UI, app skeleton, CRUD, compose and CI, and the fake agent (8.9.5) so other work does not wait for the Rust agent.
- For these stories Claude is a guide: explain concepts, propose structure and crates, review code, point to docs, give small illustrative snippets.
- Do not write the implementation, commit code, or open PRs for `guided` stories unless the owner explicitly asks.
- Teaching Phase 1: follow `docs/learn/path-p1.md`. Work one module at a time, in order.
  - Start a module: check its prerequisites, then say which concept ids to read. Cite ids; do not copy notes from the index.
  - Run the loop: concept reads → the one exercise → check the "done when" line → the story entries in `docs/guided-study-guide.md` → the owner builds the stories.
  - Ask a short question for each "done when" line before the owner starts a story. Do not give the answer first.
  - Exercises are throwaway scripts outside the repo. Do not commit them.
  - Do not start a module before its prerequisites are done. Do not teach the parked design issues (#394–#409).
  - Report progress as modules done out of 9. Do not invent time estimates; use the owner's measured pace.
- Remote is HTTPS. On this machine, run git with `-c safe.directory=<repo path>` (NTFS mount).

## Git safety (mandatory)

- Never commit or push to `main`. Work on a branch (`feat/…`, `fix/…`, `chore/…`, `docs/…`), push it, open a PR, merge the PR.
- GitHub ruleset `protect-main` enforces: PR required, no force push, no branch deletion, review threads resolved. No bypass.
- Local hooks in `.githooks/` (enable once per clone: `git config core.hooksPath .githooks`):
  - `pre-commit`: blocks commits on main and staged secrets (API keys, tokens, private keys, `.env` files).
  - `pre-push`: blocks pushes to main.
- Never use `--no-verify`, `--force`, or `git push origin main`.
- Keep local branches clean: after a PR merges, run the `repo: prune-branches` task (fetch with prune, then `git branch -d` for merged branches). Never force-delete a branch until `git cherry` shows it has no unique commits.
- Never commit secrets. Use `.env` (ignored) and `.env.example` (placeholders only).
- Every PR must link an open issue with `Closes #<n>` in the body. The required check `linked-issue` fails otherwise. Create the issue first.
- Only the owner (gru13) has write access. Others contribute from a fork through a PR; the owner reviews (CODEOWNERS) and merges.
