#!/bin/bash
# Ansible deployment script for Server Inventory Management System

set -e

echo "🚀 Deploying Server Inventory Management System with Ansible"
echo "============================================================"

# Check if Ansible is installed
if ! command -v ansible-playbook &> /dev/null; then
    echo "❌ Ansible is not installed. Installing..."
    
    # Install Ansible based on OS
    if command -v dnf &> /dev/null; then
        sudo dnf install -y ansible
    elif command -v yum &> /dev/null; then
        sudo yum install -y ansible
    elif command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y ansible
    else
        echo "❌ Unable to install Ansible automatically"
        echo "Please install Ansible manually and run this script again"
        exit 1
    fi
fi

# Verify inventory file exists
if [ ! -f "inventory.ini" ]; then
    echo "❌ inventory.ini not found"
    echo "Please create inventory.ini with your target servers"
    exit 1
fi

# Test connectivity to all hosts
echo "🔍 Testing connectivity to target hosts..."
ansible all -m ping -i inventory.ini

if [ $? -ne 0 ]; then
    echo "❌ Cannot connect to some hosts. Please check:"
    echo "   - SSH keys are properly configured"
    echo "   - Target hosts are accessible"
    echo "   - inventory.ini has correct IP addresses"
    exit 1
fi

# Run syntax check
echo "✅ Running playbook syntax check..."
ansible-playbook --syntax-check site.yml

# Run the deployment
echo "🚀 Starting deployment..."
ansible-playbook site.yml --ask-become-pass

echo ""
echo "🎉 Deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Access the application on your target servers"
echo "2. Login with admin/admin123"
echo "3. Change default credentials"
echo "4. Configure SSL certificates for production"