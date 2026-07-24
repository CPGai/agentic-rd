# G7 — Pivot/Refine Decision Tree (Step D)

**Version:** 1.0.0-draft  
**Domain:** G7 — Self-Improving Agents  
**Status:** DRAFT_PRE_GATE  
**Overlay:** OPTION_2_STANDARD  
**Upstream:** `vibecoding-v1.0.0` (G6 LOCKED)  
**BLUE resume:** `G7_IMPROVEMENT_BOUNDS_v1`  

---

## 1. Master Decision Tree

```
IMPROVEMENT TRIGGER FIRED
    │
    ├── Severity?
    │   │
    │   ├── S1 (Critical)
    │   │   └── FREEZE → PRESERVE FORENSICS → HITL GATE (HG-03)
    │   │       ├── Human directs PIVOT
    │   │       │   └── New direction → DRAFT (fresh proposal)
    │   │       ├── Human directs REFINE
    │   │       │   └── Revised approach → DRAFT (iterated)
    │   │       └── Human denies recovery
    │   │           └── QS-LOCKED → session terminated
    │   │
    │   ├── S2 (High)
    │   │   └── DRAFT → VALIDATE (prototype dune)
    │   │       │
    │   │       ├── VALIDATION PASS?
    │   │       │   ├── YES → GENERALIZATION-GAP TEST
    │   │       │   │   ├── PASS → HITL GATE (HG-01 or HG-02)
    │   │       │   │   │   ├── APPROVED → IMPROVE → MEASURE (5-cycle regression window)
    │   │       │   │   │   │   ├── No regression → success; log to ledger
    │   │       │   │   │   │   └── Regression detected → ROLLBACK → REFINE or PIVOT
    │   │       │   │   │   ├── REJECTED → DEBUG
    │   │       │   │   │   │   ├── Root cause found → REFINE (revised DRAFT)
    │   │       │   │   │   │   └── Root cause = wrong direction → PIVOT
    │   │       │   │   │   └── CHANGES REQUESTED → REFINE (incorporate feedback)
    │   │       │   │   └── FAIL (overfit) → reject; widen scope → DRAFT
    │   │       │   └── NO → DEBUG
    │   │       │       ├── Fix curve improving?
    │   │       │       │   ├── YES → REFINE (v2, v3...)
    │   │       │       │   └── NO (flat ≥3) → PIVOT
    │   │       │       └── Thrashing detected?
    │   │       │           ├── YES → PIVOT + freeze auto-integration
    │   │       │           └── NO → REFINE
    │   │       │
    │   │       └── Loop budget exceeded?
    │   │           └── YES → HITL GATE (HG-04) → approve continuation or pause
    │   │
    │   ├── S3 (Medium)
    │   │   └── DRAFT → VALIDATE
    │   │       │
    │   │       ├── VALIDATION PASS?
    │   │       │   ├── YES → GENERALIZATION-GAP TEST
    │   │       │   │   ├── PASS → Is improvement behavioral?
    │   │       │   │   │   ├── NO (token-level) → AUTO-INTEGRATE → MEASURE
    │   │       │   │   │   └── YES → Escalate to S2 → HITL GATE
    │   │       │   │   └── FAIL → reject; widen scope → DRAFT
    │   │       │   └── NO → DEBUG
    │   │       │       ├── Fix curve improving?
    │   │       │       │   ├── YES → REFINE
    │   │       │       │   └── NO (flat ≥3) → PIVOT
    │   │       │       └── Thrashing?
    │   │       │           ├── YES → PIVOT + freeze
    │   │       │           └── NO → REFINE
    │   │       │
    │   │       └── Loop budget exceeded?
    │   │           └── YES → HITL GATE (HG-04)
    │   │
    │   └── S4 (Low)
    │       └── LOG → MONITOR
    │           ├── Trend persists ≥3 cycles?
    │           │   ├── YES → Escalate to S3 → DRAFT
    │           │   └── NO → continue monitoring
    │           └── Record to memory (IT-10)
```

---

## 2. Pivot Decision Criteria

A Pivot is triggered when the current improvement direction is exhausted or fundamentally wrong.

| Criterion | Condition | Rationale |
|---|---|---|
| Flat fix curve | ≥3 fix attempts without resolution | Current approach cannot converge |
| Wrong root cause | Root cause fundamentally different from assumed | Current direction targets wrong problem |
| Thrashing | A→B→A oscillation or ≥3 same-signal improvements | Loop is cycling without progress |
| Zero success | Approach never produced any partial success | Approach is fundamentally broken |
| Budget pressure | Budget remaining < 30% | Cheaper to start fresh than continue iterating |
| HITL directive | Reviewer suggests different direction | Human judgment overrides loop heuristic |
| Circuit breaker trip during validation | Improvement itself triggered a trip | The proposed improvement is harmful |

---

## 3. Refine Decision Criteria

A Refine is triggered when the current direction shows promise but needs iteration.

| Criterion | Condition | Rationale |
|---|---|---|
| Partial success | Approach works intermittently | Core idea is sound; needs tuning |
| Improving fix curve | Each attempt is closer to resolution | Convergence is happening |
| Post-integration regression | Improvement worked but regressed later | Approach is correct; integration needs adjustment |
| Same FM class, different instance | Same failure mode type, different trigger | Pattern is generalizable; skill/prompt needs widening |
| HITL changes requested | Reviewer approved with modifications | Direction is right; details need work |

---

## 4. Operator State Machine

