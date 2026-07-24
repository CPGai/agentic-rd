#!/usr/bin/env python3
"""G7 Self-Improvement — Structural Test Suite (Step E)

Tests declarative artifacts in specs/g7_self_improve/ for structural
completeness against the 15 ST-G7 intents defined in
SELF_IMPROVEMENT_ARCHITECTURE.md section 10.

Run: python -m unittest tests.test_g7_self_improve -v
"""

import os
import re
import sys
import json
import unittest
import yaml

G7_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "specs", "g7_self_improve"
)


def _read(name):
    path = os.path.join(G7_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _read_yaml(name):
    path = os.path.join(G7_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestG7Architecture(unittest.TestCase):
    """ST-G7-01 through ST-G7-12 — architecture spec structural tests."""

    @classmethod
    def setUpClass(cls):
        cls.arch = _read("SELF_IMPROVEMENT_ARCHITECTURE.md")

    def test_st_g7_01_five_phase_loop(self):
        """ST-G7-01: Closed-loop has 5 phases."""
        for phase in ["Detect", "Acquire", "Validate", "Integrate", "Measure"]:
            self.assertIn(phase, self.arch)

    def test_st_g7_02_severity_classes(self):
        """ST-G7-02: Severity classes S1-S4 with autonomy levels."""
        for s in ["S1", "S2", "S3", "S4"]:
            self.assertIn(s, self.arch)
        self.assertIn("Restricted", self.arch)
        self.assertIn("Human-gated", self.arch)
        self.assertIn("Advisory", self.arch)
        self.assertIn("Autonomous", self.arch)

    def test_st_g7_03_acquisition_tiers(self):
        """ST-G7-03: Acquisition tiers T1-T4 with OPTION_2 status."""
        for t in ["T1", "T2", "T3", "T4"]:
            self.assertIn(t, self.arch)
        self.assertIn("Enabled", self.arch)
        self.assertIn("Conditional", self.arch)

    def test_st_g7_04_generalization_gap(self):
        """ST-G7-04: Generalization-gap safeguards include held-out + negative test."""
        lower = self.arch.lower()
        self.assertIn("held-out", lower)
        self.assertIn("negative test", lower)

    def test_st_g7_05_rollback_policy(self):
        """ST-G7-05: Rollback covers regression, thrashing, circuit breaker, HITL deny."""
        lower = self.arch.lower()
        self.assertIn("regression", lower)
        self.assertIn("thrashing", lower)
        self.assertIn("circuit breaker", lower)
        self.assertIn("hitl denies", lower)

    def test_st_g7_06_pivot_refine_criteria(self):
        """ST-G7-06: Pivot/Refine criteria include flat fix curve + thrashing."""
        lower = self.arch.lower()
        self.assertIn("flat", lower)
        self.assertIn("thrashing", lower)

    def test_st_g7_07_operators(self):
        """ST-G7-07: Operators DRAFT, DEBUG, IMPROVE, PIVOT, REFINE defined."""
        for op in ["DRAFT", "DEBUG", "IMPROVE", "PIVOT", "REFINE"]:
            self.assertIn(op, self.arch)

    def test_st_g7_08_l4_disabled(self):
        """ST-G7-08: L4 AgentCreator remains disabled (C-LOOP-02)."""
        self.assertIn("AgentCreator", self.arch)
        self.assertIn("C-LOOP-02", self.arch)
        self.assertIn("disabled", self.arch.lower())

    def test_st_g7_09_hard_bounds(self):
        """ST-G7-09: Hard bounds list >= 8 non-negotiable rules."""
        tax = _read("TAXONOMY_AND_BOUNDS.md")
        hb_count = len(re.findall(r"\bHB-\d+\b", tax))
        self.assertGreaterEqual(hb_count, 8)

    def test_st_g7_10_g5_g6_inheritance(self):
        """ST-G7-10: G5/G6 inheritance tables present."""
        self.assertIn("G5 Inheritance", self.arch)
        self.assertIn("G6 Inheritance", self.arch)

    def test_st_g7_11_option_2_recommended(self):
        """ST-G7-11: OPTION_2_STANDARD marked as recommended path."""
        self.assertIn("OPTION_2_STANDARD", self.arch)
        self.assertIn("\u2605", self.arch)
        self.assertIn("SELECTED_PATH", self.arch)

    def test_st_g7_12_resume_token(self):
        """ST-G7-12: BLUE resume token present."""
        self.assertIn("G7_IMPROVEMENT_BOUNDS_v1", self.arch)

    def test_st_g7_13_no_secrets(self):
        """ST-G7-13: No secrets or API keys in spec body."""
        bearer = re.findall(r"Bearer\s+[A-Za-z0-9\-_]{20,}", self.arch)
        sk = re.findall(r"sk-[A-Za-z0-9]{20,}", self.arch)
        self.assertEqual(len(bearer), 0)
        self.assertEqual(len(sk), 0)

    def test_st_g7_14_loop_budget(self):
        """ST-G7-14: Loop budget cap (10 proposals/session)."""
        self.assertIn("10", self.arch)
        self.assertIn("loop budget", self.arch.lower())

    def test_st_g7_15_thrashing_thresholds(self):
        """ST-G7-15: Thrashing detection thresholds defined."""
        lower = self.arch.lower()
        self.assertIn("thrashing", lower)
        self.assertIn("3", self.arch)  # threshold >=3


if __name__ == "__main__":
    unittest.main(verbosity=2)
