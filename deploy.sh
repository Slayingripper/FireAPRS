#!/bin/bash

# FireAPRS Deployment Script
# This script helps you deploy and manage the FireAPRS Docker container

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

# Build the Docker image
build_image() {
    print_status "Building FireAPRS Docker image..."
    docker build -t fire-aprs:latest .
    print_status "Docker image built successfully!"
}

# Run once (for crontab use)
run_once() {
    print_status "Running FireAPRS once..."
    docker-compose up fire-aprs
}

# Run with auto-scheduling
run_scheduled() {
    print_status "Starting FireAPRS with auto-scheduling..."
    docker-compose --profile scheduled up -d fire-aprs-scheduled
    print_status "FireAPRS is now running with auto-scheduling. Check logs with: docker logs fire-aprs-scheduled"
}

# Stop all containers
stop() {
    print_status "Stopping all FireAPRS containers..."
    docker-compose down
    docker-compose --profile scheduled down
    print_status "All containers stopped."
}

# Show logs
show_logs() {
    if [ "$1" = "scheduled" ]; then
        docker logs -f fire-aprs-scheduled
    else
        docker logs -f fire-aprs
    fi
}

# Setup crontab entry
setup_crontab() {
    print_status "Setting up crontab entry..."
    
    # Get current directory
    CURRENT_DIR=$(pwd)
    
    # Suggested crontab entry
    CRON_ENTRY="0 */2 * * * cd $CURRENT_DIR && docker-compose up fire-aprs >> /tmp/fire-aprs-cron.log 2>&1"
    
    echo ""
    print_status "To run FireAPRS every 2 hours via crontab, add this line to your crontab:"
    echo ""
    echo "$CRON_ENTRY"
    echo ""
    print_status "To edit your crontab, run: crontab -e"
    print_status "To view current crontab: crontab -l"
    echo ""
    print_warning "Make sure to customize the config.ini file with your credentials before running!"
}

# Show usage
usage() {
    echo "FireAPRS Docker Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build       Build the Docker image"
    echo "  run-once    Run FireAPRS once (suitable for crontab)"
    echo "  run-scheduled Run FireAPRS with auto-scheduling"
    echo "  stop        Stop all containers"
    echo "  logs        Show logs from the default container"
    echo "  logs-scheduled Show logs from the scheduled container"
    echo "  setup-cron  Show instructions for setting up crontab"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build                 # Build the image"
    echo "  $0 run-once             # Run once and exit"
    echo "  $0 run-scheduled        # Run with internal scheduling"
    echo "  $0 setup-cron           # Get crontab setup instructions"
}

# Main script logic
case "${1:-help}" in
    build)
        check_docker
        build_image
        ;;
    run-once)
        check_docker
        run_once
        ;;
    run-scheduled)
        check_docker
        run_scheduled
        ;;
    stop)
        check_docker
        stop
        ;;
    logs)
        show_logs
        ;;
    logs-scheduled)
        show_logs "scheduled"
        ;;
    setup-cron)
        setup_crontab
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
