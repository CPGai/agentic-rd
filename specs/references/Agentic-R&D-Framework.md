# **KNOWLEDGE BASE: AGENTIC R&D & IMPLEMENTATION FRAMEWORK**

## **System Map, Runtime Harnesses, and Operational Specification**

## **1. System Baseline & Environment Architecture**

### **Substrate & Runtime Environment**

- **Operating Substrate:** WSL2 Ubuntu-24.04 LTS on Ext4 Native File System (/home/carlospg/workspace/agentic-rd/).
- **Host Interop Bridge:** Windows 11 Pro host system communicating via low-latency IPC socket bridge with WSL2.
- **Active Python Interpreter:** /home/carlospg/workspace/agentic-rd/.venv-hermes/bin/python3.
- **Global Instruction Anchor:** ~/.hermes/instructions forcing environment activation and cross-boundary path routing.
- **Framework Lock Status:** Locked under Master Tag production-v1.0.0 (Git Commit 6b88170, Authorization Token G10_PRODUCTION_DEPLOY_v1).
- **Operating Posture:** OPTION_2_STANDARD (Binding across all domains).

### **Directory Layout & Artifact Map**

Plaintext  
/home/carlospg/workspace/agentic-rd/  
├── AGENTS.md                          # Root System Constitution & Governance  
├── HARNESS_SPEC.md                    # Three-Harness Factory Model Rules  
├── workflow_graph.yaml                # Master Execution Graph  
├── configs/                           # Global Engine Configurations  
├── logs/                              # Audit Traces & Telemetry Logs  
├── scripts/                           # Deterministic Verification & Scaffolding Scripts  
│   ├── verify_g1_harness.py ... verify_g10_production.py  
│   └── scaffold_consumer_project.py  # Zero-Touch Project Provisioner  
├── skills/                            # Framework Skill Modules (agentskills.io)  
│   └── software-development/  
│       ├── agentic-rd-g-domain-runbook/  
│       ├── context-assembly-g3/  
│       ├── hermes-mcp-server-setup/  
│       ├── session-memory-honcho/  
│       ├── wsl2-execution-routing/  
│       └── consumer-project-scaffolder/  
└── specs/                             # Declarative Specifications (G1–G10)  
├── g1_foundations/ ... g10_production/  
└── references/                    # Static Whitepaper Anchors (WP-F1..F5, WP-S1..S5)

## **2. Core Engineering Philosophy: Spec-Driven Development (SDD)**

1. **Durable Specs vs. Disposable Code:** Implementation code is ephemeral and disposable. The Gherkin BDD specifications (.gherkin/), declarative schemas (specs/), and system constitutions (AGENTS.md) serve as the durable production ground truth.
2. **Zero Raw Code Generation:** Downstream execution agents produce Meta-Prompts, declarative YAML/JSON configurations, Gherkin specs, and structural verifiers—never unharnessed imperative application code .
3. **No Frozen Model Versions:** All AI tasks route dynamically to model tiers based on complexity rather than fixed model endpoints .


## **3. Dynamic Model Routing Tiers**


| Routing Tier         | Functional Responsibilities                                                                                                     | Target Models / Class                         |
|:---------------------|:--------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------|
| **Premium Frontier** | Deep multi-step reasoning, architectural synthesis, ADRs, threat modeling, autonomous research loops, and root governance.      | Grok 4.5, Gemini 3.6 Pro, Claude Opus class   |
| **Strong Coding**    | BDD Gherkin translation, declarative config scaffolding, ESLint/ruff rule authoring, evaluation harnesses, and dry-run testing. | GLM 5.2, DeepSeek V4 Pro, Claude Sonnet class |
| **Fast Flash**       | High-throughput schema validation, syntax sanity checks, mechanical git commits, Doctor probes, and discovery queries.          | DeepSeek V4 Flash, Gemini Flash Light models  |


## **4. The Three-Harness Factory Model Architecture**

Every agentic loop operates under three mandatory harnesses designed to make autonomous Read → Write → Test → Observe → Fix execution correct-by-construction :

```
                 ┌──────────────────────────────────────┐                  
                 │          CONTEXT HARNESS             │                  
                 │  (6 Context Types \+ Skill Disclose) │                  
                 └──────────────────┬───────────────────┘                  
                                    │                  
                                    ▼            
┌─────────────────────────────────────────────────────────────────────────────┐              
│                           AGENT EXECUTION LOOP                              │              
│                      Read ──► Write ──► Test ──► Observe                    │              
└──────────────────────┬───────────────────────────────┬──────────────────────┘              
                       │                               │              
                       ▼                               ▼              
┌──────────────────────────────────────┐   ┌──────────────────────────────────┐              
│          CONSTRAINT HARNESS          │   │        EVALUATION HARNESS        │              
│ (Deterministic Linters/OWASP Gates)  │   │ (OTEL Triad + 5%/15% Judge Gates)│              
└──────────────────────────────────────┘   └──────────────────────────────────┘
```

