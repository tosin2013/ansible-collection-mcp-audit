#!/usr/bin/python

# Copyright: (c) 2024, Tosin Akinosho <tosin.akinosho@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: mcp_test_resource
short_description: Test an MCP server resource
version_added: "1.0.0"
description:
  - Tests a specific resource on a Model Context Protocol (MCP) server.
  - Reads the resource and validates the response.
  - Optionally verifies the content type matches expectations.
  - Returns detailed test results including validation status.
author:
  - Tosin Akinosho (@tosinakinosho)
options:
  resource_uri:
    description:
      - URI of the resource to test.
      - Format depends on the server's resource schema (e.g., "file:///path/to/file").
    type: str
    required: true
  expected_content_type:
    description:
      - Expected MIME type of the resource content.
      - If provided, validates that the resource returns this content type.
    type: str
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
  - The resource must exist on the server and be accessible.
  - HTTP transport is currently not implemented (will return an error).
requirements:
  - python >= 3.9
  - mcp >= 1.19.0
"""

EXAMPLES = r"""
- name: Test reading a file resource
  mcp.audit.mcp_test_resource:
    resource_uri: "file:///etc/config.yaml"
    expected_content_type: "text/yaml"
    transport: stdio
    server_command: python
    server_args: ["-m", "file_server"]
  register: result

- name: Test resource without content type validation
  mcp.audit.mcp_test_resource:
    resource_uri: "db://users/123"
    transport: sse
    server_url: http://localhost:8000/sse
  register: user_resource

- name: Test resource and verify it exists
  mcp.audit.mcp_test_resource:
    resource_uri: "config://app/settings"
    expected_content_type: "application/json"
    transport: stdio
    server_command: node
    server_args: [server.js]
  register: config_result
  failed_when: not config_result.test_passed
"""

RETURN = r"""
success:
  description: Whether the resource read succeeded.
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
  sample: "Resource test passed"
test_passed:
  description: Whether the resource test passed validation.
  returned: always
  type: bool
  sample: true
resource_content:
  description: The content of the resource.
  returned: when success is true
  type: dict
  contains:
    contents:
      description: Resource content items.
      type: list
      sample: [{"mimeType": "text/plain", "text": "file contents"}]
validation:
  description: Validation results for the resource response.
  returned: when success is true
  type: dict
  contains:
    valid:
      description: Whether the response structure is valid.
      type: bool
      sample: true
    content_type:
      description: The MIME type of the resource content.
      type: str
      sample: "text/plain"
    errors:
      description: List of validation errors.
      type: list
      sample: []
    warnings:
      description: List of validation warnings.
      type: list
      sample: []
execution_time:
  description: Time taken to read the resource (in seconds).
  returned: always
  type: float
  sample: 0.156
error:
  description: Error message if the operation failed.
  returned: when success is false
  type: str
  sample: "Resource 'unknown://resource' not found"
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
from ansible_collections.tosin2013.mcp_audit.plugins.module_utils.mcp_validator import (
    MCPValidator,
)


async def test_resource_async(
    client: MCPClient,
    resource_uri: str,
    expected_content_type=None,
    max_retries: int = 3,
    connection_reuse: bool = True,
    connection_timeout: int = 300,
) -> dict:
    """
    Asynchronously test a resource with retry logic and optional connection pooling (Phase 2).

    Args:
        client: MCPClient instance
        resource_uri: URI of the resource to read
        expected_content_type: Expected content type for validation
        max_retries: Maximum number of retry attempts for connection failures
        connection_reuse: Enable connection pooling for better performance (default: True)
        connection_timeout: Connection timeout in seconds for pooled connections (default: 300)

    Returns:
        Dictionary with test results

    Raises:
        MCPClientError: If resource read fails after all retries
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
                # Read the resource using persistent connection
                result = await persistent_client.read_resource(resource_uri)

                # Validate the response
                validator = MCPValidator()
                validation = validator.validate_resource_response(result, expected_content_type=expected_content_type)

                return {"resource_content": result, "validation": validation}
            else:
                # Use traditional context manager (Phase 1)
                async with client.connect():
                    # Read the resource
                    result = await client.read_resource(resource_uri)

                    # Validate the response
                    validator = MCPValidator()
                    validation = validator.validate_resource_response(result, expected_content_type=expected_content_type)

                    return {"resource_content": result, "validation": validation}

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
        "resource_uri": {"type": "str", "required": True},
        "expected_content_type": {"type": "str", "required": False},
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

        # Test the resource
        test_result = asyncio.run(
            test_resource_async(
                client,
                module.params["resource_uri"],
                module.params.get("expected_content_type"),
                connection_reuse=module.params.get("connection_reuse", True),
                connection_timeout=module.params.get("connection_timeout", 300),
            )
        )

        execution_time = time.time() - start_time

        # Determine if test passed
        validation = test_result["validation"]
        test_passed = validation["valid"]

        # Serialize the resource content for JSON compatibility
        from ansible_collections.tosin2013.mcp_audit.plugins.module_utils.mcp_reporter import MCPReporter

        serialized_resource_content = MCPReporter._serialize_response(test_result["resource_content"])

        # Create success result
        result = create_result(
            success=True,
            status="Resource test passed" if test_passed else "Resource test completed with warnings",
            response={"resource_content": serialized_resource_content, "validation": test_result["validation"]},
            execution_time=execution_time,
            changed=False,
        )

        # Flatten the response structure
        result["resource_content"] = serialized_resource_content
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
            status="Resource test failed",
            error=f"Resource test error: {e!s}",
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
