#!/usr/bin/python

# Copyright: (c) 2024, Tosin Akinosho <tosin.akinosho@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


DOCUMENTATION = r"""
---
module: mcp_test_llm_integration
short_description: Test MCP server with real LLM integration
version_added: "1.1.0"
description:
  - Tests an MCP server by having a real LLM interact with it.
  - Uses LiteLLM to support 100+ LLM providers (OpenAI, Anthropic, Ollama, vLLM, OpenRouter, etc.).
  - The LLM decides when to call MCP tools based on a test prompt.
  - Validates end-to-end tool invocation flow (LLM → MCP server → result → LLM).
  - Returns detailed test results including tool calls and LLM responses.
author:
  - Tosin Akinosho (@tosinakinosho)
options:
  test_prompt:
    description:
      - The prompt/question to send to the LLM.
      - The LLM will use available MCP tools to answer this prompt.
    type: str
    required: true
  llm_provider:
    description:
      - LLM provider to use via LiteLLM.
      - See U(https://docs.litellm.ai/docs/providers) for complete list.
    type: str
    choices: ['openai', 'anthropic', 'ollama', 'vllm', 'openrouter', 'azure', 'bedrock', 'vertex_ai', 'cohere']
    default: 'ollama'
  llm_model:
    description:
      - Model name to use with the LLM provider.
      - Format varies by provider (e.g., 'gpt-4', 'claude-3-opus', 'phi3.5').
    type: str
    required: true
  llm_api_key:
    description:
      - API key for the LLM provider.
      - Should be stored in Ansible Vault for security.
      - Not required for local providers like Ollama.
    type: str
  llm_base_url:
    description:
      - Base URL for the LLM API.
      - Required for self-hosted providers (vLLM, Ollama, LocalAI).
      - Default for Ollama is http://localhost:11434.
    type: str
  expected_tool_calls:
    description:
      - List of tool names that should be called by the LLM.
      - If provided, validates that these specific tools were invoked.
    type: list
    elements: str
  validate_result:
    description:
      - Whether to validate the LLM's final answer.
      - Requires I(expected_answer) to be provided.
    type: bool
    default: false
  expected_answer:
    description:
      - Expected final answer from the LLM.
      - Only used when I(validate_result=true).
    type: str
  max_iterations:
    description:
      - Maximum number of LLM-tool interaction loops.
      - Prevents infinite loops if LLM keeps calling tools.
    type: int
    default: 5
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
  - Requires LiteLLM (>=1.0.0) to be installed.
  - Requires the MCP Python SDK (>=1.19.0) to be installed.
  - API keys should be managed via Ansible Vault for security.
  - Local models (Ollama, vLLM) can be used for free testing without API costs.
  - See ADR-0016 for architecture and design decisions.
requirements:
  - python >= 3.9
  - mcp >= 1.19.0
  - litellm >= 1.0.0
seealso:
  - name: LiteLLM Documentation
    description: Complete LiteLLM documentation
    link: https://docs.litellm.ai/
  - name: LiteLLM Providers
    description: List of supported LLM providers
    link: https://docs.litellm.ai/docs/providers
  - name: Ollama
    description: Local LLM deployment
    link: https://ollama.ai/
  - name: ADR-0016
    description: Architecture decision for LiteLLM integration
    link: https://github.com/ansible-collections/mcp.audit/blob/main/docs/adrs/0016-litellm-integration.md
"""

EXAMPLES = r"""
- name: Test calculator server with Ollama (local, free)
  mcp.audit.mcp_test_llm_integration:
    test_prompt: "Calculate the sum of 15 and 27"
    llm_provider: "ollama"
    llm_model: "phi3.5"
    llm_base_url: "http://localhost:11434"
    server_command: "{{ python_interpreter }}"
    server_args:
      - "{{ test_servers_path }}/calculator/server.py"
    transport: "stdio"
    expected_tool_calls: ["add"]
    validate_result: true
    expected_answer: "42"
  register: result

- name: Test with OpenAI GPT-4 (API key from Vault)
  mcp.audit.mcp_test_llm_integration:
    test_prompt: "What is 10 multiplied by 5?"
    llm_provider: "openai"
    llm_model: "gpt-4"
    llm_api_key: "{{ openai_api_key }}"  # From Ansible Vault
    server_command: "python"
    server_args: ["-m", "calculator_server"]
    transport: "stdio"
  register: result

- name: Test with vLLM self-hosted model
  mcp.audit.mcp_test_llm_integration:
    test_prompt: "Calculate 42 + 58"
    llm_provider: "vllm"
    llm_model: "meta-llama/Llama-2-7b-chat-hf"
    llm_api_key: "dummy"
    llm_base_url: "http://localhost:8000"
    server_command: "python"
    server_args: ["server.py"]
    transport: "stdio"
    max_iterations: 3

- name: Test with OpenRouter
  mcp.audit.mcp_test_llm_integration:
    test_prompt: "Use the search tool to find information about Python"
    llm_provider: "openrouter"
    llm_model: "anthropic/claude-3-opus"
    llm_api_key: "{{ openrouter_api_key }}"
    server_command: "node"
    server_args: ["search-server.js"]
    transport: "stdio"
"""

