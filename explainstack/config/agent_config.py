"""Agent configuration for ExplainStack multi-agent system."""

from typing import Dict, Any, List
from ..agents import (
    CodeExpertAgent,
    PatchReviewerAgent, 
    ImportCleanerAgent,
    CommitWriterAgent
)
from ..backends import BackendFactory


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
        """Initialize all available agents with their backends."""
        # Get backend configurations
        backends_config = self.config.get("backends", {})
        
        # Initialize agents with their specific backends
        self.agents = {
            "code_expert": self._create_agent_with_backend(
                "code_expert", CodeExpertAgent, backends_config
            ),
            "patch_reviewer": self._create_agent_with_backend(
                "patch_reviewer", PatchReviewerAgent, backends_config
            ),
            "import_cleaner": self._create_agent_with_backend(
                "import_cleaner", ImportCleanerAgent, backends_config
            ),
            "commit_writer": self._create_agent_with_backend(
                "commit_writer", CommitWriterAgent, backends_config
            ),
        }
    
    def _create_agent_with_backend(self, agent_id: str, agent_class, backends_config: Dict[str, Any]):
        """Create an agent with its configured backend.
        
        Args:
            agent_id: Agent identifier
            agent_class: Agent class to instantiate
            backends_config: Backend configurations
            
        Returns:
            Agent instance with configured backend
        """
        # Get agent-specific backend configuration
        agent_backend_config = backends_config.get(agent_id, {})
        backend_type = agent_backend_config.get("type", "openai")
        backend_config = agent_backend_config.get("config", {})
        
        # Create backend
        backend = BackendFactory.create_backend(backend_type, backend_config)
        
        # Create agent with backend
        return agent_class(backend)
    
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
