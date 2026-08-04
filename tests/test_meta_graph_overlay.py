"""Conformance tests for the isolated Meta-Graph routing overlay."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "specs" / "meta_graph"
PROTECTED_ROOTS = (
    "AGENTS.md",
    "HARNESS_SPEC.md",
    "specs/workflow_graph.yaml",
)


def _compiler():
    try:
        from agentic_rd.meta_graph.compiler import compile_objective
    except ModuleNotFoundError as exc:
        pytest.fail(f"meta-graph compiler is not implemented: {exc}")
    return compile_objective


def test_protected_root_constitution_matches_head() -> None:
    for relative_path in PROTECTED_ROOTS:
        actual = (ROOT / relative_path).read_bytes()
        expected = subprocess.check_output(
            ["git", "show", f"HEAD:{relative_path}"], cwd=ROOT
        )
        assert actual == expected, f"protected root changed: {relative_path}"


def test_simple_objective_uses_single_step_escape_hatch() -> None:
    graph = _compiler()("List the repository Python packages.")

    assert graph["topology"] == "single_step"
    assert graph["nodes"] == []
    assert graph["edges"] == []


def test_non_read_only_legacy_string_is_conservatively_pending_hitl() -> None:
    graph = _compiler()("Erase customer records.")

    assert graph["status"] == "PENDING_HITL"
    assert graph["hitl_gate"]["required"] is True


def test_structured_input_requires_hitl_for_high_risk_class() -> None:
    graph = _compiler()(
        {
            "objective": "Authorize a vendor contract.",
            "side_effect_class": "authorization",
            "hitl_required": True,
        }
    )

    assert graph["topology"] == "hitl_approval"
    assert graph["side_effect_class"] == "authorization"
    assert graph["hitl_gate"]["required"] is True


def _load_yaml(name: str) -> dict[str, object]:
    path = OVERLAY / name
    assert path.is_file(), f"missing overlay artifact: {path}"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_overlay_scopes_local_g4_context_without_global_bleed() -> None:
    policy = _load_yaml("OVERLAY_POLICY.yaml")

    assert policy["overlay_id"] == "META_GRAPH_ROUTING_OVERLAY_v1"
    assert policy["target_scope"] == "specs/meta_graph/"
    assert policy["ephemeral_overrides"]["g4_orchestration"] == {
        "status": "ACTIVE_LOCAL_SCOPE",
        "l3_specialists_enabled": True,
        "max_spawn_width": 3,
        "max_spawn_depth": 1,
    }
    assert policy["root_immutability"]["specs/workflow_graph.yaml"] == "UNTOUCHED"
    assert policy["default_routing"] == "single_agent"


def test_canonical_schema_and_topology_catalog_cover_mvp() -> None:
    schema = _load_yaml("canonical_schema.yaml")
    catalog = _load_yaml("topology_catalog.yaml")

    assert set(schema["graph_spec"]["required"]) >= {
        "schema_version",
        "graph_id",
        "status",
        "entry_node",
        "nodes",
        "edges",
        "complexity_budget",
        "hitl_gate",
    }
    assert set(catalog["patterns"]) == {
        "single_step",
        "sequence",
        "parallel_fan_out_fan_in",
        "skeptic_audit",
        "hitl_approval",
    }


def test_complex_objective_renders_matching_mermaid_graph(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    try:
        from agentic_rd.meta_graph import compiler
    except ImportError as exc:
        pytest.fail(f"complex graph compiler is not implemented: {exc}")

    artifact_root = tmp_path / "specs" / "meta_graph"
    monkeypatch.setattr(compiler, "OVERLAY_ARTIFACT_ROOT", artifact_root)
    graph = _compiler()(
        "Research in parallel with two workers, pass findings through a skeptic audit, "
        "then require human approval before execution."
    )
    markdown = compiler.render_graph_markdown(graph)
    yaml_path, markdown_path = compiler.write_graph_artifacts(graph, artifact_root / "review")

    assert graph["topology"] == "skeptic_audit"
    assert graph["hitl_gate"]["required"] is True
    assert graph["hitl_gate"]["resume_token"] is None
    assert graph["hitl_gate"]["token_policy"] == "issuer_generated_single_use"
    assert "```mermaid" in markdown
    assert "graph TD" in markdown
    assert "-->" in markdown
    for node in graph["nodes"]:
        assert node["id"] in markdown
    for edge in graph["edges"]:
        assert f"{edge['from']} --> {edge['to']}" in markdown
    assert yaml_path.name == "GRAPH_SPEC.yaml"
    assert markdown_path.name == "GRAPH_SPEC.md"
    assert yaml.safe_load(yaml_path.read_text(encoding="utf-8")) == graph
    assert markdown_path.read_text(encoding="utf-8") == markdown


def test_irreversible_objective_requires_hitl_and_no_static_token() -> None:
    graph = _compiler()("Delete the production database.")

    assert graph["topology"] == "hitl_approval"
    assert graph["status"] == "PENDING_HITL"
    assert graph["hitl_gate"] == {
        "required": True,
        "resume_token": None,
        "token_policy": "issuer_generated_single_use",
    }


@pytest.mark.parametrize(
    "objective",
    ["Perform an irreversible operation.", "Egress live customer records."],
)
def test_explicit_irreversible_or_egress_objectives_require_hitl(objective: str) -> None:
    graph = _compiler()(objective)

    assert graph["topology"] == "hitl_approval"
    assert graph["status"] == "PENDING_HITL"
    assert graph["hitl_gate"]["required"] is True


def test_compiled_graphs_conform_to_entry_and_control_contracts() -> None:
    schema = _load_yaml("canonical_schema.yaml")
    read_only = _compiler()("Inspect the repository Python packages.")
    sequence = _compiler()(
        {"objective": "Create a local report.", "side_effect_class": "reversible", "hitl_required": False}
    )
    skeptic = _compiler()(
        {"objective": "Audit worker findings with a skeptic.", "side_effect_class": "reversible", "hitl_required": False}
    )
    parallel = _compiler()(
        {"objective": "Research with parallel workers.", "side_effect_class": "reversible", "hitl_required": False}
    )
    hitl = _compiler()("Approve a production change.")

    assert "null" in schema["graph_spec"]["properties"]["entry_node"]["type"]
    assert read_only["entry_node"] is None
    assert sequence["topology"] == "sequence"
    assert sequence["hitl_gate"]["required"] is False
    assert set(sequence["controls"]) == {"typed_stage_contracts", "failure_policy"}
    assert skeptic["topology"] == "skeptic_audit"
    assert skeptic["hitl_gate"]["required"] is False
    assert set(skeptic["controls"]) == {
        "typed_worker_outputs",
        "skeptic_rubric",
        "failure_policy",
    }
    assert parallel["topology"] == "parallel_fan_out_fan_in"
    assert set(parallel["controls"]) == {
        "immutable_input_snapshot",
        "join_policy",
        "join_node",
    }
    assert hitl["topology"] == "hitl_approval"
    assert set(hitl["controls"]) == {
        "allowed_decisions",
        "hitl_gate",
        "single_use_resume_token",
    }


def test_writer_rejects_artifacts_outside_overlay_scope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from agentic_rd.meta_graph import compiler

    artifact_root = tmp_path / "specs" / "meta_graph"
    monkeypatch.setattr(compiler, "OVERLAY_ARTIFACT_ROOT", artifact_root)
    graph = _compiler()("Inspect the repository Python packages.")

    with pytest.raises(ValueError, match="outside the Meta-Graph overlay scope"):
        compiler.write_graph_artifacts(graph, tmp_path / "outside")


def test_validator_rejects_null_entry_node_for_non_single_step(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from agentic_rd.meta_graph import compiler

    artifact_root = tmp_path / "specs" / "meta_graph"
    monkeypatch.setattr(compiler, "OVERLAY_ARTIFACT_ROOT", artifact_root)
    graph = _compiler()("Create a local report.")
    graph["entry_node"] = None

    with pytest.raises(ValueError, match="entry_node"):
        compiler.render_graph_markdown(graph)
    with pytest.raises(ValueError, match="entry_node"):
        compiler.write_graph_artifacts(graph, artifact_root / "invalid")
    assert not (artifact_root / "invalid" / "GRAPH_SPEC.yaml").exists()
