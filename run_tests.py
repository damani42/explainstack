#!/usr/bin/env python3
"""Test runner for ExplainStack."""

import sys
import subprocess
import os
from pathlib import Path

def run_tests():
    """Run all tests with coverage."""
    print("🧪 Running ExplainStack Test Suite")
    print("=" * 50)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--cov=explainstack",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=80",
        "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        print("📊 Coverage report generated in htmlcov/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return False

def run_specific_tests(test_pattern):
    """Run specific tests matching pattern."""
    print(f"🧪 Running tests matching: {test_pattern}")
    print("=" * 50)
    
    cmd = [
        sys.executable, "-m", "pytest",
        f"tests/{test_pattern}",
        "-v",
        "--tb=short"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific tests
        test_pattern = sys.argv[1]
        success = run_specific_tests(test_pattern)
    else:
        # Run all tests
        success = run_tests()
    
    sys.exit(0 if success else 1)
