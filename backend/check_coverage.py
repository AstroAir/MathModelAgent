#!/usr/bin/env python
"""
Check test coverage and report missing tests.

Usage:
    python check_coverage.py
"""

import os
import sys
from pathlib import Path


def find_python_files(directory):
    """Find all Python files in directory."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip __pycache__ and test directories
        dirs[:] = [
            d for d in dirs if d not in ["__pycache__", "tests", ".venv", "venv"]
        ]

        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                python_files.append(os.path.join(root, file))

    return python_files


def find_test_files(directory):
    """Find all test files."""
    test_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                test_files.append(os.path.join(root, file))

    return test_files


def get_expected_test_path(source_file, app_dir, tests_dir):
    """Get expected test file path for source file."""
    # Get relative path from app directory
    rel_path = os.path.relpath(source_file, app_dir)

    # Get directory and filename
    dir_name = os.path.dirname(rel_path)
    file_name = os.path.basename(rel_path)

    # Create test filename
    test_file_name = f"test_{file_name}"

    # Create test path
    test_path = os.path.join(tests_dir, dir_name, test_file_name)

    return test_path


def check_coverage():
    """Check test coverage."""
    print("=" * 80)
    print("MathModelAgent Test Coverage Check")
    print("=" * 80)
    print()

    # Directories
    app_dir = Path("app")
    tests_dir = Path("tests")

    if not app_dir.exists():
        print("❌ Error: 'app' directory not found")
        return 1

    if not tests_dir.exists():
        print("❌ Error: 'tests' directory not found")
        return 1

    # Find all source files
    source_files = find_python_files(app_dir)
    print(f"📁 Found {len(source_files)} source files in app/")

    # Find all test files
    test_files = find_test_files(tests_dir)
    print(f"🧪 Found {len(test_files)} test files in tests/")
    print()

    # Check for missing tests
    missing_tests = []
    existing_tests = []

    for source_file in source_files:
        expected_test = get_expected_test_path(source_file, app_dir, tests_dir)

        if os.path.exists(expected_test):
            existing_tests.append((source_file, expected_test))
        else:
            missing_tests.append((source_file, expected_test))

    # Report results
    print("📊 Coverage Summary")
    print("-" * 80)

    total = len(source_files)
    covered = len(existing_tests)
    coverage_percent = (covered / total * 100) if total > 0 else 0

    print(f"Total source files: {total}")
    print(f"Files with tests: {covered}")
    print(f"Files without tests: {len(missing_tests)}")
    print(f"Coverage: {coverage_percent:.1f}%")
    print()

    # Show coverage status
    if coverage_percent >= 80:
        print("✅ Great! Test coverage is above 80%")
    elif coverage_percent >= 60:
        print("⚠️  Test coverage is moderate (60-80%)")
    else:
        print("❌ Test coverage is low (below 60%)")
    print()

    # List missing tests
    if missing_tests:
        print("⚠️  Missing Test Files")
        print("-" * 80)
        for source_file, expected_test in sorted(missing_tests):
            rel_source = os.path.relpath(source_file)
            rel_test = os.path.relpath(expected_test)
            print(f"  {rel_source}")
            print(f"    → {rel_test}")
        print()

    # List existing tests
    if existing_tests and len(existing_tests) <= 20:
        print("✅ Existing Test Files")
        print("-" * 80)
        for source_file, test_file in sorted(existing_tests):
            rel_test = os.path.relpath(test_file)
            print(f"  {rel_test}")
        print()

    # Recommendations
    print("💡 Recommendations")
    print("-" * 80)

    if missing_tests:
        print("1. Create test files for modules without tests")
        print("2. Focus on core business logic first (agents, workflow)")
        print("3. Then add tests for utilities and helpers")
        print("4. Finally add tests for routers and schemas")
    else:
        print("1. All modules have test files! 🎉")
        print("2. Now focus on improving test quality")
        print("3. Add more edge cases and error scenarios")
        print("4. Increase assertion coverage")

    print()
    print("📈 Next Steps")
    print("-" * 80)
    print("1. Run: pytest --cov=app --cov-report=html")
    print("2. Open: htmlcov/index.html")
    print("3. Review uncovered lines")
    print("4. Add tests for uncovered code")
    print()

    # Return exit code
    if coverage_percent < 60:
        return 1
    return 0


def main():
    """Main entry point."""
    try:
        exit_code = check_coverage()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
