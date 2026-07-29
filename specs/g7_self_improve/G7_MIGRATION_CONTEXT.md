# G7 Migration Context — Domain G6 Handoff

**From Domain:** G6 (Vibe Coding → Spec Harness)  
**To Domain:** G7 (Self-Improvement / L4 gated)  
**Handoff Date:** 2026-07-24  
**G6 Status:** APPROVED (`G6_VIBE_ENV_LOCKED_v1`)  
**G6 Tag:** `vibecoding-v1.0.0`  
**Overlay:** OPTION_2_STANDARD

---

## 1. G6 Outputs (Locked Artifacts)

| Artifact | Size | Role |
|---|---|---|
| `specs/g6_vibe/VIBECODING_SPECTRUM.md` | 291 lines | Vibe-to-agentic spectrum, transition triggers, SDD, model routing, G5 inheritance |
| `specs/g6_vibe/SURFACE_CAPABILITY_MATRIX.yaml` | 384 lines | Surface inventory (6 surfaces), BLUE slash commands, hooks, IDE extensions, skills hub, procurement |
| `specs/g6_vibe/vibe_environment.yaml` | 274 lines | Workspace mode config (dune vs production), 9 transition triggers, SDD, G5 integration |
| `specs/g6_vibe/slash_command_mappings.yaml` | 304 lines | BLUE→Hermes command mappings, native commands, routing matrix (10 entries) |
| `specs/g6_vibe/AGENTS_INHERITANCE_RULES.md` | 212 lines | Inheritance chain, per-surface rules, dune relaxation, G5 eval inheritance |
| `specs/g6_vibe/G6_MIGRATION_CONTEXT.md` | — | From G5 handoff |
| `tests/test_g6_vibe.py` | 580 lines | 93 stdlib unittests (10 classes) |
| `scripts/verify_g6_vibe.py` | 337 lines | Standalone pack verifier (203 checks) |

**Verification:**
- Unittest suite: 93/93 OK
- Pack verifier: 203/203 OK
- 0 secrets found across all artifacts

---

## 2. Key G6 Architecture Decisions for G7

### 2.1 Three-Stage Spectrum
G6 defines a continuum from Vibe Coding → Structured AI-Assisted → Agentic Engineering across 5 dimensions. G7 self-improvement operates primarily at the Agentic Engineering end of this spectrum — any automated capability expansion must respect the SDD pattern and evaluation gates.

### 2.2 Prototype Dune vs Production Path
- **Prototype dune** (`/yolo`): approval bypass, no eval gates, disposable code, time-boxed — confined to `prototype/*` or `dune/*` branches
- **Production path**: SDD, eval gates active, circuit breaker active, checkpoint protocol mandatory, PII scrubbing mandatory

**G7 impact:** Self-improvement mutations MUST be confined to prototype dunes initially. Any automated codegen or capability expansion that affects production paths must pass through:
1. Dune experimentation → 2. Human review → 3. Spec-first refactor → 4. Eval gates → 5. HITL approval

### 2.3 Slash Command Surface
G6 maps BLUE Meta-Prompts to Hermes-native surfaces:
- `/goal` — Hermes-native standing goal (primary Orchestrator mode mechanism)
- `/grill-me` — NOT Hermes-native; BLUE Meta-Prompt convention mapped to `/steer` or AGENTS.md Glass-box rule
- `/browser` — Hermes-native CDP browser
- `/schedule` — maps to Hermes `/cron` (durable scheduler)
- `/yolo` — approval bypass toggle (vibe coding mode)

### 2.4 Model Routing Inheritance
The AGENTS.md §4 dynamic model-routing matrix is extended with G6 surface-specific routes. G7 must not pin frozen model versions (C-MODEL-01). Self-improvement cycles that augment the routing matrix must be proposed as declarative overlays, not runtime rewrites.

