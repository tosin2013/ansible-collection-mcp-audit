# Integration Tests for MCP Audit Ansible Collection

This directory contains integration tests for the `mcp.audit` Ansible collection, using real MCP server implementations to validate module functionality.

## Overview

The integration tests verify that all 5 collection modules work correctly with actual MCP servers, testing:
- Server capability discovery
- Tool invocation and validation
- Resource retrieval and verification
- Prompt template generation
- Test suite orchestration

## Directory Structure

```
tests/integration/
├── README.md                      # This file
├── ansible.cfg                    # Ansible configuration for testing
├── test-runner.yml                # Main test playbook covering all modules
├── sample_servers/                # Real MCP servers for testing
│   ├── calculator/                # Tool testing server
│   │   ├── server.py              # Calculator MCP server (stdio)
│   │   ├── README.md              # Attribution and usage
│   │   └── requirements.txt       # mcp>=1.19.0
│   ├── prompts/                   # Prompt testing server
│   │   ├── server.py              # Prompt template MCP server (stdio)
│   │   ├── README.md              # Attribution and usage
│   │   └── requirements.txt       # mcp>=1.19.0
│   └── resources/                 # Resource testing server
│       ├── server.py              # Resource MCP server (stdio)
│       ├── README.md              # Attribution and usage
│       └── requirements.txt       # mcp>=1.19.0
└── targets/                       # ansible-test integration targets
    ├── mcp_server_info/           # Server info tests
    │   └── tasks/main.yml
    ├── mcp_test_tool/             # Tool testing tests
    │   └── tasks/main.yml
    ├── mcp_test_resource/         # Resource testing tests
    │   └── tasks/main.yml
    ├── mcp_test_prompt/           # Prompt testing tests
    │   └── tasks/main.yml
    └── mcp_test_suite/            # Suite orchestration tests
        └── tasks/main.yml
```

## Test Servers

