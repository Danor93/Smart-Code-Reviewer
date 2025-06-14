#!/usr/bin/env python3
"""
Flask Web Service for Enhanced Smart Code Reviewer
Provides REST API endpoints for code review functionality
"""

import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from agents import CodeReviewAgent, CodeReviewRequest

# Import from refactored modules
from reviewers import EnhancedCodeReviewer, RAGCodeReviewer

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the code reviewers and agent
reviewer = EnhancedCodeReviewer()
rag_reviewer = RAGCodeReviewer()
code_agent = CodeReviewAgent()

# Configuration
EXAMPLES_DIR = "examples"
DEFAULT_TECHNIQUE = "zero_shot"
DEFAULT_LANGUAGE = "python"


def get_available_files() -> List[str]:
    """Get list of available Python files in examples directory"""
    examples_path = Path(EXAMPLES_DIR)
    if not examples_path.exists():
        return []

    python_files = []
    for file_path in examples_path.glob("*.py"):
        python_files.append(file_path.name)

    return sorted(python_files)


def read_file_content(filename: str) -> str:
    """Read content of a file from examples directory"""
    file_path = Path(EXAMPLES_DIR) / filename
    if not file_path.exists():
        raise FileNotFoundError(f"File {filename} not found in examples directory")

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def format_review_result(result) -> Dict[str, Any]:
    """Format review result for JSON response"""
    return {
        "rating": result.rating,
        "model_used": result.model_used,
        "provider": result.provider,
        "technique": result.technique,
        "execution_time": round(result.execution_time, 2),
        "timestamp": datetime.now().isoformat(),
        "issues": result.issues,
        "suggestions": result.suggestions,
        "reasoning": result.reasoning,
    }


@app.route("/", methods=["GET"])
def home():
    """Health check and API information"""
    available_models = reviewer.model_registry.get_available_models()
    available_files = get_available_files()

    return jsonify(
        {
            "service": "Enhanced Smart Code Reviewer API",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "/": "API information and health check",
                "/models": "List available AI models",
                "/files": "List available example files",
                "/review/{filename}": "Review specific file from examples",
                "/review-all": "Review all files in examples directory",
                "/review-custom": "Review custom code (POST)",
                "/rag/review/{filename}": "RAG-enhanced file review",
                "/rag/review-custom": "RAG-enhanced custom code review (POST)",
                "/rag/compare": "Compare RAG vs traditional review (POST)",
                "/rag/search-guidelines": "Search coding guidelines (POST)",
                "/rag/knowledge-base/stats": "Get knowledge base statistics",
                "/rag/knowledge-base/refresh": "Refresh knowledge base (POST)",
                "/agent/review": "AI Agent autonomous code review (POST)",
                "/agent/review/{filename}": "AI Agent review file from examples",
                "/agent/info": "Get AI Agent capabilities and information",
            },
            "available_models": len(available_models),
            "available_files": len(available_files),
            "examples_directory": EXAMPLES_DIR,
        }
    )


@app.route("/models", methods=["GET"])
def get_models():
    """Get list of available AI models"""
    try:
        available_models = reviewer.model_registry.get_available_models()
        return jsonify(
            {
                "success": True,
                "models": available_models,
                "count": len(available_models),
            }
        )
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/files", methods=["GET"])
def get_files():
    """Get list of available example files"""
    try:
        available_files = get_available_files()
        file_info = []

        for filename in available_files:
            try:
                file_path = Path(EXAMPLES_DIR) / filename
                stats = file_path.stat()
                content = read_file_content(filename)

                file_info.append(
                    {
                        "filename": filename,
                        "size_bytes": stats.st_size,
                        "lines": len(content.splitlines()),
                        "characters": len(content),
                        "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                    }
                )
            except Exception as e:
                logger.warning(f"Error reading file info for {filename}: {e}")
                file_info.append({"filename": filename, "error": str(e)})

        return jsonify(
            {
                "success": True,
                "files": file_info,
                "count": len(available_files),
                "directory": EXAMPLES_DIR,
            }
        )
    except Exception as e:
        logger.error(f"Error getting files: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/review/<filename>", methods=["GET", "POST"])
def review_file(filename: str):
    """Review a specific file from examples directory"""
    try:
        # Get parameters
        technique = request.args.get("technique", DEFAULT_TECHNIQUE)
        model_id = request.args.get("model", None)
        language = request.args.get("language", DEFAULT_LANGUAGE)

        # Validate filename
        if not filename.endswith(".py"):
            filename += ".py"

        available_files = get_available_files()
        if filename not in available_files:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"File {filename} not found",
                        "available_files": available_files,
                    }
                ),
                404,
            )

        # Read file content
        code_content = read_file_content(filename)

        # Get available models
        available_models = reviewer.model_registry.get_available_models()
        if not available_models:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "No AI models available. Please check your API keys.",
                    }
                ),
                503,
            )

        # Use first available model if none specified
        if not model_id:
            model_id = list(available_models.keys())[0]
        elif model_id not in available_models:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Model {model_id} not available",
                        "available_models": list(available_models.keys()),
                    }
                ),
                400,
            )

        # Run the review
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(reviewer.review_code_async(code_content, language, technique, model_id))
        finally:
            loop.close()

        response_data = format_review_result(result)
        response_data.update(
            {
                "success": True,
                "filename": filename,
                "file_size": len(code_content),
                "file_lines": len(code_content.splitlines()),
            }
        )

        return jsonify(response_data)

    except FileNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error reviewing file {filename}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/review-all", methods=["GET", "POST"])
