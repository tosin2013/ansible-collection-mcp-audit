# Copyright: (c) 2024, Tosin Akinosho <tosin.akinosho@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type
"""Unit tests for mcp_test_resource, mcp_test_prompt, and mcp_test_suite modules."""

from unittest.mock import MagicMock, patch

import pytest
from ansible_collections.mcp.audit.plugins.modules import (
    mcp_test_prompt,
    mcp_test_resource,
    mcp_test_suite,
)


class TestMCPTestResource:
    """Test cases for mcp_test_resource module."""

    @pytest.fixture
    def mock_module(self):
        """Create a mock AnsibleModule."""
        module = MagicMock()
        module.params = {
            "resource_uri": "file:///test.txt",
            "expected_content_type": None,
            "transport": "stdio",
            "server_command": "python",
            "server_args": [],
            "server_url": None,
            "server_headers": {},
            "timeout": 30,
        }
        return module

    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_resource.create_mcp_client")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_resource.asyncio.run")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_resource.AnsibleModule")
    def test_successful_resource_test(self, mock_ansible_module, mock_asyncio_run, mock_create_client, mock_module):
        """Test successful resource test."""
        mock_ansible_module.return_value = mock_module
        mock_create_client.return_value = MagicMock()
        mock_asyncio_run.return_value = {
            "resource_content": MagicMock(),
            "validation": {"valid": True, "errors": [], "warnings": []},
        }

        mcp_test_resource.run_module()

        assert mock_module.exit_json.called
        call_args = mock_module.exit_json.call_args[1]
        assert call_args["success"] is True
        assert call_args["test_passed"] is True

    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_resource.create_mcp_client")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_resource.asyncio.run")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_resource.AnsibleModule")
    def test_resource_connection_error(self, mock_ansible_module, mock_asyncio_run, mock_create_client, mock_module):
        """Test resource connection error."""
        from ansible_collections.mcp.audit.plugins.module_utils.mcp_client import MCPConnectionError

        mock_ansible_module.return_value = mock_module
        mock_create_client.return_value = MagicMock()
        mock_asyncio_run.side_effect = MCPConnectionError("Connection failed")

        mcp_test_resource.run_module()

        assert mock_module.fail_json.called
        assert mock_module.fail_json.call_args[1]["test_passed"] is False

    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_resource.create_mcp_client")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_resource.asyncio.run")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_resource.AnsibleModule")
    def test_resource_client_error(self, mock_ansible_module, mock_asyncio_run, mock_create_client, mock_module):
        """Test resource client error."""
        from ansible_collections.mcp.audit.plugins.module_utils.mcp_client import MCPClientError

        mock_ansible_module.return_value = mock_module
        mock_create_client.return_value = MagicMock()
        mock_asyncio_run.side_effect = MCPClientError("Resource not found")

        mcp_test_resource.run_module()

        assert mock_module.fail_json.called
        assert mock_module.fail_json.call_args[1]["test_passed"] is False


class TestMCPTestPrompt:
    """Test cases for mcp_test_prompt module."""

    @pytest.fixture
    def mock_module(self):
        """Create a mock AnsibleModule."""
        module = MagicMock()
        module.params = {
            "prompt_name": "greeting",
            "prompt_arguments": {},
            "transport": "stdio",
            "server_command": "python",
            "server_args": [],
            "server_url": None,
            "server_headers": {},
            "timeout": 30,
        }
        return module

    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_prompt.create_mcp_client")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_prompt.asyncio.run")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_prompt.AnsibleModule")
    def test_successful_prompt_test(self, mock_ansible_module, mock_asyncio_run, mock_create_client, mock_module):
        """Test successful prompt test."""
        mock_ansible_module.return_value = mock_module
        mock_create_client.return_value = MagicMock()
        mock_asyncio_run.return_value = {
            "prompt_result": MagicMock(),
            "validation": {"valid": True, "has_messages": True, "errors": [], "warnings": []},
        }

        mcp_test_prompt.run_module()

        assert mock_module.exit_json.called
        call_args = mock_module.exit_json.call_args[1]
        assert call_args["success"] is True
        assert call_args["test_passed"] is True

    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_prompt.create_mcp_client")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_prompt.asyncio.run")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_prompt.AnsibleModule")
    def test_prompt_connection_error(self, mock_ansible_module, mock_asyncio_run, mock_create_client, mock_module):
        """Test prompt connection error."""
        from ansible_collections.mcp.audit.plugins.module_utils.mcp_client import MCPConnectionError

        mock_ansible_module.return_value = mock_module
        mock_create_client.return_value = MagicMock()
        mock_asyncio_run.side_effect = MCPConnectionError("Connection failed")

        mcp_test_prompt.run_module()

        assert mock_module.fail_json.called
        assert mock_module.fail_json.call_args[1]["test_passed"] is False

    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_prompt.create_mcp_client")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_prompt.asyncio.run")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_prompt.AnsibleModule")
    def test_prompt_client_error(self, mock_ansible_module, mock_asyncio_run, mock_create_client, mock_module):
        """Test prompt client error."""
        from ansible_collections.mcp.audit.plugins.module_utils.mcp_client import MCPClientError

        mock_ansible_module.return_value = mock_module
        mock_create_client.return_value = MagicMock()
        mock_asyncio_run.side_effect = MCPClientError("Prompt not found")

        mcp_test_prompt.run_module()

        assert mock_module.fail_json.called
        assert mock_module.fail_json.call_args[1]["test_passed"] is False


