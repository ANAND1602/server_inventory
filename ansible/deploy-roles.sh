#!/bin/bash
# Role-based Ansible deployment script

set -e

echo "🚀 Deploying with Ansible Roles"
echo "================================"

# Check Ansible installation
if ! command -v ansible-playbook &> /dev/null; then
    echo "❌ Ansible not found. Installing..."
    if command -v dnf &> /dev/null; then
        sudo dnf install -y ansible
    else
        echo "Please install Ansible manually"
        exit 1
    fi
fi

# Test connectivity
echo "🔍 Testing connectivity..."
ansible all -m ping -i inventory.ini

# Run syntax check
echo "✅ Checking syntax..."
ansible-playbook --syntax-check site.yml

# List roles
echo "📋 Roles to be executed:"
echo "  - common (system setup)"
echo "  - application (Flask app)"
echo "  - webserver (Nginx)"

# Deploy with roles
echo "🚀 Deploying with roles..."
ansible-playbook site.yml --ask-become-pass

echo "🎉 Role-based deployment completed!"