# Resource MCP Server (Test Server)

## Attribution

This is a custom server created for the MCP Audit Ansible Collection.

- **License**: GPL-3.0-or-later
- **Copyright**: 2025 The MCP Audit Ansible Collection Contributors

## Description

This is a custom MCP server that provides resource capabilities for testing the MCP Audit Ansible Collection. It serves test resources in various formats (JSON, text, YAML) using the stdio transport.

## Available Resources

- `file://test_data/config.json` - Test JSON configuration (application/json)
- `file://test_data/document.txt` - Test text document (text/plain)
- `file://test_data/data.yaml` - Test YAML data (application/x-yaml)

## Usage

This server is used by the integration tests and should not be run manually. It is spawned by Ansible playbooks during testing.

## Requirements

- Python 3.9+
- mcp Python SDK (see requirements.txt)
