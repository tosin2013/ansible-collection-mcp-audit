#!/usr/bin/python

# Copyright: (c) 2024, Tosin Akinosho <tosin.akinosho@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: mcp_test_suite
short_description: Run a suite of MCP server tests
version_added: "1.0.0"
description:
  - Runs a comprehensive test suite against an MCP server.
  - Tests server capabilities, tools, resources, and prompts.
  - Generates a detailed test report with pass/fail statistics.
  - Useful for validating server implementations and monitoring health.
author:
  - Tosin Akinosho (@tosinakinosho)
options:
  tests:
    description:
      - List of tests to run against the MCP server.
      - Each test specifies type (tool/resource/prompt) and parameters.
    type: list
    elements: dict
    required: true
  fail_on_error:
    description:
      - Whether to fail the module if any test fails.
      - If false, module succeeds even if individual tests fail.
    type: bool
    default: false
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
  - HTTP transport is currently not implemented (will return an error).
requirements:
  - python >= 3.9
  - mcp >= 1.19.0
"""

EXAMPLES = r"""
- name: Run comprehensive test suite
  mcp.audit.mcp_test_suite:
    transport: stdio
    server_command: python
    server_args: ["-m", "my_mcp_server"]
    tests:
      - type: tool
        name: add
        arguments: {a: 5, b: 3}
        expected_result: 8
      - type: tool
        name: multiply
        arguments: {x: 6, y: 7}
        expected_result: 42
      - type: resource
        uri: "file:///config.yaml"
        expected_content_type: "text/yaml"
      - type: prompt
        name: greeting
        arguments: {name: "User"}
    fail_on_error: false
  register: test_results

- name: Run basic server validation
  mcp.audit.mcp_test_suite:
    transport: sse
    server_url: http://localhost:8000/sse
    tests:
      - type: tool
        name: echo
        arguments: {message: "test"}
    fail_on_error: true
  register: validation

- name: Test suite with failure handling
  mcp.audit.mcp_test_suite:
    transport: stdio
    server_command: node
    server_args: [server.js]
    tests:
      - type: tool
        name: calculate
        arguments: {operation: "add", values: [1, 2, 3]}
        expected_result: 6
    fail_on_error: false
  register: results
"""

RETURN = r"""
success:
  description: Whether the test suite execution succeeded.
  returned: always
  type: bool
  sample: true
changed:
  description: Whether the module made any changes (always false for test modules).
  returned: always
  type: bool
  sample: false
status:
  description: Status message describing the overall result.
  returned: always
  type: str
  sample: "Test suite completed: 4 passed, 0 failed"
test_results:
  description: Results for each individual test.
  returned: always
  type: list
  elements: dict
  contains:
    test_type:
      description: Type of test (tool/resource/prompt).
      type: str
      sample: "tool"
    test_name:
      description: Name or identifier of the test.
      type: str
      sample: "add"
    passed:
      description: Whether this specific test passed.
      type: bool
      sample: true
    error:
      description: Error message if test failed.
      type: str
      sample: null
summary:
  description: Summary statistics for the test suite.
  returned: always
  type: dict
  contains:
    total_tests:
      description: Total number of tests run.
      type: int
      sample: 4
    passed:
      description: Number of tests that passed.
      type: int
      sample: 3
    failed:
      description: Number of tests that failed.
      type: int
      sample: 1
    success_rate:
      description: Percentage of tests that passed.
      type: float
      sample: 75.0
execution_time:
  description: Total time taken to run the test suite (in seconds).
  returned: always
  type: float
  sample: 1.234
error:
  description: Error message if the test suite failed to run.
  returned: when success is false
  type: str
  sample: "Failed to connect to MCP server"
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


async def run_test_suite_async(client: MCPClient, tests: list) -> dict:
    """
    Asynchronously run a test suite.

    Args:
        client: MCPClient instance
        tests: List of test specifications

    Returns:
        Dictionary with test results and summary
    """
    test_results = []
    validator = MCPValidator()

    async with client.connect():
        for test_spec in tests:
            test_type = test_spec.get("type")
            test_result = {
                "test_type": test_type,
                "test_name": test_spec.get("name") or test_spec.get("uri") or "unknown",
                "passed": False,
                "error": None,
            }

            try:
                if test_type == "tool":
                    tool_name = test_spec["name"]
                    arguments = test_spec.get("arguments", {})
                    expected = test_spec.get("expected_result")

                    response = await client.call_tool(tool_name, arguments)
                    validation = validator.validate_tool_response(response, expected_result=expected)
                    test_result["passed"] = validation["valid"] and (validation["matches_expected"] is not False)
                    if not test_result["passed"]:
                        test_result["error"] = "; ".join(validation.get("errors", []))

                elif test_type == "resource":
                    resource_uri = test_spec["uri"]
                    expected_type = test_spec.get("expected_content_type")

                    response = await client.read_resource(resource_uri)
                    validation = validator.validate_resource_response(response, expected_content_type=expected_type)
                    test_result["passed"] = validation["valid"]
                    if not test_result["passed"]:
                        test_result["error"] = "; ".join(validation.get("errors", []))

                elif test_type == "prompt":
                    prompt_name = test_spec["name"]
                    arguments = test_spec.get("arguments", {})

                    response = await client.get_prompt(prompt_name, arguments)
                    validation = validator.validate_prompt_response(response)
                    test_result["passed"] = validation["valid"]
                    if not test_result["passed"]:
                        test_result["error"] = "; ".join(validation.get("errors", []))

                else:
                    test_result["error"] = f"Unknown test type: {test_type}"

            except Exception as e:
                test_result["error"] = str(e)

            test_results.append(test_result)

    # Calculate summary
    total_tests = len(test_results)
    passed = sum(1 for t in test_results if t["passed"])
    failed = total_tests - passed
    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0

    summary = {
        "total_tests": total_tests,
        "passed": passed,
        "failed": failed,
        "success_rate": round(success_rate, 2),
    }

    return {"test_results": test_results, "summary": summary}


def run_module():
    """Run the Ansible module."""
    module_args = {
        "tests": {"type": "list", "elements": "dict", "required": True},
        "fail_on_error": {"type": "bool", "default": False},
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

    # Validate tests parameter
    if not module.params["tests"]:
        module.fail_json(msg="tests parameter cannot be empty")

    start_time = time.time()

    try:
        # Create MCP client
        client = create_mcp_client(module.params)

        # Run test suite
        suite_result = asyncio.run(run_test_suite_async(client, module.params["tests"]))

        execution_time = time.time() - start_time

        # Determine overall success
        summary = suite_result["summary"]
        all_passed = summary["failed"] == 0
        should_fail = module.params["fail_on_error"] and not all_passed

        status = f"Test suite completed: {summary['passed']} passed, {summary['failed']} failed"

        # Create result
        result = create_result(
            success=True,
            status=status,
            response=suite_result,
            execution_time=execution_time,
            changed=False,
        )

        # Flatten the response structure
        result["test_results"] = suite_result["test_results"]
        result["summary"] = suite_result["summary"]
        result.pop("response")

        if should_fail:
            module.fail_json(msg=f"Test suite failed: {summary['failed']} tests failed", **result)
        else:
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
            status="Test suite failed",
            error=f"Test suite error: {e!s}",
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
