"""Test resources server"""

import asyncio
import sys
from pathlib import Path

# Add module_utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "plugins" / "module_utils"))

from mcp_client import MCPClient


async def test_resources():
    """Test resources server"""
    server_path = Path(__file__).parent / "sample_servers" / "resources" / "server.py"
    python_path = "/Users/tosinakinosho/workspaces/ansible-collection-mcp-audit/venv/bin/python"

    print(f"Testing resources server: {server_path}")

    client = MCPClient(transport="stdio", server_command=python_path, server_args=[str(server_path)], timeout=30)

    try:
        print("\n1. Connecting...")
        async with client.connect() as connected_client:
            print("✓ Connected!")

            print("\n2. Listing resources...")
            resources = await connected_client.list_resources()
            print(f"✓ Found {len(resources)} resources:")
            for resource in resources:
                print(f"   - {resource.uri}: {resource.name}")

            print("\n3. Reading first resource...")
            result = await connected_client.read_resource("file://test_data/config.json")
            print(f"✓ Result: {result}")

        print("\n✓ All tests passed!")
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_resources())
    sys.exit(0 if success else 1)
