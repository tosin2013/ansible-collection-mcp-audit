# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 The MCP Audit Ansible Collection Contributors
#
# Custom resource server for MCP Audit integration testing

from __future__ import annotations

import asyncio

import mcp.server.stdio
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.types import ReadResourceResult, Resource, TextResourceContents

server = Server("resource-test-server")


@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="file://test_data/config.json",
            name="Test Config",
            mimeType="application/json",
            description="Test configuration file",
        ),
        Resource(
            uri="file://test_data/document.txt",
            name="Test Document",
            mimeType="text/plain",
            description="Test text document",
        ),
        Resource(
            uri="file://test_data/data.yaml",
            name="Test YAML Data",
            mimeType="application/x-yaml",
            description="Test YAML data file",
        ),
    ]


@server.read_resource()
async def read_resource(uri: str) -> ReadResourceResult:
    """Read resource content"""
    if uri == "file://test_data/config.json":
        return ReadResourceResult(
            contents=[
                TextResourceContents(
                    uri=uri,
                    mimeType="application/json",
                    text='{"environment": "test", "enabled": true, "version": "1.0.0"}',
                )
            ]
        )
    elif uri == "file://test_data/document.txt":
        return ReadResourceResult(
            contents=[
                TextResourceContents(
                    uri=uri, mimeType="text/plain", text="This is a test document for MCP resource testing."
                )
            ]
        )
    elif uri == "file://test_data/data.yaml":
        return ReadResourceResult(
            contents=[
                TextResourceContents(
                    uri=uri,
                    mimeType="application/x-yaml",
                    text="test:\n  key: value\n  items:\n    - item1\n    - item2\n",
                )
            ]
        )
    else:
        raise ValueError(f"Resource not found: {uri}")


async def run():
    # Run the server as STDIO
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="resource-test",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(run())
