"""Safety predicates for MCP tool descriptions (static, regex-driven, no LLM).

Rule IDs are stable and referenced by the conformance suite. Ported from
ToolSieve (raihan-js/toolsieve): RulesStrip._IMPERATIVES, RulesStrip._MUST_ACT,
and parse_payload evidence extraction.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

RULE_IMPERATIVE = "imperative_targeting_other_tool"
RULE_EVIDENCE = "embedded_evidence"
RULE_FREE_TEXT = "free_text_outside_field"
RULE_COERCION = "security_justification_voice"


@dataclass(frozen=True)
class Violation:
    rule: str
    match: str
    detail: str


# Model-directed imperatives (OWASP MCP03 indicators, condensed). Ported from
# ToolSieve RulesStrip._IMPERATIVES.
_IMPERATIVES = re.compile(
    r"(?i)\b(ignore (all |any |the )?previous instructions|disregard .*instructions|"
    r"do not (tell|inform|mention|reveal).*?(user|human)|"
    r"before (using|answering|replying)[^.]*(read|send|call|execute)[^.]*\.|"
    r"you must (first )?(call|run|execute|read|send|download)[^.]*\.|"
    r"this tool (must|will|should) be (executed|called|run)[^.]*\.)"
)

# Tool-targeting call: an action verb naming another (quoted) tool. Ported from
# ToolSieve parse_payload._ACTION, restricted to call/invoke/execute.
_CALL_TARGET = re.compile(
    r"""(?i)\b(?:call(?:ing)?|invok(?:e|ing)|execut(?:e|ing))\s+(['"])([^'"]{1,80})\1"""
)

# Security-justification voice: a MUST-action tied to a "regardless"/"for
# security" justification. Ported from ToolSieve RulesStrip._MUST_ACT, with the
# explicit "for security reasons" phrasing added.
_COERCION = re.compile(
    r"(?i)\byou MUST\b[^.]*(automatically )?(modify|redirect|overwrite|send|"
    r"call|read|write|execut|append|replace)[^.]*\.|"
    r"regardless of the original[^.]*\.|"
    r"for (security|compliance|safety) reasons[^.]*\.|"
    r"to (verify|confirm) (you are|your) (safe|secure|authorized|authorised)"
    r"[^.]*\.|"
    r"this involves (calling|using)\b[^.]*(overwrite|modify|redirect|send)[^.]*\."
)

_HIDDEN = re.compile("[\u200b-\u200f\u202a-\u202e\u2060\ufeff]")
_COMMENTS = re.compile(r"<!--.*?-->", re.DOTALL)

# Evidence: quoted literals that look like credentials, keys, emails, URLs, or
# paths. Ported from ToolSieve parse_payload (single-quoted, the MCPTox
# convention), extended to double quotes.
_SQUOTE = re.compile(r"'([^'\n]{1,120})'")
_DQUOTE = re.compile(r'"([^"\n]{1,120})"')
_KEY = re.compile(
    r"(?i)\b(api[_-]?key|secret|token|password|bearer|credential)s?\b|"
    r"\bsk-[a-z0-9]{8,}\b"
)


def _looks_like_evidence(s: str) -> bool:
    """Quality filter: generic words ('path', 'name') over-trigger. Keep
    strings that look like real payloads (long, or containing path/email/URL
    characters, or matching a key pattern). Ported from parse_payload."""
    if len(s) >= 8:
        return True
    if any(c in s for c in "/.@:\\"):
        return True
    return bool(_KEY.search(s))


def quoted_literals(text: str) -> list[str]:
    """Return single- or double-quoted literals in text."""
    out = _SQUOTE.findall(text) + _DQUOTE.findall(text)
    return list(dict.fromkeys(out))  # dedupe, preserve order


def detect_hidden(text: str) -> list[str]:
    return _HIDDEN.findall(text)


def detect_comments(text: str) -> list[str]:
    return _COMMENTS.findall(text)
