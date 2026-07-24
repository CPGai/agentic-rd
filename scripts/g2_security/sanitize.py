"""Input / output sanitization helpers for MCP broker policy (SEC-IN-01).

Deterministic Constraint-layer primitives. No models or network I/O.
Patterns mirror broker_config.yaml deny/strip lists.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

# Case-insensitive via re.I at compile-time (inline (?i) mid-alternation fails on 3.12+).
_SECRET_FRAGMENTS = (
    r"\bapi[_-]?key\b\s*[:=]\s*\S+",
    r"\bpassword\b\s*[:=]\s*\S+",
    r"\bsecret\b\s*[:=]\s*\S+",
    r"\bbearer\s+[a-z0-9\-._~+/]+=*",
    r"\bsk-[a-z0-9]{10,}",
    r"BEGIN (?:RSA |OPENSSH )?PRIVATE KEY",
)

SECRET_RE = re.compile("|".join(f"(?:{p})" for p in _SECRET_FRAGMENTS), re.I)
HTML_ACTIVE_RE = re.compile(
    r"<\s*(script|iframe|object|embed|link|meta)\b[^>]*>.*?</\s*\1\s*>|javascript:",
    re.I | re.S,
)
PATH_TRAVERSAL_RE = re.compile(r"(^|/)\.\.(/|$)|%2e%2e", re.I)
CONTEXT7_LIBRARY_ID_RE = re.compile(r"^/[A-Za-z0-9._\-]+(/[A-Za-z0-9._\-]+)+$")


@dataclass(frozen=True)
class SanitizeResult:
    ok: bool
    reason: str = ""
    redacted: str = ""


def contains_secret_pattern(text: str) -> bool:
    return bool(text) and SECRET_RE.search(text) is not None


def sanitize_tool_arg(
    field: str, value: str, *, deny_secret_fields: bool = True
) -> SanitizeResult:
    """Validate a single string tool argument before tools/call forward."""
    if value is None:
        return SanitizeResult(False, "null_value")
    if not isinstance(value, str):
        return SanitizeResult(False, "non_string")
    if PATH_TRAVERSAL_RE.search(value):
        return SanitizeResult(False, "path_traversal")
    if deny_secret_fields and contains_secret_pattern(value):
        return SanitizeResult(False, "secret_pattern_in_args")
    if field == "libraryId" and value and not CONTEXT7_LIBRARY_ID_RE.match(value):
        return SanitizeResult(False, "invalid_library_id")
    return SanitizeResult(True, "", value)


def sanitize_tool_output(text: str, *, max_chars: int = 24000) -> SanitizeResult:
    """Redact secret-like and active HTML content from tool observations."""
    if text is None:
        return SanitizeResult(False, "null_output")
    if not isinstance(text, str):
        text = str(text)
    redacted = SECRET_RE.sub("[REDACTED]", text)
    redacted = HTML_ACTIVE_RE.sub("[STRIPPED_ACTIVE_HTML]", redacted)
    if len(redacted) > max_chars:
        redacted = redacted[:max_chars] + "...[TRUNCATED]"
    tainted = redacted != text or contains_secret_pattern(text)
    return SanitizeResult(True, "tainted" if tainted else "clean", redacted)


def any_arg_rejects(args: dict, fields: Iterable[str] | None = None) -> list[str]:
    """Return list of field:reason for args that fail sanitize_tool_arg."""
    rejects: list[str] = []
    items = args.items() if fields is None else ((f, args.get(f, "")) for f in fields)
    for field, value in items:
        if not isinstance(value, str):
            continue
        res = sanitize_tool_arg(field, value)
        if not res.ok:
            rejects.append(f"{field}:{res.reason}")
    return rejects
