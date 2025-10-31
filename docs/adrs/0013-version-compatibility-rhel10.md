# ADR-0013: Version Compatibility and RHEL 10 Support

## Status
Accepted

## Context
The collection must support a range of Python and Ansible versions to serve both the community and potential enterprise adoption, particularly targeting RHEL 10 integration.

Key considerations:
- **Community support**: Wide Python/Ansible version compatibility
- **RHEL 10 readiness**: Python 3.12+ expected in RHEL 10 (beta announcement)
- **RHEL 9 compatibility**: Python 3.9 is the system Python
- **Enterprise requirements**: System Python support (no venv requirement)
- **SELinux**: All modules must function correctly with SELinux enabled
- **Long-term support**: Clear EOL policy for version support
- **Testing resources**: CI/CD must test multiple version combinations

Current landscape (January 2025):
- **Python**: 3.9 (RHEL 9), 3.11 (Ubuntu 22.04), 3.12 (Ubuntu 24.04, expected RHEL 10)
- **Ansible-core**: 2.15 (stable), 2.16 (current), 2.17 (development)
- **RHEL 10 Beta**: Available, Python 3.12 expected in GA
- **ansible-core 2.15**: Requires Python 3.9+

## Decision
We will implement a **tiered version support strategy** with explicit RHEL 10 compatibility:

### 1. Python Version Support

#### Minimum Supported Version
- **Python 3.9+** (aligns with ansible-core 2.15 requirements)
- **Rationale**:
  - RHEL 9 system Python is 3.9
  - ansible-core 2.15+ requires Python 3.9+
  - Balances compatibility with modern Python features

#### Maximum Tested Version
- **Python 3.13** (latest stable as of January 2025)
- **RHEL 10 Target**: Python 3.12+ (expected GA version)

#### Support Matrix
| Python Version | Support Status | Notes |
|----------------|----------------|-------|
| 3.9 | ✅ Full Support | RHEL 9 system Python, minimum version |
| 3.10 | ✅ Full Support | Ubuntu 22.04 default |
| 3.11 | ✅ Full Support | Current stable |
| 3.12 | ✅ Full Support | RHEL 10 expected, Ubuntu 24.04 default |
| 3.13 | ✅ Full Support | Latest stable, forward compatibility |
| 3.8 | ❌ Not Supported | EOL October 2024, incompatible with ansible-core 2.15+ |

### 2. Ansible Version Support

#### Minimum Supported Version
- **ansible-core 2.15.0+**
- **Rationale**:
  - Stable release with Python 3.9+ support
  - Feature-complete for collection development
  - Widely deployed in production environments

#### Maximum Tested Version
- **ansible-core 2.17** (development/next stable)

#### Support Matrix
| Ansible Version | Support Status | Notes |
|-----------------|----------------|-------|
| ansible-core 2.15 | ✅ Full Support | Minimum version, stable |
| ansible-core 2.16 | ✅ Full Support | Current stable |
| ansible-core 2.17 | ✅ Full Support | Latest/development |
| ansible-core 2.14 | ❌ Not Supported | EOL, requires Python 3.8 |

### 3. RHEL Compatibility Requirements

#### RHEL 9
- **Python**: 3.9 (system Python)
- **Testing**: Regular CI/CD testing on CentOS Stream 9
- **SELinux**: All modules tested with SELinux enforcing
- **Package Dependencies**: Must work with system-provided packages

#### RHEL 10
- **Python**: 3.12+ (expected GA version)
- **Testing**:
  - Beta testing on RHEL 10 Beta and CentOS Stream 10
  - Pre-release validation before RHEL 10 GA
- **SELinux**: All modules tested with SELinux enforcing
- **FIPS**: Optional FIPS mode compatibility testing
- **Architecture**: Test on both x86_64 and aarch64

#### System Python Requirement
- **No venv required**: Collection must work with system Python
- **Rationale**: Enterprise environments often restrict venv creation
- **Dependencies**: Only use packages available via system package manager or `ansible.builtin.pip`

### 4. Version EOL Policy

#### Python Version EOL
- **Support period**: Maintain support for Python versions until 6 months after upstream EOL
- **Deprecation notice**: Announce 1 version ahead (e.g., announce 3.9 deprecation when 3.14 is released)
- **Example**: Python 3.9 EOL is October 2025 → Collection drops 3.9 support in April 2026

