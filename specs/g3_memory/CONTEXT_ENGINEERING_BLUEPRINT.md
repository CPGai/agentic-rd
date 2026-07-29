# CONTEXT_ENGINEERING_BLUEPRINT.md

**Domain:** G3 — Memory & Stateful Agents (Sessions, Skills & Progressive Disclosure)  
**Status:** LOCKED  
**Authoritative resume token (BLUE):** `G3_CONTEXT_LAYER_LOCKED_v1`  
**Precedence:** Course-2 (WP-S3) supersedes Course-1 (WP-F3) on overlap  
**Upstream:** G1 `HARNESS_SPEC.md` §2 · G2 `skills_registry.json` / `TOOL_DISCLOSURE_POLICY.md` · `G3_MIGRATION_CONTEXT.md`  
**Sources ingested (PyMuPDF / fitz):**

| Paper | Path | Pages | Method |
|---|---|---|---|
| WP-F3 | `specs/references/WP-F3-Context Engineering_ Sessions & Memory.pdf` | 72 | TOC clusters + keyword index → `/tmp/g3_extract/F3_*` |
| WP-S3 | `specs/references/WP-S3 - Agent Skills_Day_3.pdf` | 62 | TOC clusters + keyword index → `/tmp/g3_extract/S3_*` |
| BLUE §G3 | `specs/references/AGENTIC R&D & IMPLEMENTATION BLUE.md` L182–260 | — | Exact `RESUME_TOKEN` |

**Constraint:** Declarative artifacts only. No application runtime logic in this pack.

---

## 1. Problem statement (cross-paper)

LLMs are **stateless per API call**. Stateful agents require **Context Engineering**: dynamic assembly of the full payload (not just a static system prompt) so the model receives *no more and no less* than the information needed for the current turn (WP-F3).

Production failures are dominated by **context overflow / context rot**, not raw hallucination: accuracy degrades as input grows (“Lost in the Middle”, Chroma Context Rot) long before hard window limits (WP-S3). The architectural countermeasure is **progressive disclosure** for procedural knowledge (skills) plus **session compaction** and **extracted long-term memory** (WP-F3 + WP-S3).

**Token economics (WP-S3, normative math for this blueprint):**

| Shape | Per-turn payload (illustrative) | Capability surface |
|---|---|---|
| Monolithic prompt (50 workflows) | ~15 000 tokens every turn | All workflows always hot |
| Skills library (50 skills) | ~4 000 L1 descriptions + ~2 000 active L2 body ≈ **~6 000** effective | 50 units available; 1 body hot |
| Documented extreme | 150 000 → ~2 000 (≈98% reduction) when workflow converted to skills | Bounded tax on matching turns only |

BLUE’s contrast of **monolithic 15 k vs ~50 skills (~3 k effective)** is the same economic family; this workspace binds **HARNESS_SPEC §2.2 static envelope** + skill co-load caps below.

---

## 2. Six context types — placement, cost, cadence

Binding catalog aligns WP-F3 payload components with WP-S1 / `HARNESS_SPEC.md` §2.1 six types.

| # | Type | Static vs dynamic | Update frequency | Token posture | Primary owners |
|---|---|---|---|---|---|
| 1 | **Instructions** | **Static** small distilled constitution | Per constitution revision | Always-on ≤ 2–4 k tok target | `AGENTS.md`, module tighteners |
| 2 | **Knowledge** | **Dynamic** RAG / path-scoped reads | Per query | Pay-per-retrieve; cite chunks | `specs/**`, docs, Context7 MCP (G2 T2) |
| 3 | **Memory** | Hybrid: **pinned profile static-small** + **window dynamic** | Continuous / async consolidate | Never full history dump | Session store + Honcho (this domain) |
| 4 | **Examples** | **Dynamic** task-matched | On skill/eval match | 1–3 tight shots | skill bodies, golden sets (G5) |
| 5 | **Tools** | **Dynamic** progressive (“RAG-for-tools”) | On intent match | Schemas only for eligible tools | G2 `TOOL_REGISTRY` + broker seat |
| 6 | **Guardrails** | Static core + dynamic specialized | Per policy change / skill L2 | Core ≤ 1–2 k tok | Constraint catalog, skill overlays |

**WP-F3 assembly cycle (normative loop):** Fetch → Prepare → Invoke → Capture events/state → Compact/extract memory → next turn.

**Workspace assembly order (HARNESS_SPEC §2.3 — binding):**

