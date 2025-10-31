# ADR-0001: Collection Namespace Selection

## Status
Accepted

## Context
The Ansible collection needs a Fully Qualified Collection Name (FQCN) to be published to Ansible Galaxy. Two primary options were considered:
- `community.mcp_audit` - Using the community namespace
- `mcp.audit` - Using a dedicated MCP namespace

The namespace selection impacts:
- Collection discovery and identification
- Namespace management and ownership
- Community alignment and adoption
- Long-term maintainability

## Decision
We will use **`mcp.audit`** as the FQCN for this Ansible collection.

## Consequences

### Positive
- **Shorter and clearer**: The `mcp.audit` namespace is more concise and directly communicates the collection's purpose
- **Better namespace alignment**: Creates a dedicated namespace for MCP-related Ansible collections, allowing for future expansion (e.g., `mcp.monitoring`, `mcp.deploy`)
- **Professional identity**: Establishes a clear brand identity for MCP tooling in the Ansible ecosystem
- **Reduced naming conflicts**: Less likely to conflict with other community collections

### Negative
- **Namespace registration**: Requires registering and maintaining the `mcp` namespace on Ansible Galaxy
- **Less community visibility**: The `community` namespace might provide more initial visibility
- **Responsibility**: Takes on the responsibility of namespace ownership and governance

### Neutral
- Repository name remains `ansible-collection-mcp-audit` regardless of FQCN choice
- Internal module structure is unaffected by this decision
- Migration to a different namespace in the future is possible but requires effort

## Implementation Notes
- Update `galaxy.yml` with namespace: `mcp` and name: `audit`
- Register the `mcp` namespace on Ansible Galaxy
- Update all documentation to reference `mcp.audit` as the FQCN
- Configure GitHub repository topics and tags appropriately
