# Security Policy

## Reporting Security Vulnerabilities

**Please do NOT open public issues for security vulnerabilities!**

If you discover a security vulnerability in EVCC Scheduler, please report it privately:

### How to Report

1. **Email**: Contact the maintainer at your-email@example.com
2. **GitHub Private Security Advisory**: https://github.com/diestrohs/ha-evcc-scheduler/security/advisories
3. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Assessment**: Within 1 week
- **Fix & Release**: Depends on severity
  - Critical: Within 1-2 weeks
  - High: Within 1 month
  - Medium/Low: Next regular release

## Security Best Practices

### For Users

1. **Keep Updated**: Regularly update EVCC Scheduler
2. **Protect EVCC Token**: Never share EVCC API tokens
3. **Network Security**: EVCC should be on trusted network (or use VPN)
4. **Firewall Rules**: Restrict access to EVCC API port (7070)
5. **HTTPS/SSL**: Enable SSL in config if available

### For Developers

1. **No Hardcoded Secrets**: Never commit API keys or tokens
2. **Input Validation**: Always validate user inputs
3. **Error Messages**: Don't leak sensitive info in error messages
4. **Dependencies**: Keep aiohttp and Home Assistant updated
5. **Code Review**: Request review before merging security fixes

## Known Issues

Currently, no known security vulnerabilities.

If you find one, please report it as described above.

## Security Dependencies

### Critical Dependencies

- **aiohttp** >= 3.8.0: HTTP client library (no known CVEs)
- **Home Assistant**: 2025.12.0+
- **Python**: 3.11+

Monitor:
- https://github.com/aio-libs/aiohttp/security
- https://home-assistant.io/security/

## SSL/TLS Support

If your EVCC instance uses SSL/TLS:

1. Enable SSL in config: `ssl: true`
2. Ensure valid certificates
3. If self-signed: Use `verify_ssl: false` (not recommended for production)

## Token Security

- EVCC tokens are stored in Home Assistant's secure config storage
- **Never** commit tokens to git
- Use `.gitignore` to exclude `configuration.yaml` if it contains secrets
- Use Home Assistant's built-in secret management (if available)

## Updating Dependencies

Regular updates are performed to address security issues:

```bash
# Check for vulnerabilities:
pip install safety
safety check

# Update dependencies:
pip install --upgrade aiohttp
```

## Security Contact

- **Maintainer**: @diestrohs
- **Email**: your-email@example.com
- **Discord**: HACS Community

---

**Last Updated**: January 2026  
**Status**: No active security issues
