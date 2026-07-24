# G7 — Self-Improvement Architecture

**Version:** 1.0.0-draft  
**Domain:** G7 — Self-Improving Agents  
**Overlay:** OPTION_2_STANDARD  
**Upstream tag:** `vibecoding-v1.0.0` (G6 LOCKED)  
**BLUE resume token (authoritative):** `G7_IMPROVEMENT_BOUNDS_v1`  
**Workflow graph placeholder alias:** `G7_SELF_IMPROVE_BOUNDED`  
**Status:** DRAFT_PRE_GATE — declarative artifacts only; no production code until Step E

---

## Source Crosswalk

| Source | Authority | Contribution to this spec |
|---|---|---|
| BLUE §G7 (L381–410) | **Authoritative** | HITL gate contract, resume token, decision matrix, Meta-Prompt Steps A–F, required telemetry |
| WP-F1 (L0–L4 Taxonomy) | Course-1 | L4 = Self-Evolving System: meta-reasoning, creates tools/agents on gap detection; HITL on creation events |
| WP-S1 (Factory Model) | Course-2 supersession | Agent = Model + Harness; harness correctness-by-construction; Orchestrator designs improvement loops |
| WP-S3 (Skills) | Course-2 | agentskills.io progressive disclosure; skill anatomy L1–L3; context overflow/rot as primary failure; co-load 5–15 skills |
| WP-S4 (Security & Evaluation) | Course-2 supersession | Effective Trust, trust decay, AgBOM drift detection, checkpoints, stateful circuit breakers — G5 mechanisms that G7 must respect |
| WP-S5 (Spec-Driven Development) | Course-2 supersession | SDD pattern: spec is durable, code is disposable; token economics; G7 operates on SPECS not code |
| G1 `HARNESS_SPEC.md` | Inherited | L4 entry forbidden until G7 resume token; C-LOOP-02 AgentCreator disabled; L4 = meta-Evaluation on capability expansion |
| G5 `EVALUATION_HARNESS_SPEC.md` | Locked input | Flywheel step 5: FEED INTO IMPROVEMENT (G7) — prompt patches, tool updates, skill updates, constitution tighten; 5%/15% thresholds |
| G5 `CIRCUIT_BREAKER_RULES.yaml` | Locked input | Trust score decay engine, quarantine states, checkpoint/rollback protocol — G7 mutations cannot bypass circuit breaker |
| G6 `vibe_environment.yaml` | Locked input | Prototype dune vs production path; SDD config; G5 integration per workspace mode; transition triggers |
| G6 `G7_MIGRATION_CONTEXT.md` | Handoff | G6 outputs, unresolved risks, G7 pre-conditions, workflow graph edge |

**Course-2 supersession note:** WP-F1 frames L4 as "self-evolving system" with meta-reasoning. WP-S1/S3/S4/S5 collectively redefine self-improvement as a **closed-loop harness process** — not a free-standing capability. The agent does not self-modify autonomously; the *harness* detects gaps, acquires capabilities, validates them, and proposes upgrades under human oversight. This spec synthesizes both: WP-F1 provides the L4 taxonomy target; Course-2 papers provide the loop mechanics.

---

## 1. The Closed-Loop Improvement Cycle

### 1.1 Five-Phase Loop (BLUE §G7 normalized domain)

```
    ┌──────────────────────────────────────────┐
    │  1. DETECT                               │
    │  Failure pattern recognized from         │
    │  trajectory telemetry, eval results,     │
    │  or human feedback                       │
    └──────────────┬───────────────────────────┘
                   ▼
    ┌──────────────────────────────────────────┐
    │  2. ACQUIRE                              │
    │  Skill sourced (hub/MCP/native/gen)      │
    │  or spec refinement drafted              │
    │  or prompt patch generated               │
    └──────────────┬───────────────────────────┘
                   ▼
    ┌──────────────────────────────────────────┐
    │  3. VALIDATE                             │
    │  Prototype dune dry-run; eval gates;     │
    │  generalization-gap test; secret scan    │
    └──────────────┬───────────────────────────┘
                   ▼
    ┌──────────────────────────────────────────┐
    │  4. INTEGRATE                            │
    │  HITL review → spec-first refactor →     │
    │  eval gates → approval gate              │
    └──────────────┬───────────────────────────┘
                   ▼
    ┌──────────────────────────────────────────┐
    │  5. MEASURE                              │
    │  Post-integration telemetry; false       │
    │  positive rate; degradation count;       │
    │  thrashing detection; flywheel feedback  │
    └──────────────────────────────────────────┘
                   │
                   └──→ back to 1 (loop continues)
```