```
STATIC pack (Instructions ∩ core Guardrails ∩ pinned Memory)
  → Skills L1 scan → L2/L3 on trigger
  → Tools intent-match (RAG-for-tools)
  → Knowledge retrieve + cite
  → Memory window / observations attach
  → Model → Action/Observation
  → Compact on token | turn | semantic threshold
```

Hard rule retained: **if static payload > 20% of active context window**, force skill-backed progressive disclosure before more always-on text.

---

## 3. Skill anatomy (agentskills.io) — L1 / L2 / L3

WP-S3 progressive disclosure (Course-2 wins):

| Level | Contents | Load rule | Token intent |
|---|---|---|---|
| **L1 Metadata** | YAML frontmatter `name` + `description` (what + when + when-not) | **Always** in agent routing context | ≈ **50 tokens** target per skill (BLUE); description ≤ ~200 chars API / ≤ 1024 YAML; aim ~50 words |
| **L2 Body** | `SKILL.md` markdown instructions | **Only on trigger** (description match / explicit invoke) | Prefer ≤ ~2–5 k tok body; co-load aware (5–15 skills simultaneous in prod studies) |
| **L3 Resources** | `references/`, `scripts/`, `assets/` (templates optional) | **Strictly as needed**; scripts execute **outside** token window when possible | Zero idle tax |

**Canonical directory (agentskills.io):**

```
skill-name/
├── SKILL.md          # required: frontmatter + instructions
├── scripts/          # optional: deterministic helpers
├── references/       # optional: progressive prose
├── assets/           # optional: templates, schemas, binaries for output
└── templates/        # optional (Hermes layout variant of assets)
```

**Five rules (WP-S3, binding for G3 skill governance):**

1. One skill, one job.  
2. Descriptions are the routing interface.  
3. Skills are dependencies (version, pin, PR review, tests).  
4. Right team owns the right skill.  
5. Runtime-portable — do not hard-lock to one agent binary.

**Skill vs MCP vs AGENTS.md (routing fit):**

| Primitive | Role | Context tax |
|---|---|---|
| `AGENTS.md` / constitution | Always-on **passive** project law | Static every turn |
| **Skill** | Conditional **procedural** workflow unit | L1 always; L2/L3 on demand |
| **MCP / tools** | External action + schema surface | Disclosure after skill/intent match (G2) |

**Eval gates before production skill authority (WP-S3):** trigger ≥90% (pos+neg) · execution quality · library regression · **co-load token budget with 5–15 peers**. Isolation-only eval is a false green.

**Authority tiers (until G5/G7 open more):**

| Tier | Allowed effects | Min bar |
|---|---|---|
| Read-Only | Advise, draft analysis | LLM-judge + 90% trigger |
| Draft-Only | Propose edits needing human review | ≥20 golden cases + HITL |
| Action-Allowed | Side effects in tool gateway | Adversarial + sustained pass^k; OPTION_2 tools T1+T2 only |

**Cold fact (Step B audit):** workspace `skills/` is empty placeholder; **93** profile skills under Hermes `wsl-runtime` skills tree; 0 missing frontmatter; 52 with ≥1 L3 folder; 1 L1 budget hedge violator (`adversarial-ux-test` ≈81 tok est). G2 indexed **4** T1 skills in `skills_registry.json` as project handoff seed only.

---

## 4. Session management

### 4.1 Definitions (WP-F3)

| Term | Definition |
|---|---|
| **Session** | Short-term event container for one continuous conversation, owned by a single user/ACL principal |
| **Events** | Ordered log: user input, agent response, tool call, tool output (framework-native shapes OK inside session store) |
| **State / scratchpad** | Structured working memory mutated during the session (cart, open files, mission flags) — **not** long-term memory |
| **Memory** | Extracted, framework-agnostic snapshots (strings/dicts + metadata) persisted **across** sessions |

### 4.2 Namespaces (BLUE ToolContext conventions)

| Namespace | Scope | Examples | Persistence |
|---|---|---|---|
| `user:` | Principal-longitudinal | preferences, identity pins | Long-term memory / peer card |
| `session:` | Single conversation | scratchpad, open-task map, compaction bookmarks | Session store TTL |
| `app:` | Workspace/product | feature flags, project routing, harness mode | Config + optional memory docs |

### 4.3 Production session controls (WP-F3)

- **Strict isolation / ACL** on every session read-write.  
- **Redact PII before persist** (blast-radius reduction).  
- **TTL / retention** — sessions must not live forever.  
- **Deterministic append order** for event integrity.  
- **Hot path**: filter/compact **before** ship to model; expensive summarization **async + persisted** with event-coverage bookmarks so raw events are not double-sent.

---

