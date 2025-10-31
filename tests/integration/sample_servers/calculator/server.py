# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Original work from battula417/calculator-server
#
# This file is adapted from:
# Repository: https://github.com/battula417/calculator-server
# License: Educational/demonstration purposes
# Modifications: Minimal adaptations for integration testing

import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Create server instance
server = Server("example-server")


# Register tools using the list_tools handler
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="add",
            description="Add two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="calculate_sum",
            description="Calculate the sum of two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="calculate_product",
            description="Calculate the product of two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="get_server_info",
            description="Get information about this MCP server",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]


# Register tool call handler
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    if name == "add" or name == "calculate_sum":
        result = arguments["a"] + arguments["b"]
        return [TextContent(type="text", text=str(result))]

    elif name == "calculate_product":
        result = arguments["a"] * arguments["b"]
        return [TextContent(type="text", text=str(result))]

    elif name == "get_server_info":
        info = {
            "server_name": "example-stdio-server",
            "version": "1.0.0",
            "transport": "stdio",
            "capabilities": ["tools"],
        }
        return [TextContent(type="text", text=str(info))]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
