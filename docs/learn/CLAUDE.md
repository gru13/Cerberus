# Learning index and study paths

Rules for Claude when you work in `docs/learn/` or teach from it.

## Teaching Phase 1

- Follow `path-p1.md`. Work one module at a time, in order.
- Start a module: check its prerequisites, then say which concept ids to read. Cite ids. Do not copy notes from the index.
- Run the loop: concept reads → the one exercise → check the "done when" line → the story entries in `../guided-study-guide.md` → the owner builds the stories.
- Ask a short question for each "done when" line before the owner starts a story. Do not give the answer first.
- Exercises are throwaway scripts outside the repo. Do not commit them.
- Do not start a module before its prerequisites are done.
- Do not teach the parked design issues (#394–#409).
- Report progress as modules done out of 9. Do not invent time estimates. Use the owner's measured pace.
- Stay a guide for `guided` stories: explain, review, point to docs. Do not write the implementation (see the root `CLAUDE.md`).

## Editing the index

- Official sources only, https only, on the `allowed_domains` in `index.yaml`. Notes in our own words.
- Run `uv run docs/learn/learn.py check` after every change to `index.yaml` or `concepts/`.
- Add a new path as `path-p<n>.md` and add a row to `README.md`.
