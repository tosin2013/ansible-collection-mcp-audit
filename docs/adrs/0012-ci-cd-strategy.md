# ADR-0012: CI/CD Strategy

## Status
Accepted

## Context
Continuous Integration and Continuous Deployment (CI/CD) is essential for maintaining code quality, preventing regressions, and automating releases. The collection requires:
- **Automated testing**: Unit, integration, and sanity tests on every commit
- **Multi-version testing**: Python 3.9-3.13 × ansible-core 2.15-2.17 compatibility
- **Code quality gates**: Linting, type checking, REUSE compliance (see ADR-0011)
- **Security scanning**: Dependency vulnerabilities, code security issues
- **Automated releases**: Galaxy publication, GitHub releases, changelog generation
- **RHEL testing**: CentOS Stream 9 and 10 compatibility (see ADR-0013)

CI/CD considerations:
- **Platform choice**: GitHub Actions vs Azure Pipelines vs Jenkins
- **Test matrix**: Balance coverage vs execution time and cost
- **Docker usage**: Containerized testing for consistency
- **Caching**: Speed up builds with intelligent caching
- **Cost**: GitHub Actions has free tier limits (2000 minutes/month for public repos)
- **Community familiarity**: Most contributors know GitHub Actions

Industry standards from successful collections:
- **community.general**: GitHub Actions + Azure Pipelines (redundancy, comprehensive)
- **community.docker**: GitHub Actions primary, extensive matrix testing
- **ansible-core**: Comprehensive CI with multiple cloud providers

## Decision
We will use **GitHub Actions as the primary CI/CD platform** with a comprehensive test matrix and automated release workflow:

### 1. Platform Selection

**Primary: GitHub Actions**
- **Rationale**: Native to GitHub, free for public repos, excellent ecosystem, easy to maintain
- **Usage**: All standard CI/CD workflows (tests, quality, security, releases)

**Secondary: None initially**
- **Rationale**: GitHub Actions sufficient for initial release, add redundancy later if needed
- **Future consideration**: Azure Pipelines for additional coverage if project grows

### 2. CI/CD Workflow Structure

#### Workflow Organization
```
.github/workflows/
├── test.yml                    # Unit and integration tests
├── quality.yml                 # Code quality checks (ruff, mypy, yamllint, ansible-lint)
├── sanity.yml                  # ansible-test sanity
├── security.yml                # Security scanning (Dependabot, CodeQL)
├── rhel.yml                    # RHEL compatibility testing
├── release.yml                 # Automated releases to Galaxy
├── changelog.yml               # Changelog fragment validation
└── docs.yml                    # Documentation validation
```

### 3. Test Matrix Strategy

#### Core Test Matrix (test.yml)
```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12', '3.13']
    ansible-version: ['2.15', '2.16', '2.17']
    exclude:
      # Reduce matrix size (15 → 9 combinations)
      - python-version: '3.10'
        ansible-version: '2.15'
      - python-version: '3.10'
        ansible-version: '2.16'
      - python-version: '3.11'
        ansible-version: '2.15'
      - python-version: '3.12'
        ansible-version: '2.15'
      - python-version: '3.13'
        ansible-version: '2.15'
      - python-version: '3.13'
        ansible-version: '2.16'
```

**Rationale**: Test boundary versions (minimum, maximum) and all Ansible versions on mid-range Python.

#### RHEL Test Matrix (rhel.yml)
```yaml
strategy:
  matrix:
    include:
      - os: CentOS Stream 9
        python: '3.9'
        container: quay.io/centos/centos:stream9
      - os: CentOS Stream 10
        python: '3.12'
        container: quay.io/centos/centos:stream10
```

### 4. Complete Workflow Definitions

#### Test Workflow (test.yml)
```yaml
name: Tests
on:
  push:
    branches: [main, stable-*]
  pull_request:
    branches: [main, stable-*]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ['3.9', '3.11', '3.13']
        ansible-version: ['2.15', '2.16', '2.17']
        exclude:
          - python-version: '3.13'
            ansible-version: '2.15'

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install Ansible ${{ matrix.ansible-version }}
        run: |
          pip install "ansible-core>=${{ matrix.ansible-version }},<${{ matrix.ansible-version }}.99"

      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt

      - name: Run unit tests
        run: pytest tests/unit/ -v --cov --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
          flags: unit-tests
          name: py${{ matrix.python-version }}-ansible${{ matrix.ansible-version }}

  integration-tests:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ['3.9', '3.11', '3.13']
        ansible-version: ['2.15', '2.17']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install Ansible
        run: pip install "ansible-core>=${{ matrix.ansible-version }}"

      - name: Install collection dependencies
        run: pip install -r requirements.txt

      - name: Set up test MCP servers
        run: |
          cd tests/integration/sample_servers
          pip install -r calculator/requirements.txt
          pip install -r prompts/requirements.txt
          pip install -r resources/requirements.txt

      - name: Run integration tests
        run: ansible-test integration --docker --python ${{ matrix.python-version }}
```

