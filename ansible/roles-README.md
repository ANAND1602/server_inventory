# Ansible Roles Deployment

## 📁 Role Structure

```
roles/
├── common/                 # System setup
│   ├── tasks/main.yml     # Package installation, user creation
│   ├── handlers/main.yml  # Service handlers
│   └── meta/main.yml      # Role metadata
├── application/           # Flask application
│   ├── tasks/main.yml     # App deployment, systemd service
│   ├── handlers/main.yml  # App service handlers
│   ├── templates/         # Service, backup, logrotate templates
│   └── meta/main.yml      # Role dependencies
└── webserver/            # Nginx web server
    ├── tasks/main.yml    # Nginx installation and config
    ├── handlers/main.yml # Nginx handlers
    ├── templates/        # Nginx configuration
    └── meta/main.yml     # Role dependencies
```

## 🎯 Role Responsibilities

### Common Role
- System package updates
- Base package installation (Python3, Git, Firewalld)
- Application user creation
- Directory structure setup
- Firewall configuration
- SELinux configuration

### Application Role
- Application file deployment
- Python virtual environment setup
- Dependency installation
- Systemd service configuration
- Backup script setup
- Log rotation configuration
- Service startup

### Webserver Role
- Nginx installation
- Reverse proxy configuration
- Security headers setup
- Service management

## 🚀 Deployment Commands

### Full Deployment
```bash
ansible-playbook site.yml
```

### Role-specific Deployment
```bash
# Only common setup
ansible-playbook site.yml --tags common

# Only application
ansible-playbook site.yml --tags application

# Only webserver
ansible-playbook site.yml --tags webserver
```

### Targeted Deployment
```bash
# Specific server
ansible-playbook site.yml --limit server1

# Specific role on specific server
ansible-playbook site.yml --limit server1 --tags application
```

## 🔧 Role Dependencies

The roles have automatic dependencies:
- `application` depends on `common`
- `webserver` depends on `common`

Dependencies are handled automatically by Ansible.

## ⚙️ Customization

### Override Variables
Create `host_vars/server1.yml`:
```yaml
app_dir: /custom/path
backup_retention_days: 60
```

### Skip Roles
```bash
ansible-playbook site.yml --skip-tags webserver
```

### Role Testing
```bash
# Test individual role
ansible-playbook -i inventory.ini --check roles/common/tasks/main.yml
```

## 📊 Benefits of Role-based Structure

1. **Modularity**: Each role has specific responsibility
2. **Reusability**: Roles can be used in other projects
3. **Maintainability**: Easier to update individual components
4. **Testing**: Can test roles independently
5. **Scalability**: Easy to add new roles or modify existing ones