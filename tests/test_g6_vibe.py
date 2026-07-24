#!/usr/bin/env python3
"""G6 Vibe Coding / Agentic IDEs — Structural Tests (stdlib unittest).

Tests cover:
  - VIBECODING_SPECTRUM.md structure and content
  - SURFACE_CAPABILITY_MATRIX.yaml keys and values
  - vibe_environment.yaml configuration correctness
  - slash_command_mappings.yaml routing and BLUE commands
  - AGENTS_INHERITANCE_RULES.md inheritance rules
  - Cross-artifact consistency
  - Secret scan
  - G5 inheritance checks

Run: python -m unittest tests.test_g6_vibe -v
"""

import os
import re
import sys
import unittest

try:
    import yaml
except ImportError:
    yaml = None

# Resolve workspace root
WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G6_DIR = os.path.join(WORKSPACE, "specs", "g6_vibe")

SECRET_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"Bearer\s+[a-zA-Z0-9]{20,}"),
    re.compile(r"AIza[a-zA-Z0-9]{35}"),
]


def read_file(name):
    path = os.path.join(G6_DIR, name)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def scan_secrets(text):
    found = []
    for pat in SECRET_PATTERNS:
        found.extend(pat.findall(text))
    return found


class TestArtifactExistence(unittest.TestCase):
    """Verify all 5 G6 artifacts exist."""

    REQUIRED = [
        "VIBECODING_SPECTRUM.md",
        "SURFACE_CAPABILITY_MATRIX.yaml",
        "vibe_environment.yaml",
        "slash_command_mappings.yaml",
        "AGENTS_INHERITANCE_RULES.md",
        "G6_MIGRATION_CONTEXT.md",
    ]

    def test_artifacts_exist(self):
        for name in self.REQUIRED:
            with self.subTest(artifact=name):
                content = read_file(name)
                self.assertIsNotNone(content, f"Missing artifact: {name}")

    def test_no_stale_files(self):
        """No ephemeral/extract scripts should remain in g6_vibe/."""
        if not os.path.isdir(G6_DIR):
            self.skipTest("g6_vibe directory not found")
        stale_patterns = ["_extract", "_verify", "_tmp", ".pyc"]
        for f in os.listdir(G6_DIR):
            for pat in stale_patterns:
                self.assertFalse(
                    pat in f,
                    f"Stale file found in g6_vibe/: {f} (matched pattern: {pat})",
                )


@unittest.skipIf(yaml is None, "PyYAML not available")
class TestVIBECODINGSpectrum(unittest.TestCase):
    """Test VIBECODING_SPECTRUM.md structure and content."""

    @classmethod
    def setUpClass(cls):
        cls.content = read_file("VIBECODING_SPECTRUM.md")
        cls.lower = cls.content.lower() if cls.content else ""

    def test_domain_and_status(self):
        self.assertIn("g6", self.lower)
        self.assertIn("draft_pre_gate", self.lower)

    def test_resume_token(self):
        self.assertIn("g6_vibe_env_locked_v1", self.lower)

    def test_upstream_tag(self):
        self.assertIn("eval-v1.0.0", self.lower)

    def test_option_matrix(self):
        self.assertIn("option_1_conservative", self.lower)
        self.assertIn("option_2_standard", self.lower)
        self.assertIn("option_3_creative", self.lower)
        self.assertIn("\u2605", self.content)  # star marks recommended

    def test_whitepaper_references(self):
        self.assertIn("wp-s1", self.lower)
        self.assertIn("wp-s5", self.lower)
        self.assertIn("wp-f5", self.lower)

    def test_developer_modes(self):
        self.assertIn("conductor", self.lower)
        self.assertIn("orchestrator", self.lower)

    def test_spectrum_terms(self):
        self.assertIn("vibe coding", self.lower)
        self.assertIn("agentic engineering", self.lower)

    def test_prototype_dune(self):
        self.assertIn("prototype dune", self.lower)

    def test_transition_triggers(self):
        self.assertIn("transition trigger", self.lower)

    def test_sdd_pattern(self):
        self.assertTrue(
            "spec-driven" in self.lower or "sdd" in self.lower,
            "SDD pattern must be documented",
        )

    def test_model_routing_matrix(self):
        self.assertIn("premium frontier", self.lower)
        self.assertIn("strong coding", self.lower)
        self.assertIn("fast flash", self.lower)

    def test_surface_comparison(self):
        self.assertIn("antigravity", self.lower)
        self.assertIn("hermes", self.lower)

    def test_no_yolo_boundary(self):
        self.assertIn("no yolo", self.lower)

    def test_gherkin(self):
        self.assertIn("gherkin", self.lower)

    def test_token_economics(self):
        self.assertIn("token econom", self.lower)

    def test_g5_inheritance(self):
        self.assertIn("circuit breaker", self.lower)
        self.assertIn("trajectory", self.lower)
        self.assertIn("trust score", self.lower)

    def test_structural_test_intents(self):
        st_count = len(re.findall(r"ST-G6-\d+", self.content))
        self.assertGreaterEqual(st_count, 8, f"Expected >= 8 ST-G6 intents, found {st_count}")

    def test_no_secrets(self):
        secrets = scan_secrets(self.content)
        self.assertEqual(len(secrets), 0, f"Secrets found: {secrets}")


