**Level:** Initiative (split into epics, then stories)

**Purpose:** Fair, reproducible results.

### Scope
- **Primary:** hidden tests pass (including HTTP checks), no regressions.
- **Secondary:** time, hints used, diff size compared with the reverse patch, test runs before submit.
- **Reproducible:** each result stores image version, patch versions, test suite version, policy version.
- **Report:** score breakdown and replay of run events (edits, tests, hints).
- **Timing:** practice = instant feedback. Exam = after submit.

### Open questions
- Formula and weights.
- Partial credit when a run has several issues.