## 5. Memory architecture

### 5.1 Types (descriptive, not predictive — WP-F3)

| Kind | Role | Typical store |
|---|---|---|
| Short-term / working | Session events + state | Session DB / runtime window |
| Episodic extracts | “What happened” facts from dialogue | Memory manager rows |
| Semantic / profile | Stable preferences, standing conclusions | Peer card + vector/index |
| Procedural | How the agent succeeded (playbook) — **careful under OPTION_2** (no L4 self-mutate) | Versioned skills, not silent rewrite |

### 5.2 Manager lifecycle

`Extract → Consolidate → Store → Retrieve` as an **active** service (not passive vector DB only). RAG ≠ Memory: RAG = static external expertise; Memory = dynamic user/agent-specific context.

### 5.3 Generation & retrieval policies

| Dimension | OPTION_2_STANDARD default |
|---|---|
| Generation trigger | Hybrid: threshold (turn/token) + explicit user pin + selective memory-as-tool |
| Consolidation | Async deriver; dedupe entities; preserve provenance/lineage fields |
| Retrieval timing | Prefetch **pinned card + hybrid recall** at turn start; deep dialectic **on tool call** |
| Injection locus | Prefer dedicated memory block **after** skills/tools/knowledge; avoid burying in middle of huge tool dumps |
| Preload vs reactive | **Pinned profile preload (small)**; task memory **reactive/hybrid**; forbid full corpus preload |

### 5.4 Local Honcho mapping (live substrate)

| Component | Live observation (Step B) | G3 role |
|---|---|---|
| API | Docker `honcho-api-1` healthy; loopback bind `127.0.0.1:8000`; `GET /health` → `{"status":"ok"}`; OpenAPI title **Honcho API** | Session/peer/memory HTTP surface |
| Deriver | `honcho-deriver-1` up; env routed OpenRouter; memory note: **deepseek/deepseek-v4-flash** (isolated key) | Extract/consolidate/dream async |
| Database | `honcho-database-1` **pgvector/pgvector:pg15** on loopback `:5432` | Durable rows + vectors |
| Cache | `honcho-redis-1` loopback `:6379` | Hot cache |
| Vector | `VECTOR_STORE_TYPE=pgvector`, embed path OpenAI-compatible, dims **1536** (example/template) | Hybrid search substrate |
| Auth | `AUTH_USE_AUTH=false` | **MED residual risk** — G3 policy declare + G8 harden |
| Hermes bind | Profile `memory.provider: honcho`; `honcho.json` `baseUrl: http://localhost:8000`; hybrid recall; per-directory session strategy (durable memory) | Client integration |

Detail matrix: `HONCHO_INTEGRATION_MATRIX.yaml`. Lifecycle/API: `SESSION_STATE_SPEC.md`.

---

## 6. Compaction & token-decay model

### 6.1 Failure drivers (why compact)

1. Hard context-window overflow.  
2. API $ token growth.  
3. Latency growth.  
4. **Quality decay / context rot** (noise + middle-bury).

### 6.2 Strategy ladder (WP-F3)

| Strategy | Behavior | Tradeoff |
|---|---|---|
| Last-N turns | Sliding window keep recent events | Simple; loses deep refs |
| Token-budget truncation | Walk backward until budget (e.g. 4 k history band) | Predictable cap; abrupt cuts |
| Recursive summarization | Older spans → summary prefix + recent verbatim | Best retention; needs async + bookmarks |
| Tool-output eviction | Drop stale tool payloads already folded into state | High ROI on agent traces |
| Memory offload | Extract durable facts → memory manager; shrink session | Cross-session continuity |

### 6.3 Triggers

| Class | Examples |
|---|---|
| Count-based | Token sum, turn count, tool-output bytes |
| Time-based | Idle session compaction / TTL |
| Semantic | Topic shift, mission boundary, explicit user “new topic” |

### 6.4 Workspace debit waterfall (normative targets)

Percent of **active model context window** (inherits HARNESS_SPEC §2.2):

| Bucket | Share | Notes |
|---|---|---|
| Instructions | 5–10% | Distilled AGENTS — not full blueprints |
| Guardrails core | 3–5% | Inviolable only |
| Pinned memory / peer card | 2–5% | Standing facts only |
| Mission + scene | 15–25% | Goal, acceptance, open map |
| Dynamic (L2 skills, tools, knowledge, examples, observations) | 40–60% | Includes ≤ co-load L2 bodies |
| Reserve / completion | 10–15% | Structured verdict headroom |

