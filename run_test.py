#!/usr/bin/env python3
"""
Simple test runner for LDB Africa project
"""
import subprocess
import sys

def run_tests():
    """Run all tests with pytest"""
    print("🧪 Running LDB Africa Tests...\n")
    
    # Run pytest with coverage
    result = subprocess.run([
        "pytest",
        "tests/",            # Test directory
        "-v",                # Verbose output
        "--tb=short",        # Short traceback
        "--color=yes",       # Colored output
    ])
    
    print(f"\n✅ Tests completed with exit code: {result.returncode}")
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_tests())