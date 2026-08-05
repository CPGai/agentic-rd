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


def test_explicit_hitl_request_overrides_single_step() -> None:
    graph = _compiler()(
        {"objective": "Inspect the proposed deployment plan.", "side_effect_class": "reversible", "hitl_required": True}
    )
    assert graph["status"] == "PENDING_HITL"
    assert graph["hitl_gate"]["required"] is True
    assert graph["topology"] != "single_step"


def test_structured_objective_must_be_a_nonblank_string() -> None:
    with pytest.raises(ValueError, match="objective must be a non-blank string"):
        _compiler()({"objective": None, "side_effect_class": "authorization", "hitl_required": True})


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


def test_validator_requires_semantic_hitl_controls_and_node_kind() -> None:
    from agentic_rd.meta_graph import compiler

    request = {
        "objective": "Approve a production change.",
        "side_effect_class": "authorization",
        "hitl_required": True,
    }
    invalid_control = compiler.compile_objective(request)
    invalid_control["controls"]["hitl_gate"] = "bypassed"
    with pytest.raises(ValueError, match="control"):
        compiler.validate_graph_spec(invalid_control)

    invalid_node = compiler.compile_objective(request)
    next(node for node in invalid_node["nodes"] if node["id"] == "hitl")["kind"] = "worker"
    with pytest.raises(ValueError, match="kind"):
        compiler.validate_graph_spec(invalid_node)


def test_mermaid_labels_cannot_inject_syntax_or_edges() -> None:
    from agentic_rd.meta_graph import compiler

    graph = compiler.compile_objective(
        {
            "objective": "Research [test] 'quote' \"double\"\nNext line",
            "side_effect_class": "reversible",
            "hitl_required": False,
        }
    )
    graph["nodes"][0]["label"] = "Safe] --> injected[Node]\n'\""
    markdown = compiler.render_graph_markdown(graph)
    diagram = markdown.split("```mermaid\n", 1)[1].split("\n```", 1)[0]

    node_line = next(line for line in diagram.splitlines() if "objective_normalizer" in line)
    assert node_line.count("[") == 1
    assert node_line.count("]") == 1
    assert "'" not in node_line
    assert '"' not in node_line
    assert diagram.count("-->") == len(graph["edges"])


def test_validator_rejects_mermaid_unsafe_node_identifiers() -> None:
    from agentic_rd.meta_graph import compiler

    graph = compiler.compile_objective(
        {"objective": "Create a local report.", "side_effect_class": "reversible", "hitl_required": False}
    )
    graph["nodes"][0]["id"] = "safe] --> injected[Node"
    graph["edges"][0]["from"] = "safe] --> injected[Node"
    graph["entry_node"] = "safe] --> injected[Node"
    with pytest.raises(ValueError, match="schema validation failed"):
        compiler.render_graph_markdown(graph)


@pytest.mark.parametrize(
    ("input_data", "control", "invalid_value"),
    [
        ({"objective": "Create a local report.", "side_effect_class": "reversible", "hitl_required": False}, "typed_stage_contracts", "bypassed"),
        ({"objective": "Create a local report.", "side_effect_class": "reversible", "hitl_required": False}, "failure_policy", "continue_on_error"),
        ({"objective": "Research with parallel workers.", "side_effect_class": "reversible", "hitl_required": False}, "immutable_input_snapshot", "bypassed"),
        ({"objective": "Research with parallel workers.", "side_effect_class": "reversible", "hitl_required": False}, "join_node", "planner"),
        ({"objective": "Audit findings with a skeptic.", "side_effect_class": "reversible", "hitl_required": False}, "typed_worker_outputs", "optional"),
        ({"objective": "Approve a production change.", "side_effect_class": "authorization", "hitl_required": True}, "allowed_decisions", ["AUTO_APPROVE"]),
    ],
)
def test_validator_rejects_disabled_required_control_values(input_data: dict[str, object], control: str, invalid_value: object) -> None:
    from agentic_rd.meta_graph import compiler

    graph = compiler.compile_objective(input_data)
    graph["controls"][control] = invalid_value
    with pytest.raises(ValueError, match="control"):
        compiler.validate_graph_spec(graph)


def test_json_schema_validation_enforces_contract() -> None:
    from agentic_rd.meta_graph import compiler

    graph = compiler.compile_objective(
        {"objective": "Create a local report.", "side_effect_class": "reversible", "hitl_required": False}
    )
    graph["status"] = "INVALID"
    graph["unexpected"] = True
    with pytest.raises(ValueError, match="schema"):
        compiler.validate_graph_spec(graph)


