#!/usr/bin/env python3
"""
Installation Test Script for Server Inventory Management System
This script verifies that all dependencies are properly installed.
"""

import sys
import importlib

def test_python_version():
    """Test Python version compatibility"""
    print("Testing Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True

def test_dependencies():
    """Test required Python packages"""
    print("\nTesting dependencies...")
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'flask_jwt_extended',
        'werkzeug'
    ]
    
    all_good = True
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            all_good = False
    
    return all_good

def test_file_structure():
    """Test if all required files exist"""
    print("\nTesting file structure...")
    import os
    
    required_files = [
        'backend/app.py',
        'templates/index.html',
        'static/app.js',
        'requirements.txt',
        'README.md'
    ]
    
    all_good = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} is missing")
            all_good = False
    
    return all_good

def test_database_creation():
    """Test database creation"""
    print("\nTesting database creation...")
    try:
        sys.path.append('backend')
        from app import app, db
        
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully")
            return True
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Server Inventory Management System - Installation Test")
    print("=" * 60)
    
    tests = [
        test_python_version,
        test_dependencies,
        test_file_structure,
        test_database_creation
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    if all(results):
        print("🎉 All tests passed! The system is ready to use.")
        print("\nTo start the application:")
        print("  Windows: Double-click start.bat")
        print("  Linux:   ./start.sh")
        print("\nDefault login: admin/admin123")
        print("Access URL: http://localhost:5000")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nTo fix issues:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Ensure all files are present")
        print("3. Check Python version (3.8+ required)")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)