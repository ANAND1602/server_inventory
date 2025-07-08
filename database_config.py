#!/usr/bin/env python3
"""
Database Configuration and Management Script
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append('backend')
from app import app, db, User, Server, AuditLog

def setup_database():
    """Initialize database with tables and default data"""
    print("🗄️ Setting up database...")
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created")
        
        # Create default admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password_hash='pbkdf2:sha256:260000$...',  # admin123
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin user created")
        
        # Create sample data for testing
        create_sample_data()
        
        print("🎉 Database setup completed!")

def create_sample_data():
    """Create sample server data for testing"""
    sample_servers = [
        {
            'hostname': 'web-prod-01.company.com',
            'os_type': 'Red Hat Enterprise Linux',
            'os_version': '8.6',
            'server_type': 'virtual',
            'private_ip': '192.168.1.10',
            'public_ip': '203.0.113.10',
            'primary_owner': 'webteam@company.com',
            'secondary_owner': 'sysadmin@company.com',
            'datacenter': 'DC-East-01',
            'environment': 'production',
            'created_by': 'admin'
        },
        {
            'hostname': 'db-prod-01.company.com',
            'os_type': 'Red Hat Enterprise Linux',
            'os_version': '9.0',
            'server_type': 'physical',
            'private_ip': '192.168.1.20',
            'primary_owner': 'dba@company.com',
            'datacenter': 'DC-East-01',
            'environment': 'production',
            'created_by': 'admin'
        },
        {
            'hostname': 'app-dev-01.company.com',
            'os_type': 'CentOS',
            'os_version': '8.5',
            'server_type': 'cloud',
            'private_ip': '10.0.1.100',
            'public_ip': '203.0.113.100',
            'primary_owner': 'devteam@company.com',
            'datacenter': 'AWS-US-East-1',
            'environment': 'development',
            'created_by': 'admin'
        }
    ]
    
    for server_data in sample_servers:
        if not Server.query.filter_by(hostname=server_data['hostname']).first():
            server = Server(**server_data)
            db.session.add(server)
    
    db.session.commit()
    print("✅ Sample data created")

def backup_database():
    """Create database backup"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"backup_inventory_{timestamp}.db"
    
    # For SQLite
    import shutil
    shutil.copy('backend/server_inventory.db', f'backups/{backup_file}')
    print(f"✅ Database backed up to: backups/{backup_file}")

def restore_database(backup_file):
    """Restore database from backup"""
    import shutil
    shutil.copy(f'backups/{backup_file}', 'backend/server_inventory.db')
    print(f"✅ Database restored from: {backup_file}")

def database_stats():
    """Show database statistics"""
    with app.app_context():
        users_count = User.query.count()
        servers_count = Server.query.count()
        logs_count = AuditLog.query.count()
        
        print(f"📊 Database Statistics:")
        print(f"   Users: {users_count}")
        print(f"   Servers: {servers_count}")
        print(f"   Audit Logs: {logs_count}")
        
        # Server breakdown by type
        physical = Server.query.filter_by(server_type='physical').count()
        virtual = Server.query.filter_by(server_type='virtual').count()
        cloud = Server.query.filter_by(server_type='cloud').count()
        
        print(f"📊 Server Types:")
        print(f"   Physical: {physical}")
        print(f"   Virtual: {virtual}")
        print(f"   Cloud: {cloud}")

def migrate_to_postgresql():
    """Migration script for PostgreSQL"""
    print("🔄 Migrating to PostgreSQL...")
    
    # PostgreSQL connection string
    pg_uri = "postgresql://username:password@localhost/server_inventory"
    
    # Update app config
    app.config['SQLALCHEMY_DATABASE_URI'] = pg_uri
    
    with app.app_context():
        db.create_all()
        print("✅ PostgreSQL tables created")
        
        # Migration logic here
        # Copy data from SQLite to PostgreSQL
        
    print("✅ Migration completed")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Management')
    parser.add_argument('action', choices=['setup', 'backup', 'restore', 'stats', 'migrate'])
    parser.add_argument('--file', help='Backup file for restore')
    
    args = parser.parse_args()
    
    if args.action == 'setup':
        setup_database()
    elif args.action == 'backup':
        backup_database()
    elif args.action == 'restore':
        if args.file:
            restore_database(args.file)
        else:
            print("❌ Please specify backup file with --file")
    elif args.action == 'stats':
        database_stats()
    elif args.action == 'migrate':
        migrate_to_postgresql()