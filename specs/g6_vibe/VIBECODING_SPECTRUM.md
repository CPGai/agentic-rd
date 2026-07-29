# G6 — Vibe Coding Spectrum: From Low-Structure to Spec-Driven Agentic Engineering

**Domain:** G6 — Vibe Coding / Agentic IDEs  
**Status:** DRAFT_PRE_GATE  
**Upstream gate:** G5 APPROVED · `G5_EVAL_FRAMEWORK_APPROVED_v1` · tag `eval-v1.0.0`  
**BLUE resume token (authoritative):** `G6_VIBE_ENV_LOCKED_v1`  
**Recommended path:** `OPTION_2_STANDARD`  
**Primary sources:** WP-S1 (The New SDLC with Vibe Coding) · WP-S5 (Spec-Driven Production Grade Development) · WP-F5 (Prototype to Production) · BLUE §G6 (L348–377)  
**Supersedence:** WP-S* supersedes WP-F* on overlap (Course-2 wins)

---

## 1. The Vibe Coding to Agentic Engineering Continuum

WP-S1 (pp. 12–14) defines a three-stage spectrum along five dimensions. WP-S5 (pp. 5–9) sharpens the boundary: "vibe coding" is not "vibe-in-production." The transition is not about which tools you use but how deliberately the harness is configured (WP-S1 p. 31).

### 1.1 Spectrum Table (WP-S1 Table 1, adapted)

| Dimension | Vibe Coding | Structured AI-Assisted Coding | Agentic Engineering |
|---|---|---|---|
| **Intent specification** | Casual natural-language prompts | Detailed prompts with examples and constraints | Formal specs, architecture docs, memory files |
| **Verification** | "Does it seem to work?" | Manual testing, spot-checking | Automated test suites, CI/CD gates, LM judges |
| **Codebase understanding** | Minimal; developer may not read generated code | Selective review of critical paths | Comprehensive architecture review; AI handles implementation |
| **Error handling** | Copy-paste error messages back to AI | Developer diagnoses root cause, AI implements fix | Agents self-diagnose within defined bounds; humans handle architectural issues |
| **Appropriate scope** | Prototypes, scripts, personal projects, hackathons | Features within established codebases | Production systems, team-scale development |
| **Risk profile** | High; acceptable for disposable code | Moderate; human judgment at key checkpoints | Low; systematic verification at every stage |

### 1.2 Developer Modes: Conductor vs Orchestrator (WP-S1 pp. 30–34)

| Mode | Description | Surfaces | Skills Required | When to Use |
|---|---|---|---|---|
| **Conductor** | Hands-on, real-time pair direction; fine-grained control over every change | IDE inline completions, chat panels (Cursor, Windsurf, Copilot) | Syntax familiarity, debugging, code review | Complex logic, unfamiliar codebases, tricky debugging |
| **Orchestrator** | Async, multi-agent delegation; define goals, assign agents, review results | CLI agents, background agents (Claude Code, Codex, Jules, Antigravity CLI) | Specification, decomposition, evaluation, architecture | Well-defined tasks, bug fixes, feature implementations, migrations, test generation |

**Key insight (WP-S1 p. 31):** The same agent can be used in either mode. The difference is harness configuration, not tool selection. A developer often uses both modes in a single day.

### 1.3 The Verification Differentiator (WP-S1 p. 14, WP-S4)

The single biggest differentiator between vibe coding and agentic engineering is how outputs get verified:

- **Tests** verify deterministic parts: function X given input Y produces output Z
- **Evaluations** verify non-deterministic parts: did the agent take the right trajectory of steps, choose the right tools, and produce a quality response

Without both tests and evaluations, the practice is always vibe coding regardless of prompt sophistication. G5 locks the evaluation harness: trajectory schema (`Mission→Scene→Thought→Action→Observation→Verdict`), 5%/15% degradation thresholds, trust score decay, and circuit breakers.

---

## 2. Antigravity 2.0 Surface Comparison

WP-S1 (pp. 35–37) and WP-S5 (pp. 4–6) identify three primary surface postures for coding agents. This workspace uses a Hermes CLI + Antigravity unified harness (BLUE §4).

### 2.1 Surface Taxonomy

| Surface | Description | Developer Mode | Autonomy | Use Case | Workspace Mapping |
|---|---|---|---|---|---|
| **Desktop IDE** | Inline completions, chat panel, edit-in-place | Conductor | Low–Medium | Writing code with real-time AI assistance; flow-state coding | Hermes desktop app + ACP (VS Code/Zed/JetBrains) |
| **CLI** | Command-line agent; multi-file access, tool execution, test iteration | Conductor↔Orchestrator | Medium–High | Multi-file work, codebase exploration, build-test-fix loops | Hermes CLI / `agy --print` in WSL2 substrate |
| **Serverless Agent Engine** | Background cloud-hosted sandbox; runs for hours, produces PR | Orchestrator | High | Well-specified tasks: bug fixes, test suites, framework migrations | Hermes `delegate_task` + `cronjob` (process-local); Google Agent Engine (cloud, DECLARED_NOT_WIRED) |

