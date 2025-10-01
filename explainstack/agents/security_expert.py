"""Security Expert Agent for vulnerability analysis and security best practices."""

from .base_agent import BaseAgent


class SecurityExpertAgent(BaseAgent):
    """Agent specialized in security analysis and vulnerability detection."""
    
    def __init__(self, backend):
        super().__init__(
            name="Security Expert",
            description="Expert in security analysis, vulnerability detection, and OpenStack security best practices",
            backend=backend
        )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for security analysis."""
        return """You are a cybersecurity expert specializing in OpenStack security with deep knowledge of:

- OpenStack security architecture and best practices
- Common vulnerabilities in cloud infrastructure (CVE, OWASP Top 10)
- Python security patterns and anti-patterns
- OpenStack-specific security concerns (keystone, nova, neutron, etc.)
- Secure coding practices for cloud platforms
- Authentication and authorization security
- Data encryption and secure communication
- Security compliance (SOC2, ISO 27001, etc.)

Your task is to analyze code for security issues and provide:
1. Vulnerability assessment with severity levels
2. Security best practices recommendations
3. OpenStack-specific security considerations
4. Remediation suggestions with code examples
5. Compliance and regulatory considerations

Always prioritize security over convenience and provide actionable recommendations."""
    
    def get_user_prompt(self, user_input: str) -> str:
        """Get the user prompt for security analysis."""
        return f"""Please perform a comprehensive security analysis of this code:

```python
{user_input}
```

Provide your security analysis in the following structure:

- 🔒 **Security Summary**: Overall security assessment
- ⚠️ **Vulnerabilities Found**: List of security issues with severity levels
- 🛡️ **Security Best Practices**: Recommendations for improvement
- 🔐 **OpenStack Security**: Specific OpenStack security considerations
- 📋 **Compliance Notes**: Regulatory and compliance considerations
- 🔧 **Remediation Steps**: Specific actions to fix security issues
- 📚 **Additional Resources**: Links to security documentation and tools

Focus on:
- Input validation and sanitization
- Authentication and authorization
- Data encryption and secure storage
- Network security and communication
- Error handling and information disclosure
- OpenStack-specific security patterns
- Compliance with security standards

Be thorough but practical in your recommendations."""
