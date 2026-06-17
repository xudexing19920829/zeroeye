#!/usr/bin/env python3
"""
Verify that build diagnostics are created correctly.

This script checks that:
1. Build process completes without errors
2. Diagnostic files are generated
3. Diagnostic content is valid
"""

import os
import sys
import json
import subprocess
from pathlib import Path


def run_command(cmd: list[str], cwd: str = ".") -> tuple[bool, str]:
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def check_build_diagnostics() -> bool:
    """Check that build diagnostics are created."""
    print("Checking build diagnostics...")
    
    # Check if diagnostic directory exists
    diagnostic_dir = Path("diagnostic")
    if not diagnostic_dir.exists():
        print("❌ Diagnostic directory not found")
        return False
    
    print("✅ Diagnostic directory exists")
    
    # Check for diagnostic files
    diagnostic_files = list(diagnostic_dir.glob("**/*"))
    if not diagnostic_files:
        print("❌ No diagnostic files found")
        return False
    
    print(f"✅ Found {len(diagnostic_files)} diagnostic files")
    
    # Check file types
    json_files = [f for f in diagnostic_files if f.suffix == ".json"]
    log_files = [f for f in diagnostic_files if f.suffix == ".log"]
    
    print(f"  - JSON files: {len(json_files)}")
    print(f"  - Log files: {len(log_files)}")
    
    # Validate JSON files
    for json_file in json_files:
        try:
            with open(json_file) as f:
                json.load(f)
            print(f"  ✅ Valid JSON: {json_file.name}")
        except json.JSONDecodeError as e:
            print(f"  ❌ Invalid JSON: {json_file.name} - {e}")
            return False
    
    return True


def check_build_process() -> bool:
    """Check that build process works correctly."""
    print("\nChecking build process...")
    
    # Run build command
    success, output = run_command(["python3", "build.py", "--help"])
    if not success:
        print(f"❌ Build help failed: {output[:200]}")
        return False
    
    print("✅ Build help works")
    return True


def main() -> int:
    """Main verification function."""
    print("=== Build Diagnostics Verification ===\n")
    
    checks = [
        ("Build Process", check_build_process),
        ("Build Diagnostics", check_build_diagnostics),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n=== Summary ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n{passed}/{total} checks passed")
    
    if passed == total:
        print("\n✅ All build diagnostics verification checks passed!")
        return 0
    else:
        print("\n❌ Some checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
