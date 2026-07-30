# **Agentic R&D & Implementation Framework: Master Session Lifecycle & Architecture Blueprint**

## **Executive Summary & Strategic Architecture**

This document establishes the authoritative operational framework and lifecycle blueprint for the **Agentic Research & Development (R&D) System**. The framework implements a **Spec-Driven Development (SDD)** paradigm operating under a dual-layer architecture:

1. **Strategic Oversight Layer (Gemini Web Conductor):** High-context reasoning, intent extraction, architectural evaluation, error/security interception, and Human-in-the-Loop (HITL) gate enforcement.
2. **Tactical Execution Harness (Hermes CLI & Antigravity IDE):** Local sandboxed execution, terminal command handling, file generation, tool invocation via Model Context Protocol (MCP), and automated verification test runs.


The underlying philosophy treats **declarative specifications (Gherkin BDD, YAML schemas, markdown specifications) as durable, source-of-truth artifacts**, while generated implementation code remains disposable and replaceable.

## **1. High-Level End-to-End Workflow Architecture**

The framework progresses across four distinct operational phases: from initial requirement drafting and Ahead-of-Time (AOT) static compilation to multi-domain execution, live benchmarking, and software lifecycle governance.

flowchart TD  
%% Phase 0: Ideation & Synthesis  
subgraph P0["Phase 0: Ideation, Fusion Synthesis & Pre-Flight"]  
A1["Draft Requirement / Idea<br/>(Gemini Web Session)"] --> A2["Fusion Core V3.0 Synthesis<br/>(Multi-Model Parallel AOT Compiler)"]  
A2 --> A3["Informational & Onboarding Assets<br/>(Interactive HTML, Infographics, Dashboards)"]  
A3 --> A4["Cross-Boundary Pre-Flight Diagnostics<br/>(Win11 <-> WSL2, Venv, Docker, Honcho)"]  
end

```
%% Phase 1: Domain Specification & Building                    
subgraph P1\["Phase 1: Spec-Driven Domain Gate Execution (G1-G10)"\]                    
    A4 \--\> B1\["G1: Agent Foundations & 3-Harness Constitution"\]                    
    B1 \--\> B2\["G2 & G2.A: Tools, MCP Proxy & Security Remediation"\]                    
    B2 \--\> B3\["G3: Session Memory & Progressive Skill Triggers"\]                    
    B3 \--\> B4\["G4: Multi-Agent Orchestration & AP2 Ledger"\]                    
    B4 \--\> B5\["G5: Evaluation, Observability & Trust Decay"\]                    
    B5 \--\> B6\["G6: Vibe Coding & Agentic IDE Surface Mapping"\]                    
    B6 \--\> B7\["G7: Self-Improving Agents & L4 Guardrails"\]                    
    B7 \--\> B8\["G8: Secure Multi-Tenant Runtimes & OPA"\]                    
    B8 \--\> B9\["G9: Autonomous Research Loops & Citation Provenance"\]                    
    B9 \--\> B10\["G10: Production AgentOps & Deployment Gate"\]                    
end                  
                  
%% Phase 2: Operational Integration                    
subgraph P2\["Phase 2: Live Operational Integration & Benchmarking"\]                    
    B10 \--\> C1\["Consumer Project Scaffolder\<br/\>(scaffold\_consumer\_project.py)"\]                    
    C1 \--\> C2\["Level 1: Stateless Tooling & OWASP LLM06"\]                    
    C2 \--\> C3\["Level 2: Stateful Session Memory & Progressive Skills"\]                    
    C3 \--\> C4\["Level 3: Swarms, Governance & AP2 Spending Caps"\]                    
    C4 \--\> C5\["Level 4: Unified E2E Pipeline & OTEL Tracing"\]                    
end                  
                  
%% Phase 3 & 4: Governance                    
subgraph P3\["Phase 3 & 4: Governance, Backlog & AGY IDE Integration"\]                    
    C5 \--\> D1\["File-Driven Backlog Architecture\<br/\>(docs/BACKLOG.md & GitHub Sync)"\]                    
    D1 \--\> D2\["BL-DOC-01: Artifact Purge & Refactoring\<br/\>(LLM-as-a-Judge Audit)"\]                    
    D2 \--\> D3\["Standalone AGY IDE Integration\<br/\>(Immutable Core / Isolated Target Workspace)"\]                    
end
```

