# Security Policy

## Supported Versions

We take security seriously and aim to fix security vulnerabilities as quickly as possible. The following versions are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in MathModelAgent, please report it responsibly:

### Do NOT

- Open a public GitHub issue for security vulnerabilities
- Share the vulnerability publicly before it's been fixed
- Exploit the vulnerability beyond what's necessary to demonstrate it

### DO

1. **Report Privately**: Send details to the project maintainer through:
   - GitHub Security Advisories (preferred)
   - Direct message in QQ Group (699970403)
   - Email to the project maintainer

2. **Provide Details**: Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

3. **Allow Time**: Give us reasonable time to fix the issue before public disclosure

## Security Response Process

1. **Acknowledgment**: We'll acknowledge your report within 48 hours
2. **Investigation**: We'll investigate and assess the severity
3. **Fix Development**: We'll develop and test a fix
4. **Disclosure**: We'll coordinate disclosure with you
5. **Credit**: We'll credit you in the security advisory (unless you prefer anonymity)

## Security Measures

### Code Execution Security

MathModelAgent executes user-provided code, which poses inherent security risks. We've implemented several measures:

1. **Sandboxed Execution**:
   - Local execution uses Jupyter kernels with limited permissions
   - Cloud execution (E2B, Daytona) provides isolated containers

2. **Resource Limits**:
   - Memory limits prevent OOM attacks
   - CPU time limits prevent infinite loops
   - Disk space quotas prevent storage exhaustion

3. **Network Restrictions**:
   - Code execution environments have limited network access
   - No access to internal services

### API Security

1. **Input Validation**: All inputs are validated using Pydantic models
2. **Rate Limiting**: API endpoints have rate limits to prevent abuse
3. **CORS Configuration**: Strict CORS policies for production
4. **Authentication**: API key authentication for LLM access

### Data Privacy

1. **No Data Logging**: User inputs and outputs are not logged to external services
2. **Temporary Storage**: Generated files can be configured to auto-delete
3. **Session Isolation**: Each user's data is isolated
4. **Environment Variables**: Sensitive data stored in environment variables, not code

### Dependencies

1. **Dependency Scanning**: Automated scanning with GitHub Dependabot
2. **Regular Updates**: Dependencies are regularly updated
3. **Security Advisories**: We monitor security advisories for our dependencies

## Security Best Practices for Users

If you're deploying MathModelAgent, follow these best practices:

### For Production Deployment

1. **Use Environment Variables**: Never hardcode API keys or secrets

   ```bash
   # Good
   export OPENAI_API_KEY="your-key-here"
   
   # Bad - Don't do this!
   OPENAI_API_KEY = "sk-..." # in code
   ```

2. **Enable HTTPS**: Use HTTPS in production with valid certificates

3. **Firewall Configuration**: Restrict access to necessary ports only
   - Frontend: 443 (HTTPS) or 80 (HTTP)
   - Backend API: Should not be publicly accessible (use reverse proxy)
   - Redis: Should not be publicly accessible

4. **Update Regularly**: Keep the application and dependencies updated

5. **Monitor Logs**: Regularly check logs for suspicious activity

6. **Backup**: Regularly backup important data

### For Development

1. **Use Different API Keys**: Use separate API keys for development and production

2. **Don't Commit Secrets**: Never commit `.env` files or secrets to version control

   ```bash
   # Make sure these are in .gitignore
   .env
   .env.local
   .env.production
   ```

3. **Review Dependencies**: Be cautious when adding new dependencies

4. **Code Review**: Review code changes, especially in security-sensitive areas

## Known Limitations

1. **Code Execution Risks**: Despite sandboxing, executing arbitrary code always carries some risk
2. **LLM Output**: AI-generated code may contain vulnerabilities
3. **Resource Usage**: Malicious users could potentially waste computational resources

## Security Updates

Security updates are released as soon as possible after a vulnerability is confirmed and fixed. Updates are announced through:

- GitHub Security Advisories
- Release notes
- Community channels (QQ Group, Discord)

## Responsible Disclosure Timeline

- **Day 0**: Vulnerability reported
- **Day 1-2**: Acknowledgment sent
- **Day 3-7**: Investigation and assessment
- **Day 7-30**: Fix development and testing
- **Day 30**: Public disclosure (if fix is ready)

We aim to fix critical vulnerabilities within 30 days. For less severe issues, the timeline may be longer.

## Contact

For security-related inquiries, please use:

- GitHub Security Advisories (preferred)
- Project maintainer through community channels

---

Thank you for helping keep MathModelAgent and its users safe!