RETURN = r"""
success:
  description: Whether the test completed successfully
  returned: always
  type: bool
  sample: true
llm_interactions:
  description: List of all LLM interactions (requests and responses)
  returned: always
  type: list
  elements: dict
  sample:
    - iteration: 1
      user_message: "Calculate 15 + 27"
      tool_calls:
        - tool_name: "add"
          arguments: {"a": 15, "b": 27}
          result: "42"
      llm_response: "The sum is 42"
tool_calls_made:
  description: List of all MCP tools that were called
  returned: always
  type: list
  elements: str
  sample: ["add", "multiply"]
final_answer:
  description: The LLM's final answer after all tool interactions
  returned: always
  type: str
  sample: "The answer is 42"
validation:
  description: Validation results
  returned: when validation is requested
  type: dict
  contains:
    expected_tools_called:
      description: Whether expected tools were called
      type: bool
    tools_validated:
      description: List of tool call validations
      type: list
    answer_matches:
      description: Whether final answer matches expected
      type: bool
total_iterations:
  description: Number of LLM-tool interaction loops
  returned: always
  type: int
  sample: 3
execution_time:
  description: Total execution time in seconds
  returned: always
  type: float
  sample: 2.45
"""

import json
import time
from typing import Any, Optional

try:
    from litellm import completion

    HAS_LITELLM = True
    LITELLM_IMPORT_ERROR = None
except ImportError as e:
    HAS_LITELLM = False
    LITELLM_IMPORT_ERROR = str(e)

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.mcp.audit.plugins.module_utils.mcp_client import MCPClient


def convert_mcp_tools_to_llm_format(mcp_tools: list[Any]) -> list[dict]:
    """Convert MCP tool definitions to LiteLLM function calling format."""
    llm_tools = []

    for tool in mcp_tools:
        llm_tool = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or f"MCP tool: {tool.name}",
                "parameters": tool.inputSchema
                if hasattr(tool, "inputSchema")
                else {"type": "object", "properties": {}},
            },
        }
        llm_tools.append(llm_tool)

    return llm_tools


async def run_llm_integration_test(
    module: AnsibleModule,
    mcp_client: MCPClient,
    test_prompt: str,
    llm_provider: str,
    llm_model: str,
    llm_api_key: Optional[str],
    llm_base_url: Optional[str],
    max_iterations: int,
    expected_tool_calls: Optional[list[str]],
    validate_result: bool,
    expected_answer: Optional[str],
) -> dict[str, Any]:
    """
    Run LLM integration test with MCP server.

    Args:
        module: Ansible module instance
        mcp_client: Connected MCP client
        test_prompt: User prompt for the LLM
        llm_provider: LLM provider name
        llm_model: Model name
        llm_api_key: API key for the provider
        llm_base_url: Base URL for the API
        max_iterations: Maximum interaction loops
        expected_tool_calls: Expected tool names to be called
        validate_result: Whether to validate final answer
        expected_answer: Expected final answer

    Returns:
        Dictionary with test results
    """
    start_time = time.time()

    # Get available tools from MCP server
    tools = await mcp_client.list_tools()
    llm_tools = convert_mcp_tools_to_llm_format(tools)

    # Initialize conversation
    messages = [{"role": "user", "content": test_prompt}]
    interactions = []
    tools_called = []

    # Build LiteLLM model string
    if llm_provider == "ollama":
        model_string = f"ollama/{llm_model}"
    elif llm_provider == "vllm":
        model_string = f"openai/{llm_model}"  # vLLM uses OpenAI-compatible API
    elif llm_provider == "openrouter":
        model_string = f"openrouter/{llm_model}"
    else:
        model_string = llm_model

    # Interaction loop
    for iteration in range(max_iterations):
        interaction = {"iteration": iteration + 1, "user_message": test_prompt if iteration == 0 else None}

        # Call LLM
        llm_kwargs = {"model": model_string, "messages": messages}

        # Only include tools on the first iteration
        # After tools are called, omit tools parameter to force LLM to respond with text
        # This works around Ollama's tool calling loop issue
        if iteration == 0:
            llm_kwargs["tools"] = llm_tools

        if llm_api_key:
            llm_kwargs["api_key"] = llm_api_key
        if llm_base_url:
            llm_kwargs["api_base"] = llm_base_url

        try:
            response = completion(**llm_kwargs)
        except Exception as e:
            return {
                "success": False,
                "error": f"LLM API call failed: {e!s}",
                "execution_time": time.time() - start_time,
            }

        assistant_message = response.choices[0].message

        # Check if LLM wants to call tools
        if hasattr(assistant_message, "tool_calls") and assistant_message.tool_calls:
            tool_results = []

            # First, add the assistant message with ALL tool calls
            tool_calls_json = []
            for tool_call in assistant_message.tool_calls:
                tool_calls_json.append(
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {"name": tool_call.function.name, "arguments": tool_call.function.arguments},
                    }
                )

            messages.append({"role": "assistant", "content": None, "tool_calls": tool_calls_json})

            # Execute each tool call on MCP server
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tools_called.append(tool_name)

                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}

                # Call MCP tool
                try:
                    result = await mcp_client.call_tool(tool_name, arguments)
                    tool_result_content = result.content[0].text if result.content else ""
                except Exception as e:
                    tool_result_content = f"Error calling tool: {e!s}"

                tool_results.append({"tool_name": tool_name, "arguments": arguments, "result": tool_result_content})

                # Add tool response to messages
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": tool_result_content})

            interaction["tool_calls"] = tool_results
            interactions.append(interaction)

        else:
            # LLM provided final answer (no more tool calls)
            final_answer = assistant_message.content
            interaction["llm_response"] = final_answer
            interaction["final"] = True
            interactions.append(interaction)

            # Perform validation if requested
            validation = {}
            if expected_tool_calls:
                validation["expected_tools_called"] = all(tool in tools_called for tool in expected_tool_calls)
                validation["expected_tools"] = expected_tool_calls
                validation["actual_tools_called"] = tools_called

            if validate_result and expected_answer:
                # Simple string comparison (can be enhanced)
                validation["answer_matches"] = expected_answer.lower() in final_answer.lower()
                validation["expected_answer"] = expected_answer
                validation["actual_answer"] = final_answer

            return {
                "success": True,
                "llm_interactions": interactions,
                "tool_calls_made": tools_called,
                "final_answer": final_answer,
                "validation": validation if validation else None,
                "total_iterations": iteration + 1,
                "execution_time": round(time.time() - start_time, 2),
            }

    # Max iterations reached without final answer
    return {
        "success": False,
        "error": f"Max iterations ({max_iterations}) reached without final answer",
        "llm_interactions": interactions,
        "tool_calls_made": tools_called,
        "total_iterations": max_iterations,
        "execution_time": round(time.time() - start_time, 2),
    }


