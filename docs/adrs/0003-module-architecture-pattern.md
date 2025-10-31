# ADR-0003: Module Architecture Pattern

## Status
Accepted

## Context
The collection needs to provide functionality for testing MCP servers. Several architectural patterns were considered for organizing this functionality:

1. **Single monolithic module**: One `mcp_test` module with operation parameter
2. **Specialized modules**: Separate modules for each operation (tools, resources, prompts, server info)
3. **Role-based only**: No custom modules, use roles with existing Ansible modules
4. **Plugin-based extensions**: Extensible plugin system for test types

Key considerations:
- Ansible best practices and conventions
- User experience and ease of use
- Maintainability and code organization
- Flexibility for different testing scenarios
- Idempotency support

## Decision
We will implement **specialized Ansible modules** for each major MCP testing operation:

- `mcp_server_info` - Server capability discovery
- `mcp_test_tool` - Individual tool testing
- `mcp_test_resource` - Individual resource testing
- `mcp_test_prompt` - Individual prompt testing
- `mcp_test_suite` - Comprehensive test suite execution

All modules located in `plugins/modules/` with shared utilities in `plugins/module_utils/`.

## Consequences

### Positive
- **Clear separation of concerns**: Each module has a single, well-defined responsibility
- **Better user experience**: Users can import and use only the modules they need
- **Improved documentation**: Each module has focused documentation for its specific use case
- **Easier testing**: Unit tests can target specific functionality in isolation
- **Idempotent operations**: Each module can implement appropriate idempotency checks for its operation
- **Flexible composition**: Users can combine modules in playbooks as needed
- **Ansible conventions**: Follows Ansible best practice of task-specific modules

### Negative
- **Code duplication**: Some common functionality may be repeated across modules
- **More files to maintain**: Five modules instead of one requires more maintenance overhead
- **Coordination complexity**: Changes affecting multiple modules require coordinated updates
- **Learning curve**: Users need to understand which module to use for each task

### Neutral
- Module utils (`module_utils/`) can be used to share common code and reduce duplication
- Total lines of code is similar whether using one or multiple modules

## Implementation Notes

### Module Structure
Each module will follow this structure:
```python
# Standard module pattern
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mcp.audit.plugins.module_utils.mcp_client import MCPClient
from ansible_collections.mcp.audit.plugins.module_utils.mcp_validator import validate_result

def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_command=dict(type='str', required=True),
            server_args=dict(type='list', elements='str', default=[]),
            transport=dict(type='str', default='stdio', choices=['stdio', 'sse', 'http']),
            # Module-specific parameters
        ),
        supports_check_mode=True
    )

    # Module-specific logic

    module.exit_json(**result)

if __name__ == '__main__':
    main()
```

### Shared Module Utils
- `mcp_client.py` - MCP SDK wrapper and connection management
- `mcp_validator.py` - Result validation and verification utilities
- `mcp_reporter.py` - Status reporting and formatting utilities

### Module Documentation
Each module will include:
- DOCUMENTATION block with description and parameters
- EXAMPLES block with common usage patterns
- RETURN block with return value documentation
- Proper error messages for troubleshooting

## Alternatives Considered

### Single Monolithic Module
- **Pros**: One module to maintain, simpler imports
- **Cons**: Complex parameter handling, poor separation of concerns, harder to document
- **Verdict**: Rejected due to poor maintainability

### Role-based Only Approach
- **Pros**: No custom module development needed
- **Cons**: Cannot leverage Ansible module features, complex role logic, poor reusability
- **Verdict**: Rejected - roles complement but don't replace modules

### Plugin-based Extensions
- **Pros**: Highly flexible and extensible
- **Cons**: Overly complex for initial use case, harder for users to understand
- **Verdict**: Deferred - could be added later if needed
