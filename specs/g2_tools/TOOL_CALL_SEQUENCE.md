# TOOL_CALL_SEQUENCE.md
## G2 — Tool call sequence (broker + optional A2A)

**Status:** LOCKED declarative · `OPTION_2_STANDARD`  
**Resume:** `G2_TOOL_REGISTRY_LOCKED_v1`

```mermaid
sequenceDiagram
  autonumber
  actor U as Human / Mission
  participant H as Host (Hermes)
  participant D as Disclosure (RAG-for-tools)
  participant B as MCP Broker (Constraint)
  participant M as Model
  participant S as MCP Server (e.g. context7)
  participant A as A2A Specialist (G4+)

  U->>H: Mission + acceptance
  H->>D: Load L1 tool index (allowlisted)
  D->>M: Static context + L1 index
  M->>D: Intent / plan needs tool X
  D->>B: Candidate schema request
  B->>B: ACL + pin + collision checks
  alt deny / collision
    B-->>D: Deny (+ HITL if required)
    D-->>M: No schema / escalate
  else allow
    B-->>D: Schema bundle
    D->>M: Inject L2 schemas (top-k)
    M->>B: tools/call name args
    B->>B: Sanitize args + HITL gate
    alt HITL required
      B->>U: Approve tool inputs
      U-->>B: approve / deny
    end
    B->>S: JSON-RPC 2.0 tools/call (stdio|HTTP)
    S-->>B: result | error | isError
    B->>B: Validate schema · sanitize · taint-tag
    B-->>M: Observation
    opt multi-turn unbounded domain (G4+)
      M->>A: A2A message (not raw MCP)
      A-->>M: negotiated result
    end
    M->>D: Slice complete
    D->>D: Drop unused schemas
    M-->>U: Verdict / next ask
  end
```

### Notes
- A2A path remains **schema-only** until `G4_TOPOLOGY_APPROVED_v1`.
- Payment / A2UI extensions stay disabled under OPTION_2.
- LRO (>10s): broker emits warning and requests HITL continue or async task (see `timeout_budgets.yaml`).
