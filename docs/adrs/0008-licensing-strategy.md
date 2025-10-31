# ADR-0008: Licensing Strategy

## Status
Accepted

## Context
Ansible Galaxy requires clear licensing for all collections. The licensing decision affects:
- **Publication eligibility**: Galaxy requires GPL-compatible licenses for modules
- **Code reusability**: module_utils can be used by other collections
- **Community contribution**: Clear licensing encourages contributions
- **Enterprise adoption**: Organizations need clear license terms
- **RHEL integration**: Red Hat requires GPL-compatible licensing

Licensing considerations:
- Ansible modules must be GPL-3.0-or-later per Galaxy requirements
- module_utils should allow reuse in other collections
- License clarity is required for all files
- REUSE specification compliance improves license management
- Community contributions need clear license terms

Industry standards from successful collections:
- **community.general**: GPL-3.0-or-later for all code
- **community.docker**: GPL-3.0-or-later + BSD-2-clause dual licensing
- **ansible-core**: GPL-3.0-or-later

## Decision
We will implement a **dual-licensing strategy** with REUSE compliance:

### 1. Module Licensing
**All Ansible modules** (plugins/modules/):
- **License**: `GPL-3.0-or-later`
- **Rationale**: Required by Ansible Galaxy, ensures community availability
- **SPDX Identifier**: `GPL-3.0-or-later`

### 2. Module Utils Licensing
**All module utilities** (plugins/module_utils/):
- **License**: `GPL-3.0-or-later OR BSD-2-Clause`
- **Rationale**: Dual licensing allows reuse in other collections (BSD) while maintaining GPL compatibility
- **SPDX Identifier**: `GPL-3.0-or-later OR BSD-2-Clause`

### 3. Other Collection Components
**Tests, docs, roles, playbooks**:
- **License**: `GPL-3.0-or-later`
- **SPDX Identifier**: `GPL-3.0-or-later`

### 4. REUSE Compliance
- Use `.reuse/dep5` or `REUSE.toml` for centralized license declarations
- SPDX license identifiers in all source files
- Include full license texts in `LICENSES/` directory

## Consequences

### Positive
- **Galaxy compliant**: Meets all Ansible Galaxy licensing requirements
- **Community friendly**: GPL ensures code remains open and accessible
- **Reusable module_utils**: Dual licensing enables code sharing with other collections
- **Clear attribution**: REUSE compliance provides unambiguous licensing
- **RHEL compatible**: GPL-3.0-or-later aligns with Red Hat requirements
- **Enterprise adoption**: Clear licensing terms build trust with organizations
- **Future-proof**: "or-later" clause provides GPL version flexibility

### Negative
- **GPL restrictions**: GPL requires derivative works to be GPL-licensed
- **Dual licensing complexity**: module_utils require both license headers
- **REUSE tooling**: Requires `reuse` tool for compliance checking
- **Contributor overhead**: Contributors must agree to license terms

### Neutral
- GPL is standard for Ansible collections (not a differentiator)
- REUSE compliance is increasingly common in FOSS projects
- License maintenance is ongoing but minimal effort

## Implementation Notes

### File Structure
```
ansible-collection-mcp-audit/
├── LICENSES/
│   ├── GPL-3.0-or-later.txt
│   └── BSD-2-Clause.txt
├── REUSE.toml
├── COPYING (symlink to LICENSES/GPL-3.0-or-later.txt)
└── plugins/
    ├── modules/
    │   └── mcp_*.py (GPL-3.0-or-later)
    └── module_utils/
        └── mcp_*.py (GPL-3.0-or-later OR BSD-2-Clause)
```

### SPDX License Headers

#### For Modules (GPL-3.0-or-later only)
```python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Your Name <your.email@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: mcp_server_info
short_description: Gather information about an MCP server
description:
  - Connects to an MCP server and retrieves capability information.
author:
  - Your Name (@yourgithub)
'''
```

#### For Module Utils (Dual License)
```python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Your Name <your.email@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later OR BSD-2-Clause

"""
MCP Client Utility

This module_utils can be used under either:
- GPL-3.0-or-later (for use in GPL collections)
- BSD-2-Clause (for use in permissively licensed collections)
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type
```

### REUSE.toml Configuration
```toml
version = 1

[[annotations]]
path = ["plugins/modules/**.py", "tests/**.py", "roles/**.yml"]
SPDX-FileCopyrightText = "2024 Your Name <your.email@example.com>"
SPDX-License-Identifier = "GPL-3.0-or-later"

[[annotations]]
path = "plugins/module_utils/**.py"
SPDX-FileCopyrightText = "2024 Your Name <your.email@example.com>"
SPDX-License-Identifier = "GPL-3.0-or-later OR BSD-2-Clause"

[[annotations]]
path = ["*.md", "docs/**.md"]
SPDX-FileCopyrightText = "2024 Your Name <your.email@example.com>"
SPDX-License-Identifier = "GPL-3.0-or-later"

[[annotations]]
path = "galaxy.yml"
SPDX-FileCopyrightText = "2024 Your Name <your.email@example.com>"
SPDX-License-Identifier = "GPL-3.0-or-later"
```

