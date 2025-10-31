# ADR-0009: Documentation Strategy

## Status
Accepted

## Context
Comprehensive, accessible documentation is critical for community adoption and user success. The collection requires documentation at multiple levels:
- **Module documentation**: Embedded in code (DOCUMENTATION, EXAMPLES, RETURN blocks)
- **User guides**: Installation, quick start, tutorials
- **Developer documentation**: Contributing, testing, development setup
- **Reference documentation**: Complete module parameter reference
- **API documentation**: For module_utils reuse

Documentation considerations:
- **Ansible standards**: DOCUMENTATION/EXAMPLES/RETURN blocks are mandatory
- **Discoverability**: ansible-doc must display documentation correctly
- **Hosting**: Documentation site for web access
- **Maintenance**: Documentation must stay synchronized with code
- **Accessibility**: Clear, concise, beginner-friendly
- **SEO**: Searchable and indexed by search engines

Industry standards from successful collections:
- **community.general**: Comprehensive docs on docs.ansible.com
- **community.docker**: GitHub Pages + Sphinx
- **Ansible certified content**: ansible-doc + hosted documentation site

## Decision
We will implement a **multi-tiered documentation strategy** with Ansible-standard embedded documentation and optional hosted documentation site:

### 1. Module Documentation (Mandatory)

#### DOCUMENTATION Block (Required by Ansible)
Every module must have a DOCUMENTATION block with:
```python
DOCUMENTATION = r'''
---
module: mcp_server_info
short_description: Gather information about an MCP server
description:
  - Connects to a Model Context Protocol (MCP) server and retrieves capability information.
  - Supports stdio, SSE, and HTTP transports.
  - Returns server name, version, and available capabilities (tools, resources, prompts).
version_added: "1.0.0"
author:
  - Tosin Akinosho (@tosin2013)
options:
  server_command:
    description:
      - Command to execute the MCP server (for stdio transport).
      - Required when I(transport=stdio).
    type: str
    required: false
  server_args:
    description:
      - Arguments to pass to the server command.
      - Used with I(transport=stdio).
    type: list
    elements: str
    required: false
  transport:
    description:
      - Transport protocol to use for MCP communication.
    type: str
    choices: ['stdio', 'sse', 'http']
    default: 'stdio'
  url:
    description:
      - Server URL for SSE or HTTP transports.
      - Required when I(transport=sse) or I(transport=http).
    type: str
    required: false
requirements:
  - python >= 3.9
  - ansible-core >= 2.15.0
  - mcp >= 1.19.0
notes:
  - This module works with SELinux in enforcing mode.
  - No root privileges required.
seealso:
  - module: mcp.audit.mcp_test_tool
  - module: mcp.audit.mcp_test_suite
'''
```

#### EXAMPLES Block (Required by Ansible)
Comprehensive, copy-pasteable examples:
```python
EXAMPLES = r'''
# Gather server info via stdio transport
- name: Get MCP server information
  mcp.audit.mcp_server_info:
    server_command: python
    server_args:
      - /path/to/server.py
    transport: stdio
  register: server_info

- name: Display server capabilities
  ansible.builtin.debug:
    msg: "Server {{ server_info.server_name }} supports: {{ server_info.capabilities }}"

# Gather server info via HTTP transport
- name: Get MCP server info from HTTP endpoint
  mcp.audit.mcp_server_info:
    transport: http
    url: http://localhost:8080/mcp
  register: server_info

# Conditional task based on server capabilities
- name: Test tools only if server supports them
  mcp.audit.mcp_test_tool:
    server_command: python
    server_args:
      - /path/to/server.py
    tool_name: calculate
    tool_arguments:
      a: 5
      b: 3
  when: "'tools' in server_info.capabilities"
'''
```

#### RETURN Block (Required by Ansible)
Complete return value documentation:
```python
RETURN = r'''
server_name:
  description: Name of the MCP server
  returned: success
  type: str
  sample: "calculator-server"
server_version:
  description: Version of the MCP server
  returned: success
  type: str
  sample: "1.0.0"
capabilities:
  description: List of capabilities supported by the server
  returned: success
  type: list
  elements: str
  sample: ["tools", "resources", "prompts"]
tools:
  description: List of available tools
  returned: when tools capability is present
  type: list
  elements: dict
  sample:
    - name: "add"
      description: "Add two numbers"
      input_schema:
        type: "object"
        properties:
          a: {type: "number"}
          b: {type: "number"}
execution_time:
  description: Time taken to gather server info (seconds)
  returned: always
  type: float
  sample: 0.234
'''
```

