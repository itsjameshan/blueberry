document.addEventListener('DOMContentLoaded', () => {
    let cropData = null;
    let batchData = null;
    let originalImageFile = null;
    let originalImageWidth = 0;
    let originalImageHeight = 0;
    let bigDetectionResults = [];
    let bigHighlightTarget = null;
    let bigActiveHighlightClass = null;

    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    const bigResultImg = document.getElementById('resultImg');
    const bigHighlightCanvas = document.getElementById('bigHighlightCanvas');
    const bigHighlightContainer = document.getElementById('bigHighlightContainer');

    function setStep(step) {
        document.querySelectorAll('.step-item').forEach((el, i) => {
            el.classList.remove('active', 'done');
            if (i + 1 < step) el.classList.add('done');
            if (i + 1 === step) el.classList.add('active');
        });
        document.querySelectorAll('.step-line').forEach((el, i) => {
            if (i + 1 < step) el.classList.add('done');
            else el.classList.remove('done');
        });
        document.querySelectorAll('.step-panel').forEach((el, i) => {
            el.classList.toggle('active', i + 1 === step);
        });
        if (step === 3 && originalImageWidth && originalImageHeight) {
            document.getElementById('originalWidth').value = originalImageWidth;
            document.getElementById('originalHeight').value = originalImageHeight;
        }
    }

    function showLoading(msg) {
        loadingText.textContent = msg;
        loadingOverlay.style.display = 'flex';
    }
    function hideLoading() {
        loadingOverlay.style.display = 'none';
    }

    // ============ STEP 1: CROP ============
    const uploadArea = document.getElementById('uploadArea');
    const imageInput = document.getElementById('imageInput');
    const preview = document.getElementById('preview');
    const placeholder = uploadArea.querySelector('.upload-placeholder');
    const cropBtn = document.getElementById('cropBtn');
    const tileSizeInput = document.getElementById('tileSize');
    const overlapInput = document.getElementById('overlap');
    const imageSize = document.getElementById('imageSize');
    const tileEstimate = document.getElementById('tileEstimate');
    const cropResult = document.getElementById('cropResult');
    const cropStatus = document.getElementById('cropStatus');

    uploadArea.addEventListener('click', () => imageInput.click());
    uploadArea.addEventListener('dragover', (e) => { e.preventDefault(); uploadArea.style.borderColor = '#6C5CE7'; uploadArea.style.background = '#F4F2FF'; });
    uploadArea.addEventListener('dragleave', () => { uploadArea.style.borderColor = '#D0CAF5'; uploadArea.style.background = '#FAFAFF'; });
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#D0CAF5';
        uploadArea.style.background = '#FAFAFF';
        if (e.dataTransfer.files.length > 0) handleStep1File(e.dataTransfer.files[0]);
    });
    imageInput.addEventListener('change', (e) => { if (e.target.files.length > 0) handleStep1File(e.target.files[0]); });

    function handleStep1File(file) {
        if (!file.type.match(/^image\/(jpeg|png)$/)) {
            alert('请选择 JPG 或 PNG 格式的图片');
            return;
        }
        originalImageFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.src = e.target.result;
            preview.classList.remove('preview-hidden');
            placeholder.style.display = 'none';
            cropBtn.disabled = false;
            updateStep1Estimate();
        };
        reader.readAsDataURL(file);
    }

    function updateStep1Estimate() {
        const img = new Image();
        img.onload = () => {
            originalImageWidth = img.width;
            originalImageHeight = img.height;
            imageSize.textContent = `图片尺寸: ${img.width} × ${img.height} px`;
            const ts = parseInt(tileSizeInput.value);
            const ol = parseInt(overlapInput.value);
            const stride = ts - ol;
            const cols = Math.ceil((img.width - ol) / stride);
            const rows = Math.ceil((img.height - ol) / stride);
            tileEstimate.textContent = `预计裁剪: ${rows} × ${cols} = ${rows * cols} 张图块`;
            document.getElementById('originalWidth').value = img.width;
            document.getElementById('originalHeight').value = img.height;
        };
        img.src = preview.src;
    }
    tileSizeInput.addEventListener('input', updateStep1Estimate);
    overlapInput.addEventListener('input', updateStep1Estimate);

    cropBtn.addEventListener('click', async () => {
        if (!originalImageFile) return;
        showLoading('正在裁剪图片...');
        cropResult.style.display = 'none';
        cropStatus.textContent = '';

        const formData = new FormData();
        formData.append('image', originalImageFile);
        formData.append('tile_size', tileSizeInput.value);
        formData.append('overlap', overlapInput.value);

        try {
            const resp = await fetch('/api/crop', { method: 'POST', body: formData });
            const data = await resp.json();
            if (data.success) {
                cropData = data;
                renderCropResult(data);
                cropStatus.textContent = '裁剪完成 ✓';
                cropStatus.style.color = '#10B981';
                document.getElementById('tileSize2').value = tileSizeInput.value;
                document.getElementById('overlap2').value = overlapInput.value;
                document.getElementById('rebuildInfo').textContent = '已加载裁剪数据，原始图片尺寸已自动填充';
                setStep(2);
            } else {
                alert(data.message);
            }
        } catch (err) {
            alert('裁剪失败，请检查网络连接');
        } finally {
            hideLoading();
        }
    });

    function renderCropResult(data) {
        cropResult.style.display = 'block';
        document.getElementById('cropStats').innerHTML = `共裁剪 <strong>${data.tile_count}</strong> 张图块 | 输出目录: <strong>${data.crop_dir}</strong>`;
        const preview = document.getElementById('tilesPreview');
        const cropDirName = data.crop_dir.split(/[\\/]/).pop();
        preview.innerHTML = data.tiles.map(t => `<span class="tile-chip"><img src="/api/crop_tile/${cropDirName}/${t.name}" alt="${t.name}" onerror="this.style.display='none'"><span>${t.name}</span></span>`).join('');
        document.getElementById('detectInfo').textContent = `已加载裁剪数据：${data.tile_count} 张图块，准备就绪`;
    }

    // ============ STEP 2: BATCH DETECT ============
    const confSlider1 = document.getElementById('confSlider1');
    const confValue1 = document.getElementById('confValue1');
    const batchDetectBtn = document.getElementById('batchDetectBtn');
    const batchResult = document.getElementById('batchResult');
    const batchStatus = document.getElementById('batchStatus');

    confSlider1.addEventListener('input', () => { confValue1.textContent = confSlider1.value; });

    batchDetectBtn.addEventListener('click', async () => {
        if (!cropData || !cropData.crop_dir) {
            alert('请先完成第一步图片裁剪');
            setStep(1);
            return;
        }
        showLoading('正在批量检测中，请耐心等待...');
        batchResult.style.display = 'none';
        batchStatus.textContent = '';

        try {
            const resp = await fetch('/api/batch_detect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    crop_dir: cropData.crop_dir,
                    conf: parseFloat(confSlider1.value)
                })
            });
            const data = await resp.json();
            if (data.success) {
                batchData = data;
                renderBatchResult(data);
                batchStatus.textContent = '批量检测完成 ✓';
                batchStatus.style.color = '#10B981';
                setStep(3);
            } else {
                alert(data.message);
            }
        } catch (err) {
            alert('检测失败，请检查网络连接');
        } finally {
            hideLoading();
        }
    });

    function renderBatchResult(data) {
        batchResult.style.display = 'block';
        document.getElementById('summaryStats').innerHTML = `
            <div class="summary-stat"><div class="stat-value">${data.total_stats.total}</div><div class="stat-label">总计检测框</div></div>
            <div class="summary-stat"><div class="stat-value">${data.total_stats.RipeBlueBerry}</div><div class="stat-label">成熟蓝莓</div></div>
            <div class="summary-stat"><div class="stat-value">${data.total_stats['Semi-RipeBlueBerry']}</div><div class="stat-label">半熟蓝莓</div></div>
            <div class="summary-stat"><div class="stat-value">${data.total_stats.UnripeBlueBerry}</div><div class="stat-label">未熟蓝莓</div></div>
        `;
        const tbody = document.getElementById('batchResultBody');
        tbody.innerHTML = data.results.map(r => {
            const hasError = r.error;
            return `<tr>
                <td>${r.tile_name}</td>
                <td>${r.stats.RipeBlueBerry}</td>
                <td>${r.stats['Semi-RipeBlueBerry']}</td>
                <td>${r.stats.UnripeBlueBerry}</td>
                <td>${r.stats.total}</td>
                <td class="${hasError ? 'status-err' : 'status-ok'}">${hasError ? '失败' : '成功'}</td>
            </tr>`;
        }).join('');
    }

    // ============ STEP 3: REBUILD ============
    const confSlider2 = document.getElementById('confSlider2');
    const confValue2 = document.getElementById('confValue2');
    const rebuildBtn = document.getElementById('rebuildBtn');
    const rebuildResult = document.getElementById('rebuildResult');
    const rebuildStatus = document.getElementById('rebuildStatus');

    confSlider2.addEventListener('input', () => { confValue2.textContent = confSlider2.value; });

    rebuildBtn.addEventListener('click', async () => {
        if (!cropData || !cropData.crop_dir) {
            alert('请先完成裁剪和检测步骤');
            setStep(1);
            return;
        }
        var originalWidth = parseInt(document.getElementById('originalWidth').value) || originalImageWidth;
        var originalHeight = parseInt(document.getElementById('originalHeight').value) || originalImageHeight;
        if (!originalWidth || !originalHeight) {
            alert('未能获取原始图片尺寸，请手动填写');
            return;
        }

        showLoading('正在重建结果...');
        rebuildResult.style.display = 'none';
        rebuildStatus.textContent = '';

        try {
            const resp = await fetch('/api/rebuild', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    crop_dir: cropData.crop_dir,
                    original_image: cropData.original_image || '',
                    original_width: originalWidth,
                    original_height: originalHeight,
                    tile_size: parseInt(document.getElementById('tileSize2').value),
                    overlap: parseInt(document.getElementById('overlap2').value),
                    conf: parseFloat(confSlider2.value)
                })
            });
            const data = await resp.json();
            if (data.success) {
                renderRebuildResult(data);
                rebuildStatus.textContent = '重建完成 ✓ 所有步骤已完成！';
                rebuildStatus.style.color = '#10B981';
            } else {
                alert(data.message);
            }
        } catch (err) {
            alert('重建失败，请检查网络连接');
        } finally {
            hideLoading();
        }
    });

    function renderRebuildResult(data) {
        rebuildResult.style.display = 'block';
        bigDetectionResults = data.results || [];
        bigHighlightTarget = null;
        bigActiveHighlightClass = null;
        bigHighlightCanvas.style.display = 'none';

        document.getElementById('ripeCount').textContent = data.stats.RipeBlueBerry;
        document.getElementById('semiCount').textContent = data.stats['Semi-RipeBlueBerry'];
        document.getElementById('unripeCount').textContent = data.stats.UnripeBlueBerry;
        document.getElementById('totalCount').textContent = data.stats.total;

        if (data.result_image) {
            bigResultImg.src = data.result_image;
        } else if (preview.src && !preview.classList.contains('preview-hidden')) {
            bigResultImg.src = preview.src;
        }

        setupBigCanvasOverlay();

        const tbody = document.getElementById('resultTable').querySelector('tbody');
        const noResult = document.getElementById('noResult');
        tbody.innerHTML = '';
        if (bigDetectionResults.length === 0) {
            noResult.style.display = 'block';
            document.getElementById('resultTable').style.display = 'none';
        } else {
            noResult.style.display = 'none';
            document.getElementById('resultTable').style.display = 'table';
            bigDetectionResults.forEach((r, i) => {
                const row = document.createElement('tr');
                row.className = 'result-row';
                row.dataset.index = i;
                row.innerHTML = `
                    <td>${i + 1}</td>
                    <td>${r.class_name}</td>
                    <td>${(r.confidence * 100).toFixed(1)}%</td>
                    <td>(${r.x1}, ${r.y1}, ${r.x2}, ${r.y2})</td>
                `;
                row.addEventListener('click', () => bigHighlightBox(i));
                tbody.appendChild(row);
            });
        }

        setupBigStatClicks();
        rebuildResult.scrollIntoView({ behavior: 'smooth' });
    }

    function setupBigCanvasOverlay() {
        bigHighlightCanvas.style.display = 'none';
        bigResultImg.onload = () => syncBigCanvasSize();
        if (bigResultImg.complete) syncBigCanvasSize();
    }

    function syncBigCanvasSize() {
        const rect = bigResultImg.getBoundingClientRect();
        const containerRect = bigHighlightContainer.getBoundingClientRect();
        const offsetX = rect.left - containerRect.left;
        const offsetY = rect.top - containerRect.top;
        bigHighlightCanvas.style.left = offsetX + 'px';
        bigHighlightCanvas.style.top = offsetY + 'px';
        bigHighlightCanvas.width = rect.width;
        bigHighlightCanvas.height = rect.height;
        if (bigHighlightTarget !== null || bigActiveHighlightClass !== null) {
            drawBigHighlight();
        }
    }

    function getBigImageScale() {
        const displayedW = bigResultImg.clientWidth;
        const displayedH = bigResultImg.clientHeight;
        const naturalW = bigResultImg.naturalWidth;
        const naturalH = bigResultImg.naturalHeight;
        if (!naturalW || !naturalH) return { scaleX: 1, scaleY: 1 };
        return { scaleX: displayedW / naturalW, scaleY: displayedH / naturalH };
    }

    function bigHighlightBox(index) {
        if (bigHighlightTarget === index) {
            bigHighlightTarget = null;
        } else {
            bigHighlightTarget = index;
        }
        bigActiveHighlightClass = null;
        clearBigStatActiveStates();
        highlightBigTableRow(index);
        drawBigHighlight();
    }

    function bigHighlightByClass(className) {
        if (bigActiveHighlightClass === className) {
            bigActiveHighlightClass = null;
        } else {
            bigActiveHighlightClass = className;
        }
        bigHighlightTarget = null;
        clearBigRowActiveStates();
        highlightBigTableRowsByClass(className);
        drawBigHighlight();
    }

    function highlightBigTableRow(index) {
        clearBigRowActiveStates();
        if (index !== null) {
            const row = document.getElementById('resultTable').querySelector(`tr[data-index="${index}"]`);
            if (row) row.classList.add('active');
        }
    }

    function highlightBigTableRowsByClass(className) {
        clearBigRowActiveStates();
        if (className) {
            bigDetectionResults.forEach((r, i) => {
                if (r.class_name === className) {
                    const row = document.getElementById('resultTable').querySelector(`tr[data-index="${i}"]`);
                    if (row) row.classList.add('active');
                }
            });
        }
    }

    function drawBigHighlight() {
        const ctx = bigHighlightCanvas.getContext('2d');
        ctx.clearRect(0, 0, bigHighlightCanvas.width, bigHighlightCanvas.height);

        if (bigHighlightTarget === null && bigActiveHighlightClass === null) {
            bigHighlightCanvas.style.display = 'none';
            return;
        }

        bigHighlightCanvas.style.display = 'block';
        const { scaleX, scaleY } = getBigImageScale();

        const highlightColor = 'rgba(255, 215, 0, 0.45)';
        const highlightBorder = 'rgba(255, 180, 0, 0.9)';

        bigDetectionResults.forEach((r, i) => {
            let shouldHighlight = false;
            if (bigHighlightTarget !== null && bigHighlightTarget === i) shouldHighlight = true;
            if (bigActiveHighlightClass !== null && r.class_name === bigActiveHighlightClass) shouldHighlight = true;

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

    function clearBigStatActiveStates() {
        document.querySelectorAll('#rebuildResult .stat-item').forEach(el => el.classList.remove('active'));
    }

    function clearBigRowActiveStates() {
        const tbody = document.getElementById('resultTable').querySelector('tbody');
        if (tbody) tbody.querySelectorAll('tr').forEach(el => el.classList.remove('active'));
    }

    function setupBigStatClicks() {
        document.querySelectorAll('#rebuildResult .stat-item').forEach(el => {
            const newEl = el.cloneNode(true);
            el.parentNode.replaceChild(newEl, el);
            newEl.addEventListener('click', () => {
                const label = newEl.querySelector('.stat-label')?.textContent || '';
                clearBigRowActiveStates();
                if (label === '成熟蓝莓') {
                    newEl.classList.toggle('active');
                    bigHighlightByClass('RipeBlueBerry');
                } else if (label === '半熟蓝莓') {
                    newEl.classList.toggle('active');
                    bigHighlightByClass('Semi-RipeBlueBerry');
                } else if (label === '未熟蓝莓') {
                    newEl.classList.toggle('active');
                    bigHighlightByClass('UnripeBlueBerry');
                } else {
                    bigActiveHighlightClass = null;
                    bigHighlightTarget = null;
                    drawBigHighlight();
                }
            });
        });
    }
});