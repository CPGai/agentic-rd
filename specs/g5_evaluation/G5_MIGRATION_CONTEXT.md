# G5 Migration Context — from G4 Multi-Agent Orchestration Lock

**Generated:** 2026-07-24  
**Upstream gate:** G4 APPROVED · `OPTION_2_STANDARD` · `G4_TOPOLOGY_APPROVED_v1`  
**Locked tag:** `orchestration-v1.0.0`  
**Downstream resume (expected):** G5 domain token (BLUE §G5)  
**Domain:** G5 — Evaluation & Observability

---

## 1. What G4 locked (do not re-open lightly)

| Artifact | Role |
|---|---|
| `specs/g4_orchestration/MULTI_AGENT_TOPOLOGY.md` | Pattern catalog, root orchestrator, A2A handshake, AP2 ledger semantics |
| `specs/g4_orchestration/workflow_graph.yaml` | ADK 2.0 multi-agent graph: 7 agents + 1 remote example, 24 edges, decision boundaries |
| `specs/g4_orchestration/agent_cards/*.card.json` (8 cards) | Mock A2A Agent Card registry (root + 6 leaves + 1 remote example) |
| `specs/g4_orchestration/GHERKIN_DECOMPOSITION_TEMPLATES.md` | BDD templates with @agent/@risk/@payment tags, task envelope schema |
| `specs/g4_orchestration/POLICY_INTERCEPT_SPEC.yaml` | Centralised Agent Gateway seat (DECLARED_NOT_WIRED), 8 rules, circuit breaker |
| `specs/g4_orchestration/FAILURE_MODE_MATRIX.yaml` | 15 failure modes, 100% recovery declared, BLUE trio (timeout/region/budget) |
| `tests/test_g4_orchestration.py` | 45 unittests (stdlib unittest) |
| `scripts/verify_g4_orchestration.py` | Standalone verifier (67 checks) |

**Tag:** `orchestration-v1.0.0`

---

## 2. Inheritance rules for G5

1. Multi-agent topology is **hierarchical_coordinator_specialists** (P-HIER primary).  
2. L3 specialists enabled; L4 AgentCreator remains **forbidden** (G7).  
3. Agent Cards are **schema_only** — no live remote A2A under OPTION_2.  
4. AP2 ledger is **schema + spending limits** — `live_settle: false` until explicit commerce gate.  
5. Policy intercept seat is **DECLARED_NOT_WIRED** — wiring deferred to post-gate or G8.  
6. `max_concurrent_children=3`, `max_spawn_depth=1` (nesting off) are current caps.  
7. Failure-mode matrix (15 modes) is the **structural input** for G5 evaluation/observability design.  
8. Trajectory format `Mission→Scene→Thought→Action→Observation→Verdict` carries forward as the G5 eval primitive.  
9. Context assembly order (G3): static → skills → tools → knowledge → memory window — unchanged.  
10. Tools remain **T1+T2 only** under OPTION_2.

---

## 3. Carry-over residual risks

| Risk | Severity | Owner |
|---|---|---|
| Policy seat DECLARED_NOT_WIRED → no runtime enforcement yet | MED | G8 |
| AP2 live settle disabled → commerce paths untested at runtime | LOW | G10 / commerce gate |
| Remote A2A schema-only → no live interoperability validation | MED | G8/G10 |
| Honcho `AUTH_USE_AUTH=false` | MED | G8 |
| hermes-api-bridge non-loopback `:8642` | HIGH | G8 |
| Nested multi-agent session event translation | MED | G5 (trajectory rollup) |
| Circuit breaker declared but not wired → trust-decay detection unproven | MED | G5 |
| Intent drift / trust score monitoring not instrumented | MED | G5 |

---

## 4. Suggested G5 Step A inputs

- BLUE §G5 (Evaluation & Observability)  
- WP-F4 (Agent Quality — outside-in/end-in evaluation, trajectory, LLM-as-judge, agent-as-judge, HITL eval, observability pillars)  
- WP-S4 (Security & Evaluation — vibe trajectory, trust decay, circuit breakers, agent trust score, checkpoints)  
- Locked G4 `FAILURE_MODE_MATRIX.yaml` (15 modes → eval scenarios)  
- Locked G4 `POLICY_INTERCEPT_SPEC.yaml` (circuit breaker inputs/outputs → observability hooks)  
- Locked G3 `SESSION_STATE_SPEC.md` (compaction/lifecycle → trajectory capture)  
- Locked G1 `HARNESS_SPEC.md` §4 (Evaluation harness design)  
- Live Hermes observability surfaces (logs/, OTEL stubs in configs/)

---

## 5. Verification before G5 edits

```bash
wsl -d Ubuntu-24.04 bash -c "cd /home/carlospg/workspace/agentic-rd && source .venv-hermes/bin/activate && python -m unittest tests.test_g4_orchestration -v && python scripts/verify_g4_orchestration.py && python scripts/verify_g3_memory.py && python scripts/verify_g2_tools.py"
```

---

## 6. HITL reminder

G5 starts under OPTION_2 overlay but **must HARD_STOP** at its own gate with the BLUE-specified resume token — do not treat G4 approval as G5 approval.

---

*G4→G5 migration context · `orchestration-v1.0.0` · 2026-07-24*
