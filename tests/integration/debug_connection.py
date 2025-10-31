#!/usr/bin/env python3
"""Debug script to test MCP server connection"""

import asyncio
import sys
from pathlib import Path

# Add module_utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "plugins" / "module_utils"))

from mcp_client import MCPClient, MCPConnectionError


async def test_connection():
    """Test MCP server connection"""
    server_path = Path(__file__).parent / "sample_servers" / "calculator" / "server.py"
    python_path = "/Users/tosinakinosho/workspaces/ansible-collection-mcp-audit/venv/bin/python"

    print(f"Testing connection to: {server_path}")
    print(f"Using Python: {python_path}")

    client = MCPClient(transport="stdio", server_command=python_path, server_args=[str(server_path)], timeout=30)

    try:
        print("\n1. Attempting to connect...")
        async with client.connect() as connected_client:
            print("✓ Connected successfully!")

            print("\n2. Getting server info...")
            info = await connected_client.get_server_info()
            print(f"✓ Server info: {info}")

            print("\n3. Listing tools...")
            tools = await connected_client.list_tools()
            print(f"✓ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool.name}: {tool.description}")

            print("\n4. Calling 'add' tool...")
            result = await connected_client.call_tool("add", {"a": 5, "b": 3})
            print(f"✓ Result: {result}")

        print("\n✓ All tests passed!")
        return True

    except MCPConnectionError as e:
        print(f"\n✗ Connection error: {e}")
        import traceback

        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