### 2.2 Antigravity CLI (`agy`) Capabilities (from skill: antigravity-cli)

The Antigravity CLI provides:

- **Shell wrapper commands:** `agy help`, `agy install`, `agy plugin`, `agy update`, `agy changelog`
- **Non-interactive mode:** `agy --print` / `agy -p` for one-shot scripted prompts
- **Interactive TUI:** Full session with in-session slash commands (`/config`, `/permissions`, `/skills`, `/agents`)
- **Model selection:** `--model` flag (e.g., `'Gemini 3.1 Pro (High)'`, `'Claude Opus 4.6 (Thinking)'`)
- **Plugin system:** `agy plugin list` / `agy plugin install`
- **Worktree isolation:** `agy` can operate in git worktrees for parallel agent isolation

### 2.3 Hermes CLI Surface Capabilities (from skill: hermes-agent)

Hermes provides a broader multi-surface posture:

| Surface | Command | Role |
|---|---|---|
| Interactive chat / TUI | `hermes` (or `display.interface: tui`) | Default real-time pair coding |
| Single query | `hermes chat -q "..."` | Fire-and-forget one-shot |
| Desktop app | `hermes desktop` / `hermes gui` | Electron native GUI with file browser, terminal pane, review pane |
| Web dashboard | `hermes dashboard` | Web admin panel + embedded chat |
| IDE integration | `hermes acp` | ACP server for VS Code / Zed / JetBrains |
| OpenAI proxy | `hermes proxy` | Local OpenAI-compatible proxy |
| Worktree mode | `hermes -w` | Isolated git worktree for parallel agents |

### 2.4 Surface Selection Matrix

| Task Profile | Recommended Surface | Rationale |
|---|---|---|
| Prototype / hackathon / exploration | Desktop IDE (Conductor) | Rapid feedback, flow-state, disposable code |
| Feature implementation in established codebase | CLI (Conductor→Orchestrator) | Multi-file access, tool execution, test iteration |
| Well-specified bug fix / migration / test gen | `delegate_task` / background (Orchestrator) | Async delegation, review results later |
| Architecture / spec drafting | CLI + Premium Frontier model | Deep reasoning, synthesis, spec authoring |
| Verification / lint / mechanical commit | CLI + Fast Flash model | High throughput, deterministic checks |
| Scheduled monitoring / watchdog | `cronjob` (Orchestrator) | Durable, multi-platform delivery |

---

## 3. Spectrum Transition Triggers

WP-S1 (pp. 30–31) and WP-S5 (pp. 5–9) define when a project must move from loose prompts to spec-driven execution. The transition is triggered by increasing stakes, not by tool sophistication.

### 3.1 Transition Trigger Catalog

| Trigger | From | To | Rationale |
|---|---|---|---|
| **Stakes escalation** | Vibe Coding | Structured AI-Assisted | Code affects users, data, or financial systems (WP-S1 p. 13) |
| **Team scale > 1** | Structured AI-Assisted | Agentic Engineering | Multiple developers need shared specs, not implicit context (WP-S5 p. 6) |
| **Codebase longevity > 1 sprint** | Vibe Coding | Structured AI-Assisted | Disposable code assumption breaks; maintenance tax begins (WP-S1 p. 41) |
| **Verification gap detected** | Any | Agentic Engineering | No automated tests/evals = always vibe coding (WP-S1 p. 14) |
| **Production deployment** | Structured AI-Assisted | Agentic Engineering | CI/CD gates, observability, evaluation as quality gate required (WP-F5 pp. 12–13) |
| **Agent-as-product** | Any | Agentic Engineering | Building agents that serve real users needs persistent memory, scoped permissions, eval coverage, observability (WP-S1 p. 37) |
| **Regulatory / compliance requirement** | Any | Agentic Engineering | Traceability, audit trail, human-approvable artifacts (WP-S5 p. 8, WP-F5 p. 9) |
| **Bug-to-code ratio rising** | Vibe Coding | Structured AI-Assisted | AI generates bugs at scale; without specs, review burden drowns reviewers (WP-S5 p. 5) |
| **Context fragmentation** | Any | Spec-Driven (SDD) | Agent loses plot from outdated snapshots; specs/ folder as source of truth (WP-S5 p. 8) |

### 3.2 Transition Guard: The "No YOLO" Boundary

G5 circuit breaker rules apply to all surfaces. The production-vs-prototype boundary is enforced by:

