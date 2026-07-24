#!/usr/bin/env python3
"""Standalone G5 evaluation & observability pack verifier (repo source of truth after lock).

Run:
  cd /home/carlospg/workspace/agentic-rd && source .venv-hermes/bin/activate \
    && python scripts/verify_g5_evaluation.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
G5 = ROOT / "specs" / "g5_evaluation"

errors: list[str] = []
checks = 0


def check(cond: bool, msg: str) -> None:
    global checks
    checks += 1
    status = "OK " if cond else "ERR"
    print(f"  {status}  {msg}")
    if not cond:
        errors.append(msg)


# ---------------------------------------------------------------------------
# 1. Required files
# ---------------------------------------------------------------------------
print("=== G5 Pack Verification ===")

required_files = [
    "EVALUATION_HARNESS_SPEC.md",
    "OBSERVABILITY_PILLARS_SPEC.yaml",
    "CIRCUIT_BREAKER_RULES.yaml",
    "EVAL_DATASET_BENCHMARKS.json",
    "G5_MIGRATION_CONTEXT.md",
]
for rel in required_files:
    p = G5 / rel
    check(p.is_file() and p.stat().st_size > 0, f"exists {rel}")

# ---------------------------------------------------------------------------
# 2. Parse all artifacts
# ---------------------------------------------------------------------------
spec_md = (G5 / "EVALUATION_HARNESS_SPEC.md").read_text(encoding="utf-8")
obs_yaml = yaml.safe_load((G5 / "OBSERVABILITY_PILLARS_SPEC.yaml").read_text(encoding="utf-8"))
cb_yaml = yaml.safe_load((G5 / "CIRCUIT_BREAKER_RULES.yaml").read_text(encoding="utf-8"))
bench_json = json.loads((G5 / "EVAL_DATASET_BENCHMARKS.json").read_text(encoding="utf-8"))
check(True, "parse_all_artifacts")

# ---------------------------------------------------------------------------
# 3. EVALUATION_HARNESS_SPEC.md — 7-pillar compliance and trajectory schema
# ---------------------------------------------------------------------------
print("\n--- EVALUATION_HARNESS_SPEC.md ---")

# Trajectory 6 fields
for field in ["Mission", "Scene", "Thought", "Action", "Observation", "Verdict"]:
    check(field in spec_md, f"trajectory_field:{field}")

# JSON schema fields
for field in ["trajectory_id", "parent_trajectory_id", "agbom_snapshot"]:
    check(field in spec_md, f"json_schema:{field}")

# Dual-judge
check("LLM-as-a-Judge" in spec_md, "llm_as_judge_section")
check("Agent-as-a-Judge" in spec_md, "agent_as_judge_section")
check("pairwise comparison" in spec_md.lower(), "pairwise_comparison")

# Bias mitigations (case-insensitive)
spec_lower = spec_md.lower()
check("position bias" in spec_lower, "bias:position")
check("verbosity bias" in spec_lower, "bias:verbosity")
check("self-enhancement bias" in spec_lower, "bias:self_enhancement")

# Outside-In / Inside-Out
check("Outside-In" in spec_md, "outside_in")
check("Inside-Out" in spec_md, "inside_out")
check("Glass Box" in spec_md, "glass_box")
check("Intent Drift" in spec_md, "intent_drift")
check("Trust Decay" in spec_md, "trust_decay")

# 7 pillars P1-P7
for i in range(1, 8):
    check(f"P{i}" in spec_md, f"pillar:P{i}")

# Degradation thresholds
check("5%" in spec_md, "threshold:5pct")
check("15%" in spec_md, "threshold:15pct")

# Red/Blue/Green
for team in ["Red", "Blue", "Green"]:
    check(team in spec_md, f"team:{team}")

# Flywheel
check("Flywheel" in spec_md, "flywheel")

# OPTION_2 recommended
check("OPTION_2_STANDARD" in spec_md, "option2_present")
check("★" in spec_md, "option2_recommended_star")

# BLUE resume token
check("G5_EVAL_FRAMEWORK_APPROVED_v1" in spec_md, "resume_token_in_spec")

# Upstream tag
check("orchestration-v1.0.0" in spec_md, "upstream_tag_in_spec")

# ---------------------------------------------------------------------------
# 4. OBSERVABILITY_PILLARS_SPEC.yaml — parsing and span hierarchies
# ---------------------------------------------------------------------------
print("\n--- OBSERVABILITY_PILLARS_SPEC.yaml ---")

check(obs_yaml.get("domain") == "G5", "obs:domain=G5")
check(obs_yaml.get("overlay") == "OPTION_2_STANDARD", "obs:overlay")
check(obs_yaml.get("resume_token_authoritative") == "G5_EVAL_FRAMEWORK_APPROVED_v1", "obs:resume_token")
check(obs_yaml.get("resume_token_alias") == "G5_EVAL_APPROVED_v1", "obs:resume_alias")
check(obs_yaml.get("upstream_tag") == "orchestration-v1.0.0", "obs:upstream_tag")

# 5 OTEL span types
span_hierarchy = obs_yaml.get("otel_tracing", {}).get("span_hierarchy", {})
for span_name in ["root_span", "agent_span", "tool_span", "delegate_span", "eval_span"]:
    check(span_name in span_hierarchy, f"obs:span:{span_name}")

# JSON logging
sl = obs_yaml.get("structured_logging", {})
check(sl.get("format") == "JSON", "obs:log_format=json")
check(sl.get("pii_scrubbing") is True, "obs:pii_scrubbing")
check(sl.get("secret_redaction") is True, "obs:secret_redaction")

# Log envelope correlation IDs
required_fields = sl.get("log_envelope", {}).get("required_fields", [])
required_str = " ".join(required_fields)
check("session_id" in required_str, "obs:log:session_id")
check("agent_id" in required_str, "obs:log:agent_id")
check("trace_id" in required_str, "obs:log:trace_id")

# Telemetry hooks
g3_hooks = obs_yaml.get("telemetry_hooks_g3_memory", {}).get("hooks", [])
check(len(g3_hooks) >= 4, f"obs:g3_hooks={len(g3_hooks)}")

g4_ap2_hooks = obs_yaml.get("telemetry_hooks_g4_ap2", {}).get("hooks", [])
check(len(g4_ap2_hooks) >= 4, f"obs:g4_ap2_hooks={len(g4_ap2_hooks)}")

g4_pol_hooks = obs_yaml.get("telemetry_hooks_g4_policy", {}).get("hooks", [])
check(len(g4_pol_hooks) >= 2, f"obs:g4_policy_hooks={len(g4_pol_hooks)}")

g4_fm_hooks = obs_yaml.get("telemetry_hooks_g4_failure_modes", {}).get("hooks", [])
check(len(g4_fm_hooks) == 15, f"obs:g4_fm_hooks={len(g4_fm_hooks)}")

# FM IDs in hooks
all_fm_ids = {
    "FM-TIMEOUT", "FM-REGION-COLLISION", "FM-BUDGET-CEILING",
    "FM-CARD-INVALID", "FM-POLICY-DENY", "FM-NESTING-VIOLATION",
    "FM-CONCURRENCY-CAP", "FM-GOTO-LEAK", "FM-PARTIAL-JOIN",
    "FM-SESSION-TRANSLATION", "FM-TRUST-DECAY", "FM-REMOTE-A2A-OUTAGE",
    "FM-PAYMENT-HOLD-STALL", "FM-CRITIC-LOOP", "FM-SECRET-LEAK",
}
hook_fm_ids = {h.get("fm_id") for h in g4_fm_hooks}
check(hook_fm_ids == all_fm_ids, f"obs:fm_ids_match (missing: {all_fm_ids - hook_fm_ids})")

# Metrics
sys_metrics = obs_yaml.get("metrics", {}).get("system_metrics", [])
check(len(sys_metrics) >= 5, f"obs:system_metrics={len(sys_metrics)}")

qual_metrics = obs_yaml.get("metrics", {}).get("quality_metrics", [])
check(len(qual_metrics) >= 9, f"obs:quality_metrics={len(qual_metrics)}")

# Dashboard panels
panels = obs_yaml.get("dashboard", {}).get("panels", [])
check(len(panels) >= 6, f"obs:dashboard_panels={len(panels)}")

# PII scrubbing pipeline
pipeline = obs_yaml.get("pii_scrubbing", {}).get("pipeline", [])
check(len(pipeline) == 3, f"obs:pii_scrub_steps={len(pipeline)}")

# ---------------------------------------------------------------------------
# 5. CIRCUIT_BREAKER_RULES.yaml — 5%/15% trip logic and state transitions
# ---------------------------------------------------------------------------
print("\n--- CIRCUIT_BREAKER_RULES.yaml ---")

check(cb_yaml.get("domain") == "G5", "cb:domain=G5")
check(cb_yaml.get("overlay") == "OPTION_2_STANDARD", "cb:overlay")
check(cb_yaml.get("resume_token_authoritative") == "G5_EVAL_FRAMEWORK_APPROVED_v1", "cb:resume_token")
check(cb_yaml.get("upstream_tag") == "orchestration-v1.0.0", "cb:upstream_tag")

# Trust score
ts = cb_yaml.get("trust_score", {})
check(ts.get("range") == [0.0, 1.0], "cb:trust_score_range")
check(ts.get("initial") == 1.0, "cb:trust_score_initial=1.0")
check(ts.get("decay_direction") == "monotonically_decreasing", "cb:monotonic_decreasing")
check(ts.get("auto_restore") is False, "cb:auto_restore=false")
check(ts.get("restore_method") == "manual_hitl", "cb:restore=manual_hitl")

# Decay penalties
penalties = cb_yaml.get("decay_penalties", [])
check(len(penalties) == 18, f"cb:decay_penalties={len(penalties)}")
pen_ids = [p.get("id") for p in penalties]
expected_pen_ids = [f"PEN-{i:02d}" for i in range(1, 19)]
check(pen_ids == expected_pen_ids, "cb:penalty_ids_PEN01-18")
check(len(pen_ids) == len(set(pen_ids)), "cb:penalty_ids_unique")

# Trip thresholds
tt = cb_yaml.get("trip_thresholds", {})
check(tt.get("warning") == 0.85, "cb:threshold_warning=0.85")
check(tt.get("hitl_review") == 0.70, "cb:threshold_hitl=0.70")
check(tt.get("trip") == 0.50, "cb:threshold_trip=0.50")

# Immediate trip signals
its = tt.get("immediate_trip_signals", [])
check(len(its) == 3, f"cb:immediate_trip_signals={len(its)}")
check("secret_detected" in its, "cb:immediate:secret_detected")
check("pii_leakage_detected" in its, "cb:immediate:pii_leakage")
check("budget_ceiling_breach" in its, "cb:immediate:budget_ceiling")

# Trip triggers
triggers = cb_yaml.get("trip_triggers", [])
check(len(triggers) == 15, f"cb:trip_triggers={len(triggers)}")
trigger_fm_ids = {t.get("fm_id") for t in triggers}
check(trigger_fm_ids == all_fm_ids, f"cb:trigger_fm_ids (missing: {all_fm_ids - trigger_fm_ids})")

# Immediate trip FMs
trigger_map = {t.get("fm_id"): t for t in triggers}
check(trigger_map.get("FM-BUDGET-CEILING", {}).get("immediate_trip") is True, "cb:fm_budget_immediate")
check(trigger_map.get("FM-SECRET-LEAK", {}).get("immediate_trip") is True, "cb:fm_secret_immediate")

# Quarantine states
qs = cb_yaml.get("quarantine_states", [])
check(len(qs) == 6, f"cb:quarantine_states={len(qs)}")
qs_ids = [s.get("id") for s in qs]
expected_qs = ["QS-HEALTHY", "QS-WARNING", "QS-HITL_REVIEW", "QS-TRIPPED", "QS-QUARANTINE_REVIEW", "QS-LOCKED"]
check(qs_ids == expected_qs, f"cb:quarantine_ids (got: {qs_ids})")

# Actions on trip
actions = cb_yaml.get("actions_on_trip", [])
check("freeze_autonomous_execution" in actions, "cb:action:freeze")
check("revoke_jit_tokens" in actions, "cb:action:revoke_jit")
check("rollback_to_last_checkpoint" in actions, "cb:action:rollback")

# AgBOM
agbom = cb_yaml.get("agbom", {})
check("fields" in agbom and len(agbom["fields"]) > 0, "cb:agbom_fields")
check("drift_detection" in agbom, "cb:agbom_drift_detection")

# Checkpoint protocol
cp = cb_yaml.get("checkpoint_protocol", {})
check("rollback" in cp, "cb:checkpoint_rollback")

# ---------------------------------------------------------------------------
# 6. EVAL_DATASET_BENCHMARKS.json — schema completeness across all 18 scenarios
# ---------------------------------------------------------------------------
print("\n--- EVAL_DATASET_BENCHMARKS.json ---")

check(bench_json.get("domain") == "G5", "bench:domain=G5")
check(bench_json.get("overlay") == "OPTION_2_STANDARD", "bench:overlay")
check(bench_json.get("resume_token_authoritative") == "G5_EVAL_FRAMEWORK_APPROVED_v1", "bench:resume_token")
check(bench_json.get("upstream_tag") == "orchestration-v1.0.0", "bench:upstream_tag")

scenarios = bench_json.get("scenarios", [])
check(len(scenarios) == 18, f"bench:scenario_count={len(scenarios)}")
check(len(scenarios) >= 15, "bench:scenario_count>=15")

# Unique IDs
scenario_ids = [s.get("id") for s in scenarios]
check(len(scenario_ids) == len(set(scenario_ids)), "bench:scenario_ids_unique")

# Required fields per scenario
required_scenario_fields = {
    "id", "name", "failure_mode", "category",
    "expected_verdict", "expected_trust_score_delta",
}
for s in scenarios:
    missing = required_scenario_fields - set(s.keys())
    check(not missing, f"bench:fields:{s.get('id', '?')} (missing: {missing})")

# Category breakdown
categories = {}
for s in scenarios:
    cat = s.get("category", "?")
    categories[cat] = categories.get(cat, 0) + 1
check(categories.get("failure_mode", 0) >= 12, f"bench:failure_mode_scenarios={categories.get('failure_mode', 0)}")
check(categories.get("edge_case", 0) >= 2, f"bench:edge_case_scenarios={categories.get('edge_case', 0)}")
check(categories.get("red_team", 0) == 1, f"bench:red_team_scenarios={categories.get('red_team', 0)}")
check(categories.get("quality_eval", 0) == 1, f"bench:quality_eval_scenarios={categories.get('quality_eval', 0)}")
check(categories.get("threshold", 0) == 2, f"bench:threshold_scenarios={categories.get('threshold', 0)}")

# G4 FM coverage
covered = bench_json.get("coverage_matrix", {}).get("g4_failure_modes_covered", [])
check(len(covered) >= 12, f"bench:fm_coverage={len(covered)}")

# Threshold scenarios
th_scenarios = [s for s in scenarios if s.get("category") == "threshold"]
check(any("5%" in s.get("name", "") or "@5pct" in str(s.get("tags", [])) for s in th_scenarios), "bench:5pct_threshold")
check(any("15%" in s.get("name", "") or "@15pct" in str(s.get("tags", [])) for s in th_scenarios), "bench:15pct_threshold")

# Critical severity
crit = [s for s in scenarios if s.get("severity") == "CRITICAL"]
check(len(crit) >= 3, f"bench:critical_severity={len(crit)}")

# Circuit breaker trip scenarios
trip_scenarios = [s for s in scenarios if s.get("expected_circuit_breaker_trip") is True]
check(len(trip_scenarios) >= 3, f"bench:cb_trip_scenarios={len(trip_scenarios)}")

# ---------------------------------------------------------------------------
# 7. Cross-artifact consistency
# ---------------------------------------------------------------------------
print("\n--- Cross-Artifact Consistency ---")

check("G5_EVAL_FRAMEWORK_APPROVED_v1" in spec_md, "cross:spec:token")
check(obs_yaml.get("resume_token_authoritative") == "G5_EVAL_FRAMEWORK_APPROVED_v1", "cross:obs:token")
check(cb_yaml.get("resume_token_authoritative") == "G5_EVAL_FRAMEWORK_APPROVED_v1", "cross:cb:token")
check(bench_json.get("resume_token_authoritative") == "G5_EVAL_FRAMEWORK_APPROVED_v1", "cross:bench:token")

check("orchestration-v1.0.0" in spec_md, "cross:spec:tag")
check(obs_yaml.get("upstream_tag") == "orchestration-v1.0.0", "cross:obs:tag")
check(cb_yaml.get("upstream_tag") == "orchestration-v1.0.0", "cross:cb:tag")
check(bench_json.get("upstream_tag") == "orchestration-v1.0.0", "cross:bench:tag")

check("OPTION_2_STANDARD" in spec_md, "cross:spec:overlay")
check(obs_yaml.get("overlay") == "OPTION_2_STANDARD", "cross:obs:overlay")
check(cb_yaml.get("overlay") == "OPTION_2_STANDARD", "cross:cb:overlay")
check(bench_json.get("overlay") == "OPTION_2_STANDARD", "cross:bench:overlay")

# ---------------------------------------------------------------------------
# 8. Secret scan (min-length 20 to avoid prose false positives)
# ---------------------------------------------------------------------------
print("\n--- Secret Scan ---")

secret_rx = re.compile(
    r"(api[_-]?key\s*[:=]\s*['\"][^'\"]{8,}['\"]|"
    r"Bearer\s+[A-Za-z0-9\-._~+/]{20,}={0,2}|"
    r"sk-[A-Za-z0-9]{20,})",
    re.I,
)
scanned = 0
secret_hits = 0
for p in G5.rglob("*"):
    if not p.is_file() or p.suffix.lower() not in {".md", ".yaml", ".yml", ".json"}:
        continue
    scanned += 1
    if secret_rx.search(p.read_text(encoding="utf-8", errors="replace")):
        secret_hits += 1
        errors.append(f"secret:{p.relative_to(G5)}")
check(secret_hits == 0, f"secret_scan (files={scanned}, hits={secret_hits})")

# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------
print()
print(f"=== RESULT: {'PASS' if not errors else 'FAIL'} ===")
print(f"checks={checks}  errors={len(errors)}")
print(
    f"scenarios={len(scenarios)}  penalties={len(penalties)}  "
    f"triggers={len(triggers)}  quarantine_states={len(qs)}  "
    f"g4_fm_hooks={len(g4_fm_hooks)}  dashboard_panels={len(panels)}"
)
if errors:
    for e in errors:
        print(f"  ERR  {e}")
    sys.exit(1)
sys.exit(0)
