// API Base URL
const API_BASE = window.location.origin;

// State
let jobs = [];
let editingId = null;
let currentUser = null;
let authToken = localStorage.getItem('authToken') || null;
let currentTab = 'all';
let sortField = 'apply_date';
let sortOrder = 'desc';

// DOM Elements
const authContainer = document.getElementById('auth-container');
const appContainer = document.getElementById('app-container');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const tableBody = document.getElementById('job-table-body');
const searchInput = document.getElementById('search-input');
const filterStatus = document.getElementById('filter-status');
const filterSource = document.getElementById('filter-source');
const addBtn = document.getElementById('add-btn');
const modal = document.getElementById('modal');
const modalClose = document.getElementById('modal-close');
const modalTitle = document.getElementById('modal-title');
const jobForm = document.getElementById('job-form');
const formCancel = document.getElementById('form-cancel');
const logoutBtn = document.getElementById('logout-btn');
const userInfo = document.getElementById('user-info');
const changePasswordBtn = document.getElementById('change-password-btn');
const passwordModal = document.getElementById('password-modal');
const passwordModalClose = document.getElementById('password-modal-close');
const passwordForm = document.getElementById('password-form');
const passwordCancel = document.getElementById('password-cancel');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (authToken) {
        validateToken();
    } else {
        showAuth();
    }
    setupEventListeners();
});

// ==================== Auth Functions ====================

async function validateToken() {
    try {
        const response = await fetch(`${API_BASE}/api/auth/me`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            showApp();
            loadJobs();
            loadStats();
        } else {
            logout();
        }
    } catch (error) {
        console.error('验证失败:', error);
        showAuth();
    }
}

async function login(username, password) {
    try {
        const response = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            authToken = data.token;
            currentUser = data.user;
            localStorage.setItem('authToken', authToken);
            showApp();
            loadJobs();
            loadStats();
        } else {
            document.getElementById('login-error').textContent = data.error || '登录失败';
        }
    } catch (error) {
        document.getElementById('login-error').textContent = '网络错误，请重试';
    }
}

async function register(username, password) {
    try {
        const response = await fetch(`${API_BASE}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            await login(username, password);
        } else {
            document.getElementById('register-error').textContent = data.error || '注册失败';
        }
    } catch (error) {
        document.getElementById('register-error').textContent = '网络错误，请重试';
    }
}

async function logout() {
    try {
        await fetch(`${API_BASE}/api/auth/logout`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
    } catch (e) {}

    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    showAuth();
}

async function changePassword(oldPassword, newPassword) {
    try {
        const response = await fetch(`${API_BASE}/api/auth/change-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ old_password: oldPassword, new_password: newPassword })
        });

        const data = await response.json();

        if (response.ok) {
            alert('密码修改成功，请重新登录');
            authToken = null;
            currentUser = null;
            localStorage.removeItem('authToken');
            showAuth();
        } else {
            document.getElementById('password-error').textContent = data.error || '修改失败';
        }
    } catch (error) {
        document.getElementById('password-error').textContent = '网络错误，请重试';
    }
}

function showAuth() {
    authContainer.classList.remove('hidden');
    appContainer.classList.add('hidden');
}

function showApp() {
    authContainer.classList.add('hidden');
    appContainer.classList.remove('hidden');
    userInfo.textContent = `👤 ${currentUser.username}`;
}

// ==================== Event Listeners ====================

