#!/usr/bin/env python3
"""G8 Multi-Tenant — Standalone Pack Verifier (Step E)

Verifies all declarative artifacts in specs/g8_multitenant/ for
structural completeness, cross-artifact consistency, and secret-free
content. This is the repo source-of-truth verifier after G8 lock.

Run: python3 scripts/verify_g8_multitenant.py
"""

import os
import re
import sys
import yaml

G8_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "specs", "g8_multitenant"
)

checks = 0
errors = []


def ok(msg):
    global checks
    checks += 1


def fail(msg):
    global checks
    checks += 1
    errors.append(msg)


def check(condition, msg):
    if condition:
        ok(msg)
    else:
        fail(msg)


def read_utf8(name):
    path = os.path.join(G8_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def read_yaml(name):
    path = os.path.join(G8_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ===========================================================================
# 1. File Existence (7 artifacts + 1 migration context)
# ===========================================================================
expected_files = [
    "MULTI_TENANT_SECURITY_ARCHITECTURE.md",
    "CAPABILITY_DISCOVERY.yaml",
    "POLICY_DSL_SPEC.md",
    "tenant_policies.yaml",
    "sandbox_templates.yaml",
    "authorization_envelopes.yaml",
    "observability_pipelines.yaml",
    "G8_MIGRATION_CONTEXT.md",
]

for f in expected_files:
    path = os.path.join(G8_DIR, f)
    check(os.path.exists(path), f"EXISTS: {f}")

# ===========================================================================
# 2. YAML Safe-Load (5 files)
# ===========================================================================
yaml_files = [
    "CAPABILITY_DISCOVERY.yaml",
    "tenant_policies.yaml",
    "sandbox_templates.yaml",
    "authorization_envelopes.yaml",
    "observability_pipelines.yaml",
]

yaml_data = {}
for yf in yaml_files:
    try:
        yaml_data[yf] = read_yaml(yf)
        check(yaml_data[yf] is not None, f"YAML non-None: {yf}")
    except Exception as e:
        fail(f"YAML parse error {yf}: {e}")

# ===========================================================================
# 3. MULTI_TENANT_SECURITY_ARCHITECTURE.md — Section Coverage
# ===========================================================================
arch = read_utf8("MULTI_TENANT_SECURITY_ARCHITECTURE.md")
arch_l = arch.lower()

required_arch_sections = [
    "tiered isolation",
    "spiffe identity",
    "authorization envelope",
    "owasp llm06",
    "hybrid policy server",
    "zero cross-tenant",
    "7-pillar effective trust",
    "tenant risk-tier",
    "red/blue/green",
    "dynamic context resolvers",
    "option_1_conservative",
    "option_2_standard",
    "option_3_creative",
    "g8_multitenant_approved_v1",
    "self-improvement-v1.0.0",
]
for s in required_arch_sections:
    check(s in arch_l, f"ARCH section: {s}")

check("\u2605" in arch, "ARCH has star in option matrix")

for ctrl in ["llm06-01", "llm06-02", "llm06-03", "llm06-04",
             "llm06-05", "llm06-06", "llm06-07", "llm06-08"]:
    check(ctrl in arch_l, f"ARCH has {ctrl}")

for cid in ["c-mt-01", "c-mt-02", "c-mt-03", "c-mt-04",
            "c-mt-05", "c-mt-06", "c-mt-07", "c-mt-08"]:
    check(cid in arch_l, f"ARCH has {cid}")

for pillar in ["compute", "data", "identity", "network", "observability"]:
    check(pillar in arch_l, f"ARCH pillar: {pillar}")

# Isolation tiers
for iso in ["ISO-1", "ISO-2", "ISO-3"]:
    check(iso in arch, f"ARCH has {iso}")

# Risk tiers
for rt in ["RT-1", "RT-2", "RT-3", "RT-4"]:
    check(rt in arch, f"ARCH has {rt}")

# G7 hard bound references
for hb in ["hb-05", "hb-06", "hb-07"]:
    check(hb in arch_l, f"ARCH refs {hb}")

# ===========================================================================
# 4. POLICY_DSL_SPEC.md — Section Coverage
# ===========================================================================
dsl = read_utf8("POLICY_DSL_SPEC.md")
dsl_l = dsl.lower()

required_dsl_sections = [
    "policy dsl",
    "structural role validation",
    "semantic pii",
    "tenant risk-tier",
    "ebnf",
    "decision vocabulary",
    "allow",
    "deny",
    "hitl",
    "rewrite_caps",
    "fail-closed",
    "non-delegatable",
    "g8_multitenant_approved_v1",
    "option_2_standard",
]
for s in required_dsl_sections:
    check(s in dsl_l, f"DSL section: {s}")

for hb in ["hb-01", "hb-05", "hb-06", "hb-07"]:
    check(hb in dsl_l, f"DSL refs {hb}")

# ===========================================================================
# 5. CAPABILITY_DISCOVERY.yaml — Structural Checks
# ===========================================================================
cd = yaml_data.get("CAPABILITY_DISCOVERY.yaml", {})
if cd:
    sr = cd.get("sandbox_runtimes", [])
    check(len(sr) >= 4, f"CD sandbox_runtimes >=4 ({len(sr)})")

    names = [s.get("name", "").lower() for s in sr]
    check(any("docker" in n for n in names), "CD Docker present")
    check(any("gvisor" in n for n in names), "CD gVisor present")
    check(any("firecracker" in n for n in names), "CD Firecracker present")

    tiers = [s.get("isolation_tier") for s in sr]
    check("ISO-1" in tiers, "CD ISO-1 present")
    check("ISO-2" in tiers, "CD ISO-2 present")
    check("ISO-3" in tiers, "CD ISO-3 present")

    pii = cd.get("pii_redaction_middleware", [])
    check(len(pii) >= 4, f"CD pii_middleware >=4 ({len(pii)})")
    for p in pii:
        check(p.get("non_delegatable") is True,
              f"CD PII {p.get('id')} non_delegatable=True")

    check(cd.get("spiffe_sourcing", {}).get("trust_domain") == "agentic-rd.local",
          "CD trust_domain correct")

    om = cd.get("option_matrix", {})
    for opt in ["OPTION_1_CONSERVATIVE", "OPTION_2_STANDARD", "OPTION_3_CREATIVE"]:
        check(opt in om, f"CD {opt} present")

    gaps = cd.get("procurement_summary", {}).get("gaps", [])
    check(len(gaps) >= 3, f"CD gaps >=3 ({len(gaps)})")

# ===========================================================================
# 6. tenant_policies.yaml — Structural Checks
# ===========================================================================
tp = yaml_data.get("tenant_policies.yaml", {})
if tp:
    sys_rules = tp.get("system_wide_rules", [])
    check(len(sys_rules) >= 8, f"TP system_wide_rules >=8 ({len(sys_rules)})")

    tenants = tp.get("tenants", [])
    check(len(tenants) >= 4, f"TP tenants >=4 ({len(tenants)})")

    rts = set()
    for t in tenants:
        rts.add(t.get("risk_tier"))
        for r in ["structural_rules", "semantic_rules", "budget_rules",
                  "improvement_rules", "circuit_breaker"]:
            check(t.get(r) is not None,
                  f"TP {t.get('tenant_id')} has {r}")
        check(t.get("circuit_breaker", {}).get("per_tenant_isolated") is True,
              f"TP {t.get('tenant_id')} CB per_tenant_isolated=True")

    for rt in ["RT-1", "RT-2", "RT-3", "RT-4"]:
        check(rt in rts, f"TP {rt} present")

    check(tp.get("default_policy", {}).get("unmatched_decision") == "deny",
          "TP default fail-closed=deny")

    ctg = tp.get("cross_tenant_guarantees", [])
    check(len(ctg) >= 5, f"TP cross_tenant_guarantees >=5 ({len(ctg)})")

    # System-wide rules check: SVID required, envelope required, L4 denied
    has_svid = any("svid" in str(r.get("condition", "")).lower()
                   for r in sys_rules)
    check(has_svid, "TP SYS rule requires SVID")
    has_envelope = any("envelope" in str(r.get("condition", "")).lower()
                       for r in sys_rules)
    check(has_envelope, "TP SYS rule requires envelope")
    has_l4_deny = any("L4" in str(r.get("condition", "")) and
                      r.get("decision") == "deny"
                      for r in sys_rules)
    check(has_l4_deny, "TP SYS rule denies L4")

# ===========================================================================
# 7. sandbox_templates.yaml — Structural Checks
# ===========================================================================
st = yaml_data.get("sandbox_templates.yaml", {})
if st:
    templates = st.get("templates", [])
    check(len(templates) >= 4, f"ST templates >=4 ({len(templates)})")

    tids = set()
    for t in templates:
        tids.add(t.get("isolation_tier"))
        check(t.get("status") == "DECLARED_NOT_WIRED",
              f"ST {t.get('id')} DECLARED_NOT_WIRED")

    check("ISO-1" in tids, "ST ISO-1 present")
    check("ISO-2" in tids, "ST ISO-2 present")
    check("ISO-3" in tids, "ST ISO-3 present")

    sel = st.get("template_selection", {})
    check(sel.get("RT-1") == "TPL-ISO1-DOCKER", "ST RT-1 maps to Docker")
    check(sel.get("RT-3") == "TPL-ISO2-GVISOR", "ST RT-3 maps to gVisor")
    check(sel.get("RT-4") == "TPL-ISO3-FIRECRACKER", "ST RT-4 maps to Firecracker")

    red = st.get("shared_volume_redaction", {})
    check(red.get("always_on") is True, "ST redaction always_on=True")
    check(len(red.get("patterns", [])) >= 4,
          f"ST redaction patterns >=4 ({len(red.get('patterns', []))})")

    # Check resume token exclusions in secret scan patterns
    for p in red.get("patterns", []):
        if "secret" in p.get("name", "").lower() or "Generic" in p.get("name", ""):
            exclusions = p.get("exclusions", [])
            if exclusions:
                check("G8_MULTITENANT_APPROVED_v1" in exclusions,
                      f"ST pattern {p.get('pattern_id')} excludes G8 token")

# ===========================================================================
# 8. authorization_envelopes.yaml — Structural Checks
# ===========================================================================
ae = yaml_data.get("authorization_envelopes.yaml", {})
if ae:
    sp = ae.get("spiffe", {})
    check(sp.get("trust_domain") == "agentic-rd.local", "AE trust_domain")
    check(sp.get("svid_format") == "JWT-SVID", "AE SVID format")
    check(sp.get("svid_ttl") == "15m", "AE SVID TTL 15m")

    env = ae.get("envelope_schema", {}).get("required_fields", [])
    req_names = {f.get("name") for f in env}
    for f in ["envelope_id", "tenant_id", "agent_id", "svid", "caps",
              "tool_call", "risk_tier", "policy_decision", "reason_code",
              "rule_ids", "ts", "exp"]:
        check(f in req_names, f"AE required field: {f}")

    jit = ae.get("jit_downscoping", {})
    check(jit.get("enabled") is True, "AE JIT enabled")
    check(jit.get("per_call") is True, "AE JIT per_call")
    check(jit.get("non_reusable") is True, "AE JIT non_reusable")
    check(jit.get("zero_ambient_authority") is True, "AE zero_ambient_authority")
    check(len(jit.get("downscope_pipeline", [])) == 7, "AE pipeline steps=7")

    caps = ae.get("capabilities", [])
    check(len(caps) >= 7, f"AE capability classes >=7 ({len(caps)})")

    guarantees = ae.get("identity_guarantees", [])
    check(len(guarantees) >= 4, f"AE identity_guarantees >=4 ({len(guarantees)})")
    has_cd = any("confused deputy" in str(g.get("description", "")).lower()
                 for g in guarantees)
    check(has_cd, "AE has confused deputy prevention")

# ===========================================================================
# 9. observability_pipelines.yaml — Structural Checks
# ===========================================================================
op = yaml_data.get("observability_pipelines.yaml", {})
if op:
    red = op.get("pii_redaction", {})
    check(red.get("always_on") is True, "OP redaction always_on")
    check(red.get("non_delegatable") is True, "OP redaction non_delegatable")
    check(red.get("llm_can_bypass") is False, "OP llm_can_bypass=False")

    det = red.get("deterministic_filters", [])
    check(len(det) >= 3, f"OP det_filters >=3 ({len(det)})")
    for f in det:
        if "secret" in f.get("name", "").lower():
            exc = f.get("exclusions", [])
            check("G8_MULTITENANT_APPROVED_v1" in exc,
                  "OP secret filter excludes G8 token")
            check("G7_IMPROVEMENT_BOUNDS_v1" in exc,
                  "OP secret filter excludes G7 token")

    ptp = op.get("per_tenant_pipelines", {})
    for rt in ["RT-1", "RT-2", "RT-3", "RT-4"]:
        check(rt in ptp, f"OP pipeline for {rt}")

    rt4 = ptp.get("RT-4", {})
    check(rt4.get("human_review") is True, "OP RT-4 human_review")
    check(rt4.get("legal_hold") is True, "OP RT-4 legal_hold")
    check(rt4.get("retention_days") == 365, "OP RT-4 retention=365")

    attrs = [a.get("key") for a in
             op.get("span_enrichment", {}).get("required_attributes", [])]
    for a in ["tenant_id", "agent_id", "isolation_tier", "risk_tier",
              "policy_decision"]:
        check(a in attrs, f"OP span attr {a}")

    cti = op.get("cross_tenant_isolation", [])
    check(len(cti) >= 4, f"OP cross_tenant_isolation >=4 ({len(cti)})")

    panels = op.get("dashboard_panels", [])
    check(len(panels) >= 6, f"OP dashboard_panels >=6 ({len(panels)})")

    g5 = op.get("g5_inheritance", {})
    for m in ["trajectory_schema", "trust_score", "circuit_breaker", "agbom"]:
        check(m in g5, f"OP G5 inheritance {m}")

    cbt = g5.get("circuit_breaker", {}).get("trip_threshold_per_tier", {})
    check(cbt.get("RT-1") == 0.50, "OP RT-1 trip 0.50")
    check(cbt.get("RT-2") == 0.50, "OP RT-2 trip 0.50")
    check(cbt.get("RT-3") == 0.70, "OP RT-3 trip 0.70")
    check(cbt.get("RT-4") == 0.80, "OP RT-4 trip 0.80")

    ts = g5.get("trust_score", {})
    check(ts.get("per_tenant") is True, "OP trust_score per_tenant")

    audit = op.get("audit_log", {})
    check(audit.get("per_tenant") is True, "OP audit_log per_tenant")
    check(audit.get("cross_tenant_access") == "denied",
          "OP audit_log cross_tenant denied")

# ===========================================================================
# 10. Cross-Artifact Consistency
# ===========================================================================
all_c = ""
for f in ["MULTI_TENANT_SECURITY_ARCHITECTURE.md", "POLICY_DSL_SPEC.md"]:
    all_c += read_utf8(f)
for f in yaml_files:
    all_c += read_utf8(f)

al = all_c.lower()
check("g8_multitenant_approved_v1" in al, "XREF G8 token present")
check("option_2_standard" in al, "XREF OPTION_2_STANDARD present")
check("self-improvement-v1.0.0" in al, "XREF upstream tag present")

# Check YAML files have consistent overlay + resume token
for yf in yaml_files:
    yd = yaml_data.get(yf, {})
    check(yd.get("overlay") == "OPTION_2_STANDARD",
          f"XREF {yf} overlay=OPTION_2_STANDARD")
    check(yd.get("blue_resume_token") == "G8_MULTITENANT_APPROVED_v1",
          f"XREF {yf} resume token=G8_MULTITENANT_APPROVED_v1")

# ===========================================================================
# 11. Secret Scan (min-length 20, exclude resume tokens)
# ===========================================================================
resume_excl = [
    "G8_MULTITENANT_APPROVED_v1", "G7_IMPROVEMENT_BOUNDS_v1",
    "G5_EVAL_FRAMEWORK_APPROVED_v1", "G6_VIBE_ENV_LOCKED_v1",
    "G4_TOPOLOGY_APPROVED_v1", "G3_CONTEXT_LAYER_LOCKED_v1",
    "G2_TOOL_REGISTRY_LOCKED_v1", "G1_HARNESS_APPROVED_v1",
    "G2_TOOLING_APPROVED_v1", "G5_EVAL_APPROVED_v1",
    "RESUME_TOKEN",
]

secret_patterns = [
    (r'(?i)(?:api[_-]?key)\s*[=:]\s*\S{20,}', "API key"),
    (r'(?i)bearer\s+\S{20,}', "Bearer"),
    (r'(?i)(?:secret|password)\s*[=:]\s*\S{20,}', "Secret/Password"),
]

secret_hits = []
for pat, name in secret_patterns:
    for m in re.findall(pat, all_c):
        if not any(e in m for e in resume_excl):
            secret_hits.append(f"{name}: {m[:50]}...")

check(len(secret_hits) == 0, f"Secret scan: {len(secret_hits)} hits")
if secret_hits:
    for h in secret_hits[:5]:
        fail(f"SECRET: {h}")

# ===========================================================================
# 12. XML/HTML Tag Scan (manifest directive: pure Markdown only)
# ===========================================================================
xml_hits = re.findall(r'<[a-zA-Z/][^>]{0,100}>', all_c)
xml_filtered = [x for x in xml_hits
                if not x.startswith('<br') and not x.startswith('<hr')]

check(len(xml_filtered) == 0, f"XML/HTML tags: {len(xml_filtered)} hits")
if xml_filtered:
    for h in xml_filtered[:5]:
        fail(f"XML_TAG: {h}")

# ===========================================================================
# 13. Cross-Tenant Attack Simulation (mandated by HITL gate)
# ===========================================================================
if tp and st and op and ae:
    breach_count = 0
    breach_details = []

    tenants = tp.get("tenants", [])
    if len(tenants) >= 2:
        # Attack: Cross-tenant filesystem access
        for t in tenants:
            rules = t.get("structural_rules", [])
            has_own_path = any(
                t.get("tenant_id") in str(r.get("condition", ""))
                for r in rules
            )
            has_shared_deny = any(
                "AGENTS.md" in str(r.get("condition", "")) and
                r.get("decision") == "deny"
                for r in rules
            )
            if not has_shared_deny:
                breach_count += 1
                breach_details.append(
                    f"Tenant {t.get('tenant_id')} can write shared specs")

        # Attack: Cross-tenant identity assumption
        sys_r = tp.get("system_wide_rules", [])
        if not any("svid" in str(r.get("condition", "")).lower()
                    for r in sys_r):
            breach_count += 1
            breach_details.append("No SVID validation rule")

        # Attack: Cross-tenant network access
        for tmpl in st.get("templates", []):
            net = tmpl.get("network_spec", {})
            if net.get("egress_policy") != "deny_all_except_policy_server":
                breach_count += 1
                breach_details.append(
                    f"Template {tmpl.get('id')} allows direct egress")

        # Attack: Cross-tenant telemetry leakage
        cti = op.get("cross_tenant_isolation", [])
        if len(cti) < 4:
            breach_count += 1
            breach_details.append("Insufficient cross-tenant telemetry isolation")

        # Attack: LLM bypasses PII redaction
        if op.get("pii_redaction", {}).get("llm_can_bypass"):
            breach_count += 1
            breach_details.append("LLM can bypass PII redaction")

        # Attack: Circuit breaker cross-contamination
        for t in tenants:
            if not t.get("circuit_breaker", {}).get("per_tenant_isolated"):
                breach_count += 1
                breach_details.append(
                    f"Tenant {t.get('tenant_id')} CB not isolated")

        # Attack: Trust score cross-contamination
        g5 = op.get("g5_inheritance", {})
        if not g5.get("trust_score", {}).get("per_tenant"):
            breach_count += 1
            breach_details.append("Trust score not per-tenant")

        # Attack: Zero ambient authority violation
        jit = ae.get("jit_downscoping", {})
        if not jit.get("zero_ambient_authority"):
            breach_count += 1
            breach_details.append("Zero ambient authority not enforced")

    check(breach_count == 0,
          f"Cross-tenant breach count = {breach_count} (MUST BE 0)")
    if breach_details:
        for d in breach_details:
            fail(f"BREACH: {d}")

# ===========================================================================
# Summary
# ===========================================================================
passed = checks - len(errors)
print(f"\n{'=' * 60}")
print(f"G8 PACK VERIFIER (repo source-of-truth after lock)")
print(f"{'=' * 60}")
print(f"Total checks: {checks}")
print(f"Passed: {passed}")
print(f"Failed: {len(errors)}")
print(f"{'=' * 60}")
if errors:
    print("\nFAILURES:")
    for e in errors:
        print(f"  - {e}")
else:
    print("\nALL CHECKS PASSED")
print(f"{'=' * 60}")
sys.exit(1 if errors else 0)
