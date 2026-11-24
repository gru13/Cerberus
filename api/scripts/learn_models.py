"""Intent: Define the Pydantic models for docs/learn/sources.yaml.

Why: One schema keeps the learning index valid for the check, the build, and the tests.
"""

from datetime import date
from typing import ClassVar, Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, model_validator

from cerberus.errors import CerberusError

type SourceKind = Literal["official-docs", "api-reference", "man-page", "spec", "project-repo"]
type Area = Literal["sandbox", "realtime", "persistence", "security", "protocol", "build"]


class LearnIndexError(CerberusError):
    """The learning index file breaks a rule."""

    code: ClassVar[str] = "learn.index.invalid"
    message: ClassVar[str] = "The learning index file breaks a rule."


class Source(BaseModel):
    """One official source for a concept."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    url: str
    title: str
    kind: SourceKind
    publisher: str
    version: str
    primary: bool = False
    checked: date


class Concept(BaseModel):
    """One concept that a guided story needs, with notes and sources."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    title: str
    area: Area
    stories: list[str]
    phase: str
    keywords: list[str] = []
    notes: str
    sources: list[Source]
    llms_txt: str | None = None

    @model_validator(mode="after")
    def check_concept(self) -> "Concept":
        """Require a matching id prefix and at least one primary source.

        Functional: Rejects a concept in the wrong area or without a primary source.
        Technical: Pydantic runs this after field checks; it raises `LearnIndexError`.
        """
        if not self.id.startswith(f"{self.area}."):
            raise LearnIndexError(details={"id": self.id})
        if not any(s.primary for s in self.sources):
            raise LearnIndexError(details={"id": self.id, "rule": "primary-source"})
        return self


class LearnIndex(BaseModel):
    """The whole sources.yaml file."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    version: int
    stale_after_days: int
    allowed_domains: list[str]
    concepts: list[Concept]


def host_of(url: str) -> str:
    """Return the host name of a URL."""
    return urlparse(url).hostname or ""


def validate_index(index: LearnIndex) -> list[str]:
    """Return rule violations: repeated ids and hosts outside the allowed list.

    Functional: Lists every problem so a person can fix them in one pass.
    Technical: Compares each source host with `allowed_domains`; counts ids.
    """
    problems: list[str] = []
    seen: set[str] = set()
    allowed = set(index.allowed_domains)
    for concept in index.concepts:
        if concept.id in seen:
            problems.append(f"{concept.id}: id repeats")
        seen.add(concept.id)
        urls = [s.url for s in concept.sources] + ([concept.llms_txt] if concept.llms_txt else [])
        problems.extend(
            f"{concept.id}: host {host_of(u)} is not allowed"
            for u in urls
            if host_of(u) not in allowed
        )
    return problems


def stale_warnings(index: LearnIndex, today: date) -> list[str]:
    """Return a warning for each source that was checked too long ago.

    Functional: Shows which sources need a new check.
    Technical: Compares `today` with each `checked` date and `stale_after_days`.
    """
    limit = index.stale_after_days
    return [
        f"{c.id}: source {s.url} is stale"
        for c in index.concepts
        for s in c.sources
        if (today - s.checked).days > limit
    ]