function setupEventListeners() {
    // Auth forms
    document.getElementById('show-register').addEventListener('click', (e) => {
        e.preventDefault();
        loginForm.classList.add('hidden');
        registerForm.classList.remove('hidden');
        document.getElementById('login-error').textContent = '';
    });

    document.getElementById('show-login').addEventListener('click', (e) => {
        e.preventDefault();
        registerForm.classList.add('hidden');
        loginForm.classList.remove('hidden');
        document.getElementById('register-error').textContent = '';
    });

    document.getElementById('login-btn').addEventListener('click', () => {
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value;
        if (!username || !password) {
            document.getElementById('login-error').textContent = '请输入用户名和密码';
            return;
        }
        login(username, password);
    });

    document.getElementById('register-btn').addEventListener('click', () => {
        const username = document.getElementById('register-username').value.trim();
        const password = document.getElementById('register-password').value;
        const password2 = document.getElementById('register-password2').value;

        if (!username || !password) {
            document.getElementById('register-error').textContent = '请填写完整信息';
            return;
        }
        if (password !== password2) {
            document.getElementById('register-error').textContent = '两次密码不一致';
            return;
        }
        register(username, password);
    });

    document.getElementById('login-password').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') document.getElementById('login-btn').click();
    });

    // Logout
    logoutBtn.addEventListener('click', logout);

    // Change password
    changePasswordBtn.addEventListener('click', () => {
        passwordModal.classList.add('active');
        document.getElementById('password-error').textContent = '';
    });
    passwordModalClose.addEventListener('click', () => passwordModal.classList.remove('active'));
    passwordCancel.addEventListener('click', () => passwordModal.classList.remove('active'));
    passwordForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const oldPwd = document.getElementById('old-password').value;
        const newPwd = document.getElementById('new-password').value;
        const newPwd2 = document.getElementById('new-password2').value;
        if (newPwd !== newPwd2) {
            document.getElementById('password-error').textContent = '两次密码不一致';
            return;
        }
        changePassword(oldPwd, newPwd);
    });

    // Main app
    addBtn.addEventListener('click', () => openModal());
    modalClose.addEventListener('click', closeModal);
    formCancel.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    searchInput.addEventListener('input', debounce(renderTable, 300));
    filterStatus.addEventListener('change', renderTable);
    filterSource.addEventListener('change', renderTable);

    jobForm.addEventListener('submit', handleSubmit);

    // Tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentTab = tab.dataset.tab;
            renderTable();
        });
    });

    // Sortable columns
    document.querySelectorAll('.sortable').forEach(th => {
        th.addEventListener('click', () => {
            const field = th.dataset.field;
            if (sortField === field) {
                sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                sortField = field;
                sortOrder = 'desc';
            }
            updateSortIndicators();
            renderTable();
        });
    });
}

// ==================== API Functions ====================

async function loadJobs() {
    try {
        const response = await fetch(`${API_BASE}/api/jobs`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (response.ok) {
            jobs = await response.json();
            renderTable();
        } else if (response.status === 401) {
            logout();
        }
    } catch (error) {
        console.error('加载数据失败:', error);
        tableBody.innerHTML = '<tr><td colspan="10" class="empty-state"><div class="icon">⚠️</div><p>加载失败，请检查网络连接</p></td></tr>';
    }
}

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (response.ok) {
            const stats = await response.json();

            document.getElementById('stat-total').textContent = stats.total;
            document.getElementById('stat-pending').textContent = stats.pending;
            document.getElementById('stat-rejected').textContent = stats.rejected;
            document.getElementById('stat-interview').textContent = stats.interview;
            document.getElementById('stat-written').textContent = stats.written;
            document.getElementById('stat-offer').textContent = stats.offer;

            // Category stats
            const categories = ['国企', '外企', '私企', '招聘平台'];
            categories.forEach(cat => {
                const catData = stats.categories[cat] || { count: 0, reject: 0 };
                const countEl = document.getElementById(`cat-${cat}-count`);
                const rejectEl = document.getElementById(`cat-${cat}-reject`);
                if (countEl) countEl.textContent = catData.count;
                if (rejectEl) rejectEl.textContent = catData.reject;

                // Tab counts
                const tabCountEl = document.getElementById(`tab-count-${cat}`);
                if (tabCountEl) tabCountEl.textContent = catData.count;
            });

            // All count
            document.getElementById('tab-count-all').textContent = stats.total;
        }
    } catch (error) {
        console.error('加载统计失败:', error);
    }
}

async function createJob(data) {
    try {
        const response = await fetch(`${API_BASE}/api/jobs`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(data)
        });
        if (response.ok) {
            loadJobs();
            loadStats();
            closeModal();
        }
    } catch (error) {
        console.error('创建失败:', error);
        alert('创建失败，请重试');
    }
}

