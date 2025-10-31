"""
Test to debug the litellm tool calling loop issue
"""

import json

from litellm import completion


def test_litellm_loop():
    """Test litellm with Ollama in a loop to see if it provides final answer"""

    # Define tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculate_sum",
                "description": "Calculate the sum of two numbers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "First number"},
                        "b": {"type": "number", "description": "Second number"},
                    },
                    "required": ["a", "b"],
                },
            },
        }
    ]

    messages = [{"role": "user", "content": "Calculate the sum of 15 and 27"}]

    print("Starting test...")
    print()

    for i in range(5):
        print(f"=== Iteration {i + 1} ===")
        print(f"Sending {len(messages)} messages to LLM")

        # Call LLM
        response = completion(model="ollama/phi3.5", messages=messages, tools=tools, api_base="http://localhost:11434")

        assistant_message = response.choices[0].message

        # Check if LLM wants to call tools
        if hasattr(assistant_message, "tool_calls") and assistant_message.tool_calls:
            print(f"LLM wants to call {len(assistant_message.tool_calls)} tool(s)")

            # Build tool_calls list for message history
            tool_calls_list = []
            for tool_call in assistant_message.tool_calls:
                print(f"  - {tool_call.function.name}({tool_call.function.arguments})")
                tool_calls_list.append(
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {"name": tool_call.function.name, "arguments": tool_call.function.arguments},
                    }
                )

            # Add assistant message with tool calls
            messages.append({"role": "assistant", "content": None, "tool_calls": tool_calls_list})

            # Execute tools and add results
            for tool_call in assistant_message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                result = args["a"] + args["b"]  # Simulate tool execution
                print(f"  Tool result: {result}")

                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(result)})

            print()
        else:
            # LLM provided final answer
            print(f"LLM final answer: {assistant_message.content}")
            return True

    print("Max iterations reached without final answer!")
    print()
    print("Final message history:")
    for i, msg in enumerate(messages):
        print(f"{i + 1}. {msg.get('role')}: {msg.get('content', '[tool_calls]')[:100]}")

    return False


if __name__ == "__main__":
    success = test_litellm_loop()
    if success:
        print("\n✓ Test passed!")
    else:
        print("\n✗ Test failed - LLM stuck in loop")
