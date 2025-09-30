"""Agent selector UI component for ExplainStack."""

import chainlit as cl
from typing import Dict, Any, List, Optional
from ..config import AgentRouter


class AgentSelector:
    """UI component for agent selection in Chainlit."""
    
    def __init__(self, agent_router: AgentRouter):
        """Initialize the agent selector.
        
        Args:
            agent_router: Agent router instance
        """
        self.agent_router = agent_router
        self.agents = agent_router.get_agent_list()
    
    async def show_agent_selection(self, user_input: str) -> Optional[str]:
        """Show agent selection interface.
        
        Args:
            user_input: User's input text
            
        Returns:
            Selected agent ID or None if cancelled
        """
        # Get auto-suggestion
        suggested_agent_id = self.agent_router.get_auto_suggestion(user_input)
        suggested_agent = next(
            (agent for agent in self.agents if agent["id"] == suggested_agent_id), 
            None
        )
        
        # Create selection message
        selection_text = f"""🤖 **Select an Agent**

I detected that you might want to use the **{suggested_agent['name'] if suggested_agent else 'Code Expert'}** agent for this request.

**Available Agents:**

"""
        
        for agent in self.agents:
            is_suggested = agent["id"] == suggested_agent_id
            emoji = "🎯" if is_suggested else "🤖"
            selection_text += f"{emoji} **{agent['name']}**: {agent['description']}\n"
        
        selection_text += f"""

**Quick Selection:**
- Type `1` for **{self.agents[0]['name']}**
- Type `2` for **{self.agents[1]['name']}**  
- Type `3` for **{self.agents[2]['name']}**
- Type `4` for **{self.agents[3]['name']}**
- Type `auto` to use the suggested agent
- Type `cancel` to cancel

Or just send your message and I'll use the suggested agent automatically."""
        
        await cl.Message(content=selection_text).send()
        return suggested_agent_id
    
    def parse_agent_selection(self, user_input: str) -> Optional[str]:
        """Parse agent selection from user input.
        
        Args:
            user_input: User's input text
            
        Returns:
            Selected agent ID or None
        """
        text = user_input.lower().strip()
        
        # Quick selection by number
        if text == "1":
            return self.agents[0]["id"]
        elif text == "2":
            return self.agents[1]["id"]
        elif text == "3":
            return self.agents[2]["id"]
        elif text == "4":
            return self.agents[3]["id"]
        
        # Auto selection
        elif text == "auto":
            return self.agent_router.get_auto_suggestion(user_input)
        
        # Cancel
        elif text == "cancel":
            return None
        
        # Try to match by name
        for agent in self.agents:
            if agent["name"].lower() in text or agent["id"] in text:
                return agent["id"]
        
        return None
    
    async def show_agent_info(self, agent_id: str):
        """Show information about a specific agent.
        
        Args:
            agent_id: Agent identifier
        """
        agent_info = self.agent_router.get_available_agents().get(agent_id)
        if not agent_info:
            await cl.Message(content=f"❌ Agent '{agent_id}' not found").send()
            return
        
        info_text = f"""🤖 **{agent_info['name']}**

**Description:** {agent_info['description']}

**Capabilities:**
- Specialized in {agent_info['name'].lower()} tasks
- Optimized prompts for better results
- Expert knowledge in OpenStack development
- Professional-grade analysis and suggestions

This agent is now ready to help you! Send your code, patch, or question."""
        
        await cl.Message(content=info_text).send()
