#!/bin/bash

# Smart Code Reviewer Docker Management Script
# Usage: ./docker-run.sh [command] [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if .env file exists
check_env_file() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from .env.example..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_info "Please edit .env file with your API keys before running the container"
        else
            print_error ".env.example not found. Please create .env file with your API keys"
            exit 1
        fi
    fi
}

# Build Docker image
build() {
    print_info "Building Smart Code Reviewer Docker image..."
    docker build -t smart-code-reviewer:latest .
    print_success "Docker image built successfully!"
}

# Run with Docker Compose
run_compose() {
    check_env_file
    print_info "Starting Smart Code Reviewer Flask API with Docker Compose..."
    print_info "API will be available at http://localhost:8080"
    docker-compose up --build
}

# Run interactive container
run_interactive() {
    check_env_file
    print_info "Running Smart Code Reviewer Flask API in interactive mode..."
    print_info "API will be available at http://localhost:8080"
    
    # Create necessary directories
    mkdir -p logs results
    
    docker run -it --rm \
        --name smart-code-reviewer \
        --env-file .env \
        -p 8080:5000 \
        -v "$(pwd)/logs:/app/logs" \
        -v "$(pwd)/results:/app/results" \
        smart-code-reviewer:latest
}

# Run with specific file (legacy CLI mode)
run_with_file() {
    if [ -z "$1" ]; then
        print_error "Please specify a file path"
        exit 1
    fi
    
    check_env_file
    
    local file_path="$1"
    local file_name=$(basename "$file_path")
    
    print_info "Reviewing file: $file_path (legacy CLI mode)"
    
    # Create necessary directories
    mkdir -p logs results
    
    docker run --rm \
        --name smart-code-reviewer-cli \
        --env-file .env \
        -v "$(pwd)/$file_path:/app/code-to-review/$file_name:ro" \
        -v "$(pwd)/logs:/app/logs" \
        -v "$(pwd)/results:/app/results" \
        smart-code-reviewer:latest \
        python enhanced_code_reviewer.py "/app/code-to-review/$file_name"
}

# Run with directory (legacy CLI mode)
run_with_directory() {
    if [ -z "$1" ]; then
        print_error "Please specify a directory path"
        exit 1
    fi
    
    check_env_file
    
    local dir_path="$1"
    
    print_info "Reviewing directory: $dir_path (legacy CLI mode)"
    
    # Create necessary directories
    mkdir -p logs results
    
    docker run --rm \
        --name smart-code-reviewer-cli \
        --env-file .env \
        -v "$(pwd)/$dir_path:/app/code-to-review:ro" \
        -v "$(pwd)/logs:/app/logs" \
        -v "$(pwd)/results:/app/results" \
        smart-code-reviewer:latest \
        python enhanced_code_reviewer.py "/app/code-to-review"
}

# Stop all containers
stop() {
    print_info "Stopping Smart Code Reviewer containers..."
    docker-compose down
    print_success "Containers stopped!"
}

# Clean up containers and images
clean() {
    print_info "Cleaning up Docker containers and images..."
    docker-compose down --volumes --remove-orphans
    docker rmi smart-code-reviewer:latest 2>/dev/null || true
    print_success "Cleanup completed!"
}

# Show logs
logs() {
    docker-compose logs -f smart-code-reviewer
}

# Show usage
usage() {
    echo "Smart Code Reviewer Docker Management"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  build                 Build the Docker image"
    echo "  run                   Run Flask API with Docker Compose"
    echo "  interactive           Run Flask API in interactive mode"
    echo "  file <path>           Review a specific file (legacy CLI mode)"
    echo "  directory <path>      Review all Python files in directory (legacy CLI mode)"
    echo "  stop                  Stop all containers"
    echo "  clean                 Clean up containers and images"
    echo "  logs                  Show container logs"
    echo "  help                  Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 run                # Start Flask API at http://localhost:8080"
    echo "  $0 interactive        # Start Flask API in interactive mode"
    echo "  $0 file examples/vulnerable_code.py"
    echo "  $0 directory examples/"
    echo ""
    echo "API Endpoints (when running Flask service):"
    echo "  GET  http://localhost:8080/                  - API information"
    echo "  GET  http://localhost:8080/models            - List available models"
    echo "  GET  http://localhost:8080/files             - List available files"
    echo "  GET  http://localhost:8080/review/<filename> - Review specific file"
    echo "  GET  http://localhost:8080/review-all        - Review all files"
    echo "  POST http://localhost:8080/review-custom     - Review custom code"
    echo ""
    echo "Prerequisites:"
    echo "  - Docker and Docker Compose installed"
    echo "  - .env file with API keys configured"
}

# Main script logic
case "$1" in
    build)
        build
        ;;
    run)
        run_compose
        ;;
    interactive)
        run_interactive
        ;;
    file)
        run_with_file "$2"
        ;;
    directory)
        run_with_directory "$2"
        ;;
    stop)
        stop
        ;;
    clean)
        clean
        ;;
    logs)
        logs
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        usage
        exit 1
        ;;
esac 