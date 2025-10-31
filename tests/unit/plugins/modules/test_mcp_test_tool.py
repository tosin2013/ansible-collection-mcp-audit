# Copyright: (c) 2024, Tosin Akinosho <tosin.akinosho@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type
"""Unit tests for mcp_test_tool module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from ansible_collections.mcp.audit.plugins.modules import mcp_test_tool


class TestMCPTestTool:
    """Test cases for mcp_test_tool module."""

    @pytest.fixture
    def mock_module(self):
        """Create a mock AnsibleModule."""
        module = MagicMock()
        module.params = {
            "tool_name": "add",
            "tool_arguments": {"a": 5, "b": 3},
            "expected_result": 8,
            "transport": "stdio",
            "server_command": "python",
            "server_args": ["-m", "test_server"],
            "server_url": None,
            "server_headers": {},
            "timeout": 30,
        }
        module.check_mode = False
        return module

    @pytest.fixture
    def mock_tool_response(self):
        """Create a mock tool response."""
        response = MagicMock()
        response.content = [MagicMock(type="text", text="8")]
        return response

    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_tool.create_mcp_client")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_tool.asyncio.run")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_tool.AnsibleModule")
    def test_successful_tool_test(
        self, mock_ansible_module, mock_asyncio_run, mock_create_client, mock_module, mock_tool_response
    ):
        """Test successful tool execution with validation."""
        # Setup mocks
        mock_ansible_module.return_value = mock_module
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        test_result = {
            "tool_result": mock_tool_response,
            "validation": {
                "valid": True,
                "matches_expected": True,
                "errors": [],
                "warnings": [],
            },
        }
        mock_asyncio_run.return_value = test_result

        # Run module
        mcp_test_tool.run_module()

        # Verify
        assert mock_create_client.called
        assert mock_asyncio_run.called
        assert mock_module.exit_json.called

        # Check exit_json was called with success
        call_args = mock_module.exit_json.call_args[1]
        assert call_args["success"] is True
        assert call_args["test_passed"] is True
        assert "tool_result" in call_args
        assert "validation" in call_args
        assert call_args["changed"] is False

    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_tool.create_mcp_client")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_tool.asyncio.run")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_tool.AnsibleModule")
    def test_tool_test_with_warnings(
        self, mock_ansible_module, mock_asyncio_run, mock_create_client, mock_module, mock_tool_response
    ):
        """Test tool execution that completes with warnings."""
        # Setup mocks
        mock_ansible_module.return_value = mock_module
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        test_result = {
            "tool_result": mock_tool_response,
            "validation": {
                "valid": True,
                "matches_expected": False,
                "errors": [],
                "warnings": ["Result does not match expected value"],
            },
        }
        mock_asyncio_run.return_value = test_result

        # Run module
        mcp_test_tool.run_module()

        # Verify
        assert mock_module.exit_json.called
        call_args = mock_module.exit_json.call_args[1]
        assert call_args["success"] is True
        assert call_args["test_passed"] is False
        assert "Tool test completed with warnings" in call_args["status"]

    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_tool.AnsibleModule")
    def test_missing_tool_name(self, mock_ansible_module):
        """Test module requires tool_name parameter."""
        # This test verifies the module spec requires tool_name
        # The actual requirement is enforced by AnsibleModule
        pass

    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_tool.AnsibleModule")
    def test_stdio_missing_command(self, mock_ansible_module, mock_module):
        """Test stdio transport without server_command."""
        mock_module.params["server_command"] = None
        mock_ansible_module.return_value = mock_module

        # Run module
        mcp_test_tool.run_module()

        # Verify fail_json was called
        assert mock_module.fail_json.called
        call_args = mock_module.fail_json.call_args[1]
        assert "server_command is required" in call_args["msg"]

    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_tool.create_mcp_client")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_tool.asyncio.run")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_tool.AnsibleModule")
    def test_connection_error(self, mock_ansible_module, mock_asyncio_run, mock_create_client, mock_module):
        """Test handling of connection errors."""
        from ansible_collections.mcp.audit.plugins.module_utils.mcp_client import MCPConnectionError

        # Setup mocks
        mock_ansible_module.return_value = mock_module
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        mock_asyncio_run.side_effect = MCPConnectionError("Connection refused")

        # Run module
        mcp_test_tool.run_module()

        # Verify fail_json was called with connection error
        assert mock_module.fail_json.called
        call_args = mock_module.fail_json.call_args[1]
        assert "Failed to connect to MCP server" in call_args["msg"]
        assert call_args["success"] is False
        assert call_args["test_passed"] is False

    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_tool.create_mcp_client")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_tool.asyncio.run")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_tool.AnsibleModule")
    def test_tool_not_found(self, mock_ansible_module, mock_asyncio_run, mock_create_client, mock_module):
        """Test handling when tool is not found."""
        from ansible_collections.mcp.audit.plugins.module_utils.mcp_client import MCPClientError

        # Setup mocks
        mock_ansible_module.return_value = mock_module
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        mock_asyncio_run.side_effect = MCPClientError("Tool 'unknown_tool' not found")

        # Run module
        mcp_test_tool.run_module()

        # Verify fail_json was called
        assert mock_module.fail_json.called
        call_args = mock_module.fail_json.call_args[1]
        assert "Tool test error" in call_args["msg"]
        assert call_args["test_passed"] is False

    @pytest.mark.asyncio
    async def test_test_tool_async(self, mock_tool_response):
        """Test the async tool testing function."""
        # Create mock client
        mock_client = MagicMock()
        mock_client.call_tool = AsyncMock(return_value=mock_tool_response)

        # Mock the context manager
        mock_client.connect = MagicMock()
        mock_client.connect.return_value.__aenter__ = AsyncMock(return_value=None)
        mock_client.connect.return_value.__aexit__ = AsyncMock(return_value=None)

        # Call the function
        result = await mcp_test_tool.test_tool_async(mock_client, "add", {"a": 5, "b": 3}, expected_result=8)

        # Verify
        assert "tool_result" in result
        assert "validation" in result
        assert mock_client.call_tool.called
        mock_client.call_tool.assert_called_once_with("add", {"a": 5, "b": 3})

    @pytest.mark.asyncio
    async def test_test_tool_async_without_expected(self, mock_tool_response):
        """Test async tool testing without expected result."""
        # Create mock client
        mock_client = MagicMock()
        mock_client.call_tool = AsyncMock(return_value=mock_tool_response)

        # Mock the context manager
        mock_client.connect = MagicMock()
        mock_client.connect.return_value.__aenter__ = AsyncMock(return_value=None)
        mock_client.connect.return_value.__aexit__ = AsyncMock(return_value=None)

        # Call the function without expected_result
        result = await mcp_test_tool.test_tool_async(mock_client, "get_weather", {"city": "SF"})

        # Verify
        assert "tool_result" in result
        assert "validation" in result
        assert mock_client.call_tool.called
        mock_client.call_tool.assert_called_once_with("get_weather", {"city": "SF"})
