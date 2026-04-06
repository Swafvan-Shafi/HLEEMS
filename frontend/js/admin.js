let allBlocks = [];

document.addEventListener('DOMContentLoaded', () => {
    const auth = checkAuth('admin');
    if (!auth) return;

    loadBlocks();
    loadUsers();

    // Dropdown toggler
    const selector = document.getElementById('creationSelector');
    selector.addEventListener('change', (e) => {
        const val = e.target.value;
        document.getElementById('createStudentForm').style.display = (val === 'student') ? 'block' : 'none';
        document.getElementById('createWardenForm').style.display = (val === 'warden') ? 'block' : 'none';
        document.getElementById('createAdminForm').style.display = (val === 'admin') ? 'block' : 'none';
        
        // Clear messages
        document.getElementById('studentMessage').textContent = '';
        document.getElementById('wardenMessage').textContent = '';
        document.getElementById('adminMessage').textContent = '';
    });

    // Form Event Listeners
    setupStudentForm();
    setupWardenForm();
    setupAdminForm();
    setupEditForm();
});

async function loadBlocks() {
    try {
        const data = await apiCall('/admin/blocks');
        allBlocks = data.blocks;
        const s_select = document.getElementById('s_block_id');
        const w_select = document.getElementById('w_block_id');
        
        let options = '';
        data.blocks.forEach(b => {
            options += `<option value="${b.block_id}">${b.block_name}</option>`;
        });
        
        s_select.innerHTML = options;
        w_select.innerHTML = options;
    } catch(err) {
        console.error('Failed to load blocks:', err);
    }
}

async function loadUsers() {
    try {
        const data = await apiCall('/admin/users');
        const tbody = document.querySelector('#usersTable tbody');
        tbody.innerHTML = '';
        
        data.users.forEach(u => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><a href="#" onclick="openProfile('${u.id}')" style="color: var(--primary-light); text-decoration: underline; font-weight: bold;">${u.id}</a></td>
                <td>${u.name}</td>
                <td>${u.email}</td>
                <td><span class="badge badge-normal">${u.role.toUpperCase()}</span></td>
                <td>${new Date(u.created_at).toLocaleDateString()}</td>
                <td>
                    <button onclick="deleteUser('${u.id}')" class="btn btn-danger" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">Delete</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Failed to load users:', error);
    }
}

// Open and View Profile Logic
async function openProfile(userId) {
    try {
        const data = await apiCall(`/admin/users/${userId}`);
        const user = data.user;
        
        document.getElementById('edit_user_id').value = user.id;
        document.getElementById('edit_user_role').value = user.role;
        document.getElementById('modalTitle').textContent = `Editing Profile: ${user.id} (${user.role.toUpperCase()})`;
        
        const editFields = document.getElementById('editFields');
        editFields.innerHTML = ''; // Clear old

        if (user.role === 'student' || user.role === 'warden') {
            editFields.innerHTML += `<div class="form-group"><label>Name</label><input type="text" id="e_name" value="${user.name || ''}" required></div>`;
            editFields.innerHTML += `<div class="form-group"><label>Email</label><input type="email" id="e_email" value="${user.email || ''}" required></div>`;
            editFields.innerHTML += `<div class="form-group"><label>Phone</label><input type="text" id="e_phone" value="${user.phone || ''}"></div>`;
            
            if (user.role === 'student') {
                editFields.innerHTML += `<div class="form-group"><label>Room Number</label><input type="text" id="e_room_number" value="${user.room_number || ''}" required></div>`;
            }

            let blockOptions = '';
            allBlocks.forEach(b => {
                const selected = (b.block_id === user.block_id) ? 'selected' : '';
                blockOptions += `<option value="${b.block_id}" ${selected}>${b.block_name}</option>`;
            });
            editFields.innerHTML += `<div class="form-group"><label>Assigned Block</label><select id="e_block_id" required>${blockOptions}</select></div>`;
        } else {
             editFields.innerHTML = `<p>Admin accounts do not have extra profile fields.</p>`;
        }
        
        document.getElementById('editMessage').className = '';
        document.getElementById('editMessage').textContent = '';
        document.getElementById('profileModal').style.display = 'flex';
    } catch (error) {
        alert("Failed to load profile details: " + error.message);
    }
}

function closeProfileModal() {
    document.getElementById('profileModal').style.display = 'none';
}

function setupEditForm() {
    const ef = document.getElementById('editProfileForm');
    if (!ef) return;
    ef.addEventListener('submit', async (e) => {
        e.preventDefault();
        const msgDiv = document.getElementById('editMessage');
        msgDiv.className = '';
        msgDiv.textContent = '';
        
        const userId = document.getElementById('edit_user_id').value;
        const role = document.getElementById('edit_user_role').value;
        
        let payload = {};
        if (role === 'student' || role === 'warden') {
            payload = {
                name: document.getElementById('e_name').value,
                email: document.getElementById('e_email').value,
                phone: document.getElementById('e_phone').value,
                block_id: document.getElementById('e_block_id').value
            };
            if (role === 'student') {
                payload.room_number = document.getElementById('e_room_number').value;
            }
        } else {
            msgDiv.className = 'error-msg';
            msgDiv.textContent = "Admin profiles cannot be edited.";
            return;
        }

        try {
            await apiCall(`/admin/users/${userId}`, {
                method: 'PUT',
                body: JSON.stringify(payload)
            });
            msgDiv.className = 'success-msg';
            msgDiv.textContent = 'Profile updated successfully!';
            loadUsers();
            setTimeout(closeProfileModal, 1500);
        } catch (error) {
            msgDiv.className = 'error-msg';
            msgDiv.textContent = error.message;
        }
    });
}

function setupStudentForm() {
    const form = document.getElementById('createStudentForm');
    if(form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                user_id: document.getElementById('s_student_id').value,
                name: document.getElementById('s_name').value,
                email: document.getElementById('s_email').value,
                password: document.getElementById('s_password').value,
                phone: document.getElementById('s_phone').value,
                room_number: document.getElementById('s_room_number').value,
                block_id: document.getElementById('s_block_id').value
            };
            await submitForm('/admin/users/student', payload, 'studentMessage', form);
        });
    }
}