async function updateJob(id, data) {
    try {
        const response = await fetch(`${API_BASE}/api/jobs/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(data)
        });
        if (response.ok) {
            loadJobs();
            loadStats();
            closeModal();
        }
    } catch (error) {
        console.error('更新失败:', error);
        alert('更新失败，请重试');
    }
}

async function deleteJob(id) {
    if (!confirm('确定要删除这条记录吗？')) return;

    try {
        const response = await fetch(`${API_BASE}/api/jobs/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (response.ok) {
            loadJobs();
            loadStats();
        }
    } catch (error) {
        console.error('删除失败:', error);
        alert('删除失败，请重试');
    }
}

// ==================== Render Functions ====================

function renderTable() {
    const search = searchInput.value.toLowerCase();
    const status = filterStatus.value;
    const source = filterSource.value;

    let filtered = jobs.filter(job => {
        // Tab filter
        if (currentTab !== 'all' && job.category !== currentTab) return false;
        // Search
        if (search && !job.company.toLowerCase().includes(search) && !job.position.toLowerCase().includes(search)) {
            return false;
        }
        if (status !== 'all' && job.status !== status) return false;
        if (source !== 'all' && job.source !== source) return false;
        return true;
    });

    // Sort
    filtered.sort((a, b) => {
        let valA, valB;
        if (sortField === 'apply_date') {
            valA = a.apply_date || '0000-00-00';
            valB = b.apply_date || '0000-00-00';
        } else if (sortField === 'status') {
            valA = a.status || '';
            valB = b.status || '';
        } else {
            valA = a[sortField] || '';
            valB = b[sortField] || '';
        }

        if (valA < valB) return sortOrder === 'asc' ? -1 : 1;
        if (valA > valB) return sortOrder === 'asc' ? 1 : -1;
        return 0;
    });

    if (filtered.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="10" class="empty-state"><div class="icon">📭</div><p>暂无数据</p></td></tr>';
        return;
    }

    tableBody.innerHTML = filtered.map((job, index) => `
        <tr>
            <td>${index + 1}</td>
            <td><strong>${escapeHtml(job.company)}</strong></td>
            <td>${escapeHtml(job.position)}</td>
            <td><span class="category-badge category-${job.category}">${getCategoryLabel(job.category)}</span></td>
            <td>${job.apply_date || '-'}</td>
            <td>${job.source}</td>
            <td><span class="status-badge status-${job.status}">${job.status}</span></td>
            <td>${job.exam_date || '-'}</td>
            <td>${job.notes ? escapeHtml(job.notes) : '-'}</td>
            <td>
                <div class="action-btns">
                    ${job.link ? `<a href="${escapeHtml(job.link)}" target="_blank" class="btn btn-sm btn-secondary">链接</a>` : ''}
                    <button class="btn btn-sm btn-secondary" onclick="editJob(${job.id})">编辑</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteJob(${job.id})">删除</button>
                </div>
            </td>
        </tr>
    `).join('');
}

function getCategoryLabel(category) {
    const labels = {
        '国企': '央国企',
        '外企': '外企',
        '私企': '私企',
        '招聘平台': '招聘平台'
    };
    return labels[category] || category;
}

function updateSortIndicators() {
    document.querySelectorAll('.sortable').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
        if (th.dataset.field === sortField) {
            th.classList.add(sortOrder === 'asc' ? 'sort-asc' : 'sort-desc');
        }
    });
}

// ==================== Tab Switching ====================

function switchTab(tab) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    const tabBtn = document.querySelector(`.tab[data-tab="${tab}"]`);
    if (tabBtn) tabBtn.classList.add('active');
    currentTab = tab;
    renderTable();
}

// ==================== Modal Functions ====================

function openModal(job = null) {
    modal.classList.add('active');
    jobForm.reset();

    if (job) {
        editingId = job.id;
        modalTitle.textContent = '编辑投递';
        document.getElementById('form-id').value = job.id;
        document.getElementById('form-company').value = job.company;
        document.getElementById('form-position').value = job.position;
        document.getElementById('form-category').value = job.category;
        document.getElementById('form-source').value = job.source;
        document.getElementById('form-date').value = job.apply_date || '';
        document.getElementById('form-status').value = job.status;
        document.getElementById('form-exam-date').value = job.exam_date || '';
        document.getElementById('form-link').value = job.link || '';
        document.getElementById('form-notes').value = job.notes || '';
    } else {
        editingId = null;
        modalTitle.textContent = '新增投递';
        document.getElementById('form-id').value = '';
        // Pre-fill category based on current tab
        if (currentTab !== 'all') {
            document.getElementById('form-category').value = currentTab;
        }
    }
}

function closeModal() {
    modal.classList.remove('active');
    editingId = null;
    jobForm.reset();
}

function editJob(id) {
    const job = jobs.find(j => j.id === id);
    if (job) openModal(job);
}

// ==================== Form Handler ====================

function handleSubmit(e) {
    e.preventDefault();

    const data = {
        company: document.getElementById('form-company').value,
        position: document.getElementById('form-position').value,
        category: document.getElementById('form-category').value,
        source: document.getElementById('form-source').value,
        apply_date: document.getElementById('form-date').value || null,
        status: document.getElementById('form-status').value,
        exam_date: document.getElementById('form-exam-date').value || null,
        link: document.getElementById('form-link').value,
        notes: document.getElementById('form-notes').value,
    };

    if (editingId) {
        updateJob(editingId, data);
    } else {
        createJob(data);
    }
}

// ==================== Utility Functions ====================

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}
