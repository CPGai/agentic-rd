# Research Loop Architecture

**Domain:** G9 — Autonomous Research Loops
**Tier:** Premium Frontier (Step A)
**Status:** DRAFT_PRE_GATE
**Overlay:** OPTION_2_STANDARD
**Upstream:** multitenant-v1.0.0 (G8 LOCKED)
**BLUE Resume Token:** `G9_RESEARCH_FLEET_LOCKED_v1`
**Primary Harness Touch:** H_CONTEXT, H_EVAL

**Anchors:**
- BLUE §G9 L447–475: Hypothesis formalized as Gherkin specs, multi-agent research fleets, A2A specialist agents, domain skills with progressive disclosure of papers, methodological evaluation harness, AutoResearchClaw-style Pivot/Refine + DRAFT/DEBUG/IMPROVE, verifiable reporting (no hallucinated citations), seven HITL intervention modes
- WP-S1: Factory Model — harness correctness-by-construction; Agent = Model + Harness
- WP-S2: A2A task state machine; Agent Card; specialist composition
- WP-S3: Skills progressive disclosure; co-load 5–15; paper-as-knowledge context type
- WP-S4: 7-pillar Effective Trust; trust decay; Red/Blue/Green; slopsquatting defense; zero ambient authority
- WP-S5: SDD — spec is durable, code is disposable; hybrid Markdown+YAML; token economics
- G4 MULTI_AGENT_TOPOLOGY.md: hierarchical_coordinator_specialists; A2A handshake SM
- G5 EVALUATION_HARNESS_SPEC.md: trajectory schema; dual-judge; 5%/15% thresholds; trust score [0.0, 1.0]
- G7 PIVOT_REFINE_TREE.md: DRAFT/DEBUG/IMPROVE/PIVOT/REFINE operators; severity S1–S4
- G8 tenant_policies.yaml: per-tenant isolation; SPIFFE SVID; policy server non-delegatable

---

## 1. Executive Summary

Research loops are autonomous multi-step investigations that formalize hypotheses as Gherkin BDD specs, route them through a fleet of specialist agents, and produce synthesis reports with verifiable citation provenance. The architecture is built on three pillars: **deterministic hypothesis expression** (Gherkin DSL), **operator-driven execution** (DRAFT/DEBUG/IMPROVE loops inherited from G7), and **anti-hallucination verification** (fail-closed citation checking with zero ungrounded statements).

Under OPTION_2_STANDARD, research agents autonomously investigate, analyze, and draft syntheses, but human review is required at high-leverage gates: hypothesis authorization, synthesis sign-off, and release approval. The architecture inherits G5 evaluation (trajectory-as-truth, dual-judge, trust score), G6 SDD (spec is durable, code is disposable), G7 bounded improvement (DRAFT/DEBUG/IMPROVE operators with thrashing guards), and G8 tenant isolation (per-tenant SVIDs, policy server, zero cross-tenant leakage).

**Ultimate Engineering Objective (BLUE §G9):** *Research that is regeneratable from the hypothesis spec, methodologically auditable, and self-healing, with human review only at high-leverage gates.*

---

## 2. Hypothesis Formalization (Gherkin BDD)

### 2.1 Why Gherkin for Research Hypotheses

A research hypothesis is a testable proposition. Gherkin BDD (Given/When/Then) provides a deterministic, human-readable grammar that makes hypotheses:

1. **Machine-parseable** — the HYPOTHESIS_DSL_SPEC.md (Step C) defines EBNF grammar for structural validation
2. **Regeneratable** — the hypothesis spec is the durable artifact; the investigation is disposable (SDD principle from G6/WP-S5)
3. **Auditable** — each hypothesis has a clear acceptance criterion that the evaluation harness can verify
4. **Traceable** — Gherkin scenarios link to trajectory records (G5 Mission → Scene → Thought → Action → Observation → Verdict)

### 2.2 Hypothesis Gherkin Structure

