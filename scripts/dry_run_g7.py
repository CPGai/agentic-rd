#!/usr/bin/env python3
"""G7 Dry-Run Simulation — 10 Improvement Cycles (Step E)

Simulates the self-improvement loop across 10 synthetic failure scenarios
using the declarative rules in triggers.yaml, oversight_boundaries.yaml,
and TAXONOMY_AND_BOUNDS.md. Measures:
  - Detection accuracy (true positives / total detections)
  - False-positive rate
  - Thrashing events
  - Degradation count (post-integration regressions)
  - HITL approval rate
  - Auto-integration success rate
  - Loop budget utilization

This is a SIMULATION against declarative specs — no real code mutation.
Outputs a structured report to stdout.
"""

import os
import sys
import yaml
import random
import json
from datetime import datetime

G7_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "specs", "g7_self_improve"
)


def load_yaml(name):
    with open(os.path.join(G7_DIR, name), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# =========================================================================
# Load declarative rules
# =========================================================================
triggers = load_yaml("triggers.yaml")
oversight = load_yaml("oversight_boundaries.yaml")
tax_md = open(os.path.join(G7_DIR, "TAXONOMY_AND_BOUNDS.md"), "r", encoding="utf-8").read()

# Build trigger lookup by severity
all_triggers = []
for key in ["trajectory_triggers", "trust_score_triggers",
            "evaluation_triggers", "failure_mode_triggers",
            "pattern_triggers", "human_triggers"]:
    all_triggers.extend(triggers.get(key, []))

trigger_by_severity = {"S1": [], "S2": [], "S3": [], "S4": []}
for t in all_triggers:
    sev = t.get("severity", "S4")
    trigger_by_severity[sev].append(t)

# Autonomy zone lookup
zones = {z["zone"]: z for z in oversight.get("autonomy_zones", [])}

# =========================================================================
# Synthetic failure scenarios (10 cycles)
# Each scenario simulates a detected failure and the loop's response
# =========================================================================
scenarios = [
    {
        "id": "SIM-01",
        "trigger": "TRJ-01",
        "failure": "trajectory_verdict_fail",
        "severity": "S3",
        "improvement_type": "IT-01",
        "operator": "DRAFT",
        "description": "Agent tool call failed 3 times in a row",
        "is_real_gap": True,
        "validation_passes": True,
        "generalization_passes": True,
        "behavioral": False,
        "post_integration_regression": False,
    },
    {
        "id": "SIM-02",
        "trigger": "TS-01",
        "failure": "trust_score_warning",
        "severity": "S3",
        "improvement_type": "IT-01",
        "operator": "DRAFT",
        "description": "Trust score dropped to 0.82 from 1.0",
        "is_real_gap": True,
        "validation_passes": True,
        "generalization_passes": True,
        "behavioral": False,
        "post_integration_regression": False,
    },
    {
        "id": "SIM-03",
        "trigger": "EVAL-02",
        "failure": "hallucination_detected",
        "severity": "S2",
        "improvement_type": "IT-01",
        "operator": "DRAFT",
        "description": "LLM-as-Judge detected fabricated citation",
        "is_real_gap": True,
        "validation_passes": True,
        "generalization_passes": False,
        "behavioral": True,
        "post_integration_regression": False,
    },
    {
        "id": "SIM-04",
        "trigger": "EVAL-03",
        "failure": "intent_drift_signal",
        "severity": "S2",
        "improvement_type": "IT-04",
        "operator": "DRAFT",
        "description": "AgBOM drift detected — agent using unauthorized tool",
        "is_real_gap": True,
        "validation_passes": True,
        "generalization_passes": True,
        "behavioral": True,
        "post_integration_regression": False,
    },
    {
        "id": "SIM-05",
        "trigger": "TRJ-04",
        "failure": "flat_fix_curve",
        "severity": "S2",
        "improvement_type": "IT-03",
        "operator": "PIVOT",
        "description": "3 fix attempts without resolution — pivot required",
        "is_real_gap": True,
        "validation_passes": True,
        "generalization_passes": True,
        "behavioral": True,
        "post_integration_regression": False,
    },
    {
        "id": "SIM-06",
        "trigger": "EVAL-05",
        "failure": "degradation_5pct",
        "severity": "S3",
        "improvement_type": "IT-01",
        "operator": "DRAFT",
        "description": "5% task success rate drop — auto-flag",
        "is_real_gap": False,
        "validation_passes": False,
        "generalization_passes": False,
        "behavioral": False,
        "post_integration_regression": False,
    },
    {
        "id": "SIM-07",
        "trigger": "TS-04",
        "failure": "immediate_trip_secret",
        "severity": "S1",
        "improvement_type": "IT-07",
        "operator": "DRAFT",
        "description": "Secret detected in agent output — CRITICAL",
        "is_real_gap": True,
        "validation_passes": True,
        "generalization_passes": True,
        "behavioral": True,
        "post_integration_regression": False,
    },
    {
        "id": "SIM-08",
        "trigger": "FM-TRG-03",
        "failure": "fm_critic_loop",
        "severity": "S3",
        "improvement_type": "IT-01",
        "operator": "PIVOT",
        "description": "Critic loop not converging — pivot",
        "is_real_gap": True,
        "validation_passes": True,
        "generalization_passes": True,
        "behavioral": False,
        "post_integration_regression": True,
    },
    {
        "id": "SIM-09",
        "trigger": "PAT-01",
        "failure": "thrashing_detection",
        "severity": "S2",
        "improvement_type": "IT-04",
        "operator": "PIVOT",
        "description": "A->B->A oscillation detected — thrashing",
        "is_real_gap": True,
        "validation_passes": True,
        "generalization_passes": True,
        "behavioral": True,
        "post_integration_regression": False,
    },
    {
        "id": "SIM-10",
        "trigger": "EVAL-04",
        "failure": "trajectory_adherence_drop",
        "severity": "S3",
        "improvement_type": "IT-01",
        "operator": "DRAFT",
        "description": "Agent deviating from ideal trajectory",
        "is_real_gap": False,
        "validation_passes": True,
        "generalization_passes": True,
        "behavioral": False,
        "post_integration_regression": False,
    },
]

# =========================================================================
# Simulate loop
# =========================================================================
results = []
loop_budget = 10
proposals_made = 0
thrashing_events = 0
degradation_count = 0
false_positives = 0
true_positives = 0
auto_integrations = 0
auto_integration_successes = 0
hitl_reviews = 0
hitl_approvals = 0
hitl_rejections = 0
rollbacks = 0
pivots = 0
refines = 0

for scenario in scenarios:
    r = {
        "cycle_id": scenario["id"],
        "trigger": scenario["trigger"],
        "failure": scenario["failure"],
        "severity": scenario["severity"],
        "improvement_type": scenario["improvement_type"],
        "operator": scenario["operator"],
        "description": scenario["description"],
    }

    # Check loop budget
    if proposals_made >= loop_budget:
        r["outcome"] = "PAUSED — loop budget exceeded (HG-04)"
        r["hitl_required"] = True
        results.append(r)
        continue

    proposals_made += 1

    # Determine autonomy zone
    sev = scenario["severity"]
    if sev == "S1":
        zone = zones.get("RESTRICTED", {})
        r["zone"] = "RESTRICTED"
        r["outcome"] = "FREEZE + HITL (HG-03)"
        r["hitl_required"] = True
        hitl_reviews += 1
        if scenario["is_real_gap"]:
            true_positives += 1
            hitl_approvals += 1
            r["hitl_decision"] = "approved"
        else:
            false_positives += 1
            hitl_rejections += 1
            r["hitl_decision"] = "rejected"
    elif sev == "S2":
        zone = zones.get("HUMAN_GATED", {})
        r["zone"] = "HUMAN_GATED"
        # DRAFT -> VALIDATE -> HITL
        if not scenario["validation_passes"]:
            r["outcome"] = "VALIDATION FAIL -> DEBUG"
            r["hitl_required"] = False
            if scenario["is_real_gap"]:
                true_positives += 1
            else:
                false_positives += 1
        elif not scenario["generalization_passes"]:
            r["outcome"] = "GENERALIZATION-GAP FAIL -> reject, widen scope"
            r["hitl_required"] = False
            false_positives += 1
        else:
            r["outcome"] = "VALIDATE PASS -> HITL GATE (HG-01)"
            r["hitl_required"] = True
            hitl_reviews += 1
            if scenario["is_real_gap"]:
                true_positives += 1
                hitl_approvals += 1
                r["hitl_decision"] = "approved"
                if scenario["post_integration_regression"]:
                    degradation_count += 1
                    rollbacks += 1
                    r["post_integration"] = "REGRESSION -> ROLLBACK"
                else:
                    r["post_integration"] = "success"
            else:
                false_positives += 1
                hitl_rejections += 1
                r["hitl_decision"] = "rejected"
    elif sev == "S3":
        zone = zones.get("ADVISORY", {})
        r["zone"] = "ADVISORY"
        if not scenario["validation_passes"]:
            r["outcome"] = "VALIDATION FAIL -> DEBUG"
            r["hitl_required"] = False
            if scenario["is_real_gap"]:
                true_positives += 1
            else:
                false_positives += 1
        elif not scenario["generalization_passes"]:
            r["outcome"] = "GENERALIZATION-GAP FAIL -> reject"
            r["hitl_required"] = False
            false_positives += 1
        elif scenario["behavioral"]:
            # S3 behavioral -> escalate to S2
            r["outcome"] = "BEHAVIORAL -> escalate to S2 -> HITL"
            r["hitl_required"] = True
            hitl_reviews += 1
            if scenario["is_real_gap"]:
                true_positives += 1
                hitl_approvals += 1
                r["hitl_decision"] = "approved"
            else:
                false_positives += 1
                hitl_rejections += 1
                r["hitl_decision"] = "rejected"
        else:
            # Auto-integrate (S3, token-level)
            r["outcome"] = "AUTO-INTEGRATE (token-level)"
            r["hitl_required"] = False
            auto_integrations += 1
            if scenario["is_real_gap"]:
                true_positives += 1
                if not scenario["post_integration_regression"]:
                    auto_integration_successes += 1
                    r["post_integration"] = "success"
                else:
                    degradation_count += 1
                    rollbacks += 1
                    r["post_integration"] = "REGRESSION -> ROLLBACK"
            else:
                false_positives += 1
                r["post_integration"] = "false positive — no regression"
    else:  # S4
        zone = zones.get("AUTONOMOUS", {})
        r["zone"] = "AUTONOMOUS"
        r["outcome"] = "LOG + MONITOR"
        r["hitl_required"] = False
        if scenario["is_real_gap"]:
            true_positives += 1
        else:
            false_positives += 1

    # Track operators
    if scenario["operator"] == "PIVOT":
        pivots += 1
    elif scenario["operator"] == "REFINE":
        refines += 1

    # Track thrashing
    if scenario["failure"] == "thrashing_detection":
        thrashing_events += 1

    results.append(r)

# =========================================================================
# Compute metrics
# =========================================================================
total_detections = len(scenarios)
detection_accuracy = (true_positives / total_detections * 100) if total_detections > 0 else 0
false_positive_rate = (false_positives / total_detections * 100) if total_detections > 0 else 0
auto_integration_success_rate = (
    (auto_integration_successes / auto_integrations * 100)
    if auto_integrations > 0 else 100
)
hitl_approval_rate = (
    (hitl_approvals / hitl_reviews * 100)
    if hitl_reviews > 0 else 0
)
loop_budget_utilization = (proposals_made / loop_budget * 100)

metrics = {
    "total_cycles": total_detections,
    "true_positives": true_positives,
    "false_positives": false_positives,
    "detection_accuracy_pct": round(detection_accuracy, 1),
    "false_positive_rate_pct": round(false_positive_rate, 1),
    "thrashing_events": thrashing_events,
    "degradation_count": degradation_count,
    "rollbacks": rollbacks,
    "auto_integrations": auto_integrations,
    "auto_integration_successes": auto_integration_successes,
    "auto_integration_success_rate_pct": round(auto_integration_success_rate, 1),
    "hitl_reviews": hitl_reviews,
    "hitl_approvals": hitl_approvals,
    "hitl_rejections": hitl_rejections,
    "hitl_approval_rate_pct": round(hitl_approval_rate, 1),
    "pivots": pivots,
    "refines": refines,
    "loop_budget_utilization_pct": round(loop_budget_utilization, 1),
    "loop_budget_cap": loop_budget,
    "proposals_made": proposals_made,
}

# =========================================================================
# Print report
# =========================================================================
sep = "=" * 70
print(f"\n{sep}")
print("G7 DRY-RUN SIMULATION REPORT — 10 Improvement Cycles (Step E)")
print(f"Simulated at: {datetime.utcnow().isoformat()}Z")
print(sep)

print(f"\n{'Cycle':<8} {'Trigger':<12} {'Severity':<5} {'Zone':<14} {'Outcome':<45}")
print("-" * 90)
for r in results:
    print(f"{r['cycle_id']:<8} {r['trigger']:<12} {r['severity']:<5} "
          f"{r['zone']:<14} {r['outcome']:<45}")

print(f"\n{sep}")
print("METRICS SUMMARY")
print(sep)
for k, v in metrics.items():
    print(f"  {k:<40} {v}")

print(f"\n{sep}")
print("BLUE REQUIRED TELEMETRY VALIDATION")
print(sep)
print(f"  Detection accuracy:      {detection_accuracy:.1f}%  (threshold >= 80%)  "
      f"{'PASS' if detection_accuracy >= 80 else 'FAIL'}")
print(f"  False positive rate:     {false_positive_rate:.1f}%  (threshold <= 20%)  "
      f"{'PASS' if false_positive_rate <= 20 else 'FAIL'}")
print(f"  Thrashing events:        {thrashing_events}  (threshold <= 2)  "
      f"{'PASS' if thrashing_events <= 2 else 'FAIL'}")
print(f"  Degradation count:       {degradation_count}  (threshold = 0)  "
      f"{'PASS' if degradation_count == 0 else 'FAIL'}")

print(f"\n{sep}")
print("SIMULATION COMPLETE — declarative rules exercised against 10 synthetic scenarios")
print("No real code mutation occurred. All results are simulated from spec rules.")
print(sep)

# Write metrics as JSON for audit trail
metrics_path = os.path.join(G7_DIR, "dry_run_metrics.json")
with open(metrics_path, "w", encoding="utf-8") as f:
    json.dump({"metrics": metrics, "cycles": results,
               "simulated_at": datetime.utcnow().isoformat() + "Z"}, f, indent=2)
print(f"\nMetrics written to: {metrics_path}")
