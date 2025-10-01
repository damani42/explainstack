#!/usr/bin/env python3
"""Setup script for ExplainStack CLI."""

import os
import sys
import shutil
from pathlib import Path

def setup_cli():
    """Setup ExplainStack CLI."""
    try:
        # Get the current directory
        current_dir = Path(__file__).parent.absolute()
        cli_script = current_dir / "explainstack_cli.py"
        
        # Check if script exists
        if not cli_script.exists():
            print("❌ CLI script not found!")
            return False
        
        # Create symlink in /usr/local/bin (requires sudo)
        try:
            # Try to create symlink
            symlink_path = Path("/usr/local/bin/explainstack")
            if symlink_path.exists():
                symlink_path.unlink()
            
            symlink_path.symlink_to(cli_script)
            print(f"✅ CLI installed successfully!")
            print(f"   Symlink: {symlink_path} -> {cli_script}")
            print(f"   You can now use: explainstack --help")
            return True
            
        except PermissionError:
            print("❌ Permission denied. Please run with sudo:")
            print(f"   sudo python3 {__file__}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up CLI: {e}")
        return False

def setup_user_cli():
    """Setup CLI in user directory (no sudo required)."""
    try:
        # Get the current directory
        current_dir = Path(__file__).parent.absolute()
        cli_script = current_dir / "explainstack_cli.py"
        
        # Check if script exists
        if not cli_script.exists():
            print("❌ CLI script not found!")
            return False
        
        # Create user bin directory
        user_bin = Path.home() / "bin"
        user_bin.mkdir(exist_ok=True)
        
        # Copy script to user bin
        user_cli = user_bin / "explainstack"
        shutil.copy2(cli_script, user_cli)
        
        # Make executable
        os.chmod(user_cli, 0o755)
        
        print(f"✅ CLI installed to user directory!")
        print(f"   Location: {user_cli}")
        print(f"   Add to PATH: export PATH=\"$HOME/bin:$PATH\"")
        print(f"   Then use: explainstack --help")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up user CLI: {e}")
        return False

if __name__ == '__main__':
    print("🚀 ExplainStack CLI Setup")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--user':
        success = setup_user_cli()
    else:
        success = setup_cli()
    
    if not success:
        print("\n💡 Alternative: Install to user directory (no sudo required):")
        print(f"   python3 {__file__} --user")
        sys.exit(1)