### **1. Context Harness**

Manages total token allocation across six distinct context types:

- **Instructions:** Global constitution (AGENTS.md).
- **Knowledge:** Static reference anchors (WP-F1..F5, WP-S1..S5) .
- **Memory:** Short-term event sessions and long-term vector/honcho memory .
- **Examples:** Few-shot Gherkin templates and schema benchmarks.
- **Tools:** MCP server tool registries and A2A Agent Cards.
- **Guardrails:** Authorization envelopes, ACLs, and tenant isolation policies.

### **2. Constraint Harness**

Enforces non-LLM, deterministic rules that cannot be bypassed by prompt injection or model hallucination:

- **Linters & Custom Rules:** Strict ESLint and Ruff AST enforcement.
- **Network & File Boundaries:** OWASP LLM06 non-LLM policy server in the live execution path.
- **Credential Isolation:** Strict secret scanning and non-delegatable payment/AP2 spending gates.

### **3. Evaluation Harness**

Continuous, closed-loop telemetry and output scoring:

- **LLM-as-a-Judge:** Dual-gate scoring (5% sampling for routine tasks, 15% sampling for high-risk operations).
- **Observability Triad:** OpenTelemetry (OTEL) trace, metric, and log aggregation.
- **Trust Score Decay:** Automatic system rollback triggered if agent trust score decays by >15%.

## **5. Dual-Harness Runtime & Supervisor-Worker Topology**

Operational execution utilizes a decoupled dual-harness topology to separate high-level orchestration from execution loops :

```
┌─────────────────────────────────────────────────────────────────────────────┐      
│                        SUPERVISOR / VERIFIER PLANE                          │      
│                       Hermes CLI Engine (WSL2 Core)                         │      
│        - Reads AGENTS.md & HARNESS_SPEC.md                                  │      
│        - Enforces 3-Harness Guardrails & Non-LLM Security Gates             │      
│        - Performs Final Ad-Hoc & CI/CD Verification                         │      
└──────────────────────────────────┬──────────────────────────────────────────┘      
	  			   │      
		     Delegates Task via Meta-Prompt      
				   │      
				   ▼      
┌─────────────────────────────────────────────────────────────────────────────┐      
│                         FAST-EXECUTION WORKER PLANE                         │      
│                       Antigravity 2.0 (AGY IDE / CLI)                       │      
│        - Model: Gemini 3.6 Flash (high)                                     │      
│        - Fast Scaffolding, File Authoring, & Local Dry-Runs                 │      
│        - Fallback: Direct Hermes Execution if OAuth/UI is Unavailable       │      
└─────────────────────────────────────────────────────────────────────────────┘
```

- **Hermes CLI Engine (Supervisor):** Runs natively in WSL2 under .venv-hermes. Instantiates the Context, Constraint, and Evaluation harnesses from HARNESS_SPEC.md and performs final audit verifications.
- **Antigravity CLI / AGY 2.0 (Worker):** Executes high-speed file authoring and local generation tasks under the direction of Hermes Meta-Prompts.
- **Fallback Resilience:** If AGY CLI is unauthenticated or encounters browser OAuth blocks, Hermes automatically falls back to direct implementation without halting the workflow.

## **6. Progressive Skill Disclosure (agentskills.io Standard)**

To prevent context window rot and token-maxing, procedural capabilities follow a 3-tier progressive disclosure model :

1. **Level 1 (L1 Metadata - ~50 Tokens):** Always loaded into the agent's active context window (name, description, trigger_intents).
2. **Level 2 (L2 SKILL.md Body):** Loaded only when the user intent or tool trigger matches L1 metadata.
3. **Level 3 (L3 References & Scripts):** Assets, reference files, and executable Python scripts loaded strictly on demand during execution.


### **Symlink Architecture**

Framework skills reside in /home/carlospg/workspace/agentic-rd/skills/ and are symlinked directly to the global user path ~/.hermes/skills/ . This enables Hermes to auto-discover all framework capabilities across any active workspace directory.

## **7. Ten-Domain (G1–G10) Architectural Summary**

G1: Foundations ──► G2: Tool/MCP Broker ──► G3: Context/Memory ──► G4: Multi-Agent  
│  
G8: Multi-Tenant ◄── G7: Self-Improve ◄── G6: Vibe/AGY IDE ◄── G5: Eval/OTEL  
│  
▼  
G9: Research Loops ──► G10: Production AgentOps

