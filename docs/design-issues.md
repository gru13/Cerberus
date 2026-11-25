# Design issues

Open design questions found while writing `docs/guided-study-guide.md`.
Each one is a GitHub issue under Epic 0.2 (#379), assigned to gru13. The issue is the source of truth;
this file is the index. When an issue is decided, record the decision (build log and design index),
close the issue, and mark it Decided here.

| Issue | Topic | Status |
|---|---|---|
| [#394](https://github.com/gru13/Cerberus/issues/394) | Phase and dependency mismatches in the build order | Open |
| [#395](https://github.com/gru13/Cerberus/issues/395) | Merge or split duplicate stories | Open |
| [#396](https://github.com/gru13/Cerberus/issues/396) | Doc text that contradicts recorded decisions | Open |
| [#397](https://github.com/gru13/Cerberus/issues/397) | The agent's user identity inside the dev box | Open |
| [#398](https://github.com/gru13/Cerberus/issues/398) | Dev box setup under cap-drop ALL and a read-only rootfs | Open |
| [#399](https://github.com/gru13/Cerberus/issues/399) | Caddy listeners and upstream routing (dev box isolation, SSRF) | Open |
| [#400](https://github.com/gru13/Cerberus/issues/400) | Docker socket proxy must inspect request bodies | Open |
| [#401](https://github.com/gru13/Cerberus/issues/401) | Hide traces that show which files a patch changed | Open |
| [#402](https://github.com/gru13/Cerberus/issues/402) | Grading correctness rules | Open |
| [#403](https://github.com/gru13/Cerberus/issues/403) | Event ordering for resume from last event id | Open |
| [#404](https://github.com/gru13/Cerberus/issues/404) | Reconcile the run volume with the host store on recovery | Open |
| [#405](https://github.com/gru13/Cerberus/issues/405) | One glob dialect for Rust and Python | Open |
| [#406](https://github.com/gru13/Cerberus/issues/406) | Issue review in local mode | Open |
| [#407](https://github.com/gru13/Cerberus/issues/407) | MCP auth in local mode and confirmation for public actions | Open |
| [#408](https://github.com/gru13/Cerberus/issues/408) | Tutor principles | Open |
| [#409](https://github.com/gru13/Cerberus/issues/409) | Disk limit enforcement and secret.key backup | Open |

## Details

### #394 Phase and dependency mismatches in the build order

- **P-1 (4.3.3, P1) needs P6 stories.** It depends on 4.4.1, 4.4.2 (terminal route) and 8.7.4. Split those stories and move the terminal parts to P1.
- **P-2 (4.3.1, 8.4.2, 8.9.5) need the schema in P1, but 8.9.3 is P6.** Move schema creation and the Rust fixture tests to P1; leave the CI codegen in P6.
- **P-3 (4.3.1's done-when needs amd64 and arm64, but 8.10.4 is P6).** Move a local cross-build to P1.
- **P-4 (8.11.3/6.1.1 submit, P3) needs a snapshot, but 4.5.1 is P6, and 4.5.1 duplicates 8.8.1.** Make 4.5.1 "snapshot on submit plus flush" and move it to P3.
- **P-5 (KeyProvider for the P5 tutor) needs 8.7.1/8.7.2, which are P6.** Move them to P5 or earlier.
- **P-7 (3.7.x is listed "P4–P6" but needs the P5 LLM layer).** Pin 3.7 to P5 or later.

### #395 Merge or split duplicate stories

- **P-6 (4.4.4, P6) duplicates 4.6.1, P1.** Merge them.
- **4.5.2 vs 8.8.5** (both recover by fast or slow path). Merge, or set a clear split: 4.5.2 = sandbox steps, 8.8.5 = endpoint and state machine.
- **8.8.4 vs 8.5.2** (both requeue leases). Keep it in 8.5.2.

### #396 Doc text that contradicts recorded decisions

- **Doc 01 key design point 1** says the browser never talks to containers and that terminals use the one WebSocket. **8.4.1** lists a "terminal" channel. Both contradict the 2026-11-24 `terminal-direct-path` decision. Update both docs.
- **8.1.5 "API bound to 127.0.0.1"** is wrong inside compose. Change it to: "only Caddy publishes ports, on 127.0.0.1 and ::1".

### #397 The agent's user identity inside the dev box

- **The agent identity is undecided** (4.1.2/4.3.3):
  - Agent as `runner` is weak (ptrace, kill, key theft).
  - Agent as a separate uid needs CAP_SETUID/SETGID to start learner shells.
  - Decide and record it. Use per-run derived token keys.

### #398 Dev box setup under cap-drop ALL and a read-only rootfs

- **4.1.2 vs 4.2.2/4.2.3:** `--cap-drop ALL` stops root from chowning or touching others' files during prep. Add a "prep container with CHOWN/FOWNER/DAC_OVERRIDE" step to 4.2.1.
- **4.3.1 "copied in" vs 4.1.2 read-only rootfs:** inject the binary as a read-only mount, and share the socket directory through a named volume (this also fixes Docker Desktop and the host-path mismatch of api-in-container).

### #399 Caddy listeners and upstream routing (dev box isolation, SSRF)

- **4.4.1 + Caddy reachability:** the dev box can reach Caddy and, through Host spoofing, the unauthenticated local API (for example the issue diff). Serve preview and terminal from a separate Caddy listener on the internal network. Restrict the app site to the host-published listener.
- **4.4.2 SSRF:** upstreams derived from the Host header. Resolve them through forward_auth and an allow-list only.

### #400 Docker socket proxy must inspect request bodies

- **8.10.2:** a path-level socket proxy is effectively host root. Requires body inspection.

### #401 Hide traces that show which files a patch changed

- **2.2.3:** add "no copy of project sources outside the workdir", checked by hashing the image.
- **4.2.2:** inode numbers and ctimes leak which files were patched. Rewrite every file, then set mtimes, then chmod/chown everything.

### #402 Grading correctness rules

- **B-7 (8.8.1/4.6.1): deletes and renames of editable files are undefined in grading.** Add tombstones to the `run_files` manifest, and make the grader delete those files in the clean copy.
- **4.6.1/6.1.3:** a forged JUnit file plus skipped or missing tests. Grade against the baseline id set, the exit code and the count.
- **D-2 (3.5.2 vs 3.5.3):** 5 runs × 120 s is more than the 5-minute cap. Cache the baseline and skip the redundant reversed test run.
- **6.1.4:** the contract cannot rerun only failing tests, and learner-caused flakes are rewarded. Add an optional selector task, and treat learner flakes as fail.

### #403 Event ordering for resume from last event id

- **8.4.1:** "resume from last event id" is unsafe with sequence or UUIDv7 ids (commit order). Specify the ordering mechanism.

### #404 Reconcile the run volume with the host store on recovery

- **4.5.2/8.8.5:** the volume can be newer than the store. Define the reconciliation rule.

### #405 One glob dialect for Rust and Python

- **4.3.2/4.6.1:** the glob dialect differs between Rust and Python. Specify it in `protocol/` with shared fixtures.

### #406 Issue review in local mode

- **D-1 (3.10.1/3.10.2/3.6.2):** in local mode the only reviewer is the learner, and reviewing a generated bug spoils it. On-demand generation also cannot serve at once if review is required. Add a local "trust generator, hide diff" path (validated, unreviewed, flagged), or sample-only review.
- **3.8.2:** auto-activation without review contradicts "every issue is reviewed". Clarify that review applies per intent.

### #407 MCP auth in local mode and confirmation for public actions

- **3.2.5 vs 7.1.3:** local MCP auth is inconsistent. Require tokens in local mode.
- **3.9.4:** MCP `publish_issues` is a public action. Require UI confirmation.

### #408 Tutor principles

- **5.5.6:** the judge must see the patch. Amend the "model never sees the patch" principle to cover the tutor model only.
- **4.3.6/5.3.3:** `python -c help()` imports learner code (not read-only). Use griffe or static extraction, and merge the two tools.

### #409 Disk limit enforcement and secret.key backup

- **4.1.2:** the 5 GB disk limit cannot be enforced on default Docker. State how it is enforced (monitor plus stop).
- **8.7.1/8.2.5:** backup policy for `secret.key` is undecided.
