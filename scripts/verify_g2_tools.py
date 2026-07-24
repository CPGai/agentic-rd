#!/usr/bin/env python3
"""Structural verification for locked G2 tooling pack (Steps A–F).

Runnable without pytest:

  cd /home/carlospg/workspace/agentic-rd && source .venv-hermes/bin/activate \\
    && python scripts/verify_g2_tools.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path("/home/carlospg/workspace/agentic-rd")
G2 = ROOT / "specs/g2_tools"
sys.path.insert(0, str(ROOT / "scripts"))

from g2_security.confused_deputy import audit_confused_deputy_posture, detect_tool_shadowing  # noqa: E402
from g2_security.mock_rpc import handshake_script, validate_handshake_pair  # noqa: E402
from g2_security.pin_enforce import collect_pin_violations  # noqa: E402
from g2_security.sanitize import sanitize_tool_arg, sanitize_tool_output  # noqa: E402

errs: list[str] = []
oks: list[str] = []

PH = "[" + "IP_ADDRESS" + "]"
LOOP = ".".join(["127", "0", "0", "1"])

REQUIRED_FILES = [
    G2 / "TOOL_REGISTRY.md",
    G2 / "MCP_COMPAT_MATRIX.yaml",
    G2 / "PROCUREMENT_TIER_MATRIX.yaml",
    G2 / "broker_config.yaml",
    G2 / "timeout_budgets.yaml",
    G2 / "TOOL_DISCLOSURE_POLICY.md",
    G2 / "skills_registry.json",
    G2 / "TOOL_CALL_SEQUENCE.md",
    G2 / "pins" / "npm-mcp-pins.json",
]


def check(cond: bool, ok_msg: str, err_msg: str) -> None:
    (oks if cond else errs).append(ok_msg if cond else err_msg)


for path in REQUIRED_FILES:
    check(path.is_file(), f"present {path.relative_to(ROOT)}", f"missing {path}")

if any(e.startswith("missing") for e in errs):
    print("G2 VERIFY FAILED")
    for e in errs:
        print(" ERR", e)
    sys.exit(1)

reg = (G2 / "TOOL_REGISTRY.md").read_text(encoding="utf-8")
for marker in (
    "Version:** 1.0.0",
    "G2_TOOL_REGISTRY_LOCKED_v1",
    "OPTION_2_STANDARD",
    "JSON-RPC",
    "RAG-for-tools",
    "confused deputy",
    "context7",
    "1.0.6",
):
    check(marker.casefold() in reg.casefold(), f"registry has {marker!r}", f"registry missing {marker!r}")

matrix = yaml.safe_load((G2 / "MCP_COMPAT_MATRIX.yaml").read_text(encoding="utf-8"))
broker = yaml.safe_load((G2 / "broker_config.yaml").read_text(encoding="utf-8"))
tiers = yaml.safe_load((G2 / "PROCUREMENT_TIER_MATRIX.yaml").read_text(encoding="utf-8"))
timeouts = yaml.safe_load((G2 / "timeout_budgets.yaml").read_text(encoding="utf-8"))
skills = json.loads((G2 / "skills_registry.json").read_text(encoding="utf-8"))
pins = json.loads((G2 / "pins/npm-mcp-pins.json").read_text(encoding="utf-8"))

check(matrix.get("status") == "LOCKED", "matrix LOCKED", f"matrix status {matrix.get('status')!r}")
check(matrix.get("selected_path") == "OPTION_2_STANDARD", "matrix OPTION_2", "matrix path not OPTION_2")
check(matrix.get("resume_token") == "G2_TOOL_REGISTRY_LOCKED_v1", "matrix resume", "matrix resume mismatch")
check(broker.get("resume_token") == "G2_TOOL_REGISTRY_LOCKED_v1", "broker resume", "broker resume mismatch")
check(tiers.get("status") == "LOCKED", "tier matrix LOCKED", "tier matrix not locked")
check((timeouts.get("lro") or {}).get("threshold_ms") == 10000, "LRO 10s", "LRO threshold missing")
check(skills.get("resume_token") == "G2_TOOL_REGISTRY_LOCKED_v1", "skills resume", "skills resume mismatch")

# feature gates lock check
fg = matrix.get("feature_gates", {})
check(fg.get("ap2_payments_enabled") is False, "feature_gates ap2 disabled", "ap2_payments_enabled not false")
check(fg.get("ucp_commerce_enabled") is False, "feature_gates ucp disabled", "ucp_commerce_enabled not false")
check(fg.get("a2ui_dynamic_rendering_enabled") is False, "feature_gates a2ui disabled", "a2ui_dynamic_rendering_enabled not false")
check(fg.get("runtime_execution_option") == "OPTION_2_STANDARD", "feature_gates runtime_option", "runtime_execution_option mismatch")

# pins
viol = collect_pin_violations(pins=pins, broker=broker, matrix=matrix, skills=skills)
check(not viol, "pins enforced", f"pin violations: {viol}")

# confused deputy posture
report = audit_confused_deputy_posture(broker, matrix)
check(report.blocker_count == 0, "confused-deputy blockers=0", f"CD blockers {report.as_dict()}")

# shadowing across allowlisted tools (single server today)
tool_recs = []
for s in matrix.get("mcp_servers") or []:
    if not s.get("enabled"):
        continue
    for t in s.get("tools") or []:
        tool_recs.append({"name": t.get("name"), "server_id": s.get("server_id")})
shadow = detect_tool_shadowing(tool_recs)
check(not shadow, "no tool shadowing", f"shadow {shadow}")

# sanitize behaviors
check(
    sanitize_tool_arg("query", "explain useState").ok is True,
    "sanitize allows clean query",
    "clean query rejected",
)
check(
    sanitize_tool_arg("query", "api_key=supersecretvalue").ok is False,
    "sanitize blocks secret args",
    "secret arg allowed",
)
check(
    sanitize_tool_arg("libraryId", "/facebook/react").ok,
    "libraryId ok",
    "libraryId rejected wrongly",
)
check(
    sanitize_tool_arg("libraryId", "facebook/react").ok is False,
    "libraryId requires leading slash path",
    "bad libraryId allowed",
)
sout = sanitize_tool_output("token sk-abcdefghijklmnop cleanup")
check("REDACTED" in sout.redacted, "output redacts sk-", "output redact failed")

# mock RPC handshake
for req, resp in handshake_script():
    pair_errs = validate_handshake_pair(req, resp)
    check(not pair_errs, f"rpc {req.get('method')}", f"rpc {req.get('method')} {pair_errs}")

# hygiene
blob = "\n".join(p.read_text(encoding="utf-8") for p in REQUIRED_FILES if p.suffix in {".md", ".yaml", ".yml", ".json"})
check(PH not in blob, "no IP placeholders", "leftover IP_ADDRESS placeholder")
check(
    not re.search(r"(?i)(sk-[a-z0-9]{10,}|api[_-]?key\s*[:=]\s*['\"][^'\"]+['\"])", blob),
    "no secret patterns in specs",
    "possible secret material in specs",
)
# declarative dir should not host python (except boundary assertion script)
py_files = [p for p in G2.glob("*.py") if p.name != "assert_network_boundary.py"]
check(not py_files, "g2_tools declarative-only", f"unexpected python under g2_tools: {py_files}")

# network boundary assertion
sys.path.insert(0, str(G2))
from assert_network_boundary import run_network_boundary_assertion  # noqa: E402
net_ok = run_network_boundary_assertion()
check(net_ok, "network boundary loopback enforced", "network boundary assertion failed")

# OPTION_2 ceilings
check(tiers.get("option_2_allowed_tiers") == ["T1", "T2"], "option2 tiers T1/T2", "bad option2 tiers")
check(tiers.get("option_2_forbidden_tiers") == ["T4"], "option2 forbids T4", "T4 not forbidden")

print("=" * 60)
print("G2 VERIFY", "FAILED" if errs else "PASSED")
print("=" * 60)
for m in oks:
    print(" OK ", m)
for m in errs:
    print(" ERR", m)
print(f"ok={len(oks)} err={len(errs)}")
sys.exit(1 if errs else 0)
