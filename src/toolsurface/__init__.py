"""ToolSurface — a normative standard for safe MCP tool descriptions.

Public API:
- validate(description) -> list[Violation]
- validate_structured(obj) -> list[Violation]
- canonicalise(description) -> CanonicalResult
"""

from __future__ import annotations

from .canonicalise import CanonicalResult, canonicalise
from .predicates import (
    RULE_COERCION,
    RULE_EVIDENCE,
    RULE_FREE_TEXT,
    RULE_IMPERATIVE,
    Violation,
)
from .validate import validate, validate_structured

__all__ = [
    "CanonicalResult",
    "RULE_COERCION",
    "RULE_EVIDENCE",
    "RULE_FREE_TEXT",
    "RULE_IMPERATIVE",
    "Violation",
    "canonicalise",
    "validate",
    "validate_structured",
]

__version__ = "0.1.0"
