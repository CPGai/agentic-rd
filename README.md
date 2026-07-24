# Agentic R&D & Implementation Blueprint

**Dual-Course Synthesis** (Nov 2025 → June 2026)  
**Domain Status:** G1–G8 `APPROVED` — `OPTION_2_STANDARD` / `G1_HARNESS_APPROVED_v1` / `G2_TOOL_REGISTRY_LOCKED_v1` / `G3_CONTEXT_LAYER_LOCKED_v1` / `G4_TOPOLOGY_APPROVED_v1` / `G5_EVAL_FRAMEWORK_APPROVED_v1` / `G6_VIBE_ENV_LOCKED_v1` / `G7_IMPROVEMENT_BOUNDS_v1` / `G8_MULTITENANT_APPROVED_v1` ✅ · G9 `READY`

A formally-specified **Three-Harness Factory Model** for autonomous agentic systems, synthesizing the Google AI Agents Whitepaper Series (WP-F1–F5, Nov 2025) and Google Vibe Coding / Agentic Engineering Series (WP-S1–S5, June 2026) into a single, auditable architectural constitution spanning 10 domains (G1–G10).

```
Agent  =  Model  +  Harness
Harness = Context ∪ Constraint ∪ Evaluation
Loop   =  Read → Write → Test → Observe → Fix
```

---

## Architecture

The project's architectural constitution is triangulated across three binding artifacts:

| Artifact | Purpose |
|---|---|
| [`HARNESS_SPEC.md`](./HARNESS_SPEC.md) | Deep architecture — Context/Constraint/Evaluation harness designs, L0–L4 taxonomy mapping, 18-rule constraint catalog, token budgets, traceability matrix |
| [`AGENTS.md`](./AGENTS.md) | Global runtime rules — model-routing matrix (Premium/Strong/Flash), HITL gate map (G1–G10), Think–Act–Observe trajectory, always-on static Instructions |
| [`specs/workflow_graph.yaml`](./specs/workflow_graph.yaml) | Machine-readable topology — 41 edges, 10 domain nodes, 3 harness nodes, decision overlays, validation invariants |

**Course-2 (WP-S*) always supersedes Course-1 (WP-F*) on overlap.**

---

## Domain Landscape

| Domain | Focus | Harness Emphasis | Status |
|---|---|---|---|
| **G1** | Agent Foundations & Architecture | 🏛️ All three | ✅ `APPROVED` |
| **G2** | Tool Use & MCP | Constraint, Context | ✅ `APPROVED` |
| **G3** | Context Engineering / Sessions / Memory | Context | ✅ COMPLETED (`context-v1.0.0` · `OPTION_2_STANDARD`) |
| **G4** | Multi-Agent Orchestration | All three | ✅ COMPLETED (`orchestration-v1.0.0` · `OPTION_2_STANDARD`) |
| **G5** | Evaluation & Observability | Evaluation | ✅ COMPLETED (`eval-v1.0.0` · `OPTION_2_STANDARD`) |
| **G6** | Vibe Coding → Spec Harness | Constraint, Evaluation | ✅ COMPLETED (`vibecoding-v1.0.0` · `OPTION_2_STANDARD`) |
| **G7** | Self-Improvement (L4 gated) | Evaluation, Constraint | ✅ COMPLETED (`self-improvement-v1.0.0` · `OPTION_2_STANDARD`) |
| **G8** | Multi-Tenant & Policy | Constraint | ✅ COMPLETED (`multitenant-v1.0.0` · `OPTION_2_STANDARD`) |
| **G9** | Autonomous Research Loops | Context, Evaluation | Ready |
| **G10** | Production AgentOps | All three | Ready |

Each domain includes a 6-step delegation runbook (A–F), copy-pasteable Meta-Prompts, and a GIVEN/WHEN/THEN HITL gate with decision-support matrices (Option 1 Conservative / Option 2 Standard / Option 3 Creative).

---

## Substrate & Runtime

| Component | Specification |
|---|---|
| **OS** | WSL2 Ubuntu 24.04 |
| **Python** | 3.12 (`.venv-hermes` virtual environment) |
| **Harness Runtime** | Hermes CLI + Antigravity unified harness |
| **Skills Spec** | agentskills.io progressive disclosure (L1 → L2 → L3) |
| **Model Tiers** | Premium Frontier · Strong Coding · Fast Flash (dynamic routing) |

**Execution routing:** All shell/Python commands route exclusively through the WSL2 substrate:
```bash
wsl -d Ubuntu-24.04 bash -c "cd /home/carlospg/workspace/agentic-rd && source .venv-hermes/bin/activate && <command>"
```

---

## Directory Layout

