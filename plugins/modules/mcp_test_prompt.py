#!/usr/bin/python

# Copyright: (c) 2024, Tosin Akinosho <tosin.akinosho@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r"""
---
module: mcp_test_prompt
short_description: Test an MCP server prompt
version_added: "1.0.0"
description:
  - Tests a specific prompt on a Model Context Protocol (MCP) server.
  - Retrieves the prompt with provided arguments and validates the response.
  - Verifies that the prompt returns properly formatted messages.
  - Returns detailed test results including validation status.
author:
  - Tosin Akinosho (@tosinakinosho)
options:
  prompt_name:
    description:
      - Name of the prompt to test.
    type: str
    required: true
  prompt_arguments:
    description:
      - Arguments to pass to the prompt.
      - Must be a dictionary matching the prompt's expected parameters.
    type: dict
    default: {}
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
  - The prompt must exist on the server and accept the provided arguments.
  - HTTP transport is currently not implemented (will return an error).
requirements:
  - python >= 3.9
  - mcp >= 1.19.0
"""

EXAMPLES = r"""
- name: Test a greeting prompt
  mcp.audit.mcp_test_prompt:
    prompt_name: greeting
    prompt_arguments:
      name: "World"
      language: "en"
    transport: stdio
    server_command: python
    server_args: ["-m", "prompt_server"]
  register: result

- name: Test prompt without arguments
  mcp.audit.mcp_test_prompt:
    prompt_name: system_info
    transport: sse
    server_url: http://localhost:8000/sse
  register: sys_info

- name: Test code generation prompt
  mcp.audit.mcp_test_prompt:
    prompt_name: generate_code
    prompt_arguments:
      language: "python"
      task: "factorial function"
    transport: stdio
    server_command: node
    server_args: [server.js]
  register: code_prompt
  failed_when: not code_prompt.test_passed
"""

RETURN = r"""
success:
  description: Whether the prompt retrieval succeeded.
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
  sample: "Prompt test passed"
test_passed:
  description: Whether the prompt test passed validation.
  returned: always
  type: bool
  sample: true
prompt_result:
  description: The prompt response with messages.
  returned: when success is true
  type: dict
  contains:
    messages:
      description: Prompt messages.
      type: list
      sample: [{"role": "user", "content": "Hello World"}]
validation:
  description: Validation results for the prompt response.
  returned: when success is true
  type: dict
  contains:
    valid:
      description: Whether the response structure is valid.
      type: bool
      sample: true
    has_messages:
      description: Whether the prompt has messages.
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
  description: Time taken to retrieve the prompt (in seconds).
  returned: always
  type: float
  sample: 0.234
error:
  description: Error message if the operation failed.
  returned: when success is false
  type: str
  sample: "Prompt 'unknown_prompt' not found"
"""

import asyncio
import time

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mcp.audit.plugins.module_utils.mcp_client import (
    MCPClient,
    MCPClientError,
    MCPConnectionError,
    create_mcp_client,
)
from ansible_collections.mcp.audit.plugins.module_utils.mcp_reporter import (
    create_result,
)
from ansible_collections.mcp.audit.plugins.module_utils.mcp_validator import (
    MCPValidator,
)


async def test_prompt_async(client: MCPClient, prompt_name: str, prompt_arguments: dict) -> dict:
    """
    Asynchronously test a prompt.

    Args:
        client: MCPClient instance
        prompt_name: Name of the prompt to test
        prompt_arguments: Arguments for the prompt

    Returns:
        Dictionary with test results

    Raises:
        MCPClientError: If prompt retrieval fails
    """
    async with client.connect():
        # Get the prompt
        result = await client.get_prompt(prompt_name, prompt_arguments)

        # Validate the response
        validator = MCPValidator()
        validation = validator.validate_prompt_response(result)

        return {"prompt_result": result, "validation": validation}


def run_module():
    """Run the Ansible module."""
    module_args = {
        "prompt_name": {"type": "str", "required": True},
        "prompt_arguments": {"type": "dict", "default": {}},
        "transport": {"type": "str", "default": "stdio", "choices": ["stdio", "sse", "http"]},
        "server_command": {"type": "str", "required": False},
        "server_args": {"type": "list", "elements": "str", "default": []},
        "server_url": {"type": "str", "required": False},
        "server_headers": {"type": "dict", "default": {}},
        "timeout": {"type": "int", "default": 30},
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

        # Test the prompt
        test_result = asyncio.run(
            test_prompt_async(
                client,
                module.params["prompt_name"],
                module.params["prompt_arguments"],
            )
        )

        execution_time = time.time() - start_time

        # Determine if test passed
        validation = test_result["validation"]
        test_passed = validation["valid"]

        # Serialize the prompt result for JSON compatibility
        from ansible_collections.mcp.audit.plugins.module_utils.mcp_reporter import MCPReporter

        serialized_prompt_result = MCPReporter._serialize_response(test_result["prompt_result"])

        # Create success result
        result = create_result(
            success=True,
            status="Prompt test passed" if test_passed else "Prompt test completed with warnings",
            response={"prompt_result": serialized_prompt_result, "validation": test_result["validation"]},
            execution_time=execution_time,
            changed=False,
        )

        # Flatten the response structure
        result["prompt_result"] = serialized_prompt_result
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
            status="Prompt test failed",
            error=f"Prompt test error: {e!s}",
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