#### Ansible Version EOL
- **Support period**: Support ansible-core versions for 12 months after release
- **Minimum**: Always support at least 3 ansible-core minor versions
- **Example**: When 2.18 is released, continue supporting 2.15, 2.16, 2.17

### 5. Dependency Version Constraints

#### Core Dependencies
```txt
# requirements.txt
ansible-core>=2.15.0,<3.0.0
mcp>=1.19.0
python-dateutil>=2.8.0  # Available in RHEL repos
```

#### Optional Dependencies (for development/testing)
```txt
# requirements-dev.txt
pytest>=7.4.0
pytest-ansible>=3.1.0
ansible-lint>=6.20.0
```

## Consequences

### Positive
- **RHEL 10 ready**: Explicit Python 3.12+ support ensures RHEL 10 compatibility
- **RHEL 9 compatible**: Python 3.9 support covers current enterprise deployments
- **Wide compatibility**: Supports 5 Python versions (3.9-3.13)
- **Future-proof**: Testing latest Python/Ansible ensures forward compatibility
- **Clear expectations**: Support matrix clearly documents version compatibility
- **Enterprise friendly**: System Python support enables enterprise adoption
- **Long-term support**: EOL policy provides predictable support lifecycle

### Negative
- **Testing complexity**: Must test 5 Python × 3 Ansible version combinations = 15 test configurations
- **Maintenance burden**: Supporting multiple versions requires more careful coding
- **Feature limitations**: Can't use Python 3.10+ features in core code
- **CI/CD resources**: More test matrix cells = longer CI/CD execution time
- **RHEL 10 uncertainty**: RHEL 10 GA Python version could differ from beta

### Neutral
- Python 3.9 is minimum but older than ideal (3.10+ preferred for features)
- ansible-core 2.15 is minimum but mature and stable
- System Python requirement is standard for RHEL-focused collections

## Implementation Notes

### galaxy.yml Version Requirements
```yaml
namespace: mcp
name: audit
version: 1.0.0

# Ansible version requirements
requires_ansible: '>=2.15.0'

# Python version documented in README
# (galaxy.yml doesn't have python_requires field)
```

### Module Python Version Declaration
```python
# plugins/modules/mcp_server_info.py

#!/usr/bin/python
# -*- coding: utf-8 -*-

# Requires Python 3.9+
# Requires ansible-core 2.15+

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: mcp_server_info
requirements:
  - python >= 3.9
  - ansible-core >= 2.15.0
  - mcp >= 1.19.0
'''
```

### README Version Matrix
```markdown
## Requirements

### Minimum Versions
- Python 3.9+
- ansible-core 2.15.0+
- MCP Python SDK 1.19.0+

### Supported Versions
| Component | Versions | Notes |
|-----------|----------|-------|
| Python | 3.9, 3.10, 3.11, 3.12, 3.13 | System Python supported |
| ansible-core | 2.15, 2.16, 2.17 | Latest 3 stable versions |
| RHEL | 9, 10 (beta) | Full compatibility |

### RHEL Compatibility
- **RHEL 9**: Python 3.9 (system Python)
- **RHEL 10**: Python 3.12+ (expected GA version)
- **SELinux**: All modules work with SELinux enforcing
- **System Python**: No venv required
```

### CI/CD Test Matrix
```yaml
# .github/workflows/test.yml
name: Test Collection
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12', '3.13']
        ansible-version: ['2.15', '2.16', '2.17']
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install Ansible ${{ matrix.ansible-version }}
        run: |
          pip install "ansible-core>=${{ matrix.ansible-version }},<${{ matrix.ansible-version }}.99"

      - name: Run tests
        run: |
          ansible-test units --python ${{ matrix.python-version }}
          ansible-test integration --python ${{ matrix.python-version }}

  rhel-test:
    runs-on: ubuntu-latest
    container:
      image: quay.io/centos/centos:stream9
    steps:
      - uses: actions/checkout@v3

      - name: Install system dependencies
        run: |
          dnf install -y python3.9 python3-pip ansible-core

      - name: Run tests with system Python
        run: |
          python3.9 -m pip install --user -r requirements.txt
          ansible-test integration

  rhel10-test:
    runs-on: ubuntu-latest
    container:
      image: quay.io/centos/centos:stream10
    continue-on-error: true  # RHEL 10 is still in beta
    steps:
      - uses: actions/checkout@v3

      - name: Install system dependencies
        run: |
          dnf install -y python3 python3-pip ansible-core

      - name: Run tests with RHEL 10 Python
        run: |
          python3 -m pip install --user -r requirements.txt
          ansible-test integration
```