def review_all_files():
    """Review all files in examples directory"""
    try:
        # Get parameters
        technique = request.args.get("technique", DEFAULT_TECHNIQUE)
        model_id = request.args.get("model", None)
        language = request.args.get("language", DEFAULT_LANGUAGE)

        available_files = get_available_files()
        if not available_files:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"No Python files found in {EXAMPLES_DIR} directory",
                    }
                ),
                404,
            )

        # Get available models
        available_models = reviewer.model_registry.get_available_models()
        if not available_models:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "No AI models available. Please check your API keys.",
                    }
                ),
                503,
            )

        # Use first available model if none specified
        if not model_id:
            model_id = list(available_models.keys())[0]
        elif model_id not in available_models:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Model {model_id} not available",
                        "available_models": list(available_models.keys()),
                    }
                ),
                400,
            )

        # Review all files
        results = []
        total_start_time = datetime.now()

        for filename in available_files:
            try:
                logger.info(f"Reviewing file: {filename}")
                code_content = read_file_content(filename)

                # Run the review
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(reviewer.review_code_async(code_content, language, technique, model_id))
                finally:
                    loop.close()

                file_result = format_review_result(result)
                file_result.update(
                    {
                        "filename": filename,
                        "file_size": len(code_content),
                        "file_lines": len(code_content.splitlines()),
                        "success": True,
                    }
                )
                results.append(file_result)

            except Exception as e:
                logger.error(f"Error reviewing {filename}: {e}")
                results.append({"filename": filename, "success": False, "error": str(e)})

        total_execution_time = (datetime.now() - total_start_time).total_seconds()

        # Calculate summary statistics
        successful_reviews = [r for r in results if r.get("success", False)]
        summary = {
            "total_files": len(available_files),
            "successful_reviews": len(successful_reviews),
            "failed_reviews": len(results) - len(successful_reviews),
            "total_execution_time": round(total_execution_time, 2),
            "average_time_per_file": (round(total_execution_time / len(results), 2) if results else 0),
            "total_issues": sum(len(r.get("issues", [])) for r in successful_reviews),
            "model_used": model_id,
            "technique_used": technique,
        }

        return jsonify(
            {
                "success": True,
                "summary": summary,
                "results": results,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error reviewing all files: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/review-custom", methods=["POST"])
def review_custom_code():
    """Review custom code provided in request body"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "JSON body required"}), 400

        # Get parameters
        code_content = data.get("code")
        if not code_content:
            return jsonify({"success": False, "error": "Code content is required"}), 400

        technique = data.get("technique", DEFAULT_TECHNIQUE)
        model_id = data.get("model", None)
        language = data.get("language", DEFAULT_LANGUAGE)

        # Get available models
        available_models = reviewer.model_registry.get_available_models()
        if not available_models:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "No AI models available. Please check your API keys.",
                    }
                ),
                503,
            )

        # Use first available model if none specified
        if not model_id:
            model_id = list(available_models.keys())[0]
        elif model_id not in available_models:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Model {model_id} not available",
                        "available_models": list(available_models.keys()),
                    }
                ),
                400,
            )

        # Run the review
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(reviewer.review_code_async(code_content, language, technique, model_id))
        finally:
            loop.close()

        response_data = format_review_result(result)
        response_data.update(
            {
                "success": True,
                "code_size": len(code_content),
                "code_lines": len(code_content.splitlines()),
            }
        )

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Error reviewing custom code: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# RAG-Enhanced Endpoints
@app.route("/rag/review/<filename>", methods=["GET", "POST"])
def rag_review_file(filename: str):
    """Review a specific file using RAG-enhanced prompts"""
    try:
        # Get parameters
        model_id = request.args.get("model", None)
        language = request.args.get("language", DEFAULT_LANGUAGE)
        num_guidelines = int(request.args.get("guidelines", 3))

        # Validate filename
        if not filename.endswith(".py"):
            filename += ".py"

        available_files = get_available_files()
        if filename not in available_files:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"File {filename} not found",
                        "available_files": available_files,
                    }
                ),
                404,
            )

        # Read file content
        code_content = read_file_content(filename)

        # Run RAG review
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                rag_reviewer.review_code_with_rag(code_content, language, model_id, num_guidelines)
            )
        finally:
            loop.close()

        response_data = {
            "success": True,
            "filename": filename,
            "rating": result.rating,
            "model_used": result.model_used,
            "technique_used": result.technique_used,
            "timestamp": result.timestamp,
            "issues": result.issues,
            "suggestions": result.suggestions,
            "reasoning": result.reasoning,
            "guidelines_used": getattr(result, "guidelines_used", []),
            "rag_context_quality": getattr(result, "rag_context_quality", "unknown"),
            "num_guidelines": getattr(result, "num_guidelines", 0),
            "guideline_categories": getattr(result, "guideline_categories", []),
            "code_size": len(code_content),
            "code_lines": len(code_content.splitlines()),
        }

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Error in RAG review: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/rag/review-custom", methods=["POST"])
def rag_review_custom():
    """Review custom code using RAG-enhanced prompts"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "JSON body required"}), 400

        # Get parameters
        code_content = data.get("code")
        if not code_content:
            return jsonify({"success": False, "error": "Code content is required"}), 400

        model_id = data.get("model", None)
        language = data.get("language", DEFAULT_LANGUAGE)
        num_guidelines = data.get("guidelines", 3)

        # Run RAG review
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                rag_reviewer.review_code_with_rag(code_content, language, model_id, num_guidelines)
            )
        finally:
            loop.close()

        response_data = {
            "success": True,
            "rating": result.rating,
            "model_used": result.model_used,
            "technique_used": result.technique_used,
            "timestamp": result.timestamp,
            "issues": result.issues,
            "suggestions": result.suggestions,
            "reasoning": result.reasoning,
            "guidelines_used": getattr(result, "guidelines_used", []),
            "rag_context_quality": getattr(result, "rag_context_quality", "unknown"),
            "num_guidelines": getattr(result, "num_guidelines", 0),
            "guideline_categories": getattr(result, "guideline_categories", []),
            "code_size": len(code_content),
            "code_lines": len(code_content.splitlines()),
        }

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Error in RAG custom review: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/rag/compare", methods=["POST"])
def compare_rag_vs_traditional():
    """Compare RAG-enhanced vs traditional review"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "JSON body required"}), 400

        code_content = data.get("code")
        if not code_content:
            return jsonify({"success": False, "error": "Code content is required"}), 400

        model_id = data.get("model", None)
        language = data.get("language", DEFAULT_LANGUAGE)

        # Run comparison
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            comparison = loop.run_until_complete(rag_reviewer.compare_rag_vs_traditional(code_content, language, model_id))
        finally:
            loop.close()

        return jsonify(
            {
                "success": True,
                "comparison": comparison,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error in comparison: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/rag/search-guidelines", methods=["POST"])
def search_guidelines():
    """Search coding guidelines database"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "JSON body required"}), 400

        query = data.get("query")
        if not query:
            return jsonify({"success": False, "error": "Search query is required"}), 400

        category = data.get("category", None)
        k = data.get("limit", 5)

        # Run search
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(rag_reviewer.search_guidelines(query, category, k))
        finally:
            loop.close()

        return jsonify(
            {
                "success": True,
                "query": query,
                "category": category,
                "results": results,
                "count": len(results),
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error searching guidelines: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/rag/knowledge-base/stats", methods=["GET"])
def get_knowledge_base_stats():
    """Get knowledge base statistics"""
    try:
        stats = rag_reviewer.get_knowledge_base_stats()
        return jsonify({"success": True, "stats": stats, "timestamp": datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"Error getting knowledge base stats: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/rag/knowledge-base/refresh", methods=["POST"])
def refresh_knowledge_base():
    """Refresh the knowledge base"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            success = loop.run_until_complete(rag_reviewer.refresh_knowledge_base())
        finally:
            loop.close()

        if success:
            return jsonify(
                {
                    "success": True,
                    "message": "Knowledge base refreshed successfully",
                    "timestamp": datetime.now().isoformat(),
                }
            )
        else:
            return (
                jsonify({"success": False, "error": "Failed to refresh knowledge base"}),
                500,
            )

    except Exception as e:
        logger.error(f"Error refreshing knowledge base: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# AI AGENT ENDPOINTS
# ============================================================================


@app.route("/agent/info", methods=["GET"])
def get_agent_info():
    """Get information about the AI agent capabilities"""
    try:
        agent_info = code_agent.get_agent_info()
        return jsonify({"success": True, "agent_info": agent_info})
    except Exception as e:
        logger.error(f"Error getting agent info: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/agent/review", methods=["POST"])
def agent_review_custom():
    """AI Agent autonomous code review for custom code"""
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No JSON data provided"}), 400

        # Validate required fields
        if "code" not in data:
            return (
                jsonify({"success": False, "error": "Missing required field: code"}),
                400,
            )

        # Create request object
        review_request = CodeReviewRequest(
            code=data["code"],
            language=data.get("language", "python"),
            model_id=data.get("model_id", "gpt-4"),
            user_request=data.get("user_request", "Perform a comprehensive code review"),
            max_iterations=data.get("max_iterations", 5),
        )

        # Run async agent review
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(code_agent.review_code(review_request))

            return jsonify(
                {
                    "success": True,
                    "agent_review": result,
                    "request_info": {
                        "code_length": len(data["code"]),
                        "language": review_request.language,
                        "model_id": review_request.model_id,
                        "user_request": review_request.user_request,
                    },
                }
            )
        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Error in agent review: {e}")
        return (
            jsonify({"success": False, "error": str(e), "type": "agent_review_error"}),
            500,
        )


@app.route("/agent/review/<filename>", methods=["GET", "POST"])
def agent_review_file(filename: str):
    """AI Agent autonomous review of a file from examples directory"""
    try:
        # Validate filename
        if not filename.endswith(".py"):
            filename += ".py"

        available_files = get_available_files()
        if filename not in available_files:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"File {filename} not found",
                        "available_files": available_files,
                    }
                ),
                404,
            )

        # Read file content
        code_content = read_file_content(filename)

        # Get parameters
        model_id = request.args.get("model", "gpt-4")
        language = request.args.get("language", "python")
        user_request = request.args.get("request", f"Perform a comprehensive code review of {filename}")

        # Create request object
        review_request = CodeReviewRequest(
            code=code_content,
            language=language,
            model_id=model_id,
            user_request=user_request,
        )

        # Run async agent review
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(code_agent.review_code(review_request))

            return jsonify(
                {
                    "success": True,
                    "filename": filename,
                    "agent_review": result,
                    "file_info": {
                        "size": len(code_content),
                        "lines": len(code_content.splitlines()),
                        "language": language,
                    },
                }
            )
        finally:
            loop.close()

    except FileNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error in agent file review: {e}")
        return (
            jsonify({"success": False, "error": str(e), "type": "agent_file_review_error"}),
            500,
        )


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return (
        jsonify(
            {
                "success": False,
                "error": "Endpoint not found",
                "available_endpoints": [
                    "/",
                    "/models",
                    "/files",
                    "/review/<filename>",
                    "/review-all",
                    "/review-custom",
                    "/rag/review/<filename>",
                    "/rag/review-custom",
                    "/rag/compare",
                    "/rag/search-guidelines",
                    "/rag/knowledge-base/stats",
                    "/rag/knowledge-base/refresh",
                    "/agent/info",
                    "/agent/review",
                    "/agent/review/<filename>",
                ],
            }
        ),
        404,
    )


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"success": False, "error": "Internal server error"}), 500


if __name__ == "__main__":
    print("🚀 Starting Enhanced Smart Code Reviewer Flask API")
    print("=" * 60)

    # Check available models
    available_models = reviewer.model_registry.get_available_models()
    print(f"📋 Available Models: {len(available_models)}")
    for model_id, description in available_models.items():
        print(f"  • {model_id}: {description}")

    # Check available files
    available_files = get_available_files()
    print(f"📁 Available Files: {len(available_files)}")
    for filename in available_files:
        print(f"  • {filename}")

    print("\n🌐 API Endpoints:")
    print("  • GET  /                  - API information")
    print("  • GET  /models            - List available models")
    print("  • GET  /files             - List available files")
    print("  • GET  /review/<filename> - Review specific file")
    print("  • GET  /review-all        - Review all files")
    print("  • POST /review-custom     - Review custom code")
    print("\n🧠 RAG-Enhanced Endpoints:")
    print("  • GET  /rag/review/<filename>      - RAG-enhanced file review")
    print("  • POST /rag/review-custom          - RAG-enhanced custom review")
    print("  • POST /rag/compare                - Compare RAG vs traditional")
    print("  • POST /rag/search-guidelines      - Search coding guidelines")
    print("  • GET  /rag/knowledge-base/stats   - Knowledge base statistics")
    print("  • POST /rag/knowledge-base/refresh - Refresh knowledge base")

    print("\n🤖 AI Agent Endpoints:")
    print("  • GET  /agent/info              - Get agent capabilities")
    print("  • POST /agent/review            - Autonomous code review")
    print("  • GET  /agent/review/<filename> - Agent review of file")

    print(f"\n🔧 Starting server on http://0.0.0.0:5000 (exposed on host port 8080)")
    print("=" * 60)

    # Run the Flask app
    app.run(host="0.0.0.0", port=5000, debug=False)  # nosec B104
