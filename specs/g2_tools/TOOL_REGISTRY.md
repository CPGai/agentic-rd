# TOOL_REGISTRY.md
## Domain G2 — Tool Use & MCP (Declarative Catalog)

**Version:** 1.0.0  
**Domain:** G2 — Tool Use & MCP  
**Status:** LOCKED — `OPTION_2_STANDARD` · `RESUME_TOKEN: G2_TOOL_REGISTRY_LOCKED_v1` (alias `G2_TOOLING_APPROVED_v1`)  
**Anchors:**  
- WP-F2 *Agent Tools & Interoperability with Model Context Protocol (MCP)* (Nov 2025)  
- WP-S2 *Agent Tools & Interoperability* (May 2026) — **Course-2 supersedes Course-1 on overlap**  
- BLUE §G2 · inherits `HARNESS_SPEC.md` / `AGENTS.md` (`G1_HARNESS_APPROVED_v1` / `OPTION_2_STANDARD`)  
**Scope:** Declarative registry + broker/disclosure/timeout schemas. Broker runtime remains `DECLARED_NOT_WIRED`. No live payment/A2UI.  
**Companions:**  
[`MCP_COMPAT_MATRIX.yaml`](./MCP_COMPAT_MATRIX.yaml) · [`PROCUREMENT_TIER_MATRIX.yaml`](./PROCUREMENT_TIER_MATRIX.yaml) · [`broker_config.yaml`](./broker_config.yaml) · [`timeout_budgets.yaml`](./timeout_budgets.yaml) · [`TOOL_DISCLOSURE_POLICY.md`](./TOOL_DISCLOSURE_POLICY.md) · [`skills_registry.json`](./skills_registry.json) · [`pins/npm-mcp-pins.json`](./pins/npm-mcp-pins.json)

---

## 0. Purpose & Non-Goals

### 0.1 Purpose
Produce the enterprise **tooling constitution** for this workspace so that:

1. Every callable surface (native, MCP, A2A, commerce extension) is catalogued with risk class and disclosure rules.  
2. Tools enter context only via **progressive disclosure (“RAG-for-tools”)** (WP-S2 p15; HARNESS_SPEC §2.1 type Tools).  
3. Confused-deputy, tool-shadowing, slopsquatting, and payment surfaces are **broker-gated** before any live bind (WP-F2 pp.39–51; BLUE G2).  
4. Procurement prefers **consume over build** along a strict hierarchy (WP-S2 pp.11–16).

### 0.2 Non-Goals
- No application runtime / broker implementation code from this domain meta-prompt set.  
- No Tier-4 ad-hoc wrappers promoted without `/grill-me` + HITL.  
- No live AP2 spending, UCP checkout, or A2UI generative UI in production paths under `OPTION_2_STANDARD`.  
- No host-Windows Python/package execution for project work (`C-ARCH-01`).

---

## 1. Crosswalk Synthesis (Course-1 → Course-2)

