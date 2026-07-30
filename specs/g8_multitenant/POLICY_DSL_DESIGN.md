# G8 — Policy DSL Design & Risk-Tier Mapping (Step C)
# Model Tier: Strong Coding
# Status: DRAFT_PRE_GATE
# Overlay: OPTION_2_STANDARD
# Upstream: self-improvement-v1.0.0 (G7 LOCKED)
# BLUE resume: G8_MULTITENANT_APPROVED_v1

---

## 1. Risk-Tier Mapping

### 1.1 Tier Definition

| Tier | Name | Isolation | Tenant Examples | Trust Assumption | Default Policy |
|---|---|---|---|---|---|
| **T1** | Logical | WSL2 namespace + filesystem sandbox | Dev/test tenants, internal tools, personal assistants | Medium — tenant may mistake but not malicious | Guarded: path allowlist, no network egress, no admin |
| **T2** | Process | Docker container | Enterprise tenants, shared dev teams, staging | Lower — tenant mistakes could affect others | Secured: command allowlist, restricted network, no host-mount |
| **T3** | Sandbox | gVisor/Firecracker (declared) | Regulated tenants, PII processing, financial | Lowest — tenant is untrusted | Hardened: no network (except allowlist), read-only root, no IPC |
| **T4** | Hardware | Dedicated VM/physical (FORBIDDEN) | Government, classified | Zero — tenant is adversarial | Air-gapped: no network, no shared storage, physical isolation |

### 1.2 Tier-to-Control Mapping

| Control Area | T1 (Logical) | T2 (Process) | T3 (Sandbox) |
|---|---|---|---|
| **Filesystem** | Allowlist paths; deny ../ escapes | Container volume; read-only for others | tmpfs (ephemeral); no host mount |
| **Network egress** | Deny all (loopback only) | Allowlist URLs | Deny all (disabled) |
| **Network ingress** | Deny all | Deny all | Deny all |
| **Process creation** | Allowlisted binaries | Container-scoped only | No process creation (sandboxed) |
| **Environment variables** | Redact secrets | Container env file | No env vars (sealed) |
| **Memory access** | Process-scoped | Container memory limit | VM memory limit |
| **Device access** | None | None | None |
| **Syscalls** | Allowed (host kernel) | Restricted (Docker SecComp) | Virtualized (gVisor kernel) |
| **Timing** | Standard | Standard | Jittered (anti-timing) |
| **Persistence** | Profile directory (git-tracked) | Container volumes (ephemeral) | None (ephemeral) |

---

## 2. Policy DSL Design

### 2.1 DSL Grammar (YAML)

```yaml
# Policy DSL v1.0.0 — tenant policy document
policy:
  version: "1.0.0"
  tenant_id: "string"
  tier: T1|T2|T3
  
  # --- Sandbox configuration ---
  sandbox:
    type: "wsl2_namespace|docker|gvisor|firecracker"
    ephemeral: true|false
    max_duration: "3600s"
    memory_limit: "2g"
    cpu_limit: "1.0"
    
  # --- Filesystem rules ---
  filesystem:
    mode: read_write|read_only|none
    allow_paths: ["glob/**"]
    deny_paths: ["glob/**"]
    secret_dirs: ["glob/**"]         # read denied, write triggers PEN-03
    workspace_mode: "vibe_coding|structured_assisted|agentic_engineering"
    
  # --- Tool policies ---
  tool_policies:
    - tool: terminal
      allowed: true|false
      actions: [read|write|execute]
      deny_commands: [regex]
      allow_commands: [regex]
      deny_patterns: [regex]
      max_decision_ms: 500
      
    - tool: write_file
      allowed: true|false
      allow_paths: [glob]
      deny_paths: [glob]
      max_file_size: "1mb"
      require_checkpoint: true|false
      max_decision_ms: 200
      
    - tool: read_file
      allowed: true|false
      allow_paths: [glob]
      deny_paths: [glob]
      max_file_size: "10mb"
      max_decision_ms: 100
      
    - tool: patch
      allowed: true|false
      allow_targets: [glob]
      deny_targets: [glob]
      require_checkpoint: true|false
      max_decision_ms: 200
      
    - tool: terminal
      allowed: true|false
      actions: [read|write|execute]
      deny_commands: [regex]
      max_output: "1mb"
      timeout: "300s"
      max_decision_ms: 500
      
    - tool: delegate_task
      allowed: true|false
      max_children: 3
      max_spawn_depth: 1
      max_decision_ms: 100
      
    - tool: web_search
      allowed: true|false
      deny_domains: [regex]
      allow_domains: [regex]
      max_decision_ms: 200
      
  # --- Policy server rules ---
  policy_server:
    mode: "enforce|log_only|disabled"
    override_allowed: false    # LLM cannot override
    audit_level: "info|debug|trace"
    dynamic_resolver: true|false
    
  # --- PII rules ---
  pii:
    redaction: "auto|manual|off"
    fields: ["email|phone|ssn|credit_card|ip_address"]
    breach_notification: "immediate|batch|off"
    audit_redaction: true|false
    
  # --- Evaluation gates ---
  evaluation:
    trust_score_enabled: true|false
    circuit_breaker_enabled: true|false
    checkpoint_required: true|false
    trajectory_emission: "optional|recommended|mandatory"
    llm_as_judge: "disabled|optional|enforced"
    
  # --- Improvement loop ---
  improvement:
    loop_budget: 10
    auto_integrate_s3: true|false
    t3_generation: "dune_only|production|disabled"
    hitl_required_s2: true|false
    
  # --- Telemetry ---
  telemetry:
    log_level: "info|debug|trace"
    retention_days: 90
    include_trajectory: true|false
    breach_alert: true|false
```

### 2.2 DSL Evaluation Semantics