### 1.2 Relationship to G5 Flywheel

The G5 Agent Quality Flywheel step 5 ("FEED INTO IMPROVEMENT") is the **entry point** into the G7 loop. G5 produces evaluation findings (degradation, hallucination, intent drift, trust decay); G7 consumes them as detection inputs.

| G5 Flywheel Output | G7 Phase 1 Detection Input |
|---|---|
| Auto-flag (5% degradation) | S3 severity — auto-queue for improvement proposal |
| HITL review (15% degradation) | S2 severity — human-reviewed improvement proposal |
| Hard stop (>15% degradation) | S1 severity — mandatory improvement before resume |
| Circuit breaker trip | S1 severity — freeze + forensic analysis → improvement |
| Red Team finding | S1/S2 — security-focused improvement |
| Agent-as-Judge intent drift | S2 — spec refinement trigger |

### 1.3 Loop Boundary: SDD Compliance

Per G6 inheritance (§2.5 of migration context): self-improvement operates on **SPECS**, not directly on code. The improvement loop may:

- **Propose** spec modifications (declarative artifacts in `specs/`)
- **Draft** skill SKILL.md files (agentskills.io format)
- **Generate** prompt patches (advisory until HITL approval)
- **Suggest** tool adapter patches (schema-level, not runtime)

The loop may **NOT**:
- Directly modify production code (SDD: spec → human review → codegen)
- Rewrite AGENTS.md or HARNESS_SPEC.md (modules may only tighten)
- Modify G5 circuit breaker rules (G5 is locked)
- Enable L4 AgentCreator (requires explicit G7 resume token)
- Bypass prototype dune confinement for any mutation

---

## 2. Detection & Severity Classification

### 2.1 Detection Sources

| Source | Signal Type | Trigger Mechanism | Latency |
|---|---|---|---|
| G5 trajectory verdict `fail` | Discrete | Trajectory record verdict field | Real-time |
| G5 trajectory verdict `escalate_HITL` | Discrete | Trajectory record verdict field | Real-time |
| G5 trust score < 0.85 (warning) | Continuous | Circuit breaker threshold | Real-time |
| G5 trust score < 0.70 (HITL review) | Continuous | Circuit breaker threshold | Real-time |
| G5 trust score < 0.50 (tripped) | Continuous | Circuit breaker immediate trip | Real-time |
| G5 LLM-as-Judge score < threshold | Batch | Eval harness job | Post-run |
| G5 Agent-as-Judge intent drift | Continuous | AgBOM drift detection | Real-time |
| G5 hallucination detected | Batch | LLM-as-Judge hallucination dimension | Post-run |
| G5 Red Team bypass | Event | Adversarial injection suite | Continuous |
| G4 failure mode occurrence | Event | 15 FM trip triggers | Real-time |
| Repeated tool-call errors | Pattern | Error frequency within sliding window | Near real-time |
| Flat fix curve (C-LOOP-02) | Pattern | Fix attempt count without resolution | Near real-time |
| Human feedback (explicit) | Manual | `/steer` command or review UI | Async |
| Token budget anomaly | Metric | Cost per task trending above baseline | Batch |

### 2.2 Severity Classes (S1–S4)