```gherkin
@hypothesis @research @domain:<domain_tag>
Feature: <Hypothesis Title>
  As a research agent fleet
  I want to <investigation_objective>
  So that <scientific_or_engineering_goal>

  Scenario: <Primary Investigation Scenario>
    Given <prior_knowledge_context>
      And <available_data_sources>
      And <tool_fleet_configuration>
    When <investigation_procedure>
    Then <expected_finding_condition>
      And <citation_grounded_assertion>
      And <confidence_threshold_met>

  Scenario: <Contradiction Detection Scenario>
    Given <hypothesis_state: DRAFT>
    When <contradictory_evidence_detected>
    Then <hypothesis_state: DEBUG>
      And <contradiction_logged_with_provenance>

  Scenario: <Synthesis Sign-off Scenario>
    Given <hypothesis_state: IMPROVE_COMPLETE>
      And <all_citations_verified>
      And <confidence_threshold_met>
    When <synthesis_drafted>
    Then <synthesis_state: PENDING_HITL_SIGNOFF>
```

### 2.3 Hypothesis State Machine

Hypotheses transition through states governed by the DRAFT/DEBUG/IMPROVE operator cycle:

```
PROPOSED → DRAFT → DEBUG → IMPROVE → VALIDATED → PENDING_HITL → APPROVED
                ↑           |          |
                |___________|__________|
                    (refine loop, max 3)
```

| State | Meaning | Operator | HITL Required |
|---|---|---|---|
| PROPOSED | Hypothesis authored, not yet investigated | (entry) | Yes (HG-01 Hypothesis Auth) |
| DRAFT | Initial synthesis being composed | DRAFT | No |
| DEBUG | Citation/methodology audit in progress | DEBUG | No |
| IMPROVE | Iterative refinement based on DEBUG findings | IMPROVE | No |
| VALIDATED | All citations verified, confidence threshold met | (eval) | No |
| PENDING_HITL | Synthesis ready for human sign-off | (gate) | Yes (HG-05 Synthesis Sign-off) |
| APPROVED | Human-approved; eligible for release | (gate) | Yes (HG-07 Release Approval) |
| REJECTED | Hypothesis invalidated or ethics violation | (terminal) | Yes (logged) |

---

## 3. Execution Operators (DRAFT / DEBUG / IMPROVE)

### 3.1 Operator Inheritance from G7

G9 inherits the DRAFT/DEBUG/IMPROVE operators from G7 PIVOT_REFINE_TREE.md but specializes them for research loops. G7's operators act on self-improvement proposals; G9's operators act on research hypotheses and synthesis artifacts.

### 3.2 DRAFT Operator — Synthesis Composition

**Purpose:** Compose the initial research synthesis from retrieved literature, data, and analysis.

**Inputs:** Hypothesis Gherkin spec, retrieved papers/data, fleet agent contributions.

**Process:**
1. Parse hypothesis Gherkin → extract investigation objective + acceptance criteria
2. Route sub-tasks to specialist agents (literature search, data analysis, methodology audit)
3. Collect agent contributions via A2A task state machine (G4 handshake)
4. Compose synthesis draft with inline citation placeholders
5. Emit trajectory record (G5 Mission → Scene → Thought → Action → Observation → Verdict)

**Outputs:** DRAFT synthesis with citation placeholders, trajectory log.

**Constraints:**
- Every factual assertion must have a citation placeholder or be marked `[UNVERIFIED]`
- No assertion may be presented as confirmed without evidence
- Trust score must be ≥ 0.70 to enter DRAFT (G5 threshold)
- DRAFT is autonomous under OPTION_2 — no HITL required

### 3.3 DEBUG Operator — Citation & Methodology Audit

**Purpose:** Audit the DRAFT synthesis for citation integrity, methodological soundness, and contradiction detection.

**Inputs:** DRAFT synthesis, citation registry, source corpus.

**Process:**
1. For each citation placeholder: resolve to source, extract verbatim quote, verify contextual accuracy
2. For each `[UNVERIFIED]` assertion: flag for IMPROVE or removal
3. Run methodology audit: check sample size, statistical validity, reproducibility
4. Run contradiction detection: cross-reference assertions against source corpus
5. Emit debug report with severity-tagged findings (S1–S4 per G7)

**Outputs:** Debug report, annotated synthesis with verified/unverified/contradicted markers.

**Constraints:**
- Fail-closed: if a citation cannot be resolved, the assertion is marked `CITATION_FAILED` (not silently dropped)
- Contradictions trigger state transition to DEBUG (re-investigate)
- S1 findings (fabricated citations) freeze the hypothesis and trigger HG-04 (Low Evidence gate)

