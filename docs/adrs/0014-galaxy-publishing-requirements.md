# ADR-0014: Galaxy Publishing Requirements

## Status
Accepted

## Context
Ansible Galaxy requires specific metadata and structure for collections to be published successfully. The collection must meet all Galaxy requirements for:
- **Discoverability**: Proper naming, tagging, and descriptions
- **Usability**: Clear documentation and support channels
- **Trustworthiness**: Author attribution, licensing, repository links
- **Dependency management**: Explicit collection dependencies
- **Version management**: Semantic versioning strategy

Galaxy publishing considerations:
- galaxy.yml is the primary metadata file
- Namespace must be approved (or use existing namespace)
- Collection name must be unique within namespace
- Tags affect search and discovery
- Documentation URLs are displayed prominently
- Version must follow semantic versioning

Community collection examples:
- **community.general**: 987 stars, comprehensive metadata
- **community.docker**: 241 stars, clear purpose and documentation

## Decision
We will implement **comprehensive Galaxy metadata** with all required and recommended fields:

### 1. Collection Naming

#### FQCN (Fully Qualified Collection Name)
- **Namespace**: `mcp`
- **Name**: `audit`
- **FQCN**: `mcp.audit`
- **Rationale**: See ADR-0001 for namespace selection decision

### 2. galaxy.yml Structure

#### Complete galaxy.yml Template
```yaml
---
# Collection Metadata
namespace: mcp
name: audit
version: 1.0.0

# README and description
readme: README.md
description: >-
  Ansible collection for testing and auditing Model Context Protocol (MCP) servers.
  Provides modules to verify MCP server implementations, test tools, resources,
  and prompts, with comprehensive reporting capabilities.

# Authors (must be list, can include GitHub handles)
authors:
  - Tosin Akinosho <tosin.akinosho@gmail.com> (@tosin2013)

# Licensing
license_file: COPYING

# Tags for discovery (max 20, lowercase, no spaces)
tags:
  - mcp
  - model_context_protocol
  - audit
  - testing
  - validation
  - api_testing
  - integration_testing
  - tools
  - resources
  - prompts

# External links
repository: https://github.com/tosin2013/ansible-collection-mcp-audit
documentation: https://github.com/tosin2013/ansible-collection-mcp-audit/blob/main/README.md
homepage: https://github.com/tosin2013/ansible-collection-mcp-audit
issues: https://github.com/tosin2013/ansible-collection-mcp-audit/issues

# Ansible version requirements
requires_ansible: '>=2.15.0'

# Collection dependencies (if any)
dependencies: {}

# Build ignore patterns
build_ignore:
  - .gitignore
  - .git
  - .github
  - .vscode
  - '*.pyc'
  - '*.retry'
  - tests/output
  - '*.tar.gz'
  - docs/adrs/GAPS-ANALYSIS.md
  - docs/adrs/PRD.md
```

### 3. Semantic Versioning Strategy

