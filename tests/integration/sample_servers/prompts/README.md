# Prompt MCP Server (Test Server)

## Attribution

This server is adapted from the mcp-examples repository:

- **Original Repository**: https://github.com/jamesdhope/mcp-examples
- **Original Author**: jamesdhope
- **License**: MIT (assumed)
- **Modifications**: Simplified for stdio-only integration testing

## Description

This is a simple MCP server that provides prompt templates for testing the MCP Audit Ansible Collection. It implements various prompt patterns using the stdio transport.

## Available Prompts

- `test-prompt` - A test prompt with context and topic arguments
  - Arguments: `context` (optional), `topic` (required)
- `simple-prompt` - A simple prompt without arguments

## Usage

This server is used by the integration tests and should not be run manually. It is spawned by Ansible playbooks during testing.

## Requirements

- Python 3.9+
- mcp Python SDK (see requirements.txt)
