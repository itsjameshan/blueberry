document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('uploadArea');
    const imageInput = document.getElementById('imageInput');
    const fileList = document.getElementById('fileList');
    const detectBtn = document.getElementById('detectBtn');
    const confSlider = document.getElementById('confSlider');
    const confValue = document.getElementById('confValue');
    const summaryCard = document.getElementById('summaryCard');
    const summaryBody = document.getElementById('summaryBody');
    const summaryStats = document.getElementById('summaryStats');
    const detailCard = document.getElementById('detailCard');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    const btnBack = document.getElementById('btnBack');
    const batchHighlightCanvas = document.getElementById('batchHighlightCanvas');
    const batchHighlightContainer = document.getElementById('batchHighlightContainer');
    let selectedFiles = [];
    let allResults = [];
    let fileUrlMap = {};
    let batchHighlightTarget = null;
    let batchActiveHighlightClass = null;
    let currentDetailResults = [];
    const detailImg = document.getElementById('detailImg');

    uploadArea.addEventListener('click', () => imageInput.click());

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#6C5CE7';
        uploadArea.style.background = '#F4F2FF';
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = '#D0CAF5';
        uploadArea.style.background = '#FAFAFF';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#D0CAF5';
        uploadArea.style.background = '#FAFAFF';
        if (e.dataTransfer.files.length > 0) {
            addFiles(Array.from(e.dataTransfer.files));
        }
    });

    imageInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            addFiles(Array.from(e.target.files));
        }
    });

    function addFiles(files) {
        files.forEach(file => {
            if (!file.type.match(/^image\/(jpeg|png)$/)) return;
            if (selectedFiles.find(f => f.name === file.name && f.size === file.size)) return;
            selectedFiles.push(file);
        });
        renderFileList();
    }

    function removeFile(index) {
        selectedFiles.splice(index, 1);
        renderFileList();
    }

    function renderFileList() {
        fileList.innerHTML = selectedFiles.map((file, i) => {
            const url = URL.createObjectURL(file);
            fileUrlMap[file.name] = url;
            return `<div class="file-tag">
                <img src="${url}" class="file-thumb" alt="${file.name}">
                <span>${file.name}</span>
                <span class="remove-tag" data-index="${i}">✕</span>
            </div>`;
        }).join('');

        fileList.querySelectorAll('.remove-tag').forEach(el => {
            el.addEventListener('click', (e) => {
                e.stopPropagation();
                removeFile(parseInt(el.dataset.index));
            });
        });

        detectBtn.disabled = selectedFiles.length === 0;
        if (selectedFiles.length > 0) {
            detectBtn.textContent = `开始批量检测 (${selectedFiles.length} 张)`;
        } else {
            detectBtn.textContent = '开始批量检测';
        }
    }

    confSlider.addEventListener('input', () => {
        confValue.textContent = confSlider.value;
    });

    detectBtn.addEventListener('click', async () => {
        if (selectedFiles.length === 0) return;
        loadingOverlay.style.display = 'flex';
        summaryCard.style.display = 'none';
        detailCard.style.display = 'none';
        allResults = [];

        const formData = new FormData();
        selectedFiles.forEach(file => formData.append('images', file));
        formData.append('conf', confSlider.value);

        loadingText.textContent = `正在检测 0 / ${selectedFiles.length} ...`;

        try {
            const resp = await fetch('/api/batch_detect_multi', {
                method: 'POST',
                body: formData
            });
            const data = await resp.json();
            if (data.success) {
                allResults = data.results;
                renderSummary(data);
            } else {
                alert(data.message);
            }
        } catch (err) {
            alert('检测失败，请检查网络连接');
        } finally {
            loadingOverlay.style.display = 'none';
        }
    });

    function renderSummary(data) {
        summaryCard.style.display = 'block';
        detailCard.style.display = 'none';

        const total = data.total_stats;
        summaryStats.innerHTML = `
            <div class="summary-stat s-ripe">
                <div class="s-value">${total.RipeBlueBerry}</div>
                <div class="s-label">成熟蓝莓</div>
            </div>
            <div class="summary-stat s-semi">
                <div class="s-value">${total['Semi-RipeBlueBerry']}</div>
                <div class="s-label">半熟蓝莓</div>
            </div>
            <div class="summary-stat s-unripe">
                <div class="s-value">${total.UnripeBlueBerry}</div>
                <div class="s-label">未熟蓝莓</div>
            </div>
            <div class="summary-stat">
                <div class="s-value">${total.total}</div>
                <div class="s-label">总检测框</div>
            </div>
            <div class="summary-stat">
                <div class="s-value">${data.results.length}</div>
                <div class="s-label">检测图片数</div>
            </div>
        `;

        summaryBody.innerHTML = data.results.map((item, i) => {
            const s = item.stats;
            const resultImg = item.result_image ? item.result_image : '';
            const originUrl = fileUrlMap[item.filename] || '';
            const thumbSrc = originUrl || resultImg;
            return `<tr>
                <td>${i + 1}</td>
                <td><img src="${thumbSrc}" class="thumb-img" alt="${item.filename}" onerror="this.onerror=null;this.src='data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2248%22%20height%3D%2248%22%3E%3Crect%20fill%3D%22%23F4F2FF%22%20width%3D%2248%22%20height%3D%2248%22%20rx%3D%228%22%2F%3E%3Ctext%20x%3D%2224%22%20y%3D%2230%22%20text-anchor%3D%22middle%22%20font-size%3D%2218%22%3E%F0%9F%AB%90%3C%2Ftext%3E%3C%2Fsvg%3E'"></td>
                <td title="${item.filename}">${item.filename.length > 20 ? item.filename.substring(0, 20) + '...' : item.filename}</td>
                <td>${s.RipeBlueBerry}</td>
                <td>${s['Semi-RipeBlueBerry']}</td>
                <td>${s.UnripeBlueBerry}</td>
                <td>${s.total}</td>
                <td><button class="btn-view-detail" data-index="${i}">查看详情</button></td>
            </tr>`;
        }).join('');

        summaryBody.querySelectorAll('.btn-view-detail').forEach(btn => {
            btn.addEventListener('click', () => showDetail(parseInt(btn.dataset.index)));
        });

        summaryCard.scrollIntoView({ behavior: 'smooth' });
    }

    function showDetail(index) {
        const item = allResults[index];
        if (!item) return;

        detailCard.style.display = 'block';
        document.getElementById('detailTitle').textContent = `🔍 检测详情 - ${item.filename}`;

        currentDetailResults = item.results || [];
        batchHighlightTarget = null;
        batchActiveHighlightClass = null;
        batchHighlightCanvas.style.display = 'none';

        if (item.result_image) {
            detailImg.src = item.result_image;
        } else {
            const originUrl = fileUrlMap[item.filename] || '';
            detailImg.src = originUrl;
        }

        setupBatchCanvasOverlay();

        const s = item.stats;
        document.getElementById('dRipe').textContent = s.RipeBlueBerry;
        document.getElementById('dSemi').textContent = s['Semi-RipeBlueBerry'];
        document.getElementById('dUnripe').textContent = s.UnripeBlueBerry;
        document.getElementById('dTotal').textContent = s.total;

        const tbody = document.getElementById('detailTableBody');
        const noResult = document.getElementById('noDetailResult');
        tbody.innerHTML = '';
        noResult.style.display = 'none';

        if (currentDetailResults.length > 0) {
            currentDetailResults.forEach((r, i) => {
                const row = document.createElement('tr');
                row.className = 'result-row';
                row.dataset.index = i;
                row.innerHTML = `
                    <td>${i + 1}</td>
                    <td>${r.class_name}</td>
                    <td>${(r.confidence * 100).toFixed(1)}%</td>
                    <td>(${r.x1}, ${r.y1}, ${r.x2}, ${r.y2})</td>
                `;
                row.addEventListener('click', () => batchHighlightBox(i));
                tbody.appendChild(row);
            });
        } else {
            noResult.style.display = 'block';
        }

        setupBatchStatClicks();
        detailCard.scrollIntoView({ behavior: 'smooth' });
    }

    function setupBatchCanvasOverlay() {
        batchHighlightCanvas.style.display = 'none';
        detailImg.onload = () => syncBatchCanvasSize();
        if (detailImg.complete) syncBatchCanvasSize();
    }

    function syncBatchCanvasSize() {
        const rect = detailImg.getBoundingClientRect();
        const containerRect = batchHighlightContainer.getBoundingClientRect();
        const offsetX = rect.left - containerRect.left;
        const offsetY = rect.top - containerRect.top;
        batchHighlightCanvas.style.left = offsetX + 'px';
        batchHighlightCanvas.style.top = offsetY + 'px';
        batchHighlightCanvas.width = rect.width;
        batchHighlightCanvas.height = rect.height;
        if (batchHighlightTarget !== null || batchActiveHighlightClass !== null) {
            drawBatchHighlight();
        }
    }

    function getBatchImageScale() {
        const displayedW = detailImg.clientWidth;
        const displayedH = detailImg.clientHeight;
        const naturalW = detailImg.naturalWidth;
        const naturalH = detailImg.naturalHeight;
        if (!naturalW || !naturalH) return { scaleX: 1, scaleY: 1 };
        return { scaleX: displayedW / naturalW, scaleY: displayedH / naturalH };
    }

    function batchHighlightBox(index) {
        if (batchHighlightTarget === index) {
            batchHighlightTarget = null;
        } else {
            batchHighlightTarget = index;
        }
        batchActiveHighlightClass = null;
        clearBatchStatActiveStates();
        highlightBatchTableRow(index);
        drawBatchHighlight();
    }

    function batchHighlightByClass(className) {
        if (batchActiveHighlightClass === className) {
            batchActiveHighlightClass = null;
        } else {
            batchActiveHighlightClass = className;
        }
        batchHighlightTarget = null;
        clearBatchRowActiveStates();
        highlightBatchTableRowsByClass(className);
        drawBatchHighlight();
    }

    function highlightBatchTableRow(index) {
        clearBatchRowActiveStates();
        if (index !== null) {
            const row = document.getElementById('detailTableBody').querySelector(`tr[data-index="${index}"]`);
            if (row) row.classList.add('active');
        }
    }

    function highlightBatchTableRowsByClass(className) {
        clearBatchRowActiveStates();
        if (className) {
            currentDetailResults.forEach((r, i) => {
                if (r.class_name === className) {
                    const row = document.getElementById('detailTableBody').querySelector(`tr[data-index="${i}"]`);
                    if (row) row.classList.add('active');
                }
            });
        }
    }

    function drawBatchHighlight() {
        const ctx = batchHighlightCanvas.getContext('2d');
        ctx.clearRect(0, 0, batchHighlightCanvas.width, batchHighlightCanvas.height);

        if (batchHighlightTarget === null && batchActiveHighlightClass === null) {
            batchHighlightCanvas.style.display = 'none';
            return;
        }

        batchHighlightCanvas.style.display = 'block';
        const { scaleX, scaleY } = getBatchImageScale();

        const highlightColor = 'rgba(255, 215, 0, 0.45)';
        const highlightBorder = 'rgba(255, 180, 0, 0.9)';

        currentDetailResults.forEach((r, i) => {
            let shouldHighlight = false;
            if (batchHighlightTarget !== null && batchHighlightTarget === i) shouldHighlight = true;
            if (batchActiveHighlightClass !== null && r.class_name === batchActiveHighlightClass) shouldHighlight = true;

            if (shouldHighlight) {
                const x = r.x1 * scaleX;
                const y = r.y1 * scaleY;
                const w = (r.x2 - r.x1) * scaleX;
                const h = (r.y2 - r.y1) * scaleY;
                ctx.fillStyle = highlightColor;
                ctx.fillRect(x, y, w, h);
                ctx.strokeStyle = highlightBorder;
                ctx.lineWidth = 2;
                ctx.strokeRect(x, y, w, h);
            }
        });
    }

    function clearBatchStatActiveStates() {
        document.querySelectorAll('#detailCard .stat-item').forEach(el => el.classList.remove('active'));
    }

    function clearBatchRowActiveStates() {
        document.getElementById('detailTableBody').querySelectorAll('tr').forEach(el => el.classList.remove('active'));
    }

    function setupBatchStatClicks() {
        document.querySelectorAll('#detailCard .stat-item').forEach(el => {
            const newEl = el.cloneNode(true);
            el.parentNode.replaceChild(newEl, el);
            newEl.addEventListener('click', () => {
                const label = newEl.querySelector('.stat-label')?.textContent || '';
                clearBatchRowActiveStates();
                if (label === '成熟蓝莓') {
                    newEl.classList.toggle('active');
                    batchHighlightByClass('RipeBlueBerry');
                } else if (label === '半熟蓝莓') {
                    newEl.classList.toggle('active');
                    batchHighlightByClass('Semi-RipeBlueBerry');
                } else if (label === '未熟蓝莓') {
                    newEl.classList.toggle('active');
                    batchHighlightByClass('UnripeBlueBerry');
                } else {
                    batchActiveHighlightClass = null;
                    batchHighlightTarget = null;
                    drawBatchHighlight();
                }
            });
        });
    }

    btnBack.addEventListener('click', () => {
        detailCard.style.display = 'none';
        summaryCard.scrollIntoView({ behavior: 'smooth' });
    });
});