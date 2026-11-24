**Level:** Initiative · **Status:** Designed

**Purpose:** Help the learner debug without giving the answer. Socratic questions, library functions and classes explained from real docs, test failures and errors explained. Never the fix.
**Also provides:** the shared LLM layer (`api/src/cerberus/llm/`): provider adapters, cost metering, and budgets. #3 (generator, author assistant) uses it.
**Builds on:** #190 (KeyProvider, EventBus, events), #4.3.6 (agent read-only tools), #3 (author hints, patch for checks), #1.9 (chat panel).

## Key design points

1. **The model never sees the patch.** Only the server has it, to check answers before release. A jailbroken model cannot leak what it does not know.
2. **Version-exact docs for free.** The dev box has every library at the locked version. The tutor reads docstrings and signatures there (Python `inspect`, TS `.d.ts`). Guide-style docs come from doc packs.
3. **Guardrails are server-side.** Every code block is held and checked against the reverse patch and the project code before release. Works with any model, including small local ones.
4. **Exam mode allows code, not answers.** Exact quotes, generic samples, and library examples are allowed. Fix code, rewritten project code, and the bug location are blocked.
5. **Guardrails need a deep design.** Epic 5.5 is the core risk. A dedicated design session (5.5.7) comes before any guardrail code.
6. **Works without a key.** Author hints (at least 3 per issue, #3) drive the hint button with no LLM.


## Epic 5.1 — LLM provider layer

Shared provider adapters for the tutor, the generator, and the author assistant.

| Story | Description | Done when |
|---|---|---|
| 5.1.1 Provider interface | `chat(messages, tools, stream)` -> normalized stream of text deltas and tool calls. Capability flags: tools, streaming, context size, caching, JSON output. | One interface for all features. |
| 5.1.2 OpenAI-compatible adapter | OpenAI, OpenRouter, Groq, Gemini compat endpoint, Ollama, LM Studio, vLLM. Handles tool-call differences. | The tutor works on OpenRouter and Ollama. |
| 5.1.3 Anthropic native adapter | Tools, streaming, prompt caching (`cache_control`). | The tutor works on Claude. |
| 5.1.4 Gemini native adapter - parked | Only if the compat endpoint is not enough. | Placeholder. |
| 5.1.5 Model catalog and prices | Capabilities and prices per model: built-in defaults, OpenRouter price fetch, user override. Local models cost 0. | Cost can be estimated for any profile. |
| 5.1.6 Reliability | Timeouts, backoff on 429 and 5xx, cancel when the browser disconnects, clear errors (invalid key, out of credit, model not found). | Errors are readable by people. |
| 5.1.7 Test connection | Small call that checks key, model, and tool support (used by #1.11.1). | Pass or fail with a reason. |

## Epic 5.2 — Usage and cost control

Shared metering, budgets, routing, and caching.

| Story | Description | Done when |
|---|---|---|
| 5.2.1 Usage metering | Tokens in, out, and cached per call -> cost. `llm_usage` table: run, feature (tutor / generator / author assistant), model. | Every call has a cost. |
| 5.2.2 Budgets | Per session and per month. Warning at 80%, stop at 100%. Estimate checked before each call. | No call goes past the budget. |
| 5.2.3 Model routing | Text model and code model; override per feature. | Each feature uses its model. |
| 5.2.4 Prompt caching | Stable prefix order (policy -> tools -> bug report -> history) for the most cache hits. | Cache hits show in usage. |
| 5.2.5 Live cost | Cost updates through the EventBus to the cost meter (#1.9.3). | The meter updates while streaming. |

## Epic 5.3 — Tutor context and tools

What the tutor knows and the read-only tools it can use.

| Story | Description | Done when |
|---|---|---|
| 5.3.1 Context builder | Bug report, failure messages from the last test run, open file and selection, conversation summary. Fits a token budget. Never the patch. | Context is logged as ids and hashes only. |
| 5.3.2 Project code tools | Through the agent (#4.3.6): list, read (line range), grep, find. Read-only, size limits. | Tool steps show in the chat. |
| 5.3.3 Symbol docs tool `guided` | Docstrings and signatures from installed libraries in the dev box (Python `inspect` / `pydoc`; TS/JS `.d.ts` + JSDoc from `node_modules`). Exact version, offline. | Answers come from the installed library version. |
| 5.3.4 Prefetch mode | For models without tools: the server preloads the open file, the failing test, and the code it calls. | Small local models still get useful context. |
| 5.3.5 Untrusted tool output `guided` | Code, comments, and docs enter the prompt marked as data, with size limits. Instructions inside files are ignored. | An injection in a learner file has no effect. |

## Epic 5.4 — Docs library

Version-matched library docs with citations.

| Story | Description | Done when |
|---|---|---|
| 5.4.1 Doc sources and detection | `docs-sources.yaml`: library -> docs URL pattern per version, license. Versions detected from lock files (uv.lock, pnpm-lock, package-lock, requirements). | Projects map to library@version. |
| 5.4.2 Doc pack builder | Job on the host (internet; never the dev box) fetches docs, converts to Markdown, chunks by heading. Stored once in `doc_chunks`, shared by projects. | A Flask pack builds and is reused. |
| 5.4.3 Docs search | Postgres full-text search (good for exact API names). | Relevant passages are found. |
| 5.4.4 Citations | Each passage has URL and heading; the chat shows links. | Every docs answer has a source. |
| 5.4.5 Embeddings and prebuilt packs - parked | pgvector with a local embedding model; published packs for common libraries after a license check. | Placeholder. |

## Epic 5.5 — Guardrails

Server-side checks so the tutor never gives the fix or the direct answer. **Needs a deep design session before build (5.5.7).**

| Story | Description | Done when |
|---|---|---|
| 5.5.7 Guardrail deep design `guided` | Dedicated design session with the owner before any guardrail code: threat model (learner tricks, prompt injection, prose leaks, multi-turn extraction), attack catalog, check methods and thresholds, false-positive budget, model differences, exam vs practice rules, eval metrics. | Design doc agreed and recorded as a decision; 5.5.1-5.5.6 updated from it. |
| 5.5.1 Versioned policy `guided` | Policy prompts in the repo, per mode and hint level. Policy version stored with each message. | Each answer traces to a policy version. |
| 5.5.2 Input check `guided` | Requests for the fix, full code, or diff, and injection patterns, get a Socratic redirect. | "Write the fix" is declined politely. |
| 5.5.3 Output check `guided` | Code blocks are held and checked: (a) similarity to the reverse patch (normalized tokens + tree-sitter AST for Python and TS); (b) project identifiers in samples (only generic samples allowed); (c) rewritten project code: a block close to a project function but changed; (d) direct answer: patch location (file, function, line) together with the changed operators or literals. | Fix-like code and direct answers never reach the learner. |
| 5.5.4 Streaming with hold-back `guided` | Prose streams with a short buffer; code blocks release only after the check. A blocked answer is regenerated once with a stricter instruction, else a safe fallback. | Streaming feels live and stays safe. |
| 5.5.5 Guardrail eval set `guided` | YAML conversations (allowed / blocked / borderline) per seed issue. CI runs the deterministic checks; a manual run against real models reports leak rate per model. | Leak rate is known for each model. |
| 5.5.6 Answer judge (optional) `guided` | Off by default. In exam mode a second, cheap LLM call asks "does this reveal the fix or the location?" before release. Catches prose leaks; uses the user's tokens. | A prose leak in the eval set is caught when the judge is on. |

## Epic 5.6 — Hint ladder and modes

Three hint levels, practice and exam modes, and no-key mode.

| Story | Description | Done when |
|---|---|---|
| 5.6.1 Hint ladder | L1: a question about the symptom or concept. L2: narrows the area. L3: explains the faulty behavior, no code. Based on author hints (#3.7.2), rephrased for the context. | Three clear levels. |
| 5.6.2 No-key mode | Without an LLM profile the hint button shows author hints word for word; chat is off. | The app works without a key. |
| 5.6.3 Practice mode | Unlimited chat and hints, all tools, standard checks. | Practice works end to end. |
| 5.6.4 Exam mode | Same tools; code allowed (exact quotes of learner code, generic samples, library examples). Strict checks: fix code, rewritten project code, and direct answers are blocked. Hint limit; each hint costs score (#6). | The tutor helps with code but never gives the fix or the location. |
| 5.6.5 Hint records | Each hint stores level, blocked or not, tokens, cost; emits `run.hint`. | Scoring and replay see every hint. |

## Epic 5.7 — Explain actions

One-click explanations from the editor, tests, and terminal.

| Story | Description | Done when |
|---|---|---|
| 5.7.1 Explain selection | Monaco right-click "Explain this" on a function, class, or library call. Uses symbol docs. | Explains `db.session.commit()` from the docs. |
| 5.7.2 Explain test failure | Button on a failed test (#1.6.2): what the test expects and what the assertion means, not the fix. | A failure is explained without the fix. |
| 5.7.3 Explain error output | Select terminal text -> the tutor explains the error message. | A traceback is explained in plain words. |

## Epic 5.8 — Conversations, privacy, and author assistant

Chat storage, log privacy, and the author-assistant endpoint.

| Story | Description | Done when |
|---|---|---|
| 5.8.1 Conversation storage | Full chats per run in the local DB for history and replay. Hosted retention is #7. | A reopened run shows its chat. |
| 5.8.2 Log privacy | Logs keep ids, token counts, and hashes only. Never message text or keys. | A redaction test passes. |
| 5.8.3 Author assistant endpoint | For #3.3.5: same LLM layer and budgets, authoring tools, no fix guard (the author creates the bug). | An author gets bug ideas and hints. |

## Order

```
5.5.7 (guardrail deep design, first) -> 5.1.1-5.1.3 -> 5.1.7 -> 5.2.1-5.2.2 -> 5.3.1-5.3.2 -> 5.5.1 -> 5.5.3-5.5.4
-> 5.6.1-5.6.3 -> 5.6.2 -> 5.3.3 -> 5.7 -> 5.2.3-5.2.5 -> 5.5.2 -> 5.5.5 -> 5.6.4-5.6.5 -> 5.5.6
-> 5.4.1-5.4.4 -> 5.3.4-5.3.5 -> 5.1.5-5.1.6 -> 5.8 -> 5.1.4 / 5.4.5 (parked)
```

**First milestone:** open a `flask-notes` run with your own key (OpenRouter or Ollama) -> ask "why does search return nothing?" -> Socratic answer with visible grep steps -> "write the fix" is declined -> hints L1 to L3 work -> the cost meter updates -> the leak eval passes.

## Decisions

- The model never sees the patch. The server uses it only for output checks.
- Guardrails get a deep design session (5.5.7) before build.
- Exam mode keeps code and tools. Strict checks block fix code, rewritten project code, and direct answers. Optional answer judge.
- No-key mode: author hints word for word.
- Docs: symbol docs from the dev box first; doc packs built locally; Postgres full-text search. Embeddings and prebuilt packs are parked.
- Code in answers: generic samples and exact quotes only.
- Chats are stored in the local DB. Logs never hold message text.
- The LLM layer lives in `api/src/cerberus/llm/` (owned by #5, used by #3).

## Log events

`tutor.ask`, `tutor.answer`, `tutor.block`, `tutor.tool.call`, `run.hint`, `llm.call`, `llm.budget.warn|stop`, `docs.pack.build|fail`