| Concern | WP-F2 (Course-1) | WP-S2 (Course-2, wins) | Workspace binding |
|---|---|---|---|
| Standardization metaphor | MCP as universal interface (“USB-C”/LSP-like) solving N×M | MCP as plug-and-play socket for vibe consumption + enterprise govern | MCP is default tool wire; native tools remain first-party factory controls |
| Architecture | Host · Client · Server (F2 pp.21–22) | Same; emphasize Discovery → Configuration → Connection (S2 pp.10–12) | Hermes Host embeds MCP Client(s); broker is permanent Constraint component |
| Wire format | JSON-RPC 2.0 Request/Result/Error/Notification (F2 p.23) | JSON-RPC over transports remains | All MCP rows in compat matrix declare JSON-RPC 2.0 |
| Transports | **stdio** local · **Streamable HTTP** remote (SSE optional) (F2 p.23) | stdio for local/proto · **SSE over HTTP** for remote (S2 p.14) | Prefer stdio for trust-local; Streamable HTTP/SSE only for allowlisted remote |
| Primitives | Server: Tools/Resources/Prompts; Client: Sampling/Elicitation/Roots (F2 pp.24–25). Tools ~99% client support | Skills treated as higher layer (next paper); A2A/A2UI/UCP/AP2 expand stack | Tools first-class; Resources/Prompts optional; A2A deferred hard until G4; A2UI/UCP/AP2 Tier-3/4 gated |
| Tool schema | `name, title?, description, inputSchema, outputSchema?, annotations?` (F2 pp.26–28) | Consume schema via handshake `tools/list` (S2 p.12) | Canonical tool record = MCP tool object + workspace risk/disclosure fields |
| Discovery loop | Dynamic `tools/list`; servers may change without notify (risk) (F2 pp.40–41) | Public / 3P remote / internal registries (S2 p.11) | Client must re-list + pin/hash; allowlist filter at broker |
| Security centre of mass | Tool shadowing, malicious defs, leaks, coarse auth, confused deputy (F2 pp.39–51) | Audit public code; no prod on unverified MCP; HITL before call; no hardcoded secrets (S2 pp.15–16) | Permanent **MCP Broker** + Constraint pre-hooks `C-ARCH-04`, `C-SEC-*` |
| Interop beyond tools | MCP only | **Stack:** MCP → Skills → **A2A** → **A2UI** → **UCP/AP2** (+ x402/L402 micro-pay) | Registry sections 4–7 encode full stack; OPTION_2 disables live commerce/UI gen |
| Progressive disclosure | Implied via granular tools (F2 best practices) | Explicit **RAG-for-tools** (S2 p.15) | Mandatory: intent-match → load schema → drop on task complete |

### 1.1 Dynamic tool discovery loop (normative)

```
CONFIGURE (identity, env secrets, scope, transport)
  → CONNECT transport (stdio | streamable-http/SSE)
  → initialize (JSON-RPC handshake, capability negotiate)
  → tools/list  (+ resources/list, prompts/list if advertised)
  → BROKER FILTER (allowlist · collision check · pin/hash · risk class)
  → DISCLOSE subset to model (RAG-for-tools / intent match)
  → PRE-HOOK Constraint (sanitize · HITL if high-risk)
  → tools/call  { name, arguments }
  → VALIDATE result vs outputSchema; sanitize; taint-tag
  → OBSERVE / EVALUATE trajectory
  → DROP schemas when mission slice completes
  → on listChanged / hash-mismatch → revalidate or disconnect
```

**Anchors:** WP-F2 pp.21–30, 40–41; WP-S2 pp.10–16; HARNESS_SPEC §2.3 assembly pipeline.

### 1.2 JSON-RPC 2.0 envelope (MCP base)

```json
// Request
{"jsonrpc":"2.0","id":1,"method":"<method>","params":{}}

// Success result
{"jsonrpc":"2.0","id":1,"result":{}}

// Protocol error (unknown tool, invalid args, server fault)
{"jsonrpc":"2.0","id":1,"error":{"code":-32602,"message":"..."}}

// Notification (no id, no response)
{"jsonrpc":"2.0","method":"notifications/<name>","params":{}}
```

**Tool execution error** stays inside `result` with `"isError": true` and instructional `content[]` (WP-F2 p.29–30).  
Clients MUST distinguish protocol-layer errors from tool-layer `isError` (fail-fast Evaluation).

### 1.3 Canonical MCP Tool object (workspace)

```json
{
  "name": "get_stock_price",
  "title": "Stock Price Retrieval Tool",
  "description": "Get stock price for a specific ticker symbol...",
  "inputSchema": {
    "type": "object",
    "properties": {
      "symbol": {"type": "string", "description": "Stock ticker symbol"},
      "date": {"type": "string", "description": "Date (YYYY-MM-DD)"}
    },
    "required": ["symbol"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "price": {"type": "number", "description": "Stock price"},
      "date": {"type": "string", "description": "Stock price date"}
    },
    "required": ["price", "date"]
  },
  "annotations": {
    "readOnlyHint": true,
    "destructiveHint": false,
    "idempotentHint": true,
    "openWorldHint": true
  }
}
```

**Normative workspace rules (beyond bare MCP):**
1. Treat `title`, `description`, `inputSchema`, `outputSchema` as **required for registration** even if MCP marks some optional (WP-F2 p.26).  
2. **Never trust `annotations` from untrusted servers** as security truth — hooks may override (WP-F2 p.27).  
3. Pin `{name, description_hash, inputSchema_hash, server_id, version}` after vetting; drift → alert/disconnect (WP-F2 p.41).

