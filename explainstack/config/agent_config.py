"""Agent configuration for ExplainStack multi-agent system."""

from typing import Dict, Any, List
from ..agents import (
    CodeExpertAgent,
    PatchReviewerAgent, 
    ImportCleanerAgent,
    CommitWriterAgent,
    SecurityExpertAgent,
    PerformanceExpertAgent
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
        # Don't initialize agents here - they will be created on demand
    
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
            "security_expert": self._create_agent_with_backend(
                "security_expert", SecurityExpertAgent, backends_config
            ),
            "performance_expert": self._create_agent_with_backend(
                "performance_expert", PerformanceExpertAgent, backends_config
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
    
    def _create_agent_on_demand(self, agent_id: str):
        """Create a specific agent on demand with current configuration.
        
        Args:
            agent_id: Agent identifier
        """
        # Get backend configurations
        backends_config = self.config.get("backends", {})
        
        # Map agent IDs to their classes
        agent_classes = {
            "code_expert": CodeExpertAgent,
            "patch_reviewer": PatchReviewerAgent,
            "import_cleaner": ImportCleanerAgent,
            "commit_writer": CommitWriterAgent,
            "security_expert": SecurityExpertAgent,
            "performance_expert": PerformanceExpertAgent
        }
        
        if agent_id in agent_classes:
            agent_class = agent_classes[agent_id]
            self.agents[agent_id] = self._create_agent_with_backend(
                agent_id, agent_class, backends_config
            )
    
    def get_agent(self, agent_id: str):
        """Get agent by ID.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Agent instance or None if not found
        """
        # Create agent on demand with current configuration
        if agent_id not in self.agents:
            self._create_agent_on_demand(agent_id)
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> Dict[str, Any]:
        """Get all available agents.
        
        Returns:
            Dictionary of agent information
        """
        # Create all agents on demand
        agent_ids = ["code_expert", "patch_reviewer", "import_cleaner", "commit_writer", "security_expert", "performance_expert"]
        for agent_id in agent_ids:
            if agent_id not in self.agents:
                self._create_agent_on_demand(agent_id)
        
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
        
        # Performance analysis detection
        if any(keyword in text for keyword in [
            "performance", "optimize", "optimization", "speed", "fast",
            "slow", "bottleneck", "efficient", "scalability", "scalable",
            "memory", "cpu", "resource", "profiling", "benchmark"
        ]):
            return "performance_expert"
        
        # Security analysis detection
        if any(keyword in text for keyword in [
            "security", "vulnerability", "vuln", "secure", "safe",
            "attack", "exploit", "cve", "owasp", "compliance",
            "audit", "penetration", "threat", "risk", "hack"
        ]):
            return "security_expert"
        
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
