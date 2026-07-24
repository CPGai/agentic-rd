# G3 Migration Context — from G2 Tooling Lock

**Generated:** 2026-07-23  
**Upstream gate:** G2 APPROVED · `OPTION_2_STANDARD` · `G2_TOOL_REGISTRY_LOCKED_v1`  
**Downstream resume (expected):** `G3_CONTEXT_LAYER_LOCKED_v1`  
**Domain:** G3 — Memory & Stateful Agents (Sessions, Skills & Progressive Disclosure)

---

## 1. What G2 locked (do not re-open lightly)

| Artifact | Role |
|---|---|
| `specs/g2_tools/TOOL_REGISTRY.md` | Tool/MCP/A2A/A2UI/UCP catalog + procurement |
| `specs/g2_tools/MCP_COMPAT_MATRIX.yaml` | Transport/auth/rate/allowlist matrix |
| `specs/g2_tools/PROCUREMENT_TIER_MATRIX.yaml` | T1–T4 risk ceilings, latency, LRO HITL |
| `specs/g2_tools/broker_config.yaml` | Broker ACL seat (schema; not runtime-wired) |
| `specs/g2_tools/timeout_budgets.yaml` | Adaptive timeouts + 10s LRO |
| `specs/g2_tools/TOOL_DISCLOSURE_POLICY.md` | RAG-for-tools policy |
| `specs/g2_tools/skills_registry.json` | L1 skill/MCP bridge index (handoff seed) |
| `specs/g2_tools/pins/npm-mcp-pins.json` | `@upstash/context7-mcp@3.2.4` |
| `scripts/g2_security/*` + `tests/test_g2_security.py` | Structural sanitize / CD / pin / mock RPC |
| `scripts/verify_g2_tools.py` | Pack verifier |

**Runtime note:** MCP broker remains `DECLARED_NOT_WIRED`. G3 must not invent silent live binds outside G2 allowlists.

---

## 2. Inheritance rules for G3

1. **Course-2 supersedes Course-1** (WP-S3 skills/memory over WP-F3 when overlap).  
2. Tools stay **T1+T2 only** under OPTION_2; T4 still dune-only.  
3. Context assembly must call **RAG-for-tools** after skills match (HARNESS_SPEC §2.3):  
   `static pack → skills L1/L2 → tool intent match → knowledge → memory window`.  
4. Memory providers (Honcho live @ loopback) are **G3-owned** for session strategy, budgets, and redaction — but network auth hardening is shared with G8.  
5. `skills_registry.json` is an index stub; G3 authors full progressive-disclosure budgets + `SESSION_STATE_SPEC`.  
6. No L4 / AgentCreator. No payment/A2UI live paths.

---

## 3. Known carry-over risks

| Risk | Severity | Owner |
|---|---|---|
| Honcho `AUTH_USE_AUTH=false` local | MED | G3 policy + G8 |
| `hermes-api-bridge` non-loopback `:8642` | HIGH | G8 (G2 telemetry only) |
| context7 unauthenticated docs egress | MED | broker sanitize (done as policy) |
| Broker not runtime-wired | INFO | future integration task — not G3 scope unless needed for memory tools |

---

## 4. Suggested G3 Step A inputs

- BLUE §G3  
- WP-F3 *Context Engineering: Sessions & Memory*  
- WP-S3 *Agent Skills*  
- G2 `TOOL_DISCLOSURE_POLICY.md` + `skills_registry.json`  
- Live Honcho config (`honcho.json`, Docker stack)

## 5. Verification commands (G2 regression before G3 edits)

```bash
wsl -d Ubuntu-24.04 bash -c "cd /home/carlospg/workspace/agentic-rd && source .venv-hermes/bin/activate && python scripts/verify_g2_tools.py && python -m unittest tests.test_g2_security -v"
```

---

## 6. HITL reminder

G3 starts under OPTION_2 overlay but **must HARD_STOP** at its own gate with `G3_CONTEXT_LAYER_LOCKED_v1` — do not treat G2 approval as G3 approval.
