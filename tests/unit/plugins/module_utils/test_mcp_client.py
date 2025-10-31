# Copyright: (c) 2024, Tosin Akinosho <tosin.akinosho@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type
"""Unit tests for mcp_client module_utils."""

import pytest
from ansible_collections.mcp.audit.plugins.module_utils.mcp_client import (
    MCPClient,
    MCPClientError,
    MCPConnectionError,
    MCPTransportError,
    create_mcp_client,
)


class TestMCPClientInitialization:
    """Test cases for MCPClient initialization."""

    def test_init_stdio_transport(self):
        """Test initializing client with stdio transport."""
        client = MCPClient(
            transport="stdio",
            server_command="python",
            server_args=["server.py"],
        )

        assert client.transport == "stdio"
        assert client.server_command == "python"
        assert client.server_args == ["server.py"]
        assert client.timeout == 30

    def test_init_sse_transport(self):
        """Test initializing client with SSE transport."""
        client = MCPClient(
            transport="sse",
            server_url="http://localhost:8000",
            server_headers={"Authorization": "Bearer token"},
        )

        assert client.transport == "sse"
        assert client.server_url == "http://localhost:8000"
        assert client.server_headers == {"Authorization": "Bearer token"}

    def test_init_http_transport(self):
        """Test initializing client with HTTP transport."""
        client = MCPClient(
            transport="http",
            server_url="http://localhost:8000",
        )

        assert client.transport == "http"
        assert client.server_url == "http://localhost:8000"

    def test_init_invalid_transport(self):
        """Test initializing client with invalid transport."""
        with pytest.raises(MCPClientError) as exc_info:
            MCPClient(transport="invalid")

        assert "Unsupported transport 'invalid'" in str(exc_info.value)

    def test_init_stdio_missing_command(self):
        """Test initializing stdio client without server command."""
        with pytest.raises(MCPClientError) as exc_info:
            MCPClient(transport="stdio")

        assert "server_command is required" in str(exc_info.value)

    def test_init_sse_missing_url(self):
        """Test initializing SSE client without server URL."""
        with pytest.raises(MCPClientError) as exc_info:
            MCPClient(transport="sse")

        assert "server_url is required" in str(exc_info.value)

    def test_init_http_missing_url(self):
        """Test initializing HTTP client without server URL."""
        with pytest.raises(MCPClientError) as exc_info:
            MCPClient(transport="http")

        assert "server_url is required" in str(exc_info.value)

    def test_init_default_args(self):
        """Test initializing client with default arguments."""
        client = MCPClient(
            transport="stdio",
            server_command="python",
        )

        assert client.server_args == []
        assert client.timeout == 30

    def test_init_custom_timeout(self):
        """Test initializing client with custom timeout."""
        client = MCPClient(
            transport="stdio",
            server_command="python",
            timeout=60,
        )

        assert client.timeout == 60


class TestMCPClientMethods:
    """Test cases for MCPClient methods."""

    @pytest.mark.asyncio
    async def test_list_tools_not_connected(self):
        """Test listing tools when not connected."""
        client = MCPClient(transport="stdio", server_command="python")

        with pytest.raises(MCPClientError) as exc_info:
            await client.list_tools()

        assert "Not connected to MCP server" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_call_tool_not_connected(self):
        """Test calling tool when not connected."""
        client = MCPClient(transport="stdio", server_command="python")

        with pytest.raises(MCPClientError) as exc_info:
            await client.call_tool("test_tool")

        assert "Not connected to MCP server" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_list_resources_not_connected(self):
        """Test listing resources when not connected."""
        client = MCPClient(transport="stdio", server_command="python")

        with pytest.raises(MCPClientError) as exc_info:
            await client.list_resources()

        assert "Not connected to MCP server" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_read_resource_not_connected(self):
        """Test reading resource when not connected."""
        client = MCPClient(transport="stdio", server_command="python")

        with pytest.raises(MCPClientError) as exc_info:
            await client.read_resource("test://resource")

        assert "Not connected to MCP server" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_list_prompts_not_connected(self):
        """Test listing prompts when not connected."""
        client = MCPClient(transport="stdio", server_command="python")

        with pytest.raises(MCPClientError) as exc_info:
            await client.list_prompts()

        assert "Not connected to MCP server" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_prompt_not_connected(self):
        """Test getting prompt when not connected."""
        client = MCPClient(transport="stdio", server_command="python")

        with pytest.raises(MCPClientError) as exc_info:
            await client.get_prompt("test_prompt")

        assert "Not connected to MCP server" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_server_info_not_connected(self):
        """Test getting server info when not connected."""
        client = MCPClient(transport="stdio", server_command="python")

        with pytest.raises(MCPClientError) as exc_info:
            await client.get_server_info()

        assert "Not connected to MCP server" in str(exc_info.value)


class TestCreateMCPClient:
    """Test cases for create_mcp_client factory function."""

    def test_create_stdio_client(self):
        """Test creating stdio client from module params."""
        module_params = {
            "transport": "stdio",
            "server_command": "python",
            "server_args": ["server.py"],
            "timeout": 45,
        }

        client = create_mcp_client(module_params)

        assert isinstance(client, MCPClient)
        assert client.transport == "stdio"
        assert client.server_command == "python"
        assert client.server_args == ["server.py"]
        assert client.timeout == 45

    def test_create_sse_client(self):
        """Test creating SSE client from module params."""
        module_params = {
            "transport": "sse",
            "server_url": "http://localhost:8000",
            "server_headers": {"Authorization": "Bearer token"},
        }

        client = create_mcp_client(module_params)

        assert isinstance(client, MCPClient)
        assert client.transport == "sse"
        assert client.server_url == "http://localhost:8000"
        assert client.server_headers == {"Authorization": "Bearer token"}

    def test_create_client_default_transport(self):
        """Test creating client with default transport."""
        module_params = {
            "server_command": "python",
        }

        client = create_mcp_client(module_params)

        assert client.transport == "stdio"

    def test_create_client_default_timeout(self):
        """Test creating client with default timeout."""
        module_params = {
            "transport": "stdio",
            "server_command": "python",
        }

        client = create_mcp_client(module_params)

        assert client.timeout == 30

    def test_create_client_missing_server_args(self):
        """Test creating client without server_args defaults to empty list."""
        module_params = {
            "transport": "stdio",
            "server_command": "python",
        }

        client = create_mcp_client(module_params)

        assert client.server_args == []

    def test_create_client_missing_server_headers(self):
        """Test creating client without server_headers defaults to empty dict."""
        module_params = {
            "transport": "sse",
            "server_url": "http://localhost:8000",
        }

        client = create_mcp_client(module_params)

        assert client.server_headers == {}


class TestMCPClientExceptions:
    """Test cases for MCPClient exception classes."""

    def test_mcp_client_error(self):
        """Test MCPClientError exception."""
        error = MCPClientError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_mcp_transport_error(self):
        """Test MCPTransportError exception."""
        error = MCPTransportError("Transport error")
        assert str(error) == "Transport error"
        assert isinstance(error, MCPClientError)

    def test_mcp_connection_error(self):
        """Test MCPConnectionError exception."""
        error = MCPConnectionError("Connection error")
        assert str(error) == "Connection error"
        assert isinstance(error, MCPClientError)
