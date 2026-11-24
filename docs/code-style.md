# Code style

Mandatory for all code in this repository (`api/`, `agent/`, `web/`). The checks in
`api/scripts/style_check.py`, ruff, ty, and clippy enforce most rules. Agents and people read code
the same way: header first, body only when needed.

## 1. Signatures

Every function has a full signature: a type on every parameter and on the return value.

| Language | Rule | Check |
|---|---|---|
| Python | Full type hints, including `-> None` | ruff `ANN`, `ty check` |
| Rust | Types are required by the language; public items need `///` docs | `missing_docs` lint |
| TypeScript | `strict` mode; explicit return types on exported functions | tsconfig `strict`, ESLint |

## 2. Function header

Every function starts with a header in a fixed shape:

1. **Summary line**: one sentence, imperative, ends with a period.
2. **Tags**, each on its own line, always starting with the same word.

| Tag | Required | Says |
|---|---|---|
| Summary line | Every function | What it does |
| `Functional:` | Every function longer than 3 lines | Behavior as the caller sees it |
| `Technical:` | Every function longer than 3 lines | How: algorithm, syscalls, complexity, key libraries |
| `Limits:` | When a bound exists | Max sizes, counts, timeouts, retries |
| `Errors:` | When it can fail | Each error class and when it happens |
| `Invariants:` | Optional | What is true before and after |
| `Why:` | Optional | Why a non-obvious choice was made |
| `Perf:` | Hot paths | Back-of-the-envelope cost (network, disk, memory, CPU) |

Functions of 3 lines or fewer need only the summary line. Test functions need only typed
signatures; the test name is the summary.

Python:

```python
def apply_patch(workspace: Path, patch: Patch) -> ApplyResult:
    """Apply one issue patch to a run workspace, in order.

    Functional: Fails the session with a clear reason if any hunk is rejected.
    Technical: Runs `patch -p1 --forward` as root via docker exec; O(hunks).
    Limits: Patch <= 3 files, <= 30 lines; exec timeout 10 s.
    Errors: PatchRejectedError (a hunk fails), SessionGoneError (container stopped).
    """
```

Rust:

```rust
/// Apply one issue patch to a run workspace, in order.
///
/// Functional: Fails the session with a clear reason if any hunk is rejected.
/// Technical: Runs `patch -p1 --forward`; O(hunks).
/// Errors: `PatchError::Rejected`, `PatchError::SessionGone`.
pub fn apply_patch(workspace: &Path, patch: &Patch) -> Result<ApplyResult, PatchError> {
```

TypeScript uses the same tags inside `/** ... */`.

## 3. One intent per file

- The first line of every file states its intent: Python module docstring `"""Intent: ..."""`,
  Rust `//! Intent: ...`, TypeScript `/** Intent: ... */`.
- If the intent needs "and", split the file.
- Size flags (soft):

| Flag | Trigger | Result |
|---|---|---|
| Size warning | More than 200 lines | Warning: consider a split |
| Size limit | More than 300 lines | Failure, unless the file header has `Why: <reason it stays one file>` |
| Intent | The Intent line contains " and ", or the file is named `utils`, `helpers`, `misc`, `common` | Warning |
| Breadth | More than 12 functions in one file | Warning |
| Mixed layers | One file has both HTTP routes and database queries | Warning: routes in `router.py`, queries in `service.py` / `models.py` |

- Functions have a hard limit of **70 lines**.

## 4. Data: Pydantic (Python)

- All structured data is a Pydantic v2 model: request and response bodies, config, events, job
  payloads, agent protocol messages, LLM inputs and outputs. No raw `dict` or `TypedDict` crosses
  a function or module boundary.
- Default config: `model_config = ConfigDict(extra="forbid", frozen=True)`. Relax it only with a
  `Why:` line.
- Settings use `pydantic-settings`. Agent protocol models are generated from
  `protocol/agent.v1.schema.json`.
- SQLAlchemy models stay separate. Convert between SQLAlchemy and Pydantic only in `service.py`.

## 5. Errors

Python:

- Every error is a subclass of `cerberus.errors.CerberusError`. Each subclass sets a fixed `code`
  (dotted, e.g. `sandbox.patch.rejected`), a fixed STE100 `message`, and an `http_status`.
  Variable data goes in `details`, never in the message.
- Each module keeps its errors in its own `errors.py`.
- Never raise a built-in exception (`Exception`, `ValueError`, `RuntimeError`, ...) from `src/`.
- Catch narrowly. No `except Exception:` and no `except: pass`. Only boundary code (CLI entry,
  request middleware, job runner) may catch broadly, with `# noqa: BLE001` and a `Why:` comment.
- Keep the cause: `raise PatchRejectedError(details=...) from exc`.
- List every raised error in the function's `Errors:` tag.
- Never put secrets, keys, tokens, or full user code in an error or its details.
- The API maps `CerberusError` to problem+json with its `code` (story 8.1.3).

Rust:

- `thiserror` enums per module; `anyhow` only at the binary edge.
- No `unwrap()`, `expect()`, or `panic!` outside tests (clippy `unwrap_used`, `expect_used`).

## 6. Rules from TigerStyle

Adapted from [TigerStyle](https://github.com/tigerbeetle/tigerbeetle/blob/main/docs/TIGER_STYLE.md)
(TigerBeetle's style guide, read 2026-11-25). Summaries are in our own words.

| Rule | How we apply it |
|---|---|
| Hard limit of 70 lines per function | Checked by `style_check.py` and clippy `too_many_lines` |
| Assert arguments, return values, pre/postconditions, invariants; average at least two assertions per function | Rust: `assert!` / `debug_assert!`. Python: explicit checks that raise a `CerberusError` (plain `assert` disappears under `-O`); `assert` only in tests |
| Split compound assertions; assert what you expect and what you do not expect | One condition per check; check both valid and invalid cases |
| Put a limit on everything | Every loop, queue, retry, timeout, and size has a bound, written in `Limits:` |
| Simple, explicit control flow; no recursion | No recursion in the agent; split compound conditions; state invariants positively |
| Always say why; comments are full sentences | Capital letter and full stop; `Why:` for non-obvious choices |
| Do not abbreviate; units and qualifiers go last | `timeout_ms`, `latency_ms_max`, `retry_count_max` |
| Hard limit of 100 columns | ruff `line-length = 100`; rustfmt `max_width = 100` |
| Zero technical debt | Every `TODO` names an issue: `TODO(#123): ...` |
| Back-of-the-envelope performance sketches | `Perf:` tag on hot paths (relay, PTY, host store) |
| Few dependencies | Add a dependency only with a reason in the PR; prefer the standard library |

Not adopted (Zig-specific): static memory allocation after startup, comptime assertions.

## 7. Reading code with `rg` (for agents)

```bash
rg -m1 -n 'Intent:' api agent web                      # map of every file's intent
rg -n -A6 'def apply_patch|fn apply_patch' api agent   # one function: signature and header only
rg -n '^\s*(Functional|Technical|Limits|Errors):' api  # all headers in an area
```

Task `repo: outline` prints every file's intent and every function's summary line.
