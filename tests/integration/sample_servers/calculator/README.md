# Calculator MCP Server (Test Server)

## Attribution

This server is adapted from the calculator-server repository:

- **Original Repository**: https://github.com/battula417/calculator-server
- **Original Author**: battula417
- **License**: Educational/demonstration purposes
- **Modifications**: Minimal adaptations for Ansible integration testing

## Description

This is a simple MCP server that provides calculator tools for testing the MCP Audit Ansible Collection. It implements basic arithmetic operations using the stdio transport.

## Available Tools

- `add` - Add two numbers
- `calculate_sum` - Calculate the sum of two numbers (same as add)
- `calculate_product` - Calculate the product of two numbers
- `get_server_info` - Get server information

## Usage

This server is used by the integration tests and should not be run manually. It is spawned by Ansible playbooks during testing.

## Requirements

- Python 3.9+
- mcp Python SDK (see requirements.txt)
