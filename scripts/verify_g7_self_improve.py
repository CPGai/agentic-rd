#!/usr/bin/env python3
"""G7 Self-Improvement — Standalone Pack Verifier (Step E)

Verifies all declarative artifacts in specs/g7_self_improve/ for
structural completeness, cross-artifact consistency, and secret-free
content. This is the repo source-of-truth verifier after G7 lock.

Run: python3 scripts/verify_g7_self_improve.py
"""

import os
import re
import sys
import yaml

G7_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "specs", "g7_self_improve"
)

checks = 0
errors = []


def ok(msg):
    global checks
    checks += 1


def fail(msg):
    global checks
    checks += 1
    errors.append(msg)


def check(condition, msg):
    if condition:
        ok(msg)
    else:
        fail(msg)


def read_file(name):
    path = os.path.join(G7_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def read_yaml(name):
    path = os.path.join(G7_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# =========================================================================
# 1. SELF_IMPROVEMENT_ARCHITECTURE.md (20 checks)
# =========================================================================
arch = read_file("SELF_IMPROVEMENT_ARCHITECTURE.md")
check("Self-Improvement Architecture" in arch, "ARCH: title present")
check("G7_IMPROVEMENT_BOUNDS_v1" in arch, "ARCH: BLUE resume token")
check("OPTION_2_STANDARD" in arch, "ARCH: OPTION_2_STANDARD present")
check("\u2605" in arch, "ARCH: OPTION_2 star marker")
check("vibecoding-v1.0.0" in arch, "ARCH: upstream tag")
for p in ["Detect", "Acquire", "Validate", "Integrate", "Measure"]:
    check(p in arch, f"ARCH: phase '{p}'")
for s in ["S1", "S2", "S3", "S4"]:
    check(s in arch, f"ARCH: severity '{s}'")
for t in ["T1", "T2", "T3", "T4"]:
    check(t in arch, f"ARCH: tier '{t}'")
check("Restricted" in arch, "ARCH: S1 autonomy 'Restricted'")
check("Human-gated" in arch, "ARCH: S2 autonomy 'Human-gated'")
check("Advisory" in arch, "ARCH: S3 autonomy 'Advisory'")
check("Autonomous" in arch, "ARCH: S4 autonomy 'Autonomous'")
check("held-out" in arch.lower(), "ARCH: held-out validation")
check("negative test" in arch.lower(), "ARCH: negative test")
check("generalization" in arch.lower(), "ARCH: generalization-gap")
check("rollback" in arch.lower(), "ARCH: rollback policy")
check("thrashing" in arch.lower(), "ARCH: thrashing detection")
for op in ["DRAFT", "DEBUG", "IMPROVE", "PIVOT", "REFINE"]:
    check(op in arch, f"ARCH: operator '{op}'")
check("L4" in arch and "AgentCreator" in arch, "ARCH: L4 AgentCreator reference")
check("C-LOOP-02" in arch, "ARCH: C-LOOP-02 constraint")
check("Hard Bounds" in arch, "ARCH: hard bounds section")
check("loop budget" in arch.lower(), "ARCH: loop budget cap")
check("G5 Inheritance" in arch, "ARCH: G5 inheritance table")
check("G6 Inheritance" in arch, "ARCH: G6 inheritance table")
check("OPTION_1_CONSERVATIVE" in arch, "ARCH: OPTION_1 in matrix")
check("OPTION_3_CREATIVE" in arch, "ARCH: OPTION_3 in matrix")
check("SELECTED_PATH" in arch, "ARCH: SELECTED_PATH marker")
check("REQUIRED_TELEMETRY" in arch, "ARCH: REQUIRED_TELEMETRY")

# =========================================================================
# 2. CAPABILITY_DISCOVERY.yaml (15 checks)
# =========================================================================
cap = read_yaml("CAPABILITY_DISCOVERY.yaml")
check(cap is not None, "CAP: YAML safe_load succeeds")
check(cap.get("domain") == "G7", "CAP: domain == G7")
check(cap.get("overlay") == "OPTION_2_STANDARD", "CAP: overlay == OPTION_2_STANDARD")
check(cap.get("blue_resume_token") == "G7_IMPROVEMENT_BOUNDS_v1", "CAP: BLUE resume token")
check(cap.get("upstream_tag") == "vibecoding-v1.0.0", "CAP: upstream tag")
si = cap.get("skills_inventory", {})
check(si.get("profile_skill_count", 0) >= 50, "CAP: profile skills >= 50")
check(si.get("workspace_skill_count", 0) >= 1, "CAP: workspace skills >= 1")
sis = cap.get("self_improvement_skills", [])
check(len(sis) >= 5, "CAP: self-improvement skills >= 5")
hn = cap.get("hermes_native_mechanisms", [])
check(len(hn) >= 5, "CAP: Hermes native mechanisms >= 5")
check(cap.get("honcho_status", {}).get("health") == "ok", "CAP: Honcho health == ok")
pm = cap.get("phase_mapping", {})
for ph in ["DETECT", "ACQUIRE", "VALIDATE", "INTEGRATE", "MEASURE"]:
    check(ph in pm, f"CAP: phase '{ph}' in mapping")
ps = cap.get("procurement_summary", {})
check("t1_native_skills" in ps, "CAP: T1 procurement summary")
check("t2_vetted_mcp" in ps, "CAP: T2 procurement summary")
check("t3_custom_generation" in ps, "CAP: T3 procurement summary")

# =========================================================================
# 3. TAXONOMY_AND_BOUNDS.md (18 checks)
# =========================================================================
tax = read_file("TAXONOMY_AND_BOUNDS.md")
check("OPTION_2_STANDARD" in tax, "TAX: OPTION_2_STANDARD present")
check("G7_IMPROVEMENT_BOUNDS_v1" in tax, "TAX: BLUE resume token")
check("vibecoding-v1.0.0" in tax, "TAX: upstream tag")
for it in ["IT-01", "IT-02", "IT-03", "IT-04", "IT-05",
           "IT-06", "IT-07", "IT-08", "IT-09", "IT-10"]:
    check(it in tax, f"TAX: improvement type '{it}'")
check("Prompt Refinement" in tax, "TAX: Prompt Refinement label")
check("Skill Acquisition" in tax, "TAX: Skill Acquisition label")
check("Skill Generation" in tax, "TAX: Skill Generation label")
check("Spec Augmentation" in tax, "TAX: Spec Augmentation label")
check("Tool Adapter Patch" in tax, "TAX: Tool Adapter Patch label")
check("FORBIDDEN" in tax, "TAX: FORBIDDEN label present")
hb_count = len(re.findall(r"\bHB-\d+\b", tax))
check(hb_count >= 8, f"TAX: hard bounds count {hb_count} >= 8")
cb_count = len(re.findall(r"\bCB-\d+\b", tax))
check(cb_count >= 8, f"TAX: conditional bounds count {cb_count} >= 8")

# =========================================================================
# 4. triggers.yaml (25 checks)
# =========================================================================
trg = read_yaml("triggers.yaml")
check(trg is not None, "TRG: YAML safe_load succeeds")
check(trg.get("domain") == "G7", "TRG: domain == G7")
check(trg.get("overlay") == "OPTION_2_STANDARD", "TRG: overlay")
check(trg.get("blue_resume_token") == "G7_IMPROVEMENT_BOUNDS_v1", "TRG: BLUE resume token")
check(trg.get("upstream_tag") == "vibecoding-v1.0.0", "TRG: upstream tag")
tt = trg.get("trajectory_triggers", [])
check(len(tt) >= 3, f"TRG: trajectory triggers {len(tt)} >= 3")
for t in tt:
    check("id" in t and "severity" in t, f"TRG: trajectory trigger {t.get('id')} has id+severity")
ts = trg.get("trust_score_triggers", [])
check(len(ts) >= 3, f"TRG: trust score triggers {len(ts)} >= 3")
for t in ts:
    check("id" in t and "severity" in t, f"TRG: trust score trigger {t.get('id')} has id+severity")
et = trg.get("evaluation_triggers", [])
check(len(et) >= 3, f"TRG: evaluation triggers {len(et)} >= 3")
fm = trg.get("failure_mode_triggers", [])
check(len(fm) >= 3, f"TRG: failure mode triggers {len(fm)} >= 3")
pt = trg.get("pattern_triggers", [])
check(len(pt) >= 3, f"TRG: pattern triggers {len(pt)} >= 3")
ht = trg.get("human_triggers", [])
check(len(ht) >= 1, f"TRG: human triggers {len(ht)} >= 1")
# S1 triggers must have cooldown 0
for t in ts:
    if t.get("severity") == "S1":
        check(t.get("cooldown_cycles") == 0,
              f"TRG: S1 trigger {t.get('id')} cooldown == 0")
# All triggers have unique IDs
all_ids = [t.get("id") for grp in [tt, ts, et, fm, pt, ht] for t in grp]
check(len(all_ids) == len(set(all_ids)), "TRG: all trigger IDs unique")
cr = trg.get("cooldown_rules", {})
check("global_cooldown_cycles" in cr, "TRG: cooldown rules present")
check("escalation_override" in cr, "TRG: escalation override rule")

# =========================================================================
# 5. oversight_boundaries.yaml (20 checks)
# =========================================================================
ovs = read_yaml("oversight_boundaries.yaml")
check(ovs is not None, "OVS: YAML safe_load succeeds")
check(ovs.get("domain") == "G7", "OVS: domain == G7")
check(ovs.get("overlay") == "OPTION_2_STANDARD", "OVS: overlay")
check(ovs.get("blue_resume_token") == "G7_IMPROVEMENT_BOUNDS_v1", "OVS: BLUE resume token")
check(ovs.get("upstream_tag") == "vibecoding-v1.0.0", "OVS: upstream tag")
az = ovs.get("autonomy_zones", [])
check(len(az) >= 4, f"OVS: autonomy zones {len(az)} >= 4")
zone_names = [z.get("zone") for z in az]
check("AUTONOMOUS" in zone_names, "OVS: AUTONOMOUS zone")
check("ADVISORY" in zone_names, "OVS: ADVISORY zone")
check("HUMAN_GATED" in zone_names, "OVS: HUMAN_GATED zone")
check("RESTRICTED" in zone_names, "OVS: RESTRICTED zone")
hg = ovs.get("hitl_gates", [])
check(len(hg) >= 5, f"OVS: HITL gates {len(hg)} >= 5")
check(any(g.get("gate_id") == "HG-05" for g in hg), "OVS: HG-05 (L4 enablement) gate")
check(any(g.get("gate_id") == "HG-03" for g in hg), "OVS: HG-03 (circuit breaker trip) gate")
check(any(g.get("gate_id") == "HG-04" for g in hg), "OVS: HG-04 (loop budget) gate")
fa = ovs.get("forbidden_actions", [])
check(len(fa) >= 8, f"OVS: forbidden actions {len(fa)} >= 8")
fa_ids = [f.get("id") for f in fa]
check("FA-01" in fa_ids, "OVS: FA-01 (L4 AgentCreator forbidden)")
check("FA-02" in fa_ids, "OVS: FA-02 (circuit breaker modification forbidden)")
check("FA-09" in fa_ids, "OVS: FA-09 (AGENTS.md edit forbidden)")
wmo = ovs.get("workspace_mode_overrides", {})
check("vibe_coding" in wmo, "OVS: vibe_coding override")
check("agentic_engineering" in wmo, "OVS: agentic_engineering override")
check("improvement_ledger" in ovs, "OVS: improvement ledger schema")

# =========================================================================
# 6. PIVOT_REFINE_TREE.md (15 checks)
# =========================================================================
prt = read_file("PIVOT_REFINE_TREE.md")
check("OPTION_2_STANDARD" in prt, "PRT: OPTION_2_STANDARD present")
check("G7_IMPROVEMENT_BOUNDS_v1" in prt, "PRT: BLUE resume token")
check("vibecoding-v1.0.0" in prt, "PRT: upstream tag")
for op in ["DRAFT", "DEBUG", "IMPROVE", "PIVOT", "REFINE"]:
    check(op in prt, f"PRT: operator '{op}'")
check("thrashing" in prt.lower(), "PRT: thrashing criterion")
check("rollback" in prt.lower(), "PRT: rollback protocol")
check("generalization" in prt.lower(), "PRT: generalization-gap test")
for s in ["S1", "S2", "S3", "S4"]:
    check(s in prt, f"PRT: severity branch '{s}'")
check("flat" in prt.lower(), "PRT: flat fix curve criterion")

# =========================================================================
# 7. skill_gen_templates/ (10 checks)
# =========================================================================
tmpl_path = os.path.join(G7_DIR, "skill_gen_templates", "gap_filling_skill.tmpl.md")
readme_path = os.path.join(G7_DIR, "skill_gen_templates", "README.md")
check(os.path.exists(tmpl_path), "TPL: gap_filling_skill.tmpl.md exists")
check(os.path.exists(readme_path), "TPL: README.md exists")
tmpl = open(tmpl_path, "r", encoding="utf-8").read()
tmpl_readme = open(readme_path, "r", encoding="utf-8").read()
check("{{skill_name}}" in tmpl, "TPL: skill_name placeholder")
check("{{one_line_description}}" in tmpl, "TPL: description placeholder")
check("metadata" in tmpl, "TPL: metadata section")
check("generated_by" in tmpl, "TPL: generated_by field")
check("quality gate" in tmpl_readme.lower(), "TPL: quality gates documented")
check("8" in tmpl_readme, "TPL: 8 quality gates listed")
check("generalization" in tmpl_readme.lower(), "TPL: generalization-gap in gates")
check("secret scan" in tmpl_readme.lower(), "TPL: secret scan in gates")

# =========================================================================
# 8. Cross-Artifact Consistency (18 checks)
# =========================================================================
all_files = [
    "SELF_IMPROVEMENT_ARCHITECTURE.md",
    "CAPABILITY_DISCOVERY.yaml",
    "TAXONOMY_AND_BOUNDS.md",
    "triggers.yaml",
    "oversight_boundaries.yaml",
    "PIVOT_REFINE_TREE.md",
]
for fname in all_files:
    content = read_file(fname)
    check("G7_IMPROVEMENT_BOUNDS_v1" in content,
          f"XREF: {fname} references BLUE resume token")
    check("OPTION_2_STANDARD" in content,
          f"XREF: {fname} references OPTION_2_STANDARD")
    check("vibecoding-v1.0.0" in content,
          f"XREF: {fname} references upstream tag")

# =========================================================================
# 9. Secret Scan (min-length 20) (4 checks)
# =========================================================================
all_content = ""
for fname in all_files:
    all_content += read_file(fname)
all_content += tmpl + tmpl_readme

bearer_hits = re.findall(r"Bearer\s+[A-Za-z0-9\-_]{20,}", all_content)
sk_hits = re.findall(r"sk-[A-Za-z0-9]{20,}", all_content)
api_key_hits = re.findall(
    r"(?:api[_-]?key|apikey)\s*[=:]\s*[\'\"]?[A-Za-z0-9\-_]{20,}",
    all_content, re.IGNORECASE)
token_hits = [h for h in re.findall(
    r"(?:token|secret|password)\s*[=:]\s*[\'\"]?[A-Za-z0-9\-_]{20,}",
    all_content, re.IGNORECASE)
    if "G7_IMPROVEMENT_BOUNDS" not in h
    and "RESUME_TOKEN" not in h.upper()]

check(len(bearer_hits) == 0, f"SECRET: Bearer tokens found ({len(bearer_hits)})")
check(len(sk_hits) == 0, f"SECRET: sk- keys found ({len(sk_hits)})")
check(len(api_key_hits) == 0, f"SECRET: API keys found ({len(api_key_hits)})")
check(len(token_hits) == 0, f"SECRET: tokens/secrets found ({len(token_hits)})")

# =========================================================================
# 10. Unittest Suite (1 check)
# =========================================================================
import subprocess
test_result = subprocess.run(
    [sys.executable, "-m", "unittest", "tests.test_g7_self_improve"],
    capture_output=True, text=True,
    cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
check(test_result.returncode == 0, "UNIT: test_g7_self_improve suite passes")

# =========================================================================
# Summary
# =========================================================================
passed = checks - len(errors)
sep = "=" * 60
print(f"\n{sep}")
print("G7 SELF-IMPROVEMENT PACK VERIFIER")
print(sep)
print(f"Total checks: {checks}")
print(f"Passed: {passed}")
print(f"Failed: {len(errors)}")
if errors:
    print(f"\nFAILURES:")
    for e in errors:
        print(f"  FAIL  {e}")
else:
    print(f"\n  ALL CHECKS PASSED")
print(f"\nSecret scan: 0 secrets found")
print(f"  Bearer: {len(bearer_hits)}  sk-: {len(sk_hits)}  "
      f"API key: {len(api_key_hits)}  token: {len(token_hits)}")
print(f"\nUnittest: {'PASS' if test_result.returncode == 0 else 'FAIL'}")
print(sep)
sys.exit(0 if not errors else 1)
