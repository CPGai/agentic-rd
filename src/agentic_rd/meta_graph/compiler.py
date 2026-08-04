"""Deterministic compiler for the isolated Meta-Graph routing overlay."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
from typing import Any, Mapping

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
OVERLAY_ARTIFACT_ROOT = REPOSITORY_ROOT / "specs" / "meta_graph"

READ_ONLY_VERBS = {
    "check",
    "describe",
    "inspect",
    "list",
    "read",
    "show",
    "summarize",
    "validate",
}
COMPLEXITY_MARKERS = (
    " and ",
    " then ",
    "parallel",
    "multi-worker",
    "multi worker",
    "skeptic",
    "audit",
    "approval",
    "high-stakes",
    "high stakes",
)
IRREVERSIBLE_OR_EGRESS_MARKERS = (
    "access",
    "credential",
    "database",
    "delete",
    "deprovision",
    "destroy",
    "drop",
    "email",
    "egress",
    "export",
    "grant",
    "install",
    "irreversible",
    "payment",
    "permission",
    "production",
    "publish",
    "purge",
    "remove",
    "revoke",
    "send",
    "transmit",
    "upload",
    "webhook",
)
SIDE_EFFECT_CLASSES = {
    "read_only",
    "reversible",
    "irreversible",
    "egress",
    "authorization",
    "unknown",
}
HIGH_RISK_SIDE_EFFECT_CLASSES = {"irreversible", "egress", "authorization", "unknown"}


def parse_objective(objective: str) -> str:
    """Normalize a non-empty operational objective."""
    normalized = " ".join(objective.split())
    if not normalized:
        raise ValueError("objective must not be blank")
    return normalized


def _parse_request(request: str | Mapping[str, Any]) -> tuple[str, str, bool]:
    """Normalize caller-declared risk metadata; legacy strings fail closed."""
    if isinstance(request, str):
        objective = parse_objective(request)
        if uses_single_step_escape_hatch(objective):
            return objective, "read_only", False
        return objective, "unknown", True
    if not isinstance(request, Mapping):
        raise TypeError("request must be an objective string or structured mapping")
    required = {"objective", "side_effect_class", "hitl_required"}
    missing = required - request.keys()
    if missing:
        raise ValueError(f"structured request is missing fields: {sorted(missing)}")
    objective = parse_objective(str(request["objective"]))
    side_effect_class = request["side_effect_class"]
    hitl_required = request["hitl_required"]
    if side_effect_class not in SIDE_EFFECT_CLASSES:
        raise ValueError("side_effect_class is not supported")
    if not isinstance(hitl_required, bool):
        raise ValueError("hitl_required must be boolean")
    if side_effect_class in HIGH_RISK_SIDE_EFFECT_CLASSES and not hitl_required:
        raise ValueError("high-risk side_effect_class requires hitl_required=true")
    return objective, side_effect_class, hitl_required


def _contains_marker(objective: str, markers: tuple[str, ...]) -> bool:
    normalized = f" {parse_objective(objective).lower()} "
    return any(marker in normalized for marker in markers)


def _first_word(objective: str) -> str:
    return parse_objective(objective).split(maxsplit=1)[0].rstrip(":").lower()


def uses_single_step_escape_hatch(objective: str) -> bool:
    """Allow only explicitly read-only, side-effect-free one-step objectives."""
    normalized = parse_objective(objective)
    return (
        _first_word(normalized) in READ_ONLY_VERBS
        and not _contains_marker(normalized, COMPLEXITY_MARKERS)
        and not _contains_marker(normalized, IRREVERSIBLE_OR_EGRESS_MARKERS)
    )


def _requires_hitl(objective: str) -> bool:
    normalized = parse_objective(objective).lower()
    return (
        _contains_marker(normalized, IRREVERSIBLE_OR_EGRESS_MARKERS)
        or "approval" in normalized
        or "high-stakes" in normalized
        or "high stakes" in normalized
    )


def select_topology(objective: str, *, hitl_required: bool) -> str:
    """Select the smallest topology; HITL comes from typed request metadata."""
    normalized = parse_objective(objective).lower()
    if uses_single_step_escape_hatch(normalized):
        return "single_step"
    if "skeptic" in normalized or "audit" in normalized:
        return "skeptic_audit"
    if "parallel" in normalized or "multi-worker" in normalized or "multi worker" in normalized:
        return "parallel_fan_out_fan_in"
    if hitl_required:
        return "hitl_approval"
    return "sequence"


def _graph_id(objective: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", objective.lower()).strip("-")
    prefix = slug[:36].rstrip("-") or "objective"
    return f"meta-graph-{prefix}-{sha256(objective.encode()).hexdigest()[:8]}"


def _node(node_id: str, kind: str, label: str) -> dict[str, str]:
    return {"id": node_id, "kind": kind, "label": label}


def _hitl_gate(required: bool) -> dict[str, Any]:
    if not required:
        return {"required": False, "resume_token": None}
    return {
        "required": True,
        "resume_token": None,
        "token_policy": "issuer_generated_single_use",
    }


def _base_nodes() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    return (
        [
            _node("objective_normalizer", "planner", "Objective Normalizer"),
            _node("planner", "planner", "Task Planner"),
        ],
        [{"from": "objective_normalizer", "to": "planner"}],
    )


def _complex_graph(
    objective: str, topology: str, side_effect_class: str, hitl_required: bool
) -> dict[str, Any]:
    nodes, edges = _base_nodes()
    controls: dict[str, Any]

    if topology == "sequence":
        nodes.append(_node("stage_executor", "worker", "Stage Executor"))
        edges.append({"from": "planner", "to": "stage_executor"})
        predecessor = "stage_executor"
        controls = {
            "typed_stage_contracts": "required",
            "failure_policy": "fail_fast",
        }
    elif topology == "parallel_fan_out_fan_in":
        nodes.extend(
            [
                _node("worker_a", "worker", "Worker A"),
                _node("worker_b", "worker", "Worker B"),
                _node("join", "terminal", "Join Results"),
            ]
        )
        edges.extend(
            [
                {"from": "planner", "to": "worker_a"},
                {"from": "planner", "to": "worker_b"},
                {"from": "worker_a", "to": "join"},
                {"from": "worker_b", "to": "join"},
            ]
        )
        predecessor = "join"
        controls = {
            "immutable_input_snapshot": "required",
            "join_policy": "all_success_or_fail_fast",
            "join_node": "join",
        }
    elif topology == "skeptic_audit":
        nodes.extend(
            [
                _node("worker_a", "worker", "Worker A"),
                _node("worker_b", "worker", "Worker B"),
                _node("skeptic", "skeptic", "Skeptic Gate"),
            ]
        )
        edges.extend(
            [
                {"from": "planner", "to": "worker_a"},
                {"from": "planner", "to": "worker_b"},
                {"from": "worker_a", "to": "skeptic"},
                {"from": "worker_b", "to": "skeptic"},
            ]
        )
        predecessor = "skeptic"
        controls = {
            "typed_worker_outputs": "required",
            "skeptic_rubric": "required",
            "failure_policy": "fail_fast",
        }
    elif topology == "hitl_approval":
        predecessor = "planner"
        controls = {
            "allowed_decisions": ["APPROVE", "REJECT", "REQUEST_REVISION"],
            "hitl_gate": "required",
            "single_use_resume_token": "external_issuer",
        }
    else:
        raise ValueError(f"unsupported topology: {topology}")

    if hitl_required:
        nodes.append(_node("hitl", "hitl", "Human Approval Gate"))
        edges.append({"from": predecessor, "to": "hitl"})
        predecessor = "hitl"
    nodes.append(_node("terminal", "terminal", "Execution Handshake"))
    edges.append({"from": predecessor, "to": "terminal"})

    return {
        "schema_version": "graph-spec/1.0",
        "graph_id": _graph_id(objective),
        "status": "PENDING_HITL" if hitl_required else "DRAFT",
        "objective": objective,
        "side_effect_class": side_effect_class,
        "hitl_requested": hitl_required,
        "topology": topology,
        "entry_node": "objective_normalizer",
        "nodes": nodes,
        "edges": edges,
        "controls": controls,
        "complexity_budget": {
            "max_spawn_width": 3,
            "max_spawn_depth": 1,
            "max_refinement_iterations": 3,
        },
        "hitl_gate": _hitl_gate(hitl_required),
    }


def build_graph_spec(request: str | Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic canonical graph specification from typed input."""
    normalized, side_effect_class, hitl_required = _parse_request(request)
    topology = select_topology(normalized, hitl_required=hitl_required)
    if topology == "single_step":
        return {
            "schema_version": "graph-spec/1.0",
            "graph_id": _graph_id(normalized),
            "status": "APPROVED",
            "objective": normalized,
            "side_effect_class": side_effect_class,
            "hitl_requested": False,
            "topology": topology,
            "entry_node": None,
            "nodes": [],
            "edges": [],
            "controls": {"graph_engine": "bypassed"},
            "complexity_budget": {
                "max_spawn_width": 0,
                "max_spawn_depth": 0,
                "max_refinement_iterations": 0,
            },
            "hitl_gate": _hitl_gate(False),
        }
    return _complex_graph(normalized, topology, side_effect_class, hitl_required)


