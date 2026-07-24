# /home/carlospg/workspace/agentic-rd/src/agentic_rd/mcp_broker/sanitizer.py              
from __future__ import annotations              

import re              
from typing import Any, Iterable              

from .errors import SECURITY_VIOLATION, BrokerError              


class PreHookSanitizer:              
    """Input firewall for tools/call arguments."""              
    
    def __init__(self, sanitizer_cfg: dict[str, Any]) -> None:              
        self.enabled = bool(sanitizer_cfg.get("enabled", True))              
        self.action = sanitizer_cfg.get("action_on_match", "reject")              
        self.max_string_length = int(sanitizer_cfg.get("max_string_length", 65536))              
        
        self._traversal = [              
            re.compile(p, re.IGNORECASE)              
            for p in sanitizer_cfg.get("path_traversal_patterns", [])              
        ]              
        shell = sanitizer_cfg.get("shell_metacharacter_pattern")              
        self._shell = re.compile(shell) if shell else None              
        self._cmd = [              
            re.compile(p) for p in sanitizer_cfg.get("command_injection_patterns", [])              
        ]              
        self._pi = [              
            re.compile(p) for p in sanitizer_cfg.get("prompt_injection_markers", [])              
        ]              
        
    def _strings(self, obj: Any, path: str = "$") -> Iterable[tuple[str, str]]:              
        if isinstance(obj, str):              
            yield path, obj              
        elif isinstance(obj, dict):              
            for k, v in obj.items():              
                yield from self._strings(v, f"{path}.{k}")              
        elif isinstance(obj, list):              
            for i, v in enumerate(obj):              
                yield from self._strings(v, f"{path}[{i}]")              
                
    def _match_any(self, text: str, patterns: list[re.Pattern[str]]) -> str | None:              
        for rx in patterns:              
            if rx.search(text):              
                return rx.pattern              
        return None              
        
    def inspect(self, arguments: dict[str, Any]) -> dict[str, Any]:              
        if not self.enabled:              
            return arguments              
            
        findings: list[str] = []              
        for path, text in self._strings(arguments):              
            if len(text) > self.max_string_length:              
                findings.append(f"{path}: string too long")              
                continue              
            lowered_space = text  # keep original for shell checks              
            t = self._match_any(text, self._traversal)              
            if t:              
                findings.append(f"{path}: path_traversal:{t}")              
            if self._shell and self._shell.search(lowered_space):              
                # Shell metacharacters only hard-fail when combined with suspicious tokens              
                # or present in command-like keys; still record for sanitize paths              
                findings.append(f"{path}: shell_metachar")              
            c = self._match_any(text, self._cmd)              
            if c:              
                findings.append(f"{path}: command_injection:{c}")              
            p = self._match_any(text, self._pi)              
            if p:              
                findings.append(f"{path}: prompt_injection:{p}")              
                
        # Harden: pure metachar presence alone does not reject unless with trash patterns              
        hard = [              
            f              
            for f in findings              
            if not f.endswith(": shell_metachar")              
            or any(              
                x in f              
                for x in ()  # placeholder — shell_metachar upgraded below              
            )              
        ]              
        # Upgrade shell_metachar to hard if other hard findings on same path or cmd verbs              
        hard = [f for f in findings if "path_traversal" in f or "command_injection" in f or "prompt_injection" in f or "too long" in f]              
        soft_shell = [f for f in findings if f.endswith(": shell_metachar")]              
        # Reject shell metacharacters in any argument for locked profile (fail closed)              
        hard.extend(soft_shell)              
        
        if hard:              
            if self.action == "reject":              
                raise BrokerError(              
                    SECURITY_VIOLATION,              
                    "Pre-hook security policy violation",              
                    data={"findings": hard[:20]},              
                )              
            # sanitize mode: scrub strings              
            return self._sanitize_tree(arguments)              
        return arguments              
        
    def _sanitize_tree(self, obj: Any) -> Any:              
        if isinstance(obj, str):              
            out = obj              
            for rx in self._traversal:              
                out = rx.sub("", out)              
            if self._shell:              
                out = self._shell.sub("", out)              
            for rx in self._cmd + self._pi:              
                out = rx.sub("", out)              
            return out              
        if isinstance(obj, dict):              
            return {k: self._sanitize_tree(v) for k, v in obj.items()}              
        if isinstance(obj, list):              
            return [self._sanitize_tree(v) for v in obj]              
        return obj              
        
        
class PostHookFilter:              
    """Scan tool results for indirect prompt injection before returning to LLM."""              
    
    def __init__(self, post_cfg: dict[str, Any], fallback_markers: list[str] | None = None) -> None:              
        self.enabled = bool(post_cfg.get("enabled", True))              
        self.action = post_cfg.get("action_on_match", "redact")              
        self.redaction_token = post_cfg.get("redaction_token", "[REDACTED_INJECTION_CANDIDATE]")              
        self.wrap_prefix = post_cfg.get("wrap_prefix", "")              
        self.wrap_suffix = post_cfg.get("wrap_suffix", "")              
        patterns = list(post_cfg.get("result_injection_patterns") or [])              
        if fallback_markers:              
            patterns.extend(fallback_markers)              
        self._rx = [re.compile(p) for p in patterns]              
        
    def filter_result_content(self, content: list[dict[str, Any]]) -> list[dict[str, Any]]:              
        if not self.enabled:              
            return content              
        out: list[dict[str, Any]] = []              
        for item in content:              
            if not isinstance(item, dict):              
                out.append(item)              
                continue              
            if item.get("type") == "text" and isinstance(item.get("text"), str):              
                text = item["text"]              
                if any(rx.search(text) for rx in self._rx):              
                    if self.action == "reject":              
                        raise BrokerError(              
                            -32001,              
                            "Post-hook blocked tool output (injection candidate)",              
                        )              
                    if self.action == "wrap":              
                        new_text = f"{self.wrap_prefix}{text}{self.wrap_suffix}"              
                    else:  # redact              
                        new_text = text              
                        for rx in self._rx:              
                            new_text = rx.sub(self.redaction_token, new_text)              
                    out.append({**item, "text": new_text})              
                else:              
                    out.append(item)              
            else:              
                out.append(item)              
        return out