@unittest.skipIf(yaml is None, "PyYAML not available")
class TestSurfaceCapabilityMatrix(unittest.TestCase):
    """Test SURFACE_CAPABILITY_MATRIX.yaml."""

    @classmethod
    def setUpClass(cls):
        cls.raw = read_file("SURFACE_CAPABILITY_MATRIX.yaml")
        cls.data = yaml.safe_load(cls.raw) if cls.raw else None

    def test_yaml_loads(self):
        self.assertIsNotNone(self.data)

    def test_domain(self):
        self.assertEqual(self.data.get("domain"), "G6")

    def test_status(self):
        self.assertEqual(self.data.get("status"), "DRAFT_PRE_GATE")

    def test_overlay(self):
        self.assertEqual(self.data.get("overlay"), "OPTION_2_STANDARD")

    def test_upstream_tag(self):
        self.assertEqual(self.data.get("upstream_tag"), "eval-v1.0.0")

    def test_resume_token(self):
        self.assertEqual(self.data.get("blue_resume_token"), "G6_VIBE_ENV_LOCKED_v1")

    def test_surfaces_present(self):
        surfaces = self.data.get("surfaces", {})
        for s in ["hermes_cli", "antigravity_cli", "serverless_agent_engine"]:
            self.assertIn(s, surfaces, f"Missing surface: {s}")

    def test_blue_slash_commands(self):
        bc = self.data.get("blue_slash_commands", {})
        for cmd in ["/goal", "/grill-me", "/browser", "/schedule"]:
            self.assertIn(cmd, bc, f"Missing BLUE command: {cmd}")

    def test_hooks(self):
        hooks = self.data.get("hooks", {})
        for h in ["pre_tool", "post_file_edit", "pre_commit", "approval_bypass"]:
            self.assertIn(h, hooks, f"Missing hook: {h}")

    def test_ide_extensions(self):
        ide = self.data.get("ide_extensions", {})
        for i in ["vscode", "zed", "jetbrains"]:
            self.assertIn(i, ide, f"Missing IDE extension: {i}")

    def test_skills_hub(self):
        hub = self.data.get("skills_hub", {})
        self.assertGreaterEqual(hub.get("total_skills", 0), 50)

    def test_procurement_gaps(self):
        proc = self.data.get("procurement_summary", {})
        self.assertGreater(len(proc.get("gaps", [])), 0)

    def test_no_secrets(self):
        secrets = scan_secrets(self.raw)
        self.assertEqual(len(secrets), 0)


