// Base API Configuration
const API_BASE = 'http://localhost:5000/api';

// Utility to handle fetch requests with auth token
async function apiCall(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    
    const defaultHeaders = {
        'Content-Type': 'application/json',
    };

    if (token) {
        defaultHeaders['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
    };

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'API Request Failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Auth check utility
function checkAuth(requiredRole = null) {
    const token = localStorage.getItem('token');
    const userRole = localStorage.getItem('userRole');

    if (!token) {
        window.location.href = 'index.html';
        return null;
    }

    if (requiredRole && userRole !== requiredRole) {
        alert('Access denied. Insufficient permissions.');
        logout();
    }

    return { token, userRole };
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    localStorage.removeItem('user');
    window.location.href = 'index.html';
}
