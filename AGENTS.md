# AGENTS.md - AI Coding Agent Guide

> **For AI coding agents working on the MCP Audit Ansible Collection**

This document provides context, conventions, and best practices specifically for AI agents (Claude Code, GitHub Copilot, Cursor, etc.) working on this Ansible collection. It complements the human-focused README.md and CONTRIBUTING.md files.

## Table of Contents
- [Project Overview](#project-overview)
- [Build & Test Commands](#build--test-commands)
- [Code Style & Standards](#code-style--standards)
- [Testing Requirements](#testing-requirements)
- [Module Architecture](#module-architecture)
- [Common Pitfalls](#common-pitfalls)
- [Security Considerations](#security-considerations)
- [Git Workflow](#git-workflow)
- [Publishing Workflow](#publishing-workflow)

---

## Project Overview

**Project**: MCP Audit Ansible Collection (`mcp.audit`)
**Purpose**: Test and audit Model Context Protocol (MCP) servers using Ansible automation
**Language**: Python 3.9+
**Framework**: Ansible Collection (ansible-core 2.15+)
**Repository**: https://github.com/tosin2013/ansible-collection-mcp-audit
**Status**: Phase 6 (RHEL Testing & Galaxy Publication) - 92% Complete

### Key Technical Context

- **Primary SDK**: MCP Python SDK >=1.19.0 (official ModelContextProtocol SDK)
- **Async Architecture**: All MCP operations use `async/await` with `asyncio.run()`
- **Transport Protocols**: stdio (primary), SSE (supported), HTTP (placeholder)
- **Testing Strategy**: Two-tier (unit + integration with real MCP servers)
- **Licensing**: GPL-3.0-or-later (modules), dual GPL/BSD (module_utils), REUSE compliant
- **Target Platforms**: RHEL 9/10, CentOS Stream 9/10, Python 3.9-3.13

### Directory Structure

```
mcp.audit/
├── plugins/
│   ├── modules/              # 6 Ansible modules (5 core + 1 LLM)
│   │   ├── mcp_server_info.py       # Capability discovery
│   │   ├── mcp_test_tool.py         # Tool invocation testing
│   │   ├── mcp_test_resource.py     # Resource retrieval testing
│   │   ├── mcp_test_prompt.py       # Prompt template testing
│   │   ├── mcp_test_suite.py        # Multi-test orchestration
│   │   └── mcp_test_llm_integration.py  # LLM integration (v1.1.0)
│   └── module_utils/          # Shared utilities (dual-licensed)
│       ├── mcp_client.py      # MCP SDK wrapper
│       ├── mcp_validator.py   # Response validation
│       └── mcp_reporter.py    # JSON/YAML reporting
├── tests/
│   ├── unit/                  # pytest unit tests
│   ├── integration/           # ansible-test integration tests
│   │   ├── sample_servers/    # Real MCP servers (3rd-party)
│   │   │   ├── calculator/    # Python stdio server (MIT)
│   │   │   ├── prompts/       # Python prompts server (MIT)
│   │   │   └── nodejs-resources/  # TypeScript resource server (MIT)
│   │   └── targets/           # Test playbooks per module
│   └── sanity/                # ansible-test ignore files
├── docs/
│   ├── adrs/                  # Architecture Decision Records (16 ADRs)
│   └── IMPLEMENTATION-PLAN.md # Current phase tracking
├── changelogs/                # antsibull-changelog fragments
├── galaxy.yml                 # Collection metadata
├── requirements.txt           # Python dependencies
├── requirements-dev.txt       # Dev dependencies
├── pyproject.toml             # ruff, mypy config
├── .ansible-lint              # ansible-lint config
├── .yamllint                  # yamllint config
├── REUSE.toml                 # License compliance config
└── .github/workflows/         # CI/CD pipelines
    ├── quality.yml            # ruff, mypy, yamllint, ansible-lint
    ├── sanity.yml             # ansible-test sanity (9 test combos)
    └── security.yml           # CodeQL, TruffleHog, Dependabot
```

---

## Build & Test Commands

### Quick Setup

```bash
# Clone and navigate to collection directory
cd /path/to/ansible_collections/mcp/audit

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # or `. venv/bin/activate` on macOS/Linux

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Code Quality Checks (Run before every commit)

```bash
# Full quality check suite
make quality

# Individual tools
ruff check .                  # Linter (auto-fixes available)
ruff format --check .         # Formatter check
mypy plugins/                 # Type checking
yamllint .                    # YAML linting
ansible-lint                  # Ansible best practices
reuse lint                    # License compliance
```

### Testing Commands

```bash
# Unit tests (fast, no MCP servers needed)
pytest tests/unit/ -v --cov=plugins

# Integration tests (requires MCP servers)
cd /private/tmp/test-collections/ansible_collections/mcp/audit
ansible-playbook tests/integration/test-runner.yml -v

# Sanity tests (Ansible collection standards)
ansible-test sanity --python 3.11 --docker default

# Test specific Python version + ansible-core version
ansible-test sanity --python 3.9 --docker default
```

### Build Collection

```bash
# Build tarball for distribution
ansible-galaxy collection build

# Install locally for testing
ansible-galaxy collection install mcp-audit-1.0.0.tar.gz --force
```

---

## Code Style & Standards

### Python Code Style

**Toolchain**: ruff (linter + formatter), mypy (type checker)

```python
# ✅ GOOD: Modern type hints, comprehensive docstrings
from typing import Any

async def connect_server(
    transport: str,
    command: str | None = None,
    args: list[str] | None = None,
) -> dict[str, Any]:
    """Connect to MCP server with specified transport.

    Args:
        transport: Transport protocol ('stdio', 'sse', 'http')
        command: Server command (required for stdio)
        args: Server command arguments

    Returns:
        dict: Connection info and server capabilities

    Raises:
        MCPConnectionError: If connection fails
        ValueError: If required parameters missing
    """
    # Implementation
```

**Common ruff Errors to Avoid**:
- `E402`: Module imports not at top (OK for Ansible modules after DOCUMENTATION)
- `I001`: Import order (ruff auto-sorts with `ruff check --fix`)
- `C408`: Unnecessary dict() call (use `{}` instead for Ansible modules)
- `UP006`: Use `list`/`dict` not `List`/`Dict` (Python 3.9+ native syntax)

### Ansible Module Pattern

**CRITICAL**: All Ansible modules MUST follow this structure:

```python
#!/usr/bin/python
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Tosin Akinosho <tosin.akinosho@gmail.com>

DOCUMENTATION = r"""
---
module: mcp_example
short_description: Brief description here
version_added: "1.0.0"
description:
  - Detailed description paragraph 1
  - Detailed description paragraph 2
author:
  - Tosin Akinosho (@tosinakinosho)
options:
  param_name:
    description:
      - Parameter description
    type: str
    required: true
"""

EXAMPLES = r"""
- name: Example task
  mcp.audit.mcp_example:
    param_name: value
"""

RETURN = r"""
result_key:
  description: What this returns
  returned: always
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule  # noqa: E402
import asyncio  # noqa: E402

async def async_main(module):
    """Async logic here - use module_utils"""
    # Implementation

def run_module():
    """Sync Ansible module entry point"""
    module = AnsibleModule(
        argument_spec=dict(
            param_name=dict(type='str', required=True),
        )
    )

    try:
        result = asyncio.run(async_main(module))
        module.exit_json(**result)
    except Exception as e:
        module.fail_json(msg=str(e))

if __name__ == '__main__':
    run_module()
```

### License Headers (REUSE Compliance)

**All files MUST have SPDX headers**:

```python
# Python files (.py)
# SPDX-FileCopyrightText: 2025 Tosin Akinosho <tosin.akinosho@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

# For module_utils (dual-licensed):
# SPDX-License-Identifier: GPL-3.0-or-later OR BSD-2-Clause

# YAML files (.yml, .yaml)
# SPDX-FileCopyrightText: 2025 Tosin Akinosho <tosin.akinosho@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

# JSON files (use REUSE.toml or comments)
# See existing patterns in tests/integration/sample_servers/
```

**REUSE Tool**:
```bash
# Check all files for compliance
reuse lint

# Add license to file
reuse annotate --license GPL-3.0-or-later --copyright "Tosin Akinosho <tosin.akinosho@gmail.com>" file.py
```

---

## Testing Requirements

### Unit Test Coverage Targets

- **Overall**: ≥80% line coverage
- **module_utils**: ≥80% (mcp_validator: 82.47%, mcp_reporter: 88.57%)
- **modules**: ≥75% (async connection logic tested in integration)

**Why mcp_client.py is 51.80% coverage**: Async connection establishment requires real MCP servers (tested in integration phase, not unit tests).

### Integration Test Structure

```yaml
# tests/integration/targets/mcp_server_info/tasks/main.yml
- name: Test server info retrieval
  mcp.audit.mcp_server_info:
    transport: stdio
    server_command: "{{ python_for_mcp_server }}"
    server_args:
      - "{{ playbook_dir }}/sample_servers/calculator/server.py"
  register: result

- name: Validate response structure
  ansible.builtin.assert:
    that:
      - result.success
      - result.server_info.server_name is defined
      - result.server_info.capabilities is defined
```

### Sanity Test Ignore Files

**IMPORTANT**: ansible-core 2.19 has STRICTER requirements than 2.15-2.17:

```txt
# tests/sanity/ignore-2.19.txt
# NO EMPTY LINES OR COMMENTS ALLOWED (they cause test failures)
tests/integration/sample_servers/prompts/server.py pylint:consider-using-from-import
tests/integration/sample_servers/nodejs-resources/src/server.ts shebang
```

**For older versions (2.15-2.17)**, you can include module-level ignores:
```txt
# tests/sanity/ignore-2.15.txt
plugins/modules/mcp_server_info.py pylint:wrong-import-position
plugins/modules/mcp_server_info.py pylint:broad-exception-caught
```

---

## Module Architecture

### Module Pattern (ADR-0003)

All modules follow this consistent pattern:

1. **DOCUMENTATION/EXAMPLES/RETURN blocks** (required by Ansible)
2. **Imports AFTER documentation** (`# noqa: E402` to suppress ruff)
3. **async helper function** (`async def async_main(module)`)
4. **sync entry point** (`def run_module()`)
5. **asyncio.run()** to bridge sync/async
6. **Exception handling** with proper Ansible `module.fail_json()`

### module_utils Integration

```python
# Always use module_utils, never call MCP SDK directly in modules
from ansible_collections.mcp.audit.plugins.module_utils.mcp_client import MCPClient
from ansible_collections.mcp.audit.plugins.module_utils.mcp_validator import MCPValidator
from ansible_collections.mcp.audit.plugins.module_utils.mcp_reporter import MCPReporter

async def async_main(module):
    client = MCPClient(module.params)
    validator = MCPValidator()
    reporter = MCPReporter()

    # Connect, validate, report
    result = await client.connect()
    validated = validator.validate(result)
    return reporter.format(validated)
```

### Transport Protocol Handling

```python
# Check transport validity BEFORE async operations
if transport == 'stdio' and not command:
    module.fail_json(msg="server_command required for stdio transport")

if transport in ['sse', 'http'] and not url:
    module.fail_json(msg="server_url required for sse/http transport")

# HTTP transport returns helpful error (not yet implemented)
if transport == 'http':
    module.fail_json(
        msg="HTTP transport not yet implemented. Use stdio or SSE.",
        implemented_transports=['stdio', 'sse']
    )
```

---

## Common Pitfalls

### 1. Python 3.13 Type Hint Errors

**Problem**: `TypeError: 'type' object is not subscriptable`

```python
# ❌ BAD (fails on Python 3.13 without future import)
def func() -> list[str]:
    pass

# ✅ GOOD (Option 1: Use __future__)
from __future__ import annotations

def func() -> list[str]:
    pass

# ✅ GOOD (Option 2: Use typing module)
from typing import List

def func() -> List[str]:
    pass
```

**Fix**: See [Issue #6](https://github.com/tosin2013/ansible-collection-mcp-audit/issues/6)

### 2. REUSE License Compliance Failures

**Problem**: `reuse lint` fails with missing headers

**8 Common Files**:
- `tests/sanity/ignore-*.txt` (no headers)
- `tests/integration/sample_servers/nodejs-resources/*.json` (no headers)
- `tests/integration/test_module_direct.json` (no header)

**Fix**: See [Issue #7](https://github.com/tosin2013/ansible-collection-mcp-audit/issues/7)

```bash
# Quick fix via REUSE.toml (preferred for data files)
[[annotations]]
path = "tests/sanity/ignore-*.txt"
SPDX-FileCopyrightText = "2025 Tosin Akinosho <tosin.akinosho@gmail.com>"
SPDX-License-Identifier = "GPL-3.0-or-later"
```

### 3. Ansible Variable Scoping for MCP Servers

**Problem**: `ansible_playbook_python` points to Ansible's Python, not venv Python

```yaml
# ❌ BAD (uses Ansible's system Python, not venv)
server_command: "{{ ansible_playbook_python }}"

# ✅ GOOD (uses current venv Python)
server_command: "{{ ansible_python_interpreter }}"
```

### 4. JSON Serialization of MCP Responses

**Problem**: `TypeError: Object of type AnyUrl is not JSON serializable`

```python
# ❌ BAD (fails on Pydantic AnyUrl, complex types)
json.dumps(mcp_response)

# ✅ GOOD (use Pydantic's mode='json')
mcp_response.model_dump(mode='json')
```

### 5. Node.js MCP Server Shebangs

**Problem**: ansible-test sanity fails: "unexpected non-module shebang"

```typescript
// ❌ BAD (for test servers, not executables)
#!/usr/bin/env node

// ✅ GOOD (remove shebang, servers are called via `node server.ts`)
// No shebang line
```

**OR** add to `tests/sanity/ignore-2.19.txt`:
```
tests/integration/sample_servers/nodejs-resources/src/server.ts shebang
```

### 6. Empty Lines in Sanity Ignore Files (ansible-core 2.19+)

**Problem**: `ERROR: Line cannot be empty or contain only a comment`

```txt
# ❌ BAD (ansible-core 2.19 rejects this)
# This is a comment

tests/file.py pylint:error-code
```

```txt
# ✅ GOOD (no empty lines, no comments in 2.19)
tests/file.py pylint:error-code
tests/other.py pylint:other-error
```

---

## Security Considerations

### 1. Credential Handling (ADR-0016: LiteLLM Integration)

```yaml
# ✅ GOOD: Use Ansible Vault for API keys
- name: Test LLM integration
  mcp.audit.mcp_test_llm_integration:
    llm_provider: openai
    llm_model: gpt-4
    llm_api_key: "{{ vault_openai_api_key }}"  # From Vault
```

**Module Implementation**:
```python
# ALWAYS mark sensitive parameters with no_log=True
argument_spec = dict(
    llm_api_key=dict(type='str', required=False, no_log=True),
)
```

### 2. No Hardcoded Secrets

```python
# ❌ BAD
api_key = "sk-proj-abcd1234"

# ✅ GOOD
api_key = module.params.get('llm_api_key')
```

### 3. Third-Party Code Attribution

All sample MCP servers in `tests/integration/sample_servers/` MUST have:
- SPDX headers with original copyright
- README.md with attribution
- Original license file preserved

```python
# Example: tests/integration/sample_servers/calculator/server.py
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Original work from battula417/calculator-server
```

---

## Git Workflow

### Commit Message Format

```
<type>: <short description>

<longer description if needed>

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `refactor`: Code restructuring
- `style`: Formatting changes
- `chore`: Build/tooling changes

**Examples**:
```bash
git commit -m "fix: Add missing SPDX headers to sanity ignore files

Files tests/sanity/ignore-*.txt were missing license headers
causing reuse lint failures. Added GPL-3.0-or-later headers.

Fixes #7

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Branch Strategy

- **main**: Stable, published versions
- **develop**: Integration branch (if needed)
- **feature/***:  Feature branches
- **fix/***:  Bugfix branches

### Pre-Commit Checklist

```bash
# 1. Run all quality checks
make quality

# 2. Run unit tests
pytest tests/unit/ -v

# 3. Check REUSE compliance
reuse lint

# 4. Stage changes
git add .

# 5. Commit with proper message
git commit -m "feat: Add new feature

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Publishing Workflow

### Release Process (for v1.0.0 and beyond)

```bash
# 1. Update version in galaxy.yml
vi galaxy.yml  # Change version: 1.0.0 → 1.1.0

# 2. Create changelog fragment
vi changelogs/fragments/1.1.0-release.yml
```

```yaml
# changelogs/fragments/1.1.0-release.yml
release_summary: |
  Release 1.1.0 adds LiteLLM integration for end-to-end testing.

major_changes:
  - Added mcp_test_llm_integration module for testing with real LLMs

minor_changes:
  - Improved error messages for connection failures
  - Updated documentation with Ollama examples
```

```bash
# 3. Generate CHANGELOG.rst
antsibull-changelog release --version 1.1.0

# 4. Build collection tarball
ansible-galaxy collection build

# 5. Test installation locally
ansible-galaxy collection install mcp-audit-1.1.0.tar.gz --force

# 6. Publish to Ansible Galaxy (requires API key)
ansible-galaxy collection publish mcp-audit-1.1.0.tar.gz --token <galaxy-token>

# 7. Create GitHub release
gh release create v1.1.0 mcp-audit-1.1.0.tar.gz \
  --title "Release 1.1.0 - LiteLLM Integration" \
  --notes-file changelogs/CHANGELOG.rst
```

### Galaxy Publishing Checklist (ADR-0014)

- [ ] `galaxy.yml` has complete metadata
- [ ] Version follows semantic versioning
- [ ] `README.md` is comprehensive
- [ ] `CHANGELOG.rst` is up to date
- [ ] All tests passing (sanity, unit, integration)
- [ ] `reuse lint` passes (100% compliance)
- [ ] Documentation reviewed (DOCUMENTATION/EXAMPLES/RETURN blocks)
- [ ] No sensitive data in repository
- [ ] GitHub release created with tarball

---

## Quick Reference

### Essential Commands

```bash
# Setup
python3 -m venv venv && . venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Quality
make quality                          # All checks
ruff check . --fix                    # Auto-fix linting
ansible-lint                          # Ansible standards

# Testing
pytest tests/unit/ -v --cov          # Unit tests
ansible-playbook tests/integration/test-runner.yml  # Integration
ansible-test sanity --python 3.11     # Sanity tests

# Build
ansible-galaxy collection build      # Create tarball

# License
reuse lint                            # Check compliance
reuse annotate --license GPL-3.0-or-later --copyright "Tosin Akinosho" file.py
```

### Key Files to Always Check

1. **`docs/IMPLEMENTATION-PLAN.md`** - Current phase status
2. **`docs/adrs/*.md`** - Architectural decisions (16 ADRs)
3. **`tests/sanity/ignore-*.txt`** - Sanity test suppressions
4. **`.github/workflows/*.yml`** - CI/CD pipeline definitions
5. **`REUSE.toml`** - Centralized license declarations

### Architecture Decision Records (ADRs)

Reference these when making architectural changes:

- **ADR-0001**: Collection namespace (`mcp.audit`)
- **ADR-0002**: MCP Python SDK (>=1.19.0)
- **ADR-0003**: Module architecture pattern
- **ADR-0004**: Transport protocols (stdio/SSE/HTTP)
- **ADR-0005**: Testing strategy (unit + integration)
- **ADR-0006**: Result reporting (JSON primary)
- **ADR-0007**: Real MCP servers for testing
- **ADR-0008**: Licensing (GPL-3.0-or-later + REUSE)
- **ADR-0011**: Code quality tools
- **ADR-0012**: CI/CD strategy
- **ADR-0013**: Version compatibility (Python 3.9+, ansible-core 2.15+)
- **ADR-0016**: LiteLLM integration (v1.1.0)

---

## Additional Resources

- **README.md**: User-facing documentation
- **CONTRIBUTING.md**: Contributor guidelines (human-focused)
- **SECURITY.md**: Vulnerability disclosure process
- **Ansible Collection Guide**: https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html
- **MCP Specification**: https://modelcontextprotocol.io/
- **REUSE Specification**: https://reuse.software/spec/

---

**Last Updated**: 2025-10-31
**Project Phase**: Phase 6 (RHEL Testing & Galaxy Publication)
**Overall Completion**: 92%