| Rule | Semantics |
|---|---|
| `deny_*` wins over `allow_*` | Explicit deny always overrides explicit allow. If a tool call matches both, it is denied. |
| Default deny | If no rule matches a tool call, it is denied. |
| `allowed: false` | Tool is completely disabled for this tenant. |
| `max_*` limits | Exceeding a limit (size, duration, children) triggers automatic deny with PEN-04 penalty. |
| `require_checkpoint` | Before a mutating write, the agent must create a G5 checkpoint. If no checkpoint exists, the write is denied. |
| `workspace_mode` | Tenant workspace mode determines which tier of evaluation/enforcement applies. |
| Policy inheritance | T1 policies inherit from a default template; T2 and T3 must have explicit policies. |

---

## 3. Risk-Tier × Tool Matrix

| Tool | T1 (Logical) | T2 (Process) | T3 (Sandbox) |
|---|---|---|---|
| `terminal` | Allowlisted commands only | Allowlisted commands + timeout | **Denied** |
| `write_file` | Allowlisted paths + max 1MB | Allowlisted paths + checkpoint required | **Denied** (ephemeral filesystem) |
| `read_file` | Allowlisted paths + max 10MB | Allowlisted paths | Read-only tmpfs |
| `patch` | Allowlisted targets + checkpoint | Allowlisted targets + checkpoint | **Denied** |
| `web_search` | **Denied** (T1 default) | Allowlisted domains | **Denied** |
| `delegate_task` | Max 3 children, depth 1 | Max 3 children, depth 1 | **Denied** (T3 sandbox) |
| `vision_analyze` | Allowed | Allowed | **Denied** |
| `text_to_speech` | Allowed | Allowed | **Denied** |
| `memory` | Tenant-scoped | Tenant-scoped | **Denied** |
| `skill_manage` | **Denied** (T1 default) | HITL-only | **Denied** |
| `cronjob` | **Denied** (T1 default) | HITL-only | **Denied** |

*Note: **Denied** at a tier means the tool call is blocked by the policy intercept before reaching the agent. Agents running at T3 effectively have a read-only, no-network, no-exec capability surface.*

---

## 4. Default Policies by Tier

### 4.1 T1 (Logical) — Default Policy

```yaml
# T1-Logical-01: Standard development tenant
sandbox:
  type: wsl2_namespace
  ephemeral: false
  max_duration: "28800s"  # 8 hours
filesystem:
  mode: read_write
  allow_paths: ["/home/carlospg/workspace/**"]
  deny_paths: ["**/secrets/**", "**/.env", "**/.git/credentials"]
  secret_dirs: ["**/secrets/**", "**/.env"]
tool_policies:
  - tool: terminal
    allowed: true
    deny_commands: ["rm -rf /", "sudo", "chmod 777", "mkfs", "dd if=/dev/"]
    deny_patterns: ["curl.*http://.*token", "wget.*http://.*secret", "grep.*password.*/etc/"]
  - tool: write_file
    allow_paths: ["**/workspace/**"]
    deny_paths: ["**/.git/**", "**/secrets/**", "**/node_modules/**"]
policy_server:
  mode: enforce
```

### 4.2 T2 (Process) — Default Policy

```yaml
# T2-Process-01: Regulated enterprise tenant
sandbox:
  type: docker
  ephemeral: true
  max_duration: "7200s"
  memory_limit: "2g"
  cpu_limit: "1.0"
filesystem:
  mode: read_write
  allow_paths: ["/workspace/**"]
  deny_paths: ["/etc/**", "/proc/**", "/sys/**", "**/.keys/**"]
tool_policies:
  - tool: terminal
    allowed: true
    deny_commands: ["sudo", "su", "chown", "chmod 4777", "mount", "umount", "insmod"]
  - tool: write_file
    require_checkpoint: true
    max_file_size: "512kb"
policy_server:
  mode: enforce
  audit_level: debug
```

### 4.3 T3 (Sandbox) — Default Policy

```yaml
# T3-Sandbox-01: Regulated high-sensitivity tenant
sandbox:
  type: gvisor  # declared, not wired
  ephemeral: true
  max_duration: "3600s"
filesystem:
  mode: read_only  # tmpfs; writes go to transient overlay
  allow_paths: ["/tmp/**"]
tool_policies:
  - tool: terminal
    allowed: false  # no shell execution
  - tool: read_file
    allowed: true
    max_file_size: "512kb"
  - tool: write_file
    allowed: false  # ephemeral filesystem
policy_server:
  mode: enforce
  audit_level: trace
```

---

## 5. Policy Server DSL Validation Rules

All tenant policy documents must pass these validation rules:

| Rule | Check | Failure Action |
|---|---|---|
| `version` must be "1.0.0" | String exact match | Reject policy |
| `tenant_id` must be non-empty | String length > 0 | Reject policy |
| `tier` must be T1, T2, or T3 | Enum validation | Reject policy (T4 forbidden) |
| `sandbox.type` must match tier | T1→wsl2_namespace, T2→docker, T3→gvisor/firecracker | Reject policy |
| `tool_policies` must cover all tools | Every tool has an entry (explicit or inherited) | Reject policy |
| `policy_server.mode` must be "enforce" for T2/T3 | T1 may use "log_only", T2/T3 must enforce | Coerce T2/T3 to enforce |
| `deny_*` must not conflict with `allow_*` | No path appears in both deny and allow | Reject policy |
| `max_*` values must be positive integers | Type + value check | Reject policy |
| `pii.redaction` must be "auto" for T2/T3 | T1 may use "manual" | Coerce T2/T3 to auto |
| No unknown fields | Schema validation | Reject policy |

---

*POLICY_DSL_DESIGN.md v1.0.0-draft — G8 Step C · 2026-07-24*