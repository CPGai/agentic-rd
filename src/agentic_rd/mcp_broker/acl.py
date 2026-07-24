# /home/carlospg/workspace/agentic-rd/src/agentic_rd/mcp_broker/acl.py              
from __future__ import annotations              

import os              
from pathlib import Path              
from typing import Any              

from .errors import METHOD_NOT_FOUND, SECURITY_VIOLATION, BrokerError              
from .models import ToolSpec              


class SecurityACL:              
    def __init__(self, acl_cfg: dict[str, Any]) -> None:              
        self.policy = acl_cfg.get("policy") or {}              
        self.allowlist: dict[str, list[str]] = {              
            k: list(v) for k, v in (acl_cfg.get("allowlist") or {}).items()              
        }              
        self.canonical: dict[str, str] = dict(acl_cfg.get("canonical_registry") or {})              
        self.blocked_namespaces = [n.lower() for n in (acl_cfg.get("blocked_namespaces") or [])]              
        self.constraints: dict[str, dict[str, Any]] = dict(acl_cfg.get("tool_constraints") or {})              
        self.default_deny = self.policy.get("default_action", "deny") == "deny"              
        
    def is_tool_allowed(self, server_id: str, tool_name: str) -> bool:              
        if self._namespace_blocked(tool_name) or self._namespace_blocked(server_id):              
            return False              
        allowed = self.allowlist.get(server_id, [])              
        return tool_name in allowed              
        
    def _namespace_blocked(self, name: str) -> bool:              
        head = name.split(".", 1)[0].lower()              
        return head in self.blocked_namespaces or name.lower() in self.blocked_namespaces              
        
    def assert_call_allowed(self, server_id: str, tool_name: str) -> None:              
        # Tool shadowing: if bare name maps to a different server — deny mismatch              
        canon = self.canonical.get(tool_name)              
        if canon:              
            exp_server, exp_tool = canon.split(".", 1)              
            if exp_server != server_id or exp_tool != tool_name:              
                raise BrokerError(              
                    METHOD_NOT_FOUND,              
                    "Method not found / Unregistered deputy",              
                    data={"reason": "tool_shadowing_denied", "canonical": canon},              
                )              
        if not self.is_tool_allowed(server_id, tool_name):              
            raise BrokerError(              
                METHOD_NOT_FOUND,              
                self.policy.get("unregistered_message", "Method not found / Unregistered deputy"),              
                data={"server": server_id, "tool": tool_name},              
            )              
            
    def enforce_constraints(self, server_id: str, tool_name: str, arguments: dict[str, Any]) -> None:              
        key = f"{server_id}.{tool_name}"              
        c = self.constraints.get(key)              
        if not c:              
            return              
        # Path roots              
        path_keys = ("path", "file", "filepath", "directory", "dir")              
        allowed_roots = [str(Path(p).resolve()) for p in c.get("allowed_roots", [])]              
        denied_subs = c.get("denied_path_substrings") or []              
        for pk in path_keys:              
            if pk not in arguments:              
                continue              
            raw = arguments[pk]              
            if not isinstance(raw, str):              
                raise BrokerError(SECURITY_VIOLATION, f"{pk} must be string")              
            # Expand / resolve intended path              
            try:              
                resolved = str(Path(raw).resolve())              
            except Exception as exc:  # noqa: BLE001              
                raise BrokerError(SECURITY_VIOLATION, f"invalid path: {exc}") from exc              
            if allowed_roots:              
                if not any(resolved == r or resolved.startswith(r + os.sep) for r in allowed_roots):              
                    raise BrokerError(              
                        SECURITY_VIOLATION,              
                        "path outside allowed roots",              
                        data={"path": raw},              
                    )              
            for bad in denied_subs:              
                if bad in resolved or bad in raw:              
                    raise BrokerError(              
                        SECURITY_VIOLATION,              
                        "path matches denied substring",              
                        data={"path": raw, "denied": bad},              
                    )              
        if "max_bytes" in c and "path" in arguments:              
            # checked at dispatcher when reading; record only here              
            pass              
        if "max_message_length" in c and "message" in arguments:              
            msg = arguments.get("message", "")              
            if isinstance(msg, str) and len(msg) > int(c["max_message_length"]):              
                raise BrokerError(SECURITY_VIOLATION, "message exceeds max_message_length")              
        if "max_query_length" in c:              
            for qk in ("query", "libraryName", "library_name"):              
                if qk in arguments and isinstance(arguments[qk], str):              
                    if len(arguments[qk]) > int(c["max_query_length"]):              
                        raise BrokerError(SECURITY_VIOLATION, "query too long")              
                        
    def filter_known_tools(self, tools: list[ToolSpec]) -> list[ToolSpec]:              
        out: list[ToolSpec] = []              
        for t in tools:              
            if self.is_tool_allowed(t.server_id, t.name) and not self._namespace_blocked(t.name):              
                out.append(t)              
        return out