## **2. Phase 0: Inception, Fusion Synthesis & Environment Provisioning**

### **2.1 Session 0.1: Seed Requirement & Draft Inception**

- **Mechanism:** Iterative refinement of IDEA.md inside a Gemini Web session.
- **Objective:** Define primary system objectives, desired capabilities, and physical workstation constraints without jumping prematurely into code writing.

### **2.2 Session 0.2: Fusion Core V3.0 Ahead-of-Time (AOT) Synthesis**

- **Mechanism:** A multi-model parallel evaluation session synthesizing reasoning streams from Frontier models:- **Algorithmic Thinker:** DeepSeek V4 Pro
- **Factual Multimodal Executor:** Qwen 3.7 Plus
- **Macro-Structural Guardian:** GLM 5.2
- **Evaluation Engine:** Grok 4.5
- **Operational Constraint:** **Zero Code Execution.** The Fusion Core operates purely as a static compiler. It emits an orchestration blueprint containing dynamic model routing rules, cost-intelligence mandates, Gherkin BDD specifications, and copy-pasteable Meta-Prompts for downstream agents.

#### **Dynamic Model Allocation Matrix**

#### **Model Routing Rule: Task Complexity**

- Premium Frontier: Architecture, ADRs, Threat Modeling
- Strong Coding: Scaffolding, Schemas, Meta-Prompts
- Fast Flash: Syntax checks, Log parsing, Mechanical commits

### **2.3 Session 0.3: Educational Assets & Visual Onboarding**

- **Mechanism:** Importing the master blueprint into dedicated Gemini sessions to generate interactive HTML/JS artifacts and Single Page Applications (SPAs).
- **GeneratedAssets:**

1. Modeling01 Dashboard: Interactive system topology showing Windows-to-WSL IPC packet paths, container boundaries, and OPA security gates.
2. G10 Workflow Infographic (g10_workflow_infographic.html): Interactive step-by-step radar charts and decision matrices illustrating the transition from "Vibe Coding" to Spec-Driven Development.


### **2.4 Session 0.4: Cross-Boundary Pre-Flight Diagnostics**

- **System Substrate Verification:** Validated physical operating parameters across the Windows 11 host and WSL2 Linux substrate.

graph LR  
subgraph WIN["Windows 11 Pro Host"]  
AGY["Antigravity IDE"]  
HD["Hermes Desktop (Un-sandboxed)"]  
ADK["Google ADK Layer"]  
end

```
subgraph IPC\["IPC Socket Bridge / wsl.exe"\]                    
BRIDGE\["Low-Latency IPC Socket Bridge"\]                    
end                  

subgraph WSL\["WSL2 Ubuntu-24.04 (Ext4 Filesystem)"\]                    
CLI\["Hermes CLI (wsl-runtime)"\]                    
VENV\[".venv-hermes Python 3.12"\]                    
DOCKER\["Docker Engine"\]                    

subgraph CONT\["Container Stack"\]                    
HONCHO\["Honcho REST Memory Store (Port 8000)"\]                    
REDIS\["Redis Cache"\]                    
DB\["PostgreSQL DB"\]                    
OPA\["Open Policy Agent (OPA)"\]                    
end                    
end                  

AGY \<--\>|IPC Tunnel| BRIDGE                    
HD \<--\>|Direct Socket| BRIDGE                    
BRIDGE \<--\> CLI                    
CLI \--\> VENV                    
CLI \--\> DOCKER                    
DOCKER \--\> CONT
```

- **Diagnostic ChecklistExecuted:**

