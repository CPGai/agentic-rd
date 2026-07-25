# PRODUCTION_DSL_SPEC.md
# G10 — Production Deployment & Release Manifest DSL
# Status: DRAFT_PRE_GATE
# Overlay: OPTION_2_STANDARD
# Upstream: research-loop-v1.0.0 (G9 LOCKED)
# BLUE resume: G10_PRODUCTION_DEPLOY_v1
# Tier: Strong Coding (Step C)

version: 1.0.0-draft
domain: G10
kind: production_dsl_spec
status: DRAFT_PRE_GATE
overlay: OPTION_2_STANDARD
upstream_tag: research-loop-v1.0.0
upstream_lock_commit: "6299812"
blue_resume_token: G10_PRODUCTION_DEPLOY_v1

---

## 1. Purpose

Define a deterministic **EBNF grammar** and validation rules for production deployment and release manifests. Manifests are durable declarative artifacts; generated deploy scripts/images are disposable (WP-S5).

Consumers: `cicd_pipeline.yaml`, `quality_gates.yaml`, `doctor_checks.yaml`, `fleet_management.yaml`, and future `release_*.yaml` instances.

---

## 2. EBNF Grammar

```ebnf
production_manifest   = header body ;
header                = "apiVersion" ":" semver NL
                        "kind" ":" kind_enum NL
                        "metadata" ":" NL metadata_block ;
kind_enum             = "ReleaseManifest"
                      | "CanarySchedule"
                      | "QualityGateSet"
                      | "DoctorSuite"
                      | "FleetTopology"
                      | "RollbackPolicy" ;

metadata_block        = indent "name" ":" dns_label NL
                        indent "release_id" ":" release_id NL
                        indent "overlay" ":" "OPTION_2_STANDARD" NL
                        indent "upstream_tag" ":" tag_name NL
                        indent "resume_token" ":" "G10_PRODUCTION_DEPLOY_v1" NL
                        [indent "tenant_risk_tier" ":" risk_tier NL] ;

body                  = artifact_block
                      | canary_block
                      | gates_block
                      | doctor_block
                      | fleet_block
                      | rollback_block ;

(* ----- Artifacts / genealogy ----- *)
artifact_block        = "artifacts" ":" NL artifact_entry+ ;
artifact_entry        = indent "-" " " "digest" ":" hex_digest NL
                        indent2 "path" ":" path_str NL
                        indent2 "type" ":" artifact_type NL ;
artifact_type         = "gherkin" | "spec_yaml" | "spec_md" | "container" | "sbom" | "evidence_pack" ;

(* ----- Canary ----- *)
canary_block          = "canary" ":" NL
                        indent "schedule" ":" NL stage_entry+
                        indent "observation_window_hours" ":" integer NL
                        indent "auto_rollback" ":" boolean NL ;
stage_entry           = indent2 "-" " " "pct" ":" canary_pct NL
                        indent3 "dwell_minutes" ":" integer NL
                        indent3 "exit_gates" ":" "[" gate_id_list "]" NL ;
canary_pct            = "1" | "5" | "25" | "100" ;

(* ----- Quality gates ----- *)
gates_block           = "quality_gates" ":" NL gate_entry+ ;
gate_entry            = indent "-" " " "id" ":" gate_id NL
                        indent2 "class" ":" gate_class NL
                        indent2 "threshold" ":" threshold_expr NL
                        indent2 "on_fail" ":" fail_action NL ;
gate_class            = "quality" | "safety" | "cost" | "security" | "pii" | "policy" | "research" ;
fail_action           = "auto_flag" | "hitl_stop" | "auto_rollback" | "block_promote" ;

(* ----- Doctor ----- *)
doctor_block          = "doctor" ":" NL probe_entry+ ;
probe_entry           = indent "-" " " "id" ":" probe_id NL
                        indent2 "severity" ":" ("CRITICAL" | "HIGH" | "MED" | "LOW") NL
                        indent2 "fail_closed" ":" boolean NL
                        indent2 "probe_type" ":" probe_type NL ;
probe_type            = "svid_validation"
                      | "network_boundary"
                      | "policy_server_ping"
                      | "memory_bank_health"
                      | "pin_concurrence"
                      | "eval_endpoint"
                      | "fleet_quorum"
                      | "budget_readable" ;

(* ----- Fleet ----- *)
fleet_block           = "fleet" ":" NL
                        indent "topology" ":" "hierarchical_coordinator_specialists" NL
                        indent "max_concurrent_specialists" ":" integer NL
                        indent "model_routing" ":" NL routing_entry+ ;
routing_entry         = indent2 "-" " " "task_class" ":" task_class NL
                        indent3 "tier" ":" model_tier NL ;
task_class            = "architecture" | "codegen" | "verify" | "policy" | "research" | "ops" ;
model_tier            = "Premium_Frontier" | "Strong_Coding" | "Fast_Flash" ;

(* ----- Rollback ----- *)
rollback_block        = "rollback" ":" NL
                        indent "last_known_good" ":" hex_digest NL
                        indent "triggers" ":" NL trigger_entry+ ;
trigger_entry         = indent2 "-" " " "id" ":" rb_id NL
                        indent3 "condition" ":" condition_expr NL
                        indent3 "action" ":" "instant_lkg" NL ;

(* ----- Terminals ----- *)
release_id            = "rel-" hex_digest ;
dns_label             = letter ( letter | digit | "-" )* ;
tag_name              = (letter | digit | "." | "-" | "_")+ ;
hex_digest            = (hex)+ ;
hex                   = digit | "a"|"b"|"c"|"d"|"e"|"f"|"A"|"B"|"C"|"D"|"E"|"F" ;
semver                = digit+ "." digit+ "." digit+ [ "-" (letter | digit | ".")+ ] ;
path_str              = printable+ ;
gate_id               = "QG-" digit digit digit ;
probe_id              = "DOC-" (letter | digit | "-")+ ;
rb_id                 = "RB-" digit digit ;
gate_id_list          = gate_id ( "," gate_id )* ;
risk_tier             = "RT-1" | "RT-2" | "RT-3" | "RT-4" ;
threshold_expr        = comparison number [ "pct" | "abs" | "ms" | "usd" ] ;
condition_expr        = printable+ ;
comparison            = "<=" | ">=" | "<" | ">" | "==" ;
number                = digit+ [ "." digit+ ] ;
boolean               = "true" | "false" ;
integer               = digit+ ;
letter                = "A" | ... | "Z" | "a" | ... | "z" ;
digit                 = "0" | ... | "9" ;
printable             = ? any printable character except NL ? ;
indent                = "  " ;
indent2               = "    " ;
indent3               = "      " ;
NL                    = ? newline ? ;
```

