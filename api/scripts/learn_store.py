"""Intent: Keep docs/learn/sources.yaml storage in one canonical YAML form.

Why: The check, the editor, and hand edits share one file; one writer keeps diffs small.
"""

import hashlib
import os
from pathlib import Path

import yaml
from learn_models import LearnIndex

LEARN_DIR = Path(__file__).resolve().parents[2] / "docs" / "learn"
SOURCES_FILE = LEARN_DIR / "sources.yaml"


class CanonicalDumper(yaml.SafeDumper):
    """YAML dumper that writes multi-line strings as literal blocks."""


def _represent_str(dumper: yaml.SafeDumper, value: str) -> yaml.ScalarNode:
    """Write a string with `|` when it has line breaks, else in the plain style."""
    style = "|" if "\n" in value else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


CanonicalDumper.add_representer(str, _represent_str)


def load_index(path: Path) -> LearnIndex:
    """Load and validate a sources file.

    Functional: Returns the parsed index or fails on a schema or rule error.
    Technical: `yaml.safe_load`, then Pydantic validation.
    Errors: LearnIndexError (a concept rule fails), pydantic.ValidationError (bad shape).
    """
    return LearnIndex.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def dump_index(index: LearnIndex) -> str:
    """Return the index as canonical YAML text.

    Functional: Gives the same text for the same data, so saves make small diffs.
    Technical: Keeps model field order; dates stay YAML dates; notes use literal blocks.
    """
    data = index.model_dump()
    return yaml.dump(data, Dumper=CanonicalDumper, sort_keys=False, allow_unicode=True, width=1000)


def file_tag(path: Path) -> str:
    """Return a SHA-256 tag of the file bytes, used as a version tag."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_index(path: Path, index: LearnIndex) -> None:
    """Write the index to `path` in one atomic step.

    Functional: A crash during a save never leaves a half-written file.
    Technical: Writes a temporary file in the same directory, then `os.replace`.
    """
    temp = path.with_suffix(".yaml.tmp")
    temp.write_text(dump_index(index), encoding="utf-8")
    os.replace(temp, path)