### SELinux Testing
```yaml
# tests/integration/selinux-test.yml
---
- name: SELinux compatibility test
  hosts: localhost
  tasks:
    - name: Check SELinux status
      command: getenforce
      register: selinux_status
      changed_when: false

    - name: Ensure SELinux is enforcing
      assert:
        that:
          - selinux_status.stdout == "Enforcing"
        fail_msg: "SELinux must be enforcing for this test"

    - name: Test mcp_server_info with SELinux
      mcp.audit.mcp_server_info:
        server_command: "python3"
        server_args:
          - "/tmp/test_server.py"
        transport: "stdio"
      register: result

    - name: Verify no SELinux denials
      command: ausearch -m avc -ts recent
      register: avc_denials
      changed_when: false
      failed_when: "'mcp' in avc_denials.stdout"
```

### Python Version Feature Detection
For code that may benefit from newer Python features:
```python
import sys

# Use match/case (Python 3.10+) if available, else if/elif
if sys.version_info >= (3, 10):
    # Use match/case syntax
    pass
else:
    # Use if/elif syntax
    pass
```

### Dependency Compatibility Checking
```bash
# scripts/check_versions.sh
#!/bin/bash
set -e

echo "Checking Python version compatibility..."
python3 -c "import sys; assert sys.version_info >= (3, 9), 'Python 3.9+ required'"

echo "Checking Ansible version compatibility..."
ansible --version | grep "ansible \[core" | grep -E "(2\.15|2\.16|2\.17)"

echo "Checking MCP SDK version..."
python3 -c "import mcp; print(f'MCP SDK: {mcp.__version__}')"

echo "All version checks passed!"
```

### RHEL 10 Beta Testing Plan
1. **Monthly testing**: Test on latest CentOS Stream 10 builds
2. **Compatibility tracking**: Document any Python 3.12 specific issues
3. **Early adoption**: Engage with RHEL 10 beta program for testing access
4. **Documentation**: Maintain RHEL 10 compatibility notes in docs/RHEL10.md

## Alternatives Considered

### Python 3.10+ Only
- **Pros**: Access to modern Python features (match/case, better typing)
- **Cons**: Excludes RHEL 9 (Python 3.9), limits enterprise adoption
- **Verdict**: Rejected - RHEL 9 support is critical

### Support Python 3.8
- **Pros**: Wider compatibility (Ubuntu 20.04)
- **Cons**: Python 3.8 EOL October 2024, ansible-core 2.15+ requires 3.9+
- **Verdict**: Rejected - EOL version, incompatible with ansible-core 2.15+

### ansible-core 2.14 Support
- **Pros**: Wider Ansible version compatibility
- **Cons**: 2.14 approaching EOL, requires Python 3.8 support
- **Verdict**: Rejected - focus on supported Ansible versions

### Require venv for Dependencies
- **Pros**: Isolated environment, easier dependency management
- **Cons**: Not suitable for enterprise/RHEL environments with restricted policies
- **Verdict**: Rejected - system Python support is enterprise requirement

### Test Only Latest Python/Ansible
- **Pros**: Simpler CI/CD, faster tests
- **Cons**: Breaks on older versions, limits adoption
- **Verdict**: Rejected - version compatibility is critical for community/enterprise use

## References

- [Python Release Schedule](https://peps.python.org/pep-0569/) - Python 3.9 EOL October 2025
- [Python 3.12 Release Notes](https://docs.python.org/3.12/whatsnew/3.12.html)
- [ansible-core Roadmap](https://docs.ansible.com/ansible/devel/roadmap/ansible_core_roadmap_index.html)
- [RHEL 10 Beta Announcement](https://www.redhat.com/en/blog/introducing-red-hat-enterprise-linux-10-beta)
- [RHEL 9 Python](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/installing_and_using_dynamic_programming_languages/assembly_installing-and-using-python_installing-and-using-dynamic-programming-languages)
- [CentOS Stream 9](https://www.centos.org/centos-stream/)
- [CentOS Stream 10](https://www.centos.org/centos-stream/)

## Review and Update Schedule
- **Before RHEL 10 GA**: Validate Python 3.12 compatibility on final release
- **Quarterly**: Review Python/Ansible EOL dates and update support matrix
- **On new Ansible release**: Test compatibility within 30 days
- **Annually**: Review EOL policy and adjust if needed
- **On Python 3.14 release**: Begin planning Python 3.9 deprecation
