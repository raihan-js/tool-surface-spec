"""canonicalise: produce a safe description by stripping hidden text and
imperative/coercion sentences. Deterministic, no LLM.

Classification:
- conformant: no violations in the input.
- canonicalised: input had violations, all removed by stripping.
- non_conformant: violations remain after stripping (e.g. bare evidence that
  does not travel with an imperative sentence).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .predicates import (
    Violation,
    _CALL_TARGET,
    _COERCION,
    _COMMENTS,
    _HIDDEN,
    _IMPERATIVES,
)
from .validate import validate


@dataclass(frozen=True)
class CanonicalResult:
    description: str
    classification: str  # "conformant" | "canonicalised" | "non_conformant"
    violations: tuple[Violation, ...]


_SENTENCE = re.compile(r"(?<=[.!?]) ")


def canonicalise(description: str) -> CanonicalResult:
    original = validate(description)

    # Hidden characters and HTML-comment smuggling are stripped unconditionally;
    # they are not safety predicates but defeat the regex predicates, so they are
    # removed before any classification.
    cleaned = _HIDDEN.sub("", description)
    cleaned = _COMMENTS.sub("", cleaned)

    if not original and cleaned == description:
        return CanonicalResult(description, "conformant", ())

    kept = [
        s for s in _SENTENCE.split(cleaned)
        if not _IMPERATIVES.search(s)
        and not _CALL_TARGET.search(s)
        and not _COERCION.search(s)
    ]
    cleaned = " ".join(kept).strip()

    remaining = validate(cleaned)
    if remaining:
        return CanonicalResult(cleaned, "non_conformant", tuple(remaining))
    return CanonicalResult(cleaned, "canonicalised", tuple(original))
