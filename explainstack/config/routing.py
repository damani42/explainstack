"""Agent routing logic for ExplainStack multi-agent system."""

import logging
from typing import Dict, Any, Optional, Tuple
from .agent_config import AgentConfig

logger = logging.getLogger(__name__)


class AgentRouter:
    """Router for directing requests to appropriate agents."""
    
    def __init__(self, agent_config: AgentConfig):
        """Initialize the agent router.
        
        Args:
            agent_config: Agent configuration instance
        """
        self.agent_config = agent_config
        self.logger = logging.getLogger(__name__)
    
    async def route_request(self, user_input: str, selected_agent_id: Optional[str] = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """Route user request to appropriate agent.
        
        Args:
            user_input: User's input text
            selected_agent_id: Manually selected agent ID (optional)
            
        Returns:
            Tuple of (success, response, error_message)
        """
        try:
            # Determine which agent to use
            if selected_agent_id:
                agent_id = selected_agent_id
                self.logger.info(f"Using manually selected agent: {agent_id}")
            else:
                agent_id = self.agent_config.get_auto_agent_id(user_input)
                self.logger.info(f"Auto-selected agent: {agent_id}")
            
            # Get the agent
            agent = self.agent_config.get_agent(agent_id)
            if not agent:
                error_msg = f"Agent '{agent_id}' not found"
                self.logger.error(error_msg)
                return False, None, error_msg
            
            # Process with the agent
            self.logger.info(f"Routing to {agent.name} agent")
            return await agent.process(user_input)
            
        except Exception as e:
            error_msg = f"Routing error: {str(e)}"
            self.logger.error(f"Error in agent routing: {e}")
            return False, None, error_msg
    
    def get_available_agents(self) -> Dict[str, Any]:
        """Get list of available agents.
        
        Returns:
            Dictionary of available agents
        """
        return self.agent_config.get_all_agents()
    
    def get_agent_list(self) -> list:
        """Get agent list for UI.
        
        Returns:
            List of agent information
        """
        return self.agent_config.get_agent_list()
    
    def get_auto_suggestion(self, user_input: str) -> str:
        """Get auto-suggested agent for user input.
        
        Args:
            user_input: User's input text
            
        Returns:
            Suggested agent ID
        """
        return self.agent_config.get_auto_agent_id(user_input)
