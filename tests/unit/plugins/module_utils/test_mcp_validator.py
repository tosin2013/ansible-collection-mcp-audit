# Copyright: (c) 2024, Tosin Akinosho <tosin.akinosho@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type
"""Unit tests for mcp_validator module_utils."""

import pytest
from ansible_collections.mcp.audit.plugins.module_utils.mcp_validator import (
    MCPValidator,
    validate_response,
)


class MockToolResponse:
    """Mock MCP tool response for testing."""

    def __init__(self, content):
        self.content = content


class MockContentItem:
    """Mock content item for testing."""

    def __init__(self, item_type, text=None, data=None):
        self.type = item_type
        if text is not None:
            self.text = text
        if data is not None:
            self.data = data


class MockResourceResponse:
    """Mock MCP resource response for testing."""

    def __init__(self, contents):
        self.contents = contents


class MockResourceContent:
    """Mock resource content for testing."""

    def __init__(self, mime_type, text=None):
        self.mimeType = mime_type
        if text is not None:
            self.text = text


class MockPromptResponse:
    """Mock MCP prompt response for testing."""

    def __init__(self, messages):
        self.messages = messages


class MockTool:
    """Mock MCP tool for testing."""

    def __init__(self, name, description=None):
        self.name = name
        if description:
            self.description = description


class TestMCPValidator:
    """Test cases for MCPValidator class."""

    def test_validate_tool_response_success(self):
        """Test validating a successful tool response."""
        content = [MockContentItem("text", text="result")]
        response = MockToolResponse(content)

        result = MCPValidator.validate_tool_response(response)

        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert result["matches_expected"] is None

    def test_validate_tool_response_none(self):
        """Test validating a None tool response."""
        result = MCPValidator.validate_tool_response(None)

        assert result["valid"] is False
        assert "Tool response is None" in result["errors"]

    def test_validate_tool_response_empty_content(self):
        """Test validating a tool response with empty content."""
        response = MockToolResponse([])

        result = MCPValidator.validate_tool_response(response)

        assert result["valid"] is True
        assert "Response content is empty" in result["warnings"]

    def test_validate_tool_response_with_expected_result(self):
        """Test validating a tool response with expected result."""
        content = [MockContentItem("text", text="8")]
        response = MockToolResponse(content)

        result = MCPValidator.validate_tool_response(response, expected_result="8")

        assert result["valid"] is True
        assert result["matches_expected"] is True

    def test_validate_tool_response_mismatch_expected(self):
        """Test validating a tool response that doesn't match expected."""
        content = [MockContentItem("text", text="10")]
        response = MockToolResponse(content)

        result = MCPValidator.validate_tool_response(response, expected_result="8")

        assert result["valid"] is True
        assert result["matches_expected"] is False
        assert any("does not match expected" in w for w in result["warnings"])

    def test_validate_resource_response_success(self):
        """Test validating a successful resource response."""
        content = [MockResourceContent("text/plain", text="file content")]
        response = MockResourceResponse(content)

        result = MCPValidator.validate_resource_response(response)

        assert result["valid"] is True
        assert result["content_type"] == "text/plain"
        assert len(result["errors"]) == 0

    def test_validate_resource_response_none(self):
        """Test validating a None resource response."""
        result = MCPValidator.validate_resource_response(None)

        assert result["valid"] is False
        assert "Resource response is None" in result["errors"]

    def test_validate_resource_response_with_expected_type(self):
        """Test validating a resource response with expected content type."""
        content = [MockResourceContent("text/plain")]
        response = MockResourceResponse(content)

        result = MCPValidator.validate_resource_response(response, expected_content_type="text/plain")

        assert result["valid"] is True
        assert result["content_type"] == "text/plain"
        assert len(result["warnings"]) == 0

    def test_validate_resource_response_type_mismatch(self):
        """Test validating a resource response with mismatched content type."""
        content = [MockResourceContent("application/json")]
        response = MockResourceResponse(content)

        result = MCPValidator.validate_resource_response(response, expected_content_type="text/plain")

        assert result["valid"] is True
        assert result["content_type"] == "application/json"
        assert any("Content type mismatch" in w for w in result["warnings"])

    def test_validate_prompt_response_success(self):
        """Test validating a successful prompt response."""
        response = MockPromptResponse([{"role": "user", "content": "test"}])

        result = MCPValidator.validate_prompt_response(response)

        assert result["valid"] is True
        assert result["has_messages"] is True
        assert len(result["errors"]) == 0

    def test_validate_prompt_response_none(self):
        """Test validating a None prompt response."""
        result = MCPValidator.validate_prompt_response(None)

        assert result["valid"] is False
        assert "Prompt response is None" in result["errors"]

    def test_validate_prompt_response_empty_messages(self):
        """Test validating a prompt response with empty messages."""
        response = MockPromptResponse([])

        result = MCPValidator.validate_prompt_response(response)

        assert result["valid"] is True
        assert "Prompt messages is empty" in result["warnings"]

    def test_validate_server_info_success(self):
        """Test validating successful server info."""
        info = {
            "server_name": "test-server",
            "server_version": "1.0.0",
            "capabilities": {"tools": True, "resources": True},
        }

        result = MCPValidator.validate_server_info(info)

        assert result["valid"] is True
        assert result["has_capabilities"] is True
        assert len(result["errors"]) == 0

    def test_validate_server_info_missing_fields(self):
        """Test validating server info with missing fields."""
        info = {"server_name": "test-server"}

        result = MCPValidator.validate_server_info(info)

        assert result["valid"] is True
        assert any("missing 'server_version'" in w for w in result["warnings"])
        assert any("missing 'capabilities'" in w for w in result["warnings"])

    def test_validate_server_info_not_dict(self):
        """Test validating server info that is not a dictionary."""
        result = MCPValidator.validate_server_info("not a dict")

        assert result["valid"] is False
        assert "Server info is not a dictionary" in result["errors"][0]

    def test_validate_tool_list_success(self):
        """Test validating a successful tool list."""
        tools = [
            MockTool("add", "Add two numbers"),
            MockTool("subtract", "Subtract two numbers"),
        ]

        result = MCPValidator.validate_tool_list(tools)

        assert result["valid"] is True
        assert result["tool_count"] == 2
        assert "add" in result["tool_names"]
        assert "subtract" in result["tool_names"]

    def test_validate_tool_list_empty(self):
        """Test validating an empty tool list."""
        result = MCPValidator.validate_tool_list([])

        assert result["valid"] is True
        assert result["tool_count"] == 0
        assert "Tool list is empty" in result["warnings"]

    def test_validate_tool_list_not_list(self):
        """Test validating tool list that is not a list."""
        result = MCPValidator.validate_tool_list("not a list")

        assert result["valid"] is False
        assert "Tools is not a list" in result["errors"][0]

    def test_validate_tool_list_missing_name(self):
        """Test validating tool list with tool missing name."""
        tools = [MockTool("valid"), object()]  # Second object has no 'name' attribute

        result = MCPValidator.validate_tool_list(tools)

        assert result["valid"] is False
        assert any("missing 'name' attribute" in e for e in result["errors"])

    def test_compare_values_equal(self):
        """Test comparing equal values."""
        assert MCPValidator._compare_values("test", "test") is True
        assert MCPValidator._compare_values(42, 42) is True
        assert MCPValidator._compare_values(3.14, 3.14) is True

    def test_compare_values_string_coercion(self):
        """Test comparing values with string coercion."""
        assert MCPValidator._compare_values(42, "42") is True
        assert MCPValidator._compare_values("42", 42) is True

    def test_compare_values_numeric_coercion(self):
        """Test comparing values with numeric coercion."""
        assert MCPValidator._compare_values("3.14", 3.14) is True
        assert MCPValidator._compare_values(3.0, 3) is True

    def test_compare_values_not_equal(self):
        """Test comparing unequal values."""
        assert MCPValidator._compare_values("test", "different") is False
        assert MCPValidator._compare_values(42, 99) is False


