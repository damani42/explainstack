"""Main CLI application for ExplainStack."""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from ..config import get_config
from ..config import AgentConfig, AgentRouter
from .commands import AnalyzeCommand, SecurityCommand, ReviewCommand, CleanCommand, CommitCommand


def setup_logging(verbose: bool = False):
    """Setup logging for CLI."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="ExplainStack CLI - AI-powered OpenStack development assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  explainstack analyze file.py                    # Analyze Python code
  explainstack security file.py                   # Security analysis
  explainstack review patch.diff                  # Review patch
  explainstack clean file.py                      # Clean imports
  explainstack commit file.py                     # Generate commit message
  explainstack analyze file.py --agent security  # Use specific agent
  explainstack analyze file.py --output report.md # Save to file
        """
    )
    
    # Global options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file path'
    )
    
    parser.add_argument(
        '--agent', '-a',
        type=str,
        choices=['code_expert', 'patch_reviewer', 'import_cleaner', 'commit_writer', 'security_expert'],
        help='Specify agent to use'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        required=True
    )
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze Python code'
    )
    analyze_parser.add_argument(
        'file',
        type=str,
        help='Python file to analyze'
    )
    
    # Security command
    security_parser = subparsers.add_parser(
        'security',
        help='Security analysis of code'
    )
    security_parser.add_argument(
        'file',
        type=str,
        help='Python file to analyze for security issues'
    )
    
    # Review command
    review_parser = subparsers.add_parser(
        'review',
        help='Review patch or diff'
    )
    review_parser.add_argument(
        'file',
        type=str,
        help='Patch or diff file to review'
    )
    
    # Clean command
    clean_parser = subparsers.add_parser(
        'clean',
        help='Clean and organize imports'
    )
    clean_parser.add_argument(
        'file',
        type=str,
        help='Python file to clean imports'
    )
    
    # Commit command
    commit_parser = subparsers.add_parser(
        'commit',
        help='Generate commit message'
    )
    commit_parser.add_argument(
        'file',
        type=str,
        help='File or diff to generate commit message for'
    )
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config = get_config()
        agent_config = AgentConfig(config)
        agent_router = AgentRouter(agent_config)
        
        # Create command instances
        commands = {
            'analyze': AnalyzeCommand(agent_router),
            'security': SecurityCommand(agent_router),
            'review': ReviewCommand(agent_router),
            'clean': CleanCommand(agent_router),
            'commit': CommitCommand(agent_router)
        }
        
        # Execute command
        command = commands[args.command]
        result = command.execute(args)
        
        # Handle output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"✅ Results saved to {args.output}")
        else:
            print(result)
            
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
