# /home/carlospg/workspace/agentic-rd/src/agentic_rd/mcp_broker/schema_validator.py              
from __future__ import annotations              
              
from typing import Any              
              
from .errors import INVALID_PARAMS, INVALID_REQUEST, PARSE_ERROR, BrokerError              
              
              
def parse_jsonrpc_request(payload: Any) -> dict[str, Any]:              
    if not isinstance(payload, dict):              
        raise BrokerError(INVALID_REQUEST, "JSON-RPC request must be an object")              
    # Reject unknown top-level keys (strict envelope)              
    allowed = {"jsonrpc", "method", "params", "id"}              
    extra = set(payload.keys()) - allowed              
    if extra:              
        raise BrokerError(INVALID_REQUEST, f"Unknown top-level fields: {sorted(extra)}")              
    if payload.get("jsonrpc") != "2.0":              
        raise BrokerError(INVALID_REQUEST, "jsonrpc must be \"2.0\"")              
    method = payload.get("method")              
    if not isinstance(method, str) or not method:              
        raise BrokerError(INVALID_REQUEST, "method must be non-empty string")              
    if "id" not in payload:              
        # notifications not used for tools/list|call in this broker — require id              
        raise BrokerError(INVALID_REQUEST, "id is required")              
    rid = payload["id"]              
    if not isinstance(rid, (str, int)) and rid is not None:              
        raise BrokerError(INVALID_REQUEST, "id must be string, number, or null")              
    params = payload.get("params", {})              
    if params is None:              
        params = {}              
    if not isinstance(params, dict):              
        raise BrokerError(INVALID_PARAMS, "params must be an object")              
    return {              
        "jsonrpc": "2.0",              
        "method": method,              
        "id": rid,              
        "params": params,              
        "raw": payload,              
    }              
              
              
def _check_type(value: Any, expected: str) -> bool:              
    mapping = {              
        "string": lambda v: isinstance(v, str),              
        "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),              
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),              
        "boolean": lambda v: isinstance(v, bool),              
        "object": lambda v: isinstance(v, dict),              
        "array": lambda v: isinstance(v, list),              
        "null": lambda v: v is None,              
    }              
    fn = mapping.get(expected)              
    return bool(fn and fn(value))              
              
              
def validate_against_json_schema(instance: Any, schema: dict[str, Any], path: str = "$") -> None:              
    """Minimal strict JSON Schema subset validator (object/array/string/number/integer/boolean).              
    Enforces additionalProperties=false by default for objects when not specified.              
    """              
    if not isinstance(schema, dict):              
        raise BrokerError(INVALID_PARAMS, f"{path}: invalid schema")              
              
    if "const" in schema and instance != schema["const"]:              
        raise BrokerError(INVALID_PARAMS, f"{path}: const mismatch")              
              
    if "enum" in schema and instance not in schema["enum"]:              
        raise BrokerError(INVALID_PARAMS, f"{path}: value not in enum")              
              
    schema_type = schema.get("type")              
    if schema_type:              
        types = schema_type if isinstance(schema_type, list) else [schema_type]              
        if not any(_check_type(instance, t) for t in types):              
            raise BrokerError(INVALID_PARAMS, f"{path}: expected type {schema_type}")              
              
    if isinstance(instance, dict):              
        props = schema.get("properties") or {}              
        required = schema.get("required") or []              
        additional = schema.get("additionalProperties", False)              
        for r in required:              
            if r not in instance:              
                raise BrokerError(INVALID_PARAMS, f"{path}: missing required property '{r}'")              
        for k, v in instance.items():              
            if k in props:              
                validate_against_json_schema(v, props[k], f"{path}.{k}")              
            else:              
                if additional is False:              
                    raise BrokerError(              
                        INVALID_PARAMS,              
                        f"{path}: additional property '{k}' not allowed",              
                    )              
                if isinstance(additional, dict):              
                    validate_against_json_schema(v, additional, f"{path}.{k}")              
              
    if isinstance(instance, list):              
        if "items" in schema:              
            item_schema = schema["items"]              
            for i, item in enumerate(instance):              
                validate_against_json_schema(item, item_schema, f"{path}[{i}]")              
        min_items = schema.get("minItems")              
        max_items = schema.get("maxItems")              
        if min_items is not None and len(instance) < min_items:              
            raise BrokerError(INVALID_PARAMS, f"{path}: fewer than minItems")              
        if max_items is not None and len(instance) > max_items:              
            raise BrokerError(INVALID_PARAMS, f"{path}: more than maxItems")              
              
    if isinstance(instance, str):              
        mn = schema.get("minLength")              
        mx = schema.get("maxLength")              
        if mn is not None and len(instance) < mn:              
            raise BrokerError(INVALID_PARAMS, f"{path}: shorter than minLength")              
        if mx is not None and len(instance) > mx:              
            raise BrokerError(INVALID_PARAMS, f"{path}: longer than maxLength")              
        pattern = schema.get("pattern")              
        if pattern:              
            import re              
            if not re.search(pattern, instance):              
                raise BrokerError(INVALID_PARAMS, f"{path}: pattern mismatch")              
              
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):              
        mn = schema.get("minimum")              
        mx = schema.get("maximum")              
        if mn is not None and instance < mn:              
            raise BrokerError(INVALID_PARAMS, f"{path}: below minimum")              
        if mx is not None and instance > mx:              
            raise BrokerError(INVALID_PARAMS, f"{path}: above maximum")
