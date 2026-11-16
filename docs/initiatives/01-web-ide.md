**Level:** Initiative (split into epics, then stories)

**Purpose:** Where the user reads the bug report, edits code, runs the app, and submits.
**Stack:** Next.js + Monaco + xterm.js

### Scope
- **Editor:** file tree, tabs, Monaco. Shows editable files only. Hidden tests never reach the browser.
- **Bug report panel:** one report per issue in the run (expected vs actual, steps to reproduce, stack trace).
- **Terminal:** shell in the sandbox over WebSocket.
- **Run panel:** run the user's own tests. Practice: "Check fix" shows pass/fail counts only. Exam: hidden until submit.
- **App preview:** "Run app" button, built-in preview (sandboxed iframe) with reload and address bar, open in new tab, server output panel.
- **Tutor chat:** streaming replies, doc citations.
- **Session:** timer, submit, result screen with score breakdown.
- **Settings:** LLM provider profiles, mode (practice/exam), theme.

### Depends on
Sandbox runner, AI tutor, Scoring, Users & accounts.

### Open questions
- Autosave or manual save?
- Mobile view (read-only?)
