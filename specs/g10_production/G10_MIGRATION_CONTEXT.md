# G10 Migration Context — Domain G9 Handoff

**From Domain:** G9 (Autonomous Research Loops)
**To Domain:** G10 (Production AgentOps)
**Handoff Date:** 2026-07-25
**G9 Status:** APPROVED (`G9_RESEARCH_FLEET_LOCKED_v1`)
**G9 Tag:** `research-loop-v1.0.0`
**Overlay:** OPTION_2_STANDARD

---

## 1. G9 Outputs (Locked Artifacts)

| Artifact | Size | Role |
|---|---|---|
| `specs/g9_research/RESEARCH_LOOP_ARCHITECTURE.md` | ~600 lines | Hypothesis state machine, DRAFT/DEBUG/IMPROVE operators, progressive disclosure (H_CONTEXT), evaluation harness coupling (H_EVAL), anti-hallucination citation mechanics, 7 HITL intervention modes, 8 constraints C-RS-01 to C-RS-08, fleet topology, option matrix |
| `specs/g9_research/CAPABILITY_DISCOVERY.yaml` | ~350 lines | 7 academic API providers (arXiv, PubMed, IEEE, Semantic Scholar, OpenAlex, Crossref, CORE), 10 research skills, 4 MCP tools (1 installed, 3 candidates), procurement T1-T4, phase-source mapping, G8 compliance, capability gaps |
| `specs/g9_research/HYPOTHESIS_DSL_SPEC.md` | ~400 lines | EBNF grammar for Gherkin research hypotheses, SV-01 to SV-10 structural validation rules, SEM-01 to SEM-06 semantic validation rules, swarm routing topology, decision vocabulary, fail-closed citation verification state machine |
| `specs/g9_research/debate_protocol.yaml` | ~200 lines | 4 debate triggers (DT-01 to DT-04), stance declaration schema, 3-round evidence exchange, consensus convergence criteria (full/partial/no consensus), split report schema, G5/G7/G8 inheritance |
| `specs/g9_research/operators.yaml` | ~300 lines | DRAFT/DEBUG/IMPROVE operator specs with process steps, decisions, severity S1-S4 classification, cycle tracking (max 3), thrashing guard, state machine, trust score requirements |
| `specs/g9_research/verifiable_reporting.yaml` | ~280 lines | Zero ungrounded statements (C-RS-07), citation provenance schema (13 required fields), 4-level proof-of-source verification (L1-L4), 5 fail-closed rules, 8 anti-hallucination constraints (AH-01 to AH-08), reporting format |
| `specs/g9_research/hitl_intervention_modes.yaml` | ~350 lines | 7 HITL gates (HG-RS-01 to HG-RS-07), gate sequencing, operator-gate interaction, fail-closed rules, G5/G7/G8 inheritance |
| `tests/test_g9_research.py` | ~700 lines | 72 stdlib unittests (10 test classes): architecture, capability discovery, hypothesis DSL, debate protocol, operators, verifiable reporting, HITL modes, hallucination simulation, cross-artifact consistency, secret scan |
| `scripts/verify_g9_research.py` | ~450 lines | Standalone pack verifier (330 checks): file existence, YAML safe-load, MD section grep, structural content, cross-artifact consistency, secret scan, XML/HTML scan, hallucination simulation |

**Verification:**
- Unittest suite: 72/72 OK
- Pack verifier: 330/330 OK
- Hallucination simulation: 5 verified citations, 2 hallucinated caught, 0% false-positive rate, 100% citation provenance coverage
- IMPROVE cycle ceiling: 3 (respected, no infinite thrashing)
- Methodology compliance: SV-01 to SV-10 (100%), SEM-01 to SEM-06 (100%)
- 0 secrets found across all artifacts

---

## 2. Key G9 Architecture Decisions for G10

### 2.1 Gherkin BDD Hypothesis Formalization (C-RS-01)
Research hypotheses are expressed as Gherkin BDD specs with deterministic EBNF grammar. The hypothesis spec is the durable artifact (SDD principle); the investigation is disposable.