> Note: Final instance documents may be YAML isomorphic to this grammar. YAML parsers are authoritative for structure; EBNF constrains **allowed shapes and enumerations**.

---

## 3. Structural Validation Rules (SV-PA)

| ID | Rule | Severity |
|---|---|---|
| SV-PA-01 | `apiVersion` present and semver-parsable | BLOCK |
| SV-PA-02 | `kind` ∈ kind_enum | BLOCK |
| SV-PA-03 | `metadata.overlay` == `OPTION_2_STANDARD` under recommended path | BLOCK |
| SV-PA-04 | `metadata.resume_token` == `G10_PRODUCTION_DEPLOY_v1` | BLOCK |
| SV-PA-05 | `metadata.upstream_tag` == `research-loop-v1.0.0` for G10 v1 packs | BLOCK |
| SV-PA-06 | `metadata.release_id` matches `rel-` + hex | BLOCK |
| SV-PA-07 | Every artifact entry has `digest`, `path`, `type` | BLOCK |
| SV-PA-08 | Canary `pct` sequence must be exactly subsequence of `[1,5,25,100]` in order, no skips when progressing | BLOCK |
| SV-PA-09 | Canary must not jump (e.g. 1 → 100) | BLOCK |
| SV-PA-10 | `observation_window_hours` ∈ [24, 72] for OPTION_2 production dwell | BLOCK |
| SV-PA-11 | Each gate has `id`, `class`, `threshold`, `on_fail` | BLOCK |
| SV-PA-12 | Doctor CRITICAL probes have `fail_closed: true` | BLOCK |
| SV-PA-13 | Fleet topology must be `hierarchical_coordinator_specialists` under OPTION_2 | BLOCK |
| SV-PA-14 | `max_concurrent_specialists` ≤ 3 (Hermes observed + G8 tenant cap binding) | BLOCK |
| SV-PA-15 | Rollback block includes `last_known_good` digest when kind includes canary/prod | BLOCK |
| SV-PA-16 | No XML/HTML tags in YAML instances | BLOCK |
| SV-PA-17 | Secret scan clean (min token length 20; exclude resume tokens) | BLOCK |
| SV-PA-18 | Model routing uses dynamic tiers only — no frozen model version pins | BLOCK |

