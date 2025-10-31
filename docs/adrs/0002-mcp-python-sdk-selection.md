# ADR-0002: MCP Python SDK Selection

## Status
Accepted

## Context
The collection needs to communicate with MCP (Model Context Protocol) servers to perform audit operations. Several approaches were considered:

1. **Implement custom MCP client**: Build a custom client from scratch based on MCP specifications
2. **Use official MCP Python SDK**: Use the official SDK from https://github.com/modelcontextprotocol/python-sdk
3. **Use third-party MCP libraries**: Evaluate community-built MCP client libraries

Key requirements:
- Support for multiple transports (stdio, SSE, HTTP)
- Reliable connection management
- Active maintenance and updates
- Good documentation
- Python 3.9+ compatibility

## Decision
We will use the **official MCP Python SDK** from https://github.com/modelcontextprotocol/python-sdk (version >= 1.19.0).

## Consequences

### Positive
- **Official support**: Maintained by the MCP protocol authors, ensuring compliance with specifications
- **Complete feature set**: Full support for all MCP protocol features (tools, resources, prompts)
- **Multiple transports**: Built-in support for stdio, SSE, and HTTP transports
- **Well-documented**: Comprehensive documentation and examples available
- **Active development**: Regular updates and bug fixes from the core team
- **Community adoption**: Widely used in the MCP ecosystem, reducing integration risks
- **Type safety**: Strong typing support for better development experience

### Negative
- **External dependency**: Adds a runtime dependency on the MCP SDK
- **Version coupling**: Collection updates may be required when SDK introduces breaking changes
- **SDK bugs**: Potential issues must be resolved upstream rather than locally
- **Package size**: Increases overall collection size

### Neutral
- Requires Python 3.9+ environment for module execution
- SDK features we don't use still get included in the dependency

## Implementation Notes
- Add `mcp>=1.19.0` to `requirements.txt`
- Create module utility `mcp_client.py` that wraps the SDK for consistent usage across modules
- Implement proper error handling for SDK exceptions
- Add SDK version compatibility checks in module initialization
- Document SDK version requirements in collection README
- Consider pinning to specific SDK versions for stability in production environments

## Alternatives Considered

### Custom MCP Client Implementation
- **Pros**: Full control, no external dependencies, minimal size
- **Cons**: High development effort, maintenance burden, potential protocol incompatibilities
- **Verdict**: Rejected due to maintenance complexity and risk

### Third-party Libraries
- **Pros**: Potentially lighter weight, community-driven features
- **Cons**: Less reliable maintenance, potential protocol drift, limited adoption
- **Verdict**: Rejected due to reliability concerns and lack of official support
