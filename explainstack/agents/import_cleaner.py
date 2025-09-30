"""Import Cleaner Agent for organizing Python imports."""

from .base_agent import BaseAgent


class ImportCleanerAgent(BaseAgent):
    """Agent specialized in cleaning and organizing Python imports."""
    
    def __init__(self, backend):
        super().__init__(
            name="Import Cleaner",
            description="Expert in organizing Python imports according to OpenStack standards",
            backend=backend
        )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for import cleaning."""
        return """You are an expert Python developer specializing in import organization and OpenStack HACKING guidelines.

You have deep knowledge of:
- Python import best practices
- PEP 8 import organization
- OpenStack HACKING guidelines for imports
- Import optimization techniques
- Dependency management

Your task is to clean and organize imports by:
1. Removing unused imports
2. Grouping imports correctly (standard library, third-party, local)
3. Sorting imports alphabetically within groups
4. Following OpenStack conventions
5. Preserving important comments
6. Ensuring proper spacing

Always follow OpenStack HACKING guidelines and provide clear explanations of changes made."""
    
    def get_user_prompt(self, user_input: str) -> str:
        """Get the user prompt for import cleaning."""
        return f"""Please clean and organize the imports in this Python code:

```python
{user_input}
```

Provide the cleaned imports following OpenStack HACKING guidelines:

**Requirements:**
1. Remove any unused imports
2. Group imports in this order:
   - Standard library imports
   - Third-party package imports  
   - OpenStack-specific or project-internal imports
3. Sort imports alphabetically within each group
4. Leave one blank line between each group
5. Each import should be on its own line
6. No wildcard imports (import *)
7. No relative imports unless strictly necessary
8. Preserve meaningful comments

**Response Format:**
- **Cleaned Imports**: The reorganized import section
- **Changes Made**: Detailed list of what was changed
- **OpenStack Compliance**: How this follows HACKING guidelines
- **Best Practices**: Additional recommendations for import management

Focus on making the imports clean, organized, and compliant with OpenStack standards."""