#### Code Quality Workflow (quality.yml)
```yaml
name: Code Quality
on: [push, pull_request]

jobs:
  ruff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: chartboost/ruff-action@v1
        with:
          args: check --output-format=github
      - uses: chartboost/ruff-action@v1
        with:
          args: format --check

  mypy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - run: pip install mypy types-PyYAML
      - run: mypy plugins/

  yamllint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install yamllint
      - run: yamllint .

  ansible-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install ansible-lint
      - run: ansible-lint

  reuse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: fsfe/reuse-action@v3
```

#### Sanity Tests Workflow (sanity.yml)
```yaml
name: Ansible Sanity
on: [push, pull_request]

jobs:
  sanity:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ['3.9', '3.11', '3.13']
        ansible-version: ['2.15', '2.17']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install Ansible
        run: pip install "ansible-core==${{ matrix.ansible-version }}.*"

      - name: Run ansible-test sanity
        run: |
          ansible-test sanity \
            --docker \
            --python ${{ matrix.python-version }} \
            --skip-test pep8 \
            --skip-test pylint
        # Skip pep8/pylint as we use ruff
```

#### Security Scanning Workflow (security.yml)
```yaml
name: Security
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  codeql:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: python
      - uses: github/codeql-action/autobuild@v3
      - uses: github/codeql-action/analyze@v3

  dependency-review:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      - uses: actions/dependency-review-action@v4

  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: trufflesecurity/trufflehog@main
        with:
          extra_args: --only-verified
```

#### RHEL Compatibility Workflow (rhel.yml)
```yaml
name: RHEL Compatibility
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  rhel9:
    runs-on: ubuntu-latest
    container:
      image: quay.io/centos/centos:stream9
    steps:
      - uses: actions/checkout@v4

      - name: Install system dependencies
        run: |
          dnf install -y python3.9 python3-pip

      - name: Install Ansible and dependencies
        run: |
          python3.9 -m pip install --user ansible-core mcp
          python3.9 -m pip install --user -r requirements-dev.txt

      - name: Run tests
        run: |
          python3.9 -m pytest tests/unit/
          ansible-test integration

      - name: Test SELinux
        run: |
          # Verify SELinux is enforcing
          getenforce
          # Run basic module test
          ansible-playbook tests/selinux-test.yml

  rhel10:
    runs-on: ubuntu-latest
    container:
      image: quay.io/centos/centos:stream10
    continue-on-error: true  # RHEL 10 is still in beta
    steps:
      - uses: actions/checkout@v4

      - name: Install system dependencies
        run: dnf install -y python3 python3-pip

      - name: Run tests
        run: |
          python3 -m pip install --user ansible-core mcp
          python3 -m pytest tests/unit/
```

#### Release Workflow (release.yml)
```yaml
name: Release
on:
  release:
    types: [published]

jobs:
  publish-galaxy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install ansible-core antsibull-changelog

      - name: Extract version from tag
        id: version
        run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT

      - name: Generate changelog
        run: antsibull-changelog release --version ${{ steps.version.outputs.VERSION }}

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
        uses: softprops/action-gh-release@v1
        with:
          files: mcp-audit-*.tar.gz

      - name: Commit changelog
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add changelogs/
          git commit -m "chore: update changelog for ${{ steps.version.outputs.VERSION }}"
          git push
```

#### Changelog Fragment Validation (changelog.yml)
```yaml
name: Changelog
on: [pull_request]

jobs:
  validate-fragment:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install antsibull-changelog
        run: pip install antsibull-changelog

      - name: Check for changelog fragment
        run: |
          PR_NUMBER=${{ github.event.pull_request.number }}
          TITLE="${{ github.event.pull_request.title }}"

          if [[ "$TITLE" == *"(trivial)"* ]]; then
            echo "Trivial change, skipping"
            exit 0
          fi

          if ! ls changelogs/fragments/${PR_NUMBER}-*.yml 2>/dev/null; then
            echo "ERROR: Changelog fragment required"
            exit 1
          fi

      - name: Lint changelog
        run: antsibull-changelog lint
```

### 5. Caching Strategy

```yaml
# Example caching in workflows
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'  # Caches pip dependencies

- uses: actions/cache@v4
  with:
    path: ~/.ansible/collections
    key: ansible-collections-${{ hashFiles('galaxy.yml') }}
```

### 6. Branch Protection Rules

**main branch**:
- Require PR reviews (1 reviewer minimum)
- Require status checks to pass:
  - Tests (all matrix combinations)
  - Code Quality (ruff, mypy, yamllint, ansible-lint, reuse)
  - Sanity (ansible-test sanity)
  - Changelog (fragment validation)
- Require branches to be up to date
- No force push
- No deletion

**stable-* branches**:
- Same as main, but allow maintainer bypass for critical fixes

### 7. PR Requirements

