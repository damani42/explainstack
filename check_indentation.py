#!/usr/bin/env python3
"""Script to check indentation issues in Python files."""

import ast
import sys
import os

def check_indentation(file_path):
    """Check for indentation issues in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse the file
        ast.parse(content)
        print(f"✅ {file_path}: No syntax errors found")
        return True
        
    except SyntaxError as e:
        print(f"❌ {file_path}: Syntax error at line {e.lineno}: {e.msg}")
        if e.text:
            print(f"   Problematic line: {e.text.strip()}")
        return False
        
    except Exception as e:
        print(f"❌ {file_path}: Error reading file: {e}")
        return False

def check_all_python_files(directory):
    """Check all Python files in a directory."""
    issues_found = False
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if not check_indentation(file_path):
                    issues_found = True
    
    return not issues_found

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        success = check_indentation(file_path)
    else:
        success = check_all_python_files("explainstack")
    
    if success:
        print("\n🎉 All Python files have correct syntax!")
        sys.exit(0)
    else:
        print("\n❌ Some files have syntax issues!")
        sys.exit(1)