**G10 impact:** Production AgentOps must treat Gherkin hypothesis specs as durable artifacts in the CI/CD pipeline. Code generation from hypotheses follows the SDD pattern (spec → review → codegen → eval → HITL).

### 2.2 DRAFT/DEBUG/IMPROVE Operator Cycle (C-RS-05)
Research loops use three operators inherited from G7 but specialized for research: DRAFT (synthesis composition), DEBUG (citation/methodology audit), IMPROVE (iterative refinement). Max 3 IMPROVE cycles per hypothesis.

**G10 impact:** Production pipeline must support the DRAFT/DEBUG/IMPROVE cycle as a CI/CD stage. The 3-cycle ceiling must be enforced by the pipeline, not by prompt instructions.

### 2.3 Fail-Closed Citation Verification (C-RS-07)
Zero ungrounded statements: no assertion as fact without verified citation. Fail-closed means unresolved citations block synthesis (not silently dropped). S1 fabrications freeze the hypothesis and trigger HITL.

**G10 impact:** Production pipeline must include automated citation verification as a quality gate. Syntheses with unresolved citations cannot be deployed. S1 fabrications trigger automatic rollback.

### 2.4 Seven HITL Intervention Modes (C-RS-08)
HG-RS-01 (Hypothesis Auth), HG-RS-02 (Tool Access), HG-RS-03 (High Drift), HG-RS-04 (Low Evidence), HG-RS-05 (Synthesis Sign-off), HG-RS-06 (Exfiltration Gate), HG-RS-07 (Release Approval). Three mandatory (01, 05, 07), four conditional.

**G10 impact:** Production AgentOps must wire all 7 HITL gates into the CI/CD pipeline. The canary deployment stage must check that all mandatory gates are cleared before release. Conditional gates trigger based on runtime conditions.

### 2.5 Multi-Agent Research Fleet (C-RS-02)
Research fleets use G4 hierarchical_coordinator_specialists pattern with A2A task state machine. Max 3 concurrent specialists (G8 per-tenant + Hermes delegation cap).

**G10 impact:** Production deployment must support multi-agent fleet orchestration. The canary must validate that A2A task state machine works under production load.

### 2.6 Progressive Disclosure for Papers (C-RS-03)
Paper knowledge follows L1→L2→L3 progressive disclosure (WP-S3). Total context budget ≤15,000 tokens (5–15 papers co-loaded).

**G10 impact:** Production pipeline must enforce token budgets for research loops. Context overflow detection must trigger compaction or HITL.

### 2.7 G5/G6/G7/G8 Inheritance
Research loops inherit: G5 trajectory-as-truth + dual-judge + trust score + circuit breaker; G6 SDD + workspace mode; G7 DRAFT/DEBUG/IMPROVE + severity + thrashing guard; G8 per-tenant SVID + policy server + isolation.

**G10 impact:** Production AgentOps must integrate all inherited mechanisms into the unified CI/CD pipeline. The canary must validate that per-tenant isolation, circuit breakers, and trust scores work correctly under production conditions.

### 2.8 Eight New Constraint IDs (C-RS-01 to C-RS-08)
G9 adds 8 new constraints to the constraint catalog:
- C-RS-01: Hypothesis must be Gherkin BDD
- C-RS-02: A2A task state machine for fleet coordination
- C-RS-03: Paper progressive disclosure L1→L2→L3
- C-RS-04: G5 trajectory emission for every cycle
- C-RS-05: Fail-closed citation verification
- C-RS-06: Per-tenant SVID for all tool calls
- C-RS-07: Zero ungrounded statements
- C-RS-08: 7 HITL gates at high-leverage points

**G10 impact:** Production AgentOps must enforce all C-RS-* constraints in the CI/CD pipeline. These are in addition to C-MT-* (G8) and all prior domain constraints.

---

## 3. Unresolved Risks Carried Forward to G10