| Class | Name | Trigger Examples | Autonomy Level | Required Approval |
|---|---|---|---|---|
| **S1** | Critical | Secret leak, PII leak, circuit breaker trip, budget ceiling breach, Red Team bypass | **Restricted** — freeze + forensic | HITL mandatory before any improvement action |
| **S2** | High | Intent drift, hallucination, 15% degradation, repeated failure mode (>3 occurrences) | **Human-gated** — propose improvement, HITL reviews | HITL approval before integration |
| **S3** | Medium | 5% degradation, tool selection error, trajectory adherence drop, single FM occurrence | **Advisory** — auto-queue improvement proposal | Auto-integrate low-severity (prompt/token); HITL for behavioral |
| **S4** | Low | Token cost above baseline, minor style/convention deviation, self-repair success rate dip | **Autonomous** — log + monitor; no action unless trend persists | None (log only); escalate to S3 if trend persists ≥3 cycles |

### 2.3 Severity Escalation Rules

1. **S4 → S3**: Same signal persists for ≥3 consecutive improvement cycles without resolution.
2. **S3 → S2**: Same signal recurs after a proposed improvement was integrated (possible regression or insufficient fix).
3. **S2 → S1**: Circuit breaker trips during validation of a proposed improvement (indicates the improvement itself is harmful).
4. **Any → S1**: Secret/PII/budget ceiling detected at any point — immediate escalation regardless of prior severity.

### 2.4 Thrashing Detection

**Thrashing** = repeated improvement proposals for the same signal without convergence. Safeguards:

| Condition | Threshold | Action |
|---|---|---|
| Same signal improved ≥3 times without resolution | Thrash count = 3 | Escalate severity by one class; require HITL |
| Alternating improvements (A→B→A pattern) | Oscillation detected | Freeze auto-integration; HITL must choose direction |
| Improvement integrated then reverted within 5 cycles | Regression detected | Rollback to pre-improvement checkpoint; HITL review |
| Total improvement proposals >10 per session | Loop budget exceeded | Pause improvement loop; HITL must approve continuation |

---

## 3. Acquisition Sources & Co-Load Validation

### 3.1 Procurement Tiers (inherited from G2, extended for G7)

| Tier | Source | G7 Use Case | OPTION_2 Status | Risk |
|---|---|---|---|---|
| **T1** | Hermes native skills (profile `skills/`) | Existing skill already covers the gap — load it | **Enabled** | Lowest — pre-vetted |
| **T2** | agentskills.io hub / vetted MCP | New skill from hub matching detected gap | **Enabled** | Low — hub-curated |
| **T3** | Custom MCP / generated skill (LLM-drafted SKILL.md) | No existing skill — agent drafts new one | **Conditional** — prototype dune only; HITL before integration | Medium — unvetted content |
| **T4** | Ad-hoc prompt patch / inline code | Quick fix, throwaway | **Dune-only** — denied in production | High — no audit trail |

### 3.2 Acquisition Decision Tree

```
DETECTED GAP
    │
    ├── Is there an existing T1 skill that covers this?
    │   ├── YES → Load skill (G3 co-load rules); validate; done
    │   └── NO → Search T2 hub
    │       ├── FOUND → Procure T2 skill; validate; propose integration
    │       └── NOT FOUND → Is this a prototype dune context?
    │           ├── YES → Draft T3 skill (LLM-generated SKILL.md); validate in dune
    │           └── NO → Draft T3 spec proposal only; HITL must approve codegen
    │
    └── Is the gap a prompt/instruction issue (not a skill gap)?
        └── YES → Generate prompt patch (T4); advisory until HITL approves
```

### 3.3 Co-Load Validation Rules (G3 Inheritance)

When a newly acquired skill enters the context harness, it must pass co-load validation:

| Check | Rule | Failure Action |
|---|---|---|
| L1 metadata budget | ≤50 tokens for frontmatter | Reject — trim metadata |
| Co-load count | Total loaded skills ≤15 (G3 rule) | Evict least-relevant skill (LRU) |
| Token budget | New skill L2 body + existing context ≤ session budget | Load L1 only; defer L2 to on-trigger |
| Trigger specificity | Skill trigger condition is non-ambiguous | Reject — rewrite trigger |
| Conflict check | New skill does not contradict loaded skills | Flag conflict; HITL resolves |
| Secret scan | SKILL.md body contains no credentials | Reject + log CRITICAL |

### 3.4 Skill Generation Quality Gates

