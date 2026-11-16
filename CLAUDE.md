# Cerberus

Debugging practice and exam platform: a web IDE loads a correct base project plus one versioned issue patch; the user fixes the bug; a guardrailed LLM tutor (user's own API key) helps with Socratic hints and documentation.

Status: design phase. Agree each design topic with the user before writing code.

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

- Append one JSON line to `logs/build.jsonl` for each decision, file change, failure, or push. Use the same fields as above.
- Use event names: `decision.record`, `doc.create`, `doc.update`, `code.add`, `code.change`, `test.run`, `repo.push`, `repo.push.fail`.
- Add the commit hash in a `commit` field when known. Use `trace_id` = `session-<date>`.
- Commit the build log with the change it describes, then push.
- Remote is HTTPS. On this machine, run git with `-c safe.directory=<repo path>` (NTFS mount).
