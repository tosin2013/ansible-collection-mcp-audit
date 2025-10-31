# ADR-0011: Code Quality Tools

## Status
Accepted

## Context
Consistent code quality is essential for maintainability, collaboration, and community trust. The collection requires automated tools to enforce:
- **Python code quality**: Linting, formatting, type checking
- **Ansible-specific quality**: Module standards, playbook best practices
- **YAML formatting**: Consistent indentation and structure
- **Import organization**: Consistent import ordering
- **Documentation quality**: Complete and accurate module docs

Code quality considerations:
- **Automation**: Tools must integrate with CI/CD (see ADR-0012)
- **Pre-commit**: Developers should catch issues before committing
- **Galaxy requirements**: ansible-test sanity must pass
- **Community standards**: Follow Ansible and Python ecosystem best practices
- **Developer experience**: Fast feedback,

 clear error messages
- **Modern tooling**: Use actively maintained, performant tools

Industry standards from successful collections:
- **community.general**: ansible-lint, yamllint, flake8, pylint
- **community.docker**: Comprehensive sanity tests
- **Modern Python projects**: ruff (fast linter/formatter), mypy (type checking), black (formatting)

## Decision
We will implement a **comprehensive code quality toolchain** with modern, fast tools:

### 1. Tool Selection

| Tool | Purpose | Priority | Rationale |
|------|---------|----------|-----------|
| **ansible-test** | Ansible sanity tests | P0 | Required by Galaxy, comprehensive Ansible-specific checks |
| **ruff** | Python linting & formatting | P0 | Modern, fast (10-100x faster than flake8), replaces multiple tools |
| **mypy** | Python type checking | P0 | Catch type errors, improve code quality |
| **yamllint** | YAML linting | P0 | Consistent YAML formatting |
| **ansible-lint** | Ansible best practices | P1 | Ansible-specific linting beyond ansible-test |
| **reuse** | License compliance | P1 | REUSE spec compliance (see ADR-0008) |

**Not Selected:**
- **flake8**: Replaced by ruff (faster, more features)
- **black**: Replaced by ruff (formatting included)
- **isort**: Replaced by ruff (import sorting included)
- **pylint**: Too slow, overlaps with ruff

### 2. Ruff Configuration

**Why Ruff?**
- 10-100x faster than flake8/pylint
- Combines linting + formatting + import sorting
- Drop-in replacement for flake8, black, isort
- Actively maintained, modern Python support
- Excellent error messages

#### Configuration File
```toml
# pyproject.toml
[tool.ruff]
target-version = "py39"  # Minimum Python version (ADR-0013)
line-length = 120
exclude = [
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "*.egg-info",
]

[tool.ruff.lint]
# Enable comprehensive rule sets
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "N",      # pep8-naming
    "UP",     # pyupgrade
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "SIM",    # flake8-simplify
    "RUF",    # Ruff-specific rules
]
ignore = [
    "E501",   # Line too long (handled by formatter)
    "B008",   # Do not perform function call in argument defaults
]

[tool.ruff.lint.per-file-ignores]
"plugins/modules/*.py" = [
    "N802",   # Ansible modules use lowercase function names
]
"tests/*" = [
    "S101",   # Allow assert in tests
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "lf"
```

#### Usage
```bash
# Lint code
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .

# Check formatting without changes
ruff format --check .
```

### 3. Mypy Configuration

**Type Checking Strategy**: Gradual typing
- Start with basic type hints
- Increase strictness over time
- Focus on module_utils first (most reusable code)

#### Configuration File
```toml
# pyproject.toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # Start lenient, increase later
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_optional = true

# Per-module configuration
[[tool.mypy.overrides]]
module = "plugins.module_utils.*"
disallow_untyped_defs = true  # Strict for shared code

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false  # Lenient for tests
```

#### Usage
```bash
# Type check all code
mypy plugins/

# Type check with strict mode
mypy --strict plugins/module_utils/
```

### 4. YAML Lint Configuration

#### Configuration File
```yaml
# .yamllint
---
extends: default

rules:
  line-length:
    max: 120
    level: warning

  indentation:
    spaces: 2
    indent-sequences: true

  comments:
    min-spaces-from-content: 1

  comments-indentation: {}

  document-start:
    present: true

  truthy:
    allowed-values: ['true', 'false', 'yes', 'no']

ignore: |
  .github/
  .venv/
  build/
```

