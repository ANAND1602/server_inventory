let currentUser = null;
let authToken = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    
    // Login form handler
    document.getElementById('loginForm').addEventListener('submit', function(e) {
        e.preventDefault();
        login();
    });
});

// Authentication functions
function checkAuth() {
    const token = localStorage.getItem('authToken');
    const user = localStorage.getItem('currentUser');
    const role = localStorage.getItem('userRole');
    
    if (token && user) {
        authToken = token;
        currentUser = { username: user, role: role };
        showDashboard();
    } else {
        showLogin();
    }
}

async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            currentUser = { username: data.username, role: data.role };
            
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', data.username);
            localStorage.setItem('userRole', data.role);
            
            showDashboard();
        } else {
            showError('loginError', data.error);
        }
    } catch (error) {
        showError('loginError', 'Connection error. Please try again.');
    }
}

function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    localStorage.removeItem('userRole');
    authToken = null;
    currentUser = null;
    showLogin();
}

function showLogin() {
    document.getElementById('loginSection').classList.remove('hidden');
    document.getElementById('dashboardSection').classList.add('hidden');
}

function showDashboard() {
    document.getElementById('loginSection').classList.add('hidden');
    document.getElementById('dashboardSection').classList.remove('hidden');
    
    // Update user info
    document.getElementById('userInfo').textContent = 
        `${currentUser.username} (${currentUser.role})`;
    
    // Hide admin-only elements for regular users
    if (currentUser.role !== 'admin') {
        document.getElementById('addServerBtn').classList.add('hidden');
        document.getElementById('logsSection').classList.add('hidden');
        
        // Hide delete buttons in table (will be handled in loadServers)
    }
    
    loadServers();
    if (currentUser.role === 'admin') {
        loadLogs();
    }
}

// Server management functions
async function loadServers() {
    try {
        const response = await fetch('/api/servers', {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const servers = await response.json();
            displayServers(servers);
        } else if (response.status === 401) {
            logout();
        } else {
            showAlert('Error loading servers', 'danger');
        }
    } catch (error) {
        showAlert('Connection error', 'danger');
    }
}

function displayServers(servers) {
    const tbody = document.getElementById('serversTable');
    tbody.innerHTML = '';
    
    servers.forEach(server => {
        const row = document.createElement('tr');
        
        const typeClass = `server-type-${server.server_type}`;
        const typeIcon = getServerTypeIcon(server.server_type);
        
        row.innerHTML = `
            <td><strong>${server.hostname}</strong></td>
            <td>${server.os_type} ${server.os_version}</td>
            <td><span class="${typeClass}"><i class="${typeIcon}"></i> ${server.server_type}</span></td>
            <td><code>${server.private_ip}</code></td>
            <td><code>${server.public_ip || 'N/A'}</code></td>
            <td>
                <div><strong>${server.primary_owner}</strong></div>
                ${server.secondary_owner ? `<small class="text-muted">${server.secondary_owner}</small>` : ''}
            </td>
            <td>${server.datacenter}</td>
            <td><span class="badge bg-${getEnvColor(server.environment)}">${server.environment}</span></td>
            <td>
                ${currentUser.role === 'admin' ? 
                    `<button class="btn btn-danger btn-sm" onclick="deleteServer(${server.id}, '${server.hostname}')">
                        <i class="fas fa-trash"></i>
                    </button>` : 
                    '<span class="text-muted">Read-only</span>'
                }
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

function getServerTypeIcon(type) {
    switch(type) {
        case 'physical': return 'fas fa-server';
        case 'virtual': return 'fas fa-cube';
        case 'cloud': return 'fas fa-cloud';
        default: return 'fas fa-question';
    }
}

function getEnvColor(env) {
    switch(env) {
        case 'production': return 'danger';
        case 'staging': return 'warning';
        case 'development': return 'info';
        case 'testing': return 'secondary';
        default: return 'light';
    }
}

function showAddServerModal() {
    const modal = new bootstrap.Modal(document.getElementById('addServerModal'));
    modal.show();
}

async function addServer() {
    const form = document.getElementById('addServerForm');
    const formData = new FormData(form);
    const serverData = {};
    
    for (let [key, value] of formData.entries()) {
        if (value.trim()) {
            serverData[key] = value.trim();
        }
    }
    
    try {
        const response = await fetch('/api/servers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(serverData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('Server added successfully', 'success');
            form.reset();
            bootstrap.Modal.getInstance(document.getElementById('addServerModal')).hide();
            loadServers();
        } else {
            showAlert(data.error, 'danger');
        }
    } catch (error) {
        showAlert('Connection error', 'danger');
    }
}

async function deleteServer(serverId, hostname) {
    if (!confirm(`Are you sure you want to delete server "${hostname}"?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/servers/${serverId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            showAlert('Server deleted successfully', 'success');
            loadServers();
            loadLogs(); // Refresh logs
        } else {
            const data = await response.json();
            showAlert(data.error, 'danger');
        }
    } catch (error) {
        showAlert('Connection error', 'danger');
    }
}

function refreshServers() {
    loadServers();
    showAlert('Servers refreshed', 'info');
}

// Audit logs functions
async function loadLogs() {
    try {
        const response = await fetch('/api/logs', {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const logs = await response.json();
            displayLogs(logs);
        }
    } catch (error) {
        console.error('Error loading logs:', error);
    }
}

function displayLogs(logs) {
    const tbody = document.getElementById('logsTable');
    tbody.innerHTML = '';
    
    logs.forEach(log => {
        const row = document.createElement('tr');
        const timestamp = new Date(log.timestamp).toLocaleString();
        
        row.innerHTML = `
            <td><small>${timestamp}</small></td>
            <td><code>${log.user}</code></td>
            <td><span class="badge bg-${getActionColor(log.action)}">${log.action}</span></td>
            <td><code>${log.resource}</code></td>
            <td><small>${log.ip_address || 'N/A'}</small></td>
        `;
        
        tbody.appendChild(row);
    });
}

function getActionColor(action) {
    if (action.includes('CREATE')) return 'success';
    if (action.includes('DELETE')) return 'danger';
    if (action.includes('LOGIN')) return 'info';
    if (action.includes('FAILED')) return 'warning';
    return 'secondary';
}

// Utility functions
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

function showError(elementId, message) {
    const errorDiv = document.getElementById(elementId);
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
    
    setTimeout(() => {
        errorDiv.classList.add('hidden');
    }, 5000);
}