### 2. README.md (Repository Root)

#### Structure
```markdown
# MCP Audit Ansible Collection

![Galaxy Version](https://img.shields.io/badge/galaxy-mcp.audit-blue)
![Ansible Version](https://img.shields.io/badge/ansible-%3E%3D2.15.0-blue)
![License](https://img.shields.io/badge/license-GPL--3.0--or--later-green)

Ansible collection for testing and auditing Model Context Protocol (MCP) servers.

## Table of Contents
- [Installation](#installation)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Modules](#modules)
- [Examples](#examples)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Installation

### From Ansible Galaxy
```bash
ansible-galaxy collection install mcp.audit
```

### From Source
```bash
git clone https://github.com/tosin2013/ansible-collection-mcp-audit.git
cd ansible-collection-mcp-audit
ansible-galaxy collection build
ansible-galaxy collection install mcp-audit-*.tar.gz
```

## Requirements

- Python 3.9+
- ansible-core 2.15.0+
- MCP Python SDK 1.19.0+

See [Version Compatibility](docs/COMPATIBILITY.md) for full support matrix.

## Quick Start

[Complete quick start guide with working example]

## Modules

| Module | Description |
|--------|-------------|
| [mcp_server_info](docs/modules/mcp_server_info.md) | Gather MCP server information |
| [mcp_test_tool](docs/modules/mcp_test_tool.md) | Test individual MCP tools |
| [mcp_test_resource](docs/modules/mcp_test_resource.md) | Test MCP resources |
| [mcp_test_prompt](docs/modules/mcp_test_prompt.md) | Test MCP prompts |
| [mcp_test_suite](docs/modules/mcp_test_suite.md) | Run comprehensive test suites |

## Examples

[Links to example playbooks]

## Testing

See [TESTING.md](docs/TESTING.md) for development and testing instructions.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

GPL-3.0-or-later. See [COPYING](COPYING) for full license text.

## Support

- [Issue Tracker](https://github.com/tosin2013/ansible-collection-mcp-audit/issues)
- [Discussions](https://github.com/tosin2013/ansible-collection-mcp-audit/discussions)
- [Documentation](https://github.com/tosin2013/ansible-collection-mcp-audit/tree/main/docs)
```

### 3. Extended Documentation (docs/)

#### Directory Structure
```
docs/
├── README.md                           # Documentation index
├── INSTALLATION.md                     # Detailed installation guide
├── QUICK_START.md                      # Tutorial for new users
├── COMPATIBILITY.md                    # Version compatibility matrix
├── TESTING.md                          # Testing guide for contributors
├── TROUBLESHOOTING.md                  # Common issues and solutions
├── RHEL.md                            # RHEL-specific guidance
├── examples/                           # Example playbooks
│   ├── basic-server-test.yml
│   ├── comprehensive-audit.yml
│   ├── multi-transport.yml
│   └── ci-integration.yml
├── modules/                            # Per-module documentation
│   ├── mcp_server_info.md
│   ├── mcp_test_tool.md
│   ├── mcp_test_resource.md
│   ├── mcp_test_prompt.md
│   └── mcp_test_suite.md
└── adrs/                               # Architecture decisions
    └── [ADRs 0001-XXXX]
```

#### Per-Module Documentation (docs/modules/)
Each module gets a dedicated markdown file with:
- **Overview**: What the module does
- **Parameters**: Complete parameter reference (more detailed than DOCUMENTATION block)
- **Examples**: Multiple use cases with explanations
- **Return Values**: Detailed return value documentation
- **Error Handling**: Common errors and solutions
- **Best Practices**: Usage recommendations

Example structure:
```markdown
# mcp_server_info Module

## Overview
[Description and purpose]

## Parameters
[Complete parameter reference with examples]

## Examples
### Basic Usage
[Example with explanation]

### Advanced Usage
[Complex example with explanation]

## Return Values
[Detailed return value documentation]

## Error Handling
[Common errors and solutions]

## Best Practices
[Usage recommendations]

## See Also
[Related modules and resources]
```