def test_dfs_path_dominator_catches_shortcut_bypasses() -> None:
    from agentic_rd.meta_graph import compiler

    graph = compiler.compile_objective(
        {"objective": "Authorize a vendor contract.", "side_effect_class": "authorization", "hitl_required": True}
    )
    graph["edges"].append({"from": "planner", "to": "terminal"})
    with pytest.raises(ValueError, match="every execution path must traverse the required HITL gate"):
        compiler.validate_graph_spec(graph)


def test_compile_request_typed_envelope() -> None:
    from agentic_rd.meta_graph.compiler import CompileRequest

    request = CompileRequest.from_input({"objective": "Inspect records.", "side_effect_class": "unknown", "hitl_required": False})
    assert request.objective == "Inspect records."
    assert request.hitl_required is True
    assert CompileRequest.from_input("List files.").side_effect_class == "read_only"


def test_mermaid_ast_value_objects_sanitize_and_validate() -> None:
    from agentic_rd.meta_graph.compiler import MermaidEdge, MermaidNode, MermaidGraph

    node = MermaidNode("safe_id", "Bad] --> injected['quote']\nNext")
    edge = MermaidEdge("safe_id", "terminal")
    output = MermaidGraph([node], [edge]).to_mermaid()
    assert output.count("-->") == 1
    assert "injected[" not in output
    with pytest.raises(ValueError, match="Mermaid-safe"):
        MermaidNode("bad] --> injected", "label")


def test_orphaned_hitl_graph_nodes_fail_closed() -> None:
    from agentic_rd.meta_graph import compiler

    graph = compiler.compile_objective(
        {"objective": "Authorize a vendor contract.", "side_effect_class": "authorization", "hitl_required": True}
    )
    graph["nodes"].append({"id": "orphan", "kind": "worker", "label": "Orphan"})
    graph["edges"].append({"from": "orphan", "to": "terminal"})
    with pytest.raises(ValueError, match="unreachable"):
        compiler.validate_graph_spec(graph)


def test_schema_rejects_extra_controls_and_envelope_fields() -> None:
    from agentic_rd.meta_graph import compiler

    graph = compiler.compile_objective(
        {"objective": "Create a local report.", "side_effect_class": "reversible", "hitl_required": False}
    )
    graph["controls"]["injected"] = "bypass"
    with pytest.raises(ValueError, match="schema validation failed"):
        compiler.validate_graph_spec(graph)
    with pytest.raises(ValueError, match="unexpected"):
        compiler.CompileRequest.from_input({"objective": "x", "side_effect_class": "reversible", "hitl_required": False, "unexpected": True})


def test_validator_rejects_cycles_and_non_sink_terminal() -> None:
    from agentic_rd.meta_graph import compiler

    cycle = compiler.compile_objective({"objective": "Research in sequence.", "side_effect_class": "reversible", "hitl_required": False})
    cycle["edges"].append({"from": "stage_executor", "to": "planner"})
    with pytest.raises(ValueError, match="cycle"):
        compiler.validate_graph_spec(cycle)

    continuation = compiler.compile_objective({"objective": "Research in sequence.", "side_effect_class": "reversible", "hitl_required": False})
    continuation["edges"].append({"from": "terminal", "to": "stage_executor"})
    with pytest.raises(ValueError, match="terminal"):
        compiler.validate_graph_spec(continuation)


def test_validator_binds_hitl_gate_to_request() -> None:
    from agentic_rd.meta_graph import compiler

    graph = compiler.compile_objective({"objective": "Research in sequence.", "side_effect_class": "reversible", "hitl_required": False})
    graph["hitl_gate"]["required"] = True
    graph["status"] = "PENDING_HITL"
    with pytest.raises(ValueError, match="hitl_requested"):
        compiler.validate_graph_spec(graph)


def test_writer_rejects_existing_output_symlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from agentic_rd.meta_graph import compiler

    artifact_root = tmp_path / "specs" / "meta_graph"
    artifact_root.mkdir(parents=True)
    monkeypatch.setattr(compiler, "OVERLAY_ARTIFACT_ROOT", artifact_root)
    outside = tmp_path / "outside.yaml"
    yaml_path = artifact_root / "GRAPH_SPEC.yaml"
    yaml_path.symlink_to(outside)
    graph = _compiler()("Inspect the repository Python packages.")
    with pytest.raises(ValueError, match="symlink"):
        compiler.write_graph_artifacts(graph)