```
                    ┌─────────┐
        ┌──────────→│ DRAFT   │←──────────────┐
        │           └────┬────┘               │
        │                │                    │
        │                ▼                    │
        │           ┌─────────┐               │
        │           │VALIDATE │               │
        │           └────┬────┘               │
        │                │                    │
        │           ┌────┴────┐               │
        │           ▼         ▼               │
        │      ┌────────┐ ┌────────┐          │
        │      │  PASS  │ │  FAIL  │          │
        │      └───┬────┘ └───┬────┘          │
        │          │          │               │
        │          ▼          ▼               │
        │     ┌─────────┐ ┌────────┐          │
        │     │GENERAL. │ │ DEBUG  │──────────┘
        │     │GAP TEST │ └───┬────┘
        │     └────┬────┘     │
        │          │          ├── fix curve improving? → REFINE
        │     ┌────┴────┐     ├── flat ≥3? → PIVOT
        │     ▼         ▼     └── thrashing? → PIVOT
        │ ┌──────┐ ┌──────┐
        │ │ PASS │ │ FAIL │
        │ └──┬───┘ └──┬───┘
        │    │         │
        │    ▼         └──→ widen scope → DRAFT
        │ ┌───────────────┐
        │ │ HITL / AUTO   │
        │ │ INTEGRATE     │
        │ └───────┬───────┘
        │         │
        │         ▼
        │    ┌─────────┐
        │    │ IMPROVE │
        │    └────┬────┘
        │         │
        │         ▼
        │    ┌─────────┐
        │    │ MEASURE │ (5-cycle regression window)
        │    └────┬────┘
        │         │
        │    ┌────┴────┐
        │    ▼         ▼
        │  PASS     REGRESSION
        │    │         │
        │    │         └──→ ROLLBACK → REFINE or PIVOT
        │    │
        └────┘ (success — log to ledger)
```

---

## 5. DRAFT Operator Specification

| Field | Value |
|---|---|
| **Input** | Detected gap ID, trajectory context, severity class, improvement type |
| **Process** | 1. Analyze failure trajectory; 2. Identify root cause; 3. Determine improvement type (IT-01 to IT-10); 4. Draft declarative proposal |
| **Output** | Improvement proposal (spec/skill/prompt/constraint) in declarative form |
| **Model tier** | Premium Frontier (architectural) or Strong Coding (mechanical) |
| **Quality gates** | Must pass: structural conformance, no hallucinated APIs, secret scan |
| **Next state** | VALIDATE |

---

## 6. DEBUG Operator Specification

| Field | Value |
|---|---|
| **Input** | Failed proposal, validation error, trajectory of validation attempt |
| **Process** | 1. Analyze why validation failed; 2. Determine root cause of failure; 3. Check if root cause differs from assumed (→ PIVOT); 4. Check fix curve trend (→ REFINE or PIVOT); 5. Check for thrashing (→ PIVOT) |
| **Output** | Root cause analysis + decision: REFINE (revised DRAFT) or PIVOT (new direction) |
| **Model tier** | Premium Frontier (root cause analysis) |
| **Next state** | DRAFT (via REFINE or PIVOT) |

---

## 7. IMPROVE Operator Specification

| Field | Value |
|---|---|
| **Input** | Approved proposal, integration plan |
| **Process** | 1. Create checkpoint ref (G5 checkpoint protocol); 2. Apply improvement to target artifact; 3. Update AgBOM if tools/skills changed; 4. Run eval gate; 5. Emit post-integration telemetry |
| **Output** | Integrated artifact + post-integration telemetry record |
| **Model tier** | Strong Coding |
| **Quality gates** | Eval gate must pass; no secret scan hits; no AgBOM drift |
| **Next state** | MEASURE (5-cycle regression window) |

---

## 8. PIVOT Operator Specification

| Field | Value |
|---|---|
| **Input** | Failed approach, thrashing signal or flat fix curve |
| **Process** | 1. Declare current direction exhausted; 2. Log failure analysis to improvement ledger; 3. Identify alternative direction; 4. Reset fix attempt counter; 5. Initiate fresh DRAFT |
| **Output** | New direction declaration + fresh DRAFT proposal |
| **Model tier** | Premium Frontier (strategic direction change) |
| **Side effects** | Freeze auto-integration; increment pivot count; if pivot count ≥2 for same signal → escalate to S1 |
| **Next state** | DRAFT (fresh) |

---

## 9. REFINE Operator Specification

| Field | Value |
|---|---|
| **Input** | Partially successful proposal, fix curve trend |
| **Process** | 1. Identify what partially worked; 2. Identify what failed; 3. Adjust proposal (narrow scope, fix parameters, improve trigger); 4. Increment version (v2, v3...); 5. Re-submit to VALIDATE |
| **Output** | Iterated proposal (v2, v3...) |
| **Model tier** | Strong Coding |
| **Version ceiling** | Max 3 refinements per direction; after v3 → DEBUG (decide PIVOT or final attempt) |
| **Next state** | VALIDATE |

---

## 10. Rollback Protocol

```
REGRESSION DETECTED (within 5-cycle window)
    │
    ├── Is improvement auto-integrated (S3/S4)?
    │   └── YES → Immediate rollback (git reset to checkpoint)
    │       └── Log to ledger → REFINE or PIVOT
    │
    ├── Is improvement HITL-approved (S2)?
    │   └── YES → Rollback + notify human
    │       └── Human directs REFINE or PIVOT
    │
    └── Is circuit breaker tripped?
        └── YES → Full rollback + quarantine + HITL (HG-03)
```

---

*PIVOT_REFINE_TREE.md v1.0.0-draft — G7 Step D · 2026-07-24*
