# G6 Migration Context — from G5 Evaluation & Observability Lock

**Generated:** 2026-07-24  
**Upstream gate:** G5 APPROVED · `OPTION_2_STANDARD` · `G5_EVAL_FRAMEWORK_APPROVED_v1`  
**Locked tag:** `eval-v1.0.0`  
**Downstream resume (expected):** G6 domain token (BLUE §G6)  
**Domain:** G6 — Vibe Coding → Spec Harness

---

## 1. What G5 locked (do not re-open lightly)

| Artifact | Role |
|---|---|
| `specs/g5_evaluation/EVALUATION_HARNESS_SPEC.md` | Trajectory schema (Mission→Scene→Thought→Action→Observation→Verdict), dual-judge (LLM + Agent), Outside-In/Inside-Out taxonomy, 7-pillar Effective Trust (P1–P7), Red/Blue/Green, Agent Quality Flywheel, 5%/15% thresholds, HITL evaluation, 10 continuous quality metrics, option matrix, 10 structural test intents |
| `specs/g5_evaluation/OBSERVABILITY_PILLARS_SPEC.yaml` | OTEL tracing (5 span types: root/agent/tool/delegate/eval), W3C context propagation, structured JSON logging envelope, 25 telemetry hooks (4 G3 + 4 G4 AP2 + 2 G4 policy + 15 G4 FM), 15 metrics (5 system + 10 quality), 6 dashboard panels, PII scrubbing pipeline (3 steps) |
| `specs/g5_evaluation/CIRCUIT_BREAKER_RULES.yaml` | Trust score (range [0.0, 1.0], initial 1.0, monotonically decreasing, auto_restore=false, manual_hitl restore), 18 decay penalties (PEN-01–PEN-18), trip thresholds (warning 0.85, hitl_review 0.70, trip 0.50), 3 immediate-trip CRITICAL signals, 15 FM trip triggers, 7 actions on trip, 6 quarantine states, checkpoint protocol, AgBOM drift detection |
| `specs/g5_evaluation/EVAL_DATASET_BENCHMARKS.json` | 18 benchmark scenarios (12 failure mode + 2 edge case + 1 red team + 1 quality eval + 2 threshold), coverage matrix (12 G4 FMs covered, 5 WP-S4 pillars), telemetry summary |
| `tests/test_g5_evaluation.py` | 70 unittests (stdlib unittest) |
| `scripts/verify_g5_evaluation.py` | Standalone verifier (147 checks) — repo SoT after lock |

**Tag:** `eval-v1.0.0`

---

## 2. Inheritance rules for G6

1. The trajectory primitive `Mission→Scene→Thought→Action→Observation→Verdict` is the atomic evaluation unit — G6 vibe coding harness must emit trajectories in this schema.
2. Trust score [0.0, 1.0] with monotonically decreasing decay is the runtime trust signal — G6 prototype/vibe paths are subject to the same circuit breaker rules.
3. 5% auto-flag / 15% HITL review / >15% hard stop degradation thresholds are the graduated response — G6 must wire these into its production-vs-prototype boundary.
4. LLM-as-a-Judge uses a different model family from the agent under evaluation — G6 must not relax this.
5. Agent-as-a-Judge runs on sampling basis; verdicts are advisory (flag for HITL, not auto-rollback).
6. Green Team auto-refactors are advisory — patches proposed, not auto-merged.
7. OTEL span hierarchy (root/agent/tool/delegate/eval) must be emitted by any G6 production harness.
8. PII scrubbing pipeline (detect/scrub/audit) must be wired before any trajectory observation is stored.
9. Circuit breaker trip triggers map 1:1 to G4 failure modes — G6 must not add new trip triggers without HITL.
10. Checkpoint protocol (git checkpoint ref before filesystem mutation) must be wired in production paths.

---

## 3. Carry-over residual risks

| Risk | Severity | Owner |
|---|---|---|
| Circuit breaker declared but not wired → trust-decay detection unproven at runtime | MED | G6 (wire in production paths) / G8 (policy enforcement) |
| Intent drift / trust score monitoring not instrumented → no live telemetry yet | MED | G6 / G10 |
| Policy seat DECLARED_NOT_WIRED → no runtime enforcement | MED | G8 |
| LLM-as-a-Judge model family separation not enforced at runtime | MED | G6 / G10 |
| Observability hooks declared but not wired → no live OTEL export | MED | G10 |
| PII scrubbing pipeline declared but not wired → no live PII detection | MED | G8 / G10 |
| Red Team adversarial injection suite not implemented | MED | G6 / G9 |
| Judge agreement rate metric not instrumented | LOW | G10 |
| AgBOM drift detection not wired at runtime | MED | G6 / G10 |
| Agent Quality Flywheel not closed → no feedback loop into G7 self-improvement yet | LOW | G7 |

---

## 4. Suggested G6 Step A inputs

- BLUE §G6 (Vibe Coding → Spec Harness — production vs prototype boundary)
- WP-S1 (The New SDLC with Vibe Coding — vibe coding definition, prototype dunes, production paths)
- WP-S5 (Spec-Driven Production Grade Development — declarative specs, Gherkin, traceability)
- WP-F5 (Prototype to Production — the productionization journey)
- Locked G5 `EVALUATION_HARNESS_SPEC.md` (trajectory schema, dual-judge, thresholds)
- Locked G5 `CIRCUIT_BREAKER_RULES.yaml` (trust score, trip triggers, quarantine states)
- Locked G5 `OBSERVABILITY_PILLARS_SPEC.yaml` (OTEL spans, telemetry hooks, PII scrubbing)
- Locked G4 `FAILURE_MODE_MATRIX.yaml` (15 modes → G6 production constraints)
- Locked G3 `SESSION_STATE_SPEC.md` (compaction/lifecycle → vibe session management)
- Locked G1 `HARNESS_SPEC.md` §3 (Constraint harness — production vs prototype boundary enforcement)

---

## 5. Verification before G6 edits

```bash
wsl -d Ubuntu-24.04 bash -c "cd /home/carlospg/workspace/agentic-rd && source .venv-hermes/bin/activate && python -m unittest tests.test_g5_evaluation -v && python scripts/verify_g5_evaluation.py && python -m unittest tests.test_g4_orchestration -v && python scripts/verify_g4_orchestration.py && python scripts/verify_g3_memory.py && python scripts/verify_g2_tools.py"
```

---

## 6. HITL reminder

G6 starts under OPTION_2 overlay but **must HARD_STOP** at its own gate with the BLUE-specified resume token — do not treat G5 approval as G6 approval.

---

*G5→G6 migration context · `eval-v1.0.0` · 2026-07-24*
