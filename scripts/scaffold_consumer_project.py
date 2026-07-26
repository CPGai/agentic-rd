#!/usr/bin/env python3
"""
Consumer Project Scaffolder — Provisioner Script
=================================================
Provision a new consumer project that inherits the Agentic R&D Workspace
three-harness constitution (HARNESS_SPEC.md) and is immediately ready for
single-prompt agentic development.

Usage:
    python3 scripts/scaffold_consumer_project.py \\
        --name "insurance-broker-agent" \\
        --domain-objective "Build an AI insurance brokerage assistant"

    python3 scripts/scaffold_consumer_project.py \\
        --name "my-project" \\
        --domain-objective "Experimental vibe-coding sandbox" \\
        --base-dir /home/carlospg/workspace/projects

Author: AGY CLI (Gemini 3.6 Flash) → Hermes Supervisor audit
Version: 1.0.0
"""

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FRAMEWORK_ROOT = Path("/home/carlospg/workspace/agentic-rd")
HARNESS_SPEC = FRAMEWORK_ROOT / "HARNESS_SPEC.md"
HERMES_SKILLS_HOME = Path.home() / ".hermes" / "skills"
DEFAULT_BASE_DIR = Path("/home/carlospg/workspace/projects")

SUB_DIRS = [
    "specs",
    "skills",
    "tests",
    "logs",
]

# AGENTS.md template with inheritance clause
AGENTS_MD_TEMPLATE = """\
# {project_title}
## Consumer Project — Agentic R&D Workspace

**Scaffolded:** {scaffold_date}
**Domain Objective:** {domain_objective}
**Parent Framework:** agentic-rd v1.0.0 (G1–G10 gates approved)
**Harness Runtime:** Hermes CLI + Antigravity unified harness

---

## 1. Constitutional Inheritance

> This project inherits the full Agentic R&D Workspace constitution from:
> **`{harness_spec_path}`**
>
> All G1–G10 domain gates, three-harness policies, model-routing matrices,
> and Definition of Done criteria apply here unless explicitly overridden
> by a project-local HITL gate.

### 1.1 Inheritance Scope

| Artifact | Inherited From | Binding? |
|---|---|---|
| Three-Harness Factory Model | `HARNESS_SPEC.md` §1–4 | Yes |
| Model-Routing Matrix | `AGENTS.md` §4 | Yes |
| Think–Act–Observe Loop | `HARNESS_SPEC.md` §1.2 | Yes |
| Sandbox & Isolation Rules | `AGENTS.md` §2, §9 | Yes |
| WSL2 Execution Routing | `skills/software-development/wsl2-execution-routing/` | Yes |
| Definition of Done | `AGENTS.md` §8 | Yes |

### 1.2 Project-Local Overrides

> Add project-specific constraints, tool allowlists, or evaluation schemas
> below. Anything not explicitly overridden defaults to the parent framework.

*(No overrides yet — add as the project matures.)*

---

## 2. Three-Harness Policies

### 2.1 Context Harness

```
Agent = Model + Harness
Harness = Context ∪ Constraint ∪ Evaluation
Loop   = Read → Write → Test → Observe → Fix
```

| Harness | You must | You must not |
|---|---|---|
| **Context** | Load AGENTS.md + matched skills; progressive-disclose tools/knowledge; cite sources | Dump whole repos into context; skip skill L1 scan; ignore token envelope |
| **Constraint** | Obey `C-*` catalog; prefer hooks/linters over prompt hopes; least-privilege tools | Relax blockers locally; install unknown packages; write secrets; cross-profile writes |
| **Evaluation** | Run available tests/schemata after writes; surface trajectory fields; escalate on flat fix curves | Claim "done" without telemetry; infinite fix loops; skip HITL hard stops |

### 2.2 Six Context Types

| # | Type | Placement | Notes |
|---|---|---|---|
| 1 | Instructions | Static (always-on) | This AGENTS.md + parent constitution |
| 2 | Knowledge | Dynamic (RAG/path-scoped) | `specs/`, `docs/`, whitepaper extracts |
| 3 | Memory | Hybrid (session + profile) | Honcho memory provider (if configured) |
| 4 | Examples | Dynamic (task-matched) | Few-shot samples under `examples/` |
| 5 | Tools | Dynamic (progressive) | MCP registry, skill-wrapped tools |
| 6 | Guardrails | Static core + dynamic specialized | Constraint catalog from parent |

---

## 3. Dynamic Model Routing

| Tier | Use for | Examples | Avoid for |
|---|---|---|---|
| **Premium Frontier** | Deep multi-step reasoning, architecture, threat models, ADRs, research synthesis | HARNESS crosswalks, security design, synthesis | Typos, bulk format, trivial renames |
| **Strong Coding** | Scaffolding, declarative configs, schemas, refactors | YAML graphs, Gherkin, structural tests | Pure classification at scale |
| **Fast Flash** | High-throughput validation, syntax checks, mechanical commits | Lint fix, file moves, status probes | Novel architecture, ambiguous product intent |

**Routing heuristics:**
- Ambiguity / safety / multi-system design → Premium
- Spec-to-artifact under clear constraints → Strong
- Verify / compress / choreograph known steps → Flash
- Prefer Flash inside Evaluation remediation for *deterministic* failures; escalate model tier when root cause is semantic

---

## 4. Workspace Map

```
AGENTS.md                 ← you are here (project constitution)
specs/                    ← domain blueprints, architecture decisions
skills/                   ← project-specific progressive-disclosure procedures
tests/                    ← evaluation harness tests (Gherkin, pytest)
logs/                     ← agent trajectory logs, eval runs
```

---

## 5. Definition of Done

1. Syntactically correct artifacts isolated to the target environment
2. Copy-pasteable verification path supplied
3. Active telemetry confirmation returned
4. No secret leakage; Constraint catalog respected
5. If a domain gate applies — **stopped** with Decision-Support Payload

---

*{project_title} AGENTS.md — inherits agentic-rd v1.0.0 constitution*
"""