@unittest.skipIf(yaml is None, "PyYAML not available")
class TestVibeEnvironment(unittest.TestCase):
    """Test vibe_environment.yaml."""

    @classmethod
    def setUpClass(cls):
        cls.raw = read_file("vibe_environment.yaml")
        cls.data = yaml.safe_load(cls.raw) if cls.raw else None

    def test_yaml_loads(self):
        self.assertIsNotNone(self.data)

    def test_domain(self):
        self.assertEqual(self.data.get("domain"), "G6")

    def test_overlay(self):
        self.assertEqual(self.data.get("overlay"), "OPTION_2_STANDARD")

    def test_resume_token(self):
        self.assertEqual(self.data.get("blue_resume_token"), "G6_VIBE_ENV_LOCKED_v1")

    def test_workspace_modes(self):
        wm = self.data.get("workspace_mode", {})
        self.assertIn("prototype_dune", wm)
        self.assertIn("production_path", wm)
        self.assertTrue(wm.get("prototype_dune", {}).get("enabled"))
        self.assertTrue(wm.get("production_path", {}).get("enabled"))

    def test_transition_triggers(self):
        tts = self.data.get("transition_triggers", [])
        self.assertGreaterEqual(len(tts), 9, f"Expected >= 9 triggers, got {len(tts)}")
        ids = [t.get("id") for t in tts]
        self.assertIn("TT-01", ids)
        self.assertIn("TT-09", ids)

    def test_surface_posture(self):
        sp = self.data.get("surface_posture", {})
        self.assertEqual(sp.get("primary"), "hermes_cli")
        self.assertEqual(sp.get("secondary"), "antigravity_cli")

    def test_sdd(self):
        sdd = self.data.get("sdd", {})
        self.assertTrue(sdd.get("enabled"))
        self.assertEqual(sdd.get("spec_format"), "hybrid_markdown_yaml")
        self.assertEqual(sdd.get("bdd_syntax"), "gherkin")

    def test_g5_integration_keys(self):
        g5 = self.data.get("g5_integration", {})
        for key in ["trajectory_schema", "trust_score", "circuit_breaker",
                     "checkpoint_protocol", "pii_scrubbing", "llm_as_judge", "agbom"]:
            self.assertIn(key, g5, f"Missing G5 integration key: {key}")

    def test_hooks_declared(self):
        hooks = self.data.get("hooks", {})
        for h in ["pre_tool", "post_file_edit", "pre_commit", "approval_bypass"]:
            self.assertIn(h, hooks, f"Missing hook: {h}")

    def test_constraints_inherited(self):
        cl = self.data.get("constraints_inherited", [])
        self.assertGreaterEqual(len(cl), 15, f"Expected >= 15 constraints, got {len(cl)}")

    def test_no_secrets(self):
        secrets = scan_secrets(self.raw)
        self.assertEqual(len(secrets), 0)


@unittest.skipIf(yaml is None, "PyYAML not available")
class TestSlashCommandMappings(unittest.TestCase):
    """Test slash_command_mappings.yaml."""

    @classmethod
    def setUpClass(cls):
        cls.raw = read_file("slash_command_mappings.yaml")
        cls.data = yaml.safe_load(cls.raw) if cls.raw else None

    def test_yaml_loads(self):
        self.assertIsNotNone(self.data)

    def test_domain(self):
        self.assertEqual(self.data.get("domain"), "G6")

    def test_overlay(self):
        self.assertEqual(self.data.get("overlay"), "OPTION_2_STANDARD")

    def test_blue_commands(self):
        bc = self.data.get("blue_commands", {})
        for cmd in ["/goal", "/grill-me", "/browser", "/schedule"]:
            self.assertIn(cmd, bc, f"Missing BLUE command: {cmd}")

    def test_goal_hermes_native(self):
        goal = self.data.get("blue_commands", {}).get("/goal", {})
        self.assertTrue(goal.get("hermes_native"))

    def test_grill_me_not_native(self):
        grill = self.data.get("blue_commands", {}).get("/grill-me", {})
        self.assertFalse(grill.get("hermes_native"))
        self.assertEqual(grill.get("model_tier"), "premium_frontier")

    def test_schedule_maps_to_cron(self):
        sched = self.data.get("blue_commands", {}).get("/schedule", {})
        self.assertEqual(sched.get("hermes_command"), "/cron")

    def test_yolo_mapped(self):
        native = self.data.get("hermes_native_commands", {})
        self.assertIn("/yolo", native.get("configuration", {}))

    def test_routing_matrix_size(self):
        rm = self.data.get("routing_matrix", [])
        self.assertGreaterEqual(len(rm), 8, f"Expected >= 8 routing entries, got {len(rm)}")

    def test_no_secrets(self):
        secrets = scan_secrets(self.raw)
        self.assertEqual(len(secrets), 0)


