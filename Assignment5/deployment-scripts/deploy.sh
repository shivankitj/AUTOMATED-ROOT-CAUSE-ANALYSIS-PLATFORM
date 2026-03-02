#!/bin/bash
################################################################################
# ARCA Backend - Deployment Script
# This script deploys updates to the ARCA backend on EC2
################################################################################

set -e  # Exit on error

echo "=========================================="
echo "ARCA Backend - Deployment"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}


if [ ! -f "app.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_info "Pulling latest code from repository..."
git pull origin main
print_success "Code updated"

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
print_info "Installing dependencies..."
pip install -r requirements.txt --quiet
print_success "Dependencies installed"

# Run database migrations (if any)
# print_info "Running database migrations..."
# python manage.py migrate
# print_success "Migrations complete"

# Run tests
print_info "Running tests..."
if [ -d "tests" ]; then
    python -m pytest tests/ -v --tb=short || {
        print_error "Tests failed!"
        read -p "Continue deployment anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    }
    print_success "Tests passed"
else
    print_info "No tests directory found, skipping tests"
fi

# Restart backend service
print_info "Restarting backend service..."
sudo systemctl restart arca-backend

# Wait for service to start
sleep 5

# Check service status
if sudo systemctl is-active --quiet arca-backend; then
    print_success "Service restarted successfully"
else
    print_error "Service failed to start!"
    echo "Checking logs..."
    sudo journalctl -u arca-backend -n 50 --no-pager
    exit 1
fi

# Health check
print_info "Performing health check..."
sleep 2
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/health)

if [ "$HEALTH_CHECK" = "200" ]; then
    print_success "Health check passed"
else
    print_error "Health check failed (HTTP $HEALTH_CHECK)"
    exit 1
fi

# Reload Nginx (if config changed)
print_info "Reloading Nginx..."
sudo nginx -t && sudo systemctl reload nginx
print_success "Nginx reloaded"

echo ""
echo "=========================================="
print_success "Deployment completed successfully!"
echo "=========================================="
echo ""
echo "Service status:"
sudo systemctl status arca-backend --no-pager -l
echo ""
echo "Recent logs:"
sudo journalctl -u arca-backend -n 20 --no-pager
echo ""
echo "To view live logs:"
echo "  sudo journalctl -u arca-backend -f"
echo ""