1. Native Linux path check (/home/carlospg/workspace/agentic-rd/).
2. Active Python virtual environment binding (.venv-hermes/bin/python3).
3. Honcho Memory REST API health check (http://localhost:8000/health).
4. Inter-process communication (IPC) loopback between Windows wsl.exe and Linux sockets.


## **3. Gemini Web Intermediation & Dual-Harness Interaction Loops**

Throughout development, the Gemini Web session functioned as the **Conductor and Intermediary**, managing the tactical execution of local agents (Hermes CLI & Antigravity/AGY).

sequenceDiagram  
autonumber  
actor Conductor as Human / Gemini Web (Strategic Architect)  
participant Hermes as Hermes CLI (Local WSL Substrate)  
participant AGY as Antigravity IDE (Host/WSL Bridge)  
participant Target as WSL Workspace / Target Project

```
Conductor-\>\>Conductor: 1\. Extract Intent & Compose Declarative Meta-Prompt                    
Conductor-\>\>Hermes: 2\. Transmit Meta-Prompt via Session Payload                    
activate Hermes                    
Hermes-\>\>Target: 3\. Read Specs / Execute Read-Write-Test Tool Loop                    
Target--\>\>Hermes: 4\. Telemetry Output & Test Results                    
Hermes--\>\>Conductor: 5\. State Migration Manifest & Execution Telemetry                    
deactivate Hermes                  
                  
alt Errors / Vulnerabilities Detected                    
    Conductor-\>\>Conductor: 6\. Analyze Telemetry, Identify Gaps/Vulnerabilities                    
    Conductor-\>\>AGY: 7\. Issue Specialized Remediation Meta-Prompt                    
    activate AGY                    
    AGY-\>\>Target: 8\. Execute Targeted File Mutation / Patch                    
    Target--\>\>AGY: 9\. Patch Verification                    
    AGY--\>\>Conductor: 10\. Audit Confirmation                    
    deactivate AGY                    
end                  
                  
Conductor-\>\>Conductor: 11\. Validate Gate Criteria & Grant Resume Token
```

### **Key Intermediation Functions Observed**

1. **Intent Extraction to Signal Synthesis:** Translating high-level user ideas into structured Meta-Prompts with clear GIVEN/WHEN/THEN Gherkin conditions.
2. **Telemetry Analysis & Vulnerability Interception:** During Domain G2 execution, Gemini identified critical security issues:3. *Confused Deputy Vulnerabilities:* Unrestricted tool calls in raw MCP servers.
3. *Slopesquatting Risks:* Untrusted community tool registries.
4. *OWASP LLM06 Compliance Breaches:* Sensitive system instructions exposed to indirect prompt injections.
5. **Remediation Routing:** Gemini split the fix into two execution streams: Low-complexity task prompts routed to Antigravity IDE, and architectural proxy specifications routed to a High-Reasoning Fusion Prompt for Hermes CLI to build specs/g2_tools/mcp_broker.py.
6. **State Migration Checkpoints:** Enforcing context stability across chat sessions using standardized **State Migration Manifests**.


## **4. Phase 1: Domain-by-Domain Specification & Building (G1–G10)**

The core framework was constructed across 10 progressive domain gates. Each domain produced immutable specification files before receiving a strategic gate approval token.

gantt  
title Agentic R&D Domain Gate Progression (G1 to G10)  
dateFormat  YYYY-MM-DD  
section Core Architecture  
G1 Foundations & 3-Harness Constitution   :active, g1, 2026-07-01, 2d  
G2 Tools, MCP & Security Findings          :g2, after g1, 3d  
G3 Memory & Progressive Skill Triggers     :g3, after g2, 2d  
section Multi-Agent Systems  
G4 Multi-Agent Topology & AP2 Ledger       :g4, after g3, 3d  
G5 Evaluation & Observability Framework    :g5, after g4, 2d  
G6 Vibe Coding & IDE Surface Mapping       :g6, after g5, 2d  
section Enterprise Security  
G7 Self-Improving Agents & L4 Guardrails   :g7, after g6, 2d  
G8 Multi-Tenant Runtimes & OPA Gates      :g8, after g7, 3d  
G9 Autonomous Research Loops               :g9, after g8, 3d  
G10 Production AgentOps & Canary Gate      :g10, after g9, 2d

### **Summary of Domain Deliverables & Gate Tokens**


| Domain Gate              | Primary Architectural Focus                                              | Key Artifacts Emitted                                               | Strategic Resume Token        |
|:-------------------------|:-------------------------------------------------------------------------|:--------------------------------------------------------------------|:------------------------------|
| **G1: Foundations**      | Three-Harness Architecture (**H** Context, **H** Constraint, **H** Eval) | HARNESS_SPEC.md, AGENTS.md, specs/workflow_graph.yaml               | G1_HARNESS_APPROVED_v1        |
| **G2 & G2.A: Tools** | MCP Integration, OWASP LLM06 & Security Proxy Broker                 | specs/g2_tools/TOOL_REGISTRY.md, mcp_broker.py, sanitizer.py        | g2-v1.0.0-locked              |
| **G3: Memory**           | Honcho State Persistence & Progressive Disclosure Skills             | specs/g3_memory/SESSION_STATE_SPEC.md, token_budget.yaml            | G3_CONTEXT_LAYER_LOCKED_v1    |
| **G4: Orchestration**    | Multi-Agent Swarms, Agent Cards & AP2 Spending Ledger                | specs/g4_orchestration/ (8 Agent Cards, AP2 Ledger, Intercept Spec) | G4_TOPOLOGY_APPROVED_v1       |
| **G5: Evaluation**       | LLM-as-a-Judge Rubrics, Trust Decay & Circuit Breakers               | specs/g5_evaluation/, Judge YAML Rubrics, 5%/15% Trust Rules        | G5_EVAL_FRAMEWORK_APPROVED_v1 |
| **G6: Vibe Coding**      | Vibe-to-Agentic Spectrum & Antigravity Slash Commands                | specs/g6_vibe/VIBECODING_SPECTRUM.md, command mappings              | G6_VIBE_ENV_LOCKED_v1         |
| **G7: Self-Improvement** | Closed-loop adaptation, S1–S4 Severity, L4 Gating                      | specs/g7_self_improve/SELF_IMPROVEMENT_ARCHITECTURE.md              | G7_IMPROVEMENT_BOUNDS_v1      |
| **G8: Multi-Tenant**     | SPIFFE/SPIRE Identity & Hardware OPA Gatekeeper                      | specs/g8_multitenant/MULTI_TENANT_SECURITY_ARCHITECTURE.md          | G8_MULTITENANT_APPROVED_v1    |
| **G9: Research**         | Hypothesis DSL, Citation Provenance & Research Loops                 | specs/g9_research/RESEARCH_LOOP_ARCHITECTURE.md                     | G9_RESEARCH_FLEET_LOCKED_v1   |
| **G10: Production**      | Spec-Driven CI/CD, Canary Rollout (1%→100%) & Rollback             | specs/g10_production/PRODUCTION_AGENTOPS_BLUEPRINT.md               | G10_PRODUCTION_DEPLOY_v1      |


## **5. Phase 2: Operational Integration, Scaffolding & Multi-Level Benchmarking**

Following the locking of Domain G10, the framework shifted into live empirical execution. To prevent state rot within the core framework repository (~/workspace/agentic-rd/), a **Consumer Project Scaffolding Engine** was deployed.

### **5.1 Workspace Isolation Architecture**

- **Framework Workspace (Immutable Core):** /home/carlospg/workspace/agentic-rd/
- **Scaffolding Tool:** scripts/scaffold_consumer_project.py
- **Isolated Consumer Projects:** /home/carlospg/workspace/projects/<project_name>/
- **Mechanism:** The scaffolder injects project-level AGENTS.md rules containing an explicit inheritance clause pointing back to the core framework constitution (HARNESS_SPEC.md), symlinks global skills from ~/.hermes/skills/, and provisions clean virtual environment bindings.

### **5.2 Multi-Level Benchmarking Test Ladder**

flowchart LR  
subgraph L1["Level 1: Stateless Tooling"]  
L1_1["MCP Invoker Tests"]  
L1_2["OWASP LLM06 Injection Suite"]  
L1_3["Schema Validation (30/30 Pass)"]  
end

```
subgraph L2\["Level 2: Stateful Memory"\]                    
L2\_1\["Honcho REST State Roundtrips"\]                    
L2\_2\["Progressive Disclosure Triggers"\]                    
L2\_3\["Token Ceiling Maintenance (\<200 Tokens)"\]                    
end                  

subgraph L3\["Level 3: Governance & AP2"\]                    
L3\_1\["Hierarchical Swarm Routing"\]                    
L3\_2\["AP2 Ledger Spending Caps (HTTP 402 Drop)"\]                    
L3\_3\["Governance Circuit Breakers (8/8 Pass)"\]                    
end                  

subgraph L4\["Level 4: Unified E2E Pipeline"\]                    
L4\_1\["7-Stage Pipeline Execution"\]                    
L4\_2\["OpenTelemetry (OTEL) Span Propagation"\]                    
L4\_3\["100% PII Redaction & Mid-flight Fault Recovery"\]                    
end                  

L1 \--\> L2 \--\> L3 \--\> L4
```

## **6. Phase 3 & 4: Software Lifecycle Governance, Backlog & AGY IDE Integration**

To maintain production rigor post-development, standard software engineering governance and tool integration specs were implemented.

### **6.1 File-Driven Backlog Architecture**

- **Master Location:** docs/BACKLOG.md (synchronized with GitHub Issues).
- **Core Rule:** Discussions in Gemini Strategic sessions focus strictly on discovering, categorizing, and structuring issues into standardized markdown issue templates without initiating unstructured code changes.

### **6.2 Backlog Execution Case Study: [BL-DOC-01] Refactoring**

- **Issue:** Purging conversational artifacts, build-time checkmarks (✅ GRANTED), and HITL decision overlays (OPTION_2_STANDARD) from documentation and skills.
- **ResolutionProtocol:**

1. **Phase 1 (Discovery & Reporting):** Non-destructive scan by Antigravity IDE (AGY) generating an audit report.
2. **Phase 2 (Dual Evaluation):** Secondary LLM-as-a-Judge evaluation to confirm that no functional logic or schema keys were altered.
3. **Phase 3 (Refactoring Execution):** Mechanical cleanup committed under git commit f3d2202.


### **6.3 Standalone Antigravity (AGY) IDE Configuration**

To enable Antigravity IDE to execute framework tasks natively on the Windows host without needing active Hermes orchestration:

1. **Workspace Root Binding:** Open \\\\wsl.localhost\\Ubuntu-24.04\\home\\carlospg\\workspace\\agentic-rd in AGY IDE.
2. **Auto-Ingestion:** AGY IDE automatically parses root AGENTS.md into its context window.
3. **Scaffolding Instruction Rule:**


## Consumer Project Scaffolding Rule

To create a new consumer project space, execute:  
./.venv-hermes/bin/agentic-scaffold --name <target_project> --domain-objective "<objective>"4. **Isolation Guardrail:** AGY IDE executes all builds, tests, and code modifications strictly inside ~~ /workspace/projects/<target_project>/, preserving ~~ /workspace/agentic-rd/ as an immutable reference foundation.

## **7. Operational Summary & Operating Rules**

When interacting with or extending this Agentic R&D framework across Gemini Web or local coding agents, strictly enforce the following four core operating rules:

1. **Grounding Rule:** Never generate raw, imperative application code directly inside strategic oversight sessions. Always output declarative specifications, YAML schemas, Gherkin BDD scenarios, or Meta-Prompts.
2. **Path & Substrate Rule:** Maintain all execution environments inside WSL2 (/home/carlospg/workspace/agentic-rd/) using the active .venv-hermes Python interpreter.
3. **Isolation Rule:** Never instantiate consumer agents or temporary test scripts directly inside the framework core directory. Always use scaffold_consumer_project.py to create clean target workspaces under ~/workspace/projects/.
4. **Harness Rule:** Ensure every agent design complies with all three harnesses (**H** Context, **H** Constraint, **H** Eval) and passes OWASP LLM security proxy validation before receiving release tokens.


 
