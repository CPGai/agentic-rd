"""Confused-deputy structural checks (SEC-CD-01/02, SEC-SH-01, SEC-DYN-01).

Evaluates declarative broker ACL + registry posture. No live MCP required.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Finding:
    severity: str  # critical|high|medium|low|info
    code: str
    message: str


@dataclass
class AuditReport:
    findings: list[Finding] = field(default_factory=list)

    def add(self, severity: str, code: str, message: str) -> None:
        self.findings.append(Finding(severity, code, message))

    @property
    def blocker_count(self) -> int:
        return sum(1 for f in self.findings if f.severity in {"critical", "high"})

    def as_dict(self) -> dict[str, Any]:
        return {
            "blocker_count": self.blocker_count,
            "findings": [f.__dict__ for f in self.findings],
        }


def _servers_from_broker(broker: dict) -> list[dict]:
    return list((((broker.get("acls") or {}).get("servers")) or []))


def audit_confused_deputy_posture(broker: dict, matrix: dict) -> AuditReport:
    """Flag privilege / auth gaps that enable classic confused deputy."""
    report = AuditReport()
    policy = broker.get("policy") or {}
    controls = broker.get("confused_deputy_controls") or {}
    control_ids = set(controls.get("control_ids") or [])

    if "SEC-CD-01" not in control_ids or "SEC-CD-02" not in control_ids:
        report.add("high", "CD_CONTROLS_MISSING", "broker missing SEC-CD-01/02 control_ids")

    if policy.get("public_unverified_mcp") != "deny":
        report.add(
            "critical",
            "PUBLIC_MCP_NOT_DENIED",
            "public_unverified_mcp must be deny under OPTION_2",
        )

    if "T4" not in (policy.get("denied_tiers") or []):
        report.add("high", "T4_NOT_DENIED", "T4 must be in denied_tiers for OPTION_2")

    for srv in _servers_from_broker(broker):
        sid = srv.get("server_id")
        if not srv.get("enabled", False):
            continue
        if srv.get("tier") == "T4":
            report.add("critical", "T4_ENABLED", f"enabled T4 server {sid}")
        if srv.get("authenticated") is False:
            if sid and sid not in {"context7"}:
                report.add(
                    "medium",
                    "UNAUTH_SERVER",
                    f"unauthenticated enabled server {sid} needs registry justification",
                )
            tools_allow = set(srv.get("tools_allow") or [])
            dangerous = {
                t
                for t in tools_allow
                if any(x in t.lower() for x in ("write", "delete", "exec", "pay", "shell"))
            }
            if dangerous:
                report.add(
                    "critical",
                    "UNAUTH_DANGEROUS_TOOLS",
                    f"{sid} allowlist has dangerous tools without auth: {sorted(dangerous)}",
                )

    m_servers = {
        s.get("server_id"): s
        for s in (matrix.get("mcp_servers") or [])
        if isinstance(s, dict)
    }
    b_by_id = {s.get("server_id"): s for s in _servers_from_broker(broker)}
    if "context7" in m_servers and "context7" in b_by_id:
        m_allow = set((m_servers["context7"].get("allowlist") or {}).get("tools_permitted") or [])
        b_allow = set(b_by_id["context7"].get("tools_allow") or [])
        if m_allow and b_allow and m_allow != b_allow:
            report.add(
                "high",
                "ALLOWLIST_DRIFT",
                f"context7 allowlist drift matrix={sorted(m_allow)} broker={sorted(b_allow)}",
            )

    if (broker.get("dynamic_capability_guard") or {}).get(
        "silent_tool_add_without_allowlist_amend"
    ) != "deny":
        report.add("high", "DYNAMIC_INJECT_OPEN", "silent tool add must be deny (SEC-DYN-01)")

    return report


def detect_tool_shadowing(tool_records: list[dict]) -> list[Finding]:
    """Exact name collisions across servers (SEC-SH-01 minimal)."""
    findings: list[Finding] = []
    seen: dict[str, str] = {}
    for rec in tool_records:
        name = rec.get("name")
        server = rec.get("server_id", "?")
        if not name:
            continue
        if name in seen and seen[name] != server:
            findings.append(
                Finding(
                    "high",
                    "TOOL_NAME_COLLISION",
                    f"tool {name!r} claimed by {seen[name]} and {server}",
                )
            )
        else:
            seen[name] = server
    return findings


def end_user_authz_required(server: dict, tool_name: str) -> bool:
    """SEC-CD-02: privileged tools require end-user authz, not only server capability."""
    privileged_markers = ("write", "delete", "exec", "pay", "shell", "admin", "merge", "push")
    lower = tool_name.lower()
    if server.get("authenticated") is False and any(m in lower for m in privileged_markers):
        return True
    if (server.get("tier") in {"T3", "T4"}) and any(m in lower for m in privileged_markers):
        return True
    return False
