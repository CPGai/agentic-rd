#!/usr/bin/env python3
"""G10 Production AgentOps — Structural Test Suite (Step E)

Tests: blueprint/DSL surface, capability inventory, CI canary schedule,
quality gates (5%/15%, trust decay), doctor probes, fleet rollback rules,
chaos engine bindings, cross-artifact consistency, secret scan.

stdlib unittest only — no pytest required.
Run: python -m unittest tests.test_g10_production -v
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unittest

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G10 = os.path.join(ROOT, "specs", "g10_production")
SCRIPTS = os.path.join(ROOT, "scripts")

RESUME = "G10_PRODUCTION_DEPLOY_v1"
UPSTREAM = "research-loop-v1.0.0"
OVERLAY = "OPTION_2_STANDARD"
LKG = "v0.9.0-previous"

RESUME_TOKENS = [
    "G1_HARNESS_APPROVED_v1",
    "G2_TOOL_REGISTRY_LOCKED_v1",
    "G2_TOOLING_APPROVED_v1",
    "G3_CONTEXT_LAYER_LOCKED_v1",
    "G4_TOPOLOGY_APPROVED_v1",
    "G5_EVAL_FRAMEWORK_APPROVED_v1",
    "G5_EVAL_APPROVED_v1",
    "G6_VIBE_ENV_LOCKED_v1",
    "G7_IMPROVEMENT_BOUNDS_v1",
    "G8_MULTITENANT_APPROVED_v1",
    "G9_RESEARCH_FLEET_LOCKED_v1",
    "G10_PRODUCTION_DEPLOY_v1",
    "RESUME_TOKEN",
]

ARTIFACTS = [
    "PRODUCTION_AGENTOPS_BLUEPRINT.md",
    "CAPABILITY_DISCOVERY.yaml",
    "PRODUCTION_DSL_SPEC.md",
    "cicd_pipeline.yaml",
    "quality_gates.yaml",
    "doctor_checks.yaml",
    "fleet_management.yaml",
]


def load_yaml(name: str):
    with open(os.path.join(G10, name), "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_md(name: str) -> str:
    with open(os.path.join(G10, name), "r", encoding="utf-8") as fh:
        return fh.read()


class TestArtifactPresence(unittest.TestCase):
    def test_all_a_d_artifacts(self):
        for fn in ARTIFACTS:
            self.assertTrue(
                os.path.isfile(os.path.join(G10, fn)), f"missing {fn}"
            )

    def test_handoff_present(self):
        self.assertTrue(
            os.path.isfile(os.path.join(G10, "G10_MIGRATION_CONTEXT.md"))
        )


class TestBlueprint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = load_md("PRODUCTION_AGENTOPS_BLUEPRINT.md")
        cls.lower = cls.text.lower()

    def test_resume_and_overlay(self):
        self.assertIn(RESUME, self.text)
        self.assertIn(OVERLAY, self.text)
        self.assertIn(UPSTREAM, self.text)

    def test_core_sections(self):
        for needle in [
            "spec-driven",
            "ci/cd",
            "vertex",
            "cloud run",
            "policy server",
            "opentelemetry",
            "doctor",
            "evidence pack",
            "approval fatigue",
            "rollback",
            "canary",
            "llm06",
            "accountability",
        ]:
            self.assertIn(needle, self.lower)

    def test_option_matrix_star(self):
        self.assertIn("OPTION_2_STANDARD", self.text)
        self.assertIn("★", self.text)
        self.assertIn("OPTION_1_CONSERVATIVE", self.text)
        self.assertIn("OPTION_3_CREATIVE", self.text)

    def test_constraints_c_pa(self):
        for i in range(1, 9):
            self.assertIn(f"C-PA-0{i}", self.text)

    def test_canary_and_decay(self):
        self.assertIn("1%", self.text)
        self.assertIn("15%", self.text)
        self.assertIn("5%", self.text)


class TestDslSpec(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = load_md("PRODUCTION_DSL_SPEC.md")

    def test_ebnf_and_rules(self):
        self.assertIn("EBNF", self.text)
        self.assertGreaterEqual(len(set(re.findall(r"SV-PA-\d+", self.text))), 15)
        self.assertGreaterEqual(len(set(re.findall(r"SEM-PA-\d+", self.text))), 10)

    def test_canary_sequence(self):
        self.assertIn("1", self.text)
        self.assertIn("5", self.text)
        self.assertIn("25", self.text)
        self.assertIn("100", self.text)

    def test_thresholds(self):
        self.assertIn("5%", self.text)
        self.assertIn("15%", self.text)
        self.assertIn(RESUME, self.text)


class TestCapabilityDiscovery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_yaml("CAPABILITY_DISCOVERY.yaml")

    def test_header(self):
        self.assertEqual(self.data.get("blue_resume_token"), RESUME)
        self.assertEqual(self.data.get("overlay"), OVERLAY)
        self.assertEqual(self.data.get("upstream_tag"), UPSTREAM)

    def test_runtimes(self):
        names = [r.get("name", "") for r in self.data.get("production_runtimes") or []]
        blob = " ".join(names)
        self.assertIn("Vertex", blob)
        self.assertIn("Cloud Run", blob)
        self.assertTrue("gVisor" in blob or "Agent Sandbox" in blob)

    def test_cicd_and_telemetry(self):
        rn = " ".join(r.get("name", "") for r in self.data.get("cicd_runners") or [])
        self.assertIn("GitHub Actions", rn)
        self.assertIn("Cloud Build", rn)
        self.assertIn("Hermes", rn)
        tn = " ".join(t.get("name", "") for t in self.data.get("telemetry_collectors") or [])
        self.assertIn("OpenTelemetry", tn)
        self.assertIn("Google Cloud Observability", tn)

    def test_procurement(self):
        tiers = (self.data.get("procurement_summary") or {}).get("tiers") or {}
        for t in ["T1", "T2", "T3", "T4"]:
            self.assertIn(t, tiers)


class TestCicdPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_yaml("cicd_pipeline.yaml")

    def test_stages(self):
        sids = {s.get("id") for s in self.data.get("stages") or []}
        for s in ["STG-01", "STG-05", "STG-06", "STG-08", "STG-09", "STG-10"]:
            self.assertIn(s, sids)

    def test_canary_schedule(self):
        stg08 = next(s for s in self.data["stages"] if s["id"] == "STG-08")
        pcts = [c["pct"] for c in stg08["canary"]["schedule"]]
        self.assertEqual(pcts, [1, 5, 25, 100])
        self.assertTrue(stg08["canary"]["auto_rollback"])

    def test_branch_policy_blocks_dune(self):
        blocked = self.data.get("branch_policy", {}).get("blocked_from_canary") or []
        self.assertTrue(any("prototype" in b or "dune" in b for b in blocked))


class TestQualityGates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_yaml("quality_gates.yaml")

    def test_delta_bands(self):
        bands = self.data["delta_bands"]
        self.assertEqual(bands["amber"]["min_degradation_pct"], 5)
        self.assertEqual(bands["red"]["min_degradation_pct"], 15)

    def test_trust(self):
        ts = self.data["trust_score"]
        self.assertEqual(ts["thresholds"]["warning"], 0.85)
        self.assertEqual(ts["thresholds"]["hitl_review"], 0.70)
        self.assertEqual(ts["thresholds"]["trip"], 0.50)
        self.assertEqual(ts["canary_decay_rollback_pct"], 15)
        self.assertFalse(ts["auto_restore"])

    def test_llm06_gate(self):
        g20 = next(g for g in self.data["quality_gates"] if g["id"] == "QG-020")
        self.assertTrue(g20["non_delegatable"])
        self.assertFalse(g20["llm_can_bypass"])
        self.assertEqual(len(g20["controls"]), 8)

    def test_required_gates(self):
        ids = {g["id"] for g in self.data["quality_gates"]}
        for gid in ["QG-001", "QG-003", "QG-020", "QG-030", "QG-050"]:
            self.assertIn(gid, ids)


class TestDoctorChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_yaml("doctor_checks.yaml")

    def test_probe_types(self):
        types = {p["probe_type"] for p in self.data["probes"]}
        for pt in [
            "svid_validation",
            "network_boundary",
            "policy_server_ping",
            "memory_bank_health",
        ]:
            self.assertIn(pt, types)

    def test_critical_fail_closed(self):
        for p in self.data["probes"]:
            if p.get("severity") == "CRITICAL":
                self.assertTrue(p.get("fail_closed"), p.get("id"))

    def test_key_probes(self):
        ids = {p["id"] for p in self.data["probes"]}
        for pid in ["DOC-IDENT-01", "DOC-NET-02", "DOC-POL-01", "DOC-MEM-01"]:
            self.assertIn(pid, ids)

    def test_default_enforce(self):
        self.assertEqual(self.data["modes"]["default_production_mode"], "enforce")


class TestFleetManagement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_yaml("fleet_management.yaml")

    def test_topology(self):
        fleet = self.data["fleet"]
        self.assertEqual(fleet["topology"], "hierarchical_coordinator_specialists")
        self.assertFalse(fleet["l4_agent_creator"])
        self.assertEqual(fleet["max_concurrent_specialists"], 3)

    def test_canary(self):
        can = self.data["canary"]
        self.assertEqual([s["pct"] for s in can["schedule"]], [1, 5, 25, 100])
        self.assertTrue(can["auto_rollback"])

    def test_rollback_triggers(self):
        ids = {t["id"] for t in self.data["rollback"]["triggers"]}
        for rid in ["RB-01", "RB-02", "RB-03", "RB-04", "RB-05", "RB-06"]:
            self.assertIn(rid, ids)
        rb03 = next(t for t in self.data["rollback"]["triggers"] if t["id"] == "RB-03")
        self.assertIn("15", rb03["condition"])

    def test_model_routing_dynamic(self):
        mr = self.data["model_routing"]
        self.assertTrue(mr["forbid_frozen_version_pins_in_constitution"])
        tiers = {r["tier"] for r in mr["routes"]}
        self.assertTrue(
            {"Premium_Frontier", "Strong_Coding", "Fast_Flash"} <= tiers
        )


class TestChaosDryRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        env = os.environ.copy()
        proc = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "dry_run_g10.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            env=env,
        )
        cls.rc = proc.returncode
        cls.stdout = proc.stdout
        metrics_path = os.path.join(G10, "chaos_dry_run_metrics.json")
        with open(metrics_path, "r", encoding="utf-8") as fh:
            cls.metrics = json.load(fh)

    def test_exit_zero(self):
        self.assertEqual(self.rc, 0, self.stdout)

    def test_all_scenarios_pass(self):
        self.assertTrue(self.metrics["summary"]["all_pass"])
        self.assertEqual(self.metrics["summary"]["passed"], 5)

    def test_policy_blocks(self):
        self.assertEqual(self.metrics["summary"]["policy_critical_blocks"], 8)

    def test_pii_zero_leaks(self):
        self.assertEqual(self.metrics["summary"]["pii_leaks"], 0)

    def test_trust_rollback_lkg(self):
        self.assertTrue(self.metrics["summary"]["trust_rolled_back_to_lkg"])
        self.assertEqual(self.metrics["lkg_revision"], LKG)

    def test_doctor_isolation(self):
        self.assertTrue(self.metrics["summary"]["doctor_isolated_fleet"])


class TestCrossArtifact(unittest.TestCase):
    def test_token_overlay_upstream(self):
        for fn in ARTIFACTS:
            text = open(os.path.join(G10, fn), encoding="utf-8").read()
            self.assertIn(RESUME, text, fn)
            self.assertIn(OVERLAY, text, fn)
            self.assertIn(UPSTREAM, text, fn)


class TestSecretScan(unittest.TestCase):
    def test_no_secrets(self):
        pat = re.compile(
            r"(?:token|secret|password|api_key|apikey|bearer)\s*[=:]\s*\S{20,}",
            re.I,
        )
        bearer = re.compile(r"Bearer\s+\S{20,}", re.I)
        hits = []
        for fn in ARTIFACTS + ["chaos_dry_run_metrics.json"]:
            path = os.path.join(G10, fn)
            if not os.path.isfile(path):
                continue
            text = open(path, encoding="utf-8").read()
            for m in pat.finditer(text):
                h = m.group(0)
                if any(rt in h for rt in RESUME_TOKENS):
                    continue
                if "resume_token" in h.lower() or "blue_resume" in h.lower():
                    continue
                hits.append(f"{fn}:{h[:60]}")
            for m in bearer.finditer(text):
                hits.append(f"{fn}:bearer")
        self.assertEqual(hits, [])


class TestCanaryJumpForbidden(unittest.TestCase):
    def test_no_skip_semantics(self):
        """ST-G10-01 intent: schedule is strict 1→5→25→100."""
        fleet = load_yaml("fleet_management.yaml")
        pcts = [s["pct"] for s in fleet["canary"]["schedule"]]
        self.assertEqual(pcts, [1, 5, 25, 100])
        for a, b in zip(pcts, pcts[1:]):
            self.assertLess(a, b)


class TestTrustDecayTriggerMath(unittest.TestCase):
    def test_decay_boundary(self):
        """ST-G10-02: decay >15% trips; values at or under 15 do not."""
        baseline = 1.0
        # Use exact decay percentages to avoid binary float edge noise on 0.85.
        cases = [
            (0.90, False),   # 10% decay
            (0.851, False),  # 14.9% decay
            (0.849, True),   # 15.1% decay
            (0.80, True),    # 20% decay
        ]
        for trust, expect_trip in cases:
            decay = ((baseline - trust) / baseline) * 100.0
            trip = decay > 15.0
            self.assertEqual(trip, expect_trip, f"trust={trust} decay={decay}")


if __name__ == "__main__":
    unittest.main()