### Calculator Server (`sample_servers/calculator/`)
- **Source:** Adapted from [battula417/calculator-server](https://github.com/battula417/calculator-server)
- **License:** MIT (educational/demonstration purposes)
- **Transport:** stdio
- **Capabilities:** Tools
- **Tools Provided:**
  - `add` - Add two numbers
  - `calculate_sum` - Calculate sum of two numbers
  - `calculate_product` - Calculate product of two numbers
  - `get_server_info` - Get server information

### Prompts Server (`sample_servers/prompts/`)
- **Source:** Adapted from [jamesdhope/mcp-examples](https://github.com/jamesdhope/mcp-examples)
- **License:** MIT (assumed)
- **Transport:** stdio
- **Capabilities:** Prompts
- **Prompts Provided:**
  - `test-prompt` - Test prompt with context and topic arguments
  - `simple-prompt` - Simple prompt without arguments

### Resources Server (`sample_servers/resources/`)
- **Source:** Custom implementation for this collection
- **License:** GPL-3.0-or-later
- **Transport:** stdio
- **Capabilities:** Resources
- **Resources Provided:**
  - `file://test_data/config.json` - Test JSON configuration
  - `file://test_data/document.txt` - Test text document
  - `file://test_data/data.yaml` - Test YAML data

## Running Integration Tests

### Prerequisites

1. **Install the collection:**
   ```bash
   ansible-galaxy collection build --force
   ansible-galaxy collection install mcp-audit-*.tar.gz --force
   ```

2. **Set up collection structure for testing:**
   ```bash
   mkdir -p /tmp/test-collections/ansible_collections/mcp
   ln -sfn /path/to/ansible-collection-mcp-audit /tmp/test-collections/ansible_collections/mcp/audit
   ```

3. **Ensure MCP SDK is installed:**
   ```bash
   pip install mcp>=1.19.0
   ```

### Running Tests

#### Using the test-runner (recommended):
```bash
cd tests/integration
ansible-playbook -i localhost, \
  -e "ansible_python_interpreter=/path/to/venv/bin/python" \
  test-runner.yml
```

#### Using ansible-test (requires proper collection structure):
```bash
# From collection root in proper ansible_collections/mcp/audit/ structure
ansible-test integration mcp_server_info --python 3.11
ansible-test integration mcp_test_tool --python 3.11
ansible-test integration mcp_test_resource --python 3.11
ansible-test integration mcp_test_prompt --python 3.11
ansible-test integration mcp_test_suite --python 3.11
```

#### Running individual test targets:
```bash
cd tests/integration
ansible-playbook -i localhost, \
  -e "ansible_python_interpreter=/path/to/venv/bin/python" \
  targets/mcp_server_info/tasks/main.yml
```

## Test Coverage

### Module: mcp_server_info
- ✅ Server capability discovery with calculator server
- ✅ Tool count validation (4 tools)
- ✅ Server capability discovery with prompt server
- ✅ Prompt count validation (2 prompts)
- ✅ Server capability discovery with resource server
- ✅ Resource count validation (3 resources)

### Module: mcp_test_tool
- ✅ Add tool invocation (5 + 3 = 8)
- ✅ Product tool invocation (4 * 7 = 28)
- ✅ Server info tool invocation
- ✅ Expected result validation (10 + 20 = 30)
- ✅ Invalid tool error handling

### Module: mcp_test_resource
- ✅ JSON resource retrieval
- ✅ Text resource retrieval
- ✅ YAML resource retrieval
- ✅ Expected content validation
- ✅ Invalid resource error handling

### Module: mcp_test_prompt
- ✅ Simple prompt without arguments
- ✅ Prompt with required argument (topic)
- ✅ Prompt with optional and required arguments (context + topic)
- ✅ Invalid prompt error handling

### Module: mcp_test_suite
- ✅ Multi-tool test suite (3 tests)
- ✅ Multi-resource test suite (2 tests)
- ✅ Multi-prompt test suite (2 tests)
- ✅ Mixed test suite (2 tools)
- ✅ Summary statistics validation

## Known Issues

### Stdio Connection Timing
- **Status:** Under investigation
- **Error:** "unhandled errors in a TaskGroup (1 sub-exception)"
- **Cause:** Likely related to async process startup timing when spawning MCP servers via stdio
- **Impact:** Integration tests infrastructure is complete but tests don't run yet
- **Workaround:** Debug async stdio transport initialization sequence
- **Notes:**
  - All servers compile without syntax errors
  - MCP SDK is properly installed and accessible
  - Modules load successfully

## CI/CD Integration

Integration tests will be added to GitHub Actions workflows once the stdio timing issue is resolved:

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
          pip install ansible-core mcp>=1.19.0
          pip install -r tests/integration/sample_servers/calculator/requirements.txt
          pip install -r tests/integration/sample_servers/prompts/requirements.txt
          pip install -r tests/integration/sample_servers/resources/requirements.txt

      - name: Set up collection structure
        run: |
          mkdir -p /tmp/test-collections/ansible_collections/mcp
          ln -s $(pwd) /tmp/test-collections/ansible_collections/mcp/audit

      - name: Run integration tests
        run: |
          cd tests/integration
          ansible-playbook -i localhost, -e "ansible_python_interpreter=$(which python)" test-runner.yml
```

## Contributing

When adding new integration tests:

1. **Create test servers in `sample_servers/`** with proper attribution
2. **Add test playbooks in `targets/{module_name}/tasks/main.yml`**
3. **Update `test-runner.yml`** to include new test cases
4. **Document test coverage** in this README
5. **Ensure proper licensing** (MIT for adapted servers, GPL-3.0-or-later for custom)

## License

- **Test Infrastructure:** GPL-3.0-or-later (this project)
- **Calculator Server:** MIT (from battula417/calculator-server)
- **Prompts Server:** MIT (from jamesdhope/mcp-examples)
- **Resources Server:** GPL-3.0-or-later (custom implementation)

See individual server README files for detailed attribution.

## References

- [ADR-0005: Testing Strategy](../../docs/adrs/0005-testing-strategy.md)
- [ADR-0007: Real MCP Servers for Integration Testing](../../docs/adrs/0007-real-mcp-servers-for-integration-testing.md)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Ansible Collection Development Guide](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html)
