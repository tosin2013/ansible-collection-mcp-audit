# ADR-0006: Result Reporting Format

## Status
Accepted

## Context
Module execution results need to be returned to users in a clear, actionable format. The collection must also support generating comprehensive test reports for audit and documentation purposes.

Requirements:
- Ansible module return values (immediate feedback)
- Test suite summary reports (comprehensive overview)
- Machine-readable format (CI/CD integration)
- Human-readable format (manual review)
- Error details for troubleshooting
- Metrics for performance analysis

Format options considered:
- JSON only
- YAML only
- JSON and YAML
- Custom text format
- HTML reports

## Decision
We will use **JSON as the primary format** with **optional YAML export** capability:

1. **Module Return Values**: Ansible-standard JSON structure
2. **Test Reports**: JSON files with optional YAML conversion
3. **Summary Reports**: JSON with human-readable formatting
4. **Error Reporting**: Structured JSON with detailed error information

## Consequences

### Positive
- **Ansible native**: JSON is Ansible's native return value format
- **Machine-readable**: Easy to parse and process programmatically
- **CI/CD friendly**: Standard format for automated pipelines
- **Tooling support**: Broad ecosystem support for JSON processing
- **Flexible conversion**: Can convert to YAML when needed
- **Consistent**: Single format reduces complexity
- **Type preservation**: JSON maintains data types (numbers, booleans, etc.)

### Negative
- **Human readability**: JSON is less readable than YAML for manual review
- **Verbosity**: JSON can be more verbose with quotes and brackets
- **Comments**: JSON doesn't support comments (YAML does)

### Neutral
- YAML can be generated from JSON when human readability is prioritized
- Both formats are widely understood in the DevOps community

## Implementation Notes

### Module Return Value Structure
```json
{
  "success": true,
  "changed": false,
  "status": "ok",
  "response": {
    "result": "tool output here"
  },
  "execution_time": 0.523,
  "error": null,
  "metadata": {
    "server_command": "python server.py",
    "transport": "stdio",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Test Suite Report Structure
```json
{
  "summary": {
    "total_tests": 15,
    "passed": 13,
    "failed": 2,
    "skipped": 0,
    "success_rate": 86.67,
    "total_time": 45.2,
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "server_info": {
    "command": "python server.py",
    "transport": "stdio",
    "capabilities": ["tools", "resources", "prompts"]
  },
  "test_results": [
    {
      "test_id": "tool_calculator_add",
      "test_type": "tool",
      "name": "add",
      "status": "passed",
      "execution_time": 0.123,
      "details": {
        "arguments": {"a": 5, "b": 3},
        "expected": {"result": 8},
        "actual": {"result": 8}
      }
    },
    {
      "test_id": "resource_config_read",
      "test_type": "resource",
      "name": "config://app.json",
      "status": "failed",
      "execution_time": 0.456,
      "error": {
        "type": "ResourceNotFound",
        "message": "Resource config://app.json not found",
        "details": "Server returned 404",
        "traceback": "..."
      }
    }
  ],
  "metrics": {
    "tools_tested": 8,
    "resources_tested": 5,
    "prompts_tested": 2,
    "average_response_time": 0.301
  }
}
```

### Error Reporting Structure
```json
{
  "success": false,
  "error": {
    "type": "ConnectionError",
    "message": "Failed to connect to MCP server",
    "details": "Connection refused on localhost:8080",
    "code": "MCP_CONNECTION_FAILED",
    "timestamp": "2024-01-15T10:30:00Z",
    "troubleshooting": [
      "Verify server is running",
      "Check server_command and server_args are correct",
      "Ensure network connectivity if using remote transport"
    ]
  },
  "context": {
    "server_command": "python server.py",
    "transport": "stdio",
    "module": "mcp_test_tool"
  }
}
```

### Report Generation Module
```python
# plugins/module_utils/mcp_reporter.py
import json
import yaml
from datetime import datetime

class MCPReporter:
    def __init__(self, output_format='json'):
        self.output_format = output_format

    def generate_report(self, test_results, report_path):
        """Generate test report in specified format"""
        report_data = self._build_report_structure(test_results)

        if self.output_format == 'json':
            self._write_json(report_data, report_path)
        elif self.output_format == 'yaml':
            self._write_yaml(report_data, report_path)

    def _build_report_structure(self, test_results):
        """Build standardized report structure"""
        return {
            'summary': self._build_summary(test_results),
            'server_info': self._build_server_info(test_results),
            'test_results': test_results,
            'metrics': self._calculate_metrics(test_results)
        }
```

### Playbook Usage Examples
```yaml
# Generate JSON report (default)
- name: Run comprehensive MCP tests
  mcp.audit.mcp_test_suite:
    server_command: "python"
    server_args:
      - "/path/to/server.py"
    test_config:
      tools:
        - name: "add"
          arguments: {a: 5, b: 3}
          expected: {result: 8}
    report_path: "/tmp/mcp_test_report.json"
  register: test_results

# Convert to YAML for human review
- name: Convert report to YAML
  shell: |
    python -c "import json, yaml; print(yaml.dump(json.load(open('{{ test_results.report_path }}'))))" \
    > /tmp/mcp_test_report.yaml

# Display summary
- name: Display test summary
  debug:
    msg: "Tests: {{ test_results.summary.total_tests }}, Passed: {{ test_results.summary.passed }}, Failed: {{ test_results.summary.failed }}"
```

### Report Validation
- JSON Schema validation for report structure
- Required fields enforcement
- Type checking for metrics and counts
- Timestamp format validation (ISO 8601)

### Documentation Requirements
- Document complete report structure
- Provide schema definitions
- Include example reports for each module
- Show YAML conversion examples
- Document error codes and meanings

## Alternatives Considered

### YAML Only
- **Pros**: More human-readable, supports comments
- **Cons**: Not Ansible's native format, inconsistent with module returns
- **Verdict**: Rejected - should match Ansible conventions

### Custom Text Format
- **Pros**: Can optimize for human readability
- **Cons**: Not machine-parseable, requires custom tooling
- **Verdict**: Rejected - limits automation capabilities

### HTML Reports
- **Pros**: Beautiful formatting, interactive features possible
- **Cons**: Not suitable for module return values, requires rendering
- **Verdict**: Deferred - could be added as optional export format later

### JSON and YAML Simultaneously
- **Pros**: Best of both worlds
- **Cons**: Double file output, potential inconsistencies
- **Verdict**: Rejected - JSON with on-demand YAML conversion is sufficient
