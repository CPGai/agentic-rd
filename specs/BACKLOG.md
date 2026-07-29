# Agentic R&D Repository Backlog

This document serves as the ground-truth, git-tracked backlog for framework concerns, operational friction, and feature enhancements.

## Backlog Index

| ID | Title | Domain | Priority | Status |
| :--- | :--- | :--- | :--- | :--- |
| BL-SKILL-01 | Skill Namespace Collision and Overlap Resolution | Skill Registry / Interoperability | High | Open |

---

## Active Backlog Items

### [BL-SKILL-01] Skill Namespace Collision and Overlap Resolution (Agentic R&D vs. Hermes Native vs. Google ADK)

- **Domain/Layer:** Skill Registry, Context Boundaries, and Dual-Harness Execution (Hermes & AGY-IDE)
- **Severity/Priority:** High (Critical for preventing agent hallucination and runtime context ambiguity)
- **Origin:** Strategic Architecture Oversight / Framework Interoperability Analysis
- **Status:** Open (Documented / Awaiting Handoff Execution)

#### Description / User Concern
There is a clear risk of namespace collision and execution ambiguity between custom skills defined within the Agentic R&D framework (`/home/carlospg/workspace/agentic-rd/skills/`), native Hermes plugins/skills (e.g., global registry under `~/.hermes/skills/`), and external toolsets like the Google Agent Development Kit (ADK). When a coding agent (Hermes or Antigravity) is invoked, similar functions across these layers (such as agent scaffolding, tool invocation, or context management) risk confusing the agent about which execution standard to follow, leading to potential rule corruption or framework bleeding.

#### Architectural Implication
Unbounded or overlapping skill definitions violate the isolation and progressive-disclosure principles (`agentskills.io` L1/L2/L3 spec) established in the framework. If the root `AGENTS.md` and harness instructions do not explicitly disambiguate namespace precedents, coding agents may inadvertently mix Google ADK primitives with custom agentic-rd schemas, causing runtime errors, non-deterministic behaviors, or unwanted modifications inside the core framework repository.

#### Actionable Handoff Directive (for Hermes / AGY)
When actioned, instruct Hermes or Antigravity to perform a full capability audit across `~/.hermes/skills/`, the local framework `skills/` directory, and Google ADK command footprints:
1. Establish an explicit **Namespace Prefixing & Priority Matrix** in `HARNESS_SPEC.md` (forcing strict precedence for custom domain skills over global fallbacks).
2. Update root `AGENTS.md` to include a **Conflict Resolution Protocol** commanding coding agents to reject ambiguous or duplicate tool handlers.
3. Verify that all consumer project scaffolding runs exclusively via the designated framework wrapper (`agentic-scaffold`) without falling back to external ADK scaffolding defaults.
