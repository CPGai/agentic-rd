#!/usr/bin/env python3
"""Structural verification for locked G3 memory / context pack (Steps A–F).

Runnable without pytest:

  cd /home/carlospg/workspace/agentic-rd && source .venv-hermes/bin/activate \\
    && python scripts/verify_g3_memory.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path("/home/carlospg/workspace/agentic-rd")
G3 = ROOT / "specs/g3_memory"
SKILLS = ROOT / "skills"
sys.path.insert(0, str(ROOT / "scripts"))

from g3_memory import (  # noqa: E402
    ASSEMBLY_ORDER,
    check_l1_budget,
    coloaded_overflow,
    compact_session,
    detect_hard_rule_collisions,
    memory_vs_constraint,
    parse_skill_l1,
    resolve_precedence,
    SkillBody,
    validate_assembly_order,
)

errs: list[str] = []
oks: list[str] = []


def check(cond: bool, ok_msg: str, err_msg: str) -> None:
    (oks if cond else errs).append(ok_msg if cond else err_msg)


REQUIRED_FILES = [
    G3 / "CONTEXT_ENGINEERING_BLUEPRINT.md",
    G3 / "SESSION_STATE_SPEC.md",
    G3 / "HONCHO_INTEGRATION_MATRIX.yaml",
    G3 / "token_budget.yaml",
    G3 / "MEMORY_LOAD_POLICY.yaml",
    G3 / "SKILL_COLOAD_AUDIT.yaml",
    G3 / "G3_MIGRATION_CONTEXT.md",
]

for path in REQUIRED_FILES:
    check(path.is_file() and path.stat().st_size > 400, f"present {path.relative_to(ROOT)}", f"missing {path}")

if any(e.startswith("missing") for e in errs):
    print("G3 VERIFY FAILED")
    for e in errs:
        print(" ERR", e)
    sys.exit(1)

TOKEN = "G3_CONTEXT_LAYER_LOCKED_v1"
PATH = "OPTION_2_STANDARD"

# --- YAML packs ---
matrix = yaml.safe_load((G3 / "HONCHO_INTEGRATION_MATRIX.yaml").read_text(encoding="utf-8"))
tb = yaml.safe_load((G3 / "token_budget.yaml").read_text(encoding="utf-8"))
mlp = yaml.safe_load((G3 / "MEMORY_LOAD_POLICY.yaml").read_text(encoding="utf-8"))
audit = yaml.safe_load((G3 / "SKILL_COLOAD_AUDIT.yaml").read_text(encoding="utf-8"))

for label, doc in (
    ("matrix", matrix),
    ("token_budget", tb),
    ("memory_load", mlp),
    ("coload_audit", audit),
):
    check(doc.get("status") == "LOCKED", f"{label} LOCKED", f"{label} status {doc.get('status')!r}")
    check(doc.get("selected_path") == PATH, f"{label} OPTION_2", f"{label} path mismatch")
    tok = doc.get("resume_token") or doc.get("resume_token_expected")
    check(tok == TOKEN, f"{label} resume", f"{label} resume {tok!r}")

check((matrix.get("loopback") or {}).get("host_octets") == [127, 0, 0, 1], "loopback octets", "bad octets")
check((matrix.get("loopback") or {}).get("api_port") == 8000, "api port 8000", "bad api port")
check(
    (matrix.get("derive_model") or {}).get("observed_model_id") == "deepseek/deepseek-v4-flash",
    "derive model observed",
    "derive model mismatch",
)
check((matrix.get("auth_privacy") or {}).get("auth_use_auth_live") is False, "auth flag false", "auth flag wrong")
check((tb.get("window") or {}).get("static_pack_hard_ceiling") == 0.20, "static ceiling 0.20", "static ceiling")
check((tb.get("skills") or {}).get("concurrent_l2_soft_max") == 3, "l2 soft max 3", "l2 soft max")
check((tb.get("skills") or {}).get("l1_target_tokens_per_skill") == 50, "l1 target 50", "l1 target")

order = audit.get("assembly_order_binding") or []
check(order == list(ASSEMBLY_ORDER), "assembly order binding", f"order {order}")
check(validate_assembly_order(list(ASSEMBLY_ORDER)), "assembly helper ok", "assembly helper broken")
check(not validate_assembly_order(["memory_window", "static_pack"]), "rejects reversed assembly", "false negative order")

# --- Markdown ---
sess = (G3 / "SESSION_STATE_SPEC.md").read_text(encoding="utf-8")
bp = (G3 / "CONTEXT_ENGINEERING_BLUEPRINT.md").read_text(encoding="utf-8")
for pat in (
    "Context assembly sequence",
    "STATIC PACK",
    "Compaction policies",
    "Session lifecycle hooks",
    "mermaid",
    TOKEN,
):
    check(re.search(pat, sess, re.I) is not None, f"SESSION has {pat}", f"SESSION missing {pat}")
for pat in ("Six context types", "Skill anatomy", "Token economics", "WP-S3", TOKEN):
    check(re.search(pat, bp, re.I) is not None, f"BLUEPRINT has {pat}", f"BLUEPRINT missing {pat}")
check("LOCKED" in bp or "APPROVED" in bp or TOKEN in bp, "blueprint gate context", "blueprint weak status")

# promote expectation: statuses may still say DRAFT in prose — lock signal is YAML + TOKEN grant
# Prefer explicit LOCKED markers if present
check(TOKEN in sess and TOKEN in bp, "token in MD", "token missing MD")

# --- Skills seeds ---
skill_mds = sorted(SKILLS.rglob("SKILL.md"))
check(len(skill_mds) >= 5, f"workspace skills>={len(skill_mds)}", f"workspace skills only {len(skill_mds)}")
l1_bad = []
names = []
for sm in skill_mds:
    text = sm.read_text(encoding="utf-8")
    name, desc, has_fm = parse_skill_l1(text)
    check(has_fm, f"FM {sm.relative_to(ROOT)}", f"missing FM {sm}")
    names.append(name or sm.parent.name)
    rep = check_l1_budget(name, desc)
    if not rep["within_hedge"]:
        l1_bad.append(rep)
check(not l1_bad, "all seed L1 within hedge", f"L1 hedge fail {l1_bad}")
for required in (
    "wsl2-execution-routing",
    "agentic-rd-g-domain-runbook",
    "hermes-mcp-server-setup",
    "context-assembly-g3",
    "session-memory-honcho",
):
    check(required in names, f"seed {required}", f"missing seed {required}")

# co-load simulation smoke
demo = [
    SkillBody("a", 10, 10000, ["must use wsl"]),
    SkillBody("b", 5, 10000, ["never use wsl"]),
    SkillBody("c", 1, 15000, []),
]
ov = coloaded_overflow(demo, soft_max=3, flag_chars=32000)
check(any("CC-002_chars" in x for x in ov), "overflow detects chars", f"overflow {ov}")
cols = detect_hard_rule_collisions(demo)
check(len(cols) >= 1, "hard rule collision detect", f"cols {cols}")
check(resolve_precedence(["skill_l2", "constraint_catalog_safety_hooks"]) == "constraint_catalog_safety_hooks", "precedence", "precedence fail")
check(memory_vs_constraint(True, False) == "deny_constraint", "memory loses to constraint", "CC-004 fail")

plan = compact_session(list(range(1, 40)), last_n=10, fill_ratio=0.75)
check(plan.strategy == "C_SLIDE_N" and len(plan.model_view_event_ids) == 10, "compact slide", f"plan {plan}")
em = compact_session(list(range(1, 40)), last_n=10, fill_ratio=0.9)
check(em.strategy == "emergency_truncate", "emergency compact", f"em {em}")

# BLUE token
blue = (ROOT / "specs/references/AGENTIC R&D & IMPLEMENTATION BLUE.md").read_text(encoding="utf-8")
check(f"RESUME_TOKEN: {TOKEN}" in blue, "BLUE resume", "BLUE token missing")

# secret scan pack
blob = ""
for p in G3.iterdir():
    if p.suffix in {".md", ".yaml", ".yml"}:
        blob += p.read_text(encoding="utf-8", errors="replace")
check(re.search(r"sk-[a-zA-Z0-9]{20,}", blob) is None, "no sk secrets", "secret-like sk- found")

# graph / agents optional soft checks
wg = (ROOT / "specs/workflow_graph.yaml").read_text(encoding="utf-8")
ag = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
check("D_G3" in wg, "graph has D_G3", "graph missing G3")
# after F lock these should pass — message clearly
if "state: APPROVED" in wg and TOKEN in wg:
    # finer: G3 block
    m = re.search(r"G3:\s*\n(?:.*\n){0,25}?state:\s*(\w+)", wg)
    if m:
        check(m.group(1) == "APPROVED", "graph G3 APPROVED", f"graph G3 state {m.group(1)}")
check(TOKEN in ag, "AGENTS mentions G3 token", "AGENTS missing token")

print("=== G3 PACK VERIFY ===")
print(f"ok={len(oks)} err={len(errs)}")
if errs:
    print("G3 VERIFY FAILED")
    for e in errs:
        print(" ERR", e)
    sys.exit(1)
print("G3 VERIFY PASSED")
for line in oks[:12]:
    print(" ", line)
print(f"  ... +{max(0, len(oks)-12)} more")
