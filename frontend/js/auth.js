document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const msgDiv = document.getElementById('loginMessage');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            msgDiv.textContent = '';
            
            const username = loginForm.username.value;
            const password = loginForm.password.value;

            try {
                const response = await apiCall('/auth/login', {
                    method: 'POST',
                    body: JSON.stringify({ username, password })
                });

                // Store session
                localStorage.setItem('token', response.token);
                localStorage.setItem('userRole', response.user.role);
                localStorage.setItem('user', JSON.stringify(response.user));

                // Redirect based on role
                switch(response.user.role) {
                    case 'student':
                        window.location.href = 'student-dashboard.html';
                        break;
                    case 'warden':
                        window.location.href = 'warden-dashboard.html';
                        break;
                    case 'admin':
                        window.location.href = 'admin-dashboard.html';
                        break;
                }
            } catch (error) {
                msgDiv.textContent = error.message;
            }
        });
    }
});
