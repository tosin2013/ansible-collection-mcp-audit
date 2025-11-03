#!/usr/bin/python

# Copyright: (c) 2024, Tosin Akinosho <tosin.akinosho@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: mcp_server_info
short_description: Get information about an MCP server
version_added: "1.0.0"
description:
  - Connects to a Model Context Protocol (MCP) server and retrieves server information.
  - Returns server name, version, capabilities, and protocol information.
  - Supports stdio, SSE, and HTTP transport protocols.
  - Useful for verifying server availability and discovering capabilities.
author:
  - Tosin Akinosho (@tosinakinosho)
options:
  transport:
    description:
      - Transport protocol to use for connecting to the MCP server.
    type: str
    choices: ['stdio', 'sse', 'http']
    default: 'stdio'
  server_command:
    description:
      - Command to execute for stdio transport.
      - Required when I(transport=stdio).
    type: str
  server_args:
    description:
      - Arguments to pass to the server command.
      - Only applicable for stdio transport.
    type: list
    elements: str
    default: []
  server_url:
    description:
      - URL of the MCP server.
      - Required when I(transport=sse) or I(transport=http).
    type: str
  server_headers:
    description:
      - HTTP headers to send with the request.
      - Only applicable for SSE and HTTP transports.
      - Useful for authentication tokens.
    type: dict
    default: {}
  timeout:
    description:
      - Connection timeout in seconds.
    type: int
    default: 30
  connection_reuse:
    description:
      - Enable connection pooling for better performance.
      - When enabled, connections are reused across multiple module calls.
      - Significantly improves performance for sequential operations.
    type: bool
    default: true
    version_added: "1.1.0"
  connection_timeout:
    description:
      - Connection timeout in seconds for pooled connections.
      - Only applicable when I(connection_reuse=true).
      - Connections are automatically closed after this timeout.
    type: int
    default: 300
    version_added: "1.1.0"
notes:
  - Requires the MCP Python SDK (>=1.19.0) to be installed.
  - The server must implement the MCP protocol specification.
  - HTTP transport is currently not implemented (will return an error).
requirements:
  - python >= 3.9
  - mcp >= 1.19.0
"""

EXAMPLES = r"""
- name: Get information from stdio MCP server
  mcp.audit.mcp_server_info:
    transport: stdio
    server_command: python
    server_args:
      - -m
      - my_mcp_server
  register: server_info

- name: Get information from SSE MCP server with authentication
  mcp.audit.mcp_server_info:
    transport: sse
    server_url: http://localhost:8000/sse
    server_headers:
      Authorization: "Bearer {{ api_token }}"
    timeout: 60
  register: server_info

- name: Check if server has tool capabilities
  mcp.audit.mcp_server_info:
    transport: stdio
    server_command: node
    server_args: [server.js]
  register: result

- name: Display server capabilities
  ansible.builtin.debug:
    msg: "Server {{ result.server_info.server_name }} supports: {{ result.server_info.capabilities.keys() | list }}"
  when: result.success
"""

RETURN = r"""
success:
  description: Whether the operation succeeded.
  returned: always
  type: bool
  sample: true
changed:
  description: Whether the module made any changes (always false for info modules).
  returned: always
  type: bool
  sample: false
status:
  description: Status message describing the result.
  returned: always
  type: str
  sample: "Successfully retrieved server information"
server_info:
  description: Information about the MCP server.
  returned: when success is true
  type: dict
  contains:
    server_name:
      description: Name of the MCP server.
      type: str
      sample: "my-mcp-server"
    server_version:
      description: Version of the MCP server.
      type: str
      sample: "1.0.0"
    protocol_version:
      description: MCP protocol version supported.
      type: str
      sample: "2024-11-05"
    capabilities:
      description: Server capabilities.
      type: dict
      sample:
        tools: {}
        resources: {"subscribe": true}
        prompts: {}
execution_time:
  description: Time taken to retrieve server information (in seconds).
  returned: always
  type: float
  sample: 0.523
error:
  description: Error message if the operation failed.
  returned: when success is false
  type: str
  sample: "Failed to connect to MCP server: Connection refused"
