# ADR-0004: Transport Protocol Support

## Status
Accepted

## Context
MCP (Model Context Protocol) servers can communicate using different transport mechanisms. The collection needs to determine which transports to support and how to implement them.

Available MCP transport options:
- **stdio**: Standard input/output based communication (local processes)
- **SSE**: Server-Sent Events over HTTP (remote servers, streaming)
- **HTTP**: Standard HTTP request/response (remote servers, simple)

Considerations:
- Coverage of common MCP server deployment patterns
- Implementation complexity
- Testing requirements
- User configuration flexibility
- Performance characteristics

## Decision
We will support **all three transport protocols** (stdio, SSE, and HTTP) with stdio as the default.

All modules will accept a `transport` parameter with choices: `['stdio', 'sse', 'http']`, defaulting to `'stdio'`.

## Consequences

### Positive
- **Comprehensive coverage**: Supports all standard MCP deployment scenarios
- **Local testing**: stdio enables testing local MCP server implementations
- **Remote testing**: SSE and HTTP enable testing production servers
- **Flexibility**: Users can choose the appropriate transport for their use case
- **Future-proof**: Covers current and anticipated MCP server deployments
- **MCP SDK support**: All three transports are well-supported by the official SDK

### Negative
- **Implementation complexity**: Need to handle three different connection patterns
- **Testing overhead**: Must test all modules with all three transport types
- **Configuration complexity**: More parameters and validation logic required
- **Dependency variations**: Some transports may require additional Python dependencies
- **Error handling**: Different transports have different failure modes

### Neutral
- The MCP Python SDK handles most transport-specific details
- Default to stdio maintains simplicity for common local testing scenarios

## Implementation Notes

### Module Parameter Structure
```yaml
- name: Test MCP tool
  mcp.audit.mcp_test_tool:
    server_command: "python"  # Required for stdio
    server_args:              # Optional for stdio
      - "/path/to/server.py"
    transport: "stdio"        # Default: stdio
    # For SSE/HTTP transports:
    # server_url: "https://mcp-server.example.com"  # Required for SSE/HTTP
    # server_headers: {}      # Optional for SSE/HTTP
    tool_name: "add"
    tool_arguments:
      a: 5
      b: 3
```

### Transport-Specific Parameters
- **stdio**: Requires `server_command`, optional `server_args`
- **SSE/HTTP**: Requires `server_url`, optional `server_headers` for authentication

### Module Utils Implementation
```python
# mcp_client.py
class MCPClient:
    def __init__(self, transport, **kwargs):
        if transport == 'stdio':
            self.client = StdioMCPClient(kwargs['server_command'], kwargs.get('server_args', []))
        elif transport == 'sse':
            self.client = SSEMCPClient(kwargs['server_url'], kwargs.get('server_headers', {}))
        elif transport == 'http':
            self.client = HTTPMCPClient(kwargs['server_url'], kwargs.get('server_headers', {}))
```

### Testing Strategy
- Unit tests with mocked connections for all three transports
- Integration tests with sample MCP servers for each transport
- Document transport-specific behavior and limitations
- Provide example playbooks for each transport type

### Documentation Requirements
- Clear explanation of when to use each transport
- Examples for all three transport types
- Troubleshooting guide for transport-specific issues
- Security considerations for remote transports (SSE/HTTP)

## Security Considerations
- **stdio**: Executes local commands - validate and sanitize command parameters
- **SSE/HTTP**: Network communication - support TLS/SSL, authentication headers
- **Credentials**: Never log or expose authentication credentials
- **Timeout handling**: Implement appropriate timeouts for all transports

## Alternatives Considered

### stdio Only
- **Pros**: Simplest implementation, covers local testing
- **Cons**: Cannot test remote/production MCP servers
- **Verdict**: Rejected - too limited for real-world usage

### HTTP Only
- **Pros**: Simplest remote transport, widely understood
- **Cons**: Misses local testing scenarios, not optimal for streaming
- **Verdict**: Rejected - excludes important use cases

### stdio and HTTP Only (Exclude SSE)
- **Pros**: Covers most scenarios, simpler than all three
- **Cons**: SSE is optimal for certain MCP server implementations
- **Verdict**: Rejected - MCP SDK supports SSE well, worth including
