#!/bin/bash

# Contract Tracker - Docker Management Scripts

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to build the Docker image
build_image() {
    print_status "Building Contract Tracker Docker image..."
    docker build -t contract-tracker:latest .
    print_success "Docker image built successfully!"
}

# Function to run the container
run_container() {
    print_status "Starting Contract Tracker container..."
    
    # Create data directory if it doesn't exist
    mkdir -p ./data
    
    docker run -d \
        --name contract-tracker \
        -p 5000:5000 \
        -v "$(pwd)/data:/app/data" \
        -e FLASK_ENV=production \
        -e SECRET_KEY="docker-secret-key-$(date +%s)" \
        contract-tracker:latest
    
    print_success "Contract Tracker is running!"
    print_status "Access the application at: http://localhost:5000"
    print_status "To view logs: docker logs -f contract-tracker"
}

# Function to run with docker-compose
run_compose() {
    print_status "Starting Contract Tracker with docker-compose..."
    
    # Create data directory if it doesn't exist
    mkdir -p ./data
    
    docker-compose up -d
    
    print_success "Contract Tracker is running with docker-compose!"
    print_status "Access the application at: http://localhost:5000"
    print_status "To view logs: docker-compose logs -f"
}

# Function to run with nginx
run_with_nginx() {
    print_status "Starting Contract Tracker with nginx..."
    
    # Create data directory if it doesn't exist
    mkdir -p ./data
    
    docker-compose --profile with-nginx up -d
    
    print_success "Contract Tracker is running with nginx!"
    print_status "Access the application at: http://localhost (port 80)"
    print_status "To view logs: docker-compose logs -f"
}

# Function to stop the container
stop_container() {
    print_status "Stopping Contract Tracker..."
    
    if docker ps -q -f name=contract-tracker | grep -q .; then
        docker stop contract-tracker
        docker rm contract-tracker
        print_success "Contract Tracker stopped and removed!"
    else
        print_warning "Contract Tracker container is not running."
    fi
    
    # Also stop docker-compose services
    if docker-compose ps -q | grep -q .; then
        docker-compose down
        print_success "Docker-compose services stopped!"
    fi
}

# Function to view logs
view_logs() {
    if docker ps -q -f name=contract-tracker | grep -q .; then
        docker logs -f contract-tracker
    elif docker-compose ps -q | grep -q .; then
        docker-compose logs -f
    else
        print_error "No running Contract Tracker containers found."
    fi
}

# Function to show status
show_status() {
    print_status "Contract Tracker Status:"
    echo ""
    
    if docker ps -q -f name=contract-tracker | grep -q .; then
        print_success "Container is running"
        docker ps -f name=contract-tracker
    elif docker-compose ps -q | grep -q .; then
        print_success "Docker-compose services are running"
        docker-compose ps
    else
        print_warning "No Contract Tracker containers are running"
    fi
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    
    # Stop and remove containers
    stop_container
    
    # Remove image
    if docker images -q contract-tracker:latest | grep -q .; then
        docker rmi contract-tracker:latest
        print_success "Docker image removed!"
    fi
    
    # Remove unused images
    docker image prune -f
    
    print_success "Cleanup completed!"
}

# Function to show help
show_help() {
    echo "Contract Tracker - Docker Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build       Build the Docker image"
    echo "  run         Run the container directly"
    echo "  compose     Run with docker-compose"
    echo "  nginx       Run with nginx reverse proxy"
    echo "  stop        Stop all running containers"
    echo "  logs        View container logs"
    echo "  status      Show container status"
    echo "  cleanup     Stop containers and remove images"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build && $0 run"
    echo "  $0 compose"
    echo "  $0 nginx"
    echo "  $0 logs"
}

# Main script logic
main() {
    check_docker
    
    case "${1:-help}" in
        build)
            build_image
            ;;
        run)
            build_image
            run_container
            ;;
        compose)
            run_compose
            ;;
        nginx)
            run_with_nginx
            ;;
        stop)
            stop_container
            ;;
        logs)
            view_logs
            ;;
        status)
            show_status
            ;;
        cleanup)
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