"""

import asyncio
import time

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.tosin2013.mcp_audit.plugins.module_utils.mcp_client import (
    MCPClient,
    MCPClientError,
    MCPConnectionError,
    create_mcp_client,
)
from ansible_collections.tosin2013.mcp_audit.plugins.module_utils.mcp_connection_manager import (
    get_connection_manager,
)
from ansible_collections.tosin2013.mcp_audit.plugins.module_utils.mcp_reporter import (
    create_result,
)


async def get_server_info_async(
    client: MCPClient, max_retries: int = 3, connection_reuse: bool = True, connection_timeout: int = 300
) -> dict:
    """
    Asynchronously get server information with retry logic and optional connection pooling (Phase 2).

    Args:
        client: MCPClient instance
        max_retries: Maximum number of retry attempts for connection failures
        connection_reuse: Enable connection pooling for better performance (default: True)
        connection_timeout: Connection timeout in seconds for pooled connections (default: 300)

    Returns:
        Server information dictionary

    Raises:
        MCPClientError: If retrieval fails after all retries
    """
    retry_delay = 0.5
    last_exception = None

    for attempt in range(max_retries):
        try:
            if connection_reuse:
                # Use connection pooling (Phase 2)
                manager = get_connection_manager()
                persistent_client = await manager.get_or_create_connection(
                    client, timeout=connection_timeout, enable_reuse=True
                )
                # Get server info using persistent connection
                info = await persistent_client.get_server_info()

                # Also try to get available capabilities
                try:
                    tools = await persistent_client.list_tools()
                    info["available_tools"] = len(tools)
                except Exception:
                    info["available_tools"] = None

                try:
                    resources = await persistent_client.list_resources()
                    info["available_resources"] = len(resources)
                except Exception:
                    info["available_resources"] = None

                try:
                    prompts = await persistent_client.list_prompts()
                    info["available_prompts"] = len(prompts)
                except Exception:
                    info["available_prompts"] = None

                return info
            else:
                # Use traditional context manager (Phase 1)
                async with client.connect():
                    info = await client.get_server_info()

                    # Also try to get available capabilities
                    try:
                        tools = await client.list_tools()
                        info["available_tools"] = len(tools)
                    except Exception:
                        info["available_tools"] = None

                    try:
                        resources = await client.list_resources()
                        info["available_resources"] = len(resources)
                    except Exception:
                        info["available_resources"] = None

                    try:
                        prompts = await client.list_prompts()
                        info["available_prompts"] = len(prompts)
                    except Exception:
                        info["available_prompts"] = None

                    return info

        except MCPConnectionError as e:
            last_exception = e
            error_msg = str(e)

            # Only retry on specific connection errors (TaskGroup, process cleanup)
            if ("TaskGroup" in error_msg or "unhandled errors" in error_msg) and attempt < max_retries - 1:
                # Exponential backoff for retries
                wait_time = retry_delay * (attempt + 1)
                await asyncio.sleep(wait_time)
                continue

            # Re-raise if not a retryable error or out of retries
            raise

        except Exception:
            # Don't retry on other types of errors
            raise

    # If we exhausted all retries, raise the last exception
    if last_exception:
        raise MCPConnectionError(
            f"Failed to connect after {max_retries} attempts. Last error: {last_exception}"
        ) from last_exception


def run_module():
    """Run the Ansible module."""
    module_args = {
        "transport": {"type": "str", "default": "stdio", "choices": ["stdio", "sse", "http"]},
        "server_command": {"type": "str", "required": False},
        "server_args": {"type": "list", "elements": "str", "default": []},
        "server_url": {"type": "str", "required": False},
        "server_headers": {"type": "dict", "default": {}},
        "timeout": {"type": "int", "default": 30},
        "connection_reuse": {"type": "bool", "default": True},
        "connection_timeout": {"type": "int", "default": 300},
    }

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    # Validate transport-specific parameters
    transport = module.params["transport"]
    if transport == "stdio" and not module.params.get("server_command"):
        module.fail_json(msg="server_command is required for stdio transport")
    if transport in ("sse", "http") and not module.params.get("server_url"):
        module.fail_json(msg="server_url is required for sse/http transport")

    start_time = time.time()

    try:
        # Create MCP client
        client = create_mcp_client(module.params)

        # Get server information
        server_info = asyncio.run(
            get_server_info_async(
                client,
                connection_reuse=module.params.get("connection_reuse", True),
                connection_timeout=module.params.get("connection_timeout", 300),
            )
        )

        execution_time = time.time() - start_time

        # Create success result
        result = create_result(
            success=True,
            status="Successfully retrieved server information",
            response=server_info,
            execution_time=execution_time,
            changed=False,
        )

        # Rename 'response' to 'server_info' for clarity
        result["server_info"] = result.pop("response")

        module.exit_json(**result)

    except MCPConnectionError as e:
        execution_time = time.time() - start_time
        result = create_result(
            success=False,
            status="Connection failed",
            error=f"Failed to connect to MCP server: {e!s}",
            execution_time=execution_time,
            changed=False,
        )
        module.fail_json(msg=result["error"], **result)

    except MCPClientError as e:
        execution_time = time.time() - start_time
        result = create_result(
            success=False,
            status="Client error",
            error=f"MCP client error: {e!s}",
            execution_time=execution_time,
            changed=False,
        )
        module.fail_json(msg=result["error"], **result)

    except Exception as e:
        execution_time = time.time() - start_time
        result = create_result(
            success=False,
            status="Unexpected error",
            error=f"Unexpected error: {e!s}",
            execution_time=execution_time,
            changed=False,
        )
        module.fail_json(msg=result["error"], **result)


def main():
    """Module entry point."""
    run_module()


if __name__ == "__main__":
    main()
