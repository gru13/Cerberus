"""Intent: Validate the learning index file and generate its Markdown pages.

Why: The YAML file is the single source of truth; the Markdown pages are generated from it.
"""

import sys
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

import yaml
from learn_models import Concept, LearnIndex, LearnIndexError, stale_warnings, validate_index
from pydantic import ValidationError

LEARN_DIR = Path(__file__).resolve().parents[2] / "docs" / "learn"
SOURCES_FILE = LEARN_DIR / "sources.yaml"
HEADER = "Generated from sources.yaml by api/scripts/learn_index.py. Do not edit by hand."
TIMEOUT_SECONDS = 10


def load_index(path: Path) -> LearnIndex:
    """Load and validate a sources file."""
    return LearnIndex.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def check_offline(path: Path) -> int:
    """Check the file offline and return the exit code.

    Functional: Fails on a bad host, a repeated id, or a missing field; warns on stale dates.
    Technical: Pydantic validates the shape; `validate_index` checks hosts and ids.
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
    Technical: Tries HEAD first, then GET; a URL or timeout error counts as a failed try.
    """
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method, headers={"User-Agent": "cerberus"})  # noqa: S310
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS):  # noqa: S310
                return True
        except (urllib.error.URLError, TimeoutError):
            continue
    return False


def check_online(path: Path) -> int:
    """Request every source URL once and return 1 when a link is dead.

    Functional: Prints each dead link and a count.
    Technical: Collects unique URLs, then calls `url_is_alive` for each one.
    """
    index = load_index(path)
    urls = sorted({s.url for c in index.concepts for s in c.sources})
    dead = [u for u in urls if not url_is_alive(u)]
    for url in dead:
        print(f"FAIL dead link {url}")
    print(f"{len(urls)} links checked, {len(dead)} dead.")
    return 1 if dead else 0


def render_concept(concept: Concept) -> str:
    """Render one concept as a Markdown section with an anchor.

    Functional: Gives each concept a citable anchor equal to its id.
    Technical: Joins notes and a source list; marks primary sources.
    """
    lines = [f'<a id="{concept.id}"></a>', f"### {concept.title}", ""]
    lines.append(f"Stories: {', '.join(concept.stories)} | Phase: {concept.phase}")
    if concept.keywords:
        lines.append(f"Keywords: {', '.join(concept.keywords)}")
    lines += ["", concept.notes.strip(), "", "Sources:"]
    for s in concept.sources:
        mark = " (primary)" if s.primary else ""
        lines.append(
            f"- [{s.title}]({s.url}){mark}: {s.publisher}, {s.version}, checked {s.checked}"
        )
    if concept.llms_txt:
        lines.append(f"- llms.txt: {concept.llms_txt}")
    return "\n".join(lines) + "\n"


def build(path: Path, out_dir: Path) -> int:
    """Write README.md and one page per area into `out_dir`.

    Functional: Builds the generated learning pages from the YAML file.
    Technical: Groups concepts by area; each page starts with the do-not-edit header.
    """
    index = load_index(path)
    by_area: dict[str, list[Concept]] = defaultdict(list)
    for concept in index.concepts:
        by_area[concept.area].append(concept)
    for area, concepts in by_area.items():
        body = [f"<!-- {HEADER} -->", f"# Learning index: {area}", ""]
        body += [render_concept(c) for c in concepts]
        (out_dir / f"{area}.md").write_text("\n".join(body), encoding="utf-8")
    readme = [
        f"<!-- {HEADER} -->",
        "# Learning index",
        "",
        "Each concept has short notes and official sources. Cite a concept as",
        "`docs/learn/<area>.md#<id>`. Source of truth: `docs/learn/sources.yaml`.",
        "",
        "Policy: official sources only, on the allowed domains in `sources.yaml`.",
        "Notes are in our own words. Run `learn: check-links` to find dead links.",
        "",
        "Areas:",
    ]
    readme += [f"- [{a}]({a}.md): {len(c)} concepts" for a, c in sorted(by_area.items())]
    (out_dir / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
    return 0


def main(argv: list[str]) -> int:
    """Run the subcommand named in argv and return its exit code.

    Functional: Gives the `check`, `check --online`, and `build` commands.
    Technical: Maps rule errors and schema errors to exit code 1; usage errors to 2.
    """
    command = argv[1] if len(argv) > 1 else ""
    try:
        if command == "check":
            return check_online(SOURCES_FILE) if "--online" in argv else check_offline(SOURCES_FILE)
        if command == "build":
            return build(SOURCES_FILE, LEARN_DIR)
    except (LearnIndexError, ValidationError) as error:
        print(f"FAIL {error}")
        return 1
    print("Usage: learn_index.py check [--online] | build")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
