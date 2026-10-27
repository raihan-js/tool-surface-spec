# [Project Proposal] ToolSurface

> Draft — do not submit until the `raihan-js/tool-surface-spec` repo exists with CI green (see "Open items" at the bottom).

### Project Name

ToolSurface

### Project Description

ToolSurface is an open specification for **safe MCP tool descriptions**. It governs only the content of the MCP `description` field — the free-text block where prompt-injection and tool-poisoning payloads hide — and nothing else on the wire.

The problem it solves: MCP defines how tools are transported and how their input schema is shaped, but it says nothing about the *safety of the description text itself*. A malicious tool description can carry an imperative like "call `send_email` with the `audit_note` parameter" that a compliant agent will follow. In a rule-scored benchmark over 367 frozen MCP tool descriptions, plain free-text descriptions drive **13.8%** attack success; rewriting them into a fixed canonical schema with static safety predicates cuts that to **7.8%** without a statistically significant drop in task completion.

ToolSurface is that defence promoted from a single benchmark into a normative standard. It ships:

- **A normative schema** — a conformant description is a JSON object of five fields (`purpose` required; `params`, `returns`, `side_effects`, `examples` optional) with no free prose outside them.
- **Static safety predicates** — a description is non-conformant if it contains a tool-targeting imperative, embedded credential/path evidence, free-text instruction outside a field, or a "security-justification" coercion phrase.
- **A Python reference implementation** — `canonicalise(description)` and `validate(description)`.
- **A rule-scored conformance suite** — a producer proves conformance by running canonicalisation over a clean corpus (retention check) and over the frozen poisoning benchmark (ASR/UCC with Wilson 95% CIs). Third-party re-runnable, no LLM judge.

