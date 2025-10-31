# ADR-0010: Changelog Management

## Status
Accepted

## Context
Maintaining an accurate, comprehensive changelog is essential for:
- **User awareness**: Users need to know what changed between versions
- **Upgrade planning**: Clear breaking changes and deprecation notices
- **Community transparency**: Open development process visibility
- **Galaxy requirements**: Ansible Galaxy displays changelog information
- **Release automation**: Automated changelog generation reduces manual errors

Changelog considerations:
- **Format**: reStructuredText (CHANGELOG.rst) is Ansible Galaxy standard
- **Automation**: Manual changelog maintenance is error-prone and time-consuming
- **Fragment-based**: Each PR contributes a changelog fragment
- **Categorization**: Changes categorized by type (features, bugfixes, breaking changes, etc.)
- **Semantic versioning**: Changelog aligns with version numbers (see ADR-0014)

Industry standards from successful collections:
- **community.general**: Uses antsibull-changelog with detailed fragments
- **community.docker**: Automated CHANGELOG.rst generation
- **Ansible-core**: Fragment-based approach with strict categorization

## Decision
We will use **antsibull-changelog** for automated changelog generation with fragment-based contributions:

### 1. Changelog Tool Selection

**Tool**: `antsibull-changelog`
- **Rationale**: Official Ansible changelog tool, Galaxy-compatible, widely adopted
- **Installation**: `pip install antsibull-changelog`
- **Output**: Generates CHANGELOG.rst (required) and CHANGELOG.md (optional)

### 2. Changelog Fragment Structure

#### Fragment Directory Structure
```
changelogs/
├── config.yaml                  # antsibull-changelog configuration
├── changelog.yaml              # Machine-readable changelog (generated)
├── fragments/                  # Changelog fragments (one per PR)
│   ├── 123-add-sse-support.yml
│   ├── 124-fix-stdio-error.yml
│   └── 125-deprecate-old-param.yml
├── CHANGELOG.rst              # Generated, committed
└── CHANGELOG.md               # Optional, generated
```

#### Fragment Categories
```yaml
# changelogs/config.yaml
---
changelog_filename_template: CHANGELOG-%s.rst
changelog_filename_version_depth: 0
changes_file: changelog.yaml
changes_format: combined
keep_fragments: true
mention_ancestor: true
new_plugins_after_name: removed_features
notesdir: fragments
prelude_section_name: release_summary
prelude_section_title: Release Summary
sanitize_changelog: true
sections:
  - - release_summary
    - Release Summary
  - - major_changes
    - Major Changes
  - - minor_changes
    - Minor Changes
  - - breaking_changes
    - Breaking Changes / Porting Guide
  - - deprecated_features
    - Deprecated Features
  - - removed_features
    - Removed Features (previously deprecated)
  - - security_fixes
    - Security Fixes
  - - bugfixes
    - Bugfixes
  - - known_issues
    - Known Issues
title: MCP Audit Collection
trivial_section_name: trivial
use_fqcn: true
```

#### Fragment Template
```yaml
# changelogs/fragments/PR_NUMBER-short-description.yml
---
# Choose ONE or more categories:

release_summary: |
  Brief release summary (only for releases, not individual PRs)

major_changes:
  - Description of major change (breaking or significant new feature)

minor_changes:
  - Description of minor change (new feature, enhancement)

breaking_changes:
  - Description of breaking change with migration guidance

deprecated_features:
  - module_name - parameter_name will be removed in version 3.0.0. Use new_parameter instead.

removed_features:
  - module_name - parameter_name has been removed (deprecated in 1.5.0)

security_fixes:
  - module_name - Fixed vulnerability CVE-XXXX-XXXXX (https://link-to-advisory)

bugfixes:
  - module_name - Fixed issue with X when Y (https://github.com/tosin2013/ansible-collection-mcp-audit/issues/123)

known_issues:
  - module_name - Known issue with X under conditions Y. Workaround: Z.
```

