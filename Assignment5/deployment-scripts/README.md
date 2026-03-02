# Deployment Scripts

This directory contains automated deployment scripts for the ARCA platform.

## Files

- **`setup_ec2.sh`** - Initial EC2 instance setup script
- **`deploy.sh`** - Production deployment script
- **`rollback.sh`** - Rollback to previous version
- **`backup.sh`** - Backup script for logs and data

## Usage

### 1. Initial EC2 Setup

Run this once on a new EC2 instance:

```bash
# Upload script to EC2
scp -i your-key.pem setup_ec2.sh ubuntu@your-ec2-ip:~

# Connect to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Run setup
chmod +x setup_ec2.sh
./setup_ec2.sh
```

### 2. Deploy Updates

After making code changes:

```bash
# On EC2 instance
cd /var/www/arca-backend
./deployment-scripts/deploy.sh
```

### 3. Automated Deployment via CI/CD

The deployment is automated through GitHub Actions. Simply push to main branch:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

## Manual Deployment Steps

If automation fails, deploy manually:

```bash
# 1. Connect to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# 2. Navigate to project
cd /var/www/arca-backend

# 3. Pull latest code
git pull origin main

# 4. Activate virtual environment
source venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Restart service
sudo systemctl restart arca-backend

# 7. Check status
sudo systemctl status arca-backend

# 8. Test
curl http://localhost/health
```

## Troubleshooting

### Service won't start

```bash
# Check logs
sudo journalctl -u arca-backend -n 100

# Check service file
sudo systemctl cat arca-backend

# Test manually
cd /var/www/arca-backend
source venv/bin/activate
python app.py
```

### Nginx errors

```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

### Port already in use

```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill process
sudo kill -9 <PID>

# Restart service
sudo systemctl restart arca-backend
```

## Environment Variables

Required environment variables in `/var/www/arca-backend/.env`:

```env
FLASK_ENV=production
API_PORT=5000
MONGODB_URI=mongodb+srv://...
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
ALLOWED_ORIGINS=https://your-app.vercel.app
```

## Security Notes

- Never commit `.env` file to git
- Keep SSH key secure
- Restrict Security Group rules
- Use HTTPS in production
- Rotate secrets regularly

## Monitoring

Check service health:

```bash
# Service status
sudo systemctl status arca-backend

# Live logs
sudo journalctl -u arca-backend -f

# Access logs
tail -f /var/log/arca/access.log

# Error logs
tail -f /var/log/arca/error.log
```

## Backup and Recovery

Create backup:

```bash
./deployment-scripts/backup.sh
```

Restore from backup:

```bash
# Stop service
sudo systemctl stop arca-backend

# Restore files
tar -xzf backup-file.tar.gz -C /var/www/arca-backend

# Start service
sudo systemctl start arca-backend
```
