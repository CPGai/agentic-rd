# TOOL_DISCLOSURE_POLICY.md
## Domain G2 — Progressive Disclosure (“RAG-for-tools”)

**Version:** 1.0.0  
**Status:** LOCKED · `OPTION_2_STANDARD` · `G2_TOOL_REGISTRY_LOCKED_v1`  
**Anchors:** WP-S2 p.15 · HARNESS_SPEC §2.1–2.3 · `PROCUREMENT_TIER_MATRIX.yaml` · `broker_config.yaml`  
**Companion code gates:** structural tests under `tests/test_g2_*.py` (schema presence only; runtime disclosure engine not wired)

---

## 1. Purpose

Prevent attention dilution and tool-shadowing by ensuring the model sees **only intent-matched tool schemas**, not the global catalog, while Constraint/Broker still enforce allowlists on every call.

---

## 2. Normative rules

| ID | Rule | Enforcement |
|---|---|---|
| D-01 | Static context carries **index only** (name, one-liner, risk, tier, server_id) — never full schemas for all tools | Context Harness assembly |
| D-02 | On mission/thought, retrieve top-k schemas (`k` from tier matrix; default T2 `k=5`, hard max `8`) | Disclosure engine / skill |
| D-03 | Intent match features: lexical overlap on name/description + optional embedding score (implementation deferred) | DECLARED |
| D-04 | Broker filters candidates through ACL **before** schemas enter the prompt | broker_config.acls |
| D-05 | Name collision / semantic shadow → block load + HITL (SEC-SH-01) | broker_config.collision_detection |
| D-06 | After slice success/fail or token pressure, **drop** unused schemas from working context | Context compact step |
| D-07 | High-risk action classes never auto-disclosed without smart/always HITL flag in index | action_classes matrix |
| D-08 | Tools share the dynamic Context bucket (HARNESS ~40–60%); schemas lose to observations under pressure | token budget |
| D-09 | Prefer task-level tools over raw API shards (WP-F2 best practices) | registry authoring |
| D-10 | MCP `annotations` never authorizing force multiplier — display hints only | WP-F2 p.27 |
| D-11 | Payment / A2UI generation / A2A remote cards not disclosed under OPTION_2 live paths | a2a.extensions.*.enabled_option_2=false |
| D-12 | Unauthenticated MCP outputs taint-tagged before re-entry to model | SEC-IN-01 / SEC-LK-01 |

---

## 3. Index record (L1)

```json
{
  "name": "query-docs",
  "server_id": "context7",
  "tier": "T2",
  "risk_class": "LOW_MED",
  "one_line": "Query library docs by Context7 library id",
  "side_effect": "read",
  "hitl": "never",
  "bridge_name": "mcp__context7__query_docs"
}
```

Full JSON-Schema body loads only after D-02–D-05 pass.

---

## 4. Lifecycle

```
mission
  → build/refresh L1 index (allowlisted ∩ enabled)
  → intent-match top-k
  → collision check
  → inject schemas (L2 tool context)
  → model may tools/call
  → broker pre-hook (ACL, sanitize args, HITL)
  → observe + sanitize result
  → score trajectory
  → drop schemas not needed for next slice
```

Sequence diagram: [`TOOL_CALL_SEQUENCE.md`](./TOOL_CALL_SEQUENCE.md).

---

## 5. Token budget guidance

| Phase | Guidance |
|---|---|
| L1 index | ≤ ~1–2k tokens global |
| Per-turn L2 schemas | ≤ top-k full schemas; prefer < 4k tokens combined |
| Observations | Prefer summarized tool results; store raw under artifact ref if large |
| Pressure | Drop lowest-score schemas first; never drop Constraint core |

---

## 6. OPTION_2 surface

**Disclosable:** T1 native families + T2 allowlisted MCP (`context7` tools).  
**Not disclosable in prod profile:** T4, payment tools, A2UI generators, unauthenticated custom servers, any server absent from `broker_config.acls.servers` with `enabled: true`.

---

## 7. Failure modes

| Failure | Action |
|---|---|
| Intent match returns empty | Stay on native dig tools; do not dump full catalog |
| Collision | Deny new schema; log SEC-SH-01 |
| Pin mismatch at connect | Disconnect server; do not disclose its tools |
| Tainted observation with secret pattern | Redact + trajectory `fail`/`escalate` |

---

*TOOL_DISCLOSURE_POLICY.md v1.0.0 — declarative policy lock for G2.*