#### Version Number Format
- **Format**: `MAJOR.MINOR.PATCH` (e.g., 1.0.0)
- **Follows**: [Semantic Versioning 2.0.0](https://semver.org/)

#### Version Increment Rules
- **MAJOR**: Breaking changes (e.g., 1.0.0 → 2.0.0)
  - Incompatible module parameter changes
  - Removed modules or features
  - Changed return value structures
- **MINOR**: New features, backward compatible (e.g., 1.0.0 → 1.1.0)
  - New modules added
  - New module parameters added
  - New features in existing modules
- **PATCH**: Bug fixes, backward compatible (e.g., 1.0.0 → 1.0.1)
  - Bug fixes
  - Documentation improvements
  - Dependency updates (within compatible ranges)

#### Pre-release Versions
- **Alpha**: `1.0.0-alpha.1` (early development, breaking changes expected)
- **Beta**: `1.0.0-beta.1` (feature complete, API may change)
- **Release Candidate**: `1.0.0-rc.1` (ready for release, only critical bugs fixed)

### 4. Galaxy Publishing Workflow

#### Pre-publication Checklist
- [ ] All ansible-test sanity checks pass
- [ ] All ansible-test integration checks pass
- [ ] CHANGELOG.rst generated and up-to-date
- [ ] README.md complete with examples
- [ ] LICENSE files in place (see ADR-0008)
- [ ] All modules have DOCUMENTATION, EXAMPLES, RETURN blocks
- [ ] galaxy.yml version bumped appropriately
- [ ] Git tag created matching version

#### Publishing Process
```bash
# 1. Build the collection
ansible-galaxy collection build

# 2. Verify the tarball
tar -tzf mcp-audit-1.0.0.tar.gz

# 3. Test installation locally
ansible-galaxy collection install mcp-audit-1.0.0.tar.gz

# 4. Publish to Galaxy (requires API key)
ansible-galaxy collection publish mcp-audit-1.0.0.tar.gz --api-key=$GALAXY_API_KEY

# 5. Create GitHub release
gh release create v1.0.0 mcp-audit-1.0.0.tar.gz \
  --title "Release 1.0.0" \
  --notes-file CHANGELOG.md
```

### 5. Collection Dependencies

#### Current Dependencies
```yaml
# galaxy.yml
dependencies: {}
```

**Rationale**:
- No external Ansible collection dependencies currently needed
- Keeps the collection lightweight and reduces dependency conflicts
- If future dependencies are needed, document in ADR-0016

#### Python Dependencies
Documented in `requirements.txt`, not `galaxy.yml`:
```txt
ansible-core>=2.15.0
mcp>=1.19.0
```

### 6. Build Ignore Patterns

Exclude development and non-distribution files:
```yaml
build_ignore:
  # Version control
  - .gitignore
  - .git
  - .github

  # IDE files
  - .vscode
  - .idea
  - '*.swp'

  # Python artifacts
  - '*.pyc'
  - '__pycache__'
  - '*.egg-info'

  # Ansible artifacts
  - '*.retry'

  # Test artifacts
  - tests/output
  - tests/**/*.pyc
  - .pytest_cache

  # Build artifacts
  - '*.tar.gz'
  - build/

  # Development docs (not for distribution)
  - docs/adrs/GAPS-ANALYSIS.md
  - PRD.md

  # CI/CD local files
  - .tox
  - .coverage
```

## Consequences

### Positive
- **Galaxy ready**: All required metadata provided
- **Discoverable**: Tags and descriptions optimize search results
- **Professional**: Complete metadata signals quality and maintenance
- **Trustworthy**: Author attribution and licensing build confidence
- **Automated**: Publishing workflow can be automated in CI/CD
- **Versioned**: Clear semantic versioning strategy prevents confusion
- **Documented**: External links provide easy access to support resources

### Negative
- **Namespace approval**: May require approval for `mcp` namespace if not owned
- **Maintenance overhead**: galaxy.yml must be kept up-to-date with each release
- **Version constraints**: Semantic versioning must be strictly followed
- **Build size**: build_ignore must be carefully maintained to avoid bloat

### Neutral
- Galaxy metadata is standard for all collections (not a differentiator)
- Publishing workflow requires Galaxy API key (one-time setup)

## Implementation Notes

### Initial galaxy.yml Creation
```bash
# Create galaxy.yml in collection root
cat > galaxy.yml <<EOF
---
namespace: mcp
name: audit
version: 0.1.0
readme: README.md
description: >-
  Ansible collection for testing and auditing Model Context Protocol (MCP) servers.
authors:
  - Tosin Akinosho <tosin.akinosho@gmail.com> (@tosin2013)
license_file: COPYING
tags:
  - mcp
  - audit
  - testing
repository: https://github.com/tosin2013/ansible-collection-mcp-audit
documentation: https://github.com/tosin2013/ansible-collection-mcp-audit/blob/main/README.md
homepage: https://github.com/tosin2013/ansible-collection-mcp-audit
issues: https://github.com/tosin2013/ansible-collection-mcp-audit/issues
requires_ansible: '>=2.15.0'
dependencies: {}
EOF
```

### Namespace Request (if needed)
If `mcp` namespace doesn't exist:
```bash
# Request namespace on Galaxy
# Visit: https://galaxy.ansible.com/ui/my-namespaces/
# Click "Add namespace"
# Namespace: mcp
# Justification: "Creating MCP-related Ansible collections"
```

### Version Bump Script
```bash
#!/bin/bash
# scripts/bump_version.sh

set -e

CURRENT_VERSION=$(grep '^version:' galaxy.yml | awk '{print $2}')
echo "Current version: $CURRENT_VERSION"

# Parse version
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# Bump based on argument
case "$1" in
  major)
    NEW_VERSION="$((MAJOR + 1)).0.0"
    ;;
  minor)
    NEW_VERSION="$MAJOR.$((MINOR + 1)).0"
    ;;
  patch)
    NEW_VERSION="$MAJOR.$MINOR.$((PATCH + 1))"
    ;;
  *)
    echo "Usage: $0 {major|minor|patch}"
    exit 1
    ;;
esac

echo "New version: $NEW_VERSION"

# Update galaxy.yml
sed -i "s/^version: .*/version: $NEW_VERSION/" galaxy.yml

# Update any other version references
sed -i "s/version=.*/version=$NEW_VERSION/" setup.py 2>/dev/null || true

echo "Version bumped to $NEW_VERSION"
echo "Don't forget to:"
echo "  1. Update CHANGELOG.rst"
echo "  2. Commit changes: git commit -am 'chore: bump version to $NEW_VERSION'"
echo "  3. Create tag: git tag v$NEW_VERSION"
echo "  4. Push: git push && git push --tags"
```

### Galaxy Publishing CI/CD
```yaml
# .github/workflows/publish-galaxy.yml
name: Publish to Galaxy

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Ansible
        run: pip install ansible-core

      - name: Build collection
        run: ansible-galaxy collection build

      - name: Publish to Galaxy
        env:
          GALAXY_API_KEY: ${{ secrets.GALAXY_API_KEY }}
        run: |
          ansible-galaxy collection publish \
            mcp-audit-*.tar.gz \
            --api-key=$GALAXY_API_KEY

      - name: Upload tarball to release
        uses: actions/upload-release-asset@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          upload_url: ${{ github.event.release.upload_url }}
          asset_path: ./mcp-audit-*.tar.gz
          asset_name: mcp-audit-${{ github.event.release.tag_name }}.tar.gz
          asset_content_type: application/gzip
```

### Testing Collection Build
```bash
# Test local build
ansible-galaxy collection build

# Verify contents
tar -tzf mcp-audit-*.tar.gz | less

# Test local installation
ansible-galaxy collection install mcp-audit-*.tar.gz -f

# Test module import
ansible-doc mcp.audit.mcp_server_info

# Cleanup
rm -f mcp-audit-*.tar.gz
ansible-galaxy collection remove mcp.audit
```

### Collection Installation for Users
```bash
# Install from Galaxy (after publication)
ansible-galaxy collection install mcp.audit

# Install specific version
ansible-galaxy collection install mcp.audit:1.0.0

# Install from requirements.yml
cat > requirements.yml <<EOF
collections:
  - name: mcp.audit
    version: ">=1.0.0,<2.0.0"
EOF

ansible-galaxy collection install -r requirements.yml
```

### README.md Requirements
```markdown
# MCP Audit Ansible Collection

![Galaxy Version](https://img.shields.io/badge/galaxy-mcp.audit-blue)
![Ansible Version](https://img.shields.io/badge/ansible-%3E%3D2.15.0-blue)
![License](https://img.shields.io/badge/license-GPL--3.0--or--later-green)

Ansible collection for testing and auditing Model Context Protocol (MCP) servers.

## Installation

```bash
ansible-galaxy collection install mcp.audit
```

## Requirements

- Python 3.9+
- ansible-core 2.15.0+
- MCP Python SDK 1.19.0+

## Modules

- `mcp_server_info`: Gather MCP server information
- `mcp_test_tool`: Test individual MCP tools
- `mcp_test_resource`: Test individual MCP resources
- `mcp_test_prompt`: Test individual MCP prompts
- `mcp_test_suite`: Run comprehensive test suites

## Quick Start

[Include basic examples]

## Documentation

- [Full Documentation](https://github.com/tosin2013/ansible-collection-mcp-audit/blob/main/README.md)
- [Module Documentation](https://github.com/tosin2013/ansible-collection-mcp-audit/tree/main/docs)
- [ADRs](https://github.com/tosin2013/ansible-collection-mcp-audit/tree/main/docs/adrs)

## Support

- [Issue Tracker](https://github.com/tosin2013/ansible-collection-mcp-audit/issues)
- [Contributing Guide](https://github.com/tosin2013/ansible-collection-mcp-audit/blob/main/CONTRIBUTING.md)

## License

GPL-3.0-or-later (see [COPYING](COPYING))
```

## Alternatives Considered

### Use `community.mcp_audit` Namespace
- **Pros**: Aligns with community.* collection pattern
- **Cons**: Longer FQCN, requires community.* namespace approval
- **Verdict**: Rejected - already decided in ADR-0001 to use `mcp.audit`

### No galaxy.yml Dependencies
- **Pros**: Simplest approach, no dependency conflicts
- **Cons**: If dependencies are needed later, requires major version bump
- **Verdict**: Accepted - start with no dependencies, add only if needed (documented in ADR-0016)

### Pre-release Versions for Initial Releases
- **Pros**: Signals that collection is not production-ready
- **Cons**: Harder to discover on Galaxy, may deter early adopters
- **Verdict**: Rejected - start with 1.0.0 once all tests pass and documentation is complete

### Manual Publishing Only
- **Pros**: More control over release process
- **Cons**: Error-prone, inconsistent, slows down releases
- **Verdict**: Rejected - automate publishing via CI/CD for consistency

### Include Development Docs in Build
- **Pros**: Users can see full development history
- **Cons**: Increases build size, may confuse users with internal docs
- **Verdict**: Rejected - use build_ignore to exclude development-only files (PRD, GAPS-ANALYSIS)

## References

- [Ansible Galaxy Collection Publishing](https://docs.ansible.com/ansible/latest/dev_guide/collections_galaxy_meta.html)
- [galaxy.yml Reference](https://docs.ansible.com/ansible/latest/dev_guide/collections_galaxy_meta.html#galaxy-yml)
- [Semantic Versioning 2.0.0](https://semver.org/)
- [ansible-galaxy CLI Reference](https://docs.ansible.com/ansible/latest/cli/ansible-galaxy.html)
- [community.general galaxy.yml](https://github.com/ansible-collections/community.general/blob/main/galaxy.yml)
- [community.docker galaxy.yml](https://github.com/ansible-collections/community.docker/blob/main/galaxy.yml)

## Review and Update Schedule
- **Before each release**: Verify galaxy.yml accuracy, bump version
- **On dependency addition**: Update dependencies section, document in ADR-0016
- **Quarterly**: Review tags for relevance and Galaxy search optimization
- **On breaking changes**: Ensure semantic versioning is followed correctly
- **Annually**: Review build_ignore patterns for outdated entries