```
agentic-rd/
├── AGENTS.md                    # Global runtime constitution (always-on Instructions)
├── HARNESS_SPEC.md              # Architectural deep-spec (Context/Constraint/Eval)
├── specs/
│   ├── workflow_graph.yaml     # Machine-readable factory topology
│   ├── references/             # Immutable whitepaper corpus (WP-F1–F5, WP-S1–S5)
│   └── *.md                    # Domain blueprints (G2–G10)
├── skills/                     # Progressive disclosure skill library (agentskills.io)
├── .gherkin/                   # BDD acceptance scenarios (harness + domains)
├── tests/                      # Structural & functional test suites
├── logs/                       # Agent telemetry & evaluation logs
├── configs/                    # Harness configuration (hooks, policy, OTEL stubs)
├── examples/                   # Few-shot trajectories & golden patches
├── docs/                       # Supplementary documentation & ADRs
├── .gitignore
├── LICENSE                     # MIT
├── CONTRIBUTING.md
└── README.md                   # ← this file
```

---

## Getting Started

### Prerequisites
- Windows 11 host with WSL2 enabled
- Ubuntu 24.04 WSL2 distribution
- Python 3.12 + project venv

### Clone & Setup
```bash
git clone https://github.com/<your-org>/agentic-rd.git
cd agentic-rd
python3 -m venv .venv-hermes
source .venv-hermes/bin/activate
pip install -r requirements.txt  # when available
```

### Running Domain Steps
Domain delegation is specified in `specs/references/AGENTIC R&D & IMPLEMENTATION BLUE.md`. Each domain's Meta-Prompt targets:
- **Step A** → Premium Frontier (synthesis)
- **Step B** → Fast Flash (discovery)
- **Step C** → Strong Coding (decomposition)
- **Step D** → Strong Coding (scaffold)
- **Step E** → Strong Coding (tests)
- **Step F** → Fast Flash (validation + commit)

Every strategic domain gate (G1–G10) surfaces a `HARD_STOP` decision matrix and requires a human resume token before continuing.

---

## G1–G8 Gate Decisions (Active)

| Field | G1 Foundations | G2 Tools & MCP | G3 Context & Memory | G4 Multi-Agent | G5 Eval & Observability | G6 Vibe→Spec | G7 Self-Improvement | G8 Multi-Tenant |
|---|---|---|---|---|---|---|---|---|
| **Decision** | `OPTION_2_STANDARD` | `OPTION_2_STANDARD` | `OPTION_2_STANDARD` | `OPTION_2_STANDARD` | `OPTION_2_STANDARD` | `OPTION_2_STANDARD` | `OPTION_2_STANDARD` | `OPTION_2_STANDARD` |
| **Resume Token** | `G1_HARNESS_APPROVED_v1` ✅ | `G2_TOOL_REGISTRY_LOCKED_v1` ✅ | `G3_CONTEXT_LAYER_LOCKED_v1` ✅ | `G4_TOPOLOGY_APPROVED_v1` ✅ | `G5_EVAL_FRAMEWORK_APPROVED_v1` ✅ | `G6_VIBE_ENV_LOCKED_v1` ✅ | `G7_IMPROVEMENT_BOUNDS_v1` ✅ | `G8_MULTITENANT_APPROVED_v1` ✅ |
| **Tag** | — | `tool-registry-v1.0.0` | `context-v1.0.0` | `orchestration-v1.0.0` | `eval-v1.0.0` | `vibecoding-v1.0.0` | `self-improvement-v1.0.0` | `multitenant-v1.0.0` |
| **Default Agent Level** | L2 | L2 | L2 | L2 (→L3 after G4 gate) | L2 | L2 |
| **Harness / Substrate** | Three-harness Factory + full audit trail | Security Broker Proxy + NPM Pins + Loopback Boundary | Dynamic Token Budget + Honcho Memory + Skills Co-Load Policy | Hierarchical Coordinator + Agent Cards + Policy Seat (DECLARED) | LLM-as-Judge + OTEL Trajectories + Trust Score + Circuit Breaker + 5%/15% Thresholds | Vibe→Agentic Spectrum + SDD + Dune Policy + G5 Inheritance + Slash Command Routing |

---

## References

- **WP-F1–F5:** Introduction to Agents, Agent Tools & MCP, Context Engineering, Agent Quality, Prototype to Production (Nov 2025)
- **WP-S1–S5:** The New SDLC with Vibe Coding, Agent Tools & Interoperability, Agent Skills, Agent Security & Evaluation, Spec-Driven Production Grade Development (June 2026)
- **Blueprint:** [`specs/references/AGENTIC R&D & IMPLEMENTATION BLUE.md`](./specs/references/AGENTIC%20R&D%20&%20IMPLEMENTATION%20BLUE.md)

---

## License

MIT — see [`LICENSE`](./LICENSE)

---

*Generation is solved. Verification, judgment, and direction are the new craft.* — WP-S1