---

## 2. Procurement Hierarchy (4-Tier)

Prefer higher tiers. Resist custom REST wrappers (WP-S2 p.16 “Don't build if you can consume”).

| Tier | Source class | Examples (this workspace) | Risk class default | Production under OPTION_2? | Defense baseline |
|---|---|---|---|---|---|
| **T1** | First-party **Skills Hub** / pin-curated skills + native Hermes toolsets | In-profile `skills/**`, agentskills.io hub (`.hub`), native terminal/file/web toolsets | LOW–MED | **Yes** (current substrate) | Skill linter `C-FS-02`; progressive L1→L2→L3; no undeclared deps `C-LIB-*` |
| **T2** | **Vetted MCP servers** (official vendor / internal registry / audited stdio) | `context7` (`@upstash/context7-mcp`); future official Google/GitHub maps etc. via allowlist | MED | **Yes** if matrix row `prod_eligible: true` + broker ACL | Allowlist, schema pin, rate limit, output sanitize, no secrets in prompts |
| **T3** | **Custom MCP** authored here or internal private registry wrappers | Future project MCP adapters under controlled deploy | MED–HIGH | Conditionally after Step E audit | Controlled deploy, mTLS/gateway preferred, explicit HITL on destructive |
| **T4** | Ad-hoc scripts, unverified public MCP, one-off REST, shadow CLIs | Random `npx` MCP from public registries without audit | HIGH / CRITICAL | **No** — prototype dune only | Quarantine; `/grill-me` for gaps; never prod credentials |

### 2.1 Procurement decision tree

```
Need capability?
  → Exists as T1 skill / native toolset? USE IT
  → Exists as T2 allowlisted MCP in MCP_COMPAT_MATRIX? CONNECT via broker
  → Exists reputable public/official server worth promoting to T2?
        → Audit source → pin version → add matrix row (draft) → HITL if new attack surface
  → Must wrap internal API? Prefer T3 Custom MCP behind gateway (not raw REST in agent)
  → Else T4 prototype on dune branch only; never default profile prod path
```

### 2.2 Registry source preference (WP-S2 p.11)

1. **Internal / private registries** (API gateway, enterprise agent registry).  
2. **Official 3P remote MCP** (vendor-published, managed auth).  
3. **Public MCP registries** (`registry.modelcontextprotocol.io`, community GitHub) — **prototyping only**; audit source; never pass long-lived credentials (S2 p.11 tip).  
4. Custom build **last**.

---

## 3. Native Tool Catalog (Host factory surfaces)

These are **non-MCP** tools available to the agent runtime. They are still subject to Constraint hooks, WSL2 routing, and progressive disclosure of *schemas/prose*.

### 3.1 Hermes built-in tool surfaces (session-observed)

| Tool / family | Role | Side-effect class | Risk | Notes |
|---|---|---|---|---|
| `terminal` / process control | Shell on substrate | HIGH (exec) | HIGH | **Must** route via WSL2 + `.venv-hermes` (`C-ARCH-01`) |
| `read_file` / `write_file` / `patch` / `search_files` | Workspace FS | MED–HIGH (write) | MED | Profile write guard `C-SEC-03` |
| `execute_code` | In-process Python orchestrating tools | MED | MED | Same venv; no host Python |
| `delegate_task` | Subagent fan-out | HIGH (multi-agent) | HIGH | Full topology = G4; leaf mode only until G4 token |
| `skill_view` / `skill_manage` / `skills_list` | Progressive skills | MED | MED | agentskills.io layout |
| `memory` (+ Honcho dialectic tools) | Durable / long-term memory | MED (PII) | MED | Provider `honcho`; no secrets in memory |
| `cronjob` | Scheduled autonomous jobs | HIGH | HIGH | Self-contained prompts; no recursive cron-spawn |
| `web_search` / browser browse family | Open-world web | openWorld | MED–HIGH | Treat as untrusted content; sanitize |
| `mcp__context7__*` | MCP-bridged Context7 | LOW–MED | LOW–MED | See §4 server `context7` |
| `clarify` / `todo` / `session_search` | HITL & session UX | LOW | LOW | UX only |
| `send_message` / messaging gateway | Discord et al. | HIGH (egress) | HIGH | Tokens only via env; home channel bare ID |
| `vision_analyze` / `text_to_speech` / `open_preview` | Multi-modal UX | LOW–MED | LOW | Auxiliary models |
| Desktop panes / project tools | GUI affordances | LOW | LOW | No security boundary |

### 3.2 Local CLI inventory (WSL2 audit 2026-07-23)

**Present in WSL PATH (substrate):**  
`bash`, `git`, `curl`, `wget`, `python3` (venv), `pip`, `node`, `npm`, `npx`, `docker`, `docker-compose`, `kubectl`, `openssl`, `ssh`, `gcc`, `make`, `nc`, `ss`, `lsof`, `systemctl`, `claude` (host bridge).

**Present but host-profile / Windows-side (not default WSL PATH):**  
Hermes CLI under `AppData/Local/hermes/…`, `uv.exe` in profile `bin/`, npm globals (`claude`, `gemini`). Use via profile/Desktop host — **do not** install project deps on host Python.

**Absent in WSL PATH at audit (do not assume):**  
`jq`, `rg`, `fd`, `gh`, `sqlite3`, `hermes` (linux binary), `agy`, `codex`, `opencode`, `pytest`/`ruff`/`mypy` as global bins (may exist inside venv — invoke via `python -m` after check).

### 3.3 Docker / sidecar services (local)

| Container | Image / role | Ports | Registry status |
|---|---|---|---|
| `honcho-api-1` | honcho-api memory | `127.0.0.1:8000` | T1/T2 adjacent (memory provider, not MCP) |
| `honcho-deriver-1` | deriver worker | internal 8000 | same |
| `honcho-redis-1` | redis 8.2 | `127.0.0.1:6379` | infra |
| `honcho-database-1` | pgvector/pg15 | `127.0.0.1:5432` | infra |
| `hermes-api-bridge` | alpine/socat | `127.0.0.1:8642` | host bridge — strict loopback bound |

**Flag:** `hermes-api-bridge` publishes `127.0.0.1:8642` (strict loopback). Non-loopback external binds (`0.0.0.0`) are strictly prohibited across all substrate services.

---

## 4. MCP Server Catalog

> **Supply-Chain Policy (OPTION_2_STANDARD):** Floating `npx` execution (e.g. unpinned `npx @upstash/context7-mcp` or using floating `@latest` tags) is **explicitly forbidden** across all environments under `OPTION_2_STANDARD`. All MCP server packages must be pinned to explicit, immutable version tags (e.g. `@upstash/context7-mcp@1.0.6`) and enforced via lockfile/integrity policy (`integrity_policy: "lockfile_enforced"`).

### 4.1 Active / configured (wsl-runtime profile)

#### `context7` — library docs RAG MCP

| Field | Value |
|---|---|
| **server_id** | `context7` |
| **tier** | T2 |
| **package** | `@upstash/context7-mcp@1.0.6` (via `npx -y`, pinned) |
| **transport** | **stdio** (command spawn) |
| **config_locus** | `…/profiles/wsl-runtime/config.yaml` → `mcp_servers.context7` |
| **enabled** | `true` |
| **auth** | None configured (public rate-limited tier) |
| **auth_class** | `none_public` |
| **confused_deputy_risk** | MED — unauthenticated but read-oriented docs; still injects untrusted doc text into context |
| **tools (session-exposed bridge names)** | `mcp__context7__resolve_library_id`, `mcp__context7__query_docs`, `mcp__context7__list_prompts`, `mcp__context7__get_prompt`, `mcp__context7__list_resources`, `mcp__context7__read_resource` |
| **primary ops** | Resolve library ID → query docs (max 3 query_docs/question per tool doc) |
| **side_effect** | read-mostly / remote egress to Context7 network |
| **rate_limits** | Provider public tier (no API key) — treat as soft-unknown; back off on errors |
| **prod_eligible_OPTION_2** | **Yes** with output sanitization + no secret-bearing queries |
| **pin_policy** | **LOCKED** — `specs/g2_tools/pins/npm-mcp-pins.json` + broker_config ACL pin `1.0.6` |
| **listChanged_policy** | On reconnect re-run tools/list; refuse new tool names until allowlist amend |
| **annotations_trust** | untrusted_defaults |
| **HITL** | Not required for resolve/query; required if future write-capable tools appear |
| **anchors** | Runtime config audit; WP-S2 consumption path p.10–16; WP-F2 tool object pp.26–30 |

### 4.2 Planned / stub rows (not connected)

| server_id | tier | intent | transport (planned) | status |
|---|---|---|---|---|
| `filesystem_scoped` | T3 | Read-only project FS via MCP (if ever needed beyond native tools) | stdio | **NOT REQUIRED** — native file tools suffice; avoid duplicate attack surface |
| `github_official` | T2 | Issues/PR via official MCP if adopted | streamable-http or stdio+gh auth | stub — prefer `gh` CLI behind Constraint until bound |
| `public_unverified_*` | T4 | Any community server | any | **blocked in prod profiles** |

### 4.3 Unauthenticated MCP inventory (REQUIRED_TELEMETRY)

| server_id | auth | note |
|---|---|---|
| `context7` | **none** | Only active MCP; document-only; still sanitize outputs |

Count of unauthenticated active MCP servers: **1**.

---

## 5. A2A Agent Card Schema (canonical template)

**Role:** Machine-readable “CV” for discoverable specialist agents (WP-S2 pp.25–28).  
**Stack position:** Above MCP tools; multi-turn unbounded domains. Keep MCP layer strictly structured — dirty multi-turn negotiation remains at A2A (S2 p.24 GOTO problem).  
**Gate:** Live A2A orchestration requires **G4** resume (`G4_TOPOLOGY_APPROVED_v1`). G2 only freezes the *schema template*.

```json
{
  "$schema": "https://a2a.example.org/schemas/agent-card-v1.json",
  "apiVersion": "a2a/v1",
  "kind": "AgentCard",
  "metadata": {
    "id": "agent://org.example/compliance-specialist@1.2.0",
    "name": "compliance-specialist",
    "displayName": "Real-time Regulatory Compliance",
    "version": "1.2.0",
    "description": "Answers and verifies regulatory compliance questions for a bounded jurisdiction set.",
    "provider": {
      "organization": "example-org",
      "url": "https://example.org",
      "supportContact": "agents@example.org"
    },
    "registry": {
      "public": false,
      "enterprise": true,
      "registryUri": "https://agents.internal.example/registry"
    }
  },
  "capabilities": {
    "skills": [
      {
        "id": "reg.lookup",
        "description": "Retrieve applicable regulation clauses",
        "inputModes": ["text", "json"],
        "outputModes": ["text", "json", "a2ui"]
      }
    ],
    "streaming": true,
    "multiTurn": true,
    "pushNotifications": false
  },
  "security": {
    "authMethods": ["oauth2_client_credentials", "mtls"],
    "dataHandling": {
      "retention": "session",
      "pii": "redact",
      "trainingUse": false
    },
    "permissionRequirements": ["jurisdiction:EU", "role:analyst"],
    "compliance": ["SOC2", "ISO27001"]
  },
  "interfaces": {
    "a2a": {
      "endpoint": "https://agents.internal.example/v1/a2a/compliance",
      "transport": "https+json",
      "protocolVersion": "1.0",
      "agentExecutor": "framework-bridge"
    },
    "extensions": {
      "a2ui": {"supported": true, "catalog": "basic|byo", "maxVersion": "v0.9"},
      "ucp": {"supported": false},
      "ap2": {"supported": false},
      "x402": {"supported": false}
    }
  },
  "interactionSchemas": {
    "message": {"$ref": "#/components/schemas/A2AMessage"},
    "task": {"$ref": "#/components/schemas/A2ATask"}
  },
  "routing": {
    "discovery": ["private_registry"],
    "delegationCostClass": "L3",
    "timeoutMs": 60000,
    "hitlOnAmbiguity": true
  },
  "signatures": {
    "cardHash": "sha256:…",
    "signedBy": "registry-key-id"
  }
}
```

### 5.1 Demand-side connection patterns (S2 p.28)

1. **Direct** — hardcoded `RemoteA2aAgent(endpoint=…)` for private/vendor agents.  
2. **Registry** — `AgentRegistry.get_remote_a2a_agent(agent_name=…)` with auth validation.

Orchestrators compose specialists; they must not collapse A2A into naïve MCP `tools/call` without isolation of multi-turn state.

---

## 6. A2UI Generative Interface Constraints (“sheet music”)

**Anchors:** WP-S2 pp.32–43.  
**Security model:** Agent emits **declarative component intent**, never executable UI code. Client renderer maps ids → **trusted catalog** only → blocks XSS/code-injection class failures from raw LLM HTML/JS.

### 6.1 Normative constraints

| ID | Rule | Severity |
|---|---|---|
| A2UI-01 | Output MUST be A2UI declarative JSON (`version`, `updateComponents` / `updateDataModel`), not HTML/JS bundles | blocker |
| A2UI-02 | Component names MUST exist in renderer allowlisted catalog (basic 18 **or** BYO design-system map) | blocker |
| A2UI-03 | Prefer **path bindings** + separate data model updates over string interpolation of untrusted data into structure | major |
| A2UI-04 | Flat adjacency list of components by `id`; root via `createSurface` / agreed root id | major |
| A2UI-05 | No `eval`, inline scripts, arbitrary URLs in actions without allowlist | blocker |
| A2UI-06 | Sanitize text nodes for active content; never reflect raw tool output into UI text without filter | blocker |
| A2UI-07 | Production should **BYO catalog**; basic catalog is prototype-grade (renamed from “standard” in v0.9) | major |
| A2UI-08 | Two generation patterns only: (a) LLM emits A2UI; (b) tool template returns fixed A2UI — both pass catalog gates | major |

### 6.2 Basic catalog (v0.9) — reference only

Layout: `Row`, `Column`, `List`  
Display: `Text`, `Image`, `Icon`, `Divider`  
Containers: `Card`, `Modal`, `Tabs`  
Media: `Video`, `AudioPlayer`  
Interactive: `Button`, `TextField`, `CheckBox`, `Slider`, `DateTimeInput`, `ChoicePicker`

### 6.3 Example message (illustrative, WP-S2 p.35)

```json
{
  "version": "v0.9",
  "updateComponents": {
    "surfaceId": "main",
    "components": [
      {"id": "root", "component": "Column", "children": ["title", "summary", "export"]},
      {"id": "title", "component": "Text", "text": "Q4 Sales", "variant": "h1"},
      {"id": "summary", "component": "Text", "text": "Revenue grew 12% QoQ"},
      {"id": "export", "component": "Button", "child": "export-label",
       "action": {"event": {"name": "export_csv"}}},
      {"id": "export-label", "component": "Text", "text": "Export CSV"}
    ]
  }
}
```

**OPTION_2 posture:** Specify + test catalogs; **do not** enable live generative A2UI in production desktop until OPTION_3 or dedicated UI gate.

---

## 7. UCP / AP2 Commerce Flow (gated)

**Anchors:** WP-S2 pp.43–46. BLUE G2 ultimate objective includes cryptographically gated payment ops.

| Protocol | Role | Analogy (S2) |
|---|---|---|
| **UCP** (Universal Commerce Protocol) | Catalog, availability, cart/order construction with merchants | “Food delivery app brain” |
| **AP2** (Agent Payments Protocol) | Mandated, signed payment authorization with spending limits | “Parent credit card with strict rules” |
| **x402 / L402** (A2A extension) | Permissionless micro-pay: HTTP 402 + invoice + proof-of-payment retry (S2 p.30–31) | Pay-per-call |

### 7.1 Mandate-handshake sequence (normative, abstract)

```
HUMAN issues spending Mandate {merchant_allowlist[], max_amount, currency, expiry, scope}
  → Agent builds order via UCP (catalog → quote → fees/taxes/ETA)
  → Agent requests AP2 payment authorization presenting mandate + quote hash
  → AP2 verifies signature, merchant ∈ allowlist, amount ≤ remaining mandate
  → On success: cryptographic promissory / payment token to merchant
  → On mismatch (e.g. $50 vs approved $18.50): HARD DENY + audit event
  → Evaluation records payment trajectory fields; G5 trust pillars later
```

### 7.2 Workspace rules

| ID | Rule | OPTION_2 |
|---|---|---|
| PAY-01 | No card PANs / raw secrets in prompts, specs, or logs | enforced |
| PAY-02 | Every payment tool_call requires prior **signed mandate** object | enforced / not live |
| PAY-03 | Merchant allowlist mandatory; deny-by-default | enforced |
| PAY-04 | Amount + currency + fee total must hash-match quote | enforced |
| PAY-05 | Live UCP/AP2/x402 disabled until OPTION_3 **or** dedicated finance HITL | **disabled** |
| PAY-06 | Any future payment MCP/A2A extension is Tier ≥ T3 and `hitl: always` | enforced |

---

## 8. Progressive Disclosure Policy (“RAG-for-tools”)

**Anchors:** WP-S2 p.15; HARNESS_SPEC §2.1–2.3; Constraint `C-SEC-02`.

| Rule | Detail |
|---|---|
| D-01 Static core | Constitution + core guardrails only; **not** full tool schema dump |
| D-02 L1 index | Maintain compact tool index: `name`, one-line description, risk, server_id, tier |
| D-03 Intent match | On mission/thought, retrieve top-k schemas (k small, default 3–8) |
| D-04 Load | Inject full JSON schemas only for selected tools |
| D-05 Call | Broker pre-hook → invoke → sanitize observation |
| D-06 Drop | Remove unused schemas when slice completes or token pressure hits |
| D-07 Shadow guard | Reject loading two tools with colliding/similar names without human resolve (F2 tool shadowing) |
| D-08 Token budget | Tools share dynamic Context bucket (HARNESS ~40–60%); tool schemas must not starve observations |
| D-09 Announcement | Prefer task-level tools (“create ticket”) over raw API shard tools (F2 pp.17–18) |

Full executable policy file `TOOL_DISCLOSURE_POLICY.md` is **Step D extended** (BLUE meta-prompt); this section is the registry-embedded interim binding for A/B/D.

---

## 9. Security Controls Catalog (confused-deputy class)

| Threat (WP-F2) | Control ID | Mechanism | Owner harness |
|---|---|---|---|
| Confused deputy (pp.49–51) | SEC-CD-01 | Per-user / least-privilege credentials to MCP backend; never broad service identity for user-scoped ops | Constraint |
| Confused deputy | SEC-CD-02 | Authorization check maps **end-user** rights, not only server capability | Constraint / gateway |
| Dynamic capability injection (pp.40–41) | SEC-DYN-01 | Client allowlist of tool names; pin hashes; honor `listChanged` / disconnect on silent drift | Broker |
| Tool shadowing (pp.42–43) | SEC-SH-01 | Collision + semantic similarity check before disclosure | Broker |
| Malicious tool defs / content (p.44) | SEC-IN-01 | Sanitize inputs (path traversal), sanitize outputs (tokens, PII, active MD/HTML) | Broker + Context |
| Sensitive leaks / elicitation abuse (pp.45–46) | SEC-LK-01 | Taint tracking; separate trusted vs untrusted planner channels if 3P tools enabled | Constraint |
| Coarse MCP auth (p.46) | SEC-AUTH-01 | Gateway per-tool ACL manufacturered outside base MCP OAuth | Broker / G8 policy |
| Slopsquatting packages | SEC-SLOP-01 | `C-LIB-02` install hook; only registry-known packages | Constraint |
| Public unverified MCP in prod | SEC-PUB-01 | Tier T4 ban in prod profiles (S2 p.16) | Procurement |
| Secrets in prompts/config | SEC-SEC-01 | Env-only secrets; `security.redact_secrets: true` observed in profile | Constraint |
| High-risk sinks | SEC-HITL-01 | HITL before file delete, net egress to new hosts, prod data mutate, any payment (F2 p.43; S2 p.16) | HITL tool |

### 9.1 Broker responsibilities (permanent component — BLUE / WP-S2 stack)

Even under OPTION_2 without full implementation yet, the **architectural seat** is reserved:

- Identity & tenant scoping  
- ACL allowlists (server + tool + method)  
- Response sanitization & schema validation  
- Rate limits / timeouts / LRO (>10s → MCP Tasks pattern in later budgets file)  
- Audit log of tool calls (S2 p.16)  
- Collision detection & pin enforcement  

Deferred declarative files (post broader Step D meta-prompt, still pre-live):  
`broker_config.yaml`, `timeout_budgets.yaml`, `TOOL_DISCLOSURE_POLICY.md`, `skills_registry.json`.

---

## 10. Environment Audit Snapshot

| Item | Value |
|---|---|
| Audit timestamp | 2026-07-23 (WSL2) |
| Substrate | Ubuntu-24.04 WSL2 · project venv `.venv-hermes` |
| Active Hermes profile | `wsl-runtime` |
| MCP servers enabled | `context7` (stdio / npx) |
| Memory provider | Honcho @ `http://localhost:8000` (Docker, auth off in local dev — G8 concern) |
| Skills with SKILL.md (depth≤2 sample) | 7 top-level counted in quick scan; full tree large under categories |
| Host bridge | `hermes-api-bridge` 127.0.0.1:8642 (loopback bound) |
| Course precedence | WP-S2 > WP-F2 |

---

## 11. Traceability Matrix (sample claims → anchors)

| Registry claim | Anchor |
|---|---|
| JSON-RPC 2.0 message types | WP-F2 p.23 |
| stdio + Streamable HTTP (SSE optional) | WP-F2 p.23; WP-S2 p.14 |
| Tool definition fields | WP-F2 pp.26–28 |
| Protocol vs tool error shapes | WP-F2 pp.29–30 |
| Capability support skew (Tools vs others) | WP-F2 p.25 Table 2 |
| Discovery sources triad | WP-S2 p.11 |
| RAG-for-tools + HITL + no public prod MCP | WP-S2 pp.15–16 |
| Agent Card + registries | WP-S2 p.25 |
| A2A direct vs registry connect | WP-S2 p.28 |
| A2UI sheet-music + catalog safety | WP-S2 pp.33–34 |
| UCP vs AP2 split | WP-S2 pp.45–46 |
| Confused deputy narrative | WP-F2 pp.49–51 |
| Procurement hierarchy | BLUE G2 + WP-S2 consume-first |
| Resume / options | BLUE G2 HITL contract |

---

## 12. Residual risks & deferred (post-lock)

1. ~~Floating npx pin for `@upstash/context7-mcp`~~ → **CLOSED** pin `1.0.6`.  
2. ~~Step D extended broker/disclosure/timeout/skills artifacts~~ → **CLOSED**.  
3. ~~Step C tier matrix~~ → **CLOSED** (`PROCUREMENT_TIER_MATRIX.yaml`).  
4. ~~Step E structural security audit skeletons~~ → **CLOSED** (`scripts/g2_security/`, `tests/test_g2_*.py`).  
5. Token dualism documented: BLUE **`G2_TOOL_REGISTRY_LOCKED_v1`** authoritative; alias `G2_TOOLING_APPROVED_v1`.  
6. ~~Honcho auth-off + `hermes-api-bridge` non-loopback bind~~ → **CLOSED** rebound `hermes-api-bridge` to `127.0.0.1:8642`.  
7. Tier-4 registered count **0** — keep under OPTION_2.  
8. Broker **runtime** still `DECLARED_NOT_WIRED` (schema locked only).

---

## 13. Definition of Done (G2 lock)

1. ✅ WP-F2 + WP-S2 ingested via PyMuPDF; synthesis tables anchored.  
2. ✅ Local CLI + MCP + Docker audit recorded.  
3. ✅ Registry + compat matrix + Step C/D-ext artifacts under `specs/g2_tools/`.  
4. ✅ HITL granted `OPTION_2_STANDARD` / `G2_TOOL_REGISTRY_LOCKED_v1`.  
5. ✅ Structural security tests + pin enforcement green (sandbox).  
6. ✅ Commit + tag `tool-registry-v1.0.0` (Step F).  
7. ✅ G3 migration note prepared.

---

*G2 TOOL_REGISTRY.md v1.0.0 — declarative lock; broker runtime not authorized by this file alone.*
