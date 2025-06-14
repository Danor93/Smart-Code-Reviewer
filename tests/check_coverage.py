#!/usr/bin/env python3
"""
Quick coverage checker for Smart Code Reviewer
"""

import subprocess
import sys
from pathlib import Path


def run_coverage():
    """Run coverage analysis and show summary"""
    print("🧪 Smart Code Reviewer - Coverage Checker")
    print("=" * 50)

    try:
        # Run coverage with unit tests only
        result = subprocess.run(
            [
                "pytest",
                "tests/unit/",
                "--cov=.",
                "--cov-report=term-missing",
                "--cov-report=html",
                "--quiet",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ Coverage analysis completed successfully!")
            print("\n📊 Coverage Summary:")

            # Extract coverage info from output
            lines = result.stdout.split("\n")
            for line in lines:
                if "TOTAL" in line:
                    print(f"   {line}")
                    break

            print(f"\n📄 Detailed report: file:///{Path.cwd()}/htmlcov/index.html")
            print("\n🎯 Key Areas to Focus On:")
            print("   • RAG System (rag/*.py) - Currently 20-26% coverage")
            print("   • Agent System (agents/*.py) - Currently 40-42% coverage")
            print("   • API Advanced Features (app.py) - Currently 53% coverage")

        else:
            print("❌ Coverage analysis failed!")
            print(result.stderr)

    except FileNotFoundError:
        print("❌ pytest not found. Make sure you're in the virtual environment:")
        print("   source venv/bin/activate")
        sys.exit(1)


if __name__ == "__main__":
    run_coverage()
