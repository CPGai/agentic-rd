# G4 Migration Context — from G3 Context Layer Lock

**Generated:** 2026-07-24  
**Upstream gate:** G3 APPROVED · `G3_CONTEXT_LAYER_LOCKED_v1`  
**Downstream resume (expected):** `G4_TOPOLOGY_APPROVED_v1`  
**Domain:** G4 — Multi-Agent Orchestration

---

## 1. What G3 locked (do not re-open lightly)

| Artifact | Role |
|---|---|
| `specs/g3_memory/CONTEXT_ENGINEERING_BLUEPRINT.md` | Six types, L1–L3, token economics, co-load precedence |
| `specs/g3_memory/SESSION_STATE_SPEC.md` | Assembly order, compaction, lifecycle hooks, namespaces |
| `specs/g3_memory/HONCHO_INTEGRATION_MATRIX.yaml` | Honcho services, derive model telemetry, redaction, ceilings |
| `specs/g3_memory/token_budget.yaml` | Window share buckets + debit order |
| `specs/g3_memory/MEMORY_LOAD_POLICY.yaml` | Proactive vs reactive memory matrix |
| `specs/g3_memory/SKILL_COLOAD_AUDIT.yaml` | Precedence ranks + conflict classes |
| `skills/software-development/*` (5 seeds) | Workspace progressive-disclosure index |
| `scripts/g3_memory/` + `scripts/verify_g3_memory.py` | Structural helpers + pack gate |
| `tests/test_g3_memory.py` | unittest co-load / compaction / L1 |

**Tag:** `context-v1.0.0`

---

## 2. Inheritance rules for G4

1. Context assembly stays **static → skills → tools → knowledge → memory window**.  
2. Tools remain **T1+T2 only** under OPTION_2; RPC broker still `DECLARED_NOT_WIRED` unless G4 needs schema-only A2A.  
3. Memory is advisory — never overrides Constraint catalog or AGENTS sandbox.  
4. **No L4 / AgentCreator**; skill auto-evolution remains OPTION_3/G7.  
5. A2A Agent Cards may be schema-only until G4 HITL clears topology.  
6. Session isolation + Honcho loopback posture at G3; multi-tenant hard isolation remains G8.

---

## 3. Carry-over residual risks

| Risk | Severity | Owner |
|---|---|---|
| Honcho `AUTH_USE_AUTH=false` | MED | G8 |
| Postgres trust on loopback | MED | G8 |
| hermes-api-bridge non-loopback `:8642` | HIGH | G8 |
| Profile skill library drift vs workspace seeds | LOW | G3 ops / future seed sync |
| Nested multi-agent session event translation | MED | G4 (WP-F3 interoperability) |

---

## 4. Suggested G4 Step A inputs

- BLUE §G4  
- WP / Course on A2A / multi-agent (as listed in BLUE)  
- Locked G2 registry + G3 session/memory assembly  
- Live Hermes delegation config (max concurrent children, depth)

---

## 5. Verification before G4 edits

```bash
wsl -d Ubuntu-24.04 bash -c "cd /home/carlospg/workspace/agentic-rd && source .venv-hermes/bin/activate && python scripts/verify_g3_memory.py && python -m unittest tests.test_g3_memory -v && python scripts/verify_g2_tools.py"
```

---

## 6. HITL reminder

G4 must **HARD_STOP** at its own gate with `G4_TOPOLOGY_APPROVED_v1` — do not treat G3 approval as G4 approval.
