"""Mock MCP JSON-RPC 2.0 handshake shapes (no network).

Validates envelopes for initialize -> tools/list -> tools/call
per WP-F2 baseline and MCP_COMPAT_MATRIX protocol_baseline.
"""
from __future__ import annotations

from typing import Any


REQUIRED_JSONRPC = "2.0"


def is_request(msg: dict[str, Any]) -> bool:
    return (
        isinstance(msg, dict)
        and msg.get("jsonrpc") == REQUIRED_JSONRPC
        and "method" in msg
        and "id" in msg
    )


def is_notification(msg: dict[str, Any]) -> bool:
    return (
        isinstance(msg, dict)
        and msg.get("jsonrpc") == REQUIRED_JSONRPC
        and "method" in msg
        and "id" not in msg
    )


def is_success(msg: dict[str, Any], *, expect_id: Any = None) -> bool:
    ok = (
        isinstance(msg, dict)
        and msg.get("jsonrpc") == REQUIRED_JSONRPC
        and "result" in msg
        and "error" not in msg
        and "id" in msg
    )
    if expect_id is not None and msg.get("id") != expect_id:
        return False
    return ok


def is_error(msg: dict[str, Any]) -> bool:
    if not (isinstance(msg, dict) and msg.get("jsonrpc") == REQUIRED_JSONRPC and "error" in msg):
        return False
    err = msg["error"]
    return isinstance(err, dict) and "code" in err and "message" in err


def is_tool_execution_error(result_msg: dict[str, Any]) -> bool:
    """Tool-layer failure: result present with isError true (WP-F2 p.29-30)."""
    if not is_success(result_msg):
        return False
    result = result_msg.get("result") or {}
    return bool(result.get("isError") is True)


def mock_initialize_ok(req_id: int = 1) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "protocolVersion": "2025-06-18",
            "capabilities": {"tools": {"listChanged": True}},
            "serverInfo": {"name": "mock", "version": "0.0.0"},
        },
    }


def mock_tools_list(req_id: int = 2, tools: list[dict] | None = None) -> dict[str, Any]:
    tools = tools or [
        {
            "name": "resolve-library-id",
            "description": "Resolve library",
            "inputSchema": {"type": "object", "properties": {}},
        }
    ]
    return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools}}


def mock_tools_call_ok(req_id: int = 3, text: str = "ok") -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {"content": [{"type": "text", "text": text}], "isError": False},
    }


def mock_unknown_tool_error(req_id: int = 3) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {
            "code": -32602,
            "message": "Unknown tool: invalid_tool_name. Check tools/list.",
        },
    }


def handshake_script() -> list[tuple[dict, dict]]:
    """Ordered (request, response) pairs for structural tests."""
    return [
        (
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "agentic-rd-test", "version": "1.0.0"},
                },
            },
            mock_initialize_ok(1),
        ),
        (
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            mock_tools_list(2),
        ),
        (
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "resolve-library-id",
                    "arguments": {"libraryName": "react"},
                },
            },
            mock_tools_call_ok(3),
        ),
    ]


def validate_handshake_pair(req: dict, resp: dict) -> list[str]:
    errs: list[str] = []
    if not is_request(req):
        errs.append("invalid_request")
    if "error" in resp:
        if not is_error(resp):
            errs.append("invalid_error_response")
    else:
        if not is_success(resp, expect_id=req.get("id")):
            errs.append("invalid_success_response")
    if req.get("id") != resp.get("id") and "error" not in resp:
        errs.append("id_mismatch")
    return errs
