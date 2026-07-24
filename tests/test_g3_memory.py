#!/usr/bin/env python3
"""Unit tests for G3 context/memory structural helpers (stdlib unittest).

Run:
  cd /home/carlospg/workspace/agentic-rd && source .venv-hermes/bin/activate \\
    && python -m unittest tests.test_g3_memory -v
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path("/home/carlospg/workspace/agentic-rd")
sys.path.insert(0, str(ROOT / "scripts"))

from g3_memory import (  # noqa: E402
    ASSEMBLY_ORDER,
    check_l1_budget,
    coloaded_overflow,
    compact_session,
    detect_hard_rule_collisions,
    estimate_tokens,
    memory_vs_constraint,
    parse_skill_l1,
    resolve_precedence,
    SkillBody,
    validate_assembly_order,
)


SAMPLE_SKILL = """---
name: demo-skill
description: >
  Do the demo when the user asks for demo routing.
  Do NOT use for production payments.
priority: 10
---

# Body
Rules here.
"""


class L1Tests(unittest.TestCase):
    def test_parse_frontmatter(self) -> None:
        name, desc, ok = parse_skill_l1(SAMPLE_SKILL)
        self.assertTrue(ok)
        self.assertEqual(name, "demo-skill")
        self.assertIn("demo", desc.lower())
        self.assertIn("NOT", desc)

    def test_l1_budget_within_hedge(self) -> None:
        name, desc, _ = parse_skill_l1(SAMPLE_SKILL)
        rep = check_l1_budget(name, desc)
        self.assertTrue(rep["within_hedge"])
        self.assertGreater(rep["tokens"], 0)

    def test_estimate_tokens(self) -> None:
        self.assertEqual(estimate_tokens(""), 0)
        self.assertEqual(estimate_tokens("abcd"), 1)


class AssemblyTests(unittest.TestCase):
    def test_canonical_order(self) -> None:
        self.assertTrue(validate_assembly_order(list(ASSEMBLY_ORDER)))

    def test_rejects_reorder(self) -> None:
        bad = list(ASSEMBLY_ORDER)
        bad[0], bad[-1] = bad[-1], bad[0]
        self.assertFalse(validate_assembly_order(bad))

    def test_rejects_unknown(self) -> None:
        self.assertFalse(validate_assembly_order(["static_pack", "vibe"]))


class ColoadTests(unittest.TestCase):
    def test_overflow_count(self) -> None:
        skills = [SkillBody(f"s{i}", i, 100) for i in range(5)]
        findings = coloaded_overflow(skills, soft_max=3, flag_chars=10_000_000)
        self.assertTrue(any("CC-002_count" in f for f in findings))

    def test_hard_rule_collision(self) -> None:
        skills = [
            SkillBody("a", 1, 10, ["must enable auth"]),
            SkillBody("b", 1, 10, ["never enable auth"]),
        ]
        cols = detect_hard_rule_collisions(skills)
        self.assertGreaterEqual(len(cols), 1)
        self.assertEqual(cols[0]["id"], "CC-001")

    def test_precedence_constraints_win(self) -> None:
        winner = resolve_precedence(["memory_suggestions_advisory", "constraint_catalog_safety_hooks", "skill_l2"])
        self.assertEqual(winner, "constraint_catalog_safety_hooks")

    def test_memory_vs_constraint(self) -> None:
        self.assertEqual(memory_vs_constraint(True, False), "deny_constraint")
        self.assertEqual(memory_vs_constraint(True, True), "allow")


class CompactionTests(unittest.TestCase):
    def test_slide_n(self) -> None:
        plan = compact_session(list(range(1, 31)), last_n=10, fill_ratio=0.72)
        self.assertEqual(plan.strategy, "C_SLIDE_N")
        self.assertEqual(plan.model_view_event_ids, list(range(21, 31)))

    def test_emergency(self) -> None:
        plan = compact_session(list(range(1, 31)), last_n=10, fill_ratio=0.91)
        self.assertEqual(plan.strategy, "emergency_truncate")
        self.assertLessEqual(len(plan.model_view_event_ids), 10)

    def test_low_pressure_keeps_all(self) -> None:
        plan = compact_session([1, 2, 3], last_n=10, fill_ratio=0.2)
        self.assertEqual(plan.model_view_event_ids, [1, 2, 3])


class LockedYamlTests(unittest.TestCase):
    def test_token_budget_locked(self) -> None:
        p = ROOT / "specs/g3_memory/token_budget.yaml"
        doc = yaml.safe_load(p.read_text(encoding="utf-8"))
        self.assertEqual(doc["status"], "LOCKED")
        self.assertEqual(doc["resume_token"], "G3_CONTEXT_LAYER_LOCKED_v1")
        self.assertEqual(doc["window"]["static_pack_hard_ceiling"], 0.20)

    def test_coload_audit_order(self) -> None:
        p = ROOT / "specs/g3_memory/SKILL_COLOAD_AUDIT.yaml"
        doc = yaml.safe_load(p.read_text(encoding="utf-8"))
        self.assertEqual(doc["assembly_order_binding"], list(ASSEMBLY_ORDER))
        self.assertEqual(doc["status"], "LOCKED")

    def test_workspace_skills_exist(self) -> None:
        found = list((ROOT / "skills").rglob("SKILL.md"))
        self.assertGreaterEqual(len(found), 5)


if __name__ == "__main__":
    unittest.main()
