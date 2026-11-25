"""Intent: Check the learning index file offline and, on request, check its links online.

Why: The YAML file is the single source of truth; there are no generated pages.
"""

import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

from learn_models import LearnIndexError, concept_urls, stale_warnings, validate_index
from learn_store import SOURCES_FILE, load_index
from pydantic import ValidationError

TIMEOUT_SECONDS = 10
USAGE = "Usage: learn_index.py check [--online]"


def check_offline(path: Path) -> int:
    """Check the file offline and return the exit code.

    Functional: Fails on a bad host, a non-https link, a repeated id, or a missing field.
        Warns on stale dates.
    Technical: Pydantic validates the shape; `validate_index` checks links and ids.
    """
    try:
        index = load_index(path)
    except (LearnIndexError, ValidationError) as error:
        print(f"FAIL {error}")
        return 1
    for warning in stale_warnings(index, datetime.now(UTC).date()):
        print(f"WARN {warning}")
    problems = validate_index(index)
    for problem in problems:
        print(f"FAIL {problem}")
    print(f"{len(index.concepts)} concepts checked.")
    return 1 if problems else 0


def url_is_alive(url: str) -> bool:
    """Return True when the URL answers HEAD or GET without an error.

    Functional: Tells the link check whether one source link works.
    Technical: Tries HEAD first, then GET. A URL error, a timeout, or a malformed URL
        counts as a failed try.
    Limits: 10 s timeout per request; at most 2 requests per URL.
    """
    for method in ("HEAD", "GET"):
        try:
            request = urllib.request.Request(  # noqa: S310
                url, method=method, headers={"User-Agent": "cerberus"}
            )
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS):  # noqa: S310
                return True
        except (urllib.error.URLError, TimeoutError, ValueError):
            continue
    return False


def check_online(path: Path) -> int:
    """Run the offline check, then request every source and llms.txt URL once.

    Functional: Stops before any request when the offline check fails.
        Prints each dead link and a count.
    Technical: Collects unique URLs from `concept_urls`, then calls `url_is_alive`.
    """
    if check_offline(path) != 0:
        return 1
    index = load_index(path)
    urls = sorted({u for c in index.concepts for u in concept_urls(c)})
    dead = [u for u in urls if not url_is_alive(u)]
    for url in dead:
        print(f"FAIL dead link {url}")
    print(f"{len(urls)} links checked, {len(dead)} dead.")
    return 1 if dead else 0


def main(argv: list[str], path: Path = SOURCES_FILE) -> int:
    """Run the subcommand named in argv and return its exit code.

    Functional: Gives the `check` and `check --online` commands.
    Technical: Exit code 1 for a rule or link failure; 2 for a usage error.
    """
    args = argv[1:]
    if args == ["check"]:
        return check_offline(path)
    if args == ["check", "--online"]:
        return check_online(path)
    print(USAGE)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