function setupWardenForm() {
    const form = document.getElementById('createWardenForm');
    if(form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                user_id: document.getElementById('w_warden_id').value,
                name: document.getElementById('w_name').value,
                email: document.getElementById('w_email').value,
                password: document.getElementById('w_password').value,
                phone: document.getElementById('w_phone').value,
                block_id: document.getElementById('w_block_id').value
            };
            await submitForm('/admin/users/warden', payload, 'wardenMessage', form);
        });
    }
}

function setupAdminForm() {
    const form = document.getElementById('createAdminForm');
    if(form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                user_id: document.getElementById('a_admin_id').value,
                password: document.getElementById('a_password').value
            };
            await submitForm('/admin/users/admin', payload, 'adminMessage', form);
        });
    }
}

async function submitForm(url, payload, msgDivId, formObj) {
    const msgDiv = document.getElementById(msgDivId);
    msgDiv.className = '';
    msgDiv.textContent = '';
    try {
        await apiCall(url, {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        msgDiv.className = 'success-msg';
        msgDiv.textContent = 'Account created successfully!';
        formObj.reset();
        document.getElementById('creationSelector').value = "";
        formObj.style.display = "none";
        loadUsers();
    } catch (error) {
        msgDiv.className = 'error-msg';
        msgDiv.textContent = error.message;
    }
}

async function deleteUser(id) {
    if (!confirm(`Are you sure you want to delete user ${id}? Action cannot be undone.`)) return;
    try {
        await apiCall(`/admin/users/${id}`, { method: 'DELETE' });
        loadUsers();
    } catch (error) {
        alert(error.message);
    }
}
