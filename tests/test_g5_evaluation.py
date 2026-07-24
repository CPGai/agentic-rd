#!/usr/bin/env python3
"""Unit tests for G5 Evaluation & Observability structural invariants (stdlib unittest).

Run:
  cd /home/carlospg/workspace/agentic-rd && source .venv-hermes/bin/activate \
    && python -m unittest tests.test_g5_evaluation -v
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import yaml

ROOT = Path("/home/carlospg/workspace/agentic-rd")
G5 = ROOT / "specs" / "g5_evaluation"

# ---------------------------------------------------------------------------
# Load artifacts once
# ---------------------------------------------------------------------------
SPEC_MD = (G5 / "EVALUATION_HARNESS_SPEC.md").read_text(encoding="utf-8")
OBS_YAML = yaml.safe_load((G5 / "OBSERVABILITY_PILLARS_SPEC.yaml").read_text(encoding="utf-8"))
CB_YAML = yaml.safe_load((G5 / "CIRCUIT_BREAKER_RULES.yaml").read_text(encoding="utf-8"))
BENCH_JSON = json.loads((G5 / "EVAL_DATASET_BENCHMARKS.json").read_text(encoding="utf-8"))

# All 15 G4 failure mode IDs (must appear in circuit breaker trip triggers)
ALL_FM_IDS = {
    "FM-TIMEOUT", "FM-REGION-COLLISION", "FM-BUDGET-CEILING",
    "FM-CARD-INVALID", "FM-POLICY-DENY", "FM-NESTING-VIOLATION",
    "FM-CONCURRENCY-CAP", "FM-GOTO-LEAK", "FM-PARTIAL-JOIN",
    "FM-SESSION-TRANSLATION", "FM-TRUST-DECAY", "FM-REMOTE-A2A-OUTAGE",
    "FM-PAYMENT-HOLD-STALL", "FM-CRITIC-LOOP", "FM-SECRET-LEAK",
}

# Secret detection regex (min-length 20 to avoid prose false positives)
SECRET_RX = re.compile(
    r"(api[_-]?key\s*[:=]\s*['\"][^'\"]{8,}['\"]|"
    r"Bearer\s+[A-Za-z0-9\-._~+/]{20,}={0,2}|"
    r"sk-[A-Za-z0-9]{20,})",
    re.I,
)


class TestEvaluationHarnessSpec(unittest.TestCase):
    """ST-G5-01 through ST-G5-10: EVALUATION_HARNESS_SPEC.md compliance."""

    def test_trajectory_six_fields(self) -> None:
        """ST-G5-01: Trajectory schema has all 6 required fields."""
        for field in ["Mission", "Scene", "Thought", "Action", "Observation", "Verdict"]:
            self.assertIn(field, SPEC_MD, f"trajectory field '{field}' missing")

    def test_trajectory_json_schema_fields(self) -> None:
        """Trajectory envelope has trajectory_id, parent_trajectory_id, agbom_snapshot."""
        for field in ["trajectory_id", "parent_trajectory_id", "agbom_snapshot"]:
            self.assertIn(field, SPEC_MD, f"JSON schema field '{field}' missing")

    def test_dual_judge_framework(self) -> None:
        """ST-G5-02: LLM-as-a-Judge and Agent-as-a-Judge sections present."""
        self.assertIn("LLM-as-a-Judge", SPEC_MD)
        self.assertIn("Agent-as-a-Judge", SPEC_MD)

    def test_pairwise_comparison(self) -> None:
        """Pairwise comparison method present (WP-F4 Applied Tip)."""
        self.assertIn("pairwise comparison", SPEC_MD.lower())

    def test_bias_mitigation(self) -> None:
        """Three bias mitigations present (position, verbosity, self-enhancement)."""
        spec_lower = SPEC_MD.lower()
        self.assertIn("position bias", spec_lower)
        self.assertIn("verbosity bias", spec_lower)
        self.assertIn("self-enhancement bias", spec_lower)

    def test_outside_in_hierarchy(self) -> None:
        """ST-G5-03: Outside-In and Inside-Out (Glass Box) subsections present."""
        self.assertIn("Outside-In", SPEC_MD)
        self.assertIn("Inside-Out", SPEC_MD)
        self.assertIn("Glass Box", SPEC_MD)

    def test_intent_drift_trust_decay(self) -> None:
        """WP-S4 concepts: Intent Drift and Trust Decay present."""
        self.assertIn("Intent Drift", SPEC_MD)
        self.assertIn("Trust Decay", SPEC_MD)

    def test_seven_pillars(self) -> None:
        """ST-G5-04: 7 pillars enumerated with P1-P7 IDs."""
        for i in range(1, 8):
            self.assertIn(f"P{i}", SPEC_MD, f"pillar P{i} missing")

    def test_degradation_thresholds(self) -> None:
        """ST-G5-05: 5% and 15% degradation thresholds present."""
        self.assertIn("5%", SPEC_MD)
        self.assertIn("15%", SPEC_MD)

    def test_red_blue_green(self) -> None:
        """ST-G5-06: Red/Blue/Green rotation present."""
        for team in ["Red", "Blue", "Green"]:
            self.assertIn(team, SPEC_MD, f"team '{team}' missing")

    def test_flywheel_five_steps(self) -> None:
        """ST-G5-07: Flywheel cycle has 5 steps."""
        self.assertIn("Flywheel", SPEC_MD)
        flywheel_keywords = [
            "DEFINE QUALITY",
            "INSTRUMENT FOR VISIBILITY",
            "EVALUATE",
            "ACT ON FINDINGS",
            "FEED INTO IMPROVEMENT",
        ]
        spec_upper = SPEC_MD.upper()
        for kw in flywheel_keywords:
            self.assertIn(kw, spec_upper, f"flywheel step '{kw}' missing")

    def test_option2_recommended(self) -> None:
        """ST-G5-08: OPTION_2_STANDARD marked as recommended path."""
        self.assertIn("OPTION_2_STANDARD", SPEC_MD)
        self.assertIn("★", SPEC_MD)

    def test_resume_token(self) -> None:
        """ST-G5-09: BLUE resume token G5_EVAL_FRAMEWORK_APPROVED_v1 present."""
        self.assertIn("G5_EVAL_FRAMEWORK_APPROVED_v1", SPEC_MD)

    def test_no_secrets(self) -> None:
        """ST-G5-10: No secrets or API keys in spec body."""
        self.assertFalse(
            SECRET_RX.search(SPEC_MD),
            "possible secret detected in EVALUATION_HARNESS_SPEC.md",
        )


class TestObservabilityPillars(unittest.TestCase):
    """OBSERVABILITY_PILLARS_SPEC.yaml structural invariants."""

    def test_yaml_safe_load(self) -> None:
        """YAML parses without error."""
        self.assertIsInstance(OBS_YAML, dict)

    def test_domain_overlay(self) -> None:
        """Domain and overlay match OPTION_2_STANDARD."""
        self.assertEqual(OBS_YAML["domain"], "G5")
        self.assertEqual(OBS_YAML["overlay"], "OPTION_2_STANDARD")

    def test_resume_token(self) -> None:
        """BLUE resume token and alias present."""
        self.assertEqual(OBS_YAML["resume_token_authoritative"], "G5_EVAL_FRAMEWORK_APPROVED_v1")
        self.assertEqual(OBS_YAML["resume_token_alias"], "G5_EVAL_APPROVED_v1")

    def test_upstream_tag(self) -> None:
        """Upstream tag matches G4 lock."""
        self.assertEqual(OBS_YAML["upstream_tag"], "orchestration-v1.0.0")

    def test_five_otel_span_types(self) -> None:
        """5 OTEL span types: root, agent, tool, delegate, eval."""
        spans = OBS_YAML["otel_tracing"]["span_hierarchy"]
        for span_name in ["root_span", "agent_span", "tool_span", "delegate_span", "eval_span"]:
            self.assertIn(span_name, spans, f"span type '{span_name}' missing")

    def test_json_logging_format(self) -> None:
        """Structured logging format is JSON with PII scrubbing."""
        self.assertEqual(OBS_YAML["structured_logging"]["format"], "JSON")
        self.assertTrue(OBS_YAML["structured_logging"]["pii_scrubbing"])

    def test_log_envelope_correlation_ids(self) -> None:
        """session_id, agent_id, trace_id in log envelope required fields."""
        required = OBS_YAML["structured_logging"]["log_envelope"]["required_fields"]
        required_str = " ".join(required)
        self.assertIn("session_id", required_str)
        self.assertIn("agent_id", required_str)
        self.assertIn("trace_id", required_str)

    def test_g3_hooks_count(self) -> None:
        """G3 memory telemetry hooks >= 4."""
        hooks = OBS_YAML["telemetry_hooks_g3_memory"]["hooks"]
        self.assertGreaterEqual(len(hooks), 4)

    def test_g4_ap2_hooks_count(self) -> None:
        """G4 AP2 telemetry hooks >= 4."""
        hooks = OBS_YAML["telemetry_hooks_g4_ap2"]["hooks"]
        self.assertGreaterEqual(len(hooks), 4)

    def test_g4_policy_hooks_count(self) -> None:
        """G4 policy telemetry hooks >= 2."""
        hooks = OBS_YAML["telemetry_hooks_g4_policy"]["hooks"]
        self.assertGreaterEqual(len(hooks), 2)

    def test_g4_fm_hooks_count(self) -> None:
        """G4 failure mode telemetry hooks == 15 (one per FM)."""
        hooks = OBS_YAML["telemetry_hooks_g4_failure_modes"]["hooks"]
        self.assertEqual(len(hooks), 15)

    def test_g4_fm_hook_ids_match(self) -> None:
        """All 15 G4 FM IDs present in hook fm_id fields."""
        hooks = OBS_YAML["telemetry_hooks_g4_failure_modes"]["hooks"]
        hook_fm_ids = {h["fm_id"] for h in hooks}
        self.assertEqual(hook_fm_ids, ALL_FM_IDS)

    def test_system_metrics_count(self) -> None:
        """System metrics >= 5."""
        metrics = OBS_YAML["metrics"]["system_metrics"]
        self.assertGreaterEqual(len(metrics), 5)

    def test_quality_metrics_count(self) -> None:
        """Quality metrics >= 9."""
        metrics = OBS_YAML["metrics"]["quality_metrics"]
        self.assertGreaterEqual(len(metrics), 9)

    def test_dashboard_panels_count(self) -> None:
        """Dashboard panels >= 6."""
        panels = OBS_YAML["dashboard"]["panels"]
        self.assertGreaterEqual(len(panels), 6)

    def test_pii_scrubbing_pipeline(self) -> None:
        """PII scrubbing pipeline has 3 steps: detect, scrub, audit."""
        steps = OBS_YAML["pii_scrubbing"]["pipeline"]
        self.assertEqual(len(steps), 3)

    def test_no_secrets(self) -> None:
        """No secrets in observability spec."""
        raw = (G5 / "OBSERVABILITY_PILLARS_SPEC.yaml").read_text(encoding="utf-8")
        self.assertFalse(SECRET_RX.search(raw), "possible secret in OBSERVABILITY_PILLARS_SPEC.yaml")


class TestCircuitBreakerRules(unittest.TestCase):
    """CIRCUIT_BREAKER_RULES.yaml structural invariants."""

    def test_yaml_safe_load(self) -> None:
        """YAML parses without error."""
        self.assertIsInstance(CB_YAML, dict)

    def test_trust_score_range(self) -> None:
        """Trust score range [0.0, 1.0]."""
        ts = CB_YAML["trust_score"]
        self.assertEqual(ts["range"], [0.0, 1.0])

    def test_trust_score_initial(self) -> None:
        """Initial trust score is 1.0."""
        self.assertEqual(CB_YAML["trust_score"]["initial"], 1.0)

    def test_trust_score_monotonic_decreasing(self) -> None:
        """Trust score decays monotonically."""
        self.assertEqual(CB_YAML["trust_score"]["decay_direction"], "monotonically_decreasing")

    def test_auto_restore_false(self) -> None:
        """Auto-restore is false (WP-S4: manual_hitl only)."""
        self.assertFalse(CB_YAML["trust_score"]["auto_restore"])

    def test_restore_method_manual_hitl(self) -> None:
        """Restore method is manual_hitl."""
        self.assertEqual(CB_YAML["trust_score"]["restore_method"], "manual_hitl")

    def test_decay_penalties_count(self) -> None:
        """18 decay penalties (PEN-01 through PEN-18)."""
        penalties = CB_YAML["decay_penalties"]
        self.assertEqual(len(penalties), 18)

    def test_decay_penalty_ids(self) -> None:
        """Penalty IDs are PEN-01 through PEN-18, all unique."""
        penalties = CB_YAML["decay_penalties"]
        ids = [p["id"] for p in penalties]
        expected = [f"PEN-{i:02d}" for i in range(1, 19)]
        self.assertEqual(ids, expected)
        self.assertEqual(len(ids), len(set(ids)))

    def test_trip_thresholds(self) -> None:
        """Trip thresholds: warning 0.85, hitl_review 0.70, trip 0.50."""
        tt = CB_YAML["trip_thresholds"]
        self.assertEqual(tt["warning"], 0.85)
        self.assertEqual(tt["hitl_review"], 0.70)
        self.assertEqual(tt["trip"], 0.50)

    def test_immediate_trip_signals(self) -> None:
        """3 immediate-trip CRITICAL signals: secret, pii, budget."""
        signals = CB_YAML["trip_thresholds"]["immediate_trip_signals"]
        self.assertEqual(len(signals), 3)
        self.assertIn("secret_detected", signals)
        self.assertIn("pii_leakage_detected", signals)
        self.assertIn("budget_ceiling_breach", signals)

    def test_trip_triggers_count(self) -> None:
        """15 trip triggers (one per G4 failure mode)."""
        triggers = CB_YAML["trip_triggers"]
        self.assertEqual(len(triggers), 15)

    def test_trip_triggers_all_fm_ids(self) -> None:
        """All 15 G4 FM IDs present in trip triggers."""
        trigger_fm_ids = {t["fm_id"] for t in CB_YAML["trip_triggers"]}
        self.assertEqual(trigger_fm_ids, ALL_FM_IDS)

    def test_immediate_trip_fms(self) -> None:
        """FM-BUDGET-CEILING and FM-SECRET-LEAK have immediate_trip: true."""
        triggers = {t["fm_id"]: t for t in CB_YAML["trip_triggers"]}
        self.assertTrue(triggers["FM-BUDGET-CEILING"]["immediate_trip"])
        self.assertTrue(triggers["FM-SECRET-LEAK"]["immediate_trip"])

    def test_quarantine_states_count(self) -> None:
        """6 quarantine states."""
        states = CB_YAML["quarantine_states"]
        self.assertEqual(len(states), 6)

    def test_quarantine_state_ids(self) -> None:
        """Quarantine states: QS-HEALTHY through QS-LOCKED."""
        states = CB_YAML["quarantine_states"]
        ids = [s["id"] for s in states]
        expected = [
            "QS-HEALTHY", "QS-WARNING", "QS-HITL_REVIEW",
            "QS-TRIPPED", "QS-QUARANTINE_REVIEW", "QS-LOCKED",
        ]
        self.assertEqual(ids, expected)

    def test_actions_on_trip(self) -> None:
        """Actions include freeze, revoke JIT, rollback."""
        actions = CB_YAML["actions_on_trip"]
        self.assertIn("freeze_autonomous_execution", actions)
        self.assertIn("revoke_jit_tokens", actions)
        self.assertIn("rollback_to_last_checkpoint", actions)

    def test_agbom_fields(self) -> None:
        """AgBOM has required fields."""
        agbom = CB_YAML["agbom"]
        self.assertIn("fields", agbom)
        self.assertGreater(len(agbom["fields"]), 0)

    def test_agbom_drift_detection(self) -> None:
        """AgBOM drift detection present."""
        self.assertIn("drift_detection", CB_YAML["agbom"])

    def test_checkpoint_protocol(self) -> None:
        """Checkpoint protocol present with rollback."""
        cp = CB_YAML["checkpoint_protocol"]
        self.assertIn("rollback", cp)

    def test_no_secrets(self) -> None:
        """No secrets in circuit breaker spec."""
        raw = (G5 / "CIRCUIT_BREAKER_RULES.yaml").read_text(encoding="utf-8")
        self.assertFalse(SECRET_RX.search(raw), "possible secret in CIRCUIT_BREAKER_RULES.yaml")


class TestEvalDatasetBenchmarks(unittest.TestCase):
    """EVAL_DATASET_BENCHMARKS.json structural invariants."""

    def test_json_parse(self) -> None:
        """JSON parses without error."""
        self.assertIsInstance(BENCH_JSON, dict)

    def test_scenario_count(self) -> None:
        """18 scenarios >= 15 required."""
        scenarios = BENCH_JSON["scenarios"]
        self.assertGreaterEqual(len(scenarios), 15)
        self.assertEqual(len(scenarios), 18)

    def test_scenario_ids_unique(self) -> None:
        """All scenario IDs are unique."""
        scenarios = BENCH_JSON["scenarios"]
        ids = [s["id"] for s in scenarios]
        self.assertEqual(len(ids), len(set(ids)))

    def test_scenario_required_fields(self) -> None:
        """Each scenario has id, name, failure_mode, category, expected_verdict, expected_trust_score_delta."""
        required = {
            "id", "name", "failure_mode", "category",
            "expected_verdict", "expected_trust_score_delta",
        }
        for s in BENCH_JSON["scenarios"]:
            missing = required - set(s.keys())
            self.assertFalse(missing, f"scenario {s.get('id', '?')} missing: {missing}")

    def test_failure_mode_scenarios_count(self) -> None:
        """>= 12 failure mode scenarios."""
        fm_count = sum(
            1 for s in BENCH_JSON["scenarios"]
            if s["category"] == "failure_mode"
        )
        self.assertGreaterEqual(fm_count, 12)

    def test_edge_case_scenarios_count(self) -> None:
        """>= 2 edge case scenarios."""
        ec_count = sum(
            1 for s in BENCH_JSON["scenarios"]
            if s["category"] == "edge_case"
        )
        self.assertGreaterEqual(ec_count, 2)

    def test_red_team_scenario(self) -> None:
        """1 red team scenario present."""
        rt_count = sum(
            1 for s in BENCH_JSON["scenarios"]
            if s["category"] == "red_team"
        )
        self.assertEqual(rt_count, 1)

    def test_quality_eval_scenario(self) -> None:
        """1 quality eval scenario present."""
        qe_count = sum(
            1 for s in BENCH_JSON["scenarios"]
            if s["category"] == "quality_eval"
        )
        self.assertEqual(qe_count, 1)

    def test_threshold_scenarios_count(self) -> None:
        """2 threshold scenarios (5% and 15%)."""
        th_count = sum(
            1 for s in BENCH_JSON["scenarios"]
            if s["category"] == "threshold"
        )
        self.assertEqual(th_count, 2)

    def test_g4_fm_coverage(self) -> None:
        """G4 FM coverage >= 12 in coverage matrix."""
        covered = BENCH_JSON["coverage_matrix"]["g4_failure_modes_covered"]
        self.assertGreaterEqual(len(covered), 12)

    def test_threshold_5pct_scenario(self) -> None:
        """5% threshold scenario exists."""
        th_scenarios = [s for s in BENCH_JSON["scenarios"] if s["category"] == "threshold"]
        found_5pct = any("5%" in s.get("name", "") or "@5pct" in str(s.get("tags", [])) for s in th_scenarios)
        self.assertTrue(found_5pct, "no 5% threshold scenario")

    def test_threshold_15pct_scenario(self) -> None:
        """15% threshold scenario exists."""
        th_scenarios = [s for s in BENCH_JSON["scenarios"] if s["category"] == "threshold"]
        found_15pct = any("15%" in s.get("name", "") or "@15pct" in str(s.get("tags", [])) for s in th_scenarios)
        self.assertTrue(found_15pct, "no 15% threshold scenario")

    def test_critical_severity_scenarios(self) -> None:
        """Critical severity scenarios present (secret, budget, pii)."""
        crit = [s for s in BENCH_JSON["scenarios"] if s.get("severity") == "CRITICAL"]
        self.assertGreaterEqual(len(crit), 3)

    def test_immediate_trip_scenarios(self) -> None:
        """Scenarios with expected_circuit_breaker_trip == true exist."""
        trip_scenarios = [s for s in BENCH_JSON["scenarios"] if s.get("expected_circuit_breaker_trip") is True]
        self.assertGreaterEqual(len(trip_scenarios), 3)

    def test_no_secrets(self) -> None:
        """No secrets in benchmark JSON."""
        raw = (G5 / "EVAL_DATASET_BENCHMARKS.json").read_text(encoding="utf-8")
        self.assertFalse(SECRET_RX.search(raw), "possible secret in EVAL_DATASET_BENCHMARKS.json")


class TestCrossArtifactConsistency(unittest.TestCase):
    """All 4 artifacts reference the same token, tag, and overlay."""

    def test_resume_token_consistency(self) -> None:
        """All artifacts reference G5_EVAL_FRAMEWORK_APPROVED_v1."""
        self.assertIn("G5_EVAL_FRAMEWORK_APPROVED_v1", SPEC_MD)
        self.assertEqual(OBS_YAML["resume_token_authoritative"], "G5_EVAL_FRAMEWORK_APPROVED_v1")
        self.assertEqual(CB_YAML["resume_token_authoritative"], "G5_EVAL_FRAMEWORK_APPROVED_v1")
        self.assertEqual(BENCH_JSON["resume_token_authoritative"], "G5_EVAL_FRAMEWORK_APPROVED_v1")

    def test_upstream_tag_consistency(self) -> None:
        """All artifacts reference orchestration-v1.0.0."""
        self.assertIn("orchestration-v1.0.0", SPEC_MD)
        self.assertEqual(OBS_YAML["upstream_tag"], "orchestration-v1.0.0")
        self.assertEqual(CB_YAML["upstream_tag"], "orchestration-v1.0.0")
        self.assertEqual(BENCH_JSON["upstream_tag"], "orchestration-v1.0.0")

    def test_overlay_consistency(self) -> None:
        """All artifacts use OPTION_2_STANDARD."""
        self.assertIn("OPTION_2_STANDARD", SPEC_MD)
        self.assertEqual(OBS_YAML["overlay"], "OPTION_2_STANDARD")
        self.assertEqual(CB_YAML["overlay"], "OPTION_2_STANDARD")
        self.assertEqual(BENCH_JSON["overlay"], "OPTION_2_STANDARD")


class TestSecretScan(unittest.TestCase):
    """Step E invariant: no secrets in entire G5 pack."""

    def test_no_secrets_in_pack(self) -> None:
        for p in G5.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in {".md", ".yaml", ".yml", ".json"}:
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
            self.assertFalse(
                SECRET_RX.search(text),
                f"possible secret in {p.relative_to(G5)}",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
