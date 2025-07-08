# Ansible Deployment for Server Inventory Management System

## 📋 Prerequisites

### Control Node (where you run Ansible)
- Ansible 2.9+
- Python 3.6+
- SSH access to target servers

### Target Servers
- Red Hat Enterprise Linux 8+
- SSH access with sudo privileges
- Python 3 installed

## 🚀 Quick Deployment

### 1. Configure Inventory
Edit `inventory.ini` with your server details:
```ini
[rhel_servers]
server1 ansible_host=192.168.1.10 ansible_user=root
server2 ansible_host=192.168.1.11 ansible_user=root
```

### 2. Run Deployment
```bash
chmod +x deploy.sh
./deploy.sh
```

### 3. Access Application
- URL: http://YOUR_SERVER_IP
- Login: admin/admin123

## 📁 File Structure

```
ansible/
├── playbook.yml              # Main installation playbook
├── site.yml                  # Site-wide playbook with verification
├── inventory.ini             # Server inventory
├── ansible.cfg              # Ansible configuration
├── deploy.sh                # Deployment script
├── group_vars/
│   └── all.yml              # Global variables
└── templates/
    ├── server-inventory.service.j2  # Systemd service
    ├── nginx.conf.j2               # Nginx configuration
    ├── backup.sh.j2               # Backup script
    └── logrotate.j2              # Log rotation
```

## ⚙️ Configuration Variables

Edit `group_vars/all.yml` to customize:

```yaml
app_dir: /opt/server_inventory
backup_dir: /opt/backups/server_inventory
log_dir: /var/log/server_inventory
backup_retention_days: 30
```

## 🔧 Manual Commands

### Test Connectivity
```bash
ansible all -m ping
```

### Run Specific Tasks
```bash
# Only install packages
ansible-playbook playbook.yml --tags packages

# Only configure services
ansible-playbook playbook.yml --tags services
```

### Check Syntax
```bash
ansible-playbook --syntax-check site.yml
```

### Dry Run
```bash
ansible-playbook --check site.yml
```

## 🛡️ Security Features

The playbook automatically configures:
- Firewall rules (ports 80, 443, 5000)
- SELinux contexts and booleans
- Secure systemd service with restrictions
- Log rotation and backup automation
- Nginx reverse proxy with security headers

## 📊 What Gets Installed

1. **System Packages**: Python3, Nginx, Firewalld
2. **Application**: Flask app with virtual environment
3. **Database**: SQLite with automatic initialization
4. **Services**: Systemd service for auto-start
5. **Security**: Firewall and SELinux configuration
6. **Monitoring**: Log rotation and backup scripts
7. **Web Server**: Nginx reverse proxy

## 🔍 Verification

After deployment, the playbook:
- Tests application health (HTTP 200 response)
- Verifies services are running
- Displays access information

## 📝 Customization

### Different Database
To use PostgreSQL instead of SQLite, add to `group_vars/all.yml`:
```yaml
database_type: postgresql
database_host: localhost
database_name: server_inventory
```

### SSL Configuration
Add SSL certificate paths:
```yaml
ssl_certificate: /path/to/cert.pem
ssl_certificate_key: /path/to/key.pem
```

### Custom Domain
```yaml
server_name: inventory.company.com
```

## 🆘 Troubleshooting

### Connection Issues
```bash
# Test SSH connectivity
ssh user@target_server

# Check SSH key
ssh-add -l
```

### Permission Issues
```bash
# Run with password prompt
ansible-playbook site.yml --ask-become-pass

# Use specific SSH key
ansible-playbook site.yml --private-key ~/.ssh/id_rsa
```

### Service Issues
```bash
# Check service status on target
ansible all -m shell -a "systemctl status server-inventory"

# View logs
ansible all -m shell -a "journalctl -u server-inventory -n 20"
```

## 📞 Support

For issues with the Ansible deployment:
1. Check Ansible logs: `ansible-playbook -vvv site.yml`
2. Verify target server access
3. Check firewall and SELinux settings
4. Review application logs on target servers