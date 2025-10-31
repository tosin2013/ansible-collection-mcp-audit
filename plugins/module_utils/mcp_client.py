# Copyright: (c) 2024, Tosin Akinosho <tosin.akinosho@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later OR BSD-2-Clause

"""
MCP Client Utility

This module_utils can be used under either:
- GPL-3.0-or-later (for use in GPL collections)
- BSD-2-Clause (for use in permissively licensed collections)

Provides a unified interface for communicating with MCP servers
across different transport protocols (stdio, SSE, HTTP).
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from contextlib import asynccontextmanager
from typing import Any, ClassVar

try:
    from mcp import ClientSession
    from mcp.client.sse import sse_client
    from mcp.client.stdio import StdioServerParameters, stdio_client
    from mcp.types import Prompt, Resource, Tool

    HAS_MCP = True
    MCP_IMPORT_ERROR = None
except ImportError as e:
    HAS_MCP = False
    MCP_IMPORT_ERROR = str(e)
    # Define stub types for type checking when MCP is not available
    ClientSession = Any  # type: ignore
    Tool = Any  # type: ignore
    Resource = Any  # type: ignore
    Prompt = Any  # type: ignore


class MCPClientError(Exception):
    """Base exception for MCP client errors."""

    pass


class MCPTransportError(MCPClientError):
    """Exception raised for transport-specific errors."""

    pass


class MCPConnectionError(MCPClientError):
    """Exception raised when connection to MCP server fails."""

    pass


class MCPClient:
    """
    Unified MCP client that supports multiple transport protocols.

    This class provides a consistent interface for interacting with MCP servers
    regardless of the underlying transport mechanism (stdio, SSE, or HTTP).

    Attributes:
        transport: The transport protocol to use ('stdio', 'sse', or 'http')
        session: The MCP client session (available after connection)
    """

    SUPPORTED_TRANSPORTS: ClassVar[list[str]] = ["stdio", "sse", "http"]

    def __init__(
        self,
        transport: str = "stdio",
        server_command: str | None = None,
        server_args: list[str] | None = None,
        server_url: str | None = None,
        server_headers: dict[str, str] | None = None,
        timeout: int = 30,
    ) -> None:
        """
        Initialize the MCP client.

        Args:
            transport: Transport protocol ('stdio', 'sse', or 'http')
            server_command: Command to start MCP server (required for stdio)
            server_args: Arguments for server command (optional for stdio)
            server_url: URL of MCP server (required for sse/http)
            server_headers: HTTP headers for authentication (optional for sse/http)
            timeout: Connection timeout in seconds (default: 30)

        Raises:
            MCPClientError: If MCP SDK is not available or invalid parameters
        """
        if not HAS_MCP:
            raise MCPClientError(f"MCP Python SDK is required but not available: {MCP_IMPORT_ERROR}")

        if transport not in self.SUPPORTED_TRANSPORTS:
            raise MCPClientError(
                f"Unsupported transport '{transport}'. Supported: {', '.join(self.SUPPORTED_TRANSPORTS)}"
            )

        self.transport = transport
        self.timeout = timeout
        self.session: ClientSession | None = None
        self._read_stream = None
        self._write_stream = None

        # Validate transport-specific parameters
        if transport == "stdio":
            if not server_command:
                raise MCPClientError("server_command is required for stdio transport")
            self.server_command = server_command
            self.server_args = server_args or []
        elif transport in ("sse", "http"):
            if not server_url:
                raise MCPClientError(f"server_url is required for {transport} transport")
            self.server_url = server_url
            self.server_headers = server_headers or {}

    @asynccontextmanager
    async def connect(self):
        """
        Establish connection to the MCP server as an async context manager.

        Yields:
            MCPClient: Connected client instance

        Raises:
            MCPConnectionError: If connection fails
            MCPTransportError: If transport-specific error occurs

        Example:
            async with client.connect() as connected_client:
                tools = await connected_client.list_tools()
        """
        try:
            if self.transport == "stdio":
                server_params = StdioServerParameters(
                    command=self.server_command,
                    args=self.server_args,
                )
                async with stdio_client(server_params) as (read, write):
                    self._read_stream = read
                    self._write_stream = write
                    async with ClientSession(read, write) as session:
                        self.session = session
                        await session.initialize()
                        yield self
            elif self.transport == "sse":
                async with sse_client(self.server_url, self.server_headers) as (
                    read,
                    write,
                ):
                    self._read_stream = read
                    self._write_stream = write
                    async with ClientSession(read, write) as session:
                        self.session = session
                        await session.initialize()
                        yield self
            elif self.transport == "http":
                # HTTP transport using streamable HTTP client
                # Note: Implementation may vary based on MCP SDK version
                raise MCPTransportError("HTTP transport implementation pending - use stdio or sse for now")
        except Exception as e:
            raise MCPConnectionError(f"Failed to connect to MCP server via {self.transport}: {e!s}") from e
        finally:
            self.session = None
            self._read_stream = None
            self._write_stream = None

    async def list_tools(self) -> list[Tool]:
        """
        List all tools available on the MCP server.

        Returns:
            List of Tool objects

        Raises:
            MCPClientError: If not connected or operation fails
        """
        if not self.session:
            raise MCPClientError("Not connected to MCP server")

        try:
            response = await self.session.list_tools()
            return response.tools
        except Exception as e:
            raise MCPClientError(f"Failed to list tools: {e!s}") from e

    async def call_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> Any:
        """
        Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments as a dictionary

        Returns:
            Tool execution result

        Raises:
            MCPClientError: If not connected or tool call fails
        """
        if not self.session:
            raise MCPClientError("Not connected to MCP server")

        try:
            response = await self.session.call_tool(tool_name, arguments or {})
            return response
        except Exception as e:
            raise MCPClientError(f"Failed to call tool '{tool_name}': {e!s}") from e

    async def list_resources(self) -> list[Resource]:
        """
        List all resources available on the MCP server.

        Returns:
            List of Resource objects

        Raises:
            MCPClientError: If not connected or operation fails
        """
        if not self.session:
            raise MCPClientError("Not connected to MCP server")

        try:
            response = await self.session.list_resources()
            return response.resources
        except Exception as e:
            raise MCPClientError(f"Failed to list resources: {e!s}") from e

    async def read_resource(self, uri: str) -> Any:
        """
        Read a resource from the MCP server.

        Args:
            uri: Resource URI to read

        Returns:
            Resource content

        Raises:
            MCPClientError: If not connected or resource read fails
        """
        if not self.session:
            raise MCPClientError("Not connected to MCP server")

        try:
            response = await self.session.read_resource(uri)
            return response
        except Exception as e:
            raise MCPClientError(f"Failed to read resource '{uri}': {e!s}") from e

    async def list_prompts(self) -> list[Prompt]:
        """
        List all prompts available on the MCP server.

        Returns:
            List of Prompt objects

        Raises:
            MCPClientError: If not connected or operation fails
        """
        if not self.session:
            raise MCPClientError("Not connected to MCP server")

        try:
            response = await self.session.list_prompts()
            return response.prompts
        except Exception as e:
            raise MCPClientError(f"Failed to list prompts: {e!s}") from e

    async def get_prompt(self, prompt_name: str, arguments: dict[str, str] | None = None) -> Any:
        """
        Get a prompt from the MCP server.

        Args:
            prompt_name: Name of the prompt to get
            arguments: Prompt arguments as a dictionary

        Returns:
            Prompt result

        Raises:
            MCPClientError: If not connected or prompt retrieval fails
        """
        if not self.session:
            raise MCPClientError("Not connected to MCP server")

        try:
            response = await self.session.get_prompt(prompt_name, arguments or {})
            return response
        except Exception as e:
            raise MCPClientError(f"Failed to get prompt '{prompt_name}': {e!s}") from e

    async def get_server_info(self) -> dict[str, Any]:
        """
        Get server information and capabilities.

        Returns:
            Dictionary containing server information

        Raises:
            MCPClientError: If not connected
        """
        if not self.session:
            raise MCPClientError("Not connected to MCP server")

        try:
            # Server info is available after initialization
            return {
                "server_name": getattr(self.session, "server_name", "unknown"),
                "server_version": getattr(self.session, "server_version", "unknown"),
                "capabilities": getattr(self.session, "capabilities", {}),
            }
        except Exception as e:
            raise MCPClientError(f"Failed to get server info: {e!s}") from e


def create_mcp_client(module_params: dict[str, Any]) -> MCPClient:
    """
    Factory function to create an MCP client from Ansible module parameters.

    Args:
        module_params: Dictionary of module parameters

    Returns:
        Configured MCPClient instance

    Raises:
        MCPClientError: If parameters are invalid

    Example:
        client = create_mcp_client(module.params)
        async with client.connect():
            tools = await client.list_tools()
    """
    transport = module_params.get("transport", "stdio")

    client_kwargs = {
        "transport": transport,
        "timeout": module_params.get("timeout", 30),
    }

    if transport == "stdio":
        client_kwargs["server_command"] = module_params.get("server_command")
        client_kwargs["server_args"] = module_params.get("server_args", [])
    elif transport in ("sse", "http"):
        client_kwargs["server_url"] = module_params.get("server_url")
        client_kwargs["server_headers"] = module_params.get("server_headers", {})

    return MCPClient(**client_kwargs)
