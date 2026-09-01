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

// Chart instances
let categoryChart = null;
let dailyChart = null;
let statusChart = null;
let weeklyChart = null;

// DOM Elements
const authContainer = document.getElementById('auth-container');
const appContainer = document.getElementById('app-container');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const mainTable = document.getElementById('main-table');
const platformTable = document.getElementById('platform-table');
const tableBody = document.getElementById('job-table-body');
const platformTableBody = document.getElementById('platform-table-body');
const searchInput = document.getElementById('search-input');
const filterStatus = document.getElementById('filter-status');
const filterSource = document.getElementById('filter-source');
const addBtn = document.getElementById('add-btn');
const modal = document.getElementById('modal');
const modalClose = document.getElementById('modal-close');
const modalTitle = document.getElementById('modal-title');
const jobForm = document.getElementById('job-form');
const formCancel = document.getElementById('form-cancel');
const platformModal = document.getElementById('platform-modal');
const platformModalClose = document.getElementById('platform-modal-close');
const platformForm = document.getElementById('platform-form');
const platformFormCancel = document.getElementById('platform-form-cancel');
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
        passwordForm.reset();
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
    addBtn.addEventListener('click', () => {
        if (currentTab === '招聘平台') {
            openPlatformModal();
        } else if (currentTab === 'visualization') {
            // 可视化页签不操作
        } else {
            openModal();
        }
    });
    modalClose.addEventListener('click', closeModal);
    formCancel.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    platformModalClose.addEventListener('click', closePlatformModal);
    platformFormCancel.addEventListener('click', closePlatformModal);
    platformModal.addEventListener('click', (e) => {
        if (e.target === platformModal) closePlatformModal();
    });

    searchInput.addEventListener('input', debounce(renderTable, 300));
    filterStatus.addEventListener('change', renderTable);
    filterSource.addEventListener('change', renderTable);

    jobForm.addEventListener('submit', handleSubmit);
    platformForm.addEventListener('submit', handlePlatformSubmit);

    // Tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentTab = tab.dataset.tab;
            updateTableView();
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
        const emptyRow = '<tr><td colspan="10" class="empty-state"><div class="icon">⚠️</div><p>加载失败，请检查网络连接</p></td></tr>';
        tableBody.innerHTML = emptyRow;
        platformTableBody.innerHTML = emptyRow;
    }
}