### 3.4 IMPROVE Operator — Iterative Refinement

**Purpose:** Refine the synthesis based on DEBUG findings — add missing citations, remove unsupported assertions, strengthen methodology.

**Inputs:** Debug report, annotated synthesis.

**Process:**
1. For each S2/S3 finding: apply fix (add citation, rephrase, remove assertion)
2. For each S4 finding: log and monitor (no auto-fix)
3. Re-run citation verification on modified assertions
4. Re-run contradiction detection
5. If all citations verified AND no S1/S2 findings remain → transition to VALIDATED
6. If refinement count ≥ 3 → escalate to HG-05 (Synthesis Sign-off) for human review (thrashing guard)

**Outputs:** Improved synthesis, verification log, state transition decision.

**Constraints:**
- Max 3 IMPROVE cycles per hypothesis (inherited from G7 version ceiling)
- S1 findings cannot be auto-fixed — always escalate to HITL
- IMPROVE is autonomous for S3/S4 findings; HITL for S1/S2

---

## 4. Progressive Disclosure Skill Integration (H_CONTEXT)

### 4.1 Paper-as-Knowledge Context Type

G9 extends the G3 six-context-type model (Instructions, Knowledge, Memory, Examples, Tools, Guardrails) with a research-specific subtype: **Paper-as-Knowledge**. Academic papers are loaded as Knowledge context via progressive disclosure:

- **L1 (always loaded):** Title, abstract, key findings, citation metadata (~50 tokens)
- **L2 (on trigger):** Methodology section, results tables, limitations (~200–500 tokens)
- **L3 (on demand):** Full paper text, supplementary materials, raw data references (~2000+ tokens)

### 4.2 H_CONTEXT Harness Coupling

The H_CONTEXT harness (G1 §2) manages research loop context assembly:

| Assembly Step | Source | Budget |
|---|---|---|
| 1. Static instructions | AGENTS.md + domain skill L1 | ≤ 2000 tokens |
| 2. Hypothesis spec | Gherkin feature file | ≤ 1000 tokens |
| 3. Paper knowledge L1 | Title/abstract/metadata per paper (5–15 papers) | ≤ 3000 tokens |
| 4. Paper knowledge L2 | Triggered by hypothesis keywords | ≤ 5000 tokens |
| 5. Tool fleet manifest | CAPABILITY_DISCOVERY.yaml | ≤ 1000 tokens |
| 6. Memory window | Honcho session state (per-tenant) | ≤ 2000 tokens |
| 7. Guardrails | C-RS-* constraints + C-MT-* (G8) | ≤ 1000 tokens |

**Total context budget:** ≤ 15,000 tokens (co-load 5–15 papers, per WP-S3 token economics).

### 4.3 Skill Co-Load Precedence

Research skills co-load in priority order (G3 CC-* precedence):

1. `arxiv` (literature search) — L1 always, L2 on domain match
2. `youtube-content` (transcript synthesis) — L2 on video evidence trigger
3. `llm-wiki` (knowledge base query) — L2 on internal corpus trigger
4. `blogwatcher` (feed monitoring) — L2 on real-time monitoring trigger
5. `polymarket` (prediction market data) — L2 on forecasting trigger
6. G7 `systematic-debugging` — L2 on DEBUG operator activation
7. G5 `test-driven-development` — L2 on validation scenario generation

---

## 5. Evaluation Harness Coupling (H_EVAL)

### 5.1 G5 Trajectory Integration

Every research loop cycle emits a G5 trajectory record:

```
Mission: <hypothesis objective>
Scene: <research sub-task context>
Thought: <agent reasoning about sources>
Action: <tool call or A2A dispatch>
Observation: <tool result or agent response>
Verdict: {continue, success, fail, escalate_HITL}
```

### 5.2 Dual-Judge for Research Synthesis

G5's dual-judge model (LLM-as-Judge + Agent-as-Judge) applies to research synthesis:

- **LLM-as-Judge:** Evaluates synthesis coherence, logical flow, citation integration. Uses a different model family from the research agent (G5 OPTION_2 constraint: mitigate self-enhancement bias).
- **Agent-as-Judge:** Evaluates methodology soundness, citation accuracy, contradiction detection. Runs on a sampling basis (cost control per G5).