def compile_objective(request: str | Mapping[str, Any]) -> dict[str, Any]:
    """Compile a legacy string or structured request to a canonical graph spec."""
    return build_graph_spec(request)


def validate_graph_spec(graph: dict[str, Any]) -> None:
    """Reject graph artifacts that violate the canonical overlay contract."""
    required = {
        "schema_version",
        "graph_id",
        "status",
        "objective",
        "side_effect_class",
        "hitl_requested",
        "topology",
        "entry_node",
        "nodes",
        "edges",
        "controls",
        "complexity_budget",
        "hitl_gate",
    }
    missing = required - graph.keys()
    if missing:
        raise ValueError(f"graph is missing required fields: {sorted(missing)}")
    if graph["schema_version"] != "graph-spec/1.0":
        raise ValueError("schema_version must be graph-spec/1.0")
    if graph["status"] not in {"DRAFT", "PENDING_HITL", "APPROVED", "REJECTED"}:
        raise ValueError("status is not supported")
    if not isinstance(graph["hitl_requested"], bool):
        raise ValueError("hitl_requested must be boolean")

    topology = graph["topology"]
    required_controls = {
        "single_step": {"graph_engine"},
        "sequence": {"typed_stage_contracts", "failure_policy"},
        "parallel_fan_out_fan_in": {
            "immutable_input_snapshot",
            "join_policy",
            "join_node",
        },
        "skeptic_audit": {
            "typed_worker_outputs",
            "skeptic_rubric",
            "failure_policy",
        },
        "hitl_approval": {
            "allowed_decisions",
            "hitl_gate",
            "single_use_resume_token",
        },
    }
    if topology not in required_controls:
        raise ValueError(f"unsupported topology: {topology}")
    if not required_controls[topology].issubset(graph["controls"]):
        raise ValueError(f"controls do not satisfy topology: {topology}")

    node_ids = {node["id"] for node in graph["nodes"]}
    if len(node_ids) != len(graph["nodes"]):
        raise ValueError("node IDs must be unique")
    controls = graph["controls"]
    if topology == "single_step" and controls["graph_engine"] != "bypassed":
        raise ValueError("single_step graph_engine must be bypassed")
    if topology == "parallel_fan_out_fan_in" and controls["join_node"] not in node_ids:
        raise ValueError("parallel join_node must reference a graph node")
    if topology == "hitl_approval":
        if controls["hitl_gate"] != "required":
            raise ValueError("hitl_approval control must require an HITL gate")
        if controls["single_use_resume_token"] != "external_issuer":
            raise ValueError("hitl_approval must use an external single-use token issuer")
    if topology == "single_step":
        if graph["entry_node"] is not None or graph["nodes"] or graph["edges"]:
            raise ValueError("single_step must have null entry_node and no graph nodes or edges")
    elif not isinstance(graph["entry_node"], str) or graph["entry_node"] not in node_ids:
        raise ValueError("non-single-step entry_node must reference a graph node")
    for edge in graph["edges"]:
        if edge["from"] not in node_ids or edge["to"] not in node_ids:
            raise ValueError("edge endpoints must reference graph nodes")

    budget = graph["complexity_budget"]
    if budget["max_spawn_width"] > 3 or budget["max_spawn_depth"] > 1:
        raise ValueError("complexity budget exceeds overlay caps")

    hitl_gate = graph["hitl_gate"]
    side_effect_class = graph["side_effect_class"]
    hitl_required = graph["hitl_requested"]
    if side_effect_class not in SIDE_EFFECT_CLASSES:
        raise ValueError("side_effect_class is not supported")
    if side_effect_class in HIGH_RISK_SIDE_EFFECT_CLASSES and not hitl_required:
        raise ValueError("high-risk side_effect_class requires an HITL gate")
    if hitl_required and not hitl_gate["required"]:
        raise ValueError("high-stakes objective requires an HITL gate")
    if hitl_gate["required"]:
        if "hitl" not in node_ids:
            raise ValueError("required HITL gate must have an HITL node")
        if graph["status"] != "PENDING_HITL":
            raise ValueError("HITL graph status must be PENDING_HITL")
        if hitl_gate["resume_token"] is not None:
            raise ValueError("compiler must not emit a reusable resume_token")
        if hitl_gate.get("token_policy") != "issuer_generated_single_use":
            raise ValueError("HITL token policy must be issuer_generated_single_use")
    elif hitl_gate["resume_token"] is not None:
        raise ValueError("non-HITL graph must not contain a resume_token")


