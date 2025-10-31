"""
Quick test to validate litellm works with local Ollama
"""

from litellm import completion


def test_ollama_basic():
    """Test basic Ollama completion"""
    print("Testing litellm with Ollama...")
    print("Using model: phi3.5")

    try:
        response = completion(
            model="ollama/phi3.5",
            messages=[{"role": "user", "content": "What is 2+2? Answer with just the number."}],
            api_base="http://localhost:11434",
        )

        print(f"✓ Response: {response.choices[0].message.content}")
        print(f"✓ Model: {response.model}")
        print(f"✓ Tokens used: {response.usage.total_tokens if hasattr(response.usage, 'total_tokens') else 'N/A'}")
        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_ollama_with_tools():
    """Test Ollama with tool calling (function calling)"""
    print("\nTesting litellm with Ollama + tool calling...")

    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculate_sum",
                "description": "Add two numbers together",
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

    try:
        response = completion(
            model="ollama/phi3.5",
            messages=[{"role": "user", "content": "Use the calculate_sum function to add 15 and 27"}],
            tools=tools,
            api_base="http://localhost:11434",
        )

        print(f"✓ Response: {response.choices[0].message}")

        # Check if tool was called
        if hasattr(response.choices[0].message, "tool_calls") and response.choices[0].message.tool_calls:
            print(f"✓ Tool called: {response.choices[0].message.tool_calls[0].function.name}")
            print(f"✓ Arguments: {response.choices[0].message.tool_calls[0].function.arguments}")
        else:
            print("Note: Model did not call tool (this is OK, phi3.5 may not support function calling)")
            print(f"  Text response: {response.choices[0].message.content}")

        return True

    except Exception as e:
        print(f"Tool calling test note: {e}")
        print("  (Function calling support varies by model)")
        return True  # Not a failure - just informational


if __name__ == "__main__":
    print("=" * 60)
    print("LiteLLM + Ollama Integration Test")
    print("=" * 60)

    # Test 1: Basic completion
    success1 = test_ollama_basic()

    # Test 2: Tool calling (may not be supported by all models)
    success2 = test_ollama_with_tools()

    print("\n" + "=" * 60)
    if success1:
        print("✓ LiteLLM + Ollama integration verified!")
        print("✓ Ready to build mcp_test_llm_integration module")
    else:
        print("✗ LiteLLM + Ollama integration failed")
        print("  Please check that Ollama is running: ollama serve")
    print("=" * 60)
