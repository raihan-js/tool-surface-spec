"""validate: apply the safety predicates to a description (no LLM)."""

from __future__ import annotations

from typing import Any

from .predicates import (
    RULE_COERCION,
    RULE_EVIDENCE,
    RULE_FREE_TEXT,
    RULE_IMPERATIVE,
    Violation,
    _CALL_TARGET,
    _COERCION,
    _IMPERATIVES,
    _looks_like_evidence,
    quoted_literals,
)

# The five fields of the canonical schema (see spec.md / schema.json).
_FIELDS = {"purpose", "params", "returns", "side_effects", "examples"}


def validate(description: str) -> list[Violation]:
    """Apply the text-level predicates (imperative, evidence, coercion).

    Predicate free_text_outside_field is structural and is applied by
    validate_structured() against schema.json, not here.
    """
    violations: list[Violation] = []
    for m in _IMPERATIVES.finditer(description):
        violations.append(
            Violation(RULE_IMPERATIVE, m.group(0), "tool-targeting imperative")
        )
    for m in _CALL_TARGET.finditer(description):
        violations.append(
            Violation(RULE_IMPERATIVE, m.group(0), "call targeting another tool")
        )
    for m in _COERCION.finditer(description):
        violations.append(
            Violation(RULE_COERCION, m.group(0), "security-justification coercion")
        )
    for lit in quoted_literals(description):
        if _looks_like_evidence(lit):
            violations.append(
                Violation(RULE_EVIDENCE, lit, "embedded credential/path evidence")
            )
    return violations


def validate_structured(obj: Any) -> list[Violation]:
    """Apply predicate free_text_outside_field: the object must be a dict with
    only the five canonical fields."""
    if not isinstance(obj, dict):
        return [
            Violation(RULE_FREE_TEXT, repr(obj)[:80], "description is not a JSON object")
        ]
    extra = sorted(set(obj) - _FIELDS)
    if extra:
        return [
            Violation(
                RULE_FREE_TEXT,
                ", ".join(extra),
                "free-text field outside the canonical schema",
            )
        ]
    return []
