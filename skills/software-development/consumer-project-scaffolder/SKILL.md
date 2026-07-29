---
name: consumer-project-scaffolder
description: Scaffold new consumer projects that inherit the Agentic R&D three-harness constitution. Use when creating a new project that needs the full framework inheritance chain.
version: 1.0.0
platforms: [linux]
category: software-development
metadata:
  hermes:
    tags: [scaffolding, project-init, agentic-rd, framework]
    related_skills: [wsl2-execution-routing, agentic-rd-g-domain-runbook]
---

# Consumer Project Scaffolder

Provisions a new consumer project directory that inherits the full Agentic R&D
Workspace three-harness constitution (`HARNESS_SPEC.md`). A single command
produces a git-initialized project ready for agentic development.

## L1 — Trigger Conditions

Load this skill when:
- The user asks to "create a new project", "scaffold a consumer project",
  "start a new agentic project", or "provision a workspace"
- A new project needs the agentic-rd constitution inheritance chain
- The user mentions `--name` and `--domain-objective` in a scaffolding context

## L2 — Instructions

### 1. Run the Scaffolder

```bash
python3 scripts/scaffold_consumer_project.py \
    --name "my-project-name" \
    --domain-objective "One-line summary of the project's purpose"
```

Optional arguments:
- `--base-dir /custom/path` — override default (`/home/carlospg/workspace/projects`)
- `--dry-run` — scaffold, verify, then clean up (test mode)

### 2. What Gets Created

```
<base-dir>/<name>/
├── AGENTS.md              ← Project constitution (inherits HARNESS_SPEC.md)
├── .gitignore
├── specs/                 ← Domain blueprints, architecture decisions
├── skills/                ← Project-specific progressive-disclosure procedures
├── tests/                 ← Evaluation harness tests (Gherkin, pytest)
└── logs/                  ← Agent trajectory logs, eval runs
```

### 3. Inheritance Chain

The generated `AGENTS.md` includes:
- Project title & domain objective
- Explicit inheritance clause linking `/home/carlospg/workspace/agentic-rd/HARNESS_SPEC.md`
- Three-Harness Policies (Context, Constraint, Evaluation)
- Dynamic Model Routing matrix (Frontier, Strong Coding, Fast Flash)
- Workspace map and Definition of Done

### 4. Post-Scaffold Actions

The script automatically:
- Initializes a git repository with an initial commit
- Ensures the agentic-rd framework is installed in editable mode
- Symlinks framework skills from `skills/software-development/` into `~/.hermes/skills/`

### 5. Verification

After scaffolding, verify:

```bash
# Check project exists
ls -la /home/carlospg/workspace/projects/<name>/

# Verify AGENTS.md has inheritance clause
grep "HARNESS_SPEC.md" /home/carlospg/workspace/projects/<name>/AGENTS.md

# Check git state
cd /home/carlospg/workspace/projects/<name> && git log --oneline

# Verify skills linked
ls -la ~/.hermes/skills/
```

## L3 — References

- **Parent Constitution:** `AGENTS.md` (workspace root)
- **Deep Spec:** `HARNESS_SPEC.md`
- **Workflow Graph:** `specs/workflow_graph.yaml`
- **Provisioner Script:** `scripts/scaffold_consumer_project.py`
- **Execution Routing:** `skills/software-development/wsl2-execution-routing/SKILL.md`

## Pitfalls

- The project name must be unique under `--base-dir`; the script will refuse to overwrite an existing directory.
- If the framework `pip install -e .` fails, check that `pyproject.toml` or `setup.py` exists at the framework root.
- Skills symlinks are created only for missing links; existing links are preserved.
- The `--dry-run` flag cleans up after itself — use it to test before creating a real project.

## Example

```bash
# Test the scaffolder
python3 scripts/scaffold_consumer_project.py \
    --name "test-drive" \
    --domain-objective "Dry-run validation" \
    --dry-run

# Create a real project
python3 scripts/scaffold_consumer_project.py \
    --name "insurance-broker-agent" \
    --domain-objective "Build an AI insurance brokerage assistant with multi-agent orchestration"
```