# Architectural Decision Records (ADRs)

This directory contains Architectural Decision Records (ADRs) for the MCP Audit Ansible Collection project.

## What are ADRs?

An Architectural Decision Record (ADR) captures an important architectural decision made along with its context and consequences. This helps maintain a historical record of why decisions were made and provides context for future maintainers.

## ADR Format

Each ADR follows this structure:

- **Status**: Proposed, Accepted, Deprecated, or Superseded
- **Context**: What is the issue or decision being addressed?
- **Decision**: What is the change we're making?
- **Consequences**: Positive, negative, and neutral results of this decision

## Current ADRs

| ADR | Title | Status |
|-----|-------|--------|
| [0001](0001-collection-namespace-selection.md) | Collection Namespace Selection | Accepted |
| [0002](0002-mcp-python-sdk-selection.md) | MCP Python SDK Selection | Accepted |
| [0003](0003-module-architecture-pattern.md) | Module Architecture Pattern | Accepted |
| [0004](0004-transport-protocol-support.md) | Transport Protocol Support | Accepted |
| [0005](0005-testing-strategy.md) | Testing Strategy | Accepted |
| [0006](0006-result-reporting-format.md) | Result Reporting Format | Accepted |
| [0007](0007-real-mcp-servers-for-integration-testing.md) | Real MCP Servers for Integration Testing | Accepted |
| [0008](0008-licensing-strategy.md) | Licensing Strategy | Accepted |
| [0009](0009-documentation-strategy.md) | Documentation Strategy | Accepted |
| [0010](0010-changelog-management.md) | Changelog Management | Accepted |
| [0011](0011-code-quality-tools.md) | Code Quality Tools | Accepted |
| [0012](0012-ci-cd-strategy.md) | CI/CD Strategy | Accepted |
| [0013](0013-version-compatibility-rhel10.md) | Version Compatibility and RHEL 10 Support | Accepted |
| [0014](0014-galaxy-publishing-requirements.md) | Galaxy Publishing Requirements | Accepted |
| [0015](0015-security-policy.md) | Security Policy | Accepted |

## Creating New ADRs

When making significant architectural decisions:

1. Copy the template below or use an existing ADR as a template
2. Number it sequentially (e.g., 0007-new-decision.md)
3. Fill in all sections with clear, concise information
4. Update this README with the new ADR
5. Commit the ADR along with the related code changes

## ADR Template

```markdown
# ADR-XXXX: [Short Decision Title]

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-YYYY]

## Context
[What is the issue or decision being addressed? What factors are relevant?]

## Decision
[What is the change we're making? Be specific and clear.]

## Consequences

### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Drawback 1]
- [Drawback 2]

### Neutral
- [Neutral point 1]
- [Neutral point 2]

## Implementation Notes
[Technical details, code examples, configuration requirements, etc.]

## Alternatives Considered
[What other options were evaluated and why were they not chosen?]
```

## Reviewing ADRs

ADRs should be reviewed:
- When making related architectural decisions
- During onboarding of new team members
- When refactoring or updating related code
- Periodically to ensure decisions remain relevant

## Updating ADRs

ADRs are generally immutable once accepted. However, they can be:
- **Deprecated**: Mark as deprecated and create a new ADR if the decision is no longer valid
- **Superseded**: Link to the new ADR that replaces this decision
- **Amended**: Minor clarifications can be added, but significant changes should be new ADRs

## Further Reading

- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) by Michael Nygard
- [ADR GitHub Organization](https://adr.github.io/)