#### Usage
```bash
# Lint all YAML files
yamllint .

# Lint specific files
yamllint galaxy.yml playbooks/*.yml
```

### 5. Ansible-Lint Configuration

#### Configuration File
```yaml
# .ansible-lint
---
profile: production  # Strictest profile

exclude_paths:
  - .github/
  - tests/output/
  - .venv/

skip_list:
  - experimental  # Skip experimental rules
  - jinja[spacing]  # Allow flexible Jinja spacing

warn_list:
  - unnamed-task  # Warn but don't fail on unnamed tasks

kinds:
  - yaml: "*.yaml.j2"
  - yaml: "*.yml.j2"

# Enable all rules by default
enable_list:
  - args
  - empty-string-compare
  - no-log-password
  - no-same-owner
```

#### Usage
```bash
# Lint all Ansible content
ansible-lint

# Lint specific playbook
ansible-lint playbooks/test.yml

# Auto-fix issues
ansible-lint --fix
```

### 6. Ansible-Test Sanity

**Required Tests** (Galaxy submission requirements):
```bash
# Run all sanity tests
ansible-test sanity --docker

# Run specific tests
ansible-test sanity --test validate-modules
ansible-test sanity --test pep8
ansible-test sanity --test pylint
ansible-test sanity --test yamllint

# Test specific Python version
ansible-test sanity --python 3.9
```

**Key Sanity Tests:**
- **validate-modules**: Module DOCUMENTATION/EXAMPLES/RETURN validation
- **pep8**: Python style compliance
- **pylint**: Advanced Python linting
- **yamllint**: YAML formatting
- **import**: Import statement validation
- **compile**: Python compilation check
- **shellcheck**: Shell script linting (if any)

### 7. REUSE License Compliance

#### Configuration
```toml
# .reuse/dep5 or REUSE.toml (see ADR-0008)
version = 1

[[annotations]]
path = ["plugins/modules/**.py", "plugins/module_utils/**.py"]
SPDX-FileCopyrightText = "2025 Tosin Akinosho <tosin.akinosho@gmail.com>"
SPDX-License-Identifier = "GPL-3.0-or-later"
```

#### Usage
```bash
# Check license compliance
reuse lint

# Add license headers
reuse annotate --license GPL-3.0-or-later --copyright "Tosin Akinosho" file.py
```

### 8. Pre-Commit Configuration

**Automated quality checks before commit**:

#### Configuration File
```yaml
# .pre-commit-config.yaml
---
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-PyYAML]
        args: [--config-file=pyproject.toml]

  - repo: https://github.com/adrienverge/yamllint
    rev: v1.35.1
    hooks:
      - id: yamllint

  - repo: https://github.com/ansible/ansible-lint
    rev: v24.2.0
    hooks:
      - id: ansible-lint
        files: \.(yaml|yml)$

  - repo: https://github.com/fsfe/reuse-tool
    rev: v3.0.1
    hooks:
      - id: reuse

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
```

#### Setup
```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

### 9. Development Workflow

#### Initial Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# requirements-dev.txt content:
# ruff>=0.3.0
# mypy>=1.8.0
# yamllint>=1.35.0
# ansible-lint>=24.2.0
# reuse>=3.0.0
# pre-commit>=3.6.0
# pytest>=7.4.0
# pytest-ansible>=3.1.0
# ansible-test

# Set up pre-commit hooks
pre-commit install
```

#### Before Committing
```bash
# Run all quality checks
make quality  # Or use pre-commit

# Or run individually:
ruff check --fix .
ruff format .
mypy plugins/
yamllint .
ansible-lint
reuse lint
```

#### Makefile for Convenience
```makefile
# Makefile
.PHONY: quality format lint type-check test

quality: format lint type-check

format:
	ruff format .

lint:
	ruff check --fix .
	yamllint .
	ansible-lint

type-check:
	mypy plugins/

test:
	pytest tests/unit/
	ansible-test integration

sanity:
	ansible-test sanity --docker

ci: quality sanity test
```

