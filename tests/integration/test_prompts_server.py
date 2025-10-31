"""Test prompts server"""

import asyncio
import sys
from pathlib import Path

# Add module_utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "plugins" / "module_utils"))

from mcp_client import MCPClient


async def test_prompts():
    """Test prompts server"""
    server_path = Path(__file__).parent / "sample_servers" / "prompts" / "server.py"
    python_path = "/Users/tosinakinosho/workspaces/ansible-collection-mcp-audit/venv/bin/python"

    print(f"Testing prompts server: {server_path}")

    client = MCPClient(transport="stdio", server_command=python_path, server_args=[str(server_path)], timeout=30)

    try:
        print("\n1. Connecting...")
        async with client.connect() as connected_client:
            print("✓ Connected!")

            print("\n2. Listing prompts...")
            prompts = await connected_client.list_prompts()
            print(f"✓ Found {len(prompts)} prompts:")
            for prompt in prompts:
                print(f"   - {prompt.name}: {prompt.description}")

            print("\n3. Getting simple prompt...")
            result = await connected_client.get_prompt("simple-prompt")
            print(f"✓ Result: {result}")

        print("\n✓ All tests passed!")
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_prompts())
    sys.exit(0 if success else 1)
