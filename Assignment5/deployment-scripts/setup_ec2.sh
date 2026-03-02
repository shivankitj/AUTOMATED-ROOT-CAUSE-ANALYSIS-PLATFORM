#!/bin/bash
################################################################################
# ARCA Backend - AWS EC2 Setup Script
# This script prepares an EC2 instance for running the ARCA backend
################################################################################

set -e  # Exit on error

echo "=========================================="
echo "ARCA Backend - AWS EC2 Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if running as ubuntu user
if [ "$USER" != "ubuntu" ]; then
    print_error "This script should be run as ubuntu user"
    exit 1
fi

# Update system packages
print_info "Updating system packages..."
sudo apt update && sudo apt upgrade -y
print_success "System updated"

# Install Python 3.11
print_info "Installing Python 3.11..."
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
print_success "Python 3.11 installed"

# Install Nginx
print_info "Installing Nginx..."
sudo apt install -y nginx
sudo systemctl enable nginx
print_success "Nginx installed"

# Install Git
print_info "Installing Git..."
sudo apt install -y git curl wget
print_success "Git installed"

# Install AWS CLI
print_info "Installing AWS CLI..."
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -q awscliv2.zip
sudo ./aws/install
rm -rf aws awscliv2.zip
print_success "AWS CLI installed"

# Create application directory
print_info "Creating application directory..."
sudo mkdir -p /var/www/arca-backend
sudo chown -R ubuntu:ubuntu /var/www/arca-backend
print_success "Application directory created"

# Create log directory
print_info "Creating log directory..."
sudo mkdir -p /var/log/arca
sudo chown -R ubuntu:ubuntu /var/log/arca
print_success "Log directory created"

# Clone repository (replace with your repo URL)
print_info "Repository setup..."
echo "Please manually clone your repository with:"
echo "  cd /var/www/arca-backend"
echo "  git clone https://github.com/YOUR_USERNAME/arca-platform.git ."

# Create virtual environment
print_info "Setting up Python virtual environment..."
cd /var/www/arca-backend
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
print_success "Virtual environment created"

# Create .env template
print_info "Creating environment template..."
cat > /var/www/arca-backend/.env.template << 'EOF'
# Application Settings
FLASK_ENV=production
API_PORT=5000
DEBUG=False

# MongoDB Connection
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/arca_db?retryWrites=true&w=majority
MONGODB_DB_NAME=arca_db

# AWS Configuration
AWS_REGION=us-east-1
AWS_S3_BUCKET=arca-logs-storage

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# CORS Settings
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:5173

# Monitoring
ENABLE_METRICS=True
LOG_LEVEL=INFO
EOF
print_success "Environment template created"

# Create Nginx configuration
print_info "Creating Nginx configuration..."
sudo tee /etc/nginx/sites-available/arca-backend > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # CORS headers
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
        
        # Handle preflight requests
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:5000/api/health;
        access_log off;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/arca-backend /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
print_success "Nginx configured"

# Create systemd service
print_info "Creating systemd service..."
sudo tee /etc/systemd/system/arca-backend.service > /dev/null << 'EOF'
[Unit]
Description=ARCA Backend API Service
After=network.target

[Service]
Type=notify
User=ubuntu
Group=ubuntu
WorkingDirectory=/var/www/arca-backend
Environment="PATH=/var/www/arca-backend/venv/bin"
ExecStart=/var/www/arca-backend/venv/bin/gunicorn \
    --workers 4 \
    --threads 2 \
    --bind 127.0.0.1:5000 \
    --access-logfile /var/log/arca/access.log \
    --error-logfile /var/log/arca/error.log \
    --log-level info \
    --timeout 120 \
    app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
KillSignal=SIGQUIT
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
print_success "Systemd service created"

# Create health check script
print_info "Creating health check script..."
sudo tee /usr/local/bin/arca-health-check.sh > /dev/null << 'EOF'
#!/bin/bash
ENDPOINT="http://localhost:5000/api/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $ENDPOINT)

if [ $RESPONSE -ne 200 ]; then
    echo "[$(date)] Health check failed with status $RESPONSE" >> /var/log/arca/health-check.log
    sudo systemctl restart arca-backend
fi
EOF

sudo chmod +x /usr/local/bin/arca-health-check.sh
print_success "Health check script created"

# Configure firewall (UFW)
print_info "Configuring firewall..."
sudo apt install -y ufw
sudo ufw allow 22/tcp    
sudo ufw allow 80/tcp    
sudo ufw allow 443/tcp   # HTTPS
echo "y" | sudo ufw enable
print_success "Firewall configured"

# Final instructions
echo ""
echo "=========================================="
print_success "EC2 Server setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Clone your repository:"
echo "   cd /var/www/arca-backend"
echo "   git clone https://github.com/shivankitj/arca-platform.git ."
echo ""
echo "2. Copy and edit environment file:"
echo "   cp .env.template .env"
echo "   nano .env"
echo ""
echo "3. Install Python dependencies:"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo ""
echo "4. Start the service:"
echo "   sudo systemctl start arca-backend"
echo "   sudo systemctl enable arca-backend"
echo ""
echo "5. Check status:"
echo "   sudo systemctl status arca-backend"
echo ""
echo "6. View logs:"
echo "   sudo journalctl -u arca-backend -f"
echo ""
echo "7. Test endpoints:"
echo "   curl http://localhost/health"
echo ""
echo "=========================================="
