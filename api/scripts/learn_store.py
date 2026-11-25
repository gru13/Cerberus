"""Intent: Keep the learning index storage (one settings file, one file per area) canonical.

Why: Per-area files keep reviews small; one reader and one writer keep every tool in step.
Layout: docs/learn/index.yaml holds the settings; docs/learn/concepts/<area>.yaml holds a
    list of concepts. The area comes from the file name, so concept entries have no `area` key.
"""

import hashlib
import os
from pathlib import Path
from typing import Any, get_args

import yaml
from learn_models import Area, LearnIndex, LearnIndexError

LEARN_DIR = Path(__file__).resolve().parents[2] / "docs" / "learn"
SETTINGS_NAME = "index.yaml"
CONCEPTS_DIR = "concepts"
AREAS: tuple[str, ...] = get_args(Area.__value__)

type YamlData = Any


class CanonicalDumper(yaml.SafeDumper):
    """YAML dumper that writes multi-line strings as literal blocks."""


def _represent_str(dumper: yaml.SafeDumper, value: str) -> yaml.ScalarNode:
    """Write a string with `|` when it has line breaks, else in the plain style."""
    style = "|" if "\n" in value else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


CanonicalDumper.add_representer(str, _represent_str)


def _read_yaml(path: Path) -> YamlData:
    """Parse one YAML file with the safe loader."""
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _to_yaml(data: YamlData) -> str:
    """Return data as canonical YAML text."""
    return yaml.dump(data, Dumper=CanonicalDumper, sort_keys=False, allow_unicode=True, width=1000)


def _area_concepts(path: Path, area: str) -> list[YamlData]:
    """Read one area file and add the area from its file name to each concept.

    Functional: Fails when an entry also states an area, so the two cannot disagree.
    Technical: Expects a YAML list of mappings; an empty file counts as no concepts.
    Errors: LearnIndexError (an entry has an `area` key or the file is not a list).
    """
    entries = _read_yaml(path) or []
    if not isinstance(entries, list):
        raise LearnIndexError(details={"file": path.name, "rule": "list-of-concepts"})
    concepts = []
    for entry in entries:
        if isinstance(entry, dict) and "area" in entry:
            raise LearnIndexError(details={"file": path.name, "rule": "area-from-file-name"})
        concepts.append({**entry, "area": area} if isinstance(entry, dict) else entry)
    return concepts


def load_index(learn_dir: Path) -> LearnIndex:
    """Load the settings file and every area file, then validate them as one index.

    Functional: Returns the whole index, or fails on a file, schema, or concept rule error.
    Technical: Reads index.yaml, then concepts/<area>.yaml in area order; Pydantic validates.
    Errors: LearnIndexError (unknown area file, bad file shape, concept rule),
        pydantic.ValidationError (bad shape).
    """
    data = _read_yaml(learn_dir / SETTINGS_NAME) or {}
    if not isinstance(data, dict) or "concepts" in data:
        raise LearnIndexError(details={"file": SETTINGS_NAME, "rule": "settings-only"})
    files = {p.stem: p for p in (learn_dir / CONCEPTS_DIR).glob("*.yaml")}
    unknown = sorted(set(files) - set(AREAS))
    if unknown:
        raise LearnIndexError(details={"file": f"{unknown[0]}.yaml", "rule": "unknown-area"})
    concepts = [c for area in AREAS if area in files for c in _area_concepts(files[area], area)]
    return LearnIndex.model_validate({**data, "concepts": concepts})


def dump_index(index: LearnIndex) -> dict[str, str]:
    """Return the canonical text of every file, keyed by path relative to the learn dir.

    Functional: Gives the same text for the same data, so saves make small diffs.
    Technical: Keeps model field order and concept order; drops `area` from concept entries;
        an area without concepts gets no file.
    """
    data = index.model_dump()
    concepts = data.pop("concepts")
    files = {SETTINGS_NAME: _to_yaml(data)}
    for area in AREAS:
        entries = [
            {k: v for k, v in c.items() if k != "area"} for c in concepts if c["area"] == area
        ]
        if entries:
            files[f"{CONCEPTS_DIR}/{area}.yaml"] = _to_yaml(entries)
    return files


def index_tag(learn_dir: Path) -> str:
    """Return a SHA-256 tag over the names and bytes of every index file.

    Functional: Changes when any index file is added, removed, or edited.
    Technical: Hashes index.yaml and concepts/*.yaml in sorted path order.
    """
    digest = hashlib.sha256()
    paths = [learn_dir / SETTINGS_NAME, *sorted((learn_dir / CONCEPTS_DIR).glob("*.yaml"))]
    for path in paths:
        if path.exists():
            digest.update(str(path.relative_to(learn_dir)).encode() + b"\0" + path.read_bytes())
    return digest.hexdigest()


def save_index(learn_dir: Path, index: LearnIndex) -> None:
    """Write every index file and remove area files that have no concepts now.

    Functional: A crash never leaves a half-written file; each file is replaced whole.
    Technical: Writes a temporary file next to each target, then `os.replace`.
    Limits: Files are replaced one by one, not as one transaction across files.
    """
    files = dump_index(index)
    (learn_dir / CONCEPTS_DIR).mkdir(exist_ok=True)
    for rel, text in files.items():
        target = learn_dir / rel
        temp = target.with_suffix(".yaml.tmp")
        temp.write_text(text, encoding="utf-8")
        os.replace(temp, target)
    for area in AREAS:
        path = learn_dir / CONCEPTS_DIR / f"{area}.yaml"
        if f"{CONCEPTS_DIR}/{area}.yaml" not in files and path.exists():
            path.unlink()
