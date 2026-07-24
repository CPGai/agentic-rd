# /home/carlospg/workspace/agentic-rd/src/agentic_rd/mcp_broker/config_loader.py              
from __future__ import annotations              
              
import hashlib              
import json              
from pathlib import Path              
from typing import Any              
              
import yaml              
              
              
ROOT = Path("/home/carlospg/workspace/agentic-rd")              
              
              
def _read_yaml(path: Path) -> dict[str, Any]:              
    if not path.is_file():              
        raise FileNotFoundError(f"Missing config: {path}")              
    with path.open("r", encoding="utf-8") as fh:              
        data = yaml.safe_load(fh)              
    if not isinstance(data, dict):              
        raise ValueError(f"Config root must be mapping: {path}")              
    return data              
              
              
def load_broker_config(root: Path | None = None) -> dict[str, Any]:              
    root = root or ROOT              
    return _read_yaml(root / "specs/g2_tools/broker_config.yaml")              
              
              
def load_disclosure_policy(root: Path | None = None) -> dict[str, Any]:              
    root = root or ROOT              
    return _read_yaml(root / "specs/g2_tools/disclosure_policy.yaml")              
              
              
def load_security_acl(root: Path | None = None) -> dict[str, Any]:              
    root = root or ROOT              
    return _read_yaml(root / "specs/g2_tools/security_acl.yaml")              
              
              
def canonical_acl_payload(acl: dict[str, Any]) -> bytes:              
    body = {              
        "allowlist": acl.get("allowlist", {}),              
        "canonical_registry": acl.get("canonical_registry", {}),              
        "blocked_namespaces": acl.get("blocked_namespaces", []),              
        "tool_constraints": acl.get("tool_constraints", {}),              
    }              
    return json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")              
              
              
def acl_sha256(acl: dict[str, Any]) -> str:              
    return hashlib.sha256(canonical_acl_payload(acl)).hexdigest()              
              
              
def ensure_acl_integrity(acl: dict[str, Any], root: Path | None = None) -> str:              
    """Pin or verify ACL hash under var/mcp_broker_acl.sha256."""              
    root = root or ROOT              
    pin = root / "var" / "mcp_broker_acl.sha256"              
    pin.parent.mkdir(parents=True, exist_ok=True)              
    digest = acl_sha256(acl)              
    mode = (acl.get("allowlist_integrity") or {}).get("pin_mode", "self_hash_file")              
    if mode == "self_hash_file":              
        if not pin.exists():              
            pin.write_text(digest + "\n", encoding="utf-8")              
        else:              
            expected = pin.read_text(encoding="utf-8").strip()              
            if expected != digest:              
                raise RuntimeError(              
                    f"ACL integrity mismatch: file={expected} computed={digest}. "              
                    "Refuse to start (G2 lock)."              
                )              
    return digest
