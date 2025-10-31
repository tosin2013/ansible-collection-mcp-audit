# ADR-0007: Real MCP Servers for Integration Testing

## Status
Accepted

## Context
The original testing strategy (ADR-0005) mentioned creating sample MCP servers for integration testing. We need to decide whether to:

1. **Create custom mock servers** from scratch
2. **Use real lightweight MCP server implementations** from the ecosystem
3. **Mix of both** - use existing servers and supplement with custom ones

Key considerations:
- **Test authenticity**: Real servers provide more realistic testing scenarios
- **Maintenance burden**: Custom servers need ongoing maintenance
- **Coverage**: Need to test tools, resources, and prompts comprehensively
- **Setup complexity**: Integration tests should be easy to run
- **Community alignment**: Using real servers tests against actual MCP implementations

After research, we identified several lightweight, well-maintained MCP server implementations:

### Available Test Servers

1. **arjunprabhulal/mcp-simple-demo**
   - Very simple Python server using FastMCP
   - Tools: `hello_world`, `add`
   - Transport: SSE (can be adapted to stdio)
   - Perfect for basic tool testing

2. **battula417/calculator-server**
   - Multiple implementations (stdio_server.py, adv_server.py)
   - Tools: `add`, `calculate_sum`, `calculate_product`, `get_server_info`
   - Transport: stdio (our primary focus)
   - Well-structured with proper error handling

3. **jamesdhope/mcp-examples**
   - Example server with prompt support
   - Demonstrates prompt templates and arguments
   - Good for testing prompt-related modules

## Decision
We will **use real, lightweight MCP server implementations** for integration testing, specifically:

1. **Primary Test Server**: Clone and adapt `battula417/calculator-server`
   - Provides multiple tools for comprehensive testing
   - Native stdio transport support
   - Simple, maintainable codebase

2. **Prompt Test Server**: Clone and adapt `jamesdhope/mcp-examples`
   - Specifically for testing prompt functionality
   - Demonstrates prompt arguments and templates

3. **Supplementary Custom Servers**: Create minimal custom servers only for:
   - Resource testing (file/URI resources)
   - Edge cases not covered by existing servers
   - Error condition testing

## Consequences

### Positive
- **Real-world testing**: Tests against actual MCP SDK usage patterns
- **Reduced development time**: No need to build servers from scratch
- **Better test coverage**: Real servers exercise full MCP protocol
- **Community validation**: Using proven server implementations
- **Easier maintenance**: Established servers are already debugged
- **Learning resource**: Developers can study real server implementations
- **Protocol compliance**: Real servers follow MCP specifications correctly

### Negative
- **External dependencies**: Relying on external repositories
- **Version synchronization**: Need to track updates to source servers
- **Potential breaking changes**: Upstream changes might affect our tests
- **License considerations**: Must respect original licenses (MIT typically)
- **Customization limits**: May need to fork for specific test scenarios

### Neutral
- Servers will be copied into our repository for stability
- Original attribution and licenses will be preserved
- We maintain control over when to update from upstream

## Implementation Notes

### Repository Structure
```
tests/integration/
├── sample_servers/
│   ├── calculator/           # From battula417/calculator-server
│   │   ├── server.py         # Main stdio server
│   │   ├── README.md         # Attribution and usage
│   │   └── requirements.txt
│   ├── prompts/              # From jamesdhope/mcp-examples
│   │   ├── server.py
│   │   ├── README.md
│   │   └── requirements.txt
│   └── resources/            # Custom resource server
│       ├── server.py
│       ├── test_data/
│       └── README.md
└── targets/
    ├── mcp_test_tool/
    │   └── tasks/
    │       └── main.yml      # Uses calculator server
    └── mcp_test_prompt/
        └── tasks/
            └── main.yml      # Uses prompts server
```

### Test Server Setup Script
```bash
# tests/integration/sample_servers/setup.sh
#!/bin/bash
set -e

echo "Setting up MCP test servers..."

# Install dependencies for all servers
pip install -r calculator/requirements.txt
pip install -r prompts/requirements.txt
pip install -r resources/requirements.txt

echo "Test servers ready!"
```

