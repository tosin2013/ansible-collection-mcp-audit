# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Original work from jamesdhope/mcp-examples
#
# This file is adapted from:
# Repository: https://github.com/jamesdhope/mcp-examples
# License: MIT (assumed)
# Modifications: Simplified for stdio-only integration testing

from __future__ import annotations

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Create a server instance
server = Server("prompt-test-server")


# Add prompt capabilities
@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    return [
        types.Prompt(
            name="test-prompt",
            description="A test prompt template with arguments",
            arguments=[
                types.PromptArgument(name="context", description="Context for the prompt", required=False),
                types.PromptArgument(name="topic", description="Specific topic to focus on", required=True),
            ],
        ),
        types.Prompt(name="simple-prompt", description="A simple prompt without arguments", arguments=[]),
    ]


@server.get_prompt()
async def handle_get_prompt(name: str, arguments: dict[str, str] | None) -> types.GetPromptResult:
    if name == "test-prompt":
        if arguments is None:
            arguments = {}

        context = arguments.get("context", "")
        topic = arguments.get("topic", "general")

        messages = []
        if context:
            messages.append(
                types.PromptMessage(role="user", content=types.TextContent(type="text", text=f"Context: {context}"))
            )

        messages.append(
            types.PromptMessage(role="user", content=types.TextContent(type="text", text=f"Please help with: {topic}"))
        )

        return types.GetPromptResult(description="Test prompt with context and topic", messages=messages)

    elif name == "simple-prompt":
        return types.GetPromptResult(
            description="Simple prompt without arguments",
            messages=[
                types.PromptMessage(role="user", content=types.TextContent(type="text", text="This is a simple prompt"))
            ],
        )

    else:
        raise ValueError(f"Unknown prompt: {name}")


async def run():
    # Run the server as STDIO
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="prompt-test",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
