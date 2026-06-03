document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.a-tab');
    const tabContents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            const target = document.getElementById('tab-' + tab.dataset.tab);
            if (target) target.classList.add('active');
            loadTabData(tab.dataset.tab);
        });
    });

    loadTabData('dashboard');

    function loadTabData(tab) {
        switch (tab) {
            case 'dashboard': loadDashboard(); break;
            case 'users': loadUsers(); break;
            case 'records': loadAdminRecords(); break;
            case 'models': loadModels(); break;
        }
    }

    async function loadDashboard() {
        try {
            const resp = await fetch('/api/stats');
            const data = await resp.json();
            const statsGrid = document.getElementById('statsGrid');
            statsGrid.innerHTML = `
                <div class="stat-card"><div class="stat-card-value">${data.total_detections}</div><div class="stat-card-label">总检测次数</div></div>
                <div class="stat-card"><div class="stat-card-value">${data.total_boxes}</div><div class="stat-card-label">总检测框数</div></div>
                <div class="stat-card ripe"><div class="stat-card-value">${data.total_ripe}</div><div class="stat-card-label">成熟蓝莓</div></div>
                <div class="stat-card semi"><div class="stat-card-value">${data.total_semi_ripe}</div><div class="stat-card-label">半熟蓝莓</div></div>
                <div class="stat-card unripe"><div class="stat-card-value">${data.total_unripe}</div><div class="stat-card-label">未熟蓝莓</div></div>
                <div class="stat-card"><div class="stat-card-value">${data.user_count}</div><div class="stat-card-label">用户总数</div></div>
            `;

            const chart = document.getElementById('dailyChart');
            const daily = data.daily_stats.reverse();
            const maxCount = Math.max(...daily.map(d => d.count), 1);
            chart.innerHTML = daily.map(d => `
                <div class="chart-bar-wrap">
                    <div class="chart-count">${d.count}</div>
                    <div class="chart-bar" style="height:${(d.count / maxCount * 160)}px"></div>
                    <div class="chart-label">${d.day}</div>
                </div>
            `).join('');
        } catch (err) {
            console.error('加载统计数据失败', err);
        }
    }

    async function loadUsers() {
        try {
            const resp = await fetch('/api/users');
            const data = await resp.json();
            const tbody = document.getElementById('userBody');
            if (data.users.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="loading-cell">暂无用户</td></tr>';
                return;
            }
            tbody.innerHTML = data.users.map(u => `
                <tr>
                    <td>${u.id}</td>
                    <td>${u.username}</td>
                    <td>${u.role === 'admin' ? '<span class="badge-admin">管理员</span>' : '普通用户'}</td>
                    <td>${u.created_at}</td>
                    <td>${u.role !== 'admin' ? `<button class="btn-sm btn-delete" data-uid="${u.id}">删除</button>` : '-'}</td>
                </tr>
            `).join('');

            tbody.querySelectorAll('.btn-delete').forEach(btn => {
                btn.addEventListener('click', async () => {
                    if (!confirm('确定要删除该用户吗？')) return;
                    try {
                        const resp = await fetch(`/api/users/${btn.dataset.uid}`, { method: 'DELETE' });
                        const d = await resp.json();
                        if (d.success) loadUsers();
                        else alert(d.message);
                    } catch (err) {
                        alert('操作失败');
                    }
                });
            });
        } catch (err) {
            console.error('加载用户列表失败', err);
        }
    }

    async function loadAdminRecords() {
        try {
            const resp = await fetch('/api/records');
            const data = await resp.json();
            const tbody = document.getElementById('adminRecordBody');
            if (data.records.length === 0) {
                tbody.innerHTML = '<tr><td colspan="9" class="loading-cell">暂无检测记录</td></tr>';
                return;
            }
            tbody.innerHTML = data.records.map(r => `
                <tr>
                    <td>${r.id}</td>
                    <td>${r.username}</td>
                    <td title="${r.image_name}">${r.image_name.length > 25 ? r.image_name.substring(0, 25) + '...' : r.image_name}</td>
                    <td>${r.ripe_count}</td>
                    <td>${r.semi_ripe_count}</td>
                    <td>${r.unripe_count}</td>
                    <td>${r.total_count}</td>
                    <td>${r.created_at}</td>
                    <td><button class="btn-sm btn-view" data-img="${r.result_image}">查看</button></td>
                </tr>
            `).join('');

            tbody.querySelectorAll('.btn-view').forEach(btn => {
                btn.addEventListener('click', () => {
                    const img = btn.dataset.img;
                    const win = window.open('', '_blank');
                    win.document.write(`<img src="/api/result_image/${img}" style="max-width:100%;">`);
                });
            });
        } catch (err) {
            console.error('加载检测记录失败', err);
        }
    }

    async function loadModels() {
        try {
            const resp = await fetch('/api/models');
            const data = await resp.json();
            document.getElementById('modelStatus').textContent = data.loaded ? '模型状态: 已加载' : '模型状态: 未加载';
            const tbody = document.getElementById('modelBody');
            if (data.models.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="loading-cell">暂无模型</td></tr>';
                return;
            }
            tbody.innerHTML = data.models.map(m => `
                <tr>
                    <td>${m.id}</td>
                    <td>${m.model_name}</td>
                    <td title="${m.model_path}">${m.model_path.length > 40 ? '...' + m.model_path.slice(-40) : m.model_path}</td>
                    <td>${m.is_active ? '<span style="color:#10B981;">● 激活</span>' : '<span style="color:#8B8BA8;">○ 未激活</span>'}</td>
                    <td>${m.created_at}</td>
                    <td>
                        ${!m.is_active ? `<button class="btn-sm btn-activate" data-mid="${m.id}">激活</button>` : ''}
                        <button class="btn-sm btn-delete" data-mid="${m.id}">删除</button>
                    </td>
                </tr>
            `).join('');

            tbody.querySelectorAll('.btn-activate').forEach(btn => {
                btn.addEventListener('click', async () => {
                    try {
                        const resp = await fetch(`/api/models/${btn.dataset.mid}/activate`, { method: 'POST' });
                        const d = await resp.json();
                        if (d.success) loadModels();
                        else alert(d.message);
                    } catch (err) { alert('操作失败'); }
                });
            });

            tbody.querySelectorAll('.btn-delete').forEach(btn => {
                btn.addEventListener('click', async () => {
                    if (!confirm('确定要删除该模型吗？')) return;
                    try {
                        const resp = await fetch(`/api/models/${btn.dataset.mid}`, { method: 'DELETE' });
                        const d = await resp.json();
                        if (d.success) loadModels();
                        else alert(d.message);
                    } catch (err) { alert('操作失败'); }
                });
            });
        } catch (err) {
            console.error('加载模型列表失败', err);
        }
    }

    document.getElementById('addUserBtn').addEventListener('click', () => {
        document.getElementById('userModal').style.display = 'flex';
        document.getElementById('newUsername').value = '';
        document.getElementById('newPassword').value = '';
        document.getElementById('userModalError').textContent = '';
    });

    document.getElementById('createUserBtn').addEventListener('click', async () => {
        const username = document.getElementById('newUsername').value.trim();
        const password = document.getElementById('newPassword').value;
        const role = document.getElementById('newRole').value;
        const errEl = document.getElementById('userModalError');

        if (!username || !password) {
            errEl.textContent = '请填写用户名和密码';
            return;
        }
        if (username.length < 3) { errEl.textContent = '用户名至少3个字符'; return; }
        if (password.length < 6) { errEl.textContent = '密码至少6个字符'; return; }

        try {
            const resp = await fetch('/api/users', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password, role })
            });
            const d = await resp.json();
            if (d.success) {
                document.getElementById('userModal').style.display = 'none';
                loadUsers();
            } else {
                errEl.textContent = d.message;
            }
        } catch (err) { errEl.textContent = '操作失败'; }
    });

    document.getElementById('uploadModelBtn').addEventListener('click', () => {
        document.getElementById('modelModal').style.display = 'flex';
        document.getElementById('modelFile').value = '';
        document.getElementById('modelFileName').textContent = '';
        document.getElementById('modelModalError').textContent = '';
        document.getElementById('setActive').checked = false;
    });

    document.getElementById('modelUploadArea').addEventListener('click', () => {
        document.getElementById('modelFile').click();
    });

    document.getElementById('modelFile').addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            document.getElementById('modelFileName').textContent = e.target.files[0].name;
        }
    });

    document.getElementById('uploadModelConfirmBtn').addEventListener('click', async () => {
        const fileInput = document.getElementById('modelFile');
        const errEl = document.getElementById('modelModalError');
        if (!fileInput.files.length) {
            errEl.textContent = '请选择模型文件';
            return;
        }
        const formData = new FormData();
        formData.append('model', fileInput.files[0]);
        formData.append('is_active', document.getElementById('setActive').checked ? '1' : '0');

        try {
            const resp = await fetch('/api/models/upload', {
                method: 'POST',
                body: formData
            });
            const d = await resp.json();
            if (d.success) {
                document.getElementById('modelModal').style.display = 'none';
                loadModels();
            } else {
                errEl.textContent = d.message;
            }
        } catch (err) { errEl.textContent = '上传失败'; }
    });

    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', () => {
            const modalId = btn.dataset.close;
            if (modalId) document.getElementById(modalId).style.display = 'none';
        });
    });

    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) overlay.style.display = 'none';
        });
    });
});