### Integration Test Example
```yaml
# tests/integration/targets/mcp_test_tool/tasks/main.yml
---
- name: Test calculator add tool
  mcp.audit.mcp_test_tool:
    server_command: "python"
    server_args:
      - "{{ playbook_dir }}/sample_servers/calculator/server.py"
    transport: "stdio"
    tool_name: "add"
    tool_arguments:
      a: 5
      b: 3
  register: add_result

- name: Verify add result
  assert:
    that:
      - add_result.success
      - add_result.response.text == "8"

- name: Test calculator product tool
  mcp.audit.mcp_test_tool:
    server_command: "python"
    server_args:
      - "{{ playbook_dir }}/sample_servers/calculator/server.py"
    transport: "stdio"
    tool_name: "calculate_product"
    tool_arguments:
      a: 4
      b: 7
  register: product_result

- name: Verify product result
  assert:
    that:
      - product_result.success
      - product_result.response.text == "28"
```

### Custom Resource Server
For resource testing, create a minimal custom server:

```python
# tests/integration/sample_servers/resources/server.py
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, BlobContent

server = Server("resource-test-server")

@server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="file://test_data/config.json",
            name="Test Config",
            mimeType="application/json",
            description="Test configuration file"
        ),
        Resource(
            uri="file://test_data/document.txt",
            name="Test Document",
            mimeType="text/plain",
            description="Test text document"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "file://test_data/config.json":
        return '{"key": "value", "enabled": true}'
    elif uri == "file://test_data/document.txt":
        return "This is a test document."
    else:
        raise ValueError(f"Resource not found: {uri}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

### Attribution and Licensing
Each cloned server directory will include attribution:

```markdown
# Attribution

This server is adapted from:
- **Original Repository**: https://github.com/battula417/calculator-server
- **License**: MIT License
- **Modifications**: Minimal adaptations for integration testing

## Original License
[Include full original license text]

## Our Usage
This code is used for integration testing of the MCP Audit Ansible Collection.
```

### CI/CD Integration
```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests
on: [push, pull_request]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install ansible-core mcp
          pip install -r tests/integration/sample_servers/calculator/requirements.txt
          pip install -r tests/integration/sample_servers/prompts/requirements.txt
          pip install -r tests/integration/sample_servers/resources/requirements.txt

      - name: Run integration tests
        run: |
          ansible-test integration --requirements
```

## References

### Source Repositories
- **battula417/calculator-server**: https://github.com/battula417/calculator-server
  - Stdio calculator server with multiple operations
  - MIT License
  - Last checked: 2024-01-15

- **jamesdhope/mcp-examples**: https://github.com/jamesdhope/mcp-examples
  - Example MCP servers including prompt support
  - License: MIT (assumed, verify on clone)
  - Last checked: 2024-01-15

- **arjunprabhulal/mcp-simple-demo**: https://github.com/arjunprabhulal/mcp-simple-demo
  - Simple demonstration server
  - Backup option if needed
  - Last checked: 2024-01-15

## Alternatives Considered

### Build All Servers from Scratch
- **Pros**: Full control, no external dependencies, optimized for our needs
- **Cons**: High development effort, potential bugs, protocol compliance risks
- **Verdict**: Rejected - reinventing the wheel, high maintenance burden

### Use Only Mocks
- **Pros**: Fast tests, full control over responses
- **Cons**: Doesn't test real MCP protocol interactions, less confidence
- **Verdict**: Rejected - need real protocol testing for audit collection

### Use Official MCP SDK Examples Only
- **Pros**: Most authoritative source
- **Cons**: May not have all examples we need, may be too simple
- **Verdict**: Partially accepted - use where available, supplement with community servers

## Review Schedule
- **Quarterly**: Check source repositories for updates
- **Before major releases**: Verify compatibility with latest MCP SDK versions
- **When tests fail**: Investigate if upstream changes caused issues