class TestAGENTSInheritanceRules(unittest.TestCase):
    """Test AGENTS_INHERITANCE_RULES.md."""

    @classmethod
    def setUpClass(cls):
        cls.content = read_file("AGENTS_INHERITANCE_RULES.md")
        cls.lower = cls.content.lower() if cls.content else ""

    def test_domain_and_status(self):
        self.assertIn("g6", self.lower)
        self.assertIn("draft_pre_gate", self.lower)

    def test_resume_token(self):
        self.assertIn("g6_vibe_env_locked_v1", self.lower)

    def test_inheritance_principle(self):
        self.assertIn("inheritance", self.lower)

    def test_tightening_rules(self):
        self.assertIn("tighten", self.lower)

    def test_relaxation_forbidden(self):
        self.assertIn("relax", self.lower)

    def test_prototype_dune(self):
        self.assertIn("prototype dune", self.lower)

    def test_wsl2(self):
        self.assertIn("wsl2", self.lower)

    def test_hitl(self):
        self.assertIn("hitl", self.lower)

    def test_surfaces_documented(self):
        for s in ["hermes cli", "antigravity", "delegate", "cron"]:
            self.assertIn(s, self.lower, f"Missing surface: {s}")

    def test_g5_inheritance(self):
        self.assertIn("circuit breaker", self.lower)
        self.assertIn("trajectory", self.lower)
        self.assertIn("trust score", self.lower)

    def test_yolo_rules(self):
        self.assertIn("yolo", self.lower)

    def test_conflict_resolution(self):
        self.assertIn("conflict resolution", self.lower)

    def test_precedence(self):
        self.assertIn("precedence", self.lower)

    def test_no_secrets(self):
        secrets = scan_secrets(self.content)
        self.assertEqual(len(secrets), 0)


class TestCrossArtifactConsistency(unittest.TestCase):
    """Verify all G6 artifacts share consistent references."""

    @classmethod
    def setUpClass(cls):
        cls.all_content = ""
        for name in [
            "VIBECODING_SPECTRUM.md",
            "SURFACE_CAPABILITY_MATRIX.yaml",
            "vibe_environment.yaml",
            "slash_command_mappings.yaml",
            "AGENTS_INHERITANCE_RULES.md",
            "G6_MIGRATION_CONTEXT.md",
        ]:
            c = read_file(name)
            if c:
                cls.all_content += c + "\n"

    def test_resume_token_consistency(self):
        self.assertIn("G6_VIBE_ENV_LOCKED_v1", self.all_content)

    def test_upstream_tag_consistency(self):
        self.assertIn("eval-v1.0.0", self.all_content)

    def test_option_consistency(self):
        self.assertIn("OPTION_2_STANDARD", self.all_content)

    def test_no_secrets_any_artifact(self):
        secrets = scan_secrets(self.all_content)
        self.assertEqual(len(secrets), 0, f"Secrets found across artifacts: {secrets}")


class TestG5Inheritance(unittest.TestCase):
    """Verify G5 evaluation mechanisms are inherited correctly in G6."""

    @classmethod
    def setUpClass(cls):
        cls.ve = read_file("vibe_environment.yaml")
        cls.ve_data = yaml.safe_load(cls.ve) if cls.ve and yaml else None

    def test_trajectory_schema_inherited(self):
        g5 = self.ve_data.get("g5_integration", {})
        self.assertIn("trajectory_schema", g5)

    def test_trajectory_emission_by_mode(self):
        g5 = self.ve_data.get("g5_integration", {})
        emission = g5.get("trajectory_emission", {})
        self.assertIn("vibe_coding", emission)
        self.assertIn("agentic_engineering", emission)
        self.assertEqual(emission.get("agentic_engineering"), "mandatory")

    def test_circuit_breaker_mode_dependent(self):
        g5 = self.ve_data.get("g5_integration", {})
        cb = g5.get("circuit_breaker", {})
        self.assertEqual(cb.get("vibe_coding"), "disabled")
        self.assertEqual(cb.get("agentic_engineering"), "active_15_fm_triggers")

    def test_llm_judge_different_model_family(self):
        g5 = self.ve_data.get("g5_integration", {})
        judge = g5.get("llm_as_judge", {})
        self.assertIn("different_model_family", str(judge.get("agentic_engineering", "")))

    def test_checkpoint_protocol_mandatory_in_production(self):
        g5 = self.ve_data.get("g5_integration", {})
        cp = g5.get("checkpoint_protocol", {})
        self.assertEqual(cp.get("agentic_engineering"), "mandatory")

    def test_pii_scrubbing_mandatory_in_production(self):
        g5 = self.ve_data.get("g5_integration", {})
        pii = g5.get("pii_scrubbing", {})
        self.assertEqual(pii.get("agentic_engineering"), "mandatory")


