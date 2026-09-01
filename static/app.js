// API Base URL - change this when deployed
const API_BASE = window.location.origin;

// State
let jobs = [];
let editingId = null;

// DOM Elements
const tableBody = document.getElementById('job-table-body');
const searchInput = document.getElementById('search-input');
const filterCategory = document.getElementById('filter-category');
const filterStatus = document.getElementById('filter-status');
const filterSource = document.getElementById('filter-source');
const addBtn = document.getElementById('add-btn');
const modal = document.getElementById('modal');
const modalClose = document.getElementById('modal-close');
const modalTitle = document.getElementById('modal-title');
const jobForm = document.getElementById('job-form');
const formCancel = document.getElementById('form-cancel');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadJobs();
    loadStats();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    addBtn.addEventListener('click', () => openModal());
    modalClose.addEventListener('click', closeModal);
    formCancel.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    searchInput.addEventListener('input', debounce(renderTable, 300));
    filterCategory.addEventListener('change', renderTable);
    filterStatus.addEventListener('change', renderTable);
    filterSource.addEventListener('change', renderTable);

    jobForm.addEventListener('submit', handleSubmit);
}

// API Functions
async function loadJobs() {
    try {
        const response = await fetch(`${API_BASE}/api/jobs`);
        jobs = await response.json();
        renderTable();
    } catch (error) {
        console.error('加载数据失败:', error);
        tableBody.innerHTML = '<tr><td colspan="10" class="empty-state"><div class="icon">⚠️</div><p>加载失败，请检查网络连接</p></td></tr>';
    }
}

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        const stats = await response.json();

        document.getElementById('stat-total').textContent = stats.total;
        document.getElementById('stat-pending').textContent = stats.pending;
        document.getElementById('stat-rejected').textContent = stats.rejected;
        document.getElementById('stat-interview').textContent = stats.interview;
        document.getElementById('stat-written').textContent = stats.written;
        document.getElementById('stat-offer').textContent = stats.offer;

        document.getElementById('cat-state-count').textContent = stats.categories.state.count;
        document.getElementById('cat-state-reject').textContent = stats.categories.state.reject;
        document.getElementById('cat-foreign-count').textContent = stats.categories.foreign.count;
        document.getElementById('cat-foreign-reject').textContent = stats.categories.foreign.reject;
        document.getElementById('cat-private-count').textContent = stats.categories.private.count;
        document.getElementById('cat-private-reject').textContent = stats.categories.private.reject;
    } catch (error) {
        console.error('加载统计失败:', error);
    }
}

async function createJob(data) {
    try {
        const response = await fetch(`${API_BASE}/api/jobs`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
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
            headers: { 'Content-Type': 'application/json' },
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
            method: 'DELETE'
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

// Render Functions
function renderTable() {
    const search = searchInput.value.toLowerCase();
    const category = filterCategory.value;
    const status = filterStatus.value;
    const source = filterSource.value;

    let filtered = jobs.filter(job => {
        if (search && !job.company.toLowerCase().includes(search) && !job.position.toLowerCase().includes(search)) {
            return false;
        }
        if (category !== 'all' && job.category !== category) return false;
        if (status !== 'all' && job.status !== status) return false;
        if (source !== 'all' && job.source !== source) return false;
        return true;
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
            <td><span class="category-badge category-${job.category}">${job.category}</span></td>
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

// Modal Functions
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

// Form Handler
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

// Utility Functions
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
