# Copyright: (c) 2024, Tosin Akinosho <tosin.akinosho@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type
"""Unit tests for mcp_reporter module_utils."""

import json

from ansible_collections.mcp.audit.plugins.module_utils.mcp_reporter import (
    MCPReporter,
    create_result,
)


class TestMCPReporter:
    """Test cases for MCPReporter class."""

    def test_create_module_result_success(self):
        """Test creating a successful module result."""
        result = MCPReporter.create_module_result(
            success=True,
            status="ok",
            response={"data": "test"},
            execution_time=1.234,
        )

        assert result["success"] is True
        assert result["changed"] is False
        assert result["status"] == "ok"
        assert result["response"] == {"data": "test"}
        assert result["execution_time"] == 1.234
        assert result["error"] is None
        assert "timestamp" in result["metadata"]

    def test_create_module_result_failure(self):
        """Test creating a failed module result."""
        result = MCPReporter.create_module_result(
            success=False,
            status="failed",
            error="Connection timeout",
            execution_time=30.0,
        )

        assert result["success"] is False
        assert result["status"] == "failed"
        assert result["error"] == "Connection timeout"
        assert result["execution_time"] == 30.0

    def test_create_module_result_with_metadata(self):
        """Test creating a module result with custom metadata."""
        metadata = {
            "transport": "stdio",
            "server_command": "python server.py",
        }

        result = MCPReporter.create_module_result(
            success=True,
            status="ok",
            metadata=metadata,
        )

        assert result["metadata"]["transport"] == "stdio"
        assert result["metadata"]["server_command"] == "python server.py"
        assert "timestamp" in result["metadata"]

    def test_create_test_report(self):
        """Test creating a test suite report."""
        summary = {
            "total_tests": 10,
            "passed": 8,
            "failed": 2,
            "skipped": 0,
        }
        tests = [
            {"name": "test1", "execution_time": 1.0, "success": True},
            {"name": "test2", "execution_time": 2.0, "success": False},
        ]

        report = MCPReporter.create_test_report(summary, tests)

        assert report["summary"]["total_tests"] == 10
        assert report["summary"]["passed"] == 8
        assert report["summary"]["failed"] == 2
        assert report["summary"]["success_rate"] == 80.0
        assert report["summary"]["total_duration"] == 3.0
        assert len(report["tests"]) == 2
        assert "timestamp" in report["metadata"]

    def test_format_tool_result(self):
        """Test formatting a tool test result."""
        result = MCPReporter.format_tool_result(
            tool_name="add",
            success=True,
            response="8",
            execution_time=0.5,
            arguments={"a": 3, "b": 5},
            expected_result="8",
        )

        assert result["test_type"] == "tool"
        assert result["tool_name"] == "add"
        assert result["success"] is True
        assert result["execution_time"] == 0.5
        assert result["arguments"] == {"a": 3, "b": 5}
        assert result["expected_result"] == "8"

    def test_format_resource_result(self):
        """Test formatting a resource test result."""
        result = MCPReporter.format_resource_result(
            resource_uri="file:///test.txt",
            success=True,
            response="file content",
            execution_time=0.3,
            expected_content_type="text/plain",
        )

        assert result["test_type"] == "resource"
        assert result["resource_uri"] == "file:///test.txt"
        assert result["success"] is True
        assert result["execution_time"] == 0.3
        assert result["expected_content_type"] == "text/plain"

    def test_format_prompt_result(self):
        """Test formatting a prompt test result."""
        result = MCPReporter.format_prompt_result(
            prompt_name="greeting",
            success=True,
            response={"message": "Hello"},
            execution_time=0.2,
            arguments={"name": "World"},
        )

        assert result["test_type"] == "prompt"
        assert result["prompt_name"] == "greeting"
        assert result["success"] is True
        assert result["execution_time"] == 0.2
        assert result["arguments"] == {"name": "World"}

    def test_to_json_pretty(self):
        """Test converting data to pretty JSON."""
        data = {"key": "value", "number": 42}
        json_str = MCPReporter.to_json(data, pretty=True)

        assert '"key": "value"' in json_str
        assert '"number": 42' in json_str
        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed == data

    def test_to_json_compact(self):
        """Test converting data to compact JSON."""
        data = {"key": "value"}
        json_str = MCPReporter.to_json(data, pretty=False)

        assert "\n" not in json_str
        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed == data

    def test_serialize_response_dict(self):
        """Test serializing a dictionary response."""
        response = {"result": "success", "data": [1, 2, 3]}
        serialized = MCPReporter._serialize_response(response)

        assert serialized == response

    def test_serialize_response_list(self):
        """Test serializing a list response."""
        response = [{"id": 1}, {"id": 2}]
        serialized = MCPReporter._serialize_response(response)

        assert serialized == response

    def test_serialize_response_none(self):
        """Test serializing None response."""
        serialized = MCPReporter._serialize_response(None)

        assert serialized is None

    def test_serialize_response_primitive(self):
        """Test serializing primitive types."""
        assert MCPReporter._serialize_response("test") == "test"
        assert MCPReporter._serialize_response(42) == 42
        assert MCPReporter._serialize_response(3.14) == 3.14
        assert MCPReporter._serialize_response(True) is True

    def test_serialize_response_nested(self):
        """Test serializing nested structures."""
        response = {
            "outer": {
                "inner": ["a", "b"],
                "number": 123,
            }
        }
        serialized = MCPReporter._serialize_response(response)

        assert serialized == response


class TestCreateResultConvenience:
    """Test cases for create_result convenience function."""

    def test_create_result_basic(self):
        """Test basic create_result usage."""
        result = create_result(
            success=True,
            status="ok",
            execution_time=1.0,
        )

        assert result["success"] is True
        assert result["status"] == "ok"
        assert result["execution_time"] == 1.0

    def test_create_result_with_kwargs(self):
        """Test create_result with additional kwargs."""
        result = create_result(
            success=True,
            status="ok",
            changed=True,
            metadata={"test": "data"},
        )

        assert result["success"] is True
        assert result["changed"] is True
        assert result["metadata"]["test"] == "data"
