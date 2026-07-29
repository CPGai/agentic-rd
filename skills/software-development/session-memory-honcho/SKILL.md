---
name: session-memory-honcho
description: >
  Operate session lifecycle and Honcho memory under G3: namespaces
  user:/session:/app:, compaction bookmarks, hybrid recall, redaction.
  Use when persisting facts, recalling peer context, or compacting
  long sessions. Do NOT use to auto-rewrite skills (G7 domain only).
priority: 85
---

# Session Memory + Honcho (workspace seed)

## Namespaces
| NS | Lifetime |
|---|---|
| `user:` | cross-session standing facts |
| `session:` | single conversation scratchpad |
| `app:` | workspace/product config |

## Honcho posture
- Provider: `honcho` via loopback API
- Prefer: profile → context → search → reasoning (on demand)
- `conclude` only for durable facts or PII delete
- Redact secrets before persist
- `AUTH_USE_AUTH=false` is MED residual — G8 hardens; keep loopback-only

## Compaction
- View filter: last-N / token backfill
- Summary every ~20 short / ~60 long (align Honcho)
- Bookmark `covered_through_event_id` to avoid double-send

## Specs
`SESSION_STATE_SPEC.md` · `HONCHO_INTEGRATION_MATRIX.yaml` · `MEMORY_LOAD_POLICY.yaml`
