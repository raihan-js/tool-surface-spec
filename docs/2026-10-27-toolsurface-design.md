# ToolSurface — Design & Normative Spec

Status: draft v0.1 · 2026-10-27 · Author: Raihan Sikder

## 1. Identity

- **Name**: ToolSurface
- **Repo**: `raihan-js/tool-surface-spec` (spec + JSON Schema + conformance suite + Python reference implementation)
- **Origin**: `raihan-js/toolsieve` is the originating benchmark and stays a separate, cited artifact.
- **License**: specification text and schema under **Community Specification License 1.0** (matching MCP/TRACE); all code under **Apache-2.0**.

## 2. Scope

ToolSurface governs **only the content of the MCP `description` field** (the free-text
description of a tool). It does not re-specify `name`, `inputSchema` (MCP JSON Schema
already governs that), `annotations`, or transport. Non-goals, stated plainly:

- It does not define or change the MCP wire protocol.
- It does not replace runtime policy enforcement (authz, allowlists, sandboxes).
- It does not score tool *correctness*; it scores description *safety and structure*.

## 3. Canonical schema

A conformant description is a JSON object containing **only** the following fields.
No free prose may appear outside a field.

| Field | Required | Type | Constraint |
|-------|----------|------|------------|
| `purpose` | yes | string | One factual sentence. Must not name or instruct another tool. |
| `params` | no | string | Plain-language summary that references the `inputSchema`; must not restate it. |
| `returns` | no | string | What the tool returns. |
| `side_effects` | no | enum | `read_only` \| `write` \| `network` \| `mixed`. |
| `examples` | no | array | Bounded list of real input/output pairs. No instructions inside them. |

A description that cannot be represented in this shape is **non-conformant** and must
be either canonicalised (rewritten into the shape) or rejected, not passed through.

## 4. Safety predicates

A description is **non-conformant** if it matches any of:

1. **Tool-targeting imperative** — `call/use/invoke/execute X`, `before using X…`,
   `when answering use X…` where `X` is another tool. (Formalises ToolSieve's
   `_IMPERATIVES` regex.)
2. **Embedded evidence** — quoted literals that look like credentials, keys, emails,
   URLs, or absolute paths used to instruct an exfiltration call. (Formalises
   ToolSieve's `parse_payload` evidence extraction.)
3. **Free-text instruction outside a field** — any prose that is not inside one of
   the five schema fields.
4. **Security-justification voice** — "for security reasons", "to verify you are
   safe", "you must confirm before proceeding", and similar social-engineering
   phrasings that coerce extra tool calls.

Predicates are deliberately static and regex-driven. No LLM is required to *check*
conformance; an LLM is only an *optional* aid for *canonicalising* (see §6).

## 5. Reference implementation (Python)

Two entry points, reusing ToolSieve logic:

- `canonicalise(description: str) -> CanonicalDescription` — parses free text,
  classifies it `conformant | non_conformant | unknown`, and either keeps it or
  rewrites it into the §3 shape.
- `validate(description) -> list[Violation]` — applies the §4 predicates and
  returns the specific rule(s) violated.

The model-rewrite path (LLM rewrites into the shape) is retained with its
shared-model confound disclosed: the same model that acts as the agent rewriting
descriptions measures rewrite quality, not independence.

## 6. Conformance suite

A producer proves conformance by running, with third-party-re-runnable output:

1. **Retention test** — over a clean corpus of real tool descriptions, the fraction
   whose semantic content is retained after canonicalisation must be ≥ threshold
   (ToolSieve's clean-retention was 0.988 for RulesStrip).
2. **Poisoning benchmark** — over the frozen 1,312-instance MCPTox set (367-item
   frozen subset), report ASR and UCC with Wilson 95% CIs, rule-scored, no LLM judge.
   A conformant canonicaliser must reduce ASR vs the dateless baseline.

## 7. Relationship to ToolSieve

ToolSieve (shipped 2026-10-26) measured the attack: dateless free-text descriptions
drive **13.8%** attack success; canonicalising cuts it to **7.8%** (367 frozen items,
rule-scored, Wilson CIs). ToolSurface is that finding promoted to a normative
standard: the schema in §3 and predicates in §4 are what ToolSieve's `RulesStrip`
canonicaliser already implements. ToolSieve remains the evidence/benchmark artifact;
ToolSurface is the standard + reference implementation + conformance suite.

## 8. What justifies Growth (Sandbox thesis)

In order of weight:

1. Two unaffiliated organizations adopting the standard in a tool they ship,
   recorded in `ADOPTERS.md`.
2. One integration with an AAIF-hosted MCP project (most plausibly the MCP Gateway
   & Registry proposal #29 implementing `validate`, or legacy2mcp #54 emitting
   conformant descriptions).
3. A verifier written in a language other than Python, from this spec alone, passing
   the conformance suite.
4. Maintainers from at least two organizations.