### 2.5 SDD Pattern (WP-S5)
Spec-Driven Development is the default production path:
- Specs in `specs/` (hybrid Markdown+YAML) → Human review → Agent codegen → Tests from Gherkin → Eval gates → HITL
- Code is disposable; spec is durable
- Token economics: YAML for nesting > 3, Markdown for narrative

**G7 impact:** Self-improvement must operate on SPECS, not directly on code. The agent may propose spec modifications; humans approve; codegen follows from approved specs.

---

## 3. G5 Inheritance (Active for Production Paths)

All G5 evaluation mechanisms are inherited by G6 and must be respected by G7:

| Mechanism | Production Path | Prototype Dune |
|---|---|---|
| Trajectory schema | Mandatory | Optional |
| Trust score [0.0,1.0] | Enforced | Not enforced |
| 5%/15% thresholds | Enforced | Not enforced |
| Circuit breaker (15 FM triggers) | Active | Disabled |
| Checkpoint protocol | Mandatory | Optional |
| PII scrubbing | Mandatory | Optional |
| LLM-as-Judge | Enforced (different model family) | Not applicable |
| AgBOM | Mandatory (drift detection) | Not applicable |

---

## 4. Unresolved Risks Carried Forward to G7

| Risk | G6 Severity | G7 Relevance |
|---|---|---|
| Surface integration (Hermes↔Antigravity) not smoke-tested | MED | G7 may test or automate this |
| `/yolo` mode can be accidentally left on in production context | MED | G7 self-audit/guard must detect this |
| Transition triggers are declarative but not enforced at runtime | MED | G7 could build enforcement |
| Model routing matrix is declarative; no runtime router | MED | G7 could implement dynamic routing |
| Spec-to-code pipeline not automated (SDD is manual) | LOW | G7 natural target for automation |
| Token economics guidance not enforced by tooling | LOW | G7 could build enforcement hooks |
| Antigravity CLI not installed in WSL2 | LOW | Procurement gap; G7 may install |
| Serverless Agent Engine is DECLARED_NOT_WIRED | LOW | G10 concern; G7 may prepare |

---

## 5. G7 Pre-Conditions from G6

Before starting G7 self-improvement work:

1. Verify G6 artifacts are intact: `python scripts/verify_g6_vibe.py` must return 203/203
2. Verify G6 unit tests: `python -m unittest tests.test_g6_vibe -v` must return 93/93 OK
3. Confirm L4 is still disabled in `specs/workflow_graph.yaml` (it should be)
4. Confirm G7 gate resume token from BLUE (expected: `G7_SELF_IMPROVE_BOUNDED` or similar)
5. The G7 domain cannot relax any G6 constraint — only tighten

---

## 6. AGENTS.md State (Post-G6)

Current state of key sections for G7:
- §6 HITL Gate Map: G6 marked with `G6_VIBE_ENV_LOCKED_v1`
- §9 Explicit Non-Actions: G4 APPROVED (L3 enabled), G5 APPROVED, G6 APPROVED
- L4 AgentCreator is explicitly forbidden until G7 resume token
- Module files may only tighten AGENTS.md — G7 self-modification must respect this

---

## 7. Workflow Graph G6→G7 Edge

```yaml
# From specs/workflow_graph.yaml
G6:
  state: APPROVED
  locked: true
  tag: vibecoding-v1.0.0
  next_domain: G7
  next_resume_token_expected: G7_SELF_IMPROVE_BOUNDED

G7:
  id: D_G7
  name: self_improvement
  state: READY_FOR_DOMAIN
  requires: [G1_HARNESS_APPROVED_v1, G5]
  primary_harness_touch: [H_EVAL, H_CONSTRAINT]
  enables_level: L4
```

The G5→G6 edge (E115) is active post-G5. The G6→G7 path is unlocked by G1 but G7 has its own HITL gate — G6 does NOT auto-unlock G7.

---

*G7_MIGRATION_CONTEXT.md · Generated from G6 lock at `vibecoding-v1.0.0` · 2026-07-24*