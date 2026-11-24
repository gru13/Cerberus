# Cerberus API

FastAPI backend for Cerberus (initiative 8, #190). Python 3.13, managed with [uv](https://docs.astral.sh/uv/).

## Commands

```bash
uv sync                      # install dependencies
uv run cerberus doctor       # check this machine
uv run cerberus api --reload # start the API on http://127.0.0.1:8000
```

`cerberus worker` and `cerberus migrate` are placeholders until stories 8.5.1 and 8.2.3.

## Checks (same as CI)

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest
```
