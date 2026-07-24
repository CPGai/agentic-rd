#!/usr/bin/env python3
"""Unit tests for G4 multi-agent orchestration structural invariants (stdlib unittest).

Run:
  cd /home/carlospg/workspace/agentic-rd && source .venv-hermes/bin/activate \
    && python -m unittest tests.test_g4_orchestration -v
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

ROOT = Path("/home/carlospg/workspace/agentic-rd")
G4 = ROOT / "specs" / "g4_orchestration"

# ---------------------------------------------------------------------------
# Load artifacts once
# ---------------------------------------------------------------------------
WG = yaml.safe_load((G4 / "workflow_graph.yaml").read_text(encoding="utf-8"))
POL = yaml.safe_load((G4 / "POLICY_INTERCEPT_SPEC.yaml").read_text(encoding="utf-8"))
FM = yaml.safe_load((G4 / "FAILURE_MODE_MATRIX.yaml").read_text(encoding="utf-8"))
CARDS = {}
for _p in sorted((G4 / "agent_cards").glob("*.card.json")):
    CARDS[_p.name] = json.loads(_p.read_text(encoding="utf-8"))
TOPO = (G4 / "MULTI_AGENT_TOPOLOGY.md").read_text(encoding="utf-8")
GHERKIN = (G4 / "GHERKIN_DECOMPOSITION_TEMPLATES.md").read_text(encoding="utf-8")


class TestTopologyCaps(unittest.TestCase):
    """Step E invariant: topology caps align with OPTION_2_STANDARD."""

    def test_max_concurrent_children(self) -> None:
        self.assertEqual(WG["caps"]["max_concurrent_children"], 3)

    def test_max_spawn_depth(self) -> None:
        self.assertEqual(WG["caps"]["max_spawn_depth"], 1)

    def test_l4_disabled(self) -> None:
        self.assertFalse(WG["l4_enabled"])

    def test_primary_topology(self) -> None:
        self.assertEqual(WG["primary_topology"], "hierarchical_coordinator_specialists")

    def test_recommended_path(self) -> None:
        self.assertEqual(WG["recommended_path"], "OPTION_2_STANDARD")

    def test_resume_token(self) -> None:
        self.assertEqual(WG["resume_token_expected"], "G4_TOPOLOGY_APPROVED_v1")

    def test_lro_threshold(self) -> None:
        self.assertEqual(WG["caps"]["lro_threshold_ms"], 10000)

    def test_nested_orchestrator_false(self) -> None:
        self.assertFalse(WG["caps"]["nested_orchestrator"])


class TestAgentCards(unittest.TestCase):
    """Step E invariant: all 8 cards conform to schema."""

    REQUIRED_KEYS = {
        "id", "name", "version", "description", "url",
        "capabilities", "skills", "security", "risk_tier",
        "policy", "lifecycle", "interaction", "option_2",
    }

    def test_card_count(self) -> None:
        self.assertGreaterEqual(len(CARDS), 8)

    def test_all_cards_have_required_keys(self) -> None:
        for fname, data in CARDS.items():
            missing = self.REQUIRED_KEYS - set(data.keys())
            self.assertFalse(missing, f"{fname} missing keys: {missing}")

    def test_all_lifecycle_schema_only(self) -> None:
        for fname, data in CARDS.items():
            self.assertIn(
                data["lifecycle"],
                {"schema_only", "mock", "wired"},
                f"{fname} lifecycle={data['lifecycle']}",
            )

    def test_remote_billing_disabled(self) -> None:
        remote = CARDS.get("remote_billing_example.card.json")
        self.assertIsNotNone(remote, "remote billing card missing")
        self.assertFalse(remote["option_2"]["enabled"])
        self.assertEqual(remote["lifecycle"], "schema_only")
        self.assertEqual(remote["risk_tier"], "T4")

    def test_root_card_present(self) -> None:
        root = CARDS.get("root_orchestrator.card.json")
        self.assertIsNotNone(root)
        self.assertEqual(root["id"], "card.root.orchestrator")

    def test_all_card_ids_unique(self) -> None:
        ids = [d["id"] for d in CARDS.values()]
        self.assertEqual(len(ids), len(set(ids)))


class TestFailureMatrix(unittest.TestCase):
    """Step E invariant: 15 failure modes, all recovery declared, BLUE trio present."""

    MODES = FM["failure_modes"]

    def test_mode_count(self) -> None:
        self.assertEqual(len(self.MODES), 15)

    def test_all_recovery_declared(self) -> None:
        for m in self.MODES:
            self.assertTrue(
                m.get("recovery_declared"),
                f"{m['id']} missing recovery_declared",
            )

    def test_blue_trio_timeout(self) -> None:
        cov = FM["blue_required_coverage"]
        self.assertEqual(cov["timeout"], "FM-TIMEOUT")
        mode = next(m for m in self.MODES if m["id"] == "FM-TIMEOUT")
        self.assertEqual(mode["severity"], "HIGH")

    def test_blue_trio_region_collision(self) -> None:
        cov = FM["blue_required_coverage"]
        self.assertEqual(cov["region_collision"], "FM-REGION-COLLISION")
        mode = next(m for m in self.MODES if m["id"] == "FM-REGION-COLLISION")
        self.assertEqual(mode["severity"], "HIGH")

    def test_blue_trio_budget_ceiling(self) -> None:
        cov = FM["blue_required_coverage"]
        self.assertEqual(cov["spending_limit_exceed"], "FM-BUDGET-CEILING")
        mode = next(m for m in self.MODES if m["id"] == "FM-BUDGET-CEILING")
        self.assertEqual(mode["severity"], "CRITICAL")

    def test_unique_mode_ids(self) -> None:
        ids = [m["id"] for m in self.MODES]
        self.assertEqual(len(ids), len(set(ids)))


class TestEdgeRules(unittest.TestCase):
    """Step E invariant: edge classification breakdown."""

    EDGES = WG["edges"]

    def test_edge_count(self) -> None:
        self.assertGreaterEqual(len(self.EDGES), 20)

    def test_has_deterministic_edges(self) -> None:
        kinds = {e["kind"] for e in self.EDGES}
        self.assertIn("deterministic", kinds)

    def test_has_dynamic_edges(self) -> None:
        kinds = {e["kind"] for e in self.EDGES}
        self.assertIn("dynamic", kinds)

    def test_has_hitl_edges(self) -> None:
        kinds = {e["kind"] for e in self.EDGES}
        self.assertIn("hitl", kinds)

    def test_all_edges_have_ids(self) -> None:
        for e in self.EDGES:
            self.assertIn("id", e)
            self.assertIn("from", e)
            self.assertIn("to", e)

    def test_decision_boundaries_present(self) -> None:
        db = WG["decision_boundaries"]
        self.assertGreater(len(db["deterministic"]), 0)
        self.assertGreater(len(db["llm_driven"]), 0)
        self.assertGreater(len(db["hitl_required"]), 0)


class TestPolicyGateway(unittest.TestCase):
    """Step E invariant: policy seat DECLARED_NOT_WIRED."""

    def test_status_declared_not_wired(self) -> None:
        self.assertEqual(POL["status"], "DECLARED_NOT_WIRED")

    def test_seat_id(self) -> None:
        self.assertEqual(POL["seat_id"], "POLICY_SEAT")

    def test_payment_class_present(self) -> None:
        self.assertIn("payment", POL["intercept_classes"])

    def test_rules_count(self) -> None:
        self.assertGreaterEqual(len(POL["rules"]), 5)

    def test_fail_closed_mode(self) -> None:
        self.assertEqual(POL["mode"], "fail_closed_when_invoked")


class TestTopologyDoc(unittest.TestCase):
    """Step E invariant: MULTI_AGENT_TOPOLOGY.md section coverage."""

    def test_has_pattern_catalog(self) -> None:
        self.assertIn("## 3. Pattern catalog", TOPO)

    def test_has_root_orchestrator(self) -> None:
        self.assertIn("## 4. Hierarchical root orchestrator", TOPO)

    def test_has_a2a_handshake(self) -> None:
        self.assertIn("## 6. A2A discovery handshake", TOPO)

    def test_has_ap2_ledger(self) -> None:
        self.assertIn("## 8. AP2 micro-payment ledger semantics", TOPO)

    def test_has_resume_token(self) -> None:
        self.assertIn("G4_TOPOLOGY_APPROVED_v1", TOPO)

    def test_has_option2(self) -> None:
        self.assertIn("OPTION_2_STANDARD", TOPO)


class TestGherkinTemplates(unittest.TestCase):
    """Step E invariant: Gherkin template coverage."""

    def test_has_task_envelope(self) -> None:
        self.assertIn("Task envelope", GHERKIN)

    def test_has_agent_tag(self) -> None:
        self.assertIn("@agent:", GHERKIN)

    def test_has_payment_tag(self) -> None:
        self.assertIn("@payment", GHERKIN)

    def test_has_feature_keyword(self) -> None:
        self.assertIn("Feature:", GHERKIN)

    def test_has_risk_tag(self) -> None:
        self.assertIn("@risk:", GHERKIN)


class TestHandshakeStates(unittest.TestCase):
    """Step E invariant: A2A handshake state machine."""

    def test_all_states_present(self) -> None:
        states = set(WG["a2a_handshake_states"])
        required = {
            "CARD_RESOLVE", "SECURITY_EVAL", "POLICY_CHECK",
            "TASK_OFFER", "ACCEPTED", "RUNNING",
            "COMPLETED", "FAILED", "TIMED_OUT", "CANCELLED",
            "DENY_TERMINAL", "AGGREGATE",
        }
        self.assertTrue(required.issubset(states), f"missing: {required - states}")

    def test_state_count(self) -> None:
        self.assertGreaterEqual(len(WG["a2a_handshake_states"]), 15)


class TestSecretScan(unittest.TestCase):
    """Step E invariant: no secrets in G4 pack."""

    def test_no_secrets_in_pack(self) -> None:
        import re
        rx = re.compile(
            r"(api[_-]?key\s*[:=]\s*['\"][^'\"]{8,}['\"]|"
            r"Bearer\s+[A-Za-z0-9\-._~+/]{20,}={0,2}|"
            r"sk-[A-Za-z0-9]{20,})",
            re.I,
        )
        for p in G4.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in {".md", ".yaml", ".yml", ".json"}:
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
            self.assertFalse(
                rx.search(text),
                f"possible secret in {p.relative_to(G4)}",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
