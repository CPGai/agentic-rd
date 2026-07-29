---
name: hermes-mcp-server-setup
description: >
  Add, configure, test, or remove MCP servers on a Hermes profile. Use when
  wiring stdio/HTTP MCP, pins, or `/reload-mcp`. Do NOT use for general app
  API client code unrelated to Hermes MCP.
priority: 70
---

# Hermes MCP Server Setup (workspace seed)

## Rules
1. Prefer T1 skills / T2 vetted MCP (no T4 in prod)
2. Pin npm MCP packages (no floating `npx` without version)
3. Redact secrets from config dumps
4. Align pins across matrix, broker, skills_registry, pins JSON (G2)

## Verify
```bash
# Profile-local: hermes tools / hermes mcp list (when CLI available)
true  # structural seed — runtime CLI paths live in profile skill body
```