def render_graph_markdown(graph: dict[str, Any]) -> str:
    """Render the exact canonical node and edge layout as Mermaid Markdown."""
    validate_graph_spec(graph)
    mermaid_nodes = [f"    {node['id']}[{node['label']}]" for node in graph["nodes"]]
    mermaid_edges = [f"    {edge['from']} --> {edge['to']}" for edge in graph["edges"]]
    diagram = "\n".join(["graph TD", *mermaid_nodes, *mermaid_edges])
    state = {
        "graph_id": graph["graph_id"],
        "status": graph["status"],
        "topology": graph["topology"],
        "hitl_required": graph["hitl_gate"]["required"],
    }
    return (
        f"# Graph Architecture View: {graph['graph_id']}\n\n"
        "> **Non-normative:** canonical contract is `GRAPH_SPEC.yaml`.\n\n"
        "## Topology Diagram\n\n"
        f"```mermaid\n{diagram}\n```\n\n"
        "## Shared State Vector ($S_t$)\n\n"
        "```yaml\n"
        f"{yaml.safe_dump(state, sort_keys=False).rstrip()}\n"
        "```\n"
    )


def _resolve_output_directory(output_directory: Path | str) -> Path:
    root = OVERLAY_ARTIFACT_ROOT.resolve()
    candidate = Path(output_directory)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("output path is outside the Meta-Graph overlay scope") from exc
    return resolved


def write_graph_artifacts(
    graph: dict[str, Any], output_directory: Path | str = "."
) -> tuple[Path, Path]:
    """Write canonical YAML and a generated Markdown view within overlay scope."""
    validate_graph_spec(graph)
    output_path = _resolve_output_directory(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)
    yaml_path = output_path / "GRAPH_SPEC.yaml"
    markdown_path = output_path / "GRAPH_SPEC.md"
    yaml_path.write_text(yaml.safe_dump(graph, sort_keys=False), encoding="utf-8")
    markdown_path.write_text(render_graph_markdown(graph), encoding="utf-8")
    return yaml_path, markdown_path