**Skill L1 catalog budget:** sum of always-on skill metadata should stay inside routing slice; if catalog grows, apply **capability profiles** (WP-S3) to subset active L1 sets — full 93-skill dump is not required every turn.

**Co-load soft cap (OPTION_2):** prefer ≤ **3** L2 bodies concurrent on coding turns; hard audit flag if simultaneous L2 bodies > **8 k** tok estimated.

---

## 7. Skill co-load evaluation & precedence

### 7.1 Interaction effects

Source: WP-S3 “token budget isolation is a trap” — 5–15 skills co-load; bodies >5 k tok fail under noise; tool proliferation cut accuracy ~18% in cited MCPVerse note.

### 7.2 Precedence resolution (proposed OPTION_2 — **HITL decides**)

| Rank | Source | Wins when |
|---|---|---|
| 0 | Constraint catalog / safety hooks | Always |
| 1 | Root `AGENTS.md` + sandbox isolation | Always |
| 2 | Explicit user instruction this turn | Unless violates 0–1 |
| 3 | Module tightener (`GEMINI.md`/`CLAUDE.md`) | Narrower scope |
| 4 | Skill L2 with higher `priority` / closer trigger match | Tied → more specific `when` |
| 5 | Skill L3 referenced by winning L2 | Demoted if budget tight |
| 6 | Memory suggestions | Advisory; never override constraints |
| 7 | Default model priors | Lowest |

**Conflicts:** if two L2 skills issue incompatible hard rules → **escalate_HITL**, do not silent merge.  
**Mutations:** auto skill rewrite / A-MEM graph skill evolution = **OPTION_3 only** post G7 gates.

Deferred full artifact: `SKILL_COLOAD_AUDIT` (BLUE when Step E) — partial inventory captured in Step B.

---

## 8. Traceability matrix

| Blueprint claim | WP-F3 | WP-S3 | Workspace |
|---|---|---|---|
| Context Engineering > static prompt | Context Engineering ch. | Runtime 98% infrastructure insight | HARNESS §2 |
| Session = events + state | Sessions | Session storage in runtime | SESSION_STATE_SPEC |
| Memory manager lifecycle | Memory chapters | — | HONCHO matrix |
| Compaction strategies + async | Long-context mgmt | Context overflow failure mode | SESSION_STATE_SPEC |
| L1/L2/L3 progressive disclosure | (extended) | Skill Anatomy | agentskills.io + skills audit |
| Token economics monlith vs skills | Compaction $ / latency | 15k vs ~6k / 150k→2k | §6 waterfall |
| Co-load evaluation | — | Eval toolkit | §7 + deferred audit |
| Privacy redaction & isolation | Production sessions/memory | Security scan checklist | HONCHO matrix + G8 |

### Course-2 supersession

| Topic | Course-1 (F3) | Course-2 (S3) winner |
|---|---|---|
| Unit of procedural knowledge | Mostly prompt/plugins | **Skills** progressive disclosure |
| Primary production failure frame | Compact history | **Context overflow/rot** + skill packaging |
| Improvement loop | Memory procedural notes / manager | **Edit SKILL.md** as owned unit; meta-skills gated |
| Tooling relationship | Tools as context components | Skills orchestrate; MCP adjacent; G2 closes registry |

---

## 9. Deferred / post-gate (not claimed done)

| Item | BLUE step | Notes |
|---|---|---|
| Workspace `skills/` 3–5 seed trees | D | Profile already hosts 93; workspace mirror deferred |
| `token_budget.yaml` standalone | D | Numbers live in SESSION_STATE_SPEC § budgets for gate |
| Mermaid life-cycle diagram file | D | Embedded in SESSION_STATE_SPEC |
| Co-load conflict simulation harness | E | Structural tests post-token |
| `context-v1.0.0` tag | F | After human grant + C/E/F |
| Auth hardening Honcho | G8 shared | `AUTH_USE_AUTH=false` residual |
| hermes-api-bridge non-loopback `:8642` | G8 | Inherited HIGH from G2 migration note |

---

## 10. Definition of done (this blueprint)

1. Whitepapers ingested via PyMuPDF with cluster extracts under `/tmp/g3_extract/`.  
2. Six types, skill anatomy, session/memory/token/co-load sections complete.  
3. Maps cleanly to `SESSION_STATE_SPEC.md` + `HONCHO_INTEGRATION_MATRIX.yaml`.  
4. `G3_CONTEXT_LAYER_LOCKED_v1` locked — pack managed via `scripts/verify_g3_memory.py` + tag `context-v1.0.0`.

*End of CONTEXT_ENGINEERING_BLUEPRINT.md*
