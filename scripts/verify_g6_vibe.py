#!/usr/bin/env python3
"""Standalone G6 vibe coding & agentic IDEs pack verifier (repo source of truth after lock).

Run:
  cd /home/carlospg/workspace/agentic-rd && source .venv-hermes/bin/activate \
    && python scripts/verify_g6_vibe.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
G6 = ROOT / "specs" / "g6_vibe"

errors: list[str] = []
checks = 0


def check(cond: bool, msg: str) -> None:
    global checks
    checks += 1
    status = "OK " if cond else "ERR"
    print(f"  {status}  {msg}")
    if not cond:
        errors.append(msg)


def scan_secrets(text: str) -> list[str]:
    """Coarse secret scan with min-length 20 to avoid prose false positives."""
    found: list[str] = []
    patterns = [
        r"sk-[a-zA-Z0-9]{20,}",
        r"Bearer\s+[A-Za-z0-9\-._~+/]{20,}={0,2}",
        r"AIza[a-zA-Z0-9]{35}",
        r"api[_-]?key\s*[:=]\s*['\"][^'\"]{8,}['\"]",
    ]
    for pat in patterns:
        found.extend(re.findall(pat, text, re.I))
    return found


# ---------------------------------------------------------------------------
# 1. Required files
# ---------------------------------------------------------------------------
print("=== G6 Pack Verification ===")

REQUIRED = [
    "VIBECODING_SPECTRUM.md",
    "SURFACE_CAPABILITY_MATRIX.yaml",
    "vibe_environment.yaml",
    "slash_command_mappings.yaml",
    "AGENTS_INHERITANCE_RULES.md",
    "G6_MIGRATION_CONTEXT.md",
]
for rel in REQUIRED:
    p = G6 / rel
    check(p.is_file() and p.stat().st_size > 0, f"exists {rel}")

# ---------------------------------------------------------------------------
# 2. No stale files
# ---------------------------------------------------------------------------
for f in G6.iterdir():
    if f.is_file():
        for pat in ["_extract", "_verify", "_tmp"]:
            check(pat not in f.name, f"no_stale:{f.name}")

# ---------------------------------------------------------------------------
# 3. Parse all YAML artifacts
# ---------------------------------------------------------------------------
spec_md = (G6 / "VIBECODING_SPECTRUM.md").read_text(encoding="utf-8")
surf_yaml = yaml.safe_load((G6 / "SURFACE_CAPABILITY_MATRIX.yaml").read_text(encoding="utf-8"))
ve_yaml = yaml.safe_load((G6 / "vibe_environment.yaml").read_text(encoding="utf-8"))
slash_yaml = yaml.safe_load((G6 / "slash_command_mappings.yaml").read_text(encoding="utf-8"))
inheritance_md = (G6 / "AGENTS_INHERITANCE_RULES.md").read_text(encoding="utf-8")
check(True, "parse_all_artifacts")

# ---------------------------------------------------------------------------
# 4. VIBECODING_SPECTRUM.md
# ---------------------------------------------------------------------------
print("\n--- VIBECODING_SPECTRUM.md ---")
spec_lower = spec_md.lower()
check("g6" in spec_lower, "domain_g6")
check("draft_pre_gate" in spec_lower, "status_draft_pre_gate")
check("g6_vibe_env_locked_v1" in spec_lower, "resume_token")
check("eval-v1.0.0" in spec_lower, "upstream_tag_eval")
check("option_1_conservative" in spec_lower, "option_1")
check("option_2_standard" in spec_lower, "option_2")
check("option_3_creative" in spec_lower, "option_3")
check("\u2605" in spec_md, "option_2_star_marker")
check("wp-s1" in spec_lower, "wp_s1_ref")
check("wp-s5" in spec_lower, "wp_s5_ref")
check("wp-f5" in spec_lower, "wp_f5_ref")
check("conductor" in spec_lower, "developer_mode_conductor")
check("orchestrator" in spec_lower, "developer_mode_orchestrator")
check("vibe coding" in spec_lower, "spectrum_vibe_coding")
check("agentic engineering" in spec_lower, "spectrum_agentic_engineering")
check("prototype dune" in spec_lower, "prototype_dune_section")
check("transition trigger" in spec_lower, "transition_trigger_section")
check("no yolo" in spec_lower, "no_yolo_boundary")
check("gherkin" in spec_lower, "gherkin_reference")
check("token econom" in spec_lower, "token_economics")
check("premium frontier" in spec_lower, "model_premium")
check("strong coding" in spec_lower, "model_strong")
check("fast flash" in spec_lower, "model_flash")
check("antigravity" in spec_lower, "surface_antigravity")
check("hermes" in spec_lower, "surface_hermes")

# SDD pattern
check("spec-driven" in spec_lower or "sdd" in spec_lower, "sdd_pattern")

# G5 inheritance
check("circuit breaker" in spec_lower, "g5_circuit_breaker")
check("trajectory" in spec_lower, "g5_trajectory")
check("trust score" in spec_lower, "g5_trust_score")

# 8 ST-G6 intents
st_count = len(re.findall(r"ST-G6-\d+", spec_md))
check(st_count >= 8, f"structural_test_intents:{st_count}/8")

# Secret scan
secrets = scan_secrets(spec_md)
check(len(secrets) == 0, f"no_secrets_spectrum ({len(secrets)} found)")

# ---------------------------------------------------------------------------
# 5. SURFACE_CAPABILITY_MATRIX.yaml
# ---------------------------------------------------------------------------
print("\n--- SURFACE_CAPABILITY_MATRIX.yaml ---")
check(surf_yaml.get("domain") == "G6", "domain")
check(surf_yaml.get("status") == "DRAFT_PRE_GATE", "status")
check(surf_yaml.get("overlay") == "OPTION_2_STANDARD", "overlay")
check(surf_yaml.get("upstream_tag") == "eval-v1.0.0", "upstream_tag")
check(surf_yaml.get("blue_resume_token") == "G6_VIBE_ENV_LOCKED_v1", "resume_token")

surfaces = surf_yaml.get("surfaces", {})
for s in ["hermes_cli", "antigravity_cli", "serverless_agent_engine"]:
    check(s in surfaces, f"surface:{s}")

bc = surf_yaml.get("blue_slash_commands", {})
for cmd in ["/goal", "/grill-me", "/browser", "/schedule"]:
    check(cmd in bc, f"blue_cmd:{cmd}")

hooks = surf_yaml.get("hooks", {})
for h in ["pre_tool", "post_file_edit", "pre_commit", "approval_bypass"]:
    check(h in hooks, f"hook:{h}")

ide = surf_yaml.get("ide_extensions", {})
for i in ["vscode", "zed", "jetbrains"]:
    check(i in ide, f"ide:{i}")

hub = surf_yaml.get("skills_hub", {})
check(hub.get("total_skills", 0) >= 50, f"skills_hub_count:{hub.get('total_skills', 0)}")

proc = surf_yaml.get("procurement_summary", {})
check(len(proc.get("gaps", [])) > 0, "procurement_gaps_exist")

secrets = scan_secrets((G6 / "SURFACE_CAPABILITY_MATRIX.yaml").read_text(encoding="utf-8"))
check(len(secrets) == 0, f"no_secrets_surface ({len(secrets)} found)")

# ---------------------------------------------------------------------------
# 6. vibe_environment.yaml
# ---------------------------------------------------------------------------
print("\n--- vibe_environment.yaml ---")
check(ve_yaml.get("domain") == "G6", "domain")
check(ve_yaml.get("overlay") == "OPTION_2_STANDARD", "overlay")
check(ve_yaml.get("blue_resume_token") == "G6_VIBE_ENV_LOCKED_v1", "resume_token")

wm = ve_yaml.get("workspace_mode", {})
check("prototype_dune" in wm, "mode_prototype_dune")
check("production_path" in wm, "mode_production_path")
check(wm.get("prototype_dune", {}).get("enabled") == True, "dune_enabled")
check(wm.get("production_path", {}).get("enabled") == True, "production_enabled")

# Transition triggers
tts = ve_yaml.get("transition_triggers", [])
check(len(tts) >= 9, f"transition_triggers_count:{len(tts)}")
tt_ids = [t.get("id") for t in tts]
check("TT-01" in tt_ids, "trigger_tt01")
check("TT-09" in tt_ids, "trigger_tt09")
for t in tts:
    for field in ["id", "name", "from", "to", "condition"]:
        check(field in t, f"trigger:{t.get('id','?')}:{field}")

# Trigger names
tt_names = [t.get("name") for t in tts]
for name in ["stakes_escalation", "production_deployment", "agent_as_product"]:
    check(name in tt_names, f"trigger_name:{name}")

# Surface posture
sp = ve_yaml.get("surface_posture", {})
check(sp.get("primary") == "hermes_cli", "primary_surface")
check(sp.get("secondary") == "antigravity_cli", "secondary_surface")

# SDD
sdd = ve_yaml.get("sdd", {})
check(sdd.get("enabled") == True, "sdd_enabled")
check(sdd.get("spec_format") == "hybrid_markdown_yaml", "sdd_format")
check(sdd.get("bdd_syntax") == "gherkin", "sdd_bdd_syntax")
check(sdd.get("spec_location") == "specs/", "sdd_location")
placement = sdd.get("instruction_placement", {})
for loc in ["chat_interface", "specs_folder", "agent_skills", "agents_md"]:
    check(loc in placement, f"sdd_placement:{loc}")
te = sdd.get("token_economics", {})
check(te.get("yaml_for_nesting_depth_gt_3") == True, "token_yaml_deep_nesting")

# G5 integration
g5i = ve_yaml.get("g5_integration", {})
for key in ["trajectory_schema", "trust_score", "circuit_breaker",
            "checkpoint_protocol", "pii_scrubbing", "llm_as_judge", "agbom"]:
    check(key in g5i, f"g5_key:{key}")
check(g5i.get("trajectory_emission", {}).get("agentic_engineering") == "mandatory", "trajectory_mandatory_prod")
check(g5i.get("circuit_breaker", {}).get("vibe_coding") == "disabled", "cb_disabled_dune")
check(g5i.get("circuit_breaker", {}).get("agentic_engineering") == "active_15_fm_triggers", "cb_active_prod")
check(g5i.get("checkpoint_protocol", {}).get("agentic_engineering") == "mandatory", "checkpoint_mandatory_prod")
check(g5i.get("pii_scrubbing", {}).get("agentic_engineering") == "mandatory", "pii_mandatory_prod")

# Hooks
ve_hooks = ve_yaml.get("hooks", {})
for h in ["pre_tool", "post_file_edit", "pre_commit", "approval_bypass"]:
    check(h in ve_hooks, f"hook:{h}")

# Constraints
cl = ve_yaml.get("constraints_inherited", [])
check(len(cl) >= 15, f"constraints_count:{len(cl)}")

secrets = scan_secrets((G6 / "vibe_environment.yaml").read_text(encoding="utf-8"))
check(len(secrets) == 0, f"no_secrets_ve ({len(secrets)} found)")

# ---------------------------------------------------------------------------
# 7. slash_command_mappings.yaml
# ---------------------------------------------------------------------------
print("\n--- slash_command_mappings.yaml ---")
check(slash_yaml.get("domain") == "G6", "domain")
check(slash_yaml.get("overlay") == "OPTION_2_STANDARD", "overlay")

bc2 = slash_yaml.get("blue_commands", {})
for cmd in ["/goal", "/grill-me", "/browser", "/schedule"]:
    check(cmd in bc2, f"blue_cmd:{cmd}")

goal = bc2.get("/goal", {})
check(goal.get("hermes_native") == True, "goal_native")

grill = bc2.get("/grill-me", {})
check(grill.get("hermes_native") == False, "grill_not_native")
check(grill.get("model_tier") == "premium_frontier", "grill_premium")

sched = bc2.get("/schedule", {})
check(sched.get("hermes_command") == "/cron", "schedule_maps_to_cron")

native = slash_yaml.get("hermes_native_commands", {})
check("/yolo" in native.get("configuration", {}), "yolo_mapped")

rm = slash_yaml.get("routing_matrix", [])
check(len(rm) >= 8, f"routing_matrix_count:{len(rm)}")

secrets = scan_secrets((G6 / "slash_command_mappings.yaml").read_text(encoding="utf-8"))
check(len(secrets) == 0, f"no_secrets_slash ({len(secrets)} found)")

# ---------------------------------------------------------------------------
# 8. AGENTS_INHERITANCE_RULES.md
# ---------------------------------------------------------------------------
print("\n--- AGENTS_INHERITANCE_RULES.md ---")
inh_lower = inheritance_md.lower()
check("g6" in inh_lower, "domain_g6")
check("draft_pre_gate" in inh_lower, "status")
check("g6_vibe_env_locked_v1" in inh_lower, "resume_token")
check("inheritance" in inh_lower, "inheritance_principle")
check("tighten" in inh_lower, "tightening_rules")
check("relax" in inh_lower, "relaxation_forbidden")
check("prototype dune" in inh_lower, "prototype_dune")
check("wsl2" in inh_lower, "wsl2_rule")
check("hitl" in inh_lower, "hitl_rule")
check("yolo" in inh_lower, "yolo_rules")
check("conflict resolution" in inh_lower, "conflict_resolution")
check("precedence" in inh_lower, "precedence")

for s in ["hermes cli", "antigravity", "delegate", "cron"]:
    check(s in inh_lower, f"surface:{s}")

check("circuit breaker" in inh_lower, "g5_cb")
check("trajectory" in inh_lower, "g5_trajectory")
check("trust score" in inh_lower, "g5_trust")

secrets = scan_secrets(inheritance_md)
check(len(secrets) == 0, f"no_secrets_inheritance ({len(secrets)} found)")

# ---------------------------------------------------------------------------
# 9. Cross-artifact consistency
# ---------------------------------------------------------------------------
print("\n--- Cross-Artifact Consistency ---")
all_text = spec_md + "\n"
for name in ["SURFACE_CAPABILITY_MATRIX.yaml", "vibe_environment.yaml",
             "slash_command_mappings.yaml", "AGENTS_INHERITANCE_RULES.md"]:
    all_text += (G6 / name).read_text(encoding="utf-8") + "\n"

check("G6_VIBE_ENV_LOCKED_v1" in all_text, "cross_resume_token")
check("eval-v1.0.0" in all_text, "cross_upstream_tag")
check("OPTION_2_STANDARD" in all_text, "cross_option")

secrets = scan_secrets(all_text)
check(len(secrets) == 0, f"cross_no_secrets ({len(secrets)} found)")

# ---------------------------------------------------------------------------
# 10. Full-pack unit test suite
# ---------------------------------------------------------------------------
print("\n--- Unit Test Suite (stdlib unittest) ---")
import subprocess
result = subprocess.run(
    [sys.executable, "-m", "unittest", "tests.test_g6_vibe", "-v"],
    cwd=str(ROOT), capture_output=True, text=True,
)
print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
if result.stderr.strip():
    print(result.stderr[-500:])
check(result.returncode == 0, f"unittest_suite (exit={result.returncode})")
if result.returncode != 0:
    # Extract summary
    for line in result.stdout.splitlines():
        if "FAILED" in line or "ERROR" in line or "OK" in line:
            check(False, f"unittest:{line.strip()}")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print(f"\n{'='*60}")
passed = checks - len(errors)
print(f"  G6 VERIFICATION COMPLETE: {passed}/{checks} checks")
if errors:
    print(f"  FAILURES ({len(errors)}):")
    for e in errors:
        print(f"    - {e}")
    sys.exit(1)
else:
    print(f"  ALL CHECKS PASSED")
    sys.exit(0)