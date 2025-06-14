#!/usr/bin/env python3
"""
Enhanced Smart Code Reviewer with LangChain Integration
Supports multiple LLM providers with dynamic loading and async execution
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Import from refactored modules
from reviewers import EnhancedCodeReviewer

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Demonstrate the Enhanced Code Reviewer"""
    print("🚀 Enhanced Smart Code Reviewer with Multi-Model Support")
    print("=" * 60)

    # Initialize enhanced reviewer
    reviewer = EnhancedCodeReviewer()

    # Show available models
    available_models = reviewer.model_registry.get_available_models()
    print(f"\n📋 Available Models ({len(available_models)}):")
    for model_id, description in available_models.items():
        print(f"  • {model_id}: {description}")

    if not available_models:
        print("❌ No models available. Please check your API keys in .env file")
        return

    # Get code to review
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        try:
            # Handle directory argument
            if os.path.isdir(file_path):
                python_files = []
                for root, dirs, files in os.walk(file_path):
                    for file in files:
                        if file.endswith(".py"):
                            python_files.append(os.path.join(root, file))

                if not python_files:
                    print(f"❌ No Python files found in directory: {file_path}")
                    return

                print(f"\n📁 Found {len(python_files)} Python files:")
                for i, py_file in enumerate(python_files, 1):
                    print(f"  {i}. {py_file}")

                # Review first file for demonstration
                file_path = python_files[0]
                print(f"\n📝 Reviewing: {file_path}")

            # Read the file
            with open(file_path, "r", encoding="utf-8") as f:
                test_code = f.read()

            print(f"\n📄 File: {file_path}")
            print(f"📏 Lines: {len(test_code.splitlines())}")
            print(f"📊 Characters: {len(test_code)}")

            # Show preview of code (first 20 lines)
            lines = test_code.splitlines()
            preview_lines = lines[:20]
            print(f"\n📝 Code Preview (first 20 lines):")
            for i, line in enumerate(preview_lines, 1):
                print(f"{i:3d}: {line}")
            if len(lines) > 20:
                print(f"... and {len(lines) - 20} more lines")

        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            return
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return
    else:
        # Default sample code for testing
        test_code = """
def calculate_password_strength(password):
    # Check password strength
    if len(password) < 8:
        return "weak"
    if "password" in password.lower():
        return "weak" 
    return "strong"

# Usage
user_password = "password123"
strength = calculate_password_strength(user_password)
print("Password strength:", strength)
"""
        print(f"\n📝 Using default example code:")
        print(test_code)

    print("\n" + "=" * 60)

    # Test different techniques with first available model
    first_model = list(available_models.keys())[0]
    techniques = [
        ("zero_shot", "Zero-Shot Prompting"),
        ("few_shot", "Few-Shot Prompting"),
        ("cot", "Chain-of-Thought Prompting"),
    ]

    print(f"\n🧠 Testing Prompt Engineering Techniques with {first_model}")
    print("-" * 50)

    for technique, description in techniques:
        print(f"\n🎯 {description}")
        try:
            result = await reviewer.review_code_async(test_code, "python", technique, first_model)

            print(f"Rating: {result.rating}")
            print(f"Model: {result.model_used} ({result.provider})")
            print(f"Execution Time: {result.execution_time:.2f}s")
            print(f"Issues Found: {len(result.issues)}")
            for i, issue in enumerate(result.issues[:3], 1):  # Show first 3
                print(f"  {i}. {issue}")
            if len(result.issues) > 3:
                print(f"  ... and {len(result.issues) - 3} more")

        except Exception as e:
            print(f"Error: {e}")

    # Compare multiple models
    if len(available_models) > 1:
        print(f"\n🔄 Comparing Multiple Models (Zero-Shot)")
        print("-" * 50)

        comparison = await reviewer.compare_models_async(test_code, "python", "zero_shot")

        for model_id, result in comparison.items():
            print(f"{model_id}: {result.rating} ({len(result.issues)} issues, {result.execution_time:.2f}s)")


if __name__ == "__main__":
    print("🔧 Enhanced Setup Instructions:")
    print("1. Install packages: pip install -r requirements.txt")
    print("2. Add API keys to .env file:")
    print("   OPENAI_API_KEY=your-key")
    print("   ANTHROPIC_API_KEY=your-key")
    print("   GOOGLE_API_KEY=your-key")
    print("   HUGGINGFACE_API_TOKEN=your-token")
    print("3. Run: python enhanced_code_reviewer.py")
    print("\n" + "=" * 60)

    asyncio.run(main())
