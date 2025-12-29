const API_BASE_URL = 'http://localhost:5000/api';

function getToken() {
    return localStorage.getItem('access_token');
}

function getUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

function isAuthenticated() {
    return !!getToken();
}

async function authenticatedFetch(url, options = {}) {
    const token = getToken();
    
    const headers = {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers
    };
    
    try {
        const response = await fetch(url, { ...options, headers });
        
        if (response.status === 401) {
            logout();
            window.location.href = '/tools/auth/login.html';
            throw new Error('Unauthorized');
        }
        
        return response;
    } catch (error) {
        throw error;
    }
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/tools/auth/login.html';
}

function requireAuth() {
    if (!isAuthenticated()) {
        const currentPath = window.location.pathname;
        localStorage.setItem('redirect_after_login', currentPath);
        window.location.href = '/tools/auth/login.html';
        return false;
    }
    return true;
}

function updateAuthUI() {
    const authContainer = document.getElementById('authContainer');
    if (!authContainer) return;
    
    if (isAuthenticated()) {
        const user = getUser();
        authContainer.innerHTML = `
            <span>欢迎, ${user?.username || 'User'}</span>
            <button onclick="logout()" style="margin-left: 12px; padding: 6px 12px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">
                登出 Logout
            </button>
        `;
    } else {
        authContainer.innerHTML = `
            <a href="/tools/auth/login.html" style="margin-right: 12px; color: #667eea; text-decoration: none;">登录 Login</a>
            <a href="/tools/auth/register.html" style="padding: 6px 12px; background: #667eea; color: white; border-radius: 6px; text-decoration: none;">注册 Register</a>
        `;
    }
}

if (typeof window !== 'undefined') {
    window.getToken = getToken;
    window.getUser = getUser;
    window.isAuthenticated = isAuthenticated;
    window.authenticatedFetch = authenticatedFetch;
    window.logout = logout;
    window.requireAuth = requireAuth;
    window.updateAuthUI = updateAuthUI;
    window.API_BASE_URL = API_BASE_URL;
}
