"""Test Node.js resource server with Python client - Cross-language compatibility test"""

import asyncio
import sys
from pathlib import Path

# Add module_utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "plugins" / "module_utils"))

from mcp_client import MCPClient


async def test_nodejs_resources():
    """Test Node.js resource server"""
    server_path = Path(__file__).parent / "sample_servers" / "nodejs-resources" / "dist" / "server.js"

    print(f"Testing Node.js resource server: {server_path}")
    print("This demonstrates cross-language MCP compatibility (TypeScript ↔ Python)")

    client = MCPClient(transport="stdio", server_command="node", server_args=[str(server_path)], timeout=30)

    try:
        print("\n1. Connecting to Node.js server...")
        async with client.connect() as connected_client:
            print("✓ Connected!")

            print("\n2. Listing resources...")
            resources = await connected_client.list_resources()
            print(f"✓ Found {len(resources)} resources:")
            for resource in resources:
                print(f"   - {resource.uri}: {resource.name} ({resource.mimeType})")

            print("\n3. Reading JSON resource...")
            result = await connected_client.read_resource("file://test_data/config.json")
            print(f"✓ Read {len(result.contents)} content(s)")
            if result.contents:
                print(f"   Content preview: {result.contents[0].text[:50]}...")

            print("\n4. Reading text resource...")
            result = await connected_client.read_resource("file://test_data/document.txt")
            print(f"✓ Read text: {result.contents[0].text}")

            print("\n5. Reading YAML resource...")
            result = await connected_client.read_resource("file://test_data/data.yaml")
            print(f"✓ Read YAML content ({len(result.contents[0].text)} chars)")

        print("\n✓ All Node.js cross-language tests passed!")
        print("✓ Python client successfully communicated with TypeScript MCP server!")
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_nodejs_resources())
    sys.exit(0 if success else 1)
