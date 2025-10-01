"""CLI commands for ExplainStack."""

import asyncio
import logging
from pathlib import Path
from typing import Optional

from ..utils import FileHandler

logger = logging.getLogger(__name__)


class BaseCommand:
    """Base class for CLI commands."""
    
    def __init__(self, agent_router):
        """Initialize command with agent router."""
        self.agent_router = agent_router
        self.file_handler = FileHandler()
    
    def read_file(self, file_path: str) -> tuple[bool, Optional[str], Optional[str]]:
        """Read file content."""
        try:
            path = Path(file_path)
            if not path.exists():
                return False, None, f"File not found: {file_path}"
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return True, content, None
        except Exception as e:
            return False, None, f"Error reading file: {str(e)}"
    
    async def process_with_agent(self, content: str, agent_id: str) -> tuple[bool, Optional[str], Optional[str]]:
        """Process content with specified agent."""
        try:
            return await self.agent_router.route_request(content, agent_id)
        except Exception as e:
            logger.error(f"Error processing with agent {agent_id}: {e}")
            return False, None, f"Agent processing error: {str(e)}"
    
    def execute(self, args) -> str:
        """Execute command (to be implemented by subclasses)."""
        raise NotImplementedError


class AnalyzeCommand(BaseCommand):
    """Command for code analysis."""
    
    def execute(self, args) -> str:
        """Execute code analysis."""
        # Read file
        success, content, error = self.read_file(args.file)
        if not success:
            return f"❌ Error: {error}"
        
        # Determine agent
        agent_id = args.agent or 'code_expert'
        
        # Process with agent
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success, result, error = loop.run_until_complete(
                self.process_with_agent(content, agent_id)
            )
            loop.close()
            
            if success:
                return f"🧠 **Code Analysis**\n\n{result}"
            else:
                return f"❌ Error: {error}"
        except Exception as e:
            return f"❌ Error: {str(e)}"


class SecurityCommand(BaseCommand):
    """Command for security analysis."""
    
    def execute(self, args) -> str:
        """Execute security analysis."""
        # Read file
        success, content, error = self.read_file(args.file)
        if not success:
            return f"❌ Error: {error}"
        
        # Process with security expert
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success, result, error = loop.run_until_complete(
                self.process_with_agent(content, 'security_expert')
            )
            loop.close()
            
            if success:
                return f"🔒 **Security Analysis**\n\n{result}"
            else:
                return f"❌ Error: {error}"
        except Exception as e:
            return f"❌ Error: {str(e)}"


class ReviewCommand(BaseCommand):
    """Command for patch review."""
    
    def execute(self, args) -> str:
        """Execute patch review."""
        # Read file
        success, content, error = self.read_file(args.file)
        if not success:
            return f"❌ Error: {error}"
        
        # Process with patch reviewer
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success, result, error = loop.run_until_complete(
                self.process_with_agent(content, 'patch_reviewer')
            )
            loop.close()
            
            if success:
                return f"🔍 **Patch Review**\n\n{result}"
            else:
                return f"❌ Error: {error}"
        except Exception as e:
            return f"❌ Error: {str(e)}"


class CleanCommand(BaseCommand):
    """Command for import cleaning."""
    
    def execute(self, args) -> str:
        """Execute import cleaning."""
        # Read file
        success, content, error = self.read_file(args.file)
        if not success:
            return f"❌ Error: {error}"
        
        # Process with import cleaner
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success, result, error = loop.run_until_complete(
                self.process_with_agent(content, 'import_cleaner')
            )
            loop.close()
            
            if success:
                return f"🧹 **Import Cleaning**\n\n{result}"
            else:
                return f"❌ Error: {error}"
        except Exception as e:
            return f"❌ Error: {str(e)}"


class CommitCommand(BaseCommand):
    """Command for commit message generation."""
    
    def execute(self, args) -> str:
        """Execute commit message generation."""
        # Read file
        success, content, error = self.read_file(args.file)
        if not success:
            return f"❌ Error: {error}"
        
        # Process with commit writer
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success, result, error = loop.run_until_complete(
                self.process_with_agent(content, 'commit_writer')
            )
            loop.close()
            
            if success:
                return f"💬 **Commit Message**\n\n{result}"
            else:
                return f"❌ Error: {error}"
        except Exception as e:
            return f"❌ Error: {str(e)}"


class PerformanceCommand(BaseCommand):
    """Command for performance analysis."""
    
    def execute(self, args) -> str:
        """Execute performance analysis."""
        # Read file
        success, content, error = self.read_file(args.file)
        if not success:
            return f"❌ Error: {error}"
        
        # Process with performance expert
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success, result, error = loop.run_until_complete(
                self.process_with_agent(content, 'performance_expert')
            )
            loop.close()
            
            if success:
                return f"⚡ **Performance Analysis**\n\n{result}"
            else:
                return f"❌ Error: {error}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