When an LLM drafts a new skill (T3), the generated SKILL.md must pass:

1. **Structural conformance**: YAML frontmatter valid; `name`, `description`, `tags` present
2. **Progressive disclosure**: L1 ≤50 tokens; L2 body on trigger; L3 references optional
3. **Trigger correctness**: Trigger condition matches the detected gap that prompted generation
4. **No hallucinated APIs**: All tool names, endpoints, and imports must exist in the workspace or declared MCP registry
5. **Generalization-gap test** (§4 below): Skill must not overfit to a single failure instance
6. **Secret scan**: Zero credential patterns
7. **Eval gate**: Skill is exercised against ≥1 benchmark scenario from G5 `EVAL_DATASET_BENCHMARKS.json`

---

## 4. Generalization-Gap Safeguards

### 4.1 The Generalization Gap Problem

A self-improvement loop that overfits to specific failure instances will:
- Patch a symptom without addressing root cause
- Improve performance on seen cases while degrading on unseen cases
- Create skills that are too narrow to trigger on related failures
- Produce prompt patches that memorize rather than generalize

### 4.2 Safeguard Mechanisms

| Safeguard | Implementation | Phase |
|---|---|---|
| **Held-out validation** | Improvement must pass on ≥1 scenario NOT in the detection set | Validate (Phase 3) |
| **Negative test** | Improvement must NOT degrade performance on any existing benchmark | Validate (Phase 3) |
| **Generalization breadth** | Skill trigger must match a *class* of failures, not a single instance | Acquire (Phase 2) |
| **Regression window** | Post-integration, monitor for 5 cycles; any new degradation → rollback | Measure (Phase 5) |
| **Abstraction check** | Prompt patches must reference patterns, not specific tokens from the failure | Acquire (Phase 2) |
| **Cross-domain test** | If improvement targets domain X, verify no degradation on domain Y benchmarks | Validate (Phase 3) |
| **Complexity ceiling** | Generated skill L2 body ≤2000 tokens; prompt patch ≤500 tokens | Acquire (Phase 2) |

### 4.3 Overfitting Detection

```
Improvement proposed for failure F1
    │
    ├── Test on F1 directly → PASS? (expected)
    │   ├── NO → improvement is broken; reject
    │   └── YES → test on held-out F2 (same class, different instance)
    │       ├── PASS → improvement generalizes; proceed
    │       └── FAIL → improvement overfit to F1; reject and widen scope
    │
    └── Test on F3 (different class) → PASS? (regression check)
        ├── YES → no collateral damage; proceed
        └── NO → improvement too broad; narrow scope or reject
```

### 4.4 Rollback Policy

| Rollback Trigger | Mechanism | Scope |
|---|---|---|
| Regression detected within 5 cycles | G5 checkpoint protocol — `git reset` to pre-improvement checkpoint | Single improvement |
| Thrashing detected (§2.4) | Rollback to last stable state; freeze auto-integration | Session-level |
| Circuit breaker trips during validation | Immediate rollback; quarantine improvement proposal | Single improvement + quarantine |
| HITL denies improvement | Rollback if already integrated; discard proposal | Single improvement |
| Secret/PII found in generated skill | Immediate discard; CRITICAL log; scan all recent T3 skills | Session-level forensic |

---

## 5. Human-Gated vs Restricted Autonomy Model

### 5.1 Autonomy Spectrum

```
FULLY AUTONOMOUS ←--------------------------------------------------→ FULLY MANUAL
     |                    |                     |                    |
  S4 (Low)             S3 (Medium)          S2 (High)           S1 (Critical)
  Log + monitor        Advisory queue       Human-gated          Restricted
  No action            Auto-integrate       HITL reviews         Freeze + HITL
                       low-severity         before integration   before any action
```

### 5.2 OPTION_2_STANDARD Autonomy Rules

