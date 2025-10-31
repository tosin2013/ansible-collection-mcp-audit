<!--
SPDX-FileCopyrightText: 2025 Tosin Akinosho <tosin.akinosho@gmail.com>
SPDX-License-Identifier: GPL-3.0-or-later
-->

# Contributing to MCP Audit Ansible Collection

Thank you for your interest in contributing to the MCP Audit Ansible Collection! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [Development Workflow](#development-workflow)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Documentation Guidelines](#documentation-guidelines)
- [Licensing Requirements](#licensing-requirements)
- [Community Guidelines](#community-guidelines)

## Code of Conduct

This project adheres to the [Ansible Community Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python 3.9 or later** (3.11 recommended for development)
- **Git** for version control
- **Ansible** (ansible-core 2.15.0 or later)
- Basic understanding of:
  - Ansible module development
  - Model Context Protocol (MCP)
  - Python async/await patterns

### Finding Work

1. Browse [open issues](https://github.com/tosin2013/ansible-collection-mcp-audit/issues)
2. Look for issues labeled `good-first-issue` or `help-wanted`
3. Check the [roadmap in IMPLEMENTATION-PLAN.md](docs/IMPLEMENTATION-PLAN.md)
4. Propose new features by opening an issue first

## Development Environment Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/ansible-collection-mcp-audit.git
cd ansible-collection-mcp-audit

# Add upstream remote
git remote add upstream https://github.com/tosin2013/ansible-collection-mcp-audit.git
```

### 2. Create Python Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip
```

### 3. Install Dependencies

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install runtime dependencies
pip install -r requirements.txt
```

### 4. Install Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files (optional)
pre-commit run --all-files
```

### 5. Verify Installation

```bash
# Run quality checks
make quality

# Run unit tests
make test
```

## Development Workflow

### 1. Create a Branch

```bash
# Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# Create a feature branch
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code following the [Code Style Guidelines](#code-style-guidelines)
- Add tests for new functionality
- Update documentation as needed
- Run quality checks frequently: `make quality`

### 3. Commit Changes

```bash
# Stage changes
git add .

# Commit with a descriptive message
git commit -m "Add feature: brief description

Detailed explanation of what changed and why.

Fixes #123"
```

**Commit Message Format:**
- Use present tense ("Add feature" not "Added feature")
- First line: Brief summary (50 chars or less)
- Blank line, then detailed description
- Reference issues with `Fixes #123` or `Relates to #456`

### 4. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## Code Style Guidelines

This project follows strict code quality standards. See [ADR-0011: Code Quality Tools](docs/adrs/0011-code-quality-tools.md) for details.

### Python Code Style

**Formatter and Linter: ruff**

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Auto-fix issues
ruff check --fix .
```

**Configuration:** `pyproject.toml`

**Rules:**
- Line length: 120 characters
- Import sorting: isort style
- Docstring style: Google style
- Type hints required for all functions

### Type Checking: mypy

```bash
# Run type checking
mypy plugins/
```

**Configuration:** `pyproject.toml`

**Requirements:**
- All functions must have type hints
- Use `typing` module for complex types
- Avoid `Any` type where possible

### YAML Style: yamllint

```bash
# Lint YAML files
yamllint .
```

**Configuration:** `.yamllint`

### Ansible Style: ansible-lint

```bash
# Lint Ansible content
ansible-lint
```

**Configuration:** `.ansible-lint`

**Profile:** Production profile required

### License Compliance: REUSE

```bash
# Check license compliance
reuse lint
```

**Requirements:**
- All files must have SPDX license headers
- See [Licensing Requirements](#licensing-requirements)

### Running All Checks

```bash
# Run all quality checks at once
make quality
```

## Testing Requirements

### Unit Tests (Required)

**Framework:** pytest

```bash
# Run all unit tests
pytest tests/unit/

# Run specific test file
pytest tests/unit/plugins/module_utils/test_mcp_client.py

# Run with coverage
pytest tests/unit/ --cov --cov-report=term-missing
```

**Requirements:**
- All new code must have unit tests
- Target coverage: 80% or higher
- Test files: `tests/unit/plugins/`
- Use `pytest-asyncio` for async tests
- Mock external dependencies

**Example:**

```python
import pytest
from unittest.mock import Mock, patch
from ansible_collections.mcp.audit.plugins.module_utils.mcp_client import MCPClient

def test_client_initialization():
    """Test MCPClient initialization with stdio transport"""
    client = MCPClient(transport='stdio', server_command='python')
    assert client.transport == 'stdio'

@pytest.mark.asyncio
async def test_connect_success():
    """Test successful connection to MCP server"""
    # Your async test here
    pass
```

### Integration Tests (Encouraged)

**Framework:** ansible-test

```bash
# Run integration tests
cd tests/integration
ANSIBLE_COLLECTIONS_PATH=/Users/tosinakinosho/workspaces/ansible-collection-mcp-audit:~/.ansible/collections:/usr/share/ansible/collections ansible-playbook test-runner.yml
```

**Requirements:**
- Test against real MCP servers
- Verify all transport types (stdio, SSE)
- Test error handling
- See [ADR-0007](docs/adrs/0007-real-mcp-servers-for-integration-testing.md)

### Ansible Sanity Tests (Required)

```bash
# Build collection
ansible-galaxy collection build

# Install collection
ansible-galaxy collection install mcp-audit-*.tar.gz

# Run sanity tests
ansible-test sanity --docker
```

**Requirements:**
- All sanity tests must pass
- Production profile required
- DOCUMENTATION, EXAMPLES, RETURN blocks required

## Pull Request Process

### Before Submitting

1. ✅ All tests pass: `make test`
2. ✅ Code quality checks pass: `make quality`
3. ✅ Documentation updated
4. ✅ CHANGELOG fragment added (if applicable)
5. ✅ Commits are clean and well-described

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement

## Related Issues
Fixes #123
Relates to #456

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] CHANGELOG fragment added (if needed)
- [ ] License headers correct
```

### Review Process

1. **Automated Checks:** CI/CD runs automatically
   - Code quality (ruff, mypy, yamllint, ansible-lint)
   - Unit tests
   - Ansible sanity tests
   - Security scans (CodeQL, Dependabot)

2. **Code Review:** Maintainers review for:
   - Code quality and style
   - Test coverage
   - Documentation completeness
   - Architectural alignment

3. **Approval:** At least one maintainer approval required

4. **Merge:** Maintainer merges after approval

### After Merge

- Your contribution will be included in the next release
- CHANGELOG will be updated
- Contributors will be recognized

## Issue Reporting

### Bug Reports

**Use the bug report template:**

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Run playbook with...
2. Use module...
3. Observe error...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Collection version: 1.0.0
- Ansible version: 2.16.0
- Python version: 3.11
- OS: RHEL 9

## Additional Context
Logs, screenshots, etc.
```

### Feature Requests

**Use the feature request template:**

```markdown
## Feature Description
Clear description of the feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should this work?

## Alternatives Considered
Other approaches you've thought about

## Additional Context
Examples, mockups, etc.
```

### Security Issues

**DO NOT open public issues for security vulnerabilities!**

See [SECURITY.md](SECURITY.md) for reporting instructions.

## Documentation Guidelines

### Module Documentation (Required)

All modules must include:

**DOCUMENTATION Block:**
```python
DOCUMENTATION = r'''
---
module: mcp_test_tool
short_description: Test individual MCP tools
description:
  - Tests a specific MCP tool by invoking it with provided arguments
  - Validates the tool response against expected results
  - Reports detailed test results
options:
  server_command:
    description: Command to start the MCP server
    type: str
    required: true
  # ... more options
'''
```

**EXAMPLES Block:**
```python
EXAMPLES = r'''
- name: Test calculator add tool
  mcp.audit.mcp_test_tool:
    transport: stdio
    server_command: python
    server_args:
      - /path/to/server.py
    tool_name: add
    tool_arguments:
      a: 5
      b: 3
  register: result
'''
```

**RETURN Block:**
```python
RETURN = r'''
success:
  description: Whether the test completed successfully
  type: bool
  returned: always
# ... more return values
'''
```

### README and Documentation

- Update README.md for user-facing changes
- Add examples to `docs/examples/` if applicable
- Update IMPLEMENTATION-PLAN.md for major features
- Create ADRs for architectural decisions

### Docstrings (Required)

Use Google-style docstrings:

```python
def connect_to_server(server_command: str, transport: str = 'stdio') -> dict:
    """Connect to an MCP server.

    Args:
        server_command: Command to start the MCP server
        transport: Transport protocol to use (stdio, sse, http)

    Returns:
        Dictionary containing connection status and server info

    Raises:
        MCPConnectionError: If connection fails

    Example:
        >>> result = connect_to_server('python server.py')
        >>> print(result['connected'])
        True
    """
    pass
```

## Licensing Requirements

This project is dual-licensed. See [ADR-0008: Licensing Strategy](docs/adrs/0008-licensing-strategy.md).

### License Headers

**Modules** (`plugins/modules/`): GPL-3.0-or-later only

```python
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2025 Tosin Akinosho <tosin.akinosho@gmail.com>
```

**Module Utils** (`plugins/module_utils/`): Dual-licensed

```python
# SPDX-License-Identifier: GPL-3.0-or-later OR BSD-2-Clause
# Copyright (c) 2025 Tosin Akinosho <tosin.akinosho@gmail.com>
```

### REUSE Compliance

```bash
# Verify license compliance
reuse lint

# Should show: 100% compliance
```

### Contributor License Agreement

By contributing, you agree that:
- Your contributions will be licensed under GPL-3.0-or-later
- Module utils may be dual-licensed GPL-3.0-or-later OR BSD-2-Clause
- You have the right to license your contributions

## Community Guidelines

### Communication Channels

- **GitHub Issues:** Bug reports, feature requests
- **GitHub Discussions:** Questions, ideas, community support
- **Pull Requests:** Code contributions

### Best Practices

1. **Be Respectful:** Treat everyone with respect
2. **Be Patient:** Maintainers are volunteers
3. **Be Helpful:** Help other contributors
4. **Be Clear:** Communicate clearly and concisely
5. **Be Open:** Be open to feedback

### Response Times

- **Issues:** Initial response within 5 business days
- **Pull Requests:** Initial review within 7 business days
- **Security Issues:** Initial response within 48 hours

### Recognition

Contributors are recognized in:
- CHANGELOG.rst for each release
- GitHub contributors page
- Special mentions for significant contributions

## Additional Resources

### Documentation

- [README.md](README.md) - Project overview
- [IMPLEMENTATION-PLAN.md](docs/IMPLEMENTATION-PLAN.md) - Project roadmap
- [ADRs](docs/adrs/README.md) - Architectural decisions
- [SECURITY.md](SECURITY.md) - Security policy

### External Resources

- [Ansible Collection Development Guide](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html)
- [Ansible Module Development](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

### Contact

- **Issues:** [GitHub Issues](https://github.com/tosin2013/ansible-collection-mcp-audit/issues)
- **Discussions:** [GitHub Discussions](https://github.com/tosin2013/ansible-collection-mcp-audit/discussions)
- **Security:** See [SECURITY.md](SECURITY.md)

---

**Thank you for contributing to the MCP Audit Ansible Collection!** 🎉

Your contributions help make MCP testing easier for the entire Ansible community.
