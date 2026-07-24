# /home/carlospg/workspace/agentic-rd/src/agentic_rd/mcp_broker/disclosure.py
from __future__ import annotations

import re
from typing import Any, Sequence
from .models import ToolSpec


class ProgressiveDisclosure:
    """Progressive Tool Disclosure (RAG-for-Tools) Policy Scorer & Selector."""

    def __init__(self, disc_cfg: dict[str, Any]) -> None:
        self.cfg = disc_cfg.get("disclosure") or {}
        self.scoring_cfg = disc_cfg.get("scoring") or {}
        self.mode = self.cfg.get("mode", "intent_threshold")
        self.default_max_tools = int(self.cfg.get("default_max_tools", 8))
        self.score_threshold = float(self.cfg.get("score_threshold", 0.22))
        self.always_include = self.cfg.get("always_include") or []
        self.never_include = self.cfg.get("never_include") or []

        # Scoring parameters
        self.title_weight = float(self.scoring_cfg.get("title_weight", 2.5))
        self.description_weight = float(self.scoring_cfg.get("description_weight", 1.0))
        self.tag_weight = float(self.scoring_cfg.get("tag_weight", 1.75))
        self.name_weight = float(self.scoring_cfg.get("name_weight", 3.0))
        self.min_token_length = int(self.scoring_cfg.get("min_token_length", 2))
        self.stopwords = set(self.scoring_cfg.get("stopwords") or [])
        self.synonyms: dict[str, list[str]] = self.scoring_cfg.get("synonyms") or {}

    def _tokenize(self, text: str) -> list[str]:
        if not text:
            return []
        words = re.findall(r"\b[a-zA-Z0-9_\-\.]+\b", text.lower())
        tokens = []
        for w in words:
            if len(w) >= self.min_token_length and w not in self.stopwords:
                tokens.append(w)
        return tokens

    def _expand_tokens(self, tokens: list[str]) -> set[str]:
        expanded = set(tokens)
        for token in tokens:
            for canon, syn_list in self.synonyms.items():
                if token == canon or token in syn_list:
                    expanded.add(canon)
                    expanded.update(syn_list)
        return expanded

    def _wildcard_match(self, name: str, pattern: str) -> bool:
        regex_pat = re.escape(pattern).replace(r"\*", ".*")
        return bool(re.match(f"^{regex_pat}$", name, re.IGNORECASE))

    def _is_never_include(self, tool: ToolSpec) -> bool:
        name = tool.name
        qname = tool.qualified_name
        for pattern in self.never_include:
            if self._wildcard_match(name, pattern) or self._wildcard_match(qname, pattern):
                return True
        return False

    def _is_always_include(self, tool: ToolSpec) -> bool:
        name = tool.name
        qname = tool.qualified_name
        for pattern in self.always_include:
            if self._wildcard_match(name, pattern) or self._wildcard_match(qname, pattern):
                return True
        return False

    def score_tool(self, tool: ToolSpec, intent_tokens: set[str]) -> float:
        if not intent_tokens:
            return 0.0

        # Tokenize tool components
        name_tokens = self._tokenize(tool.name)
        desc_tokens = self._tokenize(tool.description)
        tag_tokens = []
        for t in tool.tags:
            tag_tokens.extend(self._tokenize(t))

        score = 0.0

        # Name overlap
        name_overlap = intent_tokens.intersection(name_tokens)
        if name_overlap:
            score += self.name_weight * (len(name_overlap) / max(len(name_tokens), 1))

        # Description overlap
        desc_overlap = intent_tokens.intersection(desc_tokens)
        if desc_overlap:
            score += self.description_weight * (len(desc_overlap) / max(len(desc_tokens), 1))

        # Tags overlap
        tag_overlap = intent_tokens.intersection(tag_tokens)
        if tag_overlap:
            score += self.tag_weight * (len(tag_overlap) / max(len(tag_tokens), 1))

        return score

    def disclose(self, tools: Sequence[ToolSpec], intent: str) -> list[ToolSpec]:
        # Filter out never_include
        candidates = [t for t in tools if not self._is_never_include(t)]

        if self.mode == "allowlist_only":
            return [t for t in candidates if self._is_always_include(t)]
        elif self.mode == "all_blocked_default":
            return []

        # intent_threshold mode
        intent_tokens = self._expand_tokens(self._tokenize(intent))

        scored: list[tuple[float, ToolSpec]] = []
        for t in candidates:
            if self._is_always_include(t):
                # Put at max score to ensure inclusion
                scored.append((float("inf"), t))
            else:
                score = self.score_tool(t, intent_tokens)
                if score >= self.score_threshold:
                    scored.append((score, t))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)

        selected = [t for _, t in scored[:self.default_max_tools]]
        return selected