- **G1 (Foundations & Architecture):** Establishes the 3-Harness Factory Model, HARNESS_SPEC.md, root AGENTS.md, and workflow_graph.yaml .
- **G2 (Tool Use & MCP Protocol):** Configures TOOL_REGISTRY.md, MCP client-server JSON-RPC broker, and confused-deputy / slopsquatting defenses .
- **G3 (Memory & Context Engineering):** Establishes SESSION_STATE_SPEC.md, token budget waterfalls, and progressive disclosure skill libraries .
- **G4 (Multi-Agent Orchestration):** Defines hierarchical swarms, A2A Agent Cards, Gherkin task decomposition, and AP2 ledger micro-payment bounds .
- **G5 (Evaluation & Observability):** Implements OpenTelemetry trace/metric/log integration, LLM-as-a-Judge rubrics, and dynamic circuit breakers.
- **G6 (Vibe Coding & Agentic IDEs):** Integrates Antigravity 2.0 IDE surfaces, slash-command hooks (/goal, /grill-me), and "No YOLO" spec-first rules .
- **G7 (Self-Improving Agents):** Defines controlled skill generation, PIVOT_REFINE_TREE.md, and strict non-binary trust safety bounds.
- **G8 (Secure Multi-Tenant Runtimes):** Implements SPIFFE/SPIRE identity envelopes, sandboxed runtimes (GKE/gVisor), and OWASP LLM06 non-LLM policy gates.
- **G9 (Autonomous Research Loops):** Multi-agent research fleets, hypothesis specification via Gherkin, auto-citation verification, and zero hallucination policies .
- **G10 (Production AgentOps):** Spec-driven CI/CD pipelines, canary release schedules (1% → 5% → 25% → 100%), Doctor health probes, and automatic rollbacks.

## **8. Consumer Project Provisioning Engine (The Scaffolder)**

To prevent consumer application work (e.g., Insurance Broker, Realtor, Financial Agent) from modifying or polluting the core framework baseline, the system enforces complete workspace decoupling .

```
/home/carlospg/workspace/  
├── agentic-rd/                          # Core Framework (PRISTINE & LOCKED)  
│   └── scripts/  
│       └── scaffold_consumer_project.py  
└── projects/                            # Application Workspaces  
├── insurance-broker-agent/              # Isolated Consumer Project 1  
└── realtor-agent/                       # Isolated Consumer Project 2
```

### **Zero-Touch Provisioning Command**

A single prompt or command invokes the framework scaffolder to provision a new, fully-vetted application workspace:

Bash  
python3 scripts/scaffold_consumer_project.py \\  
--name "insurance-broker-agent" \\  
--domain-objective "AI Insurance Broker for policy underwriting and risk evaluation"

### **Automated Provisioning Lifecycle**

When triggered, scaffold_consumer_project.py automatically :

1. Creates ~/workspace/projects/insurance-broker-agent/.
2. Generates subdirectories: specs/, skills/, tests/, logs/.
3. Inits a fresh Git repository and creates standard .gitignore rules.
4. Authors a tailored, project-level AGENTS.md containing an explicit inheritance clause pointing back to the core framework constitution:  
Markdown


## Architectural Inheritance

This project explicitly inherits all Context, Constraint, and Evaluation  
harness rules defined in: \`/home/carlospg/workspace/agentic-rd/HARNESS_SPEC.md\`5. Symlinks all global framework skills from ~/.hermes/skills/.6. Executes verify_consumer_workspace.py to confirm workspace isolation and health before handing control back to the operator .

## **9. Verification Suites & Doctor Health Probes**

### **Verification Commands**

The framework includes deterministic Python verifiers for every domain and operational tool. These scripts must be executed using the primary WSL virtualenv :

Bash

# Run individual domain verifiers

python3 scripts/verify_g1_harness.py  
python3 scripts/verify_g2_tools.py  
...  
python3 scripts/verify_g10_production.py

# Run dry-run and chaos tests

python3 scripts/dry_run_g7.py  
python3 scripts/dry_run_g10.py

### **Doctor Diagnostic Health Checks**

Production deployments automatically run periodic environment diagnostics (doctor_checks.yaml) to verify:

- SPIFFE SVID identity validity.
- Non-delegatable policy server response ping (<10ms).
- Active .venv-hermes interpreter binding.
- Zero unauthenticated MCP tool definitions.
- Git tag and release evidence pack integrity.

## **10. Summary Operating Rules for Custom Gem Guidance**

1. **Grounding Rule:** Never generate imperative implementation code directly. Always output declarative specifications, YAML configs, Gherkin BDD scenarios, or Meta-Prompts .
2. **Path Rule:** Maintain all active execution inside WSL2 (/home/carlospg/workspace/agentic-rd/) using Python interpreter .venv-hermes.
3. **Isolation Rule:** Never create consumer agents directly inside the agentic-rd framework directory. Always invoke scaffold_consumer_project.py to provision a clean target directory under ~/workspace/projects/ .
4. **Harness Rule:** Ensure every generated agent design incorporates all three harnesses (Context, Constraint, Evaluation) and complies with OWASP LLM06 non-LLM policy interception .


 
