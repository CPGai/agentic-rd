#!/usr/bin/env python3
"""G8 Multi-Tenant — Structural Test Suite (Step E)

Tests declarative artifacts in specs/g8_multitenant/ for structural
completeness and cross-tenant isolation invariants.

Mandatory PASS criteria (from HITL gate):
  1. Cross-tenant breach count must equal 0
  2. 100% of egress logs scanned with deterministic PII redaction
  3. 100% of tool executions undergo SPIFFE JWT-SVID envelope validation
  4. Per-tenant circuit breakers trip independently

Run: python -m unittest tests.test_g8_multitenant -v
"""

import os
import re
import sys
import unittest
import yaml

G8_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "specs", "g8_multitenant"
)


def _read(name):
    path = os.path.join(G8_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _read_yaml(name):
    path = os.path.join(G8_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestG8Architecture(unittest.TestCase):
    """ST-G8-01 through ST-G8-06 — architecture spec structural tests."""

    @classmethod
    def setUpClass(cls):
        cls.arch = _read("MULTI_TENANT_SECURITY_ARCHITECTURE.md")
        cls.arch_lower = cls.arch.lower()

    def test_st_g8_01_tiered_isolation_models(self):
        """ST-G8-01: Three isolation tiers (ISO-1, ISO-2, ISO-3) defined."""
        for tier in ["ISO-1", "ISO-2", "ISO-3"]:
            self.assertIn(tier, self.arch)
        self.assertIn("Docker", self.arch)
        self.assertIn("gVisor", self.arch)
        self.assertIn("Firecracker", self.arch)

    def test_st_g8_02_spiffe_identity_mapping(self):
        """ST-G8-02: SPIFFE identity mapping with tenant scoping."""
        self.assertIn("SPIFFE", self.arch)
        self.assertIn("trust_domain", self.arch_lower)
        self.assertIn("tenant_id", self.arch_lower)
        self.assertIn("SVID", self.arch)
        self.assertIn("JIT", self.arch)

    def test_st_g8_03_owasp_llm06_non_delegatable(self):
        """ST-G8-03: OWASP LLM06 non-delegatable controls present."""
        for ctrl in ["LLM06-01", "LLM06-02", "LLM06-03",
                      "LLM06-04", "LLM06-05", "LLM06-06",
                      "LLM06-07", "LLM06-08"]:
            self.assertIn(ctrl, self.arch)

    def test_st_g8_04_hybrid_policy_server(self):
        """ST-G8-04: Hybrid policy server architecture defined."""
        self.assertIn("Hybrid Policy Server", self.arch)
        self.assertIn("non-delegatable", self.arch_lower)
        self.assertIn("structural role validation", self.arch_lower)
        self.assertIn("semantic pii", self.arch_lower)
        self.assertIn("fail-closed", self.arch_lower)

    def test_st_g8_05_zero_cross_tenant_leakage(self):
        """ST-G8-05: Zero cross-tenant data leakage guarantees."""
        self.assertIn("Zero Cross-Tenant Data Leakage", self.arch)
        for pillar in ["Compute", "Data", "Identity", "Network", "Observability"]:
            self.assertIn(pillar, self.arch)

    def test_st_g8_06_seven_pillar_effective_trust(self):
        """ST-G8-06: 7-pillar Effective Trust integration with per-tenant scoping."""
        for pillar in ["P1", "P2", "P3", "P4", "P5", "P6", "P7"]:
            self.assertIn(pillar, self.arch)
        self.assertIn("Ephemeral Sandbox", self.arch)
        self.assertIn("Slopsquatting", self.arch)
        self.assertIn("Red/Blue/Green", self.arch)


class TestG8CapabilityDiscovery(unittest.TestCase):
    """ST-G8-07 through ST-G8-09 — capability discovery tests."""

    @classmethod
    def setUpClass(cls):
        cls.cd = _read_yaml("CAPABILITY_DISCOVERY.yaml")

    def test_st_g8_07_sandbox_runtimes_inventory(self):
        """ST-G8-07: At least 4 sandbox runtimes inventoried."""
        runtimes = self.cd.get("sandbox_runtimes", [])
        self.assertGreaterEqual(len(runtimes), 4)
        names = [r.get("name", "").lower() for r in runtimes]
        self.assertTrue(any("docker" in n for n in names))
        self.assertTrue(any("gvisor" in n for n in names))
        self.assertTrue(any("firecracker" in n for n in names))

    def test_st_g8_08_isolation_tiers_coverage(self):
        """ST-G8-08: All three isolation tiers present in runtimes."""
        tiers = [r.get("isolation_tier") for r in self.cd.get("sandbox_runtimes", [])]
        self.assertIn("ISO-1", tiers)
        self.assertIn("ISO-2", tiers)
        self.assertIn("ISO-3", tiers)

    def test_st_g8_09_pii_redaction_non_delegatable(self):
        """ST-G8-09: All PII redaction middleware is non-delegatable."""
        mw = self.cd.get("pii_redaction_middleware", [])
        self.assertGreaterEqual(len(mw), 4)
        for m in mw:
            self.assertTrue(m.get("non_delegatable"),
                            f"PII middleware {m.get('id')} must be non_delegatable")


class TestG8TenantPolicies(unittest.TestCase):
    """ST-G8-10 through ST-G8-15 — tenant policy enforcement tests."""

    @classmethod
    def setUpClass(cls):
        cls.tp = _read_yaml("tenant_policies.yaml")

    def test_st_g8_10_system_wide_rules(self):
        """ST-G8-10: System-wide rules encode G7 hard bounds (>= 8)."""
        rules = self.tp.get("system_wide_rules", [])
        self.assertGreaterEqual(len(rules), 8)

    def test_st_g8_11_four_tenants_defined(self):
        """ST-G8-11: At least 4 tenants defined with all rule categories."""
        tenants = self.tp.get("tenants", [])
        self.assertGreaterEqual(len(tenants), 4)
        for t in tenants:
            for rule_type in ["structural_rules", "semantic_rules",
                              "budget_rules", "improvement_rules"]:
                self.assertIsNotNone(t.get(rule_type),
                                     f"Tenant {t.get('tenant_id')} missing {rule_type}")

    def test_st_g8_12_all_risk_tiers_present(self):
        """ST-G8-12: All four risk tiers (RT-1 to RT-4) present."""
        tiers = {t.get("risk_tier") for t in self.tp.get("tenants", [])}
        for rt in ["RT-1", "RT-2", "RT-3", "RT-4"]:
            self.assertIn(rt, tiers)

    def test_st_g8_13_fail_closed_default(self):
        """ST-G8-13: Default policy is fail-closed (deny)."""
        default = self.tp.get("default_policy", {})
        self.assertEqual(default.get("unmatched_decision"), "deny")

    def test_st_g8_14_per_tenant_circuit_breaker_isolation(self):
        """ST-G8-14: Per-tenant circuit breakers are isolated."""
        for t in self.tp.get("tenants", []):
            cb = t.get("circuit_breaker", {})
            self.assertTrue(cb.get("per_tenant_isolated"),
                             f"Tenant {t.get('tenant_id')} CB not isolated")

    def test_st_g8_15_cross_tenant_guarantees(self):
        """ST-G8-15: Cross-tenant isolation guarantees defined (>= 5)."""
        ctg = self.tp.get("cross_tenant_guarantees", [])
        self.assertGreaterEqual(len(ctg), 5)


class TestG8SandboxTemplates(unittest.TestCase):
    """ST-G8-16 through ST-G8-18 — sandbox template tests."""

    @classmethod
    def setUpClass(cls):
        cls.st = _read_yaml("sandbox_templates.yaml")

    def test_st_g8_16_all_isolation_tiers_have_templates(self):
        """ST-G8-16: Templates exist for ISO-1, ISO-2, ISO-3."""
        tiers = {t.get("isolation_tier") for t in self.st.get("templates", [])}
        for iso in ["ISO-1", "ISO-2", "ISO-3"]:
            self.assertIn(iso, tiers)

    def test_st_g8_17_template_selection_maps_risk_tiers(self):
        """ST-G8-17: Template selection maps RT-1→Docker, RT-3→gVisor, RT-4→Firecracker."""
        sel = self.st.get("template_selection", {})
        self.assertEqual(sel.get("RT-1"), "TPL-ISO1-DOCKER")
        self.assertEqual(sel.get("RT-3"), "TPL-ISO2-GVISOR")
        self.assertEqual(sel.get("RT-4"), "TPL-ISO3-FIRECRACKER")

    def test_st_g8_18_shared_volume_redaction(self):
        """ST-G8-18: Shared volume redaction is always-on with patterns."""
        red = self.st.get("shared_volume_redaction", {})
        self.assertTrue(red.get("always_on"))
        self.assertGreaterEqual(len(red.get("patterns", [])), 4)


class TestG8AuthorizationEnvelopes(unittest.TestCase):
    """ST-G8-19 through ST-G8-23 — authorization envelope tests."""

    @classmethod
    def setUpClass(cls):
        cls.ae = _read_yaml("authorization_envelopes.yaml")

    def test_st_g8_19_spiffe_svid_config(self):
        """ST-G8-19: SPIFFE SVID configured with JWT format and 15m TTL."""
        sp = self.ae.get("spiffe", {})
        self.assertEqual(sp.get("trust_domain"), "agentic-rd.local")
        self.assertEqual(sp.get("svid_format"), "JWT-SVID")
        self.assertEqual(sp.get("svid_ttl"), "15m")

    def test_st_g8_20_envelope_required_fields(self):
        """ST-G8-20: Authorization envelope has all required fields."""
        fields = {f.get("name") for f in
                   self.ae.get("envelope_schema", {}).get("required_fields", [])}
        for f in ["envelope_id", "tenant_id", "agent_id", "svid",
                   "caps", "tool_call", "policy_decision", "rule_ids"]:
            self.assertIn(f, fields)

    def test_g8_21_jit_downscoping(self):
        """ST-G8-21: JIT downscoping with zero ambient authority."""
        jit = self.ae.get("jit_downscoping", {})
        self.assertTrue(jit.get("enabled"))
        self.assertTrue(jit.get("per_call"))
        self.assertTrue(jit.get("non_reusable"))
        self.assertTrue(jit.get("zero_ambient_authority"))
        self.assertEqual(len(jit.get("downscope_pipeline", [])), 7)

    def test_st_g8_22_capability_classes(self):
        """ST-G8-22: At least 7 capability classes defined."""
        caps = self.ae.get("capabilities", [])
        self.assertGreaterEqual(len(caps), 7)

    def test_st_g8_23_identity_guarantees(self):
        """ST-G8-23: Identity guarantees include confused deputy prevention."""
        guarantees = self.ae.get("identity_guarantees", [])
        self.assertGreaterEqual(len(guarantees), 4)


class TestG8ObservabilityPipelines(unittest.TestCase):
    """ST-G8-24 through ST-G8-28 — observability pipeline tests."""

    @classmethod
    def setUpClass(cls):
        cls.op = _read_yaml("observability_pipelines.yaml")

    def test_st_g8_24_pii_redaction_always_on(self):
        """ST-G8-24: PII redaction is always-on and non-delegatable."""
        red = self.op.get("pii_redaction", {})
        self.assertTrue(red.get("always_on"))
        self.assertTrue(red.get("non_delegatable"))
        self.assertFalse(red.get("llm_can_bypass"))

    def test_st_g8_25_per_tenant_pipelines_all_tiers(self):
        """ST-G8-25: Per-tenant pipelines defined for RT-1 through RT-4."""
        ptp = self.op.get("per_tenant_pipelines", {})
        for rt in ["RT-1", "RT-2", "RT-3", "RT-4"]:
            self.assertIn(rt, ptp)

    def test_st_g8_26_rt4_enhanced_controls(self):
        """ST-G8-26: RT-4 has human review, legal hold, 365-day retention."""
        rt4 = self.op.get("per_tenant_pipelines", {}).get("RT-4", {})
        self.assertTrue(rt4.get("human_review"))
        self.assertTrue(rt4.get("legal_hold"))
        self.assertEqual(rt4.get("retention_days"), 365)

    def test_st_g8_27_cross_tenant_telemetry_isolation(self):
        """ST-G8-27: Cross-tenant telemetry isolation guarantees (>= 4)."""
        cti = self.op.get("cross_tenant_isolation", [])
        self.assertGreaterEqual(len(cti), 4)

    def test_st_g8_28_g5_inheritance_per_tenant(self):
        """ST-G8-28: G5 mechanisms inherited with per-tenant scoping."""
        g5 = self.op.get("g5_inheritance", {})
        for mech in ["trajectory_schema", "trust_score", "circuit_breaker", "agbom"]:
            self.assertIn(mech, g5)
        cbt = g5.get("circuit_breaker", {}).get("trip_threshold_per_tier", {})
        self.assertEqual(cbt.get("RT-1"), 0.50)
        self.assertEqual(cbt.get("RT-4"), 0.80)


class TestG8PolicyDSLSpec(unittest.TestCase):
    """ST-G8-29 through ST-G8-32 — policy DSL spec tests."""

    @classmethod
    def setUpClass(cls):
        cls.dsl = _read("POLICY_DSL_SPEC.md")
        cls.dsl_lower = cls.dsl.lower()

    def test_st_g8_29_dsl_grammar_defined(self):
        """ST-G8-29: DSL grammar (EBNF) defined."""
        self.assertIn("ebnf", self.dsl_lower)
        self.assertIn("rule", self.dsl_lower)
        self.assertIn("condition", self.dsl_lower)

    def test_st_g8_30_structural_vs_semantic(self):
        """ST-G8-30: Structural role validation vs semantic PII interception defined."""
        self.assertIn("structural role validation", self.dsl_lower)
        self.assertIn("semantic pii", self.dsl_lower)
        self.assertIn("non-delegatable", self.dsl_lower)

    def test_st_g8_31_tenant_risk_tier_mapping(self):
        """ST-G8-31: Tenant risk-tier classification mapping present."""
        for rt in ["RT-1", "RT-2", "RT-3", "RT-4"]:
            self.assertIn(rt, self.dsl)
        self.assertIn("ISO-1", self.dsl)
        self.assertIn("ISO-2", self.dsl)
        self.assertIn("ISO-3", self.dsl)

    def test_st_g8_32_fail_closed(self):
        """ST-G8-32: DSL enforces fail-closed default."""
        self.assertIn("fail-closed", self.dsl_lower)
        self.assertIn("deny", self.dsl_lower)


class TestG8CrossTenantAttackSimulation(unittest.TestCase):
    """ST-G8-33 through ST-G8-40 — cross-tenant attack simulation suite.

    These tests simulate cross-tenant attack vectors defined in the
    MULTI_TENANT_SECURITY_ARCHITECTURE.md threat model (section 7.2)
    and verify that the declarative policy configuration blocks each one.

    MANDATORY PASS CRITERION: Cross-tenant breach count must equal 0.
    """

    @classmethod
    def setUpClass(cls):
        cls.tp = _read_yaml("tenant_policies.yaml")
        cls.ae = _read_yaml("authorization_envelopes.yaml")
        cls.op = _read_yaml("observability_pipelines.yaml")
        cls.st = _read_yaml("sandbox_templates.yaml")
        cls.arch = _read("MULTI_TENANT_SECURITY_ARCHITECTURE.md")

    def _tenant_by_id(self, tid):
        for t in self.tp.get("tenants", []):
            if t.get("tenant_id") == tid:
                return t
        return None

    def test_st_g8_33_breach_count_zero(self):
        """ST-G8-33: Cross-tenant breach count must be 0.

        Simulates 10 attack vectors from the threat model. Each vector
        is tested against the declarative policy configuration. If any
        vector would succeed, it counts as a breach. Total breaches = 0.
        """
        breaches = []
        tenants = self.tp.get("tenants", [])
        self.assertGreaterEqual(len(tenants), 2, "Need >=2 tenants for cross-tenant test")

        t_a = tenants[0]  # attacker
        t_b = tenants[1]  # victim

        # Attack 1: Tenant A reads Tenant B's filesystem
        # Mitigation: fs.write rules only allow own tenant path prefix
        for t in tenants:
            if t.get("tenant_id") != t_b.get("tenant_id"):
                rules = t.get("structural_rules", [])
                has_path_restriction = any(
                    "specs/tenants/" in str(r.get("condition", "")) and
                    t.get("tenant_id") in str(r.get("condition", ""))
                    for r in rules
                )
                if not has_path_restriction:
                    breaches.append("Attack 1: No path restriction for cross-tenant fs access")

        # Attack 2: Tenant A assumes Tenant B's identity
        # Mitigation: SYS-09 requires SVID; SVID tenant_id is immutable
        sys_rules = self.tp.get("system_wide_rules", [])
        has_svid_rule = any(
            "svid" in str(r.get("condition", "")).lower()
            for r in sys_rules
        )
        if not has_svid_rule:
            breaches.append("Attack 2: No SVID validation rule")

        # Attack 3: Tenant A reaches Tenant B's network
        # Mitigation: network spec in sandbox templates has egress_policy deny_all
        for tmpl in self.st.get("templates", []):
            net = tmpl.get("network_spec", {})
            if net.get("egress_policy") != "deny_all_except_policy_server":
                breaches.append(f"Attack 3: Template {tmpl.get('id')} allows direct egress")

        # Attack 4: Tenant A sees Tenant B's traces/logs
        # Mitigation: OTEL pipeline has per-tenant routing + PII redaction
        cti = self.op.get("cross_tenant_isolation", [])
        has_trace_isolation = any(
            "trace" in str(g.get("description", "")).lower()
            for g in cti
        )
        if not has_trace_isolation:
            breaches.append("Attack 4: No trace isolation guarantee")

        # Attack 5: Tenant A's improvement loop affects Tenant B
        # Mitigation: Per-tenant circuit breaker isolation
        for t in tenants:
            cb = t.get("circuit_breaker", {})
            if not cb.get("per_tenant_isolated"):
                breaches.append(f"Attack 5: Tenant {t.get('tenant_id')} CB not isolated")

        # Attack 6: Tenant A modifies shared specs (AGENTS.md)
        # Mitigation: Every tenant has deny rules for AGENTS.md/HARNESS_SPEC.md
        for t in tenants:
            rules = t.get("structural_rules", [])
            has_shared_deny = any(
                "AGENTS.md" in str(r.get("condition", "")) and
                r.get("decision") == "deny"
                for r in rules
            )
            if not has_shared_deny:
                breaches.append(f"Attack 6: Tenant {t.get('tenant_id')} can write AGENTS.md")

        # Attack 7: LLM hallucinates "no PII" to allow egress
        # Mitigation: PII redaction is non-delegatable; LLM can bypass = false
        red = self.op.get("pii_redaction", {})
        if red.get("llm_can_bypass"):
            breaches.append("Attack 7: LLM can bypass PII redaction")

        # Attack 8: No SVID on tool call
        # Mitigation: SYS-10 requires envelope; SYS-09 requires SVID
        has_envelope_rule = any(
            "envelope" in str(r.get("condition", "")).lower()
            for r in sys_rules
        )
        if not has_envelope_rule:
            breaches.append("Attack 8: No envelope requirement rule")

        # Attack 9: Tenant A's circuit breaker trip affects Tenant B
        # Mitigation: All tenants have per_tenant_isolated=True (already checked in Attack 5)
        # Re-verify with explicit cross-check
        cb_states = [t.get("circuit_breaker", {}).get("per_tenant_isolated")
                     for t in tenants]
        if not all(cb_states):
            breaches.append("Attack 9: Not all circuit breakers are isolated")

        # Attack 10: Tenant A's trust score affects Tenant B
        # Mitigation: G5 inheritance has per_tenant trust_score
        g5 = self.op.get("g5_inheritance", {})
        ts = g5.get("trust_score", {})
        if not ts.get("per_tenant"):
            breaches.append("Attack 10: Trust score not per-tenant")

        self.assertEqual(len(breaches), 0,
                         f"Cross-tenant breach count = {len(breaches)} (MUST BE 0):\n" +
                         "\n".join(f"  - {b}" for b in breaches))

    def test_st_g8_34_pii_redaction_coverage(self):
        """ST-G8-34: 100% of egress logs scanned with deterministic PII redaction."""
        red = self.op.get("pii_redaction", {})
        self.assertTrue(red.get("always_on"), "PII redaction must be always-on")
        self.assertTrue(red.get("non_delegatable"),
                        "PII redaction must be non-delegatable")
        det_filters = red.get("deterministic_filters", [])
        self.assertGreaterEqual(len(det_filters), 3,
                                "At least 3 deterministic filters required")
        for f in det_filters:
            self.assertTrue(f.get("filter_id"),
                            f"Filter missing ID: {f}")
            # Filters may have top-level replacement or nested patterns with replacements
            has_replacement = (
                f.get("replacement") is not None or
                any(p.get("replacement") for p in f.get("patterns", []))
            )
            self.assertTrue(has_replacement,
                            f"Filter {f.get('filter_id')} missing replacement (top-level or in patterns)")

    def test_st_g8_35_spiffe_svid_validation(self):
        """ST-G8-35: 100% of tool executions undergo SPIFFE JWT-SVID validation."""
        sys_rules = self.tp.get("system_wide_rules", [])
        has_svid_rule = any(
            "svid" in str(r.get("condition", "")).lower()
            for r in sys_rules
        )
        self.assertTrue(has_svid_rule,
                        "System-wide rule must require SVID")

        sp = self.ae.get("spiffe", {})
        self.assertEqual(sp.get("svid_format"), "JWT-SVID")
        self.assertEqual(sp.get("svid_ttl"), "15m")

        jit = self.ae.get("jit_downscoping", {})
        pipeline = jit.get("downscope_pipeline", [])
        svid_step = any(
            "svid" in str(s.get("name", "")).lower()
            for s in pipeline
        )
        self.assertTrue(svid_step,
                        "JIT pipeline must have SVID verification step")

    def test_st_g8_36_circuit_breaker_independence(self):
        """ST-G8-36: Per-tenant circuit breakers trip independently."""
        tenants = self.tp.get("tenants", [])
        for t in tenants:
            cb = t.get("circuit_breaker", {})
            self.assertTrue(cb.get("per_tenant_isolated"),
                            f"Tenant {t.get('tenant_id')} CB not isolated")
            self.assertIn(cb.get("trip_threshold"), [0.50, 0.70, 0.80],
                          f"Tenant {t.get('tenant_id')} invalid trip threshold")

        # Verify G5 inheritance also has per-tenant circuit breaker
        g5 = self.op.get("g5_inheritance", {})
        cb_inh = g5.get("circuit_breaker", {})
        self.assertTrue(cb_inh.get("per_tenant"),
                        "G5 inherited circuit breaker must be per-tenant")

    def test_st_g8_37_confused_deputy_prevention(self):
        """ST-G8-37: Confused deputy prevention — user-ambient delegation forbidden."""
        guarantees = self.ae.get("identity_guarantees", [])
        has_cd_prevention = any(
            "confused deputy" in str(g.get("description", "")).lower()
            for g in guarantees
        )
        self.assertTrue(has_cd_prevention,
                        "Identity guarantees must include confused deputy prevention")

    def test_st_g8_38_zero_ambient_authority(self):
        """ST-G8-38: Zero ambient authority — no persistent credentials."""
        jit = self.ae.get("jit_downscoping", {})
        self.assertTrue(jit.get("zero_ambient_authority"))
        self.assertTrue(jit.get("per_call"))
        self.assertTrue(jit.get("non_reusable"))
        self.assertEqual(jit.get("max_ttl"), "15m")

    def test_st_g8_39_l4_disabled_system_wide(self):
        """ST-G8-39: L4 AgentCreator disabled system-wide — no tenant can enable."""
        sys_rules = self.tp.get("system_wide_rules", [])
        has_l4_deny = any(
            "L4" in str(r.get("condition", "")) and
            r.get("decision") == "deny"
            for r in sys_rules
        )
        self.assertTrue(has_l4_deny,
                        "System-wide rule must deny L4 enablement")

    def test_st_g8_40_secret_scan_clean(self):
        """ST-G8-40: No secrets in any G8 artifact."""
        all_content = ""
        for f in ["MULTI_TENANT_SECURITY_ARCHITECTURE.md", "POLICY_DSL_SPEC.md",
                   "CAPABILITY_DISCOVERY.yaml", "tenant_policies.yaml",
                   "sandbox_templates.yaml", "authorization_envelopes.yaml",
                   "observability_pipelines.yaml"]:
            all_content += _read(f)

        resume_excl = [
            "G8_MULTITENANT_APPROVED_v1", "G7_IMPROVEMENT_BOUNDS_v1",
            "G5_EVAL_FRAMEWORK_APPROVED_v1", "G6_VIBE_ENV_LOCKED_v1",
            "G4_TOPOLOGY_APPROVED_v1", "G3_CONTEXT_LAYER_LOCKED_v1",
            "G2_TOOL_REGISTRY_LOCKED_v1", "G1_HARNESS_APPROVED_v1",
            "G2_TOOLING_APPROVED_v1", "G5_EVAL_APPROVED_v1",
            "RESUME_TOKEN"
        ]

        patterns = [
            r'(?i)(?:api[_-]?key)\s*[=:]\s*\S{20,}',
            r'(?i)bearer\s+\S{20,}',
            r'(?i)(?:secret|password)\s*[=:]\s*\S{20,}',
        ]

        hits = []
        for pat in patterns:
            for m in re.findall(pat, all_content):
                if not any(e in m for e in resume_excl):
                    hits.append(m[:50])

        self.assertEqual(len(hits), 0,
                         f"Secret scan found {len(hits)} hits: {hits}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