## Consequences

### Positive
- **Fast feedback**: Ruff is 10-100x faster than legacy tools
- **Comprehensive**: Multiple tools cover different quality aspects
- **Automated**: Pre-commit hooks catch issues before commit
- **CI/CD ready**: All tools integrate with GitHub Actions (ADR-0012)
- **Galaxy compliant**: ansible-test sanity ensures Galaxy requirements
- **Type safety**: Mypy catches type-related bugs early
- **Consistent style**: Automated formatting eliminates style debates
- **License compliance**: REUSE ensures licensing is correct (ADR-0008)

### Negative
- **Tool overhead**: Multiple tools to learn and maintain
- **Configuration complexity**: Each tool has its own config file
- **Pre-commit slowdown**: Hooks add 5-10 seconds to commit time
- **False positives**: Linters may flag acceptable code (use ignore comments)
- **Dependency management**: Tools must be kept up-to-date

### Neutral
- Tool selection follows modern Python best practices
- Pre-commit is optional but highly recommended
- Some tools overlap (ruff + ansible-test both check Python style)

## Implementation Notes

### CI/CD Integration (Preview - See ADR-0012)
```yaml
# .github/workflows/quality.yml
name: Code Quality
on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements-dev.txt

      - name: Run ruff
        run: |
          ruff check .
          ruff format --check .

      - name: Run mypy
        run: mypy plugins/

      - name: Run yamllint
        run: yamllint .

      - name: Run ansible-lint
        run: ansible-lint

      - name: Run ansible-test sanity
        run: ansible-test sanity --docker

      - name: Check REUSE compliance
        run: reuse lint
```

### Ignoring False Positives

#### Inline Ignores (Use Sparingly)
```python
# Ruff ignore
some_code()  # noqa: E501

# Mypy ignore
value = function()  # type: ignore[return-value]

# Multiple tools
problematic_line()  # noqa: E501  # type: ignore
```

#### File-Level Ignores
```python
# ruff: noqa: E501
# mypy: ignore-errors

# Rest of file...
```

### Code Review Checklist
```markdown
## Code Quality Checklist

- [ ] `ruff check .` passes
- [ ] `ruff format --check .` passes
- [ ] `mypy plugins/` passes (or type ignores justified)
- [ ] `yamllint .` passes
- [ ] `ansible-lint` passes
- [ ] `ansible-test sanity` passes
- [ ] `reuse lint` passes
- [ ] Pre-commit hooks installed and passing
```

## Alternatives Considered

### Flake8 + Black + isort
- **Pros**: Well-established, widely used
- **Cons**: Slow (multiple separate tools), requires 3 config files
- **Verdict**: Rejected - ruff is faster and simpler

### Pylint Only
- **Pros**: Very comprehensive linting
- **Cons**: Very slow, many false positives, difficult configuration
- **Verdict**: Rejected - ruff provides similar coverage with better performance

### No Type Checking (Skip Mypy)
- **Pros**: Less overhead, faster development
- **Cons**: Type errors caught late, reduced code quality
- **Verdict**: Rejected - type checking catches bugs early

### Manual Code Review Only
- **Pros**: No tooling overhead
- **Cons**: Inconsistent, subjective, time-consuming, error-prone
- **Verdict**: Rejected - automation is essential for quality

### Stricter Mypy from Start
- **Pros**: Maximum type safety from day one
- **Cons**: High barrier for contributors, slower initial development
- **Verdict**: Rejected - gradual typing is more pragmatic

## References

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [yamllint Documentation](https://yamllint.readthedocs.io/)
- [ansible-lint Documentation](https://ansible.readthedocs.io/projects/lint/)
- [ansible-test Documentation](https://docs.ansible.com/ansible/latest/dev_guide/testing.html)
- [pre-commit Documentation](https://pre-commit.com/)
- [REUSE Specification](https://reuse.software/spec/)

## Review and Update Schedule
- **Quarterly**: Update tool versions (pre-commit autoupdate)
- **On new Python release**: Test compatibility with new Python version
- **On tool breaking changes**: Adjust configuration as needed
- **Annually**: Review rule sets for effectiveness
- **On community feedback**: Adjust rules if causing friction