| Risk | G9 Severity | G10 Relevance |
|---|---|---|
| No live research fleet deployment (A2A specialists are schema-only) | HIGH | G10 must deploy actual multi-agent fleet; A2A handshake SM untested under production load |
| Citation verification pipeline is declarative only (no live API calls) | HIGH | G10 must wire actual arXiv/Semantic Scholar API calls; fail-closed behavior untested with real sources |
| No per-tenant skill namespace for research skills | MED | Research loops that generate skills need per-tenant isolation; current skill system is single-tenant |
| Honcho memory unauthenticated (AUTH_USE_AUTH=false) | HIGH | Research loop memory (per-tenant) is unauthenticated; G10 must deploy Honcho with auth or per-tenant namespaces |
| Policy server schema-only (DECLARED_NOT_WIRED) | HIGH | G10 must wire the policy server for production; research tool calls cannot actually pass through it yet |
| SPIFFE/SPIRE not deployed | HIGH | G10 must deploy SPIRE; research agents cannot obtain real SVIDs yet |
| No validation against real ground-truth research questions | MED | Step E used simulated ground truth; G10 should validate against real known-answer research questions |
| Debate protocol untested with real conflicting evidence | MED | Debate mode is declarative; G10 should test with real specialist disagreements |

---

## 4. G9 Pre-Conditions for G10

Before starting G10 production AgentOps:

1. Verify G9 artifacts are intact: `python3 scripts/verify_g9_research.py` must return 330/330
2. Verify G9 unit tests: `python -m unittest tests.test_g9_research -v` must return 72/72 OK
3. Confirm G10 gate resume token from BLUE: `G10_PRODUCTION_DEPLOY_v1`
4. The G10 domain cannot relax any G9 constraint — only tighten
5. Production pipeline must enforce all C-RS-* constraints alongside C-MT-* (G8) and prior domain constraints

---

## 5. AGENTS.md State (Post-G9)

Current state of key sections for G10:
- Section 6 HITL Gate Map: G9 marked with `G9_RESEARCH_FLEET_LOCKED_v1`
- Section 9 Explicit Non-Actions: G9 APPROVED; G10 may proceed under OPTION_2_STANDARD overlays — still stop at G10's own HITL gate
- G10 is the final domain with its own HITL gate — G9 does NOT auto-unlock G10

---

## 6. Workflow Graph G9 to G10 Edge

```yaml
# From specs/workflow_graph.yaml
G9:
  state: APPROVED
  locked: true
  tag: research-loop-v1.0.0
  resume_token: G9_RESEARCH_FLEET_LOCKED_v1
  next_domain: G10
  next_resume_token_expected: G10_PRODUCTION_DEPLOY_v1

G10:
  id: D_G10
  name: production_agentops
  state: READY_FOR_DOMAIN
  requires: [G1_HARNESS_APPROVED_v1, G2, G3, G4, G5, G6, G7, G8, G9]
  primary_harness_touch: [H_CONTEXT, H_CONSTRAINT, H_EVAL]
  resume_token_expected: G10_PRODUCTION_DEPLOY_v1
```

The G9 to G10 path: autonomous research loops must be fully specified and validated before production AgentOps — otherwise the production pipeline cannot enforce citation verification, HITL gates, and fleet orchestration.

---

## 7. BLUE Section G10 Reference

```
Normalized domain: Spec-driven CI/CD (push to .gherkin → regenerate → eval →
policy check → canary → production), Vertex AI Agent Engine / Cloud Run
deployment, enterprise policy server in the live path, OpenTelemetry production
monitoring, automatic rollback, Doctor checks, evidence packs, cultural
safeguards (approval fatigue, token-maxing avoidance), shared accountability
model.

Ultimate engineering objective: Full production-grade AgentOps system that
treats the Gherkin specification as the durable artifact, keeps code disposable,
and requires only one final strategic HITL gate for release.

RESUME_TOKEN: G10_PRODUCTION_DEPLOY_v1
RECOMMENDED_PATH: OPTION_2_STANDARD
```

---

*G10_MIGRATION_CONTEXT.md · Generated from G9 lock at `research-loop-v1.0.0` · 2026-07-25*