**Judge verdicts are advisory** — they flag for HITL, not auto-rollback (G5 OPTION_2 constraint).

### 5.3 Trust Score for Research Agents

G5 trust score [0.0, 1.0] applies to each research agent in the fleet:

| Threshold | Action |
|---|---|
| ≥ 0.85 | Normal operation |
| 0.70–0.84 | Warning; LLM-as-Judge sampling rate doubled |
| 0.50–0.69 | HITL review; agent contributions flagged for human audit |
| < 0.50 | Circuit breaker trip; agent quarantined; hypothesis frozen |

**G8 per-tenant scoping:** Trust scores are isolated per tenant. A research agent's trust score in Tenant A does not affect Tenant B (C-MT-04).

### 5.4 Research-Specific Evaluation Metrics

| Metric | Definition | Threshold |
|---|---|---|
| Citation accuracy | Verified citations / total citations | ≥ 0.95 |
| False-positive rate | Unsupported assertions flagged as confirmed | ≤ 0.05 |
| Methodology compliance | Scenarios passing methodology audit | ≥ 0.85 |
| Contradiction detection rate | Contradictions caught / contradictions present | ≥ 0.80 |
| Regeneratability score | Hypothesis reproducible from spec alone | 1.0 (binary) |

---

## 6. Anti-Hallucination Citation Mechanics

### 6.1 The Zero Ungrounded Statement Constraint

**C-RS-07 (core constraint, see §8):** No assertion in a research synthesis may be presented as fact without a verified citation. Unverified assertions must be explicitly marked `[UNVERIFIED]` or removed.

### 6.2 Citation Verification Pipeline

```
Assertion in DRAFT
    ↓
Citation placeholder exists?
    ├── NO → Mark [UNVERIFIED] → DEBUG flags
    └── YES → Resolve to source
                ↓
                Source exists and is accessible?
                ├── NO → Mark CITATION_FAILED → DEBUG flags S2
                └── YES → Extract verbatim quote from source
                            ↓
                            Quote supports assertion context?
                            ├── NO → Mark CITATION_MISREPRESENTED → DEBUG flags S1
                            └── YES → Mark CITATION_VERIFIED → assertion confirmed
```

### 6.3 Citation Provenance Schema

Every citation carries a provenance record:

| Field | Type | Required |
|---|---|---|
| citation_id | ULID | Yes |
| assertion_text | string | Yes |
| source_type | enum (paper, dataset, code, web, internal) | Yes |
| source_uri | string | Yes |
| source_title | string | Yes |
| source_authors | list[string] | Yes |
| source_date | ISO 8601 | Yes |
| verbatim_quote | string | Yes |
| contextual_accuracy | enum (SUPPORTS, PARTIALLY_SUPPORTS, CONTRADICTS) | Yes |
| verification_status | enum (VERIFIED, FAILED, MISREPRESENTED) | Yes |
| verified_by | enum (agent, human) | Yes |
| verification_timestamp | ISO 8601 | Yes |

### 6.4 Paper Citation Mechanics (WP-S3 Progressive Disclosure)

Citations to academic papers follow progressive disclosure:

- **L1 citation (always present):** Author et al., Year, Title — sufficient for bibliography
- **L2 citation (on audit):** Methodology context, result excerpt — sufficient for DEBUG verification
- **L3 citation (on deep audit):** Full paper section, supplementary data — sufficient for S1 investigation

---

## 7. HITL Intervention Modes (7 Gates)

G9 defines 7 HITL intervention modes, each triggered by a specific research loop condition:

| Gate | ID | Name | Trigger | Action |
|---|---|---|---|---|
| HG-RS-01 | Hypothesis Auth | Hypothesis authorization | New hypothesis submitted | Human reviews hypothesis for scientific validity, ethics, and scope before investigation begins |
| HG-RS-02 | Tool Access | Research tool authorization | New external API or data source requested | Human approves/denies tool access; checks procurement tier (T1–T4) and G8 policy compliance |
| HG-RS-03 | High Drift | High hypothesis drift | Hypothesis scope changes > 30% from original spec | Human reviews scope change; approves pivot or orders re-investigation |
| HG-RS-04 | Low Evidence | Low evidence confidence | Evidence confidence < threshold after IMPROVE cycle | Human reviews evidence quality; orders additional investigation or rejects hypothesis |
| HG-RS-05 | Synthesis Sign-off | Synthesis approval | Synthesis reaches VALIDATED state | Human reviews synthesis for scientific integrity, citation completeness, and ethical boundaries |
| HG-RS-06 | Exfiltration Gate | Data egress control | Research output ready to leave tenant boundary | Human approves data egress; G8 policy server enforces cross-tenant checks |
| HG-RS-07 | Release Approval | Final release authorization | Synthesis approved and ready for publication/distribution | Human grants final approval for release; BLUE §G9: "human review only at high-leverage gates" |

### 7.1 HITL Gate Interaction with Operators

| Operator | HITL Gates Active |
|---|---|
| DRAFT | HG-RS-01 (before), HG-RS-02 (if new tool needed) |
| DEBUG | HG-RS-03 (if drift detected), HG-RS-04 (if evidence low) |
| IMPROVE | HG-RS-03, HG-RS-04, HG-RS-05 (after max 3 cycles) |
| Post-IMPROVE | HG-RS-05 (sign-off), HG-RS-06 (egress), HG-RS-07 (release) |

---

## 8. Domain Constraints (C-RS-01 to C-RS-08)

G9 adds 8 new constraints to the constraint catalog. These tighten (never relax) inherited G1–G8 constraints.

| ID | Constraint | Enforcement | Inherited From |
|---|---|---|---|
| **C-RS-01** | Hypothesis must be expressed in Gherkin BDD before investigation begins | H_CONSTRAINT: structural validation at hypothesis submission | G6 SDD (spec is durable) |
| **C-RS-02** | Research fleet agents must use A2A task state machine for multi-step coordination | H_CONSTRAINT: G4 handshake SM enforcement | G4 MULTI_AGENT_TOPOLOGY |
| **C-RS-03** | Paper knowledge must follow L1→L2→L3 progressive disclosure | H_CONTEXT: token budget enforcement | G3/WP-S3 co-load |
| **C-RS-04** | Every research cycle must emit a G5 trajectory record | H_EVAL: trajectory-as-truth | G5 EVALUATION_HARNESS_SPEC |
| **C-RS-05** | Citation verification is fail-closed: unresolved citations block synthesis | H_CONSTRAINT: DEBUG operator enforcement | WP-S4 slopsquatting defense |
| **C-RS-06** | Research agents must carry per-tenant SVIDs for all tool calls | H_CONSTRAINT: G8 policy server | G8 C-MT-06, C-MT-07 |
| **C-RS-07** | Zero ungrounded statements: no assertion as fact without verified citation | H_CONSTRAINT: citation verification pipeline | WP-S4 zero ambient authority |
| **C-RS-08** | Human review required at 7 high-leverage gates before synthesis/release | H_EVAL: HITL gate enforcement | BLUE §G9: "human review only at high-leverage gates" |

---

## 9. Multi-Agent Research Fleet Architecture

### 9.1 Fleet Topology (G4 Inheritance)

Research fleets use the G4 `hierarchical_coordinator_specialists` pattern:

```
Research Coordinator (L3)
├── Literature Search Specialist (A2A)
├── Data Analysis Specialist (A2A)
├── Methodology Audit Specialist (A2A)
├── Citation Verification Specialist (A2A)
└── Synthesis Composer Specialist (A2A)
```

- **Coordinator:** Routes sub-tasks, collects results, manages hypothesis state machine
- **Specialists:** Autonomous within their domain; communicate via A2A task SM (NEEDS_INPUT → IN_PROGRESS → COMPLETED/FAILED)
- **L4:** false — no agent creates other agents (G7 HB-01)
- **Max concurrent:** 3 specialists (G8 per-tenant; Hermes `delegation.max_concurrent_children=3`)

### 9.2 A2A Task State Machine (G4 Inheritance)

```
PROPOSED → ACCEPTED → IN_PROGRESS → COMPLETED
                |          |              |
                |          ↓              ↓
            REJECTED   NEEDS_INPUT    FAILED
                |          |
                ↓          ↓
            (logged)   (back to coordinator)
```

