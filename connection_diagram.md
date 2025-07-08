# Frontend-Backend Connection Flow

## 🔗 Connection Architecture

### 1. Initial Page Load
```
Browser → GET / → Flask → render_template('index.html') → HTML + CSS + JS
```

### 2. Authentication Flow
```
Frontend (app.js) → POST /api/login → Flask (app.py) → Database → JWT Token → localStorage
```

### 3. Server Management
```
Frontend → GET /api/servers → Flask → SQLAlchemy → Database → JSON Response → Display
Frontend → POST /api/servers → Flask → Validation → Database → Success/Error
Frontend → DELETE /api/servers/{id} → Flask → Database → Audit Log → Success
```

### 4. Real-time Updates
```
User Action → JavaScript Function → API Call → Database Update → UI Refresh
```

## 📡 API Endpoints Connection

| Frontend Function | HTTP Method | Backend Route | Database Action |
|------------------|-------------|---------------|-----------------|
| `login()` | POST | `/api/login` | Query User table |
| `loadServers()` | GET | `/api/servers` | Query Server table |
| `addServer()` | POST | `/api/servers` | Insert Server record |
| `deleteServer()` | DELETE | `/api/servers/{id}` | Delete Server record |
| `loadLogs()` | GET | `/api/logs` | Query AuditLog table |

## 🔐 Authentication Flow

### Step 1: Login Request
```javascript
// Frontend (app.js)
const response = await fetch('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
});
```

### Step 2: Backend Validation
```python
# Backend (app.py)
@app.route('/api/login', methods=['POST'])
def login():
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=user.username)
        return jsonify({'access_token': access_token, 'role': user.role})
```

### Step 3: Token Storage & Usage
```javascript
// Store token
localStorage.setItem('authToken', data.access_token);

// Use token in subsequent requests
headers: { 'Authorization': `Bearer ${authToken}` }
```

## 🗄️ Database Connection

### SQLAlchemy Configuration
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///server_inventory.db'
db = SQLAlchemy(app)
```

### Model Relationships
```python
# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')

# Server Model  
class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), nullable=False)
    # ... other fields
    created_by = db.Column(db.String(80), nullable=False)  # Links to User

# Audit Log Model
class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80), nullable=False)  # Links to User
    action = db.Column(db.String(50), nullable=False)
    resource = db.Column(db.String(100), nullable=False)
```

## 🔄 Data Flow Examples

### Adding a Server
1. **Frontend**: User fills form → `addServer()` function called
2. **JavaScript**: Form data collected → POST request to `/api/servers`
3. **Flask**: Route handler validates data → Creates Server object
4. **Database**: SQLAlchemy inserts record → Returns success
5. **Audit**: Log entry created → Action recorded
6. **Response**: Success message → Frontend updates UI

### Loading Servers
1. **Frontend**: Page loads → `loadServers()` called
2. **JavaScript**: GET request to `/api/servers` with JWT token
3. **Flask**: Token validated → User authorized → Query all servers
4. **Database**: SQLAlchemy fetches records → Returns data
5. **Response**: JSON array → Frontend displays in table

## 🛡️ Security Integration

### JWT Token Flow
```
Login → Generate JWT → Store in localStorage → Include in headers → Validate on server
```

### Role-Based Access
```python
# Backend check
if user.role != 'admin':
    return jsonify({'error': 'Admin access required'}), 403
```

```javascript
// Frontend check
if (currentUser.role !== 'admin') {
    document.getElementById('addServerBtn').classList.add('hidden');
}
```

## 📊 Error Handling

### Frontend Error Handling
```javascript
try {
    const response = await fetch('/api/servers');
    if (response.ok) {
        // Success
    } else if (response.status === 401) {
        logout(); // Token expired
    } else {
        showAlert('Error occurred', 'danger');
    }
} catch (error) {
    showAlert('Connection error', 'danger');
}
```

### Backend Error Responses
```python
# Validation error
return jsonify({'error': 'Invalid input'}), 400

# Authentication error  
return jsonify({'error': 'Invalid credentials'}), 401

# Authorization error
return jsonify({'error': 'Admin access required'}), 403
```