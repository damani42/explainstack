"""Patch Reviewer Agent for analyzing Gerrit patches."""

from .base_agent import BaseAgent


class PatchReviewerAgent(BaseAgent):
    """Agent specialized in reviewing Gerrit patches."""
    
    def __init__(self, backend):
        super().__init__(
            name="Patch Reviewer",
            description="Expert in reviewing Gerrit patches and OpenStack code changes",
            backend=backend
        )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for patch review."""
        return """You are a senior OpenStack code reviewer with extensive experience in:
- OpenStack development practices and conventions
- Gerrit patch review process
- Code quality standards and best practices
- Security implications of code changes
- Performance impact analysis
- Backward compatibility considerations

Your task is to review patches and provide:
1. High-level summary of changes
2. File-by-file analysis
3. Identification of potential issues
4. Suggestions for improvements
5. Security and performance considerations
6. Compliance with OpenStack guidelines

Be thorough, constructive, and focus on helping improve the code quality."""
    
    def get_user_prompt(self, user_input: str) -> str:
        """Get the user prompt for patch review."""
        return f"""Please review this Gerrit patch:

```
{user_input}
```

Provide a comprehensive review in the following structure:

- 📋 **Summary**: High-level overview of what this patch changes
- 📁 **File-by-File Analysis**: Detailed breakdown of changes in each file
- ✅ **Positive Aspects**: What's done well in this patch
- ⚠️ **Issues Found**: Problems, bugs, or concerns identified
- 🔒 **Security Review**: Security implications and recommendations
- 🚀 **Performance Impact**: Performance considerations and optimizations
- 📝 **Style & Standards**: Compliance with OpenStack HACKING guidelines
- 💡 **Suggestions**: Specific recommendations for improvement
- 🧪 **Testing**: Suggestions for additional tests or validation

Focus on being constructive and helping the developer improve their contribution."""
