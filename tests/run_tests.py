#!/usr/bin/env python3
"""
Test runner script for Smart Code Reviewer
Provides convenient commands for running different types of tests
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description=None):
    """Run a shell command and handle errors"""
    if description:
        print(f"\n🔍 {description}")
        print("-" * (len(description) + 4))

    print(f"$ {command}")
    result = subprocess.run(command, shell=True)

    if result.returncode != 0:
        print(f"❌ Command failed with exit code {result.returncode}")
        return False

    return True


def run_unit_tests():
    """Run unit tests only"""
    return run_command("pytest tests/unit/ -v --tb=short", "Running Unit Tests")


def run_api_tests():
    """Run API tests only"""
    return run_command("pytest tests/unit/test_api.py -v --tb=short", "Running API Tests")


def run_integration_tests():
    """Run integration tests only"""
    return run_command("pytest tests/integration/ -v --tb=short", "Running Integration Tests")


def run_all_tests():
    """Run all tests with coverage"""
    return run_command(
        "pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing",
        "Running All Tests with Coverage",
    )


def run_fast_tests():
    """Run fast tests (excluding slow ones)"""
    return run_command("pytest tests/ -m 'not slow' -v --tb=short", "Running Fast Tests")


def run_specific_test(test_path):
    """Run a specific test file or test function"""
    return run_command(f"pytest {test_path} -v --tb=short", f"Running Specific Test: {test_path}")


def check_test_environment():
    """Check if test environment is properly set up"""
    print("🔧 Checking Test Environment")
    print("-" * 28)

    # Check if pytest is installed
    try:
        import pytest

        print(f"✅ pytest version: {pytest.__version__}")
    except ImportError:
        print("❌ pytest not installed. Run: pip install -r requirements.txt")
        return False

    # Check if coverage is available
    try:
        import coverage

        print(f"✅ coverage version: {coverage.__version__}")
    except ImportError:
        print("❌ coverage not installed. Run: pip install pytest-cov")
        return False

    # Check test files exist
    test_dir = Path("tests")
    if not test_dir.exists():
        print("❌ tests/ directory not found")
        return False

    test_files = list(test_dir.glob("test_*.py"))
    print(f"✅ Found {len(test_files)} test files")

    # Check if required modules can be imported
    try:
        sys.path.insert(0, str(Path.cwd()))
        from models.data_models import ReviewResult

        print("✅ Core modules can be imported")
    except ImportError as e:
        print(f"❌ Failed to import core modules: {e}")
        return False

    print("\n🎉 Test environment is ready!")
    return True


def generate_coverage_report():
    """Generate detailed coverage report"""
    if not run_command(
        "pytest tests/ --cov=. --cov-report=html --cov-report=xml --cov-report=term",
        "Generating Coverage Report",
    ):
        return False

    print("\n📊 Coverage Report Generated:")
    print("  - HTML Report: htmlcov/index.html")
    print("  - XML Report: coverage.xml")
    print("  - Terminal output above")

    return True


def clean_test_artifacts():
    """Clean test artifacts and cache files"""
    print("🧹 Cleaning Test Artifacts")
    print("-" * 27)

    artifacts = [
        ".pytest_cache",
        "__pycache__",
        "htmlcov",
        "coverage.xml",
        ".coverage",
        "tests/__pycache__",
        "tests/.pytest_cache",
    ]

    for artifact in artifacts:
        if os.path.exists(artifact):
            if os.path.isdir(artifact):
                import shutil

                shutil.rmtree(artifact)
                print(f"✅ Removed directory: {artifact}")
            else:
                os.remove(artifact)
                print(f"✅ Removed file: {artifact}")
        else:
            print(f"⏭️  Not found: {artifact}")

    print("\n🎉 Cleanup completed!")


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(
        description="Smart Code Reviewer Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --all              # Run all tests with coverage
  python run_tests.py --unit             # Run only unit tests  
  python run_tests.py --api              # Run only API tests
  python run_tests.py --integration      # Run only integration tests
  python run_tests.py --fast             # Run fast tests (exclude slow)
  python run_tests.py --check            # Check test environment
  python run_tests.py --coverage         # Generate coverage report
  python run_tests.py --clean            # Clean test artifacts
  python run_tests.py --test tests/test_api.py  # Run specific test file
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Run all tests with coverage")
    group.add_argument("--unit", action="store_true", help="Run unit tests only")
    group.add_argument("--api", action="store_true", help="Run API tests only")
    group.add_argument("--integration", action="store_true", help="Run integration tests only")
    group.add_argument("--fast", action="store_true", help="Run fast tests (exclude slow)")
    group.add_argument("--check", action="store_true", help="Check test environment")
    group.add_argument("--coverage", action="store_true", help="Generate coverage report")
    group.add_argument("--clean", action="store_true", help="Clean test artifacts")
    group.add_argument("--test", type=str, help="Run specific test file or function")

    args = parser.parse_args()

    print("🧪 Smart Code Reviewer Test Runner")
    print("=" * 35)

    success = True

    if args.check:
        success = check_test_environment()
    elif args.unit:
        success = run_unit_tests()
    elif args.api:
        success = run_api_tests()
    elif args.integration:
        success = run_integration_tests()
    elif args.all:
        success = run_all_tests()
    elif args.fast:
        success = run_fast_tests()
    elif args.coverage:
        success = generate_coverage_report()
    elif args.clean:
        clean_test_artifacts()
    elif args.test:
        success = run_specific_test(args.test)

    if success:
        print("\n✅ All operations completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some operations failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
