# ADR-0005: Testing Strategy

## Status
Accepted

## Context
The collection requires comprehensive testing to ensure reliability and correctness. As an Ansible collection that tests other systems (MCP servers), the testing strategy is particularly critical.

Testing considerations:
- Unit testing for module logic and utilities
- Integration testing with real MCP servers
- Mock-based testing for SDK interactions
- CI/CD pipeline integration
- Test coverage requirements
- Testing different transport types

## Decision
We will implement a **two-tier testing strategy**:

1. **Unit Tests** (`tests/unit/`)
   - Mock-based tests for module_utils
   - Test individual functions and classes
   - Fast execution, no external dependencies
   - Target: 80%+ code coverage

2. **Integration Tests** (`tests/integration/`)
   - Test against real MCP server implementations (see ADR-0007)
   - Verify full module workflows
   - Test all transport types
   - Validate error handling and edge cases
   - Target: Cover all critical user workflows

## Consequences

### Positive
- **Comprehensive coverage**: Both unit and integration tests provide thorough validation
- **Fast feedback**: Unit tests run quickly in development
- **Real-world validation**: Integration tests verify actual MCP server interactions
- **Regression prevention**: Catches breaking changes before release
- **CI/CD ready**: Structured for automated testing pipelines
- **Ansible standard**: Follows Ansible collection testing conventions
- **Quality assurance**: High confidence in module behavior

### Negative
- **Maintenance burden**: Two test suites to maintain
- **Test servers required**: Integration tests use real MCP servers (see ADR-0007 for details)
- **Slower CI/CD**: Integration tests increase pipeline execution time
- **Mock complexity**: Mocking MCP SDK requires careful design
- **Resource requirements**: Integration tests may need more resources

### Neutral
- Uses standard Python testing tools (pytest, pytest-ansible)
- Test organization follows Ansible collection conventions

## Implementation Notes

### Unit Test Structure
```
tests/unit/
├── plugins/
│   ├── module_utils/
│   │   ├── test_mcp_client.py
│   │   ├── test_mcp_validator.py
│   │   └── test_mcp_reporter.py
│   └── modules/
│       ├── test_mcp_server_info.py
│       ├── test_mcp_test_tool.py
│       ├── test_mcp_test_resource.py
│       ├── test_mcp_test_prompt.py
│       └── test_mcp_test_suite.py
└── conftest.py
```

### Integration Test Structure
```
tests/integration/
├── targets/
│   ├── mcp_server_info/
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   └── meta/
│   │       └── main.yml
│   ├── mcp_test_tool/
│   ├── mcp_test_resource/
│   ├── mcp_test_prompt/
│   └── mcp_test_suite/
├── sample_servers/
│   ├── calculator_server.py
│   ├── file_resource_server.py
│   └── prompt_template_server.py
└── inventory
```

### Unit Testing Approach
```python
# Example: tests/unit/plugins/module_utils/test_mcp_client.py
import pytest
from unittest.mock import Mock, patch
from ansible_collections.mcp.audit.plugins.module_utils.mcp_client import MCPClient

def test_stdio_client_initialization():
    """Test MCPClient initialization with stdio transport"""
    client = MCPClient(transport='stdio', server_command='python', server_args=['server.py'])
    assert client.transport == 'stdio'
    assert client.server_command == 'python'

@patch('ansible_collections.mcp.audit.plugins.module_utils.mcp_client.StdioMCPClient')
def test_connect_success(mock_stdio_client):
    """Test successful connection to MCP server"""
    mock_client_instance = Mock()
    mock_stdio_client.return_value = mock_client_instance

    client = MCPClient(transport='stdio', server_command='python')
    result = client.connect()

    assert result['success'] is True
    mock_client_instance.connect.assert_called_once()
```

### Integration Testing Approach
```yaml
# Example: tests/integration/targets/mcp_test_tool/tasks/main.yml
---
- name: Start sample calculator server
  shell: python {{ playbook_dir }}/sample_servers/calculator_server.py &
  async: 60
  poll: 0
  register: calculator_server

- name: Wait for server to be ready
  wait_for:
    timeout: 5

- name: Test calculator add tool
  mcp.audit.mcp_test_tool:
    server_command: "python"
    server_args:
      - "{{ playbook_dir }}/sample_servers/calculator_server.py"
    tool_name: "add"
    tool_arguments:
      a: 5
      b: 3
    expected_result:
      result: 8
  register: tool_result

- name: Verify tool test succeeded
  assert:
    that:
      - tool_result.success is true
      - tool_result.response.result == 8
```

### Test MCP Servers
Integration tests use real MCP server implementations from the community. See **ADR-0007: Real MCP Servers for Integration Testing** for:
- Specific server selections and sources
- Attribution and licensing
- Setup and maintenance procedures
- Rationale for using real servers vs. mocks

Key servers include:
- Calculator server for tool testing (stdio transport)
- Prompt server for prompt template testing
- Custom resource server for resource testing

### CI/CD Integration
```yaml
# .github/workflows/test.yml
name: Test Collection
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run unit tests
        run: pytest tests/unit/ -v --cov

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run integration tests
        run: ansible-test integration
```

### Testing Requirements
- Python dependencies: `pytest>=7.0.0`, `pytest-ansible>=3.0.0`, `pytest-cov>=4.0.0`
- Mock library: `unittest.mock` (Python standard library)
- Sample MCP servers: Python-based, minimal implementations
- Test data fixtures: JSON/YAML files for expected responses

### Coverage Goals
- **Unit tests**: 80%+ line coverage
- **Integration tests**: 100% of user-facing workflows
- **Transport coverage**: All modules tested with stdio, SSE, and HTTP
- **Error paths**: Key error scenarios tested

## Alternatives Considered

### Integration Tests Only
- **Pros**: Simpler structure, real-world validation
- **Cons**: Slow feedback, harder to test edge cases
- **Verdict**: Rejected - unit tests provide faster development feedback

### Unit Tests Only
- **Pros**: Fast execution, simple setup
- **Cons**: Doesn't verify real MCP SDK integration
- **Verdict**: Rejected - need real-world validation

### Manual Testing Only
- **Pros**: No test code to maintain
- **Cons**: No regression prevention, inconsistent testing
- **Verdict**: Rejected - not suitable for production-quality collection