### 3. Fragment Naming Convention

**Format**: `PR_NUMBER-brief-description.yml`

**Examples**:
- `123-add-http-transport.yml` - New feature
- `124-fix-stdio-timeout.yml` - Bug fix
- `125-deprecate-old-param.yml` - Deprecation
- `126-update-dependencies.yml` - Dependency update

**Trivial Changes** (no fragment needed):
- Documentation-only changes
- Typo fixes in comments
- Test-only changes
- CI/CD configuration changes

For trivial changes, use `(trivial)` in PR title or commit message.

### 4. Changelog Generation Workflow

#### For Each PR (Contributor)
```bash
# 1. Create changelog fragment
cat > changelogs/fragments/123-add-feature.yml <<EOF
---
minor_changes:
  - mcp_test_tool - Added support for timeout parameter to prevent hanging on slow servers.
EOF

# 2. Commit fragment with code changes
git add changelogs/fragments/123-add-feature.yml
git commit -m "feat: add timeout parameter to mcp_test_tool"
```

#### For Each Release (Maintainer)
```bash
# 1. Generate changelog for new version
antsibull-changelog release --version 1.1.0

# 2. Review generated CHANGELOG.rst
cat CHANGELOG.rst

# 3. Commit generated files
git add changelogs/CHANGELOG.rst changelogs/changelog.yaml
git commit -m "chore: generate changelog for 1.1.0"

# 4. Create git tag (see ADR-0014)
git tag v1.1.0
git push origin v1.1.0
```

#### Automated in CI/CD
```yaml
# .github/workflows/release.yml
name: Release
on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Need full history

      - name: Install antsibull-changelog
        run: pip install antsibull-changelog

      - name: Generate changelog
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          antsibull-changelog release --version $VERSION

      - name: Commit changelog
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add changelogs/
          git commit -m "chore: generate changelog for $VERSION" || true
          git push
```

### 5. Changelog Content Guidelines

#### Writing Style
- **Audience**: End users, not developers
- **Clarity**: Describe impact, not implementation
- **Completeness**: Include issue/PR links for context
- **Action-oriented**: Use verbs (Added, Fixed, Removed, Deprecated)

#### Good Examples
```yaml
minor_changes:
  - mcp_test_tool - Added ``timeout`` parameter to prevent hanging on slow servers (https://github.com/tosin2013/ansible-collection-mcp-audit/pull/123).

bugfixes:
  - mcp_server_info - Fixed connection error when server closes stdio stream unexpectedly (https://github.com/tosin2013/ansible-collection-mcp-audit/issues/45).

breaking_changes:
  - mcp_test_suite - The ``report_format`` parameter now defaults to ``json`` instead of ``yaml``. Update playbooks that rely on YAML output (https://github.com/tosin2013/ansible-collection-mcp-audit/pull/67).
```

#### Bad Examples
```yaml
# Too vague
minor_changes:
  - Improved error handling

# Too technical
bugfixes:
  - Fixed NoneType exception in _validate_response() method

# Missing context
deprecated_features:
  - old_parameter will be removed soon
```

### 6. Release Notes Process

#### Release Summary (Major/Minor Releases Only)
```yaml
# changelogs/fragments/1.1.0-release.yml
---
release_summary: |
  Release 1.1.0 introduces HTTP transport support, improved error handling,
  and several bug fixes. This release maintains backward compatibility with 1.0.x.

  Notable changes:
  - HTTP transport now supports authentication
  - Better timeout handling for slow servers
  - Fixed critical bug in resource validation
```

#### Generating Release Notes for GitHub
```bash
# Extract release notes from CHANGELOG.rst
antsibull-changelog generate --version 1.1.0 --output release-notes.md

# Use in GitHub release
gh release create v1.1.0 --title "Release 1.1.0" --notes-file release-notes.md
```

### 7. Version-Specific Changelogs