---

## 4. Semantic Validation Rules (SEM-PA)

| ID | Rule | Severity |
|---|---|---|
| SEM-PA-01 | Quality auto-flag threshold is **5%** degradation vs baseline | BLOCK |
| SEM-PA-02 | Quality HITL stop threshold is **15%** degradation vs baseline | BLOCK |
| SEM-PA-03 | Trust absolute floors: warning 0.85, hitl_review 0.70, trip 0.50 | BLOCK |
| SEM-PA-04 | Canary trust decay rollback when decay **>15%** from canary baseline | BLOCK |
| SEM-PA-05 | Policy deny surge ≥15% → auto_rollback; ≥5% → auto_flag | BLOCK |
| SEM-PA-06 | LLM06 controls non_delegatable; `on_fail` cannot be ignore | BLOCK |
| SEM-PA-07 | PII/secret signals map to `auto_rollback` or `hitl_stop`, never `auto_flag` alone | BLOCK |
| SEM-PA-08 | Cost ceiling breach maps to circuit trip path | BLOCK |
| SEM-PA-09 | Research product releases require C-RS-05/C-RS-07 gates green | BLOCK |
| SEM-PA-10 | Mandatory G9 HITL gates HG-RS-01/05/07 must be cleared before STG-08 for research artifacts | BLOCK |
| SEM-PA-11 | Dune/prototype refs cannot appear as production `artifacts.path` prefixes (`prototype/`, `dune/`) | BLOCK |
| SEM-PA-12 | L4 AgentCreator remain disabled in fleet_management | BLOCK |
| SEM-PA-13 | Evidence pack artifact type must exist before canary kind promote | BLOCK |
| SEM-PA-14 | Risk tier RT-4 requires ISO-3 runtime class in fleet binding | BLOCK |

---

## 5. Canary Schedule Parameters (normative OPTION_2)

| Stage | Traffic pct | Default dwell | Exit gates (min) |
|---|---:|---|---|
| C1 | 1% | 60 min | QG quality 5%, Doctor CRITICAL, policy surge |
| C2 | 5% | 120 min | + trust decay ≤15%, latency SLO |
| C3 | 25% | 240 min | + cost burn, fleet smoke |
| C4 | 100% | 24–72 h observation | Full SLO pack + residual risk ACK |

**Progression rule:** advance only if all exit gates pass; any RB-* trigger returns traffic to LKG and resets schedule.

**Forbidden under OPTION_2:** start at >1%; skip stages; disable auto_rollback; shrink observation_window below 24 h for first production entry.

---

## 6. Quality, Safety, Cost Gate Thresholds

### 6.1 Universal delta thresholds

| Band | Delta vs baseline | Action |
|---|---|---|
| Green | < 5% | Proceed |
| Amber | ≥ 5% and < 15% | **auto-flag** (QG review, no silent continue) |
| Red | ≥ 15% | **HITL stop** (and auto-rollback if already in canary/prod traffic) |

### 6.2 Absolute safety floors

| Signal | Threshold | Action |
|---|---|---|
| Trust score | < 0.85 | warning |
| Trust score | < 0.70 | hitl_review |
| Trust score | < 0.50 | trip + rollback |
| Trust decay from canary baseline | > 15% | rollback RB-03 |
| PII leak count | > 0 | rollback |
| Cross-tenant breach | > 0 | kill switch |
| Policy CRITICAL | > 0 burst | rollback |
| Monthly cost vs budget | > 100% | trip |

### 6.3 Token budget

| Gate | Default | Action |
|---|---|---|
| Per-turn token ceiling | per tenant template | rewrite_caps / deny |
| Session token ceiling | per tenant template | hitl / deny |
| Research context pool | ≤ 15_000 tokens (G9) | compact or HITL |

---

## 7. Automated Rollback Parameters

