#!/usr/bin/env python3
"""G3 structural helpers: assembly order, L1 budgets, co-load, compaction (no runtime I/O)."""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Iterable

ASSEMBLY_ORDER = (
    "static_pack",
    "skills_l1_scan",
    "skills_l2_l3_on_trigger",
    "tools_rag_for_tools",
    "knowledge",
    "memory_window",
)

PRECEDENCE_RANK = {
    "constraint_catalog_safety_hooks": 0,
    "root_AGENTS_md_and_sandbox": 1,
    "explicit_user_instruction_this_turn": 2,
    "module_tightener_GEMINI_CLAUDE": 3,
    "skill_l2": 4,
    "skill_l3": 5,
    "memory_suggestions_advisory": 6,
    "model_priors": 7,
}


def estimate_tokens(text: str) -> int:
    """Rough hedge: ~4 chars/token; empty → 0."""
    if not text:
        return 0
    return max(1, math.ceil(len(text) / 4))


_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.S)
_NAME = re.compile(r"^name:\s*(.+)$", re.M)
_DESC = re.compile(r"^description:\s*(.+?)(?=^\w|\Z)", re.M | re.S)


def parse_skill_l1(skill_md: str) -> tuple[str, str, bool]:
    """Return (name, description, has_frontmatter)."""
    m = _FRONTMATTER.match(skill_md.lstrip("\ufeff"))
    if not m:
        return "", "", False
    fm = m.group(1)
    nm = _NAME.search(fm)
    # description may be block or single line
    desc = ""
    dm = re.search(r"^description:\s*\|\s*\n((?:[ \t]+.*\n?)+)", fm, re.M)
    if dm:
        desc = " ".join(line.strip() for line in dm.group(1).splitlines() if line.strip())
    else:
        dm2 = re.search(r"^description:\s*>\s*\n((?:[ \t]+.*\n?)+)", fm, re.M)
        if dm2:
            desc = " ".join(line.strip() for line in dm2.group(1).splitlines() if line.strip())
        else:
            dm3 = re.search(r"^description:\s*(.+)$", fm, re.M)
            desc = dm3.group(1).strip() if dm3 else ""
    name = nm.group(1).strip() if nm else ""
    return name, desc, True


def l1_tokens(name: str, description: str) -> int:
    return estimate_tokens(f"{name} {description}")


def check_l1_budget(name: str, description: str, *, hedge: int = 80, target: int = 50) -> dict:
    tok = l1_tokens(name, description)
    return {
        "name": name,
        "tokens": tok,
        "target": target,
        "hedge": hedge,
        "within_hedge": tok <= hedge,
        "within_target": tok <= target,
    }


@dataclass
class SkillBody:
    name: str
    priority: int
    body_chars: int
    hard_rules: list[str] = field(default_factory=list)


def coloaded_overflow(skills: Iterable[SkillBody], *, soft_max: int = 3, flag_chars: int = 32000) -> list[str]:
    items = list(skills)
    findings: list[str] = []
    if len(items) > soft_max:
        findings.append(f"CC-002_count:{len(items)}>{soft_max}")
    total = sum(s.body_chars for s in items)
    if total > flag_chars:
        findings.append(f"CC-002_chars:{total}>{flag_chars}")
    return findings


def detect_hard_rule_collisions(skills: Iterable[SkillBody]) -> list[dict]:
    """Naive collision: same subject key with opposing MUST/NEVER polarity mentions."""
    polarity: dict[str, list[tuple[str, str]]] = {}
    for s in skills:
        for rule in s.hard_rules:
            key = re.sub(r"\s+", " ", rule.strip().lower())
            # extract rough subject after must/never
            m = re.search(r"\b(must not|must|never|always)\b\s+(.+)", key)
            if not m:
                continue
            pol, subj = m.group(1), m.group(2)[:80]
            polarity.setdefault(subj, []).append((s.name, pol))
    collisions = []
    for subj, ents in polarity.items():
        pols = {p for _, p in ents}
        if ("must" in pols or "always" in pols) and ("must not" in pols or "never" in pols):
            collisions.append({"id": "CC-001", "subject": subj, "parties": ents})
    return collisions


def resolve_precedence(sources: list[str]) -> str:
    """Return winning source id by lowest rank number."""
    best = None
    best_rank = 10**9
    for s in sources:
        r = PRECEDENCE_RANK.get(s, 50)
        if r < best_rank:
            best, best_rank = s, r
    if best is None:
        raise ValueError("empty sources")
    return best


def memory_vs_constraint(memory_allows: bool, constraint_allows: bool) -> str:
    """CC-004: constraints win."""
    if constraint_allows is False:
        return "deny_constraint"
    if memory_allows:
        return "allow"
    return "deny_memory"


@dataclass
class CompactionPlan:
    strategy: str
    kept_event_ids: list[int]
    summary_covers_through: int | None
    model_view_event_ids: list[int]


def compact_session(
    event_ids: list[int],
    *,
    last_n: int = 10,
    fill_ratio: float = 0.0,
    existing_bookmark: int | None = None,
) -> CompactionPlan:
    """Structural compaction planner (view-side)."""
    if not event_ids:
        return CompactionPlan("noop", [], existing_bookmark, [])
    ids = sorted(event_ids)
    if fill_ratio >= 0.85:
        kept = ids[-max(3, last_n // 2) :]
        return CompactionPlan("emergency_truncate", kept, kept[0] - 1 if kept[0] > ids[0] else None, kept)
    if fill_ratio >= 0.70 or len(ids) > last_n:
        kept = ids[-last_n:]
        covered = kept[0] - 1 if kept[0] > ids[0] else None
        if existing_bookmark is not None and (covered is None or existing_bookmark > covered):
            # do not regress bookmark falsely; view still last_n
            pass
        return CompactionPlan("C_SLIDE_N", kept, covered, kept)
    return CompactionPlan("C_TOKEN_BACKFILL", ids, existing_bookmark, ids)


def validate_assembly_order(steps: list[str]) -> bool:
    """True if steps is a subsequence of ASSEMBLY_ORDER in order (no straying)."""
    try:
        idxs = [ASSEMBLY_ORDER.index(s) for s in steps]
    except ValueError:
        return False
    return idxs == sorted(idxs) and len(idxs) == len(set(idxs))
