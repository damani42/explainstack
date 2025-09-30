"""Agent configuration for ExplainStack multi-agent system."""

from typing import Dict, Any, List
from ..agents import (
    CodeExpertAgent,
    PatchReviewerAgent, 
    ImportCleanerAgent,
    CommitWriterAgent
)


class AgentConfig:
    """Configuration manager for ExplainStack agents."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize agent configuration.
        
        Args:
            config: Main configuration dictionary
        """
        self.config = config
        self.agents = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all available agents."""
        # Get OpenAI configuration
        openai_config = self.config.get("openai", {})
        
        # Initialize agents
        self.agents = {
            "code_expert": CodeExpertAgent(openai_config),
            "patch_reviewer": PatchReviewerAgent(openai_config),
            "import_cleaner": ImportCleanerAgent(openai_config),
            "commit_writer": CommitWriterAgent(openai_config),
        }
    
    def get_agent(self, agent_id: str):
        """Get agent by ID.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> Dict[str, Any]:
        """Get all available agents.
        
        Returns:
            Dictionary of agent information
        """
        return {
            agent_id: agent.get_info() 
            for agent_id, agent in self.agents.items()
        }
    
    def get_agent_list(self) -> List[Dict[str, str]]:
        """Get list of agents for UI selection.
        
        Returns:
            List of agent information dictionaries
        """
        return [
            {
                "id": agent_id,
                "name": agent.name,
                "description": agent.description
            }
            for agent_id, agent in self.agents.items()
        ]
    
    def get_auto_agent_id(self, user_input: str) -> str:
        """Automatically determine the best agent for user input.
        
        Args:
            user_input: User's input text
            
        Returns:
            Agent ID for automatic selection
        """
        text = user_input.lower()
        
        # Patch detection
        if text.startswith("diff ") or "---" in text or "+++" in text:
            return "patch_reviewer"
        
        # Import cleaning detection
        if any(keyword in text for keyword in ["clean imports", "nettoie", "import", "organize imports"]):
            return "import_cleaner"
        
        # Commit message detection
        if any(keyword in text for keyword in ["commit message", "commit msg", "suggest commit", "git commit"]):
            return "commit_writer"
        
        # Default to code expert for general code
        return "code_expert"
