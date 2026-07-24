#!/usr/bin/env python3
"""Unit tests for G2 security structural auditors (stdlib unittest).

Run:
  cd /home/carlospg/workspace/agentic-rd && source .venv-hermes/bin/activate \\
    && python -m unittest tests.test_g2_security -v
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path("/home/carlospg/workspace/agentic-rd")
sys.path.insert(0, str(ROOT / "scripts"))

from g2_security.confused_deputy import (  # noqa: E402
    audit_confused_deputy_posture,
    detect_tool_shadowing,
    end_user_authz_required,
)
from g2_security.mock_rpc import (  # noqa: E402
    handshake_script,
    is_error,
    is_tool_execution_error,
    mock_tools_call_ok,
    mock_unknown_tool_error,
    validate_handshake_pair,
)
from g2_security.pin_enforce import collect_pin_violations  # noqa: E402
from g2_security.sanitize import (  # noqa: E402
    sanitize_tool_arg,
    sanitize_tool_output,
)


class SanitizeTests(unittest.TestCase):
    def test_clean_query_ok(self) -> None:
        self.assertTrue(sanitize_tool_arg("query", "explain useState hooks").ok)

    def test_secret_arg_blocked(self) -> None:
        self.assertFalse(sanitize_tool_arg("query", "api_key=supersecretvalue99").ok)

    def test_path_traversal_blocked(self) -> None:
        self.assertFalse(sanitize_tool_arg("path", "../../secrets").ok)

    def test_library_id_shape(self) -> None:
        self.assertTrue(sanitize_tool_arg("libraryId", "/facebook/react").ok)
        self.assertFalse(sanitize_tool_arg("libraryId", "facebook/react").ok)

    def test_output_redacts_sk(self) -> None:
        out = sanitize_tool_output("leaked sk-abcdefghijklmnop token")
        self.assertIn("REDACTED", out.redacted)


class ConfusedDeputyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        g2 = ROOT / "specs/g2_tools"
        cls.broker = yaml.safe_load((g2 / "broker_config.yaml").read_text(encoding="utf-8"))
        cls.matrix = yaml.safe_load((g2 / "MCP_COMPAT_MATRIX.yaml").read_text(encoding="utf-8"))

    def test_posture_no_blockers(self) -> None:
        report = audit_confused_deputy_posture(self.broker, self.matrix)
        self.assertEqual(report.blocker_count, 0, report.as_dict())

    def test_shadowing_collision(self) -> None:
        findings = detect_tool_shadowing(
            [
                {"name": "save_note", "server_id": "a"},
                {"name": "save_note", "server_id": "b"},
            ]
        )
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].code, "TOOL_NAME_COLLISION")

    def test_end_user_authz_on_unauth_write(self) -> None:
        self.assertTrue(
            end_user_authz_required({"authenticated": False, "tier": "T2"}, "write_file")
        )
        self.assertFalse(
            end_user_authz_required({"authenticated": False, "tier": "T2"}, "query-docs")
        )


class PinEnforceTests(unittest.TestCase):
    def test_pins_green(self) -> None:
        viol = collect_pin_violations()
        self.assertEqual(viol, [], viol)

    def test_version_is_324(self) -> None:
        pins = json.loads(
            (ROOT / "specs/g2_tools/pins/npm-mcp-pins.json").read_text(encoding="utf-8")
        )
        row = next(p for p in pins["pins"] if p["server_id"] == "context7")
        self.assertEqual(row["version"], "3.2.4")


class MockRpcTests(unittest.TestCase):
    def test_handshake_pairs(self) -> None:
        for req, resp in handshake_script():
            self.assertEqual(validate_handshake_pair(req, resp), [])

    def test_protocol_error_shape(self) -> None:
        err = mock_unknown_tool_error(9)
        self.assertTrue(is_error(err))
        self.assertEqual(err["error"]["code"], -32602)

    def test_tool_exec_error_flag(self) -> None:
        msg = mock_tools_call_ok(4, "fail")
        msg["result"]["isError"] = True
        self.assertTrue(is_tool_execution_error(msg))


if __name__ == "__main__":
    unittest.main()
