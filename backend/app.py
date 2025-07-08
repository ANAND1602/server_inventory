from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import logging
import re
import os

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///server_inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server_inventory.log'),
        logging.StreamHandler()
    ]
)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # admin or user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), nullable=False)
    os_type = db.Column(db.String(50), nullable=False)
    os_version = db.Column(db.String(50), nullable=False)
    server_type = db.Column(db.String(20), nullable=False)  # physical, virtual, cloud
    private_ip = db.Column(db.String(15), nullable=False)
    public_ip = db.Column(db.String(15))
    primary_owner = db.Column(db.String(100), nullable=False)
    secondary_owner = db.Column(db.String(100))
    datacenter = db.Column(db.String(100), nullable=False)
    environment = db.Column(db.String(20), nullable=False)  # prod, dev, test
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(80), nullable=False)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    resource = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(15))

# Security functions
def validate_ip(ip):
    pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return re.match(pattern, ip) is not None

def log_action(user, action, resource, details=None):
    log_entry = AuditLog(
        user=user,
        action=action,
        resource=resource,
        details=details,
        ip_address=request.remote_addr
    )
    db.session.add(log_entry)
    db.session.commit()
    logging.info(f"User {user} performed {action} on {resource}")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if len(data['password']) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    
    user = User(
        username=data['username'],
        password_hash=generate_password_hash(data['password']),
        role=data.get('role', 'user')
    )
    
    db.session.add(user)
    db.session.commit()
    
    log_action('system', 'USER_CREATED', f"user:{data['username']}")
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=user.username)
        log_action(user.username, 'LOGIN', 'system')
        return jsonify({
            'access_token': access_token,
            'role': user.role,
            'username': user.username
        })
    
    log_action(data.get('username', 'unknown'), 'LOGIN_FAILED', 'system')
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/servers', methods=['GET'])
@jwt_required()
def get_servers():
    current_user = get_jwt_identity()
    servers = Server.query.all()
    
    result = []
    for server in servers:
        result.append({
            'id': server.id,
            'hostname': server.hostname,
            'os_type': server.os_type,
            'os_version': server.os_version,
            'server_type': server.server_type,
            'private_ip': server.private_ip,
            'public_ip': server.public_ip,
            'primary_owner': server.primary_owner,
            'secondary_owner': server.secondary_owner,
            'datacenter': server.datacenter,
            'environment': server.environment,
            'created_at': server.created_at.isoformat(),
            'created_by': server.created_by
        })
    
    log_action(current_user, 'VIEW_SERVERS', 'servers')
    return jsonify(result)

@app.route('/api/servers', methods=['POST'])
@jwt_required()
def add_server():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    # Validation
    required_fields = ['hostname', 'os_type', 'os_version', 'server_type', 'private_ip', 'primary_owner', 'datacenter', 'environment']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    if not validate_ip(data['private_ip']):
        return jsonify({'error': 'Invalid private IP address'}), 400
    
    if data.get('public_ip') and not validate_ip(data['public_ip']):
        return jsonify({'error': 'Invalid public IP address'}), 400
    
    if data['server_type'] not in ['physical', 'virtual', 'cloud']:
        return jsonify({'error': 'Invalid server type'}), 400
    
    server = Server(
        hostname=data['hostname'],
        os_type=data['os_type'],
        os_version=data['os_version'],
        server_type=data['server_type'],
        private_ip=data['private_ip'],
        public_ip=data.get('public_ip'),
        primary_owner=data['primary_owner'],
        secondary_owner=data.get('secondary_owner'),
        datacenter=data['datacenter'],
        environment=data['environment'],
        created_by=current_user
    )
    
    db.session.add(server)
    db.session.commit()
    
    log_action(current_user, 'SERVER_CREATED', f"server:{data['hostname']}", str(data))
    return jsonify({'message': 'Server added successfully', 'id': server.id}), 201

@app.route('/api/servers/<int:server_id>', methods=['DELETE'])
@jwt_required()
def delete_server(server_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    server = Server.query.get_or_404(server_id)
    hostname = server.hostname
    
    db.session.delete(server)
    db.session.commit()
    
    log_action(current_user, 'SERVER_DELETED', f"server:{hostname}")
    return jsonify({'message': 'Server deleted successfully'})

@app.route('/api/logs', methods=['GET'])
@jwt_required()
def get_logs():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    
    result = []
    for log in logs:
        result.append({
            'id': log.id,
            'user': log.user,
            'action': log.action,
            'resource': log.resource,
            'details': log.details,
            'timestamp': log.timestamp.isoformat(),
            'ip_address': log.ip_address
        })
    
    return jsonify(result)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create default admin user
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created: admin/admin123")
    
    app.run(debug=True, host='0.0.0.0', port=5000)