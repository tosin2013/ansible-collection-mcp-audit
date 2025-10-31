#!/usr/bin/env python3
"""Debug script to test MCP connection using Ansible pattern"""

import asyncio
import sys
from pathlib import Path

# Add module_utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "plugins" / "module_utils"))

from mcp_client import MCPClient, MCPConnectionError, create_mcp_client


async def get_server_info_async(client: MCPClient) -> dict:
    """Test async function like in mcp_server_info module"""
    async with client.connect():
        info = await client.get_server_info()

        # Also try to get available capabilities
        try:
            tools = await client.list_tools()
            info["available_tools"] = len(tools)
        except Exception:
            info["available_tools"] = None

        try:
            resources = await client.list_resources()
            info["available_resources"] = len(resources)
        except Exception:
            info["available_resources"] = None

        try:
            prompts = await client.list_prompts()
            info["available_prompts"] = len(prompts)
        except Exception:
            info["available_prompts"] = None

        return info


def test_ansible_pattern():
    """Test using the same pattern as Ansible module"""
    server_path = Path(__file__).parent / "sample_servers" / "calculator" / "server.py"
    python_path = "/Users/tosinakinosho/workspaces/ansible-collection-mcp-audit/venv/bin/python"

    print(f"Testing Ansible pattern connection to: {server_path}")
    print(f"Using Python: {python_path}")

    # Simulate module.params
    module_params = {
        "transport": "stdio",
        "server_command": python_path,
        "server_args": [str(server_path)],
        "timeout": 30,
    }

    try:
        print("\n1. Creating MCP client using factory function...")
        client = create_mcp_client(module_params)
        print("✓ Client created")

        print("\n2. Running async function using asyncio.run() (Ansible pattern)...")
        server_info = asyncio.run(get_server_info_async(client))
        print(f"✓ Server info retrieved: {server_info}")

        print("\n✓ Ansible pattern test passed!")
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
    success = test_ansible_pattern()
    sys.exit(0 if success else 1)
