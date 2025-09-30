def explain_code_prompt(code: str) -> str:
    return f"""
You are given a Python code snippet from an OpenStack project.
Your task is to help the user understand it by:

1. Summarizing what the code does.
2. Explaining the logic line by line or block by block.
3. Suggesting a clear and concise docstring (in reStructuredText format if possible).

Here is the code:
```
{code}
```

Provide your answer in the following structure:

- 📝 Summary
- 🔍 Detailed Explanation
- 📘 Suggested Docstring
"""

def explain_patch_prompt(diff: str) -> str:
    return f"""
You are acting as a senior OpenStack code reviewer.

You are given a Gerrit patch in unified diff format.
Please provide:

1. A high-level summary of what this patch changes.
2. A file-by-file breakdown of what’s being modified.
3. Any red flags or unusual patterns.
4. Potential review comments or questions.
5. Suggestions for improvement or documentation.

Here is the patch:
```
{diff}
```
"""

def clean_imports_prompt(code: str) -> str:
    return f"""
You are a Python expert helping clean up a file from an OpenStack project.

Your task is to:
1. Remove any unused imports.
2. Group imports in the following order:
   - Standard library
   - Third-party packages
   - OpenStack-specific or project-internal modules
3. Leave one blank line between each group.
4. Sort imports alphabetically within each group.
5. Preserve all meaningful comments.
6. Follow OpenStack's HACKING guidelines, including:
   - No wildcard imports
   - No relative imports unless strictly needed
   - Each import should be on its own line

Here is the code:
```
{code}
```

Return the cleaned imports section only, followed by a short explanation of what was changed.
"""

def suggest_commit_message_prompt(diff: str) -> str:
    return f"""
You are an expert Git commit message writer for OpenStack projects.

You are given a Git diff and need to suggest a professional commit message following these guidelines:

1. **Format**: Use conventional commits format: `type(scope): description`
   - Types: feat, fix, docs, style, refactor, test, chore
   - Scope: component or module name (optional)
   - Description: clear, concise, imperative mood

2. **OpenStack conventions**:
   - Use present tense ("Add feature" not "Added feature")
   - Keep first line under 50 characters
   - Add detailed body if needed (separated by blank line)
   - Reference bug numbers if applicable: "Fixes: #12345"

3. **Structure your response as**:
   - **Commit Message**: [The suggested commit message]
   - **Type**: [feat/fix/docs/style/refactor/test/chore]
   - **Scope**: [component or module affected]
   - **Explanation**: [Brief explanation of the changes]

Here is the diff:
```
{diff}
```

Provide a professional commit message that clearly describes what this change does.
"""
