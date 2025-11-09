#!/bin/bash
# Heroku Container Deployment Script
# AutoLocal/CapeControl Production Deployment

set -euo pipefail

# Configuration
HEROKU_APP_NAME="${HEROKU_APP_NAME:-autorisen-dac8e65796e7}"
IMAGE_NAME="autorisen:local"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v heroku &> /dev/null; then
        log_error "Heroku CLI is not installed"
        exit 1
    fi
    
    if ! heroku auth:whoami &> /dev/null; then
        log_error "Not logged into Heroku. Run: heroku login"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Build Docker image
build_image() {
    log_info "Building Docker image..."
    
    if docker build -t "$IMAGE_NAME" .; then
        log_success "Docker image built successfully"
    else
        log_error "Docker build failed"
        exit 1
    fi
}

# Deploy to Heroku
deploy_heroku() {
    log_info "Deploying to Heroku app: $HEROKU_APP_NAME"
    
    # Tag for Heroku
    log_info "Tagging image for Heroku registry..."
    docker tag "$IMAGE_NAME" "registry.heroku.com/$HEROKU_APP_NAME/web"
    
    # Login to Heroku Container Registry
    log_info "Logging into Heroku Container Registry..."
    if ! heroku container:login; then
        log_error "Failed to login to Heroku Container Registry"
        exit 1
    fi
    
    # Push image
    log_info "Pushing image to Heroku..."
    if ! docker push "registry.heroku.com/$HEROKU_APP_NAME/web"; then
        log_error "Failed to push image to Heroku"
        exit 1
    fi
    
    # Release
    log_info "Releasing container..."
    if ! heroku container:release web --app "$HEROKU_APP_NAME"; then
        log_error "Failed to release container"
        exit 1
    fi
    
    log_success "Deployment completed!"
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    local app_url="https://$HEROKU_APP_NAME.herokuapp.com"
    
    # Wait for app to start
    sleep 30
    
    # Health check
    if curl -f -s "$app_url/api/health" > /dev/null; then
        log_success "Health check passed"
    else
        log_warning "Health check failed - app may still be starting"
    fi
    
    log_info "App URL: $app_url"
    log_info "Health: $app_url/api/health"
    log_info "Version: $app_url/api/version"
}

# Main execution
main() {
    echo "🚀 Starting Heroku Container Deployment"
    echo "========================================="
    
    check_prerequisites
    build_image
    deploy_heroku
    verify_deployment
    
    log_success "Deployment process completed!"
}

# Handle script arguments
case "${1:-deploy}" in
    "build")
        build_image
        ;;
    "deploy")
        main
        ;;
    "verify")
        verify_deployment
        ;;
    *)
        echo "Usage: $0 [build|deploy|verify]"
        echo "  build   - Build Docker image only"
        echo "  deploy  - Full deployment (default)"
        echo "  verify  - Verify existing deployment"
        exit 1
        ;;
esac