```markdown
## Pull Request Checklist

### Code Quality
- [ ] All tests pass locally
- [ ] `ruff check --fix .` applied
- [ ] `ruff format .` applied
- [ ] `mypy plugins/` passes
- [ ] No new ansible-lint warnings

### Documentation
- [ ] Module DOCUMENTATION updated (if applicable)
- [ ] README updated (if applicable)
- [ ] ADR created/updated (for architectural changes)

### Changelog
- [ ] Changelog fragment created: `changelogs/fragments/PR_NUMBER-description.yml`
- [ ] Or PR title includes `(trivial)`

### Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated (if applicable)
- [ ] Tested on Python 3.9 and 3.13
- [ ] Tested on ansible-core 2.15 and 2.17
```

## Consequences

### Positive
- **Automated quality**: Every commit tested and validated
- **Multi-version confidence**: Comprehensive matrix ensures broad compatibility
- **Fast feedback**: CI runs complete in 10-20 minutes
- **RHEL validation**: Explicit CentOS Stream testing
- **Security scanning**: CodeQL and dependency review catch vulnerabilities
- **Automated releases**: One-click Galaxy publication
- **Cost-effective**: GitHub Actions free tier sufficient
- **Developer-friendly**: Clear PR requirements and status checks

### Negative
- **CI time**: Full matrix takes 15-20 minutes
- **Maintenance overhead**: Workflows need updates as tools evolve
- **GitHub coupling**: Tight integration with GitHub (migration would be costly)
- **Matrix complexity**: 9+ test combinations to maintain
- **Cost at scale**: May hit GitHub Actions limits if project grows significantly

### Neutral
- GitHub Actions is the standard for Ansible collections
- Test matrix size is typical for multi-version projects
- Branch protection is standard best practice

## Implementation Notes

### Initial Setup Steps
```bash
# 1. Create workflow directory
mkdir -p .github/workflows

# 2. Add workflow files (test.yml, quality.yml, etc.)
# [Copy workflow definitions from above]

# 3. Set up GitHub secrets
# Settings → Secrets → Actions → New repository secret
# GALAXY_API_KEY: [Your Galaxy API key]

# 4. Configure branch protection
# Settings → Branches → Add rule
# Branch name pattern: main
# [Enable protection settings as documented above]

# 5. Initial PR to test workflows
git checkout -b test-ci
git push origin test-ci
# Open PR, verify all checks run
```

### Monitoring and Maintenance

#### Weekly
- Review failed workflow runs
- Check for workflow warnings
- Monitor GitHub Actions usage

#### Monthly
- Update action versions: `actions/checkout@v4` → `v5`
- Review test matrix for effectiveness
- Check for new security advisories

#### Quarterly
- Update Python/Ansible versions in matrix
- Review and optimize workflow performance
- Update CI/CD strategy based on lessons learned

### Troubleshooting Common Issues

#### Tests Timing Out
```yaml
# Increase timeout in workflow
jobs:
  test:
    timeout-minutes: 30  # Default is 360
```

#### Docker Rate Limiting
```yaml
# Use GitHub Container Registry instead
container:
  image: ghcr.io/ansible/ansible:latest
```

#### Flaky Tests
```yaml
# Retry failed tests
- name: Run tests with retry
  uses: nick-invision/retry@v2
  with:
    timeout_minutes: 10
    max_attempts: 3
    command: pytest tests/
```

## Alternatives Considered

### Azure Pipelines as Primary
- **Pros**: More powerful, better Windows support, more free minutes
- **Cons**: More complex, less community familiarity, separate platform
- **Verdict**: Rejected - GitHub Actions simpler for GitHub-hosted project

### Jenkins Self-Hosted
- **Pros**: Full control, unlimited minutes, powerful
- **Cons**: Infrastructure maintenance, security responsibility, cost
- **Verdict**: Rejected - too much overhead for open-source project

### Travis CI
- **Pros**: Previously popular for open source
- **Cons**: Declining, less integrated, pricing changes
- **Verdict**: Rejected - GitHub Actions more integrated

### GitLab CI
- **Pros**: Powerful, integrated
- **Cons**: Requires GitLab hosting (not GitHub)
- **Verdict**: Not applicable - project hosted on GitHub

### Larger Test Matrix (All Combinations)
- **Pros**: Maximum coverage
- **Cons**: 15 test combinations = 2-3x longer CI time, GitHub Actions minute usage
- **Verdict**: Rejected - current matrix provides sufficient coverage

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Ansible Collection CI/CD Guide](https://docs.ansible.com/ansible/devel/community/collection_contributors/collection_integration_tests.html)
- [community.general CI](https://github.com/ansible-collections/community.general/tree/main/.github/workflows)
- [community.docker CI](https://github.com/ansible-collections/community.docker/tree/main/.github/workflows)
- [GitHub Actions Best Practices](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

## Review and Update Schedule
- **Weekly**: Monitor workflow health and failures
- **Monthly**: Update action versions, review performance
- **Per Python release**: Add new Python version to matrix
- **Per Ansible release**: Add new ansible-core version to matrix
- **Quarterly**: Review matrix effectiveness and optimize
- **On RHEL 10 GA**: Update RHEL testing strategy
