# Ansible Collection - mcp.audit

[![Code Quality](https://github.com/tosin2013/ansible-collection-mcp-audit/actions/workflows/quality.yml/badge.svg)](https://github.com/tosin2013/ansible-collection-mcp-audit/actions/workflows/quality.yml)
[![Ansible Sanity](https://github.com/tosin2013/ansible-collection-mcp-audit/actions/workflows/sanity.yml/badge.svg)](https://github.com/tosin2013/ansible-collection-mcp-audit/actions/workflows/sanity.yml)
[![Security](https://github.com/tosin2013/ansible-collection-mcp-audit/actions/workflows/security.yml/badge.svg)](https://github.com/tosin2013/ansible-collection-mcp-audit/actions/workflows/security.yml)
[![License](https://img.shields.io/badge/License-GPL%203.0%20or%20later-blue.svg)](COPYING)
[![REUSE status](https://api.reuse.software/badge/github.com/tosin2013/ansible-collection-mcp-audit)](https://api.reuse.software/info/github.com/tosin2013/ansible-collection-mcp-audit)

Ansible collection for testing and auditing [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) servers. Provides comprehensive modules to verify MCP server implementations, test tools, resources, and prompts with detailed reporting capabilities.

## Features

- **Server Discovery**: Gather comprehensive information about MCP server capabilities
- **Tool Testing**: Invoke and validate individual MCP tools with expected results
- **Resource Testing**: Retrieve and verify MCP resources with content validation
- **Prompt Testing**: Test prompt templates with argument validation
- **Test Suites**: Orchestrate multiple tests with comprehensive reporting
- **LLM Integration**: End-to-end testing with real LLMs via LiteLLM (100+ providers supported)
- **Multi-Transport**: Support for stdio, SSE (Server-Sent Events), and HTTP transports
- **Cross-Language**: Tested with Python and TypeScript MCP servers
- **RHEL Ready**: Compatible with RHEL 9/10, Python 3.9-3.13, ansible-core 2.15-2.17

## Installation

### From Ansible Galaxy (Coming Soon)

```bash
ansible-galaxy collection install mcp.audit
```

### From Source

```bash
# Clone the repository
git clone https://github.com/tosin2013/ansible-collection-mcp-audit.git
cd ansible-collection-mcp-audit

# Install dependencies
pip install -r requirements.txt

# Build the collection
ansible-galaxy collection build

# Install locally
ansible-galaxy collection install mcp-audit-*.tar.gz
```

## Requirements

- **Python**: 3.9 or later
- **Ansible**: ansible-core 2.15.0 or later
- **MCP Python SDK**: 1.19.0 or later (automatically installed)
- **Operating Systems**: Linux (RHEL 9+, Ubuntu 20.04+, Debian 11+), macOS 11+

## Quick Start

### Test an MCP Server

```yaml
---
- name: Test MCP Server
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Get server information
      mcp.audit.mcp_server_info:
        transport: stdio
        server_command: python -m mcp_server_example
      register: server_info

    - name: Display capabilities
      ansible.builtin.debug:
        var: server_info.capabilities
```

### Run a Tool Test

```yaml
- name: Test calculator add tool
  mcp.audit.mcp_test_tool:
    transport: stdio
    server_command: python -m calculator_mcp_server
    tool_name: add
    tool_arguments:
      a: 5
      b: 3
    expected_result:
      result: 8
  register: tool_test

- name: Check test passed
  ansible.builtin.assert:
    that:
      - tool_test.success
      - tool_test.test_passed
```

## Modules

### Core Modules

| Module | Description | Status |
|--------|-------------|--------|
| `mcp_server_info` | Discover server capabilities and metadata | ✅ Available |
| `mcp_test_tool` | Test individual MCP tools | ✅ Available |
| `mcp_test_resource` | Test MCP resources | ✅ Available |
| `mcp_test_prompt` | Test MCP prompts | ✅ Available |
| `mcp_test_suite` | Run comprehensive test suites | ✅ Available |
| `mcp_test_llm_integration` | End-to-end testing with real LLMs | ✅ Available |

### Transport Support

- **stdio**: Process-based communication (default)
- **SSE**: Server-Sent Events over HTTP
- **HTTP**: Direct HTTP/HTTPS communication

## Documentation

- **[Installation Guide](docs/installation.md)** (Coming Soon)
- **[Module Documentation](docs/modules/)** (Coming Soon)
- **[Examples](docs/examples/)** (Coming Soon)
- **[Architectural Decision Records](docs/adrs/README.md)**
- **[Security Policy](SECURITY.md)** (Coming Soon)
- **[Contributing Guidelines](CONTRIBUTING.md)** (Coming Soon)

## Development

### Setup Development Environment

```bash
# Clone and enter directory
git clone https://github.com/tosin2013/ansible-collection-mcp-audit.git
cd ansible-collection-mcp-audit

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Run Quality Checks

```bash
# Run all quality checks
make quality

# Run individual checks
make lint        # Linting (ruff, yamllint, ansible-lint)
make format      # Code formatting (ruff)
make type-check  # Type checking (mypy)
make test        # Unit tests (pytest)
```

### Run Ansible Sanity Tests

```bash
ansible-test sanity --docker
```

## Architecture

This collection follows Ansible best practices and is built on solid architectural decisions:

- **[ADR-0001](docs/adrs/0001-collection-namespace-selection.md)**: Collection namespace (`mcp.audit`)
- **[ADR-0002](docs/adrs/0002-mcp-python-sdk-selection.md)**: MCP Python SDK selection
- **[ADR-0003](docs/adrs/0003-module-architecture-pattern.md)**: Module architecture pattern
- **[ADR-0008](docs/adrs/0008-licensing-strategy.md)**: Licensing strategy (GPL-3.0-or-later)
- **[All ADRs](docs/adrs/README.md)**: Complete architectural decisions

## License

This collection is licensed under the **GNU General Public License v3.0 or later** (GPL-3.0-or-later).

- **Modules** (`plugins/modules/`): GPL-3.0-or-later only
- **Module utilities** (`plugins/module_utils/`): Dual-licensed GPL-3.0-or-later OR BSD-2-Clause

See [COPYING](COPYING) for the full GPL-3.0 license text and [LICENSES/](LICENSES/) for all license files.

This collection is [REUSE compliant](https://reuse.software/).

## Security

Security is a top priority. Please report security vulnerabilities privately:

- **Preferred**: Use [GitHub Security Advisories](https://github.com/tosin2013/ansible-collection-mcp-audit/security/advisories/new)
- **Email**: tosin.akinosho@gmail.com (Subject: `[SECURITY] MCP Audit Collection`)

See [SECURITY.md](SECURITY.md) for our complete security policy and response timelines.

## Contributing

Contributions are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md) (coming soon) for:

- Code of Conduct
- Development workflow
- Pull request process
- Testing requirements
- Code quality standards

## Support

- **Issues**: [GitHub Issues](https://github.com/tosin2013/ansible-collection-mcp-audit/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tosin2013/ansible-collection-mcp-audit/discussions)
- **Documentation**: [GitHub Wiki](https://github.com/tosin2013/ansible-collection-mcp-audit/wiki) (coming soon)

## Roadmap

### Version 1.0.0 (Target: Q1 2025)

- ✅ Architectural foundation (Phase 0) - **COMPLETE**
- ✅ Infrastructure setup (Phase 1) - **COMPLETE**
- ✅ Module utilities development (Phase 2) - **COMPLETE**
- ✅ Core modules implementation (Phase 3) - **COMPLETE**
- ✅ Integration testing (Phase 4) - **COMPLETE**
- 🚧 Documentation and examples (Phase 5) - **IN PROGRESS**
- ⏳ Galaxy publication (Phase 6)

### Version 1.1.0 (Released: 2025-10-30)

- ✅ LiteLLM integration (Phase 8) - **COMPLETE**
- ✅ End-to-end LLM → MCP tool → Result flow validated
- ✅ Multi-provider support (Ollama, OpenRouter, vLLM, 100+ providers)
- ✅ Secure credential management with Ansible Vault

**Current Status**: 85% complete, preparing for Galaxy publication

See [IMPLEMENTATION-PLAN.md](docs/IMPLEMENTATION-PLAN.md) for the complete roadmap.

## Credits

- **Maintainer**: Tosin Akinosho ([@tosin2013](https://github.com/tosin2013))
- **MCP Protocol**: [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic
- **MCP Python SDK**: [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)

## Links

- **Repository**: https://github.com/tosin2013/ansible-collection-mcp-audit
- **Ansible Galaxy**: https://galaxy.ansible.com/mcp/audit (coming soon)
- **Model Context Protocol**: https://modelcontextprotocol.io/
- **MCP Python SDK**: https://github.com/modelcontextprotocol/python-sdk

---

**Status**: 🚀 Ready for Documentation and Galaxy Publication (85% Complete)
**Version**: 1.0.0-dev
**Last Updated**: 2025-10-30
