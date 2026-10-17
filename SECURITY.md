# Security policy

OpenRoute is an early-stage project. Do not rely on it as a security or anonymity tool.

## Reporting

Please do not post credentials, private tokens, or sensitive personal data in public issues. Until a private security contact is configured, report only non-sensitive reproducible issues in GitHub Issues and label them `security` where available.

## Current prototype boundaries

- No administrator/root access is required.
- No background service, VPN, proxy, persistence, or system configuration changes.
- The Windows diagnostic prototype makes DNS and HTTPS requests only to destinations visible in `windows/app.py`.
- Test results may be incomplete or misleading on networks with captive portals, firewalls, proxies, outages, or filtering.

Before a public binary release, maintainers should inspect dependencies, build from a clean environment, publish SHA-256 checksums, and sign artifacts where feasible.
