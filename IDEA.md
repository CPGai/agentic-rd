# IDEA.md: Sovereign Agentic R&D Workspace (Master Spectrum G1–G10)

## 1. Master Vision

Build a zero-trust, production-grade local agentic environment inside WSL2/Docker based on the June 2026 Factory Model SDLC. This workspace establishes a permanent, self-improving agent chassis that progresses systematically through 10 integrated architectural domains (G1–G10).

## 2. Phased Architectural Roadmap

- **Phase 1: Foundation & Infrastructure (G1–G3)**- G1: Root Constitution (`AGENTS.md`), Factory Harness (`HARNESS_SPEC.md`), and Workflow Graph.
- G2: MCP Broker (`TOOL_REGISTRY.md`), dynamic skill procurement, and confused-deputy defenses.
- G3: Context Engineering, `skills/` library with L1–L3 progressive disclosure, and session state.
- **Phase 2: Multi-Agent Orchestration & Governance (G4–G6)**
- G4: Hierarchical Agent-to-Agent (A2A) cards, Gherkin task decomposition, and AP2 ledgers.
- G5: OpenTelemetry trajectory tracing, LLM-as-a-Judge, and Red/Blue/Green security testing.
- G6: Antigravity / Hermes Vibe Coding integration and dynamic model-routing tiers.
- **Phase 3: Autonomous Autonomy & Production Operations (G7–G10)**
- G7: Self-improving skill acquisition, Pivot/Refine decision loops, and rollback bounds.
- G8: Ephemeral gVisor/Docker tenant isolation and hybrid policy enforcement.
- G9: Autonomous research loops with verifiable citations and hypothesis specs.
- G10: Spec-driven CI/CD, canary releases, Doctor health checks, and production AgentOps.

## 3. Runtime Environment & Tooling

- Host: Windows 11 Pro / WSL2 (Ubuntu) / Docker Desktop
- Harnesses: Hermes CLI Terminal + Antigravity 2.0 IDE / Unified Loop
- Protocols: Model Context Protocol (MCP), agentskills.io (L1/L2/L3), OpenTelemetry, Gherkin BDD

## 4. Execution Rules

- Spec-Driven SDLC: No raw code generation; produce only declarative Markdown/YAML specs, Gherkin BDD, and tests.
- Monotonic Progression: Execute sequentially G1 -> G10. Every domain must clear its strategic HITL Gate Contract before the next domain begins.

## 5. Local Environment, Tooling Registry & Bi-Directional Cross-Boundary Execution Bridge

This section codifies the verified hybrid architecture mapping tool registries and cross-kernel interop channels between the Windows host and the WSL2 substrate for the Hermes agent orchestration loop.

### 1. Host & Substrate Tooling Inventories


| Environment                         | Core Tooling / CLI                                                                              | Registry / Execution Path                                                                                                                                                                                                                                       |
|:------------------------------------|:------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Windows Host (11 Pro)**           | `google-agents-cli` (ADK)<br>`uvx`<br>`node / npm`<br>`docker`<br>`git` | `C:\Users\carlo\.local\bin\google-agents-cli.exe`<br>`C:\Users\carlo\AppData\Local\hermes\bin\uvx.exe`<br>`C:\Program Files\nodejs\`<br>`C:\Program Files\Docker\Docker\resources\bin\docker.exe`<br>`C:\Program Files\Git\cmd\git.exe` |
| **WSL2 Substrate (`Ubuntu-24.04`)** | System Binaries (`python3`, `uv`, `docker`)<br>Isolated Workspace Venv (`.venv-hermes`)   | `/usr/bin/` / `/usr/local/bin/`<br>`$HOME/workspace/agentic-rd/.venv-hermes/bin/`                                                                                                                                                                         |


### 2. Bi-Directional Cross-Boundary Execution Bridge

To eliminate context clipping and allow unhindered cross-kernel command routing between the Windows control plane and the sandboxed Linux harness:

- **Direction A (Windows ➔ WSL2 Substrate):** Driven via process wrappers from Windows PowerShell targeting the Ubuntu harness:		wsl -d Ubuntu-24.04 -e bash -c "source ~/workspace/agentic-rd/.venv-hermes/bin/activate && python3 --version"
- **Direction B (WSL2 Substrate ➔ Windows Host):** Enabled via active WSL Interop and secure DrvFs mount parameters. Configured via /etc/wsl.conf


```
├── AGENTS.md                   # Global Constitution (G1 Chassis - Ingested on every turn)          
├── HARNESS_SPEC.md             # Factory Model Harness Rules (G1 Chassis)          
├── workflow_graph.yaml         # System Execution Graph (G1/G4)          
├── IDEA.md                     # Master Vision Seed Document          
│          
├── specs/                      # Domain Specifications          
│   ├── g1_foundations/          
│   ├── g2_tools/          
│   ├── g3_memory/          
│   └── ... up to g10_agentops/          
│          
├── skills/                     # Progressive Disclosure Skill Library (agentskills.io)          
│   ├── skill_a/          
│   │   ├── metadata.yaml       # L1: ~50 tokens (Always indexed)          
│   │   ├── SKILL.md            # L2: Main body (Loaded on trigger)          
│   │   └── references/         # L3: Heavy assets/scripts (Loaded on demand)          
│   └── ...          
│          
├── tests/                      # BDD & Evaluation Suites          
│   ├── g1/          
│   ├── g2/          
│   └── ...          
│          
└── logs/                       # OpenTelemetry Trajectories & Audit Telemetry
```

 