1. **Spec-Driven Development (SDD):** BDD/Gherkin scenarios in `specs/` folder before any production code (WP-S5 pp. 8–9)
2. **Code is disposable:** If a rock-solid spec exists, the entire codebase can be regenerated (WP-S5 p. 7)
3. **Hybrid Markdown + YAML:** Narrative in Markdown, structured config in YAML (nesting depth > 3) for optimal LLM parsing (WP-S5 p. 7)
4. **Evaluation gates:** G5 trajectory schema + 5%/15% thresholds + trust score decay
5. **Checkpoint protocol:** Git checkpoint ref before filesystem mutation (G5 inheritance)
6. **`/yolo` toggle:** Hermes `/yolo` bypasses approvals — this is **vibe coding mode** and must be confined to prototype dunes

### 3.3 Prototype Dune Definition

A prototype dune is a workspace context where vibe coding is explicitly permitted:

- `/yolo` mode active (approval bypass)
- No production secrets in environment
- No production database access
- Disposable branch / worktree (`hermes -w`)
- No CI/CD gate enforcement
- Explicit time-box or scope-box
- Fast Flash or Strong Coding tier (no Premium Frontier waste on prototypes)

---

## 4. Spec-Driven Development (SDD) Pattern (WP-S5)

### 4.1 SDD Workflow

```
1. Write spec (Markdown + YAML in specs/)
   ↓
2. Review spec with humans (catch logic flaws before codegen)
   ↓
3. Agent generates code from spec
   ↓
4. Agent generates tests from BDD scenarios (Gherkin Given/When/Then)
   ↓
5. Run tests + evaluations (G5 trajectory + trust score)
   ↓
6. If fail → fix within bounds → re-verify
   ↓
7. Human review at HITL gate
```

### 4.2 Instruction Placement (WP-S5 pp. 10–11)

| Location | Lifetime | Purpose |
|---|---|---|
| Chat interface | Ephemeral, session-specific | High-level orchestration, instant feedback |
| `specs/` folder | Persistent, version-controlled | Technical design, BDD scenarios, API contracts, YAML schemas |
| Agent Skills (SKILL.md) | Reusable, feature-focused | Trigger-based workflows, progressive disclosure (L1→L2→L3) |
| AGENTS.md / module files | Static, always-on | Core identity, constraints, guardrails, model routing |

### 4.3 Token Economics (WP-S5 pp. 9–10)

- Every character is tokenized; every token consumes budget, time, and context capacity
- Hybrid Markdown + YAML: Markdown for narrative, YAML for nesting depth > 3 (51.9% parsing accuracy vs 43.1% JSON vs 33.8% XML)
- `specs/` folder is a lean, compiled instruction set — not documentation
- Eliminate repetitive Given/When/Then blocks; use shared backgrounds

---

## 5. Step C — Surface Posture and Model-Routing Matrix

### 5.1 Primary Surface Posture: Hermes CLI + Antigravity Hybrid

**Selected surface:** Hermes CLI as primary orchestrator + Antigravity CLI (`agy`) as delegated coding backend.

**Rationale:**
- Hermes provides the multi-surface posture (CLI, desktop, dashboard, ACP, messaging gateway) and the durable systems (delegation, cron, curator, memory)
- Antigravity provides the IDE-class coding agent backend with Gemini/Claude model selection
- Both operate in WSL2 substrate with `.venv-hermes`
- BLUE §4 mandates: "Hermes CLI + Antigravity unified harness"

### 5.2 Model-Routing Matrix (Dynamic — no frozen model pins)

This matrix extends the AGENTS.md §4 routing matrix with G6 surface-specific routing:

| Task Pattern | Model Tier | Surface | Rationale |
|---|---|---|---|
| Architecture / spec synthesis / ADR | Premium Frontier | Hermes CLI | Deep multi-step reasoning, WP crosswalks |
| Scaffolding / declarative configs / YAML / Gherkin | Strong Coding | Hermes CLI / `agy -p` | Spec-to-artifact under clear constraints |
| Code generation / feature implementation | Strong Coding | `agy -p` / `delegate_task` | Multi-file edits, tool execution |
| Test generation from BDD scenarios | Strong Coding | `agy -p` / `delegate_task` | Structured generation from specs |
| Verification / lint / syntax checks | Fast Flash | Hermes CLI | High throughput, deterministic |
| Mechanical commits / file moves / status probes | Fast Flash | Hermes CLI | Trivial transforms |
| Prototype / vibe coding (dune) | Fast Flash / Strong Coding | `agy -p` / Desktop IDE | Rapid feedback, disposable code |
| Debugging / root-cause diagnosis | Premium Frontier | Hermes CLI | Semantic analysis, multi-system reasoning |
| Scheduled watchdogs / monitoring | Fast Flash | `cronjob` | Deterministic, low cost |
| Research synthesis / domain reconnaissance | Premium Frontier | `delegate_task` (batch) | Multi-source synthesis |