GITIGNORE_CONTENT = """\
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/

# Virtual environments
.venv*/
venv/

# Secrets
.env
*.pem
*.key
credentials.json

# Logs
logs/*.log

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""


# ---------------------------------------------------------------------------
# Core Logic
# ---------------------------------------------------------------------------


def run(cmd: list[str], cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    result = subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ Command failed (exit {result.returncode}): {' '.join(cmd)}")
        print(f"   stderr: {result.stderr.strip()}")
        sys.exit(1)
    return result


def scaffold_project(name: str, domain_objective: str, base_dir: Path) -> Path:
    """Provision a new consumer project directory with full scaffolding."""
    project_dir = base_dir / name

    # --- Step a: Provision directory ---
    if project_dir.exists():
        print(f"⚠️  Project directory already exists: {project_dir}")
        print("   Remove it first or use a different --name.")
        sys.exit(1)

    project_dir.mkdir(parents=True, exist_ok=False)
    print(f"✅ Created project directory: {project_dir}")

    # --- Step b: Initialize git ---
    run(["git", "init"], cwd=project_dir)
    print(f"✅ Initialized git repository")

    # --- Step c: Scaffold subdirectories ---
    for subdir in SUB_DIRS:
        (project_dir / subdir).mkdir(parents=True, exist_ok=True)
    print(f"✅ Scaffolded subdirectories: {', '.join(SUB_DIRS)}")

    # --- Step d: Generate AGENTS.md ---
    agents_md = AGENTS_MD_TEMPLATE.format(
        project_title=name.replace("-", " ").title(),
        scaffold_date=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        domain_objective=domain_objective,
        harness_spec_path=str(HARNESS_SPEC),
    )
    (project_dir / "AGENTS.md").write_text(agents_md)
    print(f"✅ Generated AGENTS.md with inheritance clause → {HARNESS_SPEC}")

    # --- Write .gitignore ---
    (project_dir / ".gitignore").write_text(GITIGNORE_CONTENT)
    print(f"✅ Wrote .gitignore")

    # --- Initial git commit ---
    run(["git", "add", "-A"], cwd=project_dir)
    run(["git", "commit", "-m", "chore: initial scaffold from agentic-rd framework"], cwd=project_dir)
    print(f"✅ Initial git commit")

    return project_dir


def ensure_framework_installed() -> None:
    """Ensure agentic-rd framework is installed in editable mode."""
    print(f"🔧 Ensuring framework is installed (editable mode)...")
    result = run(["pip", "install", "-e", str(FRAMEWORK_ROOT)], check=False)
    if result.returncode == 0:
        print(f"✅ Framework installed/up-to-date in editable mode")
    else:
        # Check if already installed
        check = run(
            [sys.executable, "-c", "import agentic_rd; print(agentic_rd.__file__)"],
            check=False,
        )
        if check.returncode == 0:
            print(f"✅ Framework already importable: {check.stdout.strip()}")
        else:
            print(f"⚠️  Framework install had issues (non-fatal): {result.stderr.strip()[:200]}")


def link_framework_skills() -> None:
    """Symlink framework skills into ~/.hermes/skills/."""
    framework_skills_dir = FRAMEWORK_ROOT / "skills" / "software-development"
    HERMES_SKILLS_HOME.mkdir(parents=True, exist_ok=True)

    linked = 0
    for skill_dir in framework_skills_dir.iterdir():
        if skill_dir.is_dir():
            target = HERMES_SKILLS_HOME / skill_dir.name
            if target.exists() or target.is_symlink():
                # Already linked — skip
                continue
            os.symlink(str(skill_dir), str(target))
            linked += 1
            print(f"   🔗 Linked: {skill_dir.name} → ~/.hermes/skills/")

    if linked == 0:
        print(f"   ℹ️  All framework skills already linked in ~/.hermes/skills/")
    else:
        print(f"✅ Linked {linked} framework skills into ~/.hermes/skills/")


def cleanup_project(project_dir: Path) -> None:
    """Remove a scaffolded project (used for dry-run teardown)."""
    if project_dir.exists():
        shutil.rmtree(str(project_dir))
        print(f"🧹 Cleaned up: {project_dir}")


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold a new consumer project inheriting the Agentic R&D Workspace constitution.",
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Project name (kebab-case, e.g. 'insurance-broker-agent')",
    )
    parser.add_argument(
        "--domain-objective",
        required=True,
        help="One-line summary of the project's domain objective",
    )
    parser.add_argument(
        "--base-dir",
        default=str(DEFAULT_BASE_DIR),
        help=f"Base directory for projects (default: {DEFAULT_BASE_DIR})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scaffold, verify, then clean up (for testing)",
    )
    args = parser.parse_args()

    base_dir = Path(args.base_dir)

    print(f"\n{'='*60}")
    print(f"  Consumer Project Scaffolder")
    print(f"  Framework: {FRAMEWORK_ROOT}")
    print(f"  Base Dir:  {base_dir}")
    print(f"  Project:   {args.name}")
    print(f"  Objective: {args.domain_objective}")
    print(f"{'='*60}\n")

    # Step 1: Scaffold the project
    project_dir = scaffold_project(args.name, args.domain_objective, base_dir)

    # Step 2: Ensure framework is installed
    ensure_framework_installed()

    # Step 3: Link framework skills
    print(f"\n🔗 Linking framework skills...")
    link_framework_skills()

    # Step 4: Verification summary
    print(f"\n{'='*60}")
    print(f"  ✅ Scaffold Complete")
    print(f"  Project:  {project_dir}")
    print(f"  Git:      {args.name}/ (initial commit)")
    print(f"  Inherits: {HARNESS_SPEC}")
    print(f"{'='*60}")

    # Verify key artifacts exist
    for artifact in ["AGENTS.md", ".gitignore", "specs/", "skills/", "tests/", "logs/"]:
        path = project_dir / artifact
        status = "✅" if path.exists() else "❌"
        print(f"  {status} {artifact}")

    print()

    # Dry-run cleanup
    if args.dry_run:
        print("🧹 Dry-run mode: cleaning up test workspace...")
        cleanup_project(project_dir)
        print("✅ Dry-run complete — project removed.\n")


if __name__ == "__main__":
    main()