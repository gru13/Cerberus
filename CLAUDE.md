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
- Hierarchy: Initiative → Epic → Story (labels `initiative`, `epic`, `story`; epics are sub-issues of initiatives, stories of epics).
- Status columns: Backlog → Designing → Designed → Building → Done.
- Initiative details live in `docs/initiatives/` and in the issue body. Keep both in sync.

## Guided work (label `guided`)

- The owner builds `guided` stories personally to learn (now: the Rust in-container agent, Epic 4.3).
- For these stories Claude is a guide: explain concepts, propose structure and crates, review code, point to docs, give small illustrative snippets.
- Do not write the implementation, commit code, or open PRs for `guided` stories unless the owner explicitly asks.
- Remote is HTTPS. On this machine, run git with `-c safe.directory=<repo path>` (NTFS mount).

## Git safety (mandatory)

- Never commit or push to `main`. Work on a branch (`feat/…`, `fix/…`, `chore/…`, `docs/…`), push it, open a PR, merge the PR.
- GitHub ruleset `protect-main` enforces: PR required, no force push, no branch deletion, review threads resolved. No bypass.
- Local hooks in `.githooks/` (enable once per clone: `git config core.hooksPath .githooks`):
  - `pre-commit`: blocks commits on main and staged secrets (API keys, tokens, private keys, `.env` files).
  - `pre-push`: blocks pushes to main.
- Never use `--no-verify`, `--force`, or `git push origin main`.
- Never commit secrets. Use `.env` (ignored) and `.env.example` (placeholders only).
- Every PR must link an open issue with `Closes #<n>` in the body. The required check `linked-issue` fails otherwise. Create the issue first.
- Only the owner (gru13) has write access. Others contribute from a fork through a PR; the owner reviews (CODEOWNERS) and merges.
