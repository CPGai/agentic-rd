# /home/carlospg/workspace/agentic-rd/src/agentic_rd/mcp_broker/errors.py              
from __future__ import annotations              
              
from typing import Any, Optional              
              
              
class BrokerError(Exception):              
    def __init__(self, code: int, message: str, data: Any = None) -> None:              
        super().__init__(message)              
        self.code = code              
        self.message = message              
        self.data = data              
              
    def to_jsonrpc(self, req_id: Any) -> dict[str, Any]:              
        err: dict[str, Any] = {"code": self.code, "message": self.message}              
        if self.data is not None:              
            err["data"] = self.data              
        return {"jsonrpc": "2.0", "id": req_id, "error": err}              
              
              
def jsonrpc_error(req_id: Any, code: int, message: str, data: Any = None) -> dict[str, Any]:              
    return BrokerError(code, message, data).to_jsonrpc(req_id)              
              
              
# Standard codes              
PARSE_ERROR = -32700              
INVALID_REQUEST = -32600              
METHOD_NOT_FOUND = -32601              
INVALID_PARAMS = -32602              
INTERNAL_ERROR = -32603              
SECURITY_VIOLATION = -32000              
CONTENT_BLOCKED = -32001