| Improvement Type | Severity | Autonomy | HITL Required At |
|---|---|---|---|
| Prompt refinement (token-level) | S3/S4 | Auto-integrate | Post-integration log (S4); pre-integration review (S3 if behavioral) |
| Skill acquisition (T1/T2 existing) | S3 | Auto-integrate after validation | Post-integration log |
| Skill generation (T3 new) | S2 | Propose only — dune validation | Before integration into production |
| Spec augmentation | S2 | Propose only | Before spec is committed |
| Tool adapter patch (schema) | S2 | Propose only | Before schema change |
| Tool adapter patch (runtime) | S1 | Restricted — forbidden without HITL | Before any runtime change |
| Constitution tightening (AGENTS.md) | S1 | Propose only — human must edit | Before any edit |
| Circuit breaker rule change | S1 | **Forbidden** — G5 is locked | Never (requires G5 gate reopen) |
| L4 AgentCreator enablement | S1 | **Forbidden** — requires G7 resume token | G7 HITL gate |

### 5.3 Hard Bounds (Non-Negotiable)

These bounds cannot be relaxed by the improvement loop under any OPTION_2 configuration:

1. **L4 AgentCreator remains disabled** until `G7_IMPROVEMENT_BOUNDS_v1` resume token is granted by the human (C-LOOP-02).
2. **No self-modification of constraint catalog** — the agent may propose constraint tightenings but cannot apply them.
3. **No circuit breaker bypass** — G5 trust score and quarantine states are inviolable.
4. **No production code mutation without SDD** — spec → human review → codegen → eval → HITL.
5. **No secret/credential generation** — generated skills/prompts must not create or store credentials.
6. **No cross-profile writes** — improvements target the current profile only.
7. **No host-Windows execution** — all validation runs in WSL2 substrate.
8. **Loop budget** — max 10 improvement proposals per session; pause + HITL to continue.

---

## 6. Pivot/Refine Decision Framework

### 6.1 The Decision Point

After detecting a failure and during the Acquire phase, the improvement loop must decide: **Pivot** (change direction/strategy) or **Refine** (iterate on current approach).

### 6.2 Decision Criteria

| Signal | Pivot | Refine |
|---|---|---|
| Fix curve is flat after ≥3 attempts | ✅ | ❌ |
| Root cause is fundamentally different from assumed | ✅ | ❌ |
| Current approach partially works (intermittent success) | ❌ | ✅ |
| Fix curve is improving (each attempt closer) | ❌ | ✅ |
| Thrashing detected (A→B→A oscillation) | ✅ | ❌ |
| Approach never worked (0% success) | ✅ | ❌ |
| Approach worked but regressed after integration | ❌ | ✅ (with rollback) |
| Budget remaining < 30% | ✅ (cheaper to pivot) | ❌ |
| HITL reviewer suggests different direction | ✅ | ❌ |
| Same FM class but different instance | ❌ | ✅ |

### 6.3 Operators: DRAFT / DEBUG / IMPROVE / PIVOT / REFINE

| Operator | Input | Output | When |
|---|---|---|---|
| **DRAFT** | Detected gap + trajectory context | Proposed spec/skill/prompt (declarative) | Initial improvement proposal |
| **DEBUG** | Proposed improvement + validation failure | Root cause analysis + revised proposal | Validation failed — diagnose why |
| **IMPROVE** | Approved improvement + integration plan | Integrated spec/skill/prompt + post-integration telemetry | HITL approved; integrate |
| **PIVOT** | Failed approach + thrashing signal | New direction declaration + fresh DRAFT | Current direction exhausted |
| **REFINE** | Partial success + fix curve improving | Iterated proposal (v2, v3...) | Iterative refinement within same direction |

### 6.4 Decision Tree (Declarative — see PIVOT_REFINE_TREE.md for full tree)

```
FAILURE DETECTED (S1–S4)
    │
    ├── S1 (Critical)?
    │   └── FREEZE → HITL → human directs PIVOT or REFINE
    │
    ├── S2 (High)?
    │   └── DRAFT → VALIDATE → HITL REVIEW
    │       ├── APPROVED → IMPROVE
    │       └── REJECTED → DEBUG → (REFINE or PIVOT)
    │
    ├── S3 (Medium)?
    │   └── DRAFT → VALIDATE
    │       ├── PASS + no regression → IMPROVE (auto-integrate if low-severity)
    │       └── FAIL → DEBUG → (REFINE or PIVOT based on fix curve)
    │
    └── S4 (Low)?
        └── LOG → MONITOR → escalate to S3 if trend persists
```

