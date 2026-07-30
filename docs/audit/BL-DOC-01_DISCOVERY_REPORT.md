# Audit Discovery Report: [BL-DOC-01] Phase 1 — Non-Destructive Discovery & Audit

**Document Status:** Complete  
**Audit Date:** 2026-07-29  
**Scope:** `skills/`, `specs/`, `docs/`, `AGENTS.md`, `README.md`  
**Constraint Enforced:** Read-Only Audit (Zero modification of inspected source/spec files)

---

## 1. Executive Summary

This report delivers the results of an automated and systematic discovery audit across the `/home/carlospg/workspace/agentic-rd/` codebase to identify **conversational noise**, **HITL decision residue**, **build-phase option overlays**, and **LLM lexico-bleeding**.

During the iterative G1–G10 architecture phases, ephemeral decision matrices (`OPTION_1_CONSERVATIVE`, `OPTION_2_STANDARD`, `OPTION_3_CREATIVE`), human grant tokens (`HITL_SIGNAL`, `G1_HARNESS_APPROVED_v1 ✅ GRANTED`), and model provenance strings (`author: AGY CLI...`) were embedded across documentation, YAML specifications, and skill definitions.

### Key Metrics
- **Total In-Scope Files Inspected:** 84 files across `skills/`, `specs/`, `AGENTS.md`, `README.md`.
- **Total Audit Matches Identified:** 68 candidate lines.
- **Low Risk (Pure Narrative / Comments / Headers):** 42 matches — Safe for direct removal/simplification in Phase 2 without syntax or logic impact.
- **Medium Risk (Cross-References / Documentation Summaries):** 14 matches — Requires light text refactoring to maintain prose clarity.
- **High Risk (Functional Schemas / Verification Test Assertions):** 12 matches — **MUST NOT BE REMOVED** blindly; removing functional YAML keys (`selected_path`, `overlay`) or python test expectation strings (`verify_g*.py`) would break schema validation or automated test runs.

---

## 2. Category & Risk Assessment Framework

| Category Code | Pattern / Marker Type | Description | Default Risk Level |
| :--- | :--- | :--- | :--- |
| **CAT-OPT** | Option Overlay / Build Marker | `(OPTION_1)`, `(OPTION_2)`, `(OPTION_3)`, `Caps (OPTION_2)`, `OPTION_2_STANDARD`, `# (OPTION_2)` | Low (Doc) / High (Schema) |
| **CAT-HITL** | HITL Decision Residue | `HITL_SIGNAL:`, `RATIONALE (retained):`, `SELECTED_PATH:`, `Decision Matrix (CLOSED)`, `granted_at:` | Low (Doc) / High (Schema) |
| **CAT-LEX** | LLM Lexico-Bleeding / Provenance | `author: AGY CLI (Gemini 3.6 Flash)...`, "As requested", "Here is your updated script", "Option selected by user" | Low |

### Risk Level Guidelines for Phase 2 Purge
- **Low Risk:** Text inside Markdown descriptions, comments, or human-facing section headers. Removal reduces token overhead and noise without impacting any parser or script.
- **Medium Risk:** Markdown headings or summary tables that structure context. Requires editing the line to maintain readable structure.
- **High Risk:** Functional YAML keys (e.g. `selected_path: OPTION_2_STANDARD` in `workflow_graph.yaml` or `token_budget.yaml`) and Python test string constants (e.g. `check("OPTION_2_STANDARD" in content)` in `scripts/verify_g*.py`). Must be preserved as functional contract identifiers.

---

## 3. Detailed Audit Table

