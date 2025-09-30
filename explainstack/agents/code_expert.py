"""Code Expert Agent for explaining Python code."""

from .base_agent import BaseAgent


class CodeExpertAgent(BaseAgent):
    """Agent specialized in explaining Python code."""
    
    def __init__(self, backend):
        super().__init__(
            name="Code Expert",
            description="Expert in explaining Python code, especially OpenStack projects",
            backend=backend
        )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for code explanation."""
        return """You are an expert Python developer and OpenStack contributor with deep knowledge of:
- Python best practices and patterns
- OpenStack architecture and conventions
- Code documentation standards
- Performance optimization techniques
- Security considerations in Python code

Your task is to analyze Python code and provide:
1. Clear, concise explanations of what the code does
2. Line-by-line or block-by-block breakdowns
3. Identification of potential issues or improvements
4. Suggestions for better documentation
5. OpenStack-specific context when relevant

Always be professional, helpful, and focus on educational value."""
    
    def get_user_prompt(self, user_input: str) -> str:
        """Get the user prompt for code explanation."""
        return f"""Please analyze and explain this Python code:

```python
{user_input}
```

Provide your analysis in the following structure:

- 📝 **Summary**: What this code does in 1-2 sentences
- 🔍 **Detailed Explanation**: Line-by-line or block-by-block breakdown
- 💡 **Key Insights**: Important patterns, techniques, or concepts used
- 📘 **Suggested Docstring**: A professional docstring for the main function/class
- ⚠️ **Potential Issues**: Any problems or improvements you notice
- 🚀 **OpenStack Context**: How this relates to OpenStack development (if applicable)

Focus on being educational and helping the developer understand both the code and best practices."""