### 4. Documentation Hosting Strategy

#### Phase 1: GitHub (Immediate)
- **Platform**: GitHub repository (docs/ directory)
- **Format**: Markdown
- **Access**: https://github.com/tosin2013/ansible-collection-mcp-audit/tree/main/docs
- **Benefits**: No additional infrastructure, version-controlled
- **Limitations**: Basic formatting, no search

#### Phase 2: GitHub Pages (Optional, Future)
- **Platform**: GitHub Pages (gh-pages branch)
- **Generator**: Sphinx or MkDocs
- **URL**: https://tosin2013.github.io/ansible-collection-mcp-audit/
- **Benefits**: Professional appearance, search, navigation
- **Effort**: Moderate (CI/CD automation needed)

#### Phase 3: docs.ansible.com (Long-term Goal)
- **Platform**: Official Ansible documentation site
- **Requirements**: Collection must be widely adopted, community-maintained
- **Benefits**: Maximum visibility, authoritative hosting
- **Timeline**: Post-publication, based on adoption

**Decision for 1.0.0 Release**: Start with Phase 1 (GitHub markdown), optionally add Phase 2 (GitHub Pages) if time permits.

### 5. Documentation Standards

#### Writing Style
- **Tone**: Professional, instructional, friendly
- **Audience**: Ansible users (intermediate level assumed)
- **Clarity**: Short sentences, active voice, concrete examples
- **Completeness**: Every parameter documented, every example explained
- **Accuracy**: Documentation updated with code changes