#### Backport Process
```bash
# For patch releases to older minor versions
git checkout stable-1.0
git cherry-pick <commit-hash>

# Create fragment in backport branch
cat > changelogs/fragments/200-backport-fix.yml <<EOF
---
bugfixes:
  - mcp_test_tool - Backported fix for timeout issue from 1.1.0
EOF

# Generate patch release changelog
antsibull-changelog release --version 1.0.5
```

## Consequences

### Positive
- **Automation**: Changelog generation is automated and consistent
- **Accuracy**: Fragment-based approach reduces missed changes
- **Galaxy compatible**: CHANGELOG.rst format required by Ansible Galaxy
- **User-friendly**: Clear categorization helps users find relevant changes
- **CI/CD integrated**: Changelog generation part of release pipeline
- **Transparency**: Every change documented with PR/issue links
- **Maintainable**: Distributed contribution (each PR adds fragment)
- **Searchable**: Machine-readable changelog.yaml enables tooling

### Negative
- **Contributor overhead**: Every PR requires changelog fragment (except trivial)
- **Review burden**: Changelog fragments must be reviewed for clarity
- **Tool dependency**: Requires antsibull-changelog installation
- **Learning curve**: Contributors must learn fragment format
- **Fragment conflicts**: Multiple PRs may conflict on fragment filenames (rare)

### Neutral
- Fragment-based approach is standard for Ansible collections
- reStructuredText is the required format (not our choice)
- antsibull-changelog is the de facto standard

## Implementation Notes

### Initial Setup
```bash
# 1. Install antsibull-changelog
pip install antsibull-changelog

# 2. Initialize changelog
mkdir -p changelogs/fragments
antsibull-changelog init .

# 3. Customize config
# Edit changelogs/config.yaml to match project

# 4. Create initial release fragment
cat > changelogs/fragments/1.0.0-initial.yml <<EOF
---
release_summary: |
  Initial release of the MCP Audit Ansible Collection.

  This collection provides modules for testing and auditing Model Context Protocol (MCP)
  servers with support for stdio, SSE, and HTTP transports.

major_changes:
  - Initial release with 5 modules for MCP server testing
  - Support for stdio, SSE, and HTTP transports
  - Comprehensive test reporting in JSON format
  - RHEL 9 and RHEL 10 compatibility
EOF

# 5. Generate initial CHANGELOG.rst
antsibull-changelog release --version 1.0.0

# 6. Commit
git add changelogs/
git commit -m "chore: initialize changelog"
```

### PR Template Addition
```markdown
<!-- .github/pull_request_template.md -->

## Changelog

- [ ] This change requires a changelog fragment (most changes do)
- [ ] This is a trivial change (docs, tests, typos only - no fragment needed)

If changelog fragment is required:
- [ ] Created `changelogs/fragments/PR_NUMBER-description.yml`
- [ ] Fragment follows format guidelines
- [ ] Fragment clearly describes user-facing impact
```

### CI/CD Fragment Validation
```yaml
# .github/workflows/changelog.yml
name: Changelog
on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install antsibull-changelog
        run: pip install antsibull-changelog

      - name: Check for changelog fragment
        run: |
          PR_NUMBER=${{ github.event.pull_request.number }}
          TITLE="${{ github.event.pull_request.title }}"

          # Skip if trivial
          if [[ "$TITLE" == *"(trivial)"* ]]; then
            echo "Trivial change, skipping changelog check"
            exit 0
          fi

          # Check for fragment
          if ! ls changelogs/fragments/${PR_NUMBER}-*.yml 2>/dev/null; then
            echo "ERROR: Changelog fragment required for non-trivial changes"
            echo "Create: changelogs/fragments/${PR_NUMBER}-description.yml"
            exit 1
          fi

      - name: Lint changelog
        run: antsibull-changelog lint
```