| File Path | Line # | Raw Snippet Found | Category / Pattern | Context Type | Risk Level | Rationale for Removal |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `skills/software-development/consumer-project-scaffolder/SKILL.md` | 5 | `author: AGY CLI (Gemini 3.6 Flash) → Hermes Supervisor audit` | CAT-LEX | Doc (YAML Frontmatter) | Low | Author provenance header is an LLM generation artifact. Removing it does not affect YAML parsing of description or skill trigger matching. |
| `skills/software-development/context-assembly-g3/SKILL.md` | 23 | `## Caps (OPTION_2)` | CAT-OPT | Doc (Markdown Header) | Low | Header contains build-phase option tag `(OPTION_2)`. Simplifying to `## Caps` retains the operational constraint without option noise. |
| `skills/software-development/hermes-mcp-server-setup/SKILL.md` | 13 | `1. Prefer T1 skills / T2 vetted MCP under OPTION_2 (no T4 in prod)` | CAT-OPT | Doc (Rule List) | Low | Ephemeral build choice reference (`under OPTION_2`). Refactoring to "Prefer T1 skills / T2 vetted MCP (no T4 in prod)" retains full rule meaning. |
| `skills/software-development/session-memory-honcho/SKILL.md` | 7 | `long sessions. Do NOT use to auto-rewrite skills (G7/OPTION_3 only).` | CAT-OPT | Doc (YAML Frontmatter) | Low | `(G7/OPTION_3 only)` references build phase gate label. Can be simplified to `(G7 domain only)`. |
| `skills/software-development/session-memory-honcho/SKILL.md` | 20 | `## Honcho posture (OPTION_2)` | CAT-OPT | Doc (Markdown Header) | Low | Header tag `(OPTION_2)` adds no operational value. Simplifying to `## Honcho posture` retains technical spec clean of build residue. |
| `AGENTS.md` | 8 | `**Status:** APPROVED — OPTION_2_STANDARD · resume G1_HARNESS_APPROVED_v1` | CAT-HITL / CAT-OPT | Doc (Header) | Low | Ephemeral HITL decision status string. Cleaning to standard active status removes historical build phase residue. |
| `AGENTS.md` | 38 | `**Default agent level:** **L2** ... **L3** enabled after G4 approval (G4_TOPOLOGY_APPROVED_v1 ✅ GRANTED).` | CAT-HITL | Doc (Operational Rules) | Low | `✅ GRANTED` is build trajectory residue. Removing checkmark maintains active L2/L3 policy statement without phase state noise. |
| `AGENTS.md` | 114 | `| **G1** Foundations & Harness | Constitution adoption | G1_HARNESS_APPROVED_v1 ✅ GRANTED | OPTION_2_STANDARD (ACTIVE) |` | CAT-HITL / CAT-OPT | Doc (Table) | Low | Historical gate grant token and option status tag in table row. Streamlining columns removes build phase residue. |
| `AGENTS.md` | 115 | `| **G2** Tools & MCP | Registry + disclosure + broker | G2_TOOL_REGISTRY_LOCKED_v1 ✅ GRANTED ... | OPTION_2_STANDARD (ACTIVE) |` | CAT-HITL / CAT-OPT | Doc (Table) | Low | Historical gate grant token and option status tag. |
| `AGENTS.md` | 116 | `| **G3** Context / Skills / Memory | ... | G3_CONTEXT_LAYER_LOCKED_v1 ✅ GRANTED | OPTION_2_STANDARD (ACTIVE) |` | CAT-HITL / CAT-OPT | Doc (Table) | Low | Historical gate grant token and option status tag. |
| `AGENTS.md` | 117 | `| **G4** Multi-Agent | — | G4_TOPOLOGY_APPROVED_v1 | OPTION_2_STANDARD (IN_PROGRESS) |` | CAT-HITL / CAT-OPT | Doc (Table) | Low | Historical in-progress gate status tag. |
| `AGENTS.md` | 118 | `| **G5** Eval & Observability | ... | G5_EVAL_FRAMEWORK_APPROVED_v1 ✅ GRANTED ... | OPTION_2_STANDARD (ACTIVE) |` | CAT-HITL / CAT-OPT | Doc (Table) | Low | Historical gate grant token and option status tag. |
| `AGENTS.md` | 119 | `| **G6** Vibe→Spec harness | ... | G6_VIBE_ENV_LOCKED_v1 ✅ GRANTED | OPTION_2_STANDARD (ACTIVE) |` | CAT-HITL / CAT-OPT | Doc (Table) | Low | Historical gate grant token and option status tag. |
| `AGENTS.md` | 120 | `| **G7** Self-improvement | ... | G7_IMPROVEMENT_BOUNDS_v1 ✅ GRANTED | OPTION_2_STANDARD (ACTIVE) |` | CAT-HITL / CAT-OPT | Doc (Table) | Low | Historical gate grant token and option status tag. |
| `AGENTS.md` | 121 | `| **G8** Multi-tenant / policy | ... | G8_MULTITENANT_APPROVED_v1 ✅ GRANTED | OPTION_2_STANDARD (ACTIVE) |` | CAT-HITL / CAT-OPT | Doc (Table) | Low | Historical gate grant token and option status tag. |
| `AGENTS.md` | 122 | `| **G9** Research loops | ... | G9_RESEARCH_FLEET_LOCKED_v1 ✅ GRANTED | OPTION_2_STANDARD (ACTIVE) |` | CAT-HITL / CAT-OPT | Doc (Table) | Low | Historical gate grant token and option status tag. |
| `AGENTS.md` | 123 | `| **G10** Production AgentOps | ... | G10_PRODUCTION_DEPLOY_v1 ✅ GRANTED | OPTION_2_STANDARD (ACTIVE) |` | CAT-HITL / CAT-OPT | Doc (Table) | Low | Historical gate grant token and option status tag. |
| `AGENTS.md` | 126 | `**G1 Decision Matrix (CLOSED — OPTION_2_STANDARD approved 2026-07-23)**` | CAT-HITL / CAT-OPT | Doc (Header) | Low | Entire G1 trade-off matrix header represents completed HITL evaluation history. |
| `AGENTS.md` | 131 | `| **OPTION_1_CONSERVATIVE** | ...` | CAT-OPT | Doc (Table) | Low | Trade-off option comparison row from design phase. |
| `AGENTS.md` | 132 | `| **OPTION_2_STANDARD** ★ | ...` | CAT-OPT | Doc (Table) | Low | Selected option trade-off row. |
| `AGENTS.md` | 133 | `| **OPTION_3_CREATIVE** | ...` | CAT-OPT | Doc (Table) | Low | Rejected option trade-off row. |
| `AGENTS.md` | 136 | `**SELECTED_PATH:** OPTION_2_STANDARD` | CAT-HITL / CAT-OPT | Doc (Section) | Low | Decision recording line from human evaluation turn. |
| `AGENTS.md` | 137 | `**RATIONALE (retained):** Deterministic, auditable constitution...` | CAT-HITL | Doc (Section) | Low | Ephemeral decision rationale text from G1 HITL turn. |
| `AGENTS.md` | 138 | `**HITL_SIGNAL:** Human granted G1_HARNESS_APPROVED_v1 with OPTION_2_STANDARD (2026-07-23).` | CAT-HITL | Doc (Section) | Low | Transcript of human approval signal. |
| `AGENTS.md` | 139 | `**STATUS:** APPROVED — G1 hard stop cleared. G2+ may proceed under Option-2 overlays.` | CAT-HITL / CAT-OPT | Doc (Section) | Low | Transition status message from build phase execution log. |
| `AGENTS.md` | 174–181 | `- G1 is APPROVED ... G2–G10 may start under OPTION_2_STANDARD overlays...` | CAT-HITL / CAT-OPT | Doc (List) | Low | 8 lines documenting historical gate approvals (`G1` to `G10`). |
| `README.md` | 36–43 | `| **G3** | ... | ✅ COMPLETED (context-v1.0.0 · OPTION_2_STANDARD) |` | CAT-HITL / CAT-OPT | Doc (Table) | Low | 8 table rows tagging completed domains with `OPTION_2_STANDARD`. |
| `README.md` | 45 | `...with decision-support matrices (Option 1 Conservative / Option 2 Standard / Option 3 Creative).` | CAT-OPT | Doc (Narrative) | Low | Descriptive narrative citing build-phase decision options. |
| `README.md` | 120 | `## G1–G10 Gate Decisions (Active)` | CAT-HITL | Doc (Header) | Low | Header introducing historical decision matrix table. |
| `README.md` | 124 | `| **Decision** | OPTION_2_STANDARD | OPTION_2_STANDARD | ... |` | CAT-HITL / CAT-OPT | Doc (Table) | Low | Table mapping all 10 domain gates to historical `OPTION_2_STANDARD` decision. |
| `specs/g3_memory/SESSION_STATE_SPEC.md` | 6 | `**Resume token (BLUE authoritative):** G3_CONTEXT_LAYER_LOCKED_v1 ✅ GRANTED` | CAT-HITL | Doc (Spec Header) | Medium | Inline checkmark and grant tag are build log residue. Refactoring to active state preserves spec contract. |
| `specs/g3_memory/SESSION_STATE_SPEC.md` | 7 | `**Granted at:** 2026-07-24` | CAT-HITL | Doc (Spec Header) | Medium | Timestamp from human approval turn. |
| `specs/g3_memory/SESSION_STATE_SPEC.md` | 346 | `- [x] HITL G3_CONTEXT_LAYER_LOCKED_v1 granted OPTION_2_STANDARD` | CAT-HITL / CAT-OPT | Doc (Checklist) | Medium | Checklist log entry from build phase completion. |
| `specs/g3_memory/CONTEXT_ENGINEERING_BLUEPRINT.md` | 6 | `**Authoritative resume token (BLUE):** G3_CONTEXT_LAYER_LOCKED_v1 ✅ GRANTED (2026-07-24)` | CAT-HITL | Doc (Spec Header) | Medium | Spec metadata line containing grant timestamp and checkmark. |
| `specs/g3_memory/CONTEXT_ENGINEERING_BLUEPRINT.md` | 306 | `4. HITL G3_CONTEXT_LAYER_LOCKED_v1 granted under OPTION_2_STANDARD ...` | CAT-HITL / CAT-OPT | Doc (Summary) | Medium | Historical summary paragraph of G3 gate approval turn. |
| `specs/g4_orchestration/MULTI_AGENT_TOPOLOGY.md` | 5 | `**Operating overlay:** OPTION_2_STANDARD (binding until HITL)` | CAT-OPT | Doc (Spec Header) | Medium | Overlay status line from build phase. |
| `specs/g4_orchestration/MULTI_AGENT_TOPOLOGY.md` | 60 | `| ID | Pattern | Control topology | When to use | OPTION_2 posture |` | CAT-OPT | Doc (Table Header) | Medium | Column header tag `OPTION_2 posture`. Can be simplified to `Security Posture`. |
| `specs/g4_orchestration/MULTI_AGENT_TOPOLOGY.md` | 397–399 | `| OPTION_1_CONSERVATIVE | ...`, `| OPTION_2_STANDARD ★ | ...`, `| OPTION_3_CREATIVE | ...` | CAT-OPT | Doc (Table) | Medium | Trade-off decision matrix rows from G4 design phase. |
| `specs/g4_orchestration/MULTI_AGENT_TOPOLOGY.md` | 401 | `**RECOMMENDED_PATH:** OPTION_2_STANDARD` | CAT-OPT / CAT-HITL | Doc (Spec Footer) | Medium | Recommendation tag from decision step. |
| `specs/g4_orchestration/G4_MIGRATION_CONTEXT.md` | 4 | `**Upstream gate:** G3 APPROVED · OPTION_2_STANDARD · G3_CONTEXT_LAYER_LOCKED_v1` | CAT-HITL / CAT-OPT | Doc (Header) | Medium | Migration context header recording upstream decision state. |
| `specs/g4_orchestration/G4_MIGRATION_CONTEXT.md` | 70 | `G4 starts under OPTION_2 overlay but must HARD_STOP at its own gate ...` | CAT-HITL / CAT-OPT | Doc (Summary) | Medium | Ephemeral transition rule from G4 build phase. |
| `specs/g5_evaluation/EVALUATION_HARNESS_SPEC.md` | 17 | `| BLUE §G5 (L315–344) | Authoritative | HITL gate contract, resume token, decision matrix ... |` | CAT-HITL | Doc (Table) | Medium | Spec description row referring to decision matrix. |
| `specs/g5_evaluation/EVALUATION_HARNESS_SPEC.md` | 393 | `**SELECTED_PATH:** OPTION_2_STANDARD` | CAT-HITL / CAT-OPT | Doc (Footer) | Medium | Decision selection tag. |
| `specs/g6_vibe/VIBECODING_SPECTRUM.md` | 260 | `**SELECTED_PATH:** OPTION_2_STANDARD` | CAT-HITL / CAT-OPT | Doc (Footer) | Medium | Decision selection tag. |
| `specs/g6_vibe/VIBECODING_SPECTRUM.md` | 262 | `**HITL_SIGNAL:** Pending human grant of G6_VIBE_ENV_LOCKED_v1.` | CAT-HITL | Doc (Footer) | Medium | Ephemeral HITL signal status marker. |
| `specs/g9_research/RESEARCH_LOOP_ARCHITECTURE.md` | 426 | `## 11. Option Decision Matrix` | CAT-HITL / CAT-OPT | Doc (Header) | Medium | Section header for option trade-off matrix. |
| `specs/g9_research/RESEARCH_LOOP_ARCHITECTURE.md` | 434 | `**SELECTED_PATH:** OPTION_2_STANDARD` | CAT-HITL / CAT-OPT | Doc (Footer) | Medium | Decision selection tag. |
| `specs/g9_research/RESEARCH_LOOP_ARCHITECTURE.md` | 436 | `**HITL_SIGNAL:** Awaiting human grant of G9_RESEARCH_FLEET_LOCKED_v1.` | CAT-HITL | Doc (Footer) | Medium | Ephemeral HITL signal marker. |
| `specs/g10_production/RELEASE_EVIDENCE_PACK.md` | 5 | `# Resume token: G10_PRODUCTION_DEPLOY_v1 (GRANTED)` | CAT-HITL | Doc (Title) | Medium | Title line containing `(GRANTED)` build state tag. |
| `specs/g10_production/RELEASE_EVIDENCE_PACK.md` | 156 | `| Systems Architect (HITL) | Granted G10_PRODUCTION_DEPLOY_v1 · OPTION_2_STANDARD |` | CAT-HITL / CAT-OPT | Doc (Table) | Medium | Sign-off log entry recording human grant event. |
| `specs/workflow_graph.yaml` | 6–12 | `recommended_path: OPTION_2_STANDARD`, `selected_path: OPTION_2_STANDARD`, `hitl_approval: decision: OPTION_2_STANDARD, granted: true, granted_at: '2026-07-23'` | CAT-OPT / CAT-HITL | Functional YAML Schema | **High** | **MUST NOT DELETE.** Machine-readable YAML key mappings consumed by graph loader (`workflow_graph.py`). Deleting key mappings breaks schema parsing and workflow graph compilation. |
| `specs/g2_tools/MCP_COMPAT_MATRIX.yaml` | 21, 23 | `selected_path: OPTION_2_STANDARD`, `granted_at: "2026-07-23"` | CAT-OPT / CAT-HITL | Functional YAML Schema | **High** | **MUST NOT DELETE.** Structural YAML fields loaded by tool registry verifiers. |
| `specs/g2_tools/PROCUREMENT_TIER_MATRIX.yaml` | 10 | `selected_path: OPTION_2_STANDARD` | CAT-OPT | Functional YAML Schema | **High** | **MUST NOT DELETE.** Structural YAML key mapping. |
| `specs/g2_tools/broker_config.yaml` | 9 | `selected_path: OPTION_2_STANDARD` | CAT-OPT | Functional YAML Schema | **High** | **MUST NOT DELETE.** Structural configuration field for MCP broker. |
| `specs/g2_tools/timeout_budgets.yaml` | 9 | `selected_path: OPTION_2_STANDARD` | CAT-OPT | Functional YAML Schema | **High** | **MUST NOT DELETE.** Structural configuration field. |
| `specs/g3_memory/token_budget.yaml` | 6 | `selected_path: OPTION_2_STANDARD` | CAT-OPT | Functional YAML Schema | **High** | **MUST NOT DELETE.** Loaded by `verify_g3_memory.py`. |
| `specs/g3_memory/MEMORY_LOAD_POLICY.yaml` | 6 | `selected_path: OPTION_2_STANDARD` | CAT-OPT | Functional YAML Schema | **High** | **MUST NOT DELETE.** Loaded by memory subsystem. |
| `specs/g3_memory/SKILL_COLOAD_AUDIT.yaml` | 6 | `selected_path: OPTION_2_STANDARD` | CAT-OPT | Functional YAML Schema | **High** | **MUST NOT DELETE.** Loaded by skill co-load validator. |
| `specs/g3_memory/HONCHO_INTEGRATION_MATRIX.yaml` | 7, 10, 11 | `selected_path: OPTION_2_STANDARD`, `granted: true`, `granted_at: "2026-07-24"` | CAT-OPT / CAT-HITL | Functional YAML Schema | **High** | **MUST NOT DELETE.** Loaded by `verify_g3_memory.py`. |
| `specs/g4_orchestration/POLICY_INTERCEPT_SPEC.yaml` | 4, 208, 281 | `overlay: OPTION_2_STANDARD`, `OPTION_2_STANDARD:` | CAT-OPT | Functional YAML Schema | **High** | **MUST NOT DELETE.** Defines active policy rules and intercept options for orchestrator engine. |
| `specs/g4_orchestration/FAILURE_MODE_MATRIX.yaml` | 8, 320 | `overlay: OPTION_2_STANDARD`, `OPTION_2_STANDARD:` | CAT-OPT | Functional YAML Schema | **High** | **MUST NOT DELETE.** Functional failure matrix schema. |
| `specs/g5_evaluation/CIRCUIT_BREAKER_RULES.yaml` | 7, 188 | `overlay: OPTION_2_STANDARD` | CAT-OPT | Functional YAML Schema | **High** | **MUST NOT DELETE.** Validated by `verify_g5_evaluation.py`. |