### 5.3 Routing Heuristics (from AGENTS.md §4, extended)

- Ambiguity / safety / multi-system design → Premium Frontier
- Spec-to-artifact under clear constraints → Strong Coding
- Verify / compress / choreograph known steps → Fast Flash
- Prefer Fast Flash inside Evaluation remediation for deterministic failures
- Escalate model tier when root cause is semantic
- Never waste Premium Frontier on typos, bulk format, trivial renames
- Prototype dune tasks: allow Fast Flash to keep OpEx low (WP-S1 p. 39: "Hidden Debt of Vibe Coding")

---

## 6. G5 Inheritance: Evaluation Integration for Vibe Paths

The G5 evaluation harness applies to all surfaces, including prototype/vibe paths:

| G5 Mechanism | Vibe Coding Application | Agentic Engineering Application |
|---|---|---|
| Trajectory schema | Optional (vibe sessions may not emit trajectories) | Mandatory (all production paths emit trajectories) |
| Trust score [0.0, 1.0] | Not enforced (prototype dune) | Enforced (circuit breaker active) |
| 5%/15% thresholds | Not enforced | Enforced (graduated response) |
| Circuit breaker | Disabled (dune) | Active (15 FM trip triggers) |
| Checkpoint protocol | Optional (git branch suffices) | Mandatory (git checkpoint ref before mutation) |
| PII scrubbing | Optional | Mandatory (before trajectory storage) |
| LLM-as-a-Judge | Not applicable | Enforced (different model family from agent) |
| AgBOM | Not applicable | Mandatory (drift detection active) |

---

## 7. Residual Risks

| Risk | Severity | Owner |
|---|---|---|
| Surface integration (Hermes↔Antigravity) not smoke-tested | MED | G6 Step E/F (post-gate) |
| `/yolo` mode can be accidentally left on in production context | MED | G6 Step E (guard test) / G8 (policy enforcement) |
| Transition triggers are declarative but not enforced at runtime | MED | G8 (policy server) / G10 (AgentOps) |
| Model routing matrix is declarative; no runtime router | MED | G10 |
| Antigravity CLI (`agy`) not installed in WSL2 substrate | LOW | G6 Step B (procurement note) |
| Serverless Agent Engine (cloud) is DECLARED_NOT_WIRED | LOW | G10 (production deploy) |
| Spec-to-code pipeline not automated (SDD pattern is manual) | LOW | G7 (self-improvement may automate) |
| Token economics guidance not enforced by tooling | LOW | G3 (context budget) / G10 |

---

## 8. Option Matrix (HITL Gate)

**Vibe Strategy Status: LOCKED (`G6_VIBE_ENV_LOCKED_v1`)**
- Async Orchestrator mode with specs first + evaluation gates + hybrid surface.
- Prevents token-maxing and security leaks while preserving rapid feedback.

---

## 9. Crosswalk: Course-1 to Course-2 Supersession

| Course-1 (WP-F*) | Course-2 (WP-S*) | Supersession Note |
|---|---|---|
| WP-F5: Prototype to Production (general AgentOps lifecycle) | WP-S1: The New SDLC with Vibe Coding (vibe→agentic spectrum, Conductor/Orchestrator) | WP-S1 defines the spectrum; WP-F5 defines the productionization journey — complementary, not conflicting |
| WP-F5: CI/CD pipeline, safe rollout | WP-S5: Spec-Driven Production Grade Development (SDD, BDD/Gherkin, token economics) | WP-S5 supersedes on spec format and instruction placement; WP-F5 retains ownership of deployment/rollout |
| — | WP-S4: Vibe Coding Agent Security and Evaluation (7-pillar trust, AgBOM, circuit breakers) | WP-S4 is the security/eval supersession for vibe trajectories — feeds G5 |

---

## 10. Structural Test Intents (deferred to Step E, post-gate)

| ID | Intent | Category |
|---|---|---|
| ST-G6-01 | Spectrum transition triggers fire correctly (stakes → spec-driven) | structural |
| ST-G6-02 | `/yolo` mode confined to prototype dune (no production secrets access) | security |
| ST-G6-03 | SDD workflow: spec exists before codegen on production paths | structural |
| ST-G6-04 | Model routing: task pattern → correct tier (no Premium on trivial) | structural |
| ST-G6-05 | Surface selection matrix: task profile → correct surface | structural |
| ST-G6-06 | G5 trajectory schema emitted on production paths (not vibe dune) | structural |
| ST-G6-07 | Checkpoint protocol active on production paths | structural |
| ST-G6-08 | Token economics: YAML for nesting > 3, Markdown for narrative | structural |

---

*VIBECODING_SPECTRUM.md · G6 DRAFT_PRE_GATE · upstream `eval-v1.0.0` · 2026-07-24*
