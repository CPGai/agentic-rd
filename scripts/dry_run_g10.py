#!/usr/bin/env python3
"""G10 Chaos Engineering & Production Dry-Run (Step E)

Simulates production AgentOps control loops against declarative specs:
  - Enterprise policy spikes (OWASP LLM06 non-delegatable interception)
  - Mock PII injection + trace redaction completeness
  - Forced trust score decay >15% → automated rollback to LKG
  - Doctor CRITICAL probe fail → canary fleet isolation

This is a SIMULATION against declarative specs — no live cloud mutation.
Run: python scripts/dry_run_g10.py
Emits: specs/g10_production/chaos_dry_run_metrics.json
"""
from __future__ import annotations

import json
import os
import sys
from copy import deepcopy
from datetime import datetime, timezone

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G10 = os.path.join(ROOT, "specs", "g10_production")
OUT = os.path.join(G10, "chaos_dry_run_metrics.json")

LKG_REVISION = "v0.9.0-previous"
CANARY_REVISION = "v1.0.0-canary-candidate"
TRUST_BASELINE = 1.0


def load_yaml(name: str):
    with open(os.path.join(G10, name), "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


class PolicyServerSim:
    """Deterministic LLM06 non-delegatable checks — LLM cannot downgrade deny."""

    CONTROLS = [
        "LLM06-01",
        "LLM06-02",
        "LLM06-03",
        "LLM06-04",
        "LLM06-05",
        "LLM06-06",
        "LLM06-07",
        "LLM06-08",
    ]

    def __init__(self):
        self.decisions = []
        self.deny_count = 0
        self.allow_count = 0
        self.critical_blocks = 0

    def evaluate(self, event: dict) -> dict:
        control = event.get("control")
        malicious = event.get("malicious", False)
        llm_advisory = event.get("llm_wants", "allow")

        if control not in self.CONTROLS:
            decision = "deny"
            reason = "unknown_control_fail_closed"
        elif malicious:
            decision = "deny"
            reason = f"non_delegatable_{control}"
            self.critical_blocks += 1
        else:
            decision = "allow"
            reason = "clean"

        # LLM can escalate allow→hitl but never deny→allow
        if decision == "deny" and llm_advisory == "allow":
            final = "deny"
            note = "llm_cannot_downgrade_deny"
        elif decision == "allow" and llm_advisory == "hitl":
            final = "hitl"
            note = "llm_escalate_ok"
        else:
            final = decision
            note = "deterministic"

        if final == "deny":
            self.deny_count += 1
        elif final == "allow":
            self.allow_count += 1

        rec = {
            "control": control,
            "final": final,
            "reason": reason,
            "llm_advisory": llm_advisory,
            "note": note,
            "non_delegatable": True,
        }
        self.decisions.append(rec)
        return rec


class TraceRedactor:
    """Deterministic PII / secret redaction for OTEL-style envelopes."""

    def __init__(self):
        self.total_fields = 0
        self.redacted_fields = 0
        self.leaks = 0

    def scrub(self, span: dict) -> dict:
        out = deepcopy(span)
        attrs = out.setdefault("attributes", {})
        marker_map = [
            ("email", "@", "REDACTED_EMAIL"),
            ("ssn", "SSN:", "REDACTED_SSN"),
            ("phone", "TEL:", "REDACTED_PHONE"),
            ("credit", "CC:", "REDACTED_CC"),
            ("secret", "SECRET=", "REDACTED_SECRET"),
        ]
        for key, val in list(attrs.items()):
            self.total_fields += 1
            sval = str(val)
            redacted = False
            for kind, marker, token in marker_map:
                if marker in sval or kind in key.lower():
                    attrs[key] = token
                    self.redacted_fields += 1
                    redacted = True
                    break
            if redacted:
                for _kind, marker, _token in marker_map:
                    if marker in str(attrs[key]):
                        self.leaks += 1
        out["attributes"] = attrs
        return out


class TrustRollbackEngine:
    def __init__(self, baseline: float = TRUST_BASELINE, lkg: str = LKG_REVISION):
        self.baseline = baseline
        self.trust = baseline
        self.lkg = lkg
        self.active_revision = CANARY_REVISION
        self.canary_pct = 25
        self.events = []
        self.rolled_back = False

    def apply_decay(self, new_trust: float) -> dict:
        self.trust = new_trust
        decay_pct = ((self.baseline - self.trust) / self.baseline) * 100.0
        action = "continue"
        if decay_pct > 15.0 or self.trust < 0.50:
            action = "instant_lkg"
            self.active_revision = self.lkg
            self.canary_pct = 0
            self.rolled_back = True
        rec = {
            "trust": self.trust,
            "baseline": self.baseline,
            "decay_pct": round(decay_pct, 2),
            "action": action,
            "active_revision": self.active_revision,
            "canary_pct": self.canary_pct,
        }
        self.events.append(rec)
        return rec


class DoctorFleetIsolator:
    def __init__(self):
        self.fleet_state = "CANARY_ACTIVE"
        self.canary_pct = 5
        self.active_revision = CANARY_REVISION
        self.events = []

    def on_probe(self, probe_id: str, severity: str, fail_closed: bool) -> dict:
        action = "noop"
        if severity == "CRITICAL" and fail_closed:
            action = "auto_rollback_isolate"
            self.fleet_state = "ISOLATED_LKG"
            self.canary_pct = 0
            self.active_revision = LKG_REVISION
        rec = {
            "probe_id": probe_id,
            "severity": severity,
            "fail_closed": fail_closed,
            "action": action,
            "fleet_state": self.fleet_state,
            "active_revision": self.active_revision,
            "canary_pct": self.canary_pct,
        }
        self.events.append(rec)
        return rec


def run_policy_spike(policy: PolicyServerSim) -> dict:
    malicious_events = [
        {"control": c, "malicious": True, "llm_wants": "allow"}
        for c in PolicyServerSim.CONTROLS
    ]
    clean_events = [
        {"control": "LLM06-01", "malicious": False, "llm_wants": "allow"},
        {"control": "LLM06-03", "malicious": False, "llm_wants": "hitl"},
    ]
    results = [policy.evaluate(e) for e in malicious_events + clean_events]
    mal_results = [r for r in results if r["reason"].startswith("non_delegatable_")]
    mal_ok = all(r["final"] == "deny" and r["non_delegatable"] for r in mal_results)
    no_llm_downgrade = all(
        not (
            r["llm_advisory"] == "allow"
            and r["final"] == "allow"
            and r["reason"].startswith("non_delegatable_")
        )
        for r in results
    )
    baseline_deny_rate = 0.0
    spike_deny_rate = policy.deny_count / max(1, len(results))
    surge_pct = (spike_deny_rate - baseline_deny_rate) * 100.0
    auto_rollback_candidacy = surge_pct >= 15.0
    return {
        "name": "policy_spike_llm06",
        "controls_exercised": 8,
        "malicious_all_denied": mal_ok,
        "llm_cannot_downgrade_deny": no_llm_downgrade,
        "critical_blocks": policy.critical_blocks,
        "deny_count": policy.deny_count,
        "surge_pct_vs_zero_baseline": round(surge_pct, 2),
        "auto_rollback_candidacy": auto_rollback_candidacy,
        "pass": mal_ok
        and no_llm_downgrade
        and policy.critical_blocks == 8
        and auto_rollback_candidacy,
    }


def run_pii_injection(redactor: TraceRedactor) -> dict:
    dirty_span = {
        "name": "root.request",
        "attributes": {
            "tenant_id": "t-demo",
            "user_email": "user@example.com",
            "user_ssn": "SSN:123-45-6789",
            "user_phone": "TEL:+1-555-0100",
            "payment": "CC:4111111111111111",
            "tool_secret": "SECRET=not-a-real-key-value-xyz",
            "release_id": "rel-deadbeef",
            "clean_flag": "ok",
        },
    }
    clean = redactor.scrub(dirty_span)
    attrs = clean["attributes"]
    raw_markers = ["@", "SSN:", "TEL:", "CC:", "SECRET="]
    residual = []
    for k, v in attrs.items():
        for m in raw_markers:
            if m in str(v):
                residual.append(f"{k}:{v}")
    complete = len(residual) == 0 and redactor.redacted_fields >= 5
    return {
        "name": "pii_injection_redaction",
        "fields_seen": redactor.total_fields,
        "fields_redacted": redactor.redacted_fields,
        "residual_raw_markers": residual,
        "leaks": redactor.leaks,
        "scrubbed_sample": attrs,
        "pass": complete and redactor.leaks == 0,
    }


def run_trust_decay(engine: TrustRollbackEngine) -> dict:
    steps = [0.95, 0.90, 0.88, 0.80]  # final decay = 20% > 15%
    for t in steps:
        engine.apply_decay(t)
    last = engine.events[-1]
    return {
        "name": "trust_decay_rollback",
        "baseline": TRUST_BASELINE,
        "final_trust": last["trust"],
        "final_decay_pct": last["decay_pct"],
        "rolled_back": engine.rolled_back,
        "active_revision": engine.active_revision,
        "expected_lkg": LKG_REVISION,
        "canary_pct_after": engine.canary_pct,
        "pass": (
            engine.rolled_back
            and engine.active_revision == LKG_REVISION
            and last["decay_pct"] > 15.0
            and engine.canary_pct == 0
        ),
    }


def run_doctor_critical(iso: DoctorFleetIsolator, doctor: dict) -> dict:
    probes = doctor.get("probes") or []
    crit = [
        p
        for p in probes
        if p.get("severity") == "CRITICAL" and p.get("fail_closed") is True
    ]
    target = next((p for p in crit if p.get("id") == "DOC-POL-01"), crit[0] if crit else None)
    if not target:
        return {
            "name": "doctor_critical_isolation",
            "pass": False,
            "error": "no critical probes",
        }
    rec = iso.on_probe(target["id"], "CRITICAL", True)
    return {
        "name": "doctor_critical_isolation",
        "probe_id": target["id"],
        "fleet_state": iso.fleet_state,
        "active_revision": iso.active_revision,
        "canary_pct": iso.canary_pct,
        "action": rec["action"],
        "pass": (
            iso.fleet_state == "ISOLATED_LKG"
            and iso.active_revision == LKG_REVISION
            and iso.canary_pct == 0
            and rec["action"] == "auto_rollback_isolate"
        ),
    }


def validate_specs_present() -> dict:
    required = [
        "PRODUCTION_AGENTOPS_BLUEPRINT.md",
        "CAPABILITY_DISCOVERY.yaml",
        "PRODUCTION_DSL_SPEC.md",
        "cicd_pipeline.yaml",
        "quality_gates.yaml",
        "doctor_checks.yaml",
        "fleet_management.yaml",
    ]
    missing = [f for f in required if not os.path.isfile(os.path.join(G10, f))]
    return {"name": "spec_surface_intact", "missing": missing, "pass": len(missing) == 0}


def main() -> int:
    qg = load_yaml("quality_gates.yaml")
    doctor = load_yaml("doctor_checks.yaml")
    fleet = load_yaml("fleet_management.yaml")

    assert (qg.get("trust_score") or {}).get("canary_decay_rollback_pct") == 15
    assert (fleet.get("canary") or {}).get("auto_rollback") is True
    rb_ids = {t.get("id") for t in ((fleet.get("rollback") or {}).get("triggers") or [])}
    assert "RB-03" in rb_ids and "RB-04" in rb_ids and "RB-02" in rb_ids

    policy = PolicyServerSim()
    redactor = TraceRedactor()
    trust_eng = TrustRollbackEngine()
    doctor_iso = DoctorFleetIsolator()

    scenarios = [
        validate_specs_present(),
        run_policy_spike(policy),
        run_pii_injection(redactor),
        run_trust_decay(trust_eng),
        run_doctor_critical(doctor_iso, doctor),
    ]

    passed = sum(1 for s in scenarios if s.get("pass"))
    failed = [s["name"] for s in scenarios if not s.get("pass")]

    report = {
        "domain": "G10",
        "kind": "chaos_dry_run",
        "overlay": "OPTION_2_STANDARD",
        "resume_token": "G10_PRODUCTION_DEPLOY_v1",
        "upstream_tag": "research-loop-v1.0.0",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "lkg_revision": LKG_REVISION,
        "canary_revision": CANARY_REVISION,
        "scenarios": scenarios,
        "summary": {
            "total": len(scenarios),
            "passed": passed,
            "failed": failed,
            "all_pass": passed == len(scenarios),
            "policy_critical_blocks": policy.critical_blocks,
            "pii_leaks": redactor.leaks,
            "trust_rolled_back_to_lkg": trust_eng.rolled_back
            and trust_eng.active_revision == LKG_REVISION,
            "doctor_isolated_fleet": doctor_iso.fleet_state == "ISOLATED_LKG",
        },
        "spec_refs": {
            "quality_gates": "quality_gates.yaml",
            "doctor_checks": "doctor_checks.yaml",
            "fleet_management": "fleet_management.yaml",
            "cicd_pipeline": "cicd_pipeline.yaml",
        },
    }

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
        fh.write("\n")

    print("=" * 60)
    print("G10 CHAOS DRY-RUN (Step E)")
    print("=" * 60)
    for s in scenarios:
        flag = "PASS" if s.get("pass") else "FAIL"
        print(f"  [{flag}] {s.get('name')}")
    print("-" * 60)
    print(f"Result: {passed}/{len(scenarios)} scenarios passed")
    print(f"LKG revision binding: {LKG_REVISION}")
    print(f"Metrics: {OUT}")
    print("=" * 60)
    if failed:
        print("FAILED:", ", ".join(failed))
        return 1
    print("CHAOS DRY-RUN CLEAN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
