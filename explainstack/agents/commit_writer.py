"""Commit Writer Agent for generating professional commit messages."""

from .base_agent import BaseAgent


class CommitWriterAgent(BaseAgent):
    """Agent specialized in writing professional commit messages."""
    
    def __init__(self, config: dict):
        super().__init__(
            name="Commit Writer",
            description="Expert in writing professional commit messages for OpenStack projects",
            config=config
        )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for commit message writing."""
        return """You are an expert Git commit message writer specializing in OpenStack development conventions.

You have deep knowledge of:
- Conventional commit message formats
- OpenStack commit message conventions
- Git best practices and standards
- Project-specific commit message patterns
- Bug tracking integration (Launchpad, GitHub issues)

Your task is to write professional commit messages that:
1. Follow conventional commit format: `type(scope): description`
2. Use present tense and imperative mood
3. Keep the first line under 50 characters
4. Include detailed body when necessary
5. Reference bug numbers when applicable
6. Follow OpenStack-specific conventions
7. Be clear and descriptive

Always provide multiple options when appropriate and explain the reasoning behind your choices."""
    
    def get_user_prompt(self, user_input: str) -> str:
        """Get the user prompt for commit message writing."""
        return f"""Please write a professional commit message for this change:

```
{user_input}
```

**Requirements:**
- Use conventional commit format: `type(scope): description`
- Types: feat, fix, docs, style, refactor, test, chore, perf, ci
- Use present tense ("Add feature" not "Added feature")
- Keep first line under 50 characters
- Add detailed body if needed (separated by blank line)
- Reference bug numbers if applicable: "Fixes: #12345"
- Follow OpenStack conventions

**Response Format:**
- **Commit Message**: [The suggested commit message]
- **Type**: [feat/fix/docs/style/refactor/test/chore/perf/ci]
- **Scope**: [component or module affected]
- **Explanation**: [Why this message works well]
- **Alternative Options**: [Other good commit message options]
- **OpenStack Context**: [How this follows OpenStack conventions]

Focus on creating clear, professional commit messages that help other developers understand the change."""
