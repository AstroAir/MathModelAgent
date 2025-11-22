#!/usr/bin/env python
"""
Test runner script for MathModelAgent backend.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --coverage   # Run with coverage report
    python run_tests.py --verbose    # Run with verbose output
    python run_tests.py --fast       # Skip slow tests
"""

import sys
import subprocess
import argparse


def run_tests(args):
    """Run pytest with specified arguments."""
    cmd = ["pytest"]

    # Add verbosity
    if args.verbose:
        cmd.extend(["-v", "-s"])

    # Add coverage
    if args.coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])

    # Skip slow tests
    if args.fast:
        cmd.extend(["-m", "not slow"])

    # Run specific directory
    if args.directory:
        cmd.append(f"tests/{args.directory}")

    # Run specific file
    if args.file:
        cmd.append(f"tests/{args.file}")

    # Run specific test
    if args.test:
        cmd.extend(["-k", args.test])

    # Parallel execution
    if args.parallel:
        cmd.extend(["-n", "auto"])

    # Show failed tests first
    if args.failed_first:
        cmd.append("--lf")

    # Stop on first failure
    if args.exitfirst:
        cmd.append("-x")

    # Add any extra arguments
    if args.extra:
        cmd.extend(args.extra)

    print(f"Running: {' '.join(cmd)}")
    print("-" * 80)

    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run tests for MathModelAgent backend")

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    parser.add_argument(
        "-c", "--coverage", action="store_true", help="Generate coverage report"
    )

    parser.add_argument("-f", "--fast", action="store_true", help="Skip slow tests")

    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        help="Run tests in specific directory (e.g., routers, core)",
    )

    parser.add_argument(
        "--file",
        type=str,
        help="Run specific test file (e.g., routers/test_modeling_router.py)",
    )

    parser.add_argument("-k", "--test", type=str, help="Run tests matching pattern")

    parser.add_argument(
        "-n",
        "--parallel",
        action="store_true",
        help="Run tests in parallel (requires pytest-xdist)",
    )

    parser.add_argument(
        "--lf",
        "--failed-first",
        action="store_true",
        dest="failed_first",
        help="Run failed tests first",
    )

    parser.add_argument(
        "-x", "--exitfirst", action="store_true", help="Stop on first failure"
    )

    parser.add_argument("extra", nargs="*", help="Extra arguments to pass to pytest")

    args = parser.parse_args()

    # Run tests
    exit_code = run_tests(args)

    # Print summary
    print("-" * 80)
    if exit_code == 0:
        print("✅ All tests passed!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print("❌ Some tests failed!")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