class TestSDDPattern(unittest.TestCase):
    """Verify Spec-Driven Development pattern is correctly configured."""

    @classmethod
    def setUpClass(cls):
        cls.ve = read_file("vibe_environment.yaml")
        cls.ve_data = yaml.safe_load(cls.ve) if cls.ve and yaml else None

    def test_sdd_enabled(self):
        sdd = self.ve_data.get("sdd", {})
        self.assertTrue(sdd.get("enabled"))

    def test_spec_format(self):
        sdd = self.ve_data.get("sdd", {})
        self.assertEqual(sdd.get("spec_format"), "hybrid_markdown_yaml")

    def test_bdd_syntax(self):
        sdd = self.ve_data.get("sdd", {})
        self.assertEqual(sdd.get("bdd_syntax"), "gherkin")

    def test_spec_location(self):
        sdd = self.ve_data.get("sdd", {})
        self.assertEqual(sdd.get("spec_location"), "specs/")

    def test_instruction_placement(self):
        sdd = self.ve_data.get("sdd", {})
        placement = sdd.get("instruction_placement", {})
        for loc in ["chat_interface", "specs_folder", "agent_skills", "agents_md"]:
            self.assertIn(loc, placement, f"Missing instruction placement: {loc}")

    def test_token_economics_yaml_for_deep_nesting(self):
        sdd = self.ve_data.get("sdd", {})
        te = sdd.get("token_economics", {})
        self.assertTrue(te.get("yaml_for_nesting_depth_gt_3"))


class TestTransitionTriggers(unittest.TestCase):
    """Verify transition triggers are properly defined."""

    @classmethod
    def setUpClass(cls):
        cls.ve = read_file("vibe_environment.yaml")
        cls.ve_data = yaml.safe_load(cls.ve) if cls.ve and yaml else None

    def test_trigger_ids_unique(self):
        tts = self.ve_data.get("transition_triggers", [])
        ids = [t.get("id") for t in tts]
        self.assertEqual(len(ids), len(set(ids)), "Transition trigger IDs must be unique")

    def test_trigger_fields(self):
        tts = self.ve_data.get("transition_triggers", [])
        for t in tts:
            with self.subTest(trigger=t.get("id")):
                self.assertIn("id", t)
                self.assertIn("name", t)
                self.assertIn("from", t)
                self.assertIn("to", t)
                self.assertIn("condition", t)

    def test_production_deployment_trigger(self):
        tts = self.ve_data.get("transition_triggers", [])
        names = [t.get("name") for t in tts]
        self.assertIn("production_deployment", names)

    def test_agent_as_product_trigger(self):
        tts = self.ve_data.get("transition_triggers", [])
        names = [t.get("name") for t in tts]
        self.assertIn("agent_as_product", names)


def _flatten_activation(activation):
    """Flatten a YAML list-of-dicts activation block into a single dict."""
    if isinstance(activation, dict):
        return activation
    if isinstance(activation, list):
        result = {}
        for item in activation:
            if isinstance(item, str):
                result[item] = True
            elif isinstance(item, dict):
                result.update(item)
        return result
    return {}


class TestPrototypeDuneSafety(unittest.TestCase):
    """Verify prototype dune safety boundaries."""

    @classmethod
    def setUpClass(cls):
        cls.ve = read_file("vibe_environment.yaml")
        cls.ve_data = yaml.safe_load(cls.ve) if cls.ve and yaml else None

    def test_dune_no_production_secrets(self):
        dune = self.ve_data.get("workspace_mode", {}).get("prototype_dune", {})
        activation = _flatten_activation(dune.get("activation", {}))
        self.assertIn("no_production_secrets", activation)
        self.assertTrue(activation.get("no_production_secrets"))

    def test_dune_no_production_db(self):
        dune = self.ve_data.get("workspace_mode", {}).get("prototype_dune", {})
        activation = _flatten_activation(dune.get("activation", {}))
        self.assertIn("no_production_db_access", activation)

    def test_dune_circuit_breaker_disabled(self):
        dune = self.ve_data.get("workspace_mode", {}).get("prototype_dune", {})
        self.assertEqual(dune.get("circuit_breaker"), "disabled")

    def test_production_eval_gates_active(self):
        prod = self.ve_data.get("workspace_mode", {}).get("production_path", {})
        activation = _flatten_activation(prod.get("activation", {}))
        self.assertTrue(activation.get("eval_gates_active"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