### galaxy.yml License Configuration
```yaml
namespace: mcp
name: audit
version: 1.0.0
license_file: COPYING

# OR for clarity with dual licensing:
license:
  - GPL-3.0-or-later
```

### License Text Files
1. **Download official license texts**:
```bash
mkdir -p LICENSES
curl -o LICENSES/GPL-3.0-or-later.txt https://www.gnu.org/licenses/gpl-3.0.txt
curl -o LICENSES/BSD-2-Clause.txt https://opensource.org/license/bsd-2-clause
```

2. **Create COPYING symlink** (Galaxy requirement):
```bash
ln -s LICENSES/GPL-3.0-or-later.txt COPYING
```

### REUSE Compliance Checking
Install and run REUSE tools:
```bash
pip install reuse
reuse lint
```

Expected output:
```
# SUMMARY

* Bad licenses: 0
* Deprecated licenses: 0
* Licenses without file extension: 0
* Missing licenses: 0
* Unused licenses: 0
* Used licenses: GPL-3.0-or-later, BSD-2-Clause
* Read errors: 0
* Files with copyright information: 42 / 42
* Files with license information: 42 / 42

Congratulations! Your project is compliant with version 3.0 of the REUSE Specification :-)
```

### Contributor License Agreement (CLA)
**Decision**: No formal CLA required
- **Rationale**: Small community project, GPL provides sufficient protection
- **Alternative**: Require `Signed-off-by` in commits (Developer Certificate of Origin)

```bash
git commit -s -m "feat: add mcp_server_info module"
```

This adds:
```
Signed-off-by: Your Name <your.email@example.com>
```

### LICENSE vs COPYING
- **COPYING**: Traditional name for GPL license file (required by Galaxy)
- **LICENSES/**: Modern REUSE standard for multiple licenses
- **Solution**: Symlink COPYING → LICENSES/GPL-3.0-or-later.txt

### CI/CD License Checking
```yaml
# .github/workflows/license-check.yml
name: License Compliance
on: [push, pull_request]

jobs:
  reuse-compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: fsfe/reuse-action@v1
```

## Alternatives Considered

### GPL-3.0-or-later Only (No Dual Licensing)
- **Pros**: Simpler, single license for everything
- **Cons**: module_utils can't be reused in BSD/MIT collections, limits interoperability
- **Verdict**: Rejected - dual licensing provides better ecosystem integration

### MIT or BSD for Everything
- **Pros**: More permissive, wider reuse
- **Cons**: Not allowed for Ansible modules (Galaxy requirement), doesn't align with Ansible ecosystem
- **Verdict**: Rejected - violates Galaxy requirements

### Apache-2.0
- **Pros**: Patent protection, corporate-friendly
- **Cons**: Not standard for Ansible collections, GPL compatibility questions
- **Verdict**: Rejected - not aligned with Ansible community standards

### No REUSE Compliance
- **Pros**: Less tooling overhead
- **Cons**: Ambiguous licensing for individual files, harder to track attribution
- **Verdict**: Rejected - REUSE compliance is best practice and increasingly expected

### Contributor License Agreement (CLA)
- **Pros**: Legal protection for maintainers
- **Cons**: Barrier to contribution, requires legal infrastructure
- **Verdict**: Rejected for now - can be added later if needed; Developer Certificate of Origin (DCO) with `Signed-off-by` is sufficient

## References

- [Ansible Galaxy Collection Requirements](https://docs.ansible.com/ansible/latest/dev_guide/collections_galaxy_meta.html#licensing)
- [REUSE Specification](https://reuse.software/spec/)
- [SPDX License List](https://spdx.org/licenses/)
- [GPL-3.0-or-later Full Text](https://www.gnu.org/licenses/gpl-3.0.txt)
- [BSD-2-Clause Full Text](https://opensource.org/license/bsd-2-clause)
- [Developer Certificate of Origin](https://developercertificate.org/)
- [community.general License](https://github.com/ansible-collections/community.general/blob/main/COPYING)
- [community.docker License](https://github.com/ansible-collections/community.docker/blob/main/COPYING)

## Review and Update Schedule
- **Before Galaxy publication**: Verify all files have SPDX identifiers
- **Quarterly**: Run `reuse lint` to ensure ongoing compliance
- **On new file creation**: Apply appropriate license header from templates
- **On external code inclusion**: Verify license compatibility and add attribution