def main():
    module_args = dict(
        # Test configuration
        test_prompt=dict(type="str", required=True),
        # LLM configuration
        llm_provider=dict(
            type="str",
            default="ollama",
            choices=["openai", "anthropic", "ollama", "vllm", "openrouter", "azure", "bedrock", "vertex_ai", "cohere"],
        ),
        llm_model=dict(type="str", required=True),
        llm_api_key=dict(type="str", no_log=True),
        llm_base_url=dict(type="str"),
        # Validation options
        expected_tool_calls=dict(type="list", elements="str"),
        validate_result=dict(type="bool", default=False),
        expected_answer=dict(type="str"),
        max_iterations=dict(type="int", default=5),
        # MCP server connection (same as other modules)
        transport=dict(type="str", default="stdio", choices=["stdio", "sse", "http"]),
        server_command=dict(type="str"),
        server_args=dict(type="list", elements="str", default=[]),
        server_url=dict(type="str"),
        server_headers=dict(type="dict", default={}),
        timeout=dict(type="int", default=30),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        required_if=[
            ("transport", "stdio", ["server_command"]),
            ("transport", "sse", ["server_url"]),
            ("transport", "http", ["server_url"]),
            ("validate_result", True, ["expected_answer"]),
        ],
        supports_check_mode=False,
    )

    # Check for litellm
    if not HAS_LITELLM:
        module.fail_json(msg=missing_required_lib("litellm"), exception=LITELLM_IMPORT_ERROR)

    # Extract parameters
    test_prompt = module.params["test_prompt"]
    llm_provider = module.params["llm_provider"]
    llm_model = module.params["llm_model"]
    llm_api_key = module.params.get("llm_api_key")
    llm_base_url = module.params.get("llm_base_url")
    max_iterations = module.params["max_iterations"]
    expected_tool_calls = module.params.get("expected_tool_calls")
    validate_result = module.params["validate_result"]
    expected_answer = module.params.get("expected_answer")

    # MCP connection parameters
    transport = module.params["transport"]
    server_command = module.params.get("server_command")
    server_args = module.params.get("server_args", [])
    server_url = module.params.get("server_url")
    server_headers = module.params.get("server_headers", {})
    timeout = module.params["timeout"]

    # Set default base URL for Ollama
    if llm_provider == "ollama" and not llm_base_url:
        llm_base_url = "http://localhost:11434"

    # Create MCP client
    mcp_client = MCPClient(
        transport=transport,
        server_command=server_command,
        server_args=server_args,
        server_url=server_url,
        server_headers=server_headers,
        timeout=timeout,
    )

    # Run the test
    try:
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def run_test():
            async with mcp_client.connect() as connected_client:
                return await run_llm_integration_test(
                    module=module,
                    mcp_client=connected_client,
                    test_prompt=test_prompt,
                    llm_provider=llm_provider,
                    llm_model=llm_model,
                    llm_api_key=llm_api_key,
                    llm_base_url=llm_base_url,
                    max_iterations=max_iterations,
                    expected_tool_calls=expected_tool_calls,
                    validate_result=validate_result,
                    expected_answer=expected_answer,
                )

        result = loop.run_until_complete(run_test())
        loop.close()

        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=f"LLM integration test failed: {e!s}", exception=str(e))


if __name__ == "__main__":
    main()
