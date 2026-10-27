# ToolSurface — normative specification

Version 0.1 · 2026-10-27 · status: draft

ToolSurface governs the **content of the MCP `description` field** and nothing
else. It does not re-specify `name`, `inputSchema`, `annotations`, or transport.

## 1. Canonical schema

A conformant description is a JSON object containing **only** these fields.
No free prose may appear outside a field. The machine-readable form is
`schema.json`.

| Field | Required | Type | Constraint |
|-------|----------|------|------------|
| `purpose` | yes | string ≤ 500 | One factual sentence. Must not name or instruct another tool. |
| `params` | no | string ≤ 500 | Summary that references `inputSchema`; never restates it. |
| `returns` | no | string ≤ 500 | What the tool returns. |
| `side_effects` | no | enum | `read_only` \| `write` \| `network` \| `mixed` |
| `examples` | no | array ≤ 5 | Real input/output pairs; no instructions inside them. |

A description that cannot be represented in this shape is **non-conformant**
and must be canonicalised or rejected, never passed through.

## 2. Safety predicates

A description is non-conformant if it matches any of:

1. **`imperative_targeting_other_tool`** — imperative instructions to call,
   use, invoke, or execute another tool, or to ignore prior instructions.
2. **`embedded_evidence`** — quoted literals that look like credentials, keys,
   emails, URLs, or absolute paths used to direct an exfiltration call.
3. **`free_text_outside_field`** — prose that is not inside one of the five
   schema fields (enforced structurally by `schema.json`).
4. **`security_justification_voice`** — coercion phrased as a security or
   compliance requirement ("for security reasons", "you MUST … regardless of
   the original request").

Predicates are static and regex-driven. No LLM is required to check
conformance; an LLM is only an optional aid for canonicalising.

## 3. Reference implementation

Python package `toolsurface`:

- `validate(description: str) -> list[Violation]` — applies predicates 1, 2, 4.
- `validate_structured(obj: dict) -> list[Violation]` — applies predicate 3.
- `canonicalise(description: str) -> CanonicalResult` — strips hidden
  characters, HTML-comment-smuggled text, and imperative/coercion sentences,
  then classifies the result `conformant | canonicalised | non_conformant`.

## 4. Conformance suite

A producer proves conformance by running, with third-party-runnable output:

1. **Retention test** — over a clean corpus, the fraction of descriptions whose
   semantic content survives canonicalisation must meet a stated threshold.
2. **Poisoning benchmark** — over the frozen 1,312-instance MCPTox set
   (367-item frozen subset), report ASR and UCC with Wilson 95% CIs,
   rule-scored, no LLM judge. A conformant canonicaliser must reduce ASR
   versus the dateless baseline.

## 5. Relationship to ToolSieve

[ToolSieve](https://github.com/raihan-js/toolsieve) (shipped 2026-10-26)
measured the attack: dateless free-text descriptions drive 13.8% attack
success; canonicalising cuts it to 7.8% (367 frozen items, rule-scored,
Wilson CIs). ToolSurface is that finding promoted to a normative standard.
ToolSieve remains the benchmark artifact; ToolSurface is the standard,
reference implementation, and conformance suite.

## 6. License

Specification text and `schema.json`: Community Specification License 1.0.
Reference implementation, conformance suite, and examples: Apache-2.0.
