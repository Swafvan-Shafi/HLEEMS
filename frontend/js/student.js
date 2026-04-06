document.addEventListener('DOMContentLoaded', () => {
    const auth = checkAuth('student');
    if (!auth) return;

    const user = JSON.parse(localStorage.getItem('user'));
    document.getElementById('welcomeName').textContent = `Welcome, ${user.profile.name || user.id}`;

    const requestForm = document.getElementById('requestForm');
    const pwForm = document.getElementById('passwordForm');
    const msgDiv = document.getElementById('reqMessage');
    const pwMsg = document.getElementById('pwMessage');
    const reqTypeSelect = document.getElementById('reqType');
    const lateEntryGroup = document.getElementById('lateEntryGroup');
    const exitGroup = document.getElementById('exitGroup');

    // UI Toggle
    reqTypeSelect.addEventListener('change', (e) => {
        const val = e.target.value;
        if (val === 'late_entry') {
            lateEntryGroup.style.display = 'block';
            exitGroup.style.display = 'none';
            document.getElementById('entryDate').required = true;
            document.getElementById('entryTime').required = true;
            document.getElementById('exitTime').required = false;
            document.getElementById('reentryTime').required = false;
        } else if (val === 'exit') {
            lateEntryGroup.style.display = 'none';
            exitGroup.style.display = 'block';
            document.getElementById('entryDate').required = false;
            document.getElementById('entryTime').required = false;
            document.getElementById('exitTime').required = true;
            document.getElementById('reentryTime').required = true;
        }
    });

    checkAdministrativeFlags();
    loadRequests();

    if (requestForm) {
        requestForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            msgDiv.className = '';
            msgDiv.textContent = '';
            
            const req_type = reqTypeSelect.value;
            const payload = {
                request_type: req_type,
                reason: document.getElementById('reason').value,
            };

            if (req_type === 'late_entry') {
                payload.entry_date = document.getElementById('entryDate').value;
                payload.entry_time = document.getElementById('entryTime').value;
            } else {
                payload.exit_time = document.getElementById('exitTime').value;
                payload.reentry_time = document.getElementById('reentryTime').value;
            }

            try {
                await apiCall('/student/requests', {
                    method: 'POST',
                    body: JSON.stringify(payload)
                });
                msgDiv.className = 'success-msg';
                msgDiv.textContent = 'Request submitted successfully!';
                requestForm.reset();
                reqTypeSelect.dispatchEvent(new Event('change')); // reset toggles
                loadRequests(); 
            } catch (error) {
                msgDiv.className = 'error-msg';
                msgDiv.textContent = error.message;
            }
        });
    }

    if (pwForm) {
        pwForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            pwMsg.className = '';
            pwMsg.textContent = '';

            const payload = {
                current_password: document.getElementById('curPass').value,
                new_password: document.getElementById('newPass').value,
                confirm_password: document.getElementById('confPass').value,
            };

            try {
                await apiCall('/student/password', {
                    method: 'PUT',
                    body: JSON.stringify(payload)
                });
                pwMsg.className = 'success-msg';
                pwMsg.textContent = 'Password strictly updated!';
                pwForm.reset();
            } catch (error) {
                pwMsg.className = 'error-msg';
                pwMsg.textContent = error.message;
            }
        });
    }
});

async function checkAdministrativeFlags() {
    try {
        const data = await apiCall('/student/profile');
        if (data.profile.late_warning_sent && !sessionStorage.getItem('warning_dismissed')) {
            document.getElementById('lateWarningModal').style.display = 'flex';
        }
    } catch(err) {
        console.error("Administrative check failed", err);
    }
}

function dismissWarningModal() {
    document.getElementById('lateWarningModal').style.display = 'none';
    sessionStorage.setItem('warning_dismissed', 'true');
}

function togglePasswordForm() {
    const pw = document.getElementById('passwordWrapper');
    if (pw.style.display === 'none') {
        pw.style.display = 'block';
    } else {
        pw.style.display = 'none';
        document.getElementById('pwMessage').textContent = '';
    }
}

async function loadRequests() {
    try {
        const data = await apiCall('/student/requests');
        const tbody = document.querySelector('#requestsTable tbody');
        tbody.innerHTML = '';
        
        data.requests.forEach(req => {
            const tr = document.createElement('tr');
            
            let timeStr = '';
            if (req.request_type === 'late_entry') timeStr = `Date: ${req.entry_date} - Est Time: ${req.entry_time}`;
            if (req.request_type === 'exit') timeStr = `Out: ${req.exit_time} - In: ${req.reentry_time}`;

            tr.innerHTML = `
                <td>${req.request_type.replace('_', ' ').toUpperCase()}</td>
                <td><small>${timeStr}</small></td>
                <td>${req.reason}</td>
                <td><span class="badge badge-${req.status}">${req.status.toUpperCase()}</span></td>
                <td>${new Date(req.created_at).toLocaleDateString()}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Failed to load requests:', error);
    }
}
