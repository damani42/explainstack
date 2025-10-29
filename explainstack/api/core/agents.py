from typing import Any


def run_agent(agent: str, content: str) -> Any:
    """Dispatch to the appropriate ExplainStack agent based on the agent name."""
    # Lazy import to avoid heavy dependencies at import time
    try:
        from explainstack.agents import code_expert, patch_reviewer, import_cleaner, commit_writer  # type: ignore
    except Exception:
        # If the modules are unavailable, return placeholder
        return {"error": "Agent modules not available"}

    if agent == "analyze":
        return code_expert.explain(content)  # type: ignore
    elif agent == "review":
        return patch_reviewer.review(content)  # type: ignore
    elif agent == "clean":
        return import_cleaner.clean(content)  # type: ignore
    elif agent == "commit":
        return commit_writer.generate(content)  # type: ignore
    else:
        return {"error": f"Unknown agent: {agent}"}
