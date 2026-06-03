document.addEventListener('DOMContentLoaded', () => {
    let allRecords = [];
    let currentPage = 1;
    const pageSize = 15;

    const searchInput = document.getElementById('searchInput');
    const refreshBtn = document.getElementById('refreshBtn');
    const modal = document.getElementById('detailModal');
    const modalClose = document.getElementById('modalClose');

    loadRecords();

    refreshBtn.addEventListener('click', loadRecords);

    searchInput.addEventListener('input', () => {
        currentPage = 1;
        renderTable();
    });

    modalClose.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.style.display = 'none';
    });

    async function loadRecords() {
        document.getElementById('recordBody').innerHTML = '<tr><td colspan="10" class="loading-cell">加载中...</td></tr>';
        try {
            const resp = await fetch('/api/records');
            const data = await resp.json();
            if (data.success) {
                allRecords = data.records;
                currentPage = 1;
                renderTable();
            }
        } catch (err) {
            document.getElementById('recordBody').innerHTML = '<tr><td colspan="10" class="loading-cell" style="color:#EF4444;">加载失败</td></tr>';
        }
    }

    function renderTable() {
        const search = searchInput.value.trim().toLowerCase();
        let filtered = allRecords;
        if (search) {
            filtered = allRecords.filter(r => r.image_name.toLowerCase().includes(search));
        }

        const totalPages = Math.ceil(filtered.length / pageSize) || 1;
        if (currentPage > totalPages) currentPage = totalPages;

        const start = (currentPage - 1) * pageSize;
        const pageRecords = filtered.slice(start, start + pageSize);

        const tbody = document.getElementById('recordBody');
        if (pageRecords.length === 0) {
            tbody.innerHTML = '<tr><td colspan="10" class="loading-cell">暂无检测记录</td></tr>';
        } else {
            let html = '';
            pageRecords.forEach(r => {
                const showUser = document.querySelector('th:nth-child(2)')?.textContent === '用户';
                html += `<tr>
                    <td>${r.id}</td>
                    ${showUser ? `<td>${r.username}</td>` : ''}
                    <td title="${r.image_name}">${r.image_name.length > 20 ? r.image_name.substring(0, 20) + '...' : r.image_name}</td>
                    <td>${r.ripe_count}</td>
                    <td>${r.semi_ripe_count}</td>
                    <td>${r.unripe_count}</td>
                    <td>${r.total_count}</td>
                    <td>${r.conf_threshold}</td>
                    <td>${r.created_at}</td>
                    <td class="action-cell">
                        <button class="btn-view" data-id="${r.id}">查看</button>
                        <button class="btn-download" data-id="${r.id}">下载</button>
                    </td>
                </tr>`;
            });
            tbody.innerHTML = html;
        }

        renderPagination(totalPages);

        document.querySelectorAll('.btn-view').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = parseInt(btn.dataset.id);
                const record = allRecords.find(r => r.id === id);
                if (record) showDetail(record);
            });
        });

        document.querySelectorAll('.btn-download').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = parseInt(btn.dataset.id);
                downloadRecord(id);
            });
        });
    }

    function renderPagination(totalPages) {
        const pag = document.getElementById('pagination');
        if (totalPages <= 1) {
            pag.innerHTML = '';
            return;
        }
        let html = '';
        html += `<button class="page-btn" ${currentPage === 1 ? 'disabled' : ''} data-page="${currentPage - 1}">上一页</button>`;
        for (let i = 1; i <= totalPages; i++) {
            html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" data-page="${i}">${i}</button>`;
        }
        html += `<button class="page-btn" ${currentPage === totalPages ? 'disabled' : ''} data-page="${currentPage + 1}">下一页</button>`;
        pag.innerHTML = html;

        pag.querySelectorAll('.page-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const p = parseInt(btn.dataset.page);
                if (p >= 1 && p <= totalPages) {
                    currentPage = p;
                    renderTable();
                }
            });
        });
    }

    function showDetail(record) {
        document.getElementById('detailImg').src = `/api/result_image/${record.result_image}`;
        document.getElementById('detailInfo').innerHTML = `
            <div class="detail-stat"><div class="val">${record.total_count}</div><div class="lbl">总检测框</div></div>
            <div class="detail-stat"><div class="val">${record.ripe_count}</div><div class="lbl">成熟蓝莓</div></div>
            <div class="detail-stat"><div class="val">${record.semi_ripe_count}</div><div class="lbl">半熟蓝莓</div></div>
            <div class="detail-stat"><div class="val">${record.unripe_count}</div><div class="lbl">未熟蓝莓</div></div>
            <div class="detail-stat"><div class="val">${record.conf_threshold}</div><div class="lbl">置信度阈值</div></div>
        `;
        modal.style.display = 'flex';
    }

    function downloadRecord(id) {
        const record = allRecords.find(r => r.id === id);
        if (!record) return;
        window.open(`/api/record/${id}/download`, '_blank');
    }
});