#### Formatting Standards
- **Markdown**: GitHub-flavored markdown for all docs
- **Code blocks**: Always specify language (```yaml, ```python, ```bash)
- **Links**: Relative links within docs/, absolute for external
- **Tables**: Use for parameter lists, compatibility matrices
- **Admonitions**: Use blockquotes for notes, warnings, tips

#### Parameter Documentation
```markdown
## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `server_command` | str | No* | - | Command to execute the MCP server. Required when `transport=stdio`. |
| `transport` | str | No | `stdio` | Transport protocol. Choices: `stdio`, `sse`, `http`. |
```

### 6. Documentation Maintenance

#### Synchronization Strategy
- **Code changes**: Update documentation in same PR/commit
- **PR requirement**: Documentation updates mandatory for new features
- **Review process**: Documentation reviewed alongside code
- **CI/CD check**: Fail build if DOCUMENTATION blocks are missing/invalid

#### Versioning
- **version_added**: Track which version introduced each option
- **Deprecation notices**: Document deprecated parameters/modules
- **Changelog**: Link documentation to CHANGELOG entries

#### Quality Checks
```yaml
# .github/workflows/docs.yml
name: Documentation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Validate module documentation
        run: |
          ansible-test sanity --test validate-modules

      - name: Check ansible-doc
        run: |
          for module in plugins/modules/*.py; do
            ansible-doc mcp.audit.$(basename $module .py) || exit 1
          done

      - name: Lint markdown
        run: |
          pip install markdownlint-cli2
          markdownlint-cli2 "**/*.md"
```

## Consequences

### Positive
- **Ansible compliance**: DOCUMENTATION/EXAMPLES/RETURN blocks meet Galaxy requirements
- **User-friendly**: Comprehensive examples and tutorials reduce support burden
- **Discoverability**: ansible-doc provides instant access to documentation
- **Maintainability**: Documentation lives with code, easy to keep synchronized
- **Professional**: Multi-tiered approach serves all user levels
- **SEO-ready**: Markdown documentation is searchable and indexable
- **Scalable**: Can add hosted documentation (GitHub Pages) later without refactoring

### Negative
- **Maintenance burden**: Documentation must be updated with every code change
- **Initial effort**: Comprehensive documentation requires significant upfront work
- **Duplication**: Some content duplicated between embedded docs and markdown files
- **CI/CD complexity**: Documentation validation adds to pipeline execution time
- **Hosted docs deferred**: Phase 2 (GitHub Pages) not included in 1.0.0 timeline

### Neutral
- Markdown-first approach is standard for Ansible collections
- Documentation structure follows community collection patterns
- GitHub hosting is sufficient for initial release

## Implementation Notes

### Module Documentation Template
```python
# plugins/modules/template.py
#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Tosin Akinosho <tosin@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: module_name
short_description: [One-line description]
description:
  - [Detailed description paragraph 1]
  - [Detailed description paragraph 2]
version_added: "1.0.0"
author:
  - Tosin Akinosho (@tosin2013)
options:
  parameter_name:
    description:
      - [Parameter description]
    type: str
    required: true
requirements:
  - python >= 3.9
  - ansible-core >= 2.15.0
  - mcp >= 1.19.0
notes:
  - [Important usage notes]
seealso:
  - module: mcp.audit.related_module
'''

EXAMPLES = r'''
# [Example description]
- name: [Task name]
  mcp.audit.module_name:
    parameter_name: value
  register: result
'''

RETURN = r'''
field_name:
  description: [Field description]
  returned: always
  type: str
  sample: "example value"
'''
```

### Documentation PR Checklist
```markdown
## Documentation Checklist

- [ ] Module DOCUMENTATION block complete and accurate
- [ ] Module EXAMPLES block includes multiple use cases
- [ ] Module RETURN block documents all return values
- [ ] docs/modules/[module_name].md created/updated
- [ ] README.md updated (if adding new module)
- [ ] ansible-doc displays documentation correctly
- [ ] ansible-test sanity --test validate-modules passes
- [ ] CHANGELOG fragment created (see ADR-0010)
```

### Documentation Review Guidelines
```markdown
## Documentation Review Checklist

### Completeness
- [ ] All parameters documented with type, required, default
- [ ] At least 2 examples provided
- [ ] All return values documented
- [ ] Error handling documented

### Accuracy
- [ ] Examples are copy-pasteable and work
- [ ] Parameter types match implementation
- [ ] Return value samples are realistic
- [ ] version_added is correct

### Clarity
- [ ] Short description is clear and concise
- [ ] Parameter descriptions explain purpose, not just repeat name
- [ ] Examples include explanatory task names
- [ ] No jargon without explanation

### Style
- [ ] Follows Ansible documentation style guide
- [ ] Consistent terminology throughout
- [ ] Proper use of I() for option names
- [ ] Proper use of M() for module names
```

## Alternatives Considered

### Sphinx + Read the Docs
- **Pros**: Professional documentation site, excellent search, versioning
- **Cons**: Requires reStructuredText conversion, additional infrastructure, steeper learning curve
- **Verdict**: Rejected for 1.0.0 - Markdown-first is simpler, can migrate later if needed

### MkDocs + GitHub Pages
- **Pros**: Markdown-native, beautiful themes, easy setup
- **Cons**: Requires CI/CD setup, adds build step
- **Verdict**: Deferred to post-1.0.0 (Phase 2) - good option for future enhancement

### Documentation-Only Repository
- **Pros**: Separation of concerns, dedicated docs team
- **Cons**: Synchronization challenges, duplication, slower updates
- **Verdict**: Rejected - documentation should live with code

### Wiki for User Guides
- **Pros**: Easy community contributions, low barrier
- **Cons**: Not version-controlled, quality inconsistency, no CI/CD
- **Verdict**: Rejected - wikis difficult to maintain and keep accurate

### ansible-doc Only (No Extended Docs)
- **Pros**: Zero additional work, Ansible-native
- **Cons**: Limited formatting, no tutorials, no examples directory
- **Verdict**: Rejected - insufficient for community adoption

## References

- [Ansible Module Documentation Guidelines](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_documenting.html)
- [Ansible Documentation Style Guide](https://docs.ansible.com/ansible/latest/community/documentation_contributions.html)
- [community.general Documentation](https://docs.ansible.com/ansible/latest/collections/community/general/)
- [community.docker Documentation](https://docs.ansible.com/ansible/latest/collections/community/docker/)
- [GitHub Flavored Markdown Spec](https://github.github.com/gfm/)
- [MkDocs](https://www.mkdocs.org/)
- [Sphinx](https://www.sphinx-doc.org/)

## Review and Update Schedule
- **Per release**: Review all documentation for accuracy
- **Quarterly**: Review extended docs for relevance
- **On deprecation**: Add deprecation notices to affected documentation
- **On new module**: Create complete documentation set following template
- **Post-1.0.0**: Evaluate adding GitHub Pages (Phase 2)
