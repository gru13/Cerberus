**Level:** Initiative · **Status:** Designed

**Purpose:** Fair, reproducible results. Grade the fix from a clean copy, score it with a versioned formula, explain the breakdown, replay the run, and track progress.
**Builds on:** #4.6 (clean-copy runner, `learner` mode), #190 (queue, event store, host store, run orchestration 8.11.3), #3 (expected failures, difficulty, hints), #5 (hint records).
**Used by:** #1.8.3 (result screen), #1.8.4 (replay), #3.6.3 (difficulty), #3.10.1 (issue picking).

## Key design points

1. **Grading never trusts the dev box.** Fresh container, `--network none`, patch plus only the editable files from the host store snapshot. Read-only files come from the image; new files are ignored.
2. **Held-out tests stop gaming.** Visible tests can be special-cased. Projects can declare `grading_tests`: removed from the dev box, run only at grading.
3. **Reproducible.** Each result stores every input version. A re-grade with the same inputs gives the same score.
4. **Good habits are free.** Running tests often costs nothing. Score comes from correctness, time, hints, and change size.


## Epic 6.1 — Grading run

Grade the fix from a clean copy, with held-out tests and a flake guard.

| Story | Description | Done when |
|---|---|---|
| 6.1.1 Grading job | Submit -> queue job -> clean-copy runner in `learner` mode (#4.6) with the host store snapshot -> JUnit -> result. Idempotent per snapshot hash. | A submit gives a graded result. |
| 6.1.2 Grading tests (held-out) `guided` | `project.yaml` `grading_tests` (optional patterns). Removed from the dev box at prepare (#4.2.2); present only in clean-copy runs. Results show counts, not names. | A hardcoded fix fails the held-out tests. |
| 6.1.3 Pass rules `guided` | Full suite passes: expected failures now pass, no test that passed before now fails, `<error>` counts as a fail. | Rules apply per issue. |
| 6.1.4 Flake guard `guided` | Failing tests run once more. Different results -> mark flaky, no penalty, flag the issue or project. | A flaky test never costs the learner. |
| 6.1.5 Practice check | "Check my fix" in practice runs the same grading without submit. | The learner sees if the fix holds, held-out tests included. |

## Epic 6.2 — Score formula

Versioned formula: correctness, time, hints, change size.

| Story | Description | Done when |
|---|---|---|
| 6.2.1 Formula v1 | 100 points: correctness 60, time 15, hints 15, change size 10. Stored as `scoring_version`. | The breakdown adds up to the total. |
| 6.2.2 Partial credit | Not all pass: share of expected failures fixed, minus regressions, max 40. Multi-issue runs weighted by difficulty (multi-issue runs come later). | Partial fixes get fair partial points. |
| 6.2.3 Time | Target time per difficulty (e.g. d1 10 min to d5 60 min). Full points up to target, 0 at 3x target. Idle (> 5 min) and interrupted time excluded, from events. | A crash or a break costs no points. |
| 6.2.4 Hints | Cost per level (e.g. L1 -3, L2 -5, L3 -7). Explain actions and docs questions are free. | Hint cost matches the ladder (#1.9.4). |
| 6.2.5 Change size | Learner diff against the reverse patch size, whitespace and formatting ignored. Up to 2x: full points; large rewrites lose some. | A one-line fix is not beaten by a rewrite. |
| 6.2.6 Fix type | Revert-equivalent or alternative fix (tests pass, code differs). Shown, never penalized. Alternative fixes go to the author. | An alternative fix gets the same score. |

## Epic 6.3 — Results and reproducibility

Self-describing results and deterministic re-grades.

| Story | Description | Done when |
|---|---|---|
| 6.3.1 Result record | Breakdown, test results, flags, and all input versions: project SHA, image digest, issue version, runner, agent, policy, formula, snapshot hash. | A result describes itself fully. |
| 6.3.2 Re-grade | `cerberus regrade <run>`. Same inputs give the same score. A new formula adds a new result row; the old row stays. | Re-grade is deterministic. |
| 6.3.3 Result API | For #1.8.3: breakdown, files changed (learner diff), original diff, issue origin. | The result screen loads from one call. |
| 6.3.4 Score events | `run.score` with the triple, as in CLAUDE.md. | Logged. |

## Epic 6.4 — Replay

Replay a run step by step, with the code at each moment.

| Story | Description | Done when |
|---|---|---|
| 6.4.1 Timeline API | Ordered events: edits, test runs, hints, tasks, terminal commands. | #1.8.4 shows the timeline. |
| 6.4.2 Code at any moment | File versions from the host store manifest; the scrubber shows the code at that time. | The learner sees the full debugging path. |
| 6.4.3 Replay export | Run bundle as JSON (no secrets) for sharing or review. | Export then import shows the same replay. |

## Epic 6.5 — Progress and analytics

Personal stats, skill profile, difficulty calibration, and issue quality.

| Story | Description | Done when |
|---|---|---|
| 6.5.1 Personal stats | Solved count, average score and time, by category and difficulty, history chart. | A stats page exists. |
| 6.5.2 Skill profile | Rating per category (Elo-style against issue difficulty). Exam scores count fully, practice with less weight. Feeds issue picking (#3.10.1). | The next issue fits the learner level. |
| 6.5.3 Difficulty calibration | Solve rate, median time, and hints give each issue version a calibrated difficulty (#3.6.3) after enough runs. | Difficulty follows real data. |
| 6.5.4 Issue quality flags | Issues that nobody solves, everyone solves at once, or that are flaky go to review. | Bad issues show up without manual search. |

## Epic 6.6 — Integrity

Hardcode check now; exam integrity and leaderboards for hosted mode.

| Story | Description | Done when |
|---|---|---|
| 6.6.1 Hardcode check | Literals from test files that appear new in the learner diff -> warning flag on the result. No penalty in v1. | Special-casing is flagged. |
| 6.6.2 Exam integrity - parked | Hosted (#7): paste volume, focus loss, proctoring signals. | Placeholder. |
| 6.6.3 Leaderboards and exam reports - parked | Hosted (#7): groups, rankings, admin dashboards. | Placeholder. |

## Order

```
6.1.1 -> 6.1.3 -> 6.2.1 -> 6.3.1 -> 6.3.3 -> 6.3.4   (first graded result)
-> 6.2.3-6.2.5 -> 6.1.4 -> 6.1.5 -> 6.2.2 -> 6.2.6 -> 6.1.2 -> 6.6.1
-> 6.4.1-6.4.2 -> 6.3.2 -> 6.5.1 -> 6.5.4 -> 6.5.2-6.5.3 -> 6.4.3 -> 6.6.2-6.6.3 (parked)
```

**First milestone:** fix the `flask-notes` bug and submit -> clean-copy grading passes -> the result screen shows 60 / 15 / 15 / 10 with time and hints -> a re-grade gives the same score.

## Decisions

- Optional held-out `grading_tests` per project (#2 contract, #4 prepare).
- Formula v1: correctness 60, time 15, hints 15, change size 10. Versioned.
- Practice shows a score labeled "practice"; it counts less in the skill profile.
- Test runs are never penalized. Alternative fixes get the same score.
- Idle (> 5 min) and interrupted time do not count.
- Hardcode check flags only in v1.
- One issue per run in v1. Multi-issue runs come later.

## Log events

`grade.start`, `grade.end`, `grade.flaky`, `run.score`, `score.regrade`, `issue.flag`
