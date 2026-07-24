# /home/carlospg/workspace/agentic-rd/src/agentic_rd/mcp_broker/broker.py
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Callable, Optional

from .acl import SecurityACL
from .config_loader import (
    ROOT,
    ensure_acl_integrity,
    load_broker_config,
    load_disclosure_policy,
    load_security_acl,
)
from .disclosure import ProgressiveDisclosure
from .errors import (
    CONTENT_BLOCKED,
    INTERNAL_ERROR,
    INVALID_PARAMS,
    METHOD_NOT_FOUND,
    SECURITY_VIOLATION,
    BrokerError,
    jsonrpc_error,
)
from .models import DispatchResult, ToolSpec
from .sanitizer import PostHookFilter, PreHookSanitizer
from .schema_validator import parse_jsonrpc_request, validate_against_json_schema

UpstreamHandler = Callable[[str, str, dict[str, Any]], DispatchResult]


class McpSecurityBroker:
    """Mandatory interceptor between LLM and MCP servers."""

    def __init__(
        self,
        root: Path | None = None,
        catalog: list[ToolSpec] | None = None,
        upstream: UpstreamHandler | None = None,
    ) -> None:
        self.root = root or ROOT
        self.cfg = load_broker_config(self.root)
        self.acl_cfg = load_security_acl(self.root)
        self.disc_cfg = load_disclosure_policy(self.root)
        self.acl_digest = ensure_acl_integrity(self.acl_cfg, self.root)

        self.acl = SecurityACL(self.acl_cfg)
        self.sanitizer = PreHookSanitizer(self.cfg.get("sanitizer") or {})
        post_cfg = self.cfg.get("post_hook") or {}
        self.post_filter = PostHookFilter(
            post_cfg,
            fallback_markers=self.cfg.get("sanitizer", {}).get("prompt_injection_markers"),
        )
        self.catalog = catalog or []
        self.upstream = upstream

    def _log_audit(
        self,
        method: str,
        params: dict[str, Any],
        decision: str,
        req_id: Any,
        is_error: bool = False,
        latency_ms: float = 0.0,
        server_id: str | None = None,
        tool_name: str | None = None,
    ) -> None:
        audit_cfg = self.cfg.get("audit") or {}
        if not audit_cfg.get("enabled", True):
            return

        if decision == "deny" and not audit_cfg.get("log_denies", True):
            return
        if decision == "allow" and not audit_cfg.get("log_all_calls", True):
            return

        log_path = self.root / self.cfg.get("paths", {}).get("audit_log", "var/log/mcp_broker_audit.jsonl")
        log_path.parent.mkdir(parents=True, exist_ok=True)

        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tenant": "local-dev",
            "method": method,
            "id": req_id,
            "decision": decision,
            "is_error": is_error,
            "latency_ms": latency_ms,
        }
        if server_id:
            entry["server_id"] = server_id
        if tool_name:
            entry["tool_name"] = tool_name

        if audit_cfg.get("include_payload_hash", True):
            payload_str = json.dumps(params, sort_keys=True)
            entry["args_hash"] = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def handle_jsonrpc(self, payload: Any) -> dict[str, Any]:
        start_time = time.perf_counter()
        req_id = None
        method = "unknown"
        server_id = None
        tool_name = None
        try:
            req = parse_jsonrpc_request(payload)
            req_id = req["id"]
            method = req["method"]
            params = req["params"]

            if method == "initialize":
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "serverInfo": {"name": "mcp-security-broker", "version": "3.0.0"}
                    }
                }
                self._log_audit(method, params, "allow", req_id, latency_ms=(time.perf_counter() - start_time) * 1000)
                return res
            elif method == "ping":
                res = {"jsonrpc": "2.0", "id": req_id, "result": {}}
                self._log_audit(method, params, "allow", req_id, latency_ms=(time.perf_counter() - start_time) * 1000)
                return res
            elif method == "tools/list":
                intent = None
                for k in self.disc_cfg.get("intent_extraction", {}).get("intent_param_keys", []):
                    if k in params:
                        intent = params[k]
                        break
                if not intent:
                    intent = self.disc_cfg.get("intent_extraction", {}).get("fallback_intent", "general safe information retrieval")

                allowed_tools = self.acl.filter_known_tools(self.catalog)
                disclosure = ProgressiveDisclosure(self.disc_cfg)
                disclosed_tools = disclosure.disclose(allowed_tools, intent)

                include_schema = self.disc_cfg.get("response_shaping", {}).get("include_input_schema", True)
                tools_decl = [t.public_declaration(include_input_schema=include_schema) for t in disclosed_tools]

                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": tools_decl
                    }
                }
                self._log_audit(method, params, "allow", req_id, latency_ms=(time.perf_counter() - start_time) * 1000)
                return res
            elif method == "tools/call":
                name = params.get("name")
                arguments = params.get("arguments") or {}
                if not name:
                    raise BrokerError(INVALID_PARAMS, "name is required")

                if "." in name:
                    server_id, tool_name = name.split(".", 1)
                else:
                    canon = self.acl.canonical.get(name)
                    if not canon:
                        raise BrokerError(METHOD_NOT_FOUND, f"Method not found: {name}")
                    server_id, tool_name = canon.split(".", 1)

                # Check ACL tool call authorization
                try:
                    self.acl.assert_call_allowed(server_id, tool_name)
                except BrokerError as err:
                    self._log_audit(method, params, "deny", req_id, is_error=True, server_id=server_id, tool_name=tool_name)
                    raise

                tool_spec = next((t for t in self.catalog if t.server_id == server_id and t.name == tool_name), None)
                if not tool_spec:
                    raise BrokerError(METHOD_NOT_FOUND, f"Tool spec not found: {server_id}.{tool_name}")

                # Validate inputs against schema
                validate_against_json_schema(arguments, tool_spec.input_schema)

                # Enforce ACL tool constraints
                self.acl.enforce_constraints(server_id, tool_name, arguments)

                # Sanitize arguments (pre-hook)
                sanitized_args = self.sanitizer.inspect(arguments)

                if not self.upstream:
                    raise BrokerError(INTERNAL_ERROR, "No upstream dispatcher configured")

                res = self.upstream(server_id, tool_name, sanitized_args)

                # Post-hook output filter
                filtered_content = self.post_filter.filter_result_content(res.content)

                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": filtered_content
                    }
                }
                if res.is_error:
                    resp["result"]["isError"] = True

                self._log_audit(
                    method,
                    params,
                    "allow",
                    req_id,
                    is_error=res.is_error,
                    latency_ms=(time.perf_counter() - start_time) * 1000,
                    server_id=server_id,
                    tool_name=tool_name
                )
                return resp
            else:
                raise BrokerError(METHOD_NOT_FOUND, f"Method not found: {method}")

        except BrokerError as err:
            err_resp = err.to_jsonrpc(req_id)
            self._log_audit(
                method,
                payload.get("params", {}) if isinstance(payload, dict) else {},
                "deny",
                req_id,
                is_error=True,
                latency_ms=(time.perf_counter() - start_time) * 1000,
                server_id=server_id,
                tool_name=tool_name
            )
            return err_resp
        except Exception as exc:
            err_resp = jsonrpc_error(req_id, INTERNAL_ERROR, str(exc))
            self._log_audit(
                method,
                payload.get("params", {}) if isinstance(payload, dict) else {},
                "deny",
                req_id,
                is_error=True,
                latency_ms=(time.perf_counter() - start_time) * 1000,
                server_id=server_id,
                tool_name=tool_name
            )
            return err_resp
