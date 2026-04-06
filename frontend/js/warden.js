document.addEventListener('DOMContentLoaded', () => {
    const auth = checkAuth('warden');
    if (!auth) return;

    const user = JSON.parse(localStorage.getItem('user'));
    document.getElementById('welcomeName').textContent = `Welcome, ${user.profile.name || user.id}`;

    loadRequests('pending');
});

// UI Context Switcher
function switchTab(tabId) {
    document.getElementById('requestsModule').style.display = 'none';
    document.getElementById('resolvedModule').style.display = 'none';
    document.getElementById('studentInfoModule').style.display = 'none';
    
    document.getElementById(tabId).style.display = 'block';

    if(tabId === 'requestsModule') loadRequests('pending');
    if(tabId === 'resolvedModule') loadRequests('resolved');
}


// Requests Processing with dynamic queries capturing either pending or resolved contexts
async function loadRequests(statusContext) {
    try {
        let typeFilter, searchFilter, tbodyId;
        
        if (statusContext === 'pending') {
            typeFilter = document.getElementById('requestFilter').value;
            searchFilter = document.getElementById('requestSearch').value.trim();
            tbodyId = '#requestsTable tbody';
        } else {
            typeFilter = document.getElementById('resolvedFilter').value;
            searchFilter = document.getElementById('resolvedSearch').value.trim();
            tbodyId = '#resolvedTable tbody';
        }

        // Pass filters functionally to backend query
        let queryParams = new URLSearchParams();
        queryParams.append('status', statusContext);
        if (typeFilter !== 'all') queryParams.append('type', typeFilter);
        if (searchFilter) queryParams.append('search', searchFilter);

        const url = `/warden/requests?${queryParams.toString()}`;
        const data = await apiCall(url);
        const tbody = document.querySelector(tbodyId);
        tbody.innerHTML = '';
        
        if (data.requests.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;">No ${statusContext} requests found for this filter context.</td></tr>`;
            return;
        }

        data.requests.forEach(req => {
            const tr = document.createElement('tr');

            let timeStr = '';
            if (req.request_type === 'late_entry') {
                timeStr = `Date: ${req.entry_date}<br>Est IN: ${req.entry_time}`;
            } else if (req.request_type === 'exit') {
                timeStr = `OUT: ${req.exit_time}<br>Must IN by: ${req.reentry_time}`;
            }

            if (statusContext === 'pending') {
                tr.innerHTML = `
                    <td><b>${req.student_name}</b><br><small>Roll: ${req.student_id}</small><br><small>Room: ${req.room_number}</small></td>
                    <td>${req.request_type.replace('_',' ').toUpperCase()}</td>
                    <td><small>${timeStr}</small></td>
                    <td>${req.reason}</td>
                    <td>
                        <button onclick="updateRequest(${req.request_id}, 'approved')" class="btn btn-success" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; display:block; margin-bottom:5px; width:100%;">Approve</button>
                        <button onclick="updateRequest(${req.request_id}, 'rejected')" class="btn btn-danger" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; display:block; width:100%;">Reject</button>
                    </td>
                `;
            } else {
                tr.innerHTML = `
                    <td><b>${req.student_name}</b><br><small>Roll: ${req.student_id}</small><br><small>Room: ${req.room_number}</small></td>
                    <td>${req.request_type.replace('_',' ').toUpperCase()}</td>
                    <td><small>${timeStr}</small></td>
                    <td><span class="badge badge-${req.status}">${req.status.toUpperCase()}</span></td>
                    <td>${new Date(req.created_at).toLocaleDateString()}</td>
                `;
            }

            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Failed to load requests:', error);
    }
}

async function updateRequest(id, status) {
    if (!confirm(`Are you sure you want to strictly ${status.toUpperCase()} this request?`)) return;
    try {
        await apiCall(`/warden/requests/${id}`, {
            method: 'PUT',
            body: JSON.stringify({ status })
        });
        loadRequests('pending'); 
    } catch (error) {
        alert(error.message);
    }
}

// Student View Profile (Read-Only)
async function searchStudentInfo() {
    const studentId = document.getElementById('studentSearchInput').value.trim();
    const errDiv = document.getElementById('studentInfoError');
    const resultDiv = document.getElementById('studentInfoResult');
    
    errDiv.className = 'hidden';
    resultDiv.className = 'hidden';

    if(!studentId) {
        errDiv.className = 'error-msg';
        errDiv.textContent = 'Please enter a Roll No.';
        return;
    }

    try {
        // Safe backend fetch strictly validating against local warden block mapping
        const res = await apiCall(`/warden/students/${studentId}`);
        const s = res.student;

        document.getElementById('di_roll').textContent = s.student_id;
        document.getElementById('di_name').textContent = s.name;
        document.getElementById('di_email').textContent = s.email;
        document.getElementById('di_phone').textContent = s.phone || "Not Set";
        document.getElementById('di_room').textContent = s.room_number;
        document.getElementById('di_block').textContent = s.block_id;

        resultDiv.className = '';
    } catch(err) {
        errDiv.className = 'error-msg';
        errDiv.textContent = err.message;
    }
}