class TestValidateResponseFunction:
    """Test cases for validate_response convenience function."""

    def test_validate_response_tool(self):
        """Test validate_response with tool type."""
        content = [MockContentItem("text", text="result")]
        response = MockToolResponse(content)

        result = validate_response("tool", response)

        assert result["valid"] is True

    def test_validate_response_resource(self):
        """Test validate_response with resource type."""
        content = [MockResourceContent("text/plain")]
        response = MockResourceResponse(content)

        result = validate_response("resource", response)

        assert result["valid"] is True

    def test_validate_response_prompt(self):
        """Test validate_response with prompt type."""
        response = MockPromptResponse([])

        result = validate_response("prompt", response)

        assert result["valid"] is True

    def test_validate_response_server_info(self):
        """Test validate_response with server_info type."""
        info = {"server_name": "test"}

        result = validate_response("server_info", info)

        assert result["valid"] is True

    def test_validate_response_tool_list(self):
        """Test validate_response with tool_list type."""
        tools = [MockTool("test")]

        result = validate_response("tool_list", tools)

        assert result["valid"] is True

    def test_validate_response_invalid_type(self):
        """Test validate_response with invalid type."""
        with pytest.raises(ValueError) as exc_info:
            validate_response("invalid_type", None)

        assert "Invalid response_type" in str(exc_info.value)
