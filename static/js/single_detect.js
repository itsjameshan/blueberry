document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('uploadArea');
    const imageInput = document.getElementById('imageInput');
    const preview = document.getElementById('preview');
    const placeholder = uploadArea.querySelector('.upload-placeholder');
    const detectBtn = document.getElementById('detectBtn');
    const confSlider = document.getElementById('confSlider');
    const confValue = document.getElementById('confValue');
    const resultCard = document.getElementById('resultCard');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const resultTableBody = document.getElementById('resultTableBody').querySelector('tbody');
    const noResult = document.getElementById('noResult');
    const resultImg = document.getElementById('resultImg');
    const highlightCanvas = document.getElementById('highlightCanvas');
    const highlightContainer = document.getElementById('highlightContainer');
    let selectedFile = null;
    let detectionResults = [];
    let highlightTarget = null;
    let activeHighlightClass = null;

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
        if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
    });

    imageInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) handleFile(e.target.files[0]);
    });

    function handleFile(file) {
        if (!file.type.match(/^image\/(jpeg|png)$/)) {
            alert('请选择 JPG 或 PNG 格式的图片');
            return;
        }
        selectedFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.src = e.target.result;
            preview.classList.remove('preview-hidden');
            placeholder.style.display = 'none';
            detectBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    }

    confSlider.addEventListener('input', () => {
        confValue.textContent = confSlider.value;
    });

    detectBtn.addEventListener('click', async () => {
        if (!selectedFile) return;
        loadingOverlay.style.display = 'flex';
        resultCard.style.display = 'none';

        const formData = new FormData();
        formData.append('image', selectedFile);
        formData.append('conf', confSlider.value);

        try {
            const resp = await fetch('/api/detect_single', { method: 'POST', body: formData });
            const data = await resp.json();
            if (data.success) {
                renderResult(data);
            } else {
                alert(data.message);
            }
        } catch (err) {
            alert('检测失败，请检查网络连接');
        } finally {
            loadingOverlay.style.display = 'none';
        }
    });

    function renderResult(data) {
        resultCard.style.display = 'block';
        detectionResults = data.results;
        activeHighlightClass = null;
        resultImg.src = data.result_image;
        document.getElementById('ripeCount').textContent = data.stats.RipeBlueBerry;
        document.getElementById('semiCount').textContent = data.stats['Semi-RipeBlueBerry'];
        document.getElementById('unripeCount').textContent = data.stats.UnripeBlueBerry;
        document.getElementById('totalCount').textContent = data.stats.total;

        resultTableBody.innerHTML = '';
        document.getElementById('resultTableBody').style.display = 'table';
        noResult.style.display = 'none';

        if (data.results.length === 0) {
            document.getElementById('resultTableBody').style.display = 'none';
            noResult.style.display = 'block';
        } else {
            data.results.forEach((r, i) => {
                const row = document.createElement('tr');
                row.className = 'result-row';
                row.dataset.index = i;
                row.innerHTML = `
                    <td>${i + 1}</td>
                    <td>${r.class_name}</td>
                    <td>${(r.confidence * 100).toFixed(1)}%</td>
                    <td>(${r.x1}, ${r.y1}, ${r.x2}, ${r.y2})</td>
                `;
                row.addEventListener('click', () => highlightBox(i));
                resultTableBody.appendChild(row);
            });
        }

        setupStatClicks();
        setupCanvasOverlay();
        resultCard.scrollIntoView({ behavior: 'smooth' });
    }

    function setupCanvasOverlay() {
        highlightCanvas.style.display = 'none';
        resultImg.onload = () => {
            syncCanvasSize();
        };
        if (resultImg.complete) syncCanvasSize();
        window.addEventListener('resize', syncCanvasSize);
    }

    function syncCanvasSize() {
        const rect = resultImg.getBoundingClientRect();
        const containerRect = highlightContainer.getBoundingClientRect();
        const offsetX = rect.left - containerRect.left;
        const offsetY = rect.top - containerRect.top;
        highlightCanvas.style.left = offsetX + 'px';
        highlightCanvas.style.top = offsetY + 'px';
        highlightCanvas.width = rect.width;
        highlightCanvas.height = rect.height;
        if (highlightTarget !== null || activeHighlightClass !== null) {
            drawHighlight();
        }
    }

    function getImageScale() {
        const displayedW = resultImg.clientWidth;
        const displayedH = resultImg.clientHeight;
        const naturalW = resultImg.naturalWidth;
        const naturalH = resultImg.naturalHeight;
        if (!naturalW || !naturalH) return { scaleX: 1, scaleY: 1 };
        return { scaleX: displayedW / naturalW, scaleY: displayedH / naturalH };
    }

    function highlightBox(index) {
        if (highlightTarget === index) {
            highlightTarget = null;
        } else {
            highlightTarget = index;
        }
        activeHighlightClass = null;
        clearStatActiveStates();
        highlightTableRow(index);
        drawHighlight();

        const row = resultTableBody.querySelector(`tr[data-index="${index}"]`);
        if (row) row.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function highlightByClass(className) {
        if (activeHighlightClass === className) {
            activeHighlightClass = null;
        } else {
            activeHighlightClass = className;
        }
        highlightTarget = null;
        clearRowActiveStates();
        highlightTableRowsByClass(className);
        drawHighlight();
    }

    function highlightTableRow(index) {
        clearRowActiveStates();
        if (index !== null) {
            const row = resultTableBody.querySelector(`tr[data-index="${index}"]`);
            if (row) row.classList.add('active');
        }
    }

    function highlightTableRowsByClass(className) {
        clearRowActiveStates();
        if (className) {
            detectionResults.forEach((r, i) => {
                if (r.class_name === className) {
                    const row = resultTableBody.querySelector(`tr[data-index="${i}"]`);
                    if (row) row.classList.add('active');
                }
            });
        }
    }

    function drawHighlight() {
        const ctx = highlightCanvas.getContext('2d');
        ctx.clearRect(0, 0, highlightCanvas.width, highlightCanvas.height);

        if (highlightTarget === null && activeHighlightClass === null) {
            highlightCanvas.style.display = 'none';
            return;
        }

        highlightCanvas.style.display = 'block';
        const { scaleX, scaleY } = getImageScale();

        const highlightColor = 'rgba(255, 215, 0, 0.45)';
        const highlightBorder = 'rgba(255, 180, 0, 0.9)';

        detectionResults.forEach((r, i) => {
            let shouldHighlight = false;
            if (highlightTarget !== null && highlightTarget === i) shouldHighlight = true;
            if (activeHighlightClass !== null && r.class_name === activeHighlightClass) shouldHighlight = true;

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

    function clearStatActiveStates() {
        document.querySelectorAll('.stat-item').forEach(el => el.classList.remove('active'));
    }

    function clearRowActiveStates() {
        resultTableBody.querySelectorAll('tr').forEach(el => el.classList.remove('active'));
    }

    function setupStatClicks() {
        document.querySelectorAll('.stat-item').forEach(el => {
            el.addEventListener('click', () => {
                const label = el.querySelector('.stat-label')?.textContent || '';
                clearRowActiveStates();
                if (label === '成熟蓝莓') {
                    el.classList.toggle('active');
                    highlightByClass('RipeBlueBerry');
                } else if (label === '半熟蓝莓') {
                    el.classList.toggle('active');
                    highlightByClass('Semi-RipeBlueBerry');
                } else if (label === '未熟蓝莓') {
                    el.classList.toggle('active');
                    highlightByClass('UnripeBlueBerry');
                } else {
                    activeHighlightClass = null;
                    highlightTarget = null;
                    drawHighlight();
                }
            });
        });
    }
});