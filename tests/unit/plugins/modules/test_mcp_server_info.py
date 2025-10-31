# Copyright: (c) 2024, Tosin Akinosho <tosin.akinosho@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type
"""Unit tests for mcp_server_info module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from ansible_collections.mcp.audit.plugins.modules import mcp_server_info


class TestMCPServerInfo:
    """Test cases for mcp_server_info module."""

    @pytest.fixture
    def mock_module(self):
        """Create a mock AnsibleModule."""
        module = MagicMock()
        module.params = {
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
    def mock_server_info(self):
        """Create mock server information."""
        return {
            "server_name": "test-server",
            "server_version": "1.0.0",
            "protocol_version": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {},
                "prompts": {},
            },
        }

    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_server_info.create_mcp_client")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_server_info.asyncio.run")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_server_info.AnsibleModule")
    def test_successful_server_info_retrieval(
        self, mock_ansible_module, mock_asyncio_run, mock_create_client, mock_module, mock_server_info
    ):
        """Test successful server information retrieval."""
        # Setup mocks
        mock_ansible_module.return_value = mock_module
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        mock_asyncio_run.return_value = mock_server_info

        # Run module
        mcp_server_info.run_module()

        # Verify
        assert mock_create_client.called
        assert mock_asyncio_run.called
        assert mock_module.exit_json.called

        # Check exit_json was called with success
        call_args = mock_module.exit_json.call_args[1]
        assert call_args["success"] is True
        assert "server_info" in call_args
        assert call_args["server_info"]["server_name"] == "test-server"
        assert call_args["changed"] is False

    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_server_info.AnsibleModule")
    def test_stdio_missing_command(self, mock_ansible_module, mock_module):
        """Test stdio transport without server_command."""
        mock_module.params["server_command"] = None
        mock_ansible_module.return_value = mock_module

        # Run module
        mcp_server_info.run_module()

        # Verify fail_json was called
        assert mock_module.fail_json.called
        call_args = mock_module.fail_json.call_args[1]
        assert "server_command is required" in call_args["msg"]

    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_server_info.AnsibleModule")
    def test_sse_missing_url(self, mock_ansible_module, mock_module):
        """Test SSE transport without server_url."""
        mock_module.params["transport"] = "sse"
        mock_module.params["server_command"] = None
        mock_module.params["server_url"] = None
        mock_ansible_module.return_value = mock_module

        # Run module
        mcp_server_info.run_module()

        # Verify fail_json was called
        assert mock_module.fail_json.called
        call_args = mock_module.fail_json.call_args[1]
        assert "server_url is required" in call_args["msg"]

    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_server_info.create_mcp_client")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_server_info.asyncio.run")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_server_info.AnsibleModule")
    def test_connection_error(self, mock_ansible_module, mock_asyncio_run, mock_create_client, mock_module):
        """Test handling of connection errors."""
        from ansible_collections.mcp.audit.plugins.module_utils.mcp_client import MCPConnectionError

        # Setup mocks
        mock_ansible_module.return_value = mock_module
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        mock_asyncio_run.side_effect = MCPConnectionError("Connection refused")

        # Run module
        mcp_server_info.run_module()

        # Verify fail_json was called with connection error
        assert mock_module.fail_json.called
        call_args = mock_module.fail_json.call_args[1]
        assert "Failed to connect to MCP server" in call_args["msg"]
        assert call_args["success"] is False

    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_server_info.create_mcp_client")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_server_info.asyncio.run")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_server_info.AnsibleModule")
    def test_client_error(self, mock_ansible_module, mock_asyncio_run, mock_create_client, mock_module):
        """Test handling of MCP client errors."""
        from ansible_collections.mcp.audit.plugins.module_utils.mcp_client import MCPClientError

        # Setup mocks
        mock_ansible_module.return_value = mock_module
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        mock_asyncio_run.side_effect = MCPClientError("Invalid response")

        # Run module
        mcp_server_info.run_module()

        # Verify fail_json was called with client error
        assert mock_module.fail_json.called
        call_args = mock_module.fail_json.call_args[1]
        assert "MCP client error" in call_args["msg"]
        assert call_args["success"] is False

    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_server_info.create_mcp_client")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_server_info.asyncio.run")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_server_info.AnsibleModule")
    def test_unexpected_error(self, mock_ansible_module, mock_asyncio_run, mock_create_client, mock_module):
        """Test handling of unexpected errors."""
        # Setup mocks
        mock_ansible_module.return_value = mock_module
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        mock_asyncio_run.side_effect = RuntimeError("Unexpected error")

        # Run module
        mcp_server_info.run_module()

        # Verify fail_json was called with unexpected error
        assert mock_module.fail_json.called
        call_args = mock_module.fail_json.call_args[1]
        assert "Unexpected error" in call_args["msg"]
        assert call_args["success"] is False

    @pytest.mark.asyncio
    async def test_get_server_info_async(self, mock_server_info):
        """Test the async server info retrieval function."""
        # Create mock client
        mock_client = MagicMock()
        mock_client.get_server_info = AsyncMock(return_value=mock_server_info.copy())
        mock_client.list_tools = AsyncMock(return_value=[MagicMock(), MagicMock()])
        mock_client.list_resources = AsyncMock(return_value=[MagicMock()])
        mock_client.list_prompts = AsyncMock(return_value=[])

        # Mock the context manager
        mock_client.connect = MagicMock()
        mock_client.connect.return_value.__aenter__ = AsyncMock(return_value=None)
        mock_client.connect.return_value.__aexit__ = AsyncMock(return_value=None)

        # Call the function
        result = await mcp_server_info.get_server_info_async(mock_client)

        # Verify
        assert result["server_name"] == "test-server"
        assert result["available_tools"] == 2
        assert result["available_resources"] == 1
        assert result["available_prompts"] == 0

    @pytest.mark.asyncio
    async def test_get_server_info_async_with_capability_errors(self, mock_server_info):
        """Test async server info when capability queries fail."""
        # Create mock client that fails on capability queries
        mock_client = MagicMock()
        mock_client.get_server_info = AsyncMock(return_value=mock_server_info.copy())
        mock_client.list_tools = AsyncMock(side_effect=Exception("Not supported"))
        mock_client.list_resources = AsyncMock(side_effect=Exception("Not supported"))
        mock_client.list_prompts = AsyncMock(side_effect=Exception("Not supported"))

        # Mock the context manager
        mock_client.connect = MagicMock()
        mock_client.connect.return_value.__aenter__ = AsyncMock(return_value=None)
        mock_client.connect.return_value.__aexit__ = AsyncMock(return_value=None)

        # Call the function
        result = await mcp_server_info.get_server_info_async(mock_client)

        # Verify - should have None for unavailable capabilities
        assert result["server_name"] == "test-server"
        assert result["available_tools"] is None
        assert result["available_resources"] is None
        assert result["available_prompts"] is None
