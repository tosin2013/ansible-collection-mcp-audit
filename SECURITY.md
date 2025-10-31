# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          | End of Support |
| ------- | ------------------ | -------------- |
| 1.x.x   | :white_check_mark: | TBD            |
| < 1.0   | :x:                | 2024-01-01     |

**Policy**: We support the latest major version and the previous major version for 12 months after a new major version is released.

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities using one of these methods:

### GitHub Private Vulnerability Reporting (Preferred)
1. Go to the [Security tab](https://github.com/tosin2013/ansible-collection-mcp-audit/security)
2. Click "Report a vulnerability"
3. Fill out the form with details

### Email
If you prefer email, send to: **tosin.akinosho@gmail.com**
- Subject line: `[SECURITY] MCP Audit Collection: [Brief Description]`
- Include:
  - Description of the vulnerability
  - Steps to reproduce
  - Potential impact
  - Suggested fix (if any)

### What to Expect
- **Initial Response**: Within 48 hours
- **Status Update**: Within 5 business days
- **Fix Timeline**:
  - Critical: Within 7 days
  - High: Within 14 days
  - Medium: Within 30 days
  - Low: Next regular release

### Disclosure Process
1. **Private Discussion**: We'll work with you privately to understand and fix the issue
2. **Fix Development**: We'll develop a fix and test it
3. **Advisory Creation**: We'll create a GitHub Security Advisory
4. **Coordinated Release**: We'll release the fix and publish the advisory
5. **CVE Assignment**: For significant vulnerabilities, we'll request a CVE

### Recognition
- We'll credit you in the security advisory (unless you prefer to remain anonymous)
- Your name will be added to our CONTRIBUTORS file

### Bug Bounty
Currently, we do not offer a paid bug bounty program. This is an open-source project maintained by volunteers.

## Security Best Practices for Users

### Installation
```bash
# Always verify the collection before installation
ansible-galaxy collection install mcp.audit --force

# Check the installed version
ansible-galaxy collection list | grep mcp.audit
```

### Usage
- **Principle of Least Privilege**: Run playbooks with minimum required permissions
- **Input Validation**: Always validate user-supplied inputs to modules
- **Secrets Management**: Use Ansible Vault for sensitive data
- **Regular Updates**: Keep the collection updated to the latest version

```yaml
# Use Ansible Vault for sensitive data
- name: Test MCP server with credentials
  mcp.audit.mcp_server_info:
    url: https://mcp.example.com
    auth_token: "{{ vault_mcp_token }}"
```

## Security Features

### Built-in Security
- **No Privileged Operations**: Modules do not require root/sudo
- **SELinux Compatible**: Works with SELinux in enforcing mode
- **Input Sanitization**: All inputs are validated and sanitized
- **Secure Defaults**: Secure defaults for all parameters
- **Timeout Protection**: Configurable timeouts prevent hanging

### Dependency Security
- **Regular Scans**: Dependabot scans dependencies weekly
- **Minimal Dependencies**: Only essential dependencies included
- **Version Pinning**: Dependencies pinned to secure versions

## Known Security Limitations

### Limitations
1. **Server Trust**: Modules trust the MCP server they connect to. Use only trusted servers.
2. **Command Injection Risk**: When using `server_command` parameter, ensure the command is from a trusted source.
3. **Network Security**: When using HTTP/SSE transports, use HTTPS and verify certificates.

### Mitigations
```yaml
# Example: Secure MCP server testing
- name: Test MCP server securely
  mcp.audit.mcp_server_info:
    transport: http
    url: https://mcp.example.com  # Always use HTTPS
    verify_ssl: true               # Verify SSL certificates
    timeout: 30                    # Set reasonable timeout
```

## Security Updates

### Update Notifications
- **GitHub Watch**: Star/watch the repository for security updates
- **GitHub Security Advisories**: Subscribe to advisories
- **Ansible Galaxy**: Collection updates shown on Galaxy page
- **RSS Feed**: Subscribe to release RSS feed

### Update Process
```bash
# Check for updates
ansible-galaxy collection list mcp.audit

# Update to latest version
ansible-galaxy collection install mcp.audit --force

# Review changelog for security fixes
cat ~/.ansible/collections/ansible_collections/mcp/audit/CHANGELOG.rst
```

## Third-Party Dependencies

### Current Dependencies
- **MCP Python SDK** (>= 1.19.0): Official MCP SDK
- **ansible-core** (>= 2.15.0): Ansible automation platform

### Dependency Monitoring
- Dependabot: Automated dependency updates
- Weekly scans for new vulnerabilities
- Immediate updates for critical vulnerabilities

## Security Scanning

### Automated Scans
- **CodeQL**: Weekly code security analysis
- **Dependabot**: Daily dependency vulnerability checks
- **TruffleHog**: Secret scanning on every commit
- **ansible-test**: Security-focused sanity tests

### Manual Reviews
- Security review for all PRs touching security-sensitive code
- Annual comprehensive security audit
- Penetration testing before major releases

## Contact

- **Security Issues**: tosin.akinosho@gmail.com (private)
- **General Questions**: [GitHub Discussions](https://github.com/tosin2013/ansible-collection-mcp-audit/discussions)
- **Maintainer**: @tosin2013

---

**Last Updated**: 2025-01-15
**Version**: 1.0