- `NEEDS_INPUT` prevents infinite GOTO tool-wrap (WP-S2 GOTO problem)
- Each specialist carries a G4 Agent Card with capabilities, tools, and trust score
- Cross-tenant specialist dispatch requires HG-RS-06 (Exfiltration Gate) approval

### 9.3 Debate Protocol (Step D: debate_protocol.yaml)

Multi-agent research fleets may enter **debate mode** when specialists produce conflicting analyses. The debate protocol governs:

1. **Stance declaration:** Each specialist declares its position with evidence
2. **Evidence exchange:** Specialists share citations and methodology
3. **Convergence attempt:** Coordinator attempts synthesis of positions
4. **Consensus or split report:** If consensus reached → proceed to IMPROVE; if not → split report with both positions flagged for HITL (HG-RS-05)

See `debate_protocol.yaml` (Step D) for declarative parameters.

---

## 10. G5/G6/G7/G8 Inheritance Summary

| Domain | Inherited Mechanism | G9 Application |
|---|---|---|
| G5 | Trajectory schema | Every research cycle emits Mission→Scene→Thought→Action→Observation→Verdict |
| G5 | Dual-judge | LLM-as-Judge evaluates coherence; Agent-as-Judge evaluates methodology |
| G5 | Trust score [0.0, 1.0] | Per-agent trust; < 0.50 → quarantine; per-tenant isolation (G8) |
| G5 | Circuit breaker | 15 FM trip triggers + 3 CRITICAL (secret, PII, budget) apply to research agents |
| G5 | 5%/15% thresholds | 5% auto-flag citation errors; 15% HITL for methodology non-compliance |
| G6 | SDD (spec durable) | Hypothesis Gherkin is the durable artifact; investigation is disposable |
| G6 | Workspace mode | Research loops run in `agentic_engineering` mode (not dune) |
| G7 | DRAFT/DEBUG/IMPROVE | Operators specialized for research (§3 above) |
| G7 | Severity S1–S4 | S1 = fabricated citation (freeze+HITL); S2 = misrepresentation; S3 = missing citation; S4 = minor phrasing |
| G7 | Thrashing guard | Max 3 IMPROVE cycles per hypothesis; > 3 → HITL |
| G7 | Loop budget | 10 research proposals per session (inherited HB-08) |
| G8 | Per-tenant isolation | Research agents carry per-tenant SVIDs; trust scores isolated |
| G8 | Policy server | All tool calls pass through policy server; non-delegatable |
| G8 | SPIFFE JWT-SVID | 15-minute TTL; research loops handle rotation for long investigations |

---

## 11. Option Decision Matrix

**Research Strategy Status: LOCKED (`G9_RESEARCH_FLEET_LOCKED_v1`)**
- Autonomous investigation + human-gated synthesis & ethical review.
- Autonomous investigation maximizes research velocity while 7 HITL gates protect scientific integrity.

---

## 12. Verification & Telemetry Requirements

Per BLUE §G9, the following telemetry must be reported at the HITL gate:

| Telemetry | Definition | Source |
|---|---|---|
| Accuracy vs ground truth | Synthesis accuracy on known-answer research questions | Step E validation (post-gate) |
| False-positive rate | Unsupported assertions presented as confirmed | DEBUG operator log |
| Methodology compliance score | Scenarios passing methodology audit | Agent-as-Judge sampling |

**Pre-gate (Steps A–D):** Declarative artifacts only. No codegen, no validation runs.
**Post-gate (Steps E–F):** Validation against known-ground-truth research questions; measure accuracy, false-positive confidence, contradiction detection. Tag `research-loop-v1.0.0`.

---

## 13. Cross-Artifact Consistency

All G9 artifacts reference:
- **BLUE resume token:** `G9_RESEARCH_FLEET_LOCKED_v1`
- **Upstream tag:** `multitenant-v1.0.0`
- **Overlay:** `OPTION_2_STANDARD`
- **Constraint IDs:** C-RS-01 to C-RS-08 (new) + C-MT-01 to C-MT-08 (inherited from G8)
- **HITL gates:** HG-RS-01 to HG-RS-07

---

*RESEARCH_LOOP_ARCHITECTURE.md · G9 Step A · Premium Frontier · DRAFT_PRE_GATE · 2026-07-25*
