"""Dependency / MCP package pin enforcement (SEC-SLOP-01 / broker pin policy)."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

WORKSPACE = Path("/home/carlospg/workspace/agentic-rd")
PINS_PATH = WORKSPACE / "specs/g2_tools/pins/npm-mcp-pins.json"
BROKER_PATH = WORKSPACE / "specs/g2_tools/broker_config.yaml"
MATRIX_PATH = WORKSPACE / "specs/g2_tools/MCP_COMPAT_MATRIX.yaml"
SKILLS_REG = WORKSPACE / "specs/g2_tools/skills_registry.json"

FLOATING_NPX_RE = re.compile(r"@upstash/context7-mcp(?!@)")


def load_pins(path: Path = PINS_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} root must be mapping")
    return data


def expected_context7_pin(pins: dict[str, Any] | None = None) -> dict[str, str]:
    pins = pins or load_pins()
    for row in pins.get("pins") or []:
        if row.get("server_id") == "context7":
            return {"package": row["package"], "version": str(row["version"])}
    raise KeyError("context7 pin missing from npm-mcp-pins.json")


def collect_pin_violations(
    *,
    pins: dict[str, Any] | None = None,
    broker: dict[str, Any] | None = None,
    matrix: dict[str, Any] | None = None,
    skills: dict[str, Any] | None = None,
) -> list[str]:
    """Return human-readable violation strings (empty == pass)."""
    pins = pins or load_pins()
    broker = broker or load_yaml(BROKER_PATH)
    matrix = matrix or load_yaml(MATRIX_PATH)
    skills = skills or json.loads(SKILLS_REG.read_text(encoding="utf-8"))

    violations: list[str] = []
    if pins.get("policy", {}).get("allow_floating_npx") is not False:
        violations.append("pins.policy.allow_floating_npx must be false")
    if pins.get("policy", {}).get("enforce") is not True:
        violations.append("pins.policy.enforce must be true")

    exp = expected_context7_pin(pins)
    pkg, ver = exp["package"], exp["version"]

    servers = ((broker.get("acls") or {}).get("servers")) or []
    c7b = next((s for s in servers if s.get("server_id") == "context7"), None)
    if not c7b:
        violations.append("broker missing context7 server acl")
    else:
        pin = c7b.get("pin") or {}
        if pin.get("package") != pkg or str(pin.get("version")) != ver:
            violations.append(f"broker pin mismatch {pin} != {pkg}@{ver}")
        if pin.get("enforce") is not True:
            violations.append("broker pin.enforce must be true")

    c7m = next(
        (s for s in (matrix.get("mcp_servers") or []) if s.get("server_id") == "context7"),
        None,
    )
    if not c7m:
        violations.append("matrix missing context7")
    else:
        package = c7m.get("package") or {}
        if package.get("name") != pkg or str(package.get("version_pin")) != ver:
            violations.append(f"matrix package pin mismatch {package}")
        args = (c7m.get("transport") or {}).get("args") or []
        joined = " ".join(str(a) for a in args)
        if f"{pkg}@{ver}" not in joined:
            violations.append(f"matrix transport.args must include {pkg}@{ver}, got {args}")
        if FLOATING_NPX_RE.search(joined) and f"@{ver}" not in joined:
            violations.append("matrix still references floating context7 package")
        if matrix.get("environment_audit", {}).get("floating_version_pins"):
            violations.append("matrix.environment_audit.floating_version_pins must be empty")

    bridges = skills.get("mcp_bridges") or []
    c7s = next((b for b in bridges if b.get("server_id") == "context7"), None)
    if not c7s:
        violations.append("skills_registry missing context7 mcp_bridge")
    elif str(c7s.get("version_pin")) != ver or c7s.get("package") != pkg:
        violations.append(f"skills_registry pin mismatch {c7s}")

    return violations


def pins_enforced_ok() -> bool:
    return not collect_pin_violations()
