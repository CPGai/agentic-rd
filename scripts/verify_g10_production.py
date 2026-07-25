#!/usr/bin/env python3
"""G10 Production AgentOps — Pack Verifier (Step E/F)

Standalone verifier: file existence, YAML safe_load, MD section grep,
structural content, chaos dry-run metrics, cross-artifact consistency,
secret scan, XML/HTML YAML scan.

Run: python scripts/verify_g10_production.py
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G10 = os.path.join(ROOT, "specs", "g10_production")

errors: list[str] = []
checks = 0

RESUME = "G10_PRODUCTION_DEPLOY_v1"
UPSTREAM = "research-loop-v1.0.0"
OVERLAY = "OPTION_2_STANDARD"

ALL_FILES = [
    "PRODUCTION_AGENTOPS_BLUEPRINT.md",
    "CAPABILITY_DISCOVERY.yaml",
    "PRODUCTION_DSL_SPEC.md",
    "cicd_pipeline.yaml",
    "quality_gates.yaml",
    "doctor_checks.yaml",
    "fleet_management.yaml",
]
YAML_FILES = [
    "CAPABILITY_DISCOVERY.yaml",
    "cicd_pipeline.yaml",
    "quality_gates.yaml",
    "doctor_checks.yaml",
    "fleet_management.yaml",
]
RESUME_TOKENS = [
    "G1_HARNESS_APPROVED_v1",
    "G2_TOOL_REGISTRY_LOCKED_v1",
    "G2_TOOLING_APPROVED_v1",
    "G3_CONTEXT_LAYER_LOCKED_v1",
    "G4_TOPOLOGY_APPROVED_v1",
    "G5_EVAL_FRAMEWORK_APPROVED_v1",
    "G5_EVAL_APPROVED_v1",
    "G6_VIBE_ENV_LOCKED_v1",
    "G7_IMPROVEMENT_BOUNDS_v1",
    "G8_MULTITENANT_APPROVED_v1",
    "G9_RESEARCH_FLEET_LOCKED_v1",
    "G10_PRODUCTION_DEPLOY_v1",
    "RESUME_TOKEN",
]


def check(cond: bool, msg: str) -> None:
    global checks
    checks += 1
    if not cond:
        errors.append(msg)


def load_yaml(path: str):
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


# 1. File existence
for f in ALL_FILES:
    check(os.path.isfile(os.path.join(G10, f)), f"MISSING: {f}")
check(
    os.path.isfile(os.path.join(G10, "G10_MIGRATION_CONTEXT.md")),
    "MISSING: G10_MIGRATION_CONTEXT.md",
)
check(os.path.isfile(os.path.join(ROOT, "scripts", "dry_run_g10.py")), "MISSING dry_run_g10.py")
check(
    os.path.isfile(os.path.join(ROOT, "tests", "test_g10_production.py")),
    "MISSING test_g10_production.py",
)

# 2. YAML safe_load
yaml_data = {}
for yf in YAML_FILES:
    path = os.path.join(G10, yf)
    try:
        yaml_data[yf] = load_yaml(path)
        check(isinstance(yaml_data[yf], dict), f"YAML not dict: {yf}")
    except Exception as e:
        yaml_data[yf] = {}
        errors.append(f"YAML parse error {yf}: {e}")
        checks += 1

# 3. Blueprint MD sections
bp = load_text(os.path.join(G10, "PRODUCTION_AGENTOPS_BLUEPRINT.md"))
bp_l = bp.lower()
for sec in [
    "Spec-Driven CI/CD",
    "Deployment Topologies",
    "Vertex AI",
    "Cloud Run",
    "Live-Path Enterprise Policy",
    "OpenTelemetry",
    "Automatic Rollback",
    "Doctor Checks",
    "Release Evidence Pack",
    "Shared Accountability",
    "Cultural Safeguards",
    "approval fatigue",
    "token-max",
    "OPTION_1_CONSERVATIVE",
    "OPTION_2_STANDARD",
    "OPTION_3_CREATIVE",
    "G10_PRODUCTION_DEPLOY_v1",
    "research-loop-v1.0.0",
    "C-PA-01",
    "C-PA-08",
    "LLM06",
    "1%",
    "15%",
    "5%",
]:
    check(sec.lower() in bp_l, f"Blueprint missing '{sec}'")
check("★" in bp, "Blueprint missing OPTION_2 star")

# 4. DSL sections
dsl = load_text(os.path.join(G10, "PRODUCTION_DSL_SPEC.md"))
for sec in [
    "EBNF",
    "Structural Validation",
    "Semantic Validation",
    "Canary Schedule",
    "Residual Risk",
    "auto_flag",
    "hitl_stop",
    RESUME,
    OVERLAY,
]:
    check(sec.lower() in dsl.lower(), f"DSL missing '{sec}'")
check(len(set(re.findall(r"SV-PA-\d+", dsl))) >= 15, "SV-PA count < 15")
check(len(set(re.findall(r"SEM-PA-\d+", dsl))) >= 10, "SEM-PA count < 10")

# 5. Capability discovery
cap = yaml_data.get("CAPABILITY_DISCOVERY.yaml", {})
check(cap.get("blue_resume_token") == RESUME, "cap token")
check(cap.get("overlay") == OVERLAY, "cap overlay")
check(cap.get("upstream_tag") == UPSTREAM, "cap upstream")
rts = cap.get("production_runtimes") or []
names = " ".join(str(r.get("name", "")) for r in rts)
check("Vertex" in names, "Vertex runtime")
check("Cloud Run" in names, "Cloud Run runtime")
check("gVisor" in names or "Agent Sandbox" in names, "GKE/gVisor runtime")
rn = " ".join(str(r.get("name", "")) for r in (cap.get("cicd_runners") or []))
check("GitHub Actions" in rn, "GitHub Actions")
check("Cloud Build" in rn, "Cloud Build")
check("Hermes" in rn, "Hermes scheduler")
tn = " ".join(str(t.get("name", "")) for t in (cap.get("telemetry_collectors") or []))
check("OpenTelemetry" in tn, "OTEL collector")
check("Google Cloud Observability" in tn, "GCP Observability")
proc = (cap.get("procurement_summary") or {}).get("tiers") or {}
for t in ["T1", "T2", "T3", "T4"]:
    check(t in proc, f"procurement {t}")

# 6. cicd
cicd = yaml_data.get("cicd_pipeline.yaml", {})
check(cicd.get("blue_resume_token") == RESUME, "cicd token")
sids = {s.get("id") for s in (cicd.get("stages") or [])}
for s in ["STG-01", "STG-02", "STG-03", "STG-04", "STG-05", "STG-06", "STG-07", "STG-08", "STG-09", "STG-10"]:
    check(s in sids or s == "STG-05" and ("STG-05" in sids or "STG-05_fast" in sids), f"stage {s}")
# stricter STG-05
check("STG-05" in sids, "STG-05 full present")
stg08 = next((s for s in cicd.get("stages") or [] if s.get("id") == "STG-08"), {})
pcts = [c.get("pct") for c in ((stg08.get("canary") or {}).get("schedule") or [])]
check(pcts == [1, 5, 25, 100], f"cicd canary pcts {pcts}")
check((stg08.get("canary") or {}).get("auto_rollback") is True, "cicd auto_rollback")

# 7. quality gates
qg = yaml_data.get("quality_gates.yaml", {})
check(qg.get("blue_resume_token") == RESUME, "qg token")
bands = qg.get("delta_bands") or {}
check((bands.get("amber") or {}).get("min_degradation_pct") == 5, "5% amber")
check((bands.get("red") or {}).get("min_degradation_pct") == 15, "15% red")
ts = qg.get("trust_score") or {}
thr = ts.get("thresholds") or {}
check(thr.get("warning") == 0.85, "warning 0.85")
check(thr.get("hitl_review") == 0.70, "hitl 0.70")
check(thr.get("trip") == 0.50, "trip 0.50")
check(ts.get("canary_decay_rollback_pct") == 15, "decay 15")
check(ts.get("auto_restore") is False, "auto_restore false")
gates = qg.get("quality_gates") or []
gids = {g.get("id") for g in gates}
for gid in ["QG-001", "QG-002", "QG-003", "QG-010", "QG-020", "QG-030", "QG-050", "QG-061"]:
    check(gid in gids, f"gate {gid}")
g20 = next((g for g in gates if g.get("id") == "QG-020"), {})
check(g20.get("non_delegatable") is True, "QG-020 non_delegatable")
check(g20.get("llm_can_bypass") is False, "QG-020 no bypass")
check(len(g20.get("controls") or []) == 8, "LLM06 count 8")

# 8. doctor
doc = yaml_data.get("doctor_checks.yaml", {})
check(doc.get("blue_resume_token") == RESUME, "doc token")
probes = doc.get("probes") or []
check(len(probes) >= 15, f"probes count {len(probes)}")
types = {p.get("probe_type") for p in probes}
for pt in ["svid_validation", "network_boundary", "policy_server_ping", "memory_bank_health", "pin_concurrence", "fleet_quorum"]:
    check(pt in types, f"probe_type {pt}")
check(all(p.get("fail_closed") is True for p in probes if p.get("severity") == "CRITICAL"), "CRITICAL fail_closed")
pids = {p.get("id") for p in probes}
for pid in ["DOC-IDENT-01", "DOC-NET-02", "DOC-POL-01", "DOC-MEM-01", "DOC-MEM-02"]:
    check(pid in pids, f"probe {pid}")
check((doc.get("modes") or {}).get("default_production_mode") == "enforce", "doctor enforce default")

# 9. fleet
fl = yaml_data.get("fleet_management.yaml", {})
check(fl.get("blue_resume_token") == RESUME, "fleet token")
fleet = fl.get("fleet") or {}
check(fleet.get("topology") == "hierarchical_coordinator_specialists", "topology")
check(fleet.get("l4_agent_creator") is False, "L4 disabled")
check(fleet.get("max_concurrent_specialists") == 3, "max specialists 3")
can = fl.get("canary") or {}
sp = [x.get("pct") for x in (can.get("schedule") or [])]
check(sp == [1, 5, 25, 100], f"fleet canary {sp}")
check(can.get("auto_rollback") is True, "fleet auto_rollback")
rbs = (fl.get("rollback") or {}).get("triggers") or []
rb_ids = {r.get("id") for r in rbs}
for rid in ["RB-01", "RB-02", "RB-03", "RB-04", "RB-05", "RB-06", "RB-07", "RB-08", "RB-09"]:
    check(rid in rb_ids, f"rollback {rid}")
rb03 = next((r for r in rbs if r.get("id") == "RB-03"), {})
check("15" in str(rb03.get("condition", "")), "RB-03 mentions 15")
routes = (fl.get("model_routing") or {}).get("routes") or []
tiers = {r.get("tier") for r in routes}
check("Premium_Frontier" in tiers and "Strong_Coding" in tiers and "Fast_Flash" in tiers, "model tiers")
check((fl.get("model_routing") or {}).get("forbid_frozen_version_pins_in_constitution") is True, "no frozen pins")
check((fl.get("policy_live_path") or {}).get("intent_status") == "WIRED_LIVE_PATH", "policy live path intent")

# 10. Chaos dry-run execution + metrics
dry = subprocess.run(
    [sys.executable, os.path.join(ROOT, "scripts", "dry_run_g10.py")],
    cwd=ROOT,
    capture_output=True,
    text=True,
)
check(dry.returncode == 0, f"dry_run_g10 rc={dry.returncode}")
metrics_path = os.path.join(G10, "chaos_dry_run_metrics.json")
check(os.path.isfile(metrics_path), "chaos_dry_run_metrics.json missing")
if os.path.isfile(metrics_path):
    metrics = json.load(open(metrics_path, encoding="utf-8"))
    check(metrics.get("resume_token") == RESUME, "metrics token")
    check(metrics.get("summary", {}).get("all_pass") is True, "metrics all_pass")
    check(metrics.get("summary", {}).get("passed") == 5, "metrics passed==5")
    check(metrics.get("summary", {}).get("policy_critical_blocks") == 8, "metrics policy blocks")
    check(metrics.get("summary", {}).get("pii_leaks") == 0, "metrics pii leaks")
    check(metrics.get("summary", {}).get("trust_rolled_back_to_lkg") is True, "metrics trust LKG")
    check(metrics.get("summary", {}).get("doctor_isolated_fleet") is True, "metrics doctor isolate")
    check(metrics.get("lkg_revision") == "v0.9.0-previous", "LKG revision string")

# 11. Cross-artifact consistency
for fn in ALL_FILES:
    content = load_text(os.path.join(G10, fn))
    check(RESUME in content, f"{fn} missing token")
    check(OVERLAY in content, f"{fn} missing overlay")
    check(UPSTREAM in content, f"{fn} missing upstream")

# 12. Secret scan
SECRET_PATTERNS = [
    re.compile(r"(?:token|secret|password|api_key|apikey|bearer)\s*[=:]\s*\S{20,}", re.I),
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9\-_]{20,}"),
]
secret_hits = []
scan_files = ALL_FILES + (["chaos_dry_run_metrics.json"] if os.path.isfile(metrics_path) else [])
for f in scan_files:
    content = load_text(os.path.join(G10, f))
    for pat in SECRET_PATTERNS:
        for m in pat.finditer(content):
            hit = m.group(0)
            if any(rt in hit for rt in RESUME_TOKENS):
                continue
            if "resume_token" in hit.lower() or "blue_resume" in hit.lower():
                continue
            secret_hits.append(f"{f}: {hit[:80]}")
check(len(secret_hits) == 0, f"Secret scan hits: {secret_hits[:5]}")

# 13. XML/HTML in YAML only
xml_pat = re.compile(r"<[a-zA-Z][^>]*>")
xml_hits = []
for yf in YAML_FILES:
    content = load_text(os.path.join(G10, yf))
    for m in xml_pat.finditer(content):
        xml_hits.append(f"{yf}: {m.group(0)}")
check(len(xml_hits) == 0, f"XML/HTML in YAML: {xml_hits[:5]}")

# 14. ST-G10 intent bindings
check("ST-G10-01" in bp or "Canary schedule rejects jump" in bp, "ST-G10 intents present")
check("RB-03" in load_text(os.path.join(G10, "fleet_management.yaml")), "RB-03 in fleet")

# Summary
passed = checks - len(errors)
print("=" * 60)
print("G10 PACK VERIFIER (Step E/F)")
print("=" * 60)
print(f"Total checks: {checks}")
print(f"Passed:       {passed}")
print(f"Failed:       {len(errors)}")
if errors:
    print("\n--- FAILURES ---")
    for e in errors:
        print(f"  FAIL: {e}")
print("=" * 60)
print("RESULT: ALL CHECKS PASSED" if not errors else f"RESULT: {len(errors)} FAILURES")
print("=" * 60)
sys.exit(1 if errors else 0)
