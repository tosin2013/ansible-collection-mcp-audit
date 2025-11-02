# Ansible Galaxy Publishing Guide

This document explains how to publish the `mcp.audit` collection to Ansible Galaxy, both manually and automatically via GitHub Actions.

## Prerequisites

1. **Ansible Galaxy Account**
   - Create an account at https://galaxy.ansible.com/
   - Join or create the `mcp` namespace

2. **Galaxy API Token**
   - Go to https://galaxy.ansible.com/ui/token/
   - Create a new API token
   - Copy the token (you won't be able to see it again)

## GitHub Repository Setup

### 1. Add Galaxy API Token to GitHub Secrets

1. Go to your repository settings: `https://github.com/tosin2013/ansible-collection-mcp-audit/settings/secrets/actions`
2. Click "New repository secret"
3. Name: `ANSIBLE_GALAXY_API_KEY`
4. Value: Paste your Galaxy API token
5. Click "Add secret"

### 2. Create Galaxy Environment (Optional but Recommended)

1. Go to repository settings → Environments
2. Create a new environment named `ansible-galaxy`
3. Configure protection rules:
   - Required reviewers (optional)
   - Wait timer before deployment (optional)
   - Deployment branches: `main` and `v*` tags only

## Publishing Workflow

### Automatic Publishing

The collection is automatically published to Ansible Galaxy when:

1. **Version Tag Push**
   ```bash
   # Bump version in galaxy.yml first
   git add galaxy.yml
   git commit -m "chore: bump version to 1.1.0"
   git tag v1.1.0
   git push origin main --tags
   ```

2. **Dependabot Updates**
   - When dependabot creates a PR with dependency updates
   - After the PR is merged and all CI tests pass
   - The collection is automatically published

3. **Manual Trigger**
   ```
   Go to Actions → Publish to Ansible Galaxy → Run workflow
   Select branch: main
   Enable "Force publish" if needed
   ```

### Manual Publishing

You can also publish manually from your local machine:

```bash
# 1. Build the collection
ansible-galaxy collection build

# 2. Publish to Galaxy
ansible-galaxy collection publish mcp-audit-1.0.0.tar.gz --api-key=YOUR_API_KEY
```

## Version Management

### Semantic Versioning

This collection follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: New functionality (backward compatible)
- **PATCH** version: Bug fixes (backward compatible)

### Version Bump Workflow

1. **Update version in galaxy.yml**
   ```yaml
   version: 1.1.0  # Increment as needed
   ```

2. **Create changelog entry** (optional)
   ```bash
   antsibull-changelog release --version 1.1.0
   ```

3. **Commit and tag**
   ```bash
   git add galaxy.yml changelogs/
   git commit -m "chore: bump version to 1.1.0"
   git tag v1.1.0
   git push origin main --tags
   ```

4. **GitHub Actions will automatically**
   - Run all CI tests
   - Build the collection
   - Publish to Galaxy
   - Create a GitHub release with artifacts

## Publishing Checklist

Before publishing a new version:

- [ ] All tests are passing (Code Quality, Sanity Tests)
- [ ] Version number updated in `galaxy.yml`
- [ ] Changelog updated (if using antsibull-changelog)
- [ ] README.md is up to date
- [ ] All new modules have documentation
- [ ] COPYING license file is included
- [ ] No sensitive information in build (check .gitignore and build_ignore in galaxy.yml)

## Troubleshooting

### "Collection version already exists"

Galaxy doesn't allow re-publishing the same version. You must:
1. Increment the version number in `galaxy.yml`
2. Create a new tag
3. Publish again

### "Invalid token"

Your API token may have expired or been revoked:
1. Generate a new token at https://galaxy.ansible.com/ui/token/
2. Update the `ANSIBLE_GALAXY_API_KEY` secret in GitHub

### "Namespace not found"

Ensure you have access to the `mcp` namespace:
1. Request access from namespace owner
2. Or create the namespace if it doesn't exist

### Build failures

Check the build output for issues:
```bash
ansible-galaxy collection build --verbose
```

Common issues:
- Missing required files (README.md, COPYING)
- Invalid galaxy.yml syntax
- Files outside collection structure

## Resources

- [Ansible Galaxy Documentation](https://docs.ansible.com/ansible/latest/galaxy/user_guide.html)
- [Collection Distribution Guide](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections_distributing.html)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Semantic Versioning](https://semver.org/)
