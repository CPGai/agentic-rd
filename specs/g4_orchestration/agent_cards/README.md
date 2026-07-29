# agent_cards/README.md

**Domain:** G4 · Mock A2A Agent Card registry  
**Lifecycle default:** `schema_only`  
**Live remote invoke:** **denied** unless card.`option_2.enabled` and policy allow.

## Inventory

| File | Card id | Role | risk_tier | option_2 |
|---|---|---|---|---|
| `root_orchestrator.card.json` | `card.root.orchestrator` | Hierarchical root | T2 | yes |
| `spec_gherkin_specialist.card.json` | `card.leaf.spec_gherkin` | Gherkin decomposition leaf | T1 | yes leaf |
| `strong_coding_specialist.card.json` | `card.leaf.strong_coder` | Declarative/spec implementation leaf | T2 | yes leaf |
| `research_knowledge_specialist.card.json` | `card.leaf.research` | Knowledge / MCP retrieve leaf | T2 | yes leaf |
| `security_policy_specialist.card.json` | `card.leaf.security_review` | Security/mandate critic | T2 | yes leaf |
| `critic_review_specialist.card.json` | `card.leaf.critic_review` | Iterative refinement critic | T1 | yes leaf |
| `quality_eval_specialist.card.json` | `card.leaf.quality_eval` | Structural verify + trajectory pack | T1 | yes leaf |
| `remote_billing_example.card.json` | `card.remote.billing_specialist_example` | Example remote AaaS | T4 | **no** |

## Schema checklist (structural)

Every card MUST include: `id`, `name`, `version`, `description`, `url`, `capabilities`, `skills`, `security`, `risk_tier`, `policy`, `lifecycle`, `interaction`, `option_2`.

Payment extensions optional: `ap2`, `x402`, `a2ui`.

## Risk tiers (G4 local)

| Tier | Meaning | OPTION_2 default |
|---|---|---|
| T0 | Pure read / format | auto |
| T1 | Workspace declarative / review | auto with trace |
| T2 | Shell/MCP brokered write or retrieve | policy intercept |
| T3 | Custom remote / elevated | HITL + allowlist |
| T4 | Payment, IAM, prod, untrusted remote | deny or hard HITL |

Alignment note: G2 procurement T1–T4 is **tooling**; G4 tiers annotate **agents**. Do not conflate IDs in telemetry.

## Registry rules

1. Private registry is the only OPTION_2 source of truth.  
2. Public marketplace cards may exist as mocks (`option_2.enabled: false`).  
3. Changing `risk_tier` upward mid-task requires policy re-check.  
4. `supportsAgentToolShim: true` only when interaction is schema-closed enough to avoid A2A GOTO leakage (WP-S2).
