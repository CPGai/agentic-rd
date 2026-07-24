---
name: wsl2-execution-routing
description: >
  Route all shell, terminal, and Python execution through WSL2 Ubuntu-24.04
  with project `.venv-hermes`. Use when running commands, installs, or tests
  in agentic-rd. Do NOT use for pure markdown edits that need no shell.
priority: 100
---

# WSL2 Execution Routing (workspace seed)

## When to use
- Any `terminal` / Python / package command in this workspace
- After a host-Windows Python failure

## Rules
1. Always:
   `wsl -d Ubuntu-24.04 bash -c "cd /home/carlospg/workspace/agentic-rd && source .venv-hermes/bin/activate && <cmd>"`
2. Primary interpreter: `/home/carlospg/workspace/agentic-rd/.venv-hermes/bin/python3`
3. Never install packages on Windows host Python/uv for project work
4. For large scripts: Temp→`/tmp` via Hermes `write_file`, then run in WSL

## Verify
```bash
wsl -d Ubuntu-24.04 bash -c 'cd /home/carlospg/workspace/agentic-rd && source .venv-hermes/bin/activate && which python && python -V'
```