### Release Checklist
```markdown
## Release Checklist

- [ ] All PRs have changelog fragments (or marked trivial)
- [ ] Version bumped in galaxy.yml (see ADR-0014)
- [ ] Run: `antsibull-changelog release --version X.Y.Z`
- [ ] Review generated CHANGELOG.rst for accuracy
- [ ] Commit: `git add changelogs/ && git commit -m "chore: release X.Y.Z"`
- [ ] Tag: `git tag vX.Y.Z`
- [ ] Push: `git push && git push --tags`
- [ ] Create GitHub release with changelog excerpt
- [ ] Publish to Galaxy (see ADR-0014)
```

### Fragment Examples by Category

#### Major Changes
```yaml
# changelogs/fragments/150-http-transport.yml
---
major_changes:
  - All modules now support HTTP transport in addition to stdio and SSE, enabling testing of HTTP-based MCP servers (https://github.com/tosin2013/ansible-collection-mcp-audit/pull/150).
```

#### Breaking Changes
```yaml
# changelogs/fragments/175-remove-old-param.yml
---
breaking_changes:
  - mcp_test_tool - Removed deprecated ``legacy_mode`` parameter. Use ``transport`` parameter instead. Playbooks using ``legacy_mode`` must be updated (https://github.com/tosin2013/ansible-collection-mcp-audit/pull/175).
```

#### Deprecation
```yaml
# changelogs/fragments/180-deprecate-yaml.yml
---
deprecated_features:
  - mcp_test_suite - The ``report_format=yaml`` option is deprecated and will be removed in version 3.0.0. Use ``report_format=json`` and convert output if YAML is needed (https://github.com/tosin2013/ansible-collection-mcp-audit/pull/180).
```

#### Security Fix
```yaml
# changelogs/fragments/200-security-fix.yml
---
security_fixes:
  - mcp_server_info - Fixed command injection vulnerability when using user-supplied ``server_command`` parameter. Always validate and sanitize server commands (https://github.com/tosin2013/ansible-collection-mcp-audit/security/advisories/GHSA-xxxx-xxxx).
```

## Alternatives Considered

### Manual CHANGELOG.md Maintenance
- **Pros**: Simple, no tools required, full control
- **Cons**: Error-prone, often forgotten, inconsistent format, merge conflicts
- **Verdict**: Rejected - doesn't scale, not Galaxy-standard

### Conventional Commits Only
- **Pros**: Changelog generated from commit messages
- **Cons**: Not Ansible-standard, difficult to categorize properly, lacks user-facing language
- **Verdict**: Rejected - commit messages are developer-focused, not user-focused

### Keep A Changelog Format
- **Pros**: Human-readable, simple format
- **Cons**: Not Ansible Galaxy standard, requires manual maintenance
- **Verdict**: Rejected - not compatible with Galaxy requirements

### GitHub Releases Only
- **Pros**: Built into GitHub, easy to create
- **Cons**: Not in repository, not in collection tarball, not Galaxy-compatible
- **Verdict**: Rejected - need CHANGELOG.rst for Galaxy

### Towncrier (Python Community Tool)
- **Pros**: Similar fragment-based approach
- **Cons**: Not Ansible-standard, different format, less community familiarity
- **Verdict**: Rejected - antsibull-changelog is Ansible ecosystem standard

## References

- [antsibull-changelog Documentation](https://github.com/ansible-community/antsibull-changelog)
- [Ansible Collection Changelog Guidelines](https://docs.ansible.com/ansible/devel/community/collection_development_process.html#generating-changelogs)
- [community.general Changelog](https://github.com/ansible-collections/community.general/tree/main/changelogs)
- [community.docker Changelog](https://github.com/ansible-collections/community.docker/tree/main/changelogs)
- [Semantic Versioning 2.0.0](https://semver.org/)

## Review and Update Schedule
- **Per PR**: Review changelog fragments for clarity and accuracy
- **Per release**: Generate and review full CHANGELOG.rst
- **Quarterly**: Review fragment categories for effectiveness
- **Annually**: Review changelog config for potential improvements
- **On breaking changes**: Ensure clear migration guidance in changelog