---

## 7. Relationship to L4 Self-Evolving System

### 7.1 L4 Taxonomy (WP-F1)

L4 = Self-Evolving System: "Meta-reasoning; creates tools/agents on gap detection." The agent at L4 can:
- Detect capability gaps autonomously
- Create new tools or agents to fill those gaps
- Modify its own harness configuration

### 7.2 G7 as L4 Gate

G7 is the domain that **gates** L4 enablement. Under OPTION_2_STANDARD:

| L4 Capability | Pre-G7 Status | Post-G7 (if token granted) |
|---|---|---|
| Gap detection (Phase 1) | **Enabled** (uses G5 telemetry) | Enabled |
| Skill drafting (Phase 2, T3) | **Enabled in dune only** | Enabled in dune; HITL for production |
| Auto-integrate low-severity (S3/S4) | **Enabled** (prompt/token only) | Enabled |
| Auto-integrate high-severity (S1/S2) | **Disabled** — HITL required | Enabled with constraints |
| AgentCreator (creates new agents) | **Disabled** (C-LOOP-02) | Enabled with HITL per-creation |
| Constraint self-modification | **Disabled** | Disabled (always human-only) |
| Circuit breaker self-modification | **Disabled** | Disabled (always human-only) |

### 7.3 L4 Enablement Path

```
G7 HITL Gate (this domain)
    │
    ├── Human grants G7_IMPROVEMENT_BOUNDS_v1
    │   ├── L4 AgentCreator: still disabled (requires separate explicit enablement)
    │   ├── S1/S2 auto-integration: still HITL-gated
    │   └── T3 skill generation: enabled for production with HITL review
    │
    └── Human does NOT grant token
        ├── Improvement loop operates at S3/S4 autonomy only
        ├── S1/S2: HITL mandatory
        └── L4: fully disabled
```

---

## 8. G5/G6 Inheritance Summary

### 8.1 G5 Inheritance

| G5 Mechanism | G7 Respect |
|---|---|
| Trust score [0.0, 1.0] | Improvement loop cannot modify trust score; improvements are paused when trust < 0.70 |
| Circuit breaker (15 FM triggers) | Improvement validation runs under circuit breaker; trip = rollback |
| Checkpoint protocol | Every improvement integration creates a checkpoint ref for rollback |
| AgBOM drift detection | Improvement that adds tools/skills updates AgBOM; drift triggers PEN-01/PEN-02 |
| LLM-as-Judge | Judge evaluates improvement proposals (advisory, not auto-merge) |
| 5%/15% thresholds | Degradation after improvement integration triggers rollback |
| Red/Blue/Green | Green Team may propose improvements; Blue Team monitors for regression |

### 8.2 G6 Inheritance

| G6 Mechanism | G7 Respect |
|---|---|
| Prototype dune | T3 skill generation + T4 prompt patches confined to dune |
| Production path (SDD) | All production improvements follow spec → review → codegen → eval → HITL |
| Workspace mode | Improvement autonomy scales with mode: vibe (relaxed) → structured (advisory) → agentic (enforced) |
| Transition triggers | TT-04 (verification gap) can trigger improvement loop activation |
| Hooks (DECLARED_NOT_WIRED) | G7 may wire pre_commit hook for secret scan on generated skills |
| Model routing | Improvement loop uses dynamic tiers: Premium for DRAFT, Strong for DEBUG/IMPROVE, Fast for MEASURE |

---

## 9. Residual Risks

| Risk | Severity | G7 Mitigation | Final Owner |
|---|---|---|---|
| Generated skills contain hallucinated APIs | HIGH | Quality gate §3.4.4 + eval benchmark | G7 post-gate |
| Improvement loop thrashes without convergence | HIGH | Thrashing detection §2.4 + loop budget | G7 |
| Overfitting to specific failure instances | MED | Generalization-gap safeguards §4 | G7 |
| L4 enablement too permissive | HIGH | Hard bounds §5.3; L4 path §7.3 | HITL |
| Improvement degrades unrelated domains | MED | Cross-domain test §4.2 + regression window | G7 post-gate |
| Spec modifications drift from BLUE intent | MED | HITL review on all spec augmentations | HITL |
| Loop budget exceeded under load | LOW | Budget cap §5.3.8 + HITL pause | G7 |