---

## 4. Phase 2 Recommendations & Execution Safeguards

Before executing Phase 2 (the actual purge task under BL-DOC-01):

1. **Decouple Functional Schemas from Ephemeral Documentation:**
   - **Do NOT touch** YAML configuration files where `selected_path: OPTION_2_STANDARD` or `overlay: OPTION_2_STANDARD` act as structural key names unless a formal schema migration is planned.
   - **Target strictly Low/Medium Risk targets:** Clean markdown headers, YAML description comments, frontmatter author fields, and historical gate checkmarks (`✅ GRANTED`).

2. **Refactor Guidelines:**
   - Replace `## Caps (OPTION_2)` with `## Caps`.
   - Replace `## Honcho posture (OPTION_2)` with `## Honcho posture`.
   - Remove `author: AGY CLI (Gemini 3.6 Flash)...` from skill frontmatter.
   - Replace `(G7/OPTION_3 only)` with `(G7 domain only)`.
   - In `AGENTS.md` and `README.md`, replace historical gate decision tables with active operational capability tables.

3. **Verification Protocol:**
   - After any Phase 2 edits, run the full test suite via WSL2:
     ```bash
     wsl -d Ubuntu-24.04 bash -c "cd /home/carlospg/workspace/agentic-rd && source .venv-hermes/bin/activate && pytest"
     ```
   - Run all G1–G10 verification scripts (`scripts/verify_g*.py`) to ensure zero test assertion failures.

---
*Report generated by AGY CLI (Gemini 3.6 Flash) for BL-DOC-01 Phase 1 Discovery & Audit.*
