#!/usr/bin/python

# Copyright: (c) 2024, Tosin Akinosho <tosin.akinosho@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: mcp_test_tool
short_description: Test an MCP server tool
version_added: "1.0.0"
description:
  - Tests a specific tool on a Model Context Protocol (MCP) server.
  - Calls the tool with provided arguments and validates the response.
  - Optionally compares the result with an expected value.
  - Returns detailed test results including validation status.
author:
  - Tosin Akinosho (@tosinakinosho)
options:
  tool_name:
    description:
      - Name of the tool to test.
    type: str
    required: true
  tool_arguments:
    description:
      - Arguments to pass to the tool.
      - Must be a dictionary matching the tool's expected parameters.
    type: dict
    default: {}
  expected_result:
    description:
      - Expected result to compare against the actual result.
      - If provided, the module will validate that the tool returns this value.
      - Comparison supports type coercion (e.g., "42" matches 42).
    type: raw
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
    type: dict
    default: {}
  timeout:
    description:
      - Connection timeout in seconds.
    type: int
    default: 30
notes:
  - Requires the MCP Python SDK (>=1.19.0) to be installed.
  - The tool must exist on the server and accept the provided arguments.
  - HTTP transport is currently not implemented (will return an error).
requirements:
  - python >= 3.9
  - mcp >= 1.19.0
"""

EXAMPLES = r"""
- name: Test add tool on calculator server
  mcp.audit.mcp_test_tool:
    tool_name: add
    tool_arguments:
      a: 5
      b: 3
    expected_result: 8
    transport: stdio
    server_command: python
    server_args: ["-m", "calculator_server"]
  register: result

- name: Test tool without expected result
  mcp.audit.mcp_test_tool:
    tool_name: get_weather
    tool_arguments:
      city: "San Francisco"
    transport: sse
    server_url: http://localhost:8000/sse
  register: weather_result

- name: Test tool and verify response structure
  mcp.audit.mcp_test_tool:
    tool_name: search
    tool_arguments:
      query: "ansible automation"
      limit: 10
    transport: stdio
    server_command: node
    server_args: [server.js]
  register: search_result

- name: Fail if tool result doesn't match expected
  mcp.audit.mcp_test_tool:
    tool_name: multiply
    tool_arguments:
      x: 6
      y: 7
    expected_result: 42
    transport: stdio
    server_command: python
    server_args: ["-m", "math_server"]
  register: result
  failed_when: not result.test_passed
"""

RETURN = r"""
success:
  description: Whether the tool call succeeded.
  returned: always
  type: bool
  sample: true
changed:
  description: Whether the module made any changes (always false for test modules).
  returned: always
  type: bool
  sample: false
status:
  description: Status message describing the result.
  returned: always
  type: str
  sample: "Tool test passed"
test_passed:
  description: Whether the tool test passed validation.
  returned: always
  type: bool
  sample: true
tool_result:
  description: The result returned by the tool.
  returned: when success is true
  type: dict
  contains:
    content:
      description: Tool response content.
      type: list
      sample: [{"type": "text", "text": "8"}]
validation:
  description: Validation results for the tool response.
  returned: when success is true
  type: dict
  contains:
    valid:
      description: Whether the response structure is valid.
      type: bool
      sample: true
    matches_expected:
      description: Whether the result matches the expected value (null if no expected value provided).
      type: bool
      sample: true
    errors:
      description: List of validation errors.
      type: list
      sample: []
    warnings:
      description: List of validation warnings.
      type: list
      sample: []
execution_time:
  description: Time taken to execute the tool (in seconds).
  returned: always
  type: float
  sample: 0.234
error:
  description: Error message if the operation failed.
  returned: when success is false
  type: str
  sample: "Tool 'unknown_tool' not found on server"
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
from ansible_collections.tosin2013.mcp_audit.plugins.module_utils.mcp_reporter import (
    create_result,
)
from ansible_collections.tosin2013.mcp_audit.plugins.module_utils.mcp_validator import (
    MCPValidator,
)


async def test_tool_async(
    client: MCPClient,
    tool_name: str,
    tool_arguments: dict,
    expected_result=None,
    max_retries: int = 3,
    connection_reuse: bool = True,
    connection_timeout: int = 300,
) -> dict:
    """
    Asynchronously test a tool with retry logic and optional connection pooling (Phase 2).

    Args:
        client: MCPClient instance
        tool_name: Name of the tool to test
        tool_arguments: Arguments for the tool
        expected_result: Expected result for comparison
        max_retries: Maximum number of retry attempts for connection failures
        connection_reuse: Enable connection pooling for better performance (default: True)
        connection_timeout: Connection timeout in seconds for pooled connections (default: 300)

    Returns:
        Dictionary with test results

    Raises:
        MCPClientError: If tool call fails after all retries
    """
    from ansible_collections.tosin2013.mcp_audit.plugins.module_utils.mcp_connection_manager import (
        get_connection_manager,
    )

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
                # Call the tool using persistent connection
                result = await persistent_client.call_tool(tool_name, tool_arguments)

                # Validate the response
                validator = MCPValidator()
                validation = validator.validate_tool_response(result, expected_result=expected_result)

                return {"tool_result": result, "validation": validation}
            else:
                # Use traditional context manager (Phase 1)
                async with client.connect():
                    # Call the tool
                    result = await client.call_tool(tool_name, tool_arguments)

                    # Validate the response
                    validator = MCPValidator()
                    validation = validator.validate_tool_response(result, expected_result=expected_result)

                    return {"tool_result": result, "validation": validation}

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

        except Exception as e:
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
        "tool_name": {"type": "str", "required": True},
        "tool_arguments": {"type": "dict", "default": {}},
        "expected_result": {"type": "raw", "required": False},
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

        # Test the tool
        test_result = asyncio.run(
            test_tool_async(
                client,
                module.params["tool_name"],
                module.params["tool_arguments"],
                module.params.get("expected_result"),
                connection_reuse=module.params.get("connection_reuse", True),
                connection_timeout=module.params.get("connection_timeout", 300),
            )
        )

        execution_time = time.time() - start_time

        # Determine if test passed
        validation = test_result["validation"]
        test_passed = validation["valid"] and (validation["matches_expected"] is not False)

        # Serialize the tool result for JSON compatibility
        from ansible_collections.tosin2013.mcp_audit.plugins.module_utils.mcp_reporter import MCPReporter

        serialized_tool_result = MCPReporter._serialize_response(test_result["tool_result"])

        # Create success result
        result = create_result(
            success=True,
            status="Tool test passed" if test_passed else "Tool test completed with warnings",
            response={"tool_result": serialized_tool_result, "validation": test_result["validation"]},
            execution_time=execution_time,
            changed=False,
        )

        # Flatten the response structure
        result["tool_result"] = serialized_tool_result
        result["validation"] = test_result["validation"]
        result["test_passed"] = test_passed
        result.pop("response")

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
        result["test_passed"] = False
        module.fail_json(msg=result["error"], **result)

    except MCPClientError as e:
        execution_time = time.time() - start_time
        result = create_result(
            success=False,
            status="Tool test failed",
            error=f"Tool test error: {e!s}",
            execution_time=execution_time,
            changed=False,
        )
        result["test_passed"] = False
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
        result["test_passed"] = False
        module.fail_json(msg=result["error"], **result)


def main():
    """Module entry point."""
    run_module()


if __name__ == "__main__":
    main()