async function loadStats(category) {
    try {
        // 根据当前页签决定筛选
        let categoryParam = 'all';
        if (['国企', '外企', '私企', '招聘平台'].includes(currentTab)) {
            categoryParam = currentTab;
        }

        const url = `${API_BASE}/api/stats?category=${categoryParam}`;
        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (response.ok) {
            const stats = await response.json();

            // Main stats
            document.getElementById('stat-total').textContent = stats.total;
            document.getElementById('stat-pending').textContent = stats.pending;
            document.getElementById('stat-rejected').textContent = stats.rejected;
            document.getElementById('stat-interview').textContent = stats.interview;
            document.getElementById('stat-written').textContent = stats.written;
            document.getElementById('stat-offer').textContent = stats.offer;

            // Over 1 month and no reply
            document.getElementById('stat-over-1month').textContent = stats.over_1month;
            document.getElementById('stat-no-reply').textContent = stats.no_reply;

            // Category stats (始终显示全部数据)
            const categories = ['国企', '外企', '私企', '招聘平台'];
            categories.forEach(cat => {
                const catData = stats.categories[cat] || { count: 0, reject: 0 };
                const countEl = document.getElementById(`cat-${cat}-count`);
                const rejectEl = document.getElementById(`cat-${cat}-reject`);
                if (countEl) countEl.textContent = catData.count;
                if (rejectEl) rejectEl.textContent = catData.reject;

                // Tab counts
                const tabCountEl = document.getElementById(`tab-count-${cat}`);
                if (tabCountEl) {
                    if (cat === '招聘平台') {
                        tabCountEl.textContent = catData.positions || 0;
                    } else {
                        tabCountEl.textContent = catData.count;
                    }
                }

                // Platform positions display
                if (cat === '招聘平台') {
                    const posEl = document.getElementById(`cat-${cat}-positions`);
                    if (posEl) posEl.textContent = catData.positions || 0;
                }
            });

            // All count = total
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

function updateTableView() {
    const visualizationSection = document.getElementById('visualization-section');
    const categorySummary = document.querySelector('.category-summary');

    if (currentTab === 'visualization') {
        // 显示可视化，隐藏表格
        mainTable.classList.add('hidden');
        platformTable.classList.add('hidden');
        visualizationSection.classList.remove('hidden');
        filterStatus.parentElement.classList.add('hidden');
        filterSource.parentElement.classList.add('hidden');
        addBtn.classList.add('hidden');
        if (categorySummary) categorySummary.classList.add('hidden');
        // 初始化图表
        setTimeout(initVisualization, 100);
    } else if (currentTab === '招聘平台') {
        mainTable.classList.add('hidden');
        platformTable.classList.remove('hidden');
        visualizationSection.classList.add('hidden');
        filterStatus.parentElement.classList.add('hidden');
        filterSource.parentElement.classList.remove('hidden');
        addBtn.classList.remove('hidden');
        if (categorySummary) categorySummary.classList.remove('hidden');
    } else {
        mainTable.classList.remove('hidden');
        platformTable.classList.add('hidden');
        visualizationSection.classList.add('hidden');
        filterStatus.parentElement.classList.remove('hidden');
        filterSource.parentElement.classList.remove('hidden');
        addBtn.classList.remove('hidden');
        if (categorySummary) categorySummary.classList.remove('hidden');
    }
}

function renderTable() {
    if (currentTab === '招聘平台') {
        renderPlatformTable();
    } else {
        renderMainTable();
    }
}

function renderMainTable() {
    const search = searchInput.value.toLowerCase();
    const status = filterStatus.value;
    const source = filterSource.value;

    let filtered = jobs.filter(job => {
        if (currentTab !== 'all' && job.category !== currentTab) return false;
        if (search && !job.company.toLowerCase().includes(search) && !job.position.toLowerCase().includes(search)) return false;
        if (status !== 'all' && job.status !== status) return false;
        if (source !== 'all' && job.source !== source) return false;
        return true;
    });

    // Sort
    filtered.sort((a, b) => {
        let valA = a[sortField] || '';
        let valB = b[sortField] || '';
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
            <td title="${escapeHtml(job.company)}"><strong>${escapeHtml(job.company)}</strong></td>
            <td title="${escapeHtml(job.position)}">${escapeHtml(job.position)}</td>
            <td><span class="category-badge category-${job.category}">${getCategoryLabel(job.category)}</span></td>
            <td>${job.apply_date || '-'}</td>
            <td>${job.source}</td>
            <td><span class="status-badge status-${job.status}">${job.status}</span></td>
            <td>${job.exam_date || '-'}</td>
            <td class="notes-cell" title="${escapeHtml(job.notes || '')}">${job.notes ? escapeHtml(job.notes) : '-'}</td>
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

function renderPlatformTable() {
    const search = searchInput.value.toLowerCase();

    let filtered = jobs.filter(job => {
        if (job.category !== '招聘平台') return false;
        if (search && !job.company.toLowerCase().includes(search) && !job.position.toLowerCase().includes(search)) return false;
        return true;
    });

    // Sort
    filtered.sort((a, b) => {
        let valA = a[sortField] || '';
        let valB = b[sortField] || '';
        if (valA < valB) return sortOrder === 'asc' ? -1 : 1;
        if (valA > valB) return sortOrder === 'asc' ? 1 : -1;
        return 0;
    });

    if (filtered.length === 0) {
        platformTableBody.innerHTML = '<tr><td colspan="10" class="empty-state"><div class="icon">📭</div><p>暂无数据</p></td></tr>';
        return;
    }

    platformTableBody.innerHTML = filtered.map((job, index) => `
        <tr>
            <td>${index + 1}</td>
            <td title="${escapeHtml(job.company)}"><strong>${escapeHtml(job.company)}</strong></td>
            <td title="${escapeHtml(job.position || '')}">${escapeHtml(job.position || '-')}</td>
            <td>${job.updated_at ? job.updated_at.substring(0, 10) : '-'}</td>
            <td>${job.apply_date || '-'}</td>
            <td>${job.pass_screening || 0}</td>
            <td>${job.in_exam || 0}</td>
            <td>${job.in_interview || 0}</td>
            <td class="notes-cell" title="${escapeHtml(job.notes || '')}">${job.notes ? escapeHtml(job.notes) : '-'}</td>
            <td>
                <div class="action-btns">
                    ${job.link ? `<a href="${escapeHtml(job.link)}" target="_blank" class="btn btn-sm btn-secondary">链接</a>` : ''}
                    <button class="btn btn-sm btn-secondary" onclick="editPlatformJob(${job.id})">更新</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteJob(${job.id})">删除</button>
                </div>
            </td>
        </tr>
    `).join('');
}

function getCategoryLabel(category) {
    const labels = { '国企': '央国企', '外企': '外企', '私企': '私企', '招聘平台': '招聘平台' };
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
    updateTableView();
    renderTable();
    // 切换页签时重新加载统计数据
    loadStats();
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
        if (currentTab !== 'all' && currentTab !== '招聘平台') {
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

function openPlatformModal(job = null) {
    platformModal.classList.add('active');
    platformForm.reset();

    if (job) {
        editingId = job.id;
        document.getElementById('platform-modal-title').textContent = '更新平台记录';
        document.getElementById('platform-form-id').value = job.id;
        document.getElementById('platform-form-company').value = job.company;
        document.getElementById('platform-form-position').value = job.position || '';
        document.getElementById('platform-form-date').value = job.apply_date || '';
        document.getElementById('platform-form-pass-screening').value = job.pass_screening || 0;
        document.getElementById('platform-form-in-exam').value = job.in_exam || 0;
        document.getElementById('platform-form-in-interview').value = job.in_interview || 0;
        document.getElementById('platform-form-link').value = job.link || '';
        document.getElementById('platform-form-notes').value = job.notes || '';
    } else {
        editingId = null;
        document.getElementById('platform-modal-title').textContent = '新增平台记录';
        document.getElementById('platform-form-id').value = '';
    }
}

function closePlatformModal() {
    platformModal.classList.remove('active');
    editingId = null;
    platformForm.reset();
}

function editPlatformJob(id) {
    const job = jobs.find(j => j.id === id);
    if (job) openPlatformModal(job);
}

// ==================== Form Handlers ====================

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

function handlePlatformSubmit(e) {
    e.preventDefault();
    const data = {
        company: document.getElementById('platform-form-company').value,
        position: document.getElementById('platform-form-position').value,
        category: '招聘平台',
        source: '官网',
        apply_date: document.getElementById('platform-form-date').value || null,
        status: '流程中',
        pass_screening: parseInt(document.getElementById('platform-form-pass-screening').value) || 0,
        in_exam: parseInt(document.getElementById('platform-form-in-exam').value) || 0,
        in_interview: parseInt(document.getElementById('platform-form-in-interview').value) || 0,
        link: document.getElementById('platform-form-link').value,
        notes: document.getElementById('platform-form-notes').value,
    };
    if (editingId) {
        updateJob(editingId, data);
        closePlatformModal();
    } else {
        createJob(data);
        closePlatformModal();
    }
}

// ==================== Visualization Functions ====================

function initVisualization() {
    // 更新统计卡片
    updateVizStats();

    // 初始化图表
    initCategoryChart();
    initDailyChart();
    initStatusChart();
    initWeeklyChart();
}

function updateVizStats() {
    const today = new Date().toISOString().split('T')[0];

    // 今日投递
    const todayCount = jobs.filter(j => j.apply_date === today).length;
    document.getElementById('viz-today-count').textContent = todayCount;

    // 总投递
    const totalCount = jobs.length;
    document.getElementById('viz-total-count').textContent = totalCount;

    // 本周投递
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    const weekCount = jobs.filter(j => j.apply_date && j.apply_date >= weekAgo.toISOString().split('T')[0]).length;
    document.getElementById('viz-week-count').textContent = weekCount;

    // 单日最多
    const dateCount = {};
    jobs.forEach(j => {
        if (j.apply_date) {
            dateCount[j.apply_date] = (dateCount[j.apply_date] || 0) + 1;
        }
    });
    const maxDay = Math.max(...Object.values(dateCount), 0);
    document.getElementById('viz-max-day').textContent = maxDay;
}

function initCategoryChart() {
    const ctx = document.getElementById('category-chart').getContext('2d');

    // 按类型统计
    const categories = { '国企': 0, '外企': 0, '私企': 0, '招聘平台': 0 };
    jobs.forEach(j => {
        if (j.category in categories) {
            categories[j.category]++;
        }
    });

    if (categoryChart) categoryChart.destroy();

    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['央国企', '外企', '私企', '招聘平台'],
            datasets: [{
                data: [categories['国企'], categories['外企'], categories['私企'], categories['招聘平台']],
                backgroundColor: ['#3b82f6', '#8b5cf6', '#f59e0b', '#10b981'],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 15, font: { size: 12 } }
                }
            }
        }
    });
}

function initDailyChart() {
    const ctx = document.getElementById('daily-chart').getContext('2d');

    // 按日期统计投递数量
    const dateCount = {};
    jobs.forEach(j => {
        if (j.apply_date) {
            dateCount[j.apply_date] = (dateCount[j.apply_date] || 0) + 1;
        }
    });

    // 排序日期
    const sortedDates = Object.keys(dateCount).sort();
    const counts = sortedDates.map(d => dateCount[d]);

    if (dailyChart) dailyChart.destroy();

    dailyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: sortedDates.map(d => d.substring(5)), // 只显示 MM-DD
            datasets: [{
                label: '投递数量',
                data: counts,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                fill: true,
                tension: 0.3,
                pointRadius: 4,
                pointBackgroundColor: '#667eea'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });
}

function initStatusChart() {
    const ctx = document.getElementById('status-chart').getContext('2d');

    // 按状态统计
    const statusCount = {};
    jobs.forEach(j => {
        statusCount[j.status] = (statusCount[j.status] || 0) + 1;
    });

    const labels = Object.keys(statusCount);
    const data = Object.values(statusCount);
    const colors = [
        '#f59e0b', '#ef4444', '#ef4444', '#3b82f6',
        '#8b5cf6', '#6b7280', '#10b981', '#9ca3af', '#d97706'
    ];

    if (statusChart) statusChart.destroy();

    statusChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 10, font: { size: 11 } }
                }
            }
        }
    });
}

function initWeeklyChart() {
    const ctx = document.getElementById('weekly-chart').getContext('2d');

    // 近7日统计
    const last7Days = [];
    for (let i = 6; i >= 0; i--) {
        const d = new Date();
        d.setDate(d.getDate() - i);
        last7Days.push(d.toISOString().split('T')[0]);
    }

    const dailyData = last7Days.map(date => {
        return jobs.filter(j => j.apply_date === date).length;
    });

    if (weeklyChart) weeklyChart.destroy();

    weeklyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: last7Days.map(d => {
                const date = new Date(d);
                return `${date.getMonth() + 1}/${date.getDate()}`;
            }),
            datasets: [{
                label: '投递数',
                data: dailyData,
                backgroundColor: dailyData.map((v, i) => i === 6 ? '#667eea' : 'rgba(102, 126, 234, 0.5)'),
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });
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