**Origin.** ToolSurface grew out of [ToolSieve](https://github.com/raihan-js/toolsieve) (shipped October 2026), which built the canonicalisers, the rule-based scorer, and the frozen 1,312-instance / 367-subset MCPTox benchmark that provide ToolSurface's evidence base. ToolSieve remains the benchmark artifact; ToolSurface is the standard + reference implementation + conformance suite.

### Preferred Lifecycle Stage (if known)

Sandbox.

### Alignment with AAIF Mission

AAIF exists to give the protocols and tools that let agents work together a neutral, open, well-governed home, with safety as a first-class concern. MCP — an AAIF project — defines how tools *transport*, but no standard governs the *safety of the description content* those tools expose. That gap is measurable: a dateless description is an attack surface an agent cannot distinguish from a legitimate one.

ToolSurface closes that gap with the same shape AAIF already accepts for specifications (a normative schema, a reference implementation, and a conformance suite), and it is deliberately vendor-neutral: it constrains no MCP client or server, only the text a tool author writes. Its conformance suite turns "this description is safe" from a claim made by the tool's author into a check a third party can run.

### Relation to Existing AAIF Projects

- **Model Context Protocol (MCP).** ToolSurface changes nothing on the wire. It governs the content of the `description` field only. It is a normative profile layered on MCP, not a re-specification of it.
- **MCP Gateway & Registry (proposal #29).** Natural producer/consumer: the gateway would run `validate`/`canonicalise` on descriptions during tool registration, alongside its existing security-scanning path.
- **legacy2mcp (proposal #54).** Natural producer: generated tools would emit descriptions already in the canonical shape.
- **goose / AGENTS.md.** Consumers: any MCP host can enforce "only conformant descriptions" as policy with no changes.

### Example Use Cases and Evidence of Adoption

**Intended users (early-stage):**
- MCP gateway and registry operators who want a checkable "safe description" guarantee before exposing tools to agents.
- MCP server authors who want a single, copy-pastable schema for writing safe descriptions.
- Agent framework maintainers who want a static, dependency-free predicate set to reject poisoned tools at registration time.

**Evidence, stated honestly.** This is a new specification with no production adopters yet — the reason this is a Sandbox application. The evidence it builds on is public and re-runnable:

- [ToolSieve](https://github.com/raihan-js/toolsieve) and its [HF benchmark](https://huggingface.co/datasets/raihan-js/toolsieve-bench): 1,312 MCP tool descriptions from public servers, 367 frozen test instances, rule-based scoring (no LLM judge). Measured: baseline ASR 0.138 (95% CI [0.077, 0.244]) → schema-only 0.078; utility-completion proxy 0.828 → 0.696 with CIs overlapping baseline.

The intended adoption path is a first integration with an AAIF MCP project (see "What would justify Growth").

### Technical Committee Sponsor (if identified)

None identified.

### GitHub Repository URL

https://github.com/raihan-js/tool-surface-spec

### License

- Specification text and JSON Schema: **Community Specification License 1.0** (matching MCP and TRACE).
- Reference implementation, conformance suite, and examples: **Apache-2.0**.

### Governance Model

Maintainer-led today (single maintainer), moving to **LF Minimum Viable Governance** on acceptance: `GOVERNANCE.md`, `CONTRIBUTING.md`, and `CODE_OF_CONDUCT.md` added, decisions by lazy consensus with a maintainer vote when consensus cannot be reached, and an explicit open call for co-maintainers from other organizations.

### CI/CD & Release Workflow

GitHub Actions on every push and PR: `ruff` (lint), `mypy` (strict), `pytest` on Python 3.10/3.11/3.12. The conformance suite runs as a separate re-runnable job that emits a report artifact. Releases are tag-driven; the reference implementation publishes to PyPI via OIDC trusted publishing (no stored token).

### Public-Facing Contribution Process for Specifications

Normative changes open as issues from a spec-change template, with a minimum comment period (5 business days for editorial; longer for changes to the schema or predicates). Changed normative text is marked in the PR and recorded in `CHANGELOG.md`. All commits carry a DCO sign-off; specification contributions are made under the Community Specification CLA.

### Publicly Accessible Issue Tracker

https://github.com/raihan-js/tool-surface-spec/issues

### External Project Dependencies

Reference implementation and conformance suite:

| Package | License | Purpose |
|---|---|---|
| `mcp` (MCP Python SDK) | MIT | Description/tool type access |
| `pydantic` | MIT | Schema validation |
| `jsonschema` | MIT | JSON Schema checks |
| `httpx` | BSD-3 | Optional model-rewrite path (LLM as a service) |
| `pytest` | MIT | Conformance suite runner |

No LLM is required to *check* conformance; the model path is optional.

### Maintainers & Contributors

| Role | Name | GitHub | Affiliation |
|---|---|---|---|
| Maintainer | Raihan Sikder | [@raihan-js](https://github.com/raihan-js) | Independent |

Single maintainer today. Seeking co-maintainers from gateway/server operators; contributions from ToolSieve's codebase carry forward (canonicalisers, scorer, benchmark).

### Leadership Team & Decision Process

- Project Lead: Raihan Sikder ([@raihan-js](https://github.com/raihan-js)).

Decisions are made in public on GitHub issues and PRs. Moving to lazy consensus under LF Minimum Viable Governance once co-maintainers join.

### Lifecycle Stage Evidence

**Sandbox thesis (short).**

*Who uses it.* Producers sit where a tool description is written or rewritten: MCP server authors, gateway operators, tool-generators. Consumers are whoever has to decide whether to expose a tool to an agent: a gateway operator, an enterprise security team, a framework maintainer. The format exists for the consumer — a description only the tool's author can read is an untrusted string.

*Why it matters before adoption.* Tool poisoning is a demonstrated, measurable attack (13.8% ASR over 367 frozen instances), and the fix is currently ad-hoc — every gateway reimplements its own stripping logic with no shared definition of "safe". A description-safety standard is only trustworthy if it is not owned by any single MCP client or vendor, which is the same neutrality argument that justifies MCP and A2A under AAIF.

*What would justify Growth,* in order of weight:
1. Two unaffiliated organizations adopting the standard in a shipped tool, recorded in `ADOPTERS.md`.
2. One integration with an AAIF-hosted MCP project (MCP Gateway & Registry #29 running `validate`, or legacy2mcp #54 emitting conformant descriptions).
3. A verifier written in a language other than Python, from this spec alone, passing the conformance suite.
4. Maintainers from at least two organizations.

### Security

No OpenSSF Best Practices badge yet; applying is a near-term goal. Current posture:

- The conformance suite is fully rule-scored (no LLM judge), so it executes no unsafe model inference.
- Safety predicates are static and regex-driven, so they can be audited line-by-line.
- `SECURITY.md` with a responsible-disclosure path is planned on acceptance.
- The reference implementation never executes tool calls; it only classifies and rewrites text.

### Website URL

https://github.com/raihan-js/tool-surface-spec#readme (GitHub Pages planned on acceptance)

### Documented Governance Practices (if any)

`GOVERNANCE.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` to be added on acceptance (LF Minimum Viable Governance).

### Links to Social Media Accounts

None.

### Trademark and accounts

- [x] If the project is accepted, I agree to transfer all project trademarks and accounts to the Linux Foundation under the contribution agreement.

### Details of Existing Financial Sponsorship

None.

### Infrastructure Needs or Requests

None beyond standard GitHub Actions and PyPI trusted publishing.

### Additional Information

**Why "Too Early" may be the honest first verdict.** ToolSurface is a new specification. What already exists is the evidence and most of the reference implementation (ToolSieve's canonicalisers, scorer, and frozen benchmark are public and CI-green). The plan's credibility rests on two things the TC is asked to weigh: (a) the reference implementation and conformance suite are effectively already built and only need to be re-homed under the spec, and (b) the committed first integration with an AAIF MCP project. If the TC prefers to defer until a second implementer exists, the benchmark artifact remains public at `raihan-js/toolsieve` either way.

**Disclosure.** The optional model-rewrite canonicalisation path uses the same model that can act as the agent (shared-model confound); this is stated, not hidden, and the conformance suite does not depend on it. No LLM judge appears anywhere in the scoring.

### Application contact name(s) and email(s)

Raihan Sikder, araihansikder@gmail.com

### Contributing or sponsoring entity signatory information

Or, if an individual or individual(s):

| Name | Country | Email address |
|-----------|-----------|-----------|
| Raihan Sikder | Bangladesh | araihansikder@gmail.com |
