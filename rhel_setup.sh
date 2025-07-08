#!/bin/bash
# Red Hat Enterprise Linux Setup Script for Server Inventory System

echo "🔧 Setting up Server Inventory on Red Hat Enterprise Linux"
echo "=========================================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root for security reasons"
   echo "Please run as a regular user with sudo privileges"
   exit 1
fi

# Update system
echo "📦 Updating system packages..."
sudo dnf update -y

# Install required packages
echo "📦 Installing required packages..."
sudo dnf install -y python3 python3-pip python3-venv git nginx firewalld

# Install development tools (optional)
sudo dnf groupinstall -y "Development Tools"

# Create application user
echo "👤 Creating application user..."
sudo useradd -r -s /bin/false -d /opt/server_inventory inventory || echo "User already exists"

# Create application directory
echo "📁 Setting up application directory..."
sudo mkdir -p /opt/server_inventory
sudo mkdir -p /opt/backups/server_inventory
sudo mkdir -p /var/log/server_inventory

# Set ownership
sudo chown inventory:inventory /opt/server_inventory
sudo chown inventory:inventory /opt/backups/server_inventory
sudo chown inventory:inventory /var/log/server_inventory

# Copy application files
echo "📋 Copying application files..."
sudo cp -r * /opt/server_inventory/
sudo chown -R inventory:inventory /opt/server_inventory/

# Create Python virtual environment
echo "🐍 Setting up Python virtual environment..."
sudo -u inventory python3 -m venv /opt/server_inventory/venv

# Install Python dependencies
echo "📦 Installing Python dependencies..."
sudo -u inventory /opt/server_inventory/venv/bin/pip install --upgrade pip
sudo -u inventory /opt/server_inventory/venv/bin/pip install -r /opt/server_inventory/requirements.txt

# Configure firewall
echo "🔥 Configuring firewall..."
sudo systemctl enable firewalld
sudo systemctl start firewalld
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# Configure SELinux
echo "🛡️ Configuring SELinux..."
sudo setsebool -P httpd_can_network_connect 1
sudo semanage port -a -t http_port_t -p tcp 5000 2>/dev/null || echo "Port already configured"

# Set SELinux contexts
sudo semanage fcontext -a -t httpd_exec_t "/opt/server_inventory/venv/bin/python3" 2>/dev/null || echo "Context already set"
sudo restorecon -Rv /opt/server_inventory/

# Install systemd service
echo "⚙️ Installing systemd service..."
sudo cp /opt/server_inventory/server-inventory.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable server-inventory

# Create log rotation configuration
echo "📝 Setting up log rotation..."
sudo tee /etc/logrotate.d/server-inventory > /dev/null <<EOF
/var/log/server_inventory/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 inventory inventory
    postrotate
        systemctl reload server-inventory
    endscript
}
EOF

# Create backup script
echo "💾 Creating backup script..."
sudo tee /opt/server_inventory/backup.sh > /dev/null <<'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups/server_inventory"
DB_PATH="/opt/server_inventory/backend/server_inventory.db"

# Create backup
cp "$DB_PATH" "$BACKUP_DIR/inventory_$DATE.db"

# Compress old backups (older than 7 days)
find "$BACKUP_DIR" -name "*.db" -mtime +7 -exec gzip {} \;

# Remove old compressed backups (older than 30 days)
find "$BACKUP_DIR" -name "*.gz" -mtime +30 -delete

echo "Backup completed: inventory_$DATE.db"
EOF

sudo chmod +x /opt/server_inventory/backup.sh
sudo chown inventory:inventory /opt/server_inventory/backup.sh

# Add backup to crontab
echo "⏰ Setting up automated backups..."
(sudo -u inventory crontab -l 2>/dev/null; echo "0 2 * * * /opt/server_inventory/backup.sh") | sudo -u inventory crontab -

# Configure Nginx (optional)
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/conf.d/server-inventory.conf > /dev/null <<EOF
server {
    listen 80;
    server_name localhost;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /static {
        alias /opt/server_inventory/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Test Nginx configuration
sudo nginx -t

# Start services
echo "🚀 Starting services..."
sudo systemctl start server-inventory
sudo systemctl enable nginx
sudo systemctl start nginx

# Check service status
echo "✅ Checking service status..."
sudo systemctl status server-inventory --no-pager
sudo systemctl status nginx --no-pager

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Access the application: http://$(hostname -I | awk '{print $1}')"
echo "2. Login with: admin/admin123"
echo "3. Change default password immediately"
echo "4. Configure SSL certificate for production"
echo ""
echo "📁 Important Paths:"
echo "   Application: /opt/server_inventory"
echo "   Logs: /var/log/server_inventory"
echo "   Backups: /opt/backups/server_inventory"
echo "   Service: systemctl status server-inventory"
echo ""
echo "🔧 Management Commands:"
echo "   Start:   sudo systemctl start server-inventory"
echo "   Stop:    sudo systemctl stop server-inventory"
echo "   Restart: sudo systemctl restart server-inventory"
echo "   Logs:    sudo journalctl -u server-inventory -f"
echo ""