---

## 10. Structural Test Intents (Step E deferred)

| ID | Assert |
|---|---|
| ST-G7-01 | Closed-loop has 5 phases: Detect → Acquire → Validate → Integrate → Measure |
| ST-G7-02 | Severity classes S1–S4 enumerated with autonomy levels |
| ST-G7-03 | Acquisition tiers T1–T4 with OPTION_2 status |
| ST-G7-04 | Generalization-gap safeguards include held-out validation + negative test |
| ST-G7-05 | Rollback policy covers regression, thrashing, circuit breaker trip, HITL deny |
| ST-G7-06 | Pivot/Refine decision criteria include flat fix curve + thrashing |
| ST-G7-07 | Operators DRAFT, DEBUG, IMPROVE, PIVOT, REFINE defined |
| ST-G7-08 | L4 AgentCreator remains disabled (C-LOOP-02) |
| ST-G7-09 | Hard bounds list ≥8 non-negotiable rules |
| ST-G7-10 | G5/G6 inheritance tables present |
| ST-G7-11 | OPTION_2_STANDARD marked as recommended path |
| ST-G7-12 | BLUE resume token `G7_IMPROVEMENT_BOUNDS_v1` present |
| ST-G7-13 | No secrets or API keys in spec body |
| ST-G7-14 | Loop budget cap (10 proposals/session) present |
| ST-G7-15 | Thrashing detection thresholds defined |

---

## 11. Option Matrix (BLUE §G7)

| Option | Summary | Pros | Cons | Risks |
|---|---|---|---|---|
| **OPTION_1_CONSERVATIVE** | Full human gate on every proposed skill/spec change | Maximum safety; zero autonomous mutation | No velocity gain; human bottleneck on every improvement | Context rot on long-horizon tasks; improvement loop stalls |
| **OPTION_2_STANDARD** ★ | Low-severity (prompt/token) auto-integrate; high-severity (behavioral) HITL | Balances velocity with safety; non-negotiable that self-modification cannot silently degrade production | Setup overhead; needs G5 eval + circuit breaker active | False positives at S3; judge bias on improvement evaluation |
| **OPTION_3_CREATIVE** | Fully autonomous with 100% reliable automatic rollback | Max velocity; self-healing system | Infinite loop risk; rollback reliability unproven | Cascading self-improvement; production degradation; constraint drift |

**SELECTED_PATH:** `OPTION_2_STANDARD`  
**RATIONALE:** Balances velocity with the non-negotiable requirement that self-modification cannot silently degrade production behavior. G5 circuit breaker + trust score provide the safety net; G6 SDD pattern ensures spec-first discipline. L4 AgentCreator remains disabled — G7 gates the *bounded* improvement loop, not full autonomy.  
**REQUIRED_TELEMETRY:** Detection accuracy, false positives, thrashing events, degradation count.  
**HITL_SIGNAL:** Human must grant `G7_IMPROVEMENT_BOUNDS_v1` before Step E (dry-run simulations) and L4 enablement.

---

## 12. Companion Artifacts (Step D)

| Artifact | Role |
|---|---|
| `triggers.yaml` | Event bindings for autonomous detection (failure thresholds, trajectory anomaly triggers) |
| `oversight_boundaries.yaml` | Explicit rules governing HITL gates vs autonomous execution |
| `PIVOT_REFINE_TREE.md` | Decision trees for DRAFT, DEBUG, IMPROVE, PIVOT, REFINE operators |
| `skill_gen_templates/` | Declarative templates for generating SKILL.md specs |

---

*SELF_IMPROVEMENT_ARCHITECTURE.md v1.0.0-draft — G7 Self-Improving Agents · `vibecoding-v1.0.0` upstream · 2026-07-24*