| ID | Condition (semantic) | Action | Max time to LKG |
|---|---|---|---|
| RB-01 | Circuit breaker trip | instant_lkg | 5 min |
| RB-02 | Policy violation surge ≥15% | instant_lkg + HITL | 5 min |
| RB-03 | Trust decay >15% vs canary baseline | instant_lkg | 5 min |
| RB-04 | Doctor CRITICAL fail | instant_lkg or traffic shed | 5 min |
| RB-05 | PII/secret leakage | instant_lkg + quarantine | 5 min |
| RB-06 | Cross-tenant breach | kill switch | immediate |
| RB-07 | Eval probe ≥15% degradation | pause/rollback | 15 min |
| RB-08 | Cost ceiling breach | trip + scale-in | 5 min |
| RB-09 | Error budget exhaust | halt canary / rollback | 15 min |

**Parameters:**

```yaml
rollback_parameters:
  mode: automatic
  require_hitl_to_re_canary: true
  cool_down_full_pipeline_cycles: 1
  last_known_good_immutable: true
  feature_flag_kill_switch: true
```

---

## 8. Residual Risk Matrix (DSL-level)

| ID | Risk | Likelihood | Impact | Treatment | Residual |
|---|---|---|---|---|---|
| RR-01 | Policy server wire lag | H | H | Doctor fail-closed in enforce | MED after probes |
| RR-02 | SPIRE not live | H | H | Identity probes | MED |
| RR-03 | Unknown prod traffic shapes | M | H | Canary + 24–72 h dwell | MED |
| RR-04 | Judge drift | M | M | Dual-judge family split | LOW |
| RR-05 | Approval fatigue | M | M | C-PA-08 cultural caps | LOW |
| RR-06 | Research citation live-API gaps | M | M | Fail-closed gate | MED |
| RR-07 | Multi-agent load failures | H | H | Step E chaos | HIGH until E |
| RR-08 | Cost runaway at 100% | M | H | RB-08 + budgets | MED |
| RR-09 | G9 carry-forward unauth memory | H | H | Doctor memory auth | HIGH until auth |
| RR-10 | OPTION_3 temptation (full auto) | L | H | HARD_STOP culture | LOW |

---

## 9. Decision Vocabulary

| Token | Meaning |
|---|---|
| `allow_promote` | Stage exit green |
| `auto_flag` | ≥5% issue; human review required before advance |
| `hitl_stop` | ≥15% or CRITICAL; pipeline halt |
| `auto_rollback` | Traffic to LKG without waiting |
| `block_promote` | Pre-traffic gate fail |
| `kill_switch` | Full disable affected tool/agent class |

---

## 10. Example (YAML isomorphic)

```yaml
apiVersion: "1.0.0"
kind: ReleaseManifest
metadata:
  name: agentic-rd-prod
  release_id: "rel-deadbeefcafebabe"
  overlay: OPTION_2_STANDARD
  upstream_tag: research-loop-v1.0.0
  resume_token: G10_PRODUCTION_DEPLOY_v1
  tenant_risk_tier: RT-2
canary:
  observation_window_hours: 48
  auto_rollback: true
  schedule:
    - pct: 1
      dwell_minutes: 60
      exit_gates: [QG-001, QG-010]
    - pct: 5
      dwell_minutes: 120
      exit_gates: [QG-001, QG-002, QG-010]
    - pct: 25
      dwell_minutes: 240
      exit_gates: [QG-001, QG-002, QG-003, QG-010]
    - pct: 100
      dwell_minutes: 2880
      exit_gates: [QG-001, QG-002, QG-003, QG-004, QG-010]
rollback:
  last_known_good: "deadbeefcafebabe"
  triggers:
    - id: RB-03
      condition: "trust_decay_pct > 15"
      action: instant_lkg
```

---

## 11. Companions & Inheritance

- Blueprint: `PRODUCTION_AGENTOPS_BLUEPRINT.md`
- Discovery: `CAPABILITY_DISCOVERY.yaml`
- Instances: `cicd_pipeline.yaml`, `quality_gates.yaml`, `doctor_checks.yaml`, `fleet_management.yaml`
- Thresholds inherit G5 5%/15% and trust floors; isolation inherits G8; research gates inherit G9

---

*PRODUCTION_DSL_SPEC.md · G10 Step C · OPTION_2_STANDARD · DRAFT_PRE_GATE · 2026-07-25*