class TestMCPTestSuite:
    """Test cases for mcp_test_suite module."""

    @pytest.fixture
    def mock_module(self):
        """Create a mock AnsibleModule."""
        module = MagicMock()
        module.params = {
            "tests": [{"type": "tool", "name": "add", "arguments": {"a": 1, "b": 2}}],
            "fail_on_error": False,
            "transport": "stdio",
            "server_command": "python",
            "server_args": [],
            "server_url": None,
            "server_headers": {},
            "timeout": 30,
        }
        return module

    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_suite.create_mcp_client")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_suite.asyncio.run")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_suite.AnsibleModule")
    def test_successful_suite(self, mock_ansible_module, mock_asyncio_run, mock_create_client, mock_module):
        """Test successful test suite."""
        mock_ansible_module.return_value = mock_module
        mock_create_client.return_value = MagicMock()
        mock_asyncio_run.return_value = {
            "test_results": [{"test_type": "tool", "test_name": "add", "passed": True, "error": None}],
            "summary": {"total_tests": 1, "passed": 1, "failed": 0, "success_rate": 100.0},
        }

        mcp_test_suite.run_module()

        assert mock_module.exit_json.called
        call_args = mock_module.exit_json.call_args[1]
        assert call_args["success"] is True
        assert call_args["summary"]["passed"] == 1

    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_suite.create_mcp_client")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_suite.asyncio.run")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_suite.AnsibleModule")
    def test_suite_fail_on_error(self, mock_ansible_module, mock_asyncio_run, mock_create_client, mock_module):
        """Test suite with fail_on_error enabled."""
        mock_module.params["fail_on_error"] = True
        mock_ansible_module.return_value = mock_module
        mock_create_client.return_value = MagicMock()
        mock_asyncio_run.return_value = {
            "test_results": [{"test_type": "tool", "test_name": "add", "passed": False, "error": "Failed"}],
            "summary": {"total_tests": 1, "passed": 0, "failed": 1, "success_rate": 0.0},
        }

        mcp_test_suite.run_module()

        assert mock_module.fail_json.called
        assert "tests failed" in mock_module.fail_json.call_args[1]["msg"]

    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_suite.AnsibleModule")
    def test_suite_empty_tests(self, mock_ansible_module, mock_module):
        """Test suite with empty tests list."""
        mock_module.params["tests"] = []
        mock_ansible_module.return_value = mock_module

        mcp_test_suite.run_module()

        assert mock_module.fail_json.called
        assert "cannot be empty" in mock_module.fail_json.call_args[1]["msg"]

    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_suite.create_mcp_client")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_suite.asyncio.run")
    @patch("ansible_collections.mcp.audit.plugins.modules.mcp_test_suite.AnsibleModule")
    def test_suite_connection_error(self, mock_ansible_module, mock_asyncio_run, mock_create_client, mock_module):
        """Test suite connection error."""
        from ansible_collections.mcp.audit.plugins.module_utils.mcp_client import MCPConnectionError

        mock_ansible_module.return_value = mock_module
        mock_create_client.return_value = MagicMock()
        mock_asyncio_run.side_effect = MCPConnectionError("Connection failed")

        mcp_test_suite.run_module()

        assert mock_module.fail_json.called
        assert "Failed to connect" in mock_module.fail_json.call_args[1]["msg"]
