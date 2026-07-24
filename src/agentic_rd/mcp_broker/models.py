from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class ToolSpec:
    server_id: str
    name: str
    description: str = ""
    input_schema: dict[str, Any] = field(default_factory=lambda: {"type": "object", "properties": {}})
    tags: tuple[str, ...] = ()

    @property
    def qualified_name(self) -> str:
        return f"{self.server_id}.{self.name}"

    def public_declaration(self, include_input_schema: bool = True) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "server": self.server_id,
        }
        if include_input_schema:
            d["inputSchema"] = self.input_schema
        return d


@dataclass
class BrokerRequest:
    raw: dict[str, Any]
    jsonrpc: str
    method: str
    id: Any
    params: dict[str, Any]


@dataclass
class DispatchResult:
    content: list[dict[str, Any]]
    is_error: bool = False
    raw: Optional[dict[str, Any]] = None
