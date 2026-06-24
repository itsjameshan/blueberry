document.addEventListener('DOMContentLoaded', function() {
    initSearch();
    initDetectionTabs();
    initSingleDetection();
    initBatchDetection();
    initLargeDetection();
    initRecords();
    checkUrlHash();
});

function initSearch() {
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');

    if (!searchInput || !searchBtn) return;

    searchBtn.addEventListener('click', () => {
        const keyword = searchInput.value.trim();
        if (keyword) {
            alert('正在搜索: ' + keyword);
        } else {
            alert('请输入搜索关键词');
        }
    });

    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchBtn.click();
        }
    });
}

function checkUrlHash() {
    const hash = window.location.hash;
    if (hash === '#batch') {
        switchTab('batch');
    } else if (hash === '#large') {
        switchTab('large');
    } else if (hash === '#records') {
        switchTab('records');
    }
}

function initDetectionTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;
            switchTab(tabId);
        });
    });
}

function switchTab(tabId) {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');
    
    tabBtns.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tabId) {
            btn.classList.add('active');
        }
    });
    
    tabPanels.forEach(panel => {
        panel.classList.remove('active');
        if (panel.id === 'tab-' + tabId) {
            panel.classList.add('active');
        }
    });
}

function initSingleDetection() {
    const uploadArea = document.getElementById('single-upload-area');
    const uploadBtn = document.getElementById('single-upload-btn');
    const fileInput = document.getElementById('single-file-input');

    if (!uploadArea || !uploadBtn || !fileInput) return;

    uploadBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handleSingleFile(file);
    });

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file) handleSingleFile(file);
    });
}

function handleSingleFile(file) {
    if (!file.type.startsWith('image/')) {
        alert('请选择有效的图片文件');
        return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        uploadSingleImage(e.target.result, file);
    };
    reader.readAsDataURL(file);
}

function uploadSingleImage(imageData, file) {
    const uploadArea = document.getElementById('single-upload-area');
    const resultDiv = document.getElementById('single-result');
    const loadingOverlay = document.getElementById('loading-overlay');
    
    uploadArea.style.display = 'none';
    resultDiv.style.display = 'none';
    loadingOverlay.classList.add('active');

    document.getElementById('single-preview-img').src = imageData;

    const apiUrl = document.getElementById('api-url')?.value || 'https://api.blueberry-detection.com/v1';
    
    setTimeout(() => {
        const fakeResult = generateFakeDetectionResult();
        displaySingleResult(fakeResult);
        
        loadingOverlay.classList.remove('active');
        resultDiv.style.display = 'block';
        
        saveRecord('single', imageData, fakeResult);
    }, 2000);
}

function generateFakeDetectionResult() {
    const ripeness = Math.floor(Math.random() * 40) + 60;
    let level, colorClass, statusClass;
    
    if (ripeness >= 85) {
        level = '成熟';
        colorClass = 'ripe';
        statusClass = 'success';
    } else if (ripeness >= 70) {
        level = '半成熟';
        colorClass = 'partial';
        statusClass = 'warning';
    } else {
        level = '未成熟';
        colorClass = 'unripe';
        statusClass = 'danger';
    }

    const qualityLevels = ['A', 'A', 'A', 'B', 'B', 'C'];
    const quality = qualityLevels[Math.floor(Math.random() * qualityLevels.length)];

    return {
        ripeness: ripeness,
        level: level,
        colorClass: colorClass,
        statusClass: statusClass,
        size: (Math.random() * 5 + 10).toFixed(1) + 'mm',
        quality: quality,
        color: (Math.floor(Math.random() * 20) + 75) + '%',
        confidence: (Math.floor(Math.random() * 5) + 95) + '%'
    };
}

function displaySingleResult(result) {
    document.getElementById('single-ripeness').textContent = result.ripeness + '%';
    document.getElementById('single-label').innerHTML = `成熟度判定：<strong>${result.level}</strong>`;
    
    const bar = document.getElementById('single-bar');
    bar.className = 'ripeness-fill ' + result.colorClass;
    bar.style.width = result.ripeness + '%';
    
    document.getElementById('single-size').textContent = result.size;
    document.getElementById('single-quality').textContent = result.quality;
    document.getElementById('single-color').textContent = result.color;
    document.getElementById('single-conf').textContent = result.confidence;
    
    const resultCard = document.querySelector('#single-result .result-card');
    resultCard.className = 'result-card ' + result.statusClass;
}

function resetSingle() {
    const uploadArea = document.getElementById('single-upload-area');
    const resultDiv = document.getElementById('single-result');
    const fileInput = document.getElementById('single-file-input');
    
    uploadArea.style.display = 'block';
    resultDiv.style.display = 'none';
    fileInput.value = '';
}

function initBatchDetection() {
    const addBtn = document.getElementById('batch-add-btn');
    const fileInput = document.getElementById('batch-file-input');
    const grid = document.getElementById('batch-grid');
    const detectBtn = document.getElementById('batch-detect-btn');

    if (!addBtn || !fileInput || !grid) return;

    let selectedFiles = [];

    addBtn.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        
        files.forEach((file, idx) => {
            if (file.type.startsWith('image/')) {
                selectedFiles.push(file);
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    const item = document.createElement('div');
                    item.className = 'batch-item has-image';
                    item.innerHTML = `
                        <img src="${e.target.result}" alt="图片">
                        <button class="remove-btn" onclick="removeBatchItem(this, ${selectedFiles.length - 1})">×</button>
                    `;
                    grid.insertBefore(item, addBtn);
                };
                reader.readAsDataURL(file);
            }
        });

        detectBtn.style.display = selectedFiles.length > 0 ? 'block' : 'none';
    });

    detectBtn.addEventListener('click', () => {
        if (selectedFiles.length === 0) return;

        const resultsBody = document.getElementById('batch-results-body');
        const resultsDiv = document.getElementById('batch-results');
        const loadingOverlay = document.getElementById('loading-overlay');
        
        resultsBody.innerHTML = '';
        resultsDiv.style.display = 'none';
        loadingOverlay.classList.add('active');

        let ripeCount = 0, partialCount = 0, unripeCount = 0;
        const results = [];
        
        selectedFiles.forEach((file, index) => {
            const result = generateFakeDetectionResult();
            results.push({ file, result });
            
            if (result.level === '成熟') ripeCount++;
            else if (result.level === '半成熟') partialCount++;
            else unripeCount++;
        });

        const delay = Math.min(2000 + selectedFiles.length * 500, 5000);
        
        setTimeout(() => {
            results.forEach(({ file, result }) => {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const statusClass = result.level === '成熟' ? 'success' : result.level === '半成熟' ? 'warning' : 'danger';
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><img src="${e.target.result}"></td>
                        <td>${result.ripeness}%</td>
                        <td>${result.quality}</td>
                        <td>${result.color}</td>
                        <td>${result.confidence}</td>
                        <td><span class="status-badge ${statusClass}">${result.level}</span></td>
                    `;
                    resultsBody.appendChild(row);
                };
                reader.readAsDataURL(file);
            });

            document.getElementById('batch-total').textContent = selectedFiles.length;
            document.getElementById('batch-ripe').textContent = ripeCount;
            document.getElementById('batch-partial').textContent = partialCount;
            document.getElementById('batch-unripe').textContent = unripeCount;
            
            loadingOverlay.classList.remove('active');
            resultsDiv.style.display = 'block';
        }, delay);
    });
}

function removeBatchItem(btn, index) {
    btn.parentElement.remove();
    selectedFiles.splice(index, 1);
    
    const detectBtn = document.getElementById('batch-detect-btn');
    detectBtn.style.display = selectedFiles.length > 0 ? 'block' : 'none';
    
    document.getElementById('batch-results').style.display = 'none';
}

function initLargeDetection() {
    const uploadArea = document.getElementById('large-upload-area');
    const uploadBtn = document.getElementById('large-upload-btn');
    const fileInput = document.getElementById('large-file-input');

    if (!uploadArea || !uploadBtn || !fileInput) return;

    uploadBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handleLargeFile(file);
    });

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file) handleLargeFile(file);
    });
}

function handleLargeFile(file) {
    if (!file.type.startsWith('image/')) {
        alert('请选择有效的图片文件');
        return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        uploadLargeImage(e.target.result);
    };
    reader.readAsDataURL(file);
}

function uploadLargeImage(imageData) {
    const uploadArea = document.getElementById('large-upload-area');
    const resultDiv = document.getElementById('large-result');
    const loadingOverlay = document.getElementById('loading-overlay');
    
    uploadArea.style.display = 'none';
    resultDiv.style.display = 'none';
    loadingOverlay.classList.add('active');

    setTimeout(() => {
        displayLargeResult(imageData);
        
        loadingOverlay.classList.remove('active');
        resultDiv.style.display = 'block';
    }, 2500);
}

function displayLargeResult(imageSrc) {
    const previewDiv = document.getElementById('large-preview');
    previewDiv.innerHTML = `<img src="${imageSrc}" id="large-image">`;

    const markers = generateFakeMarkers();
    const image = document.getElementById('large-image');
    
    image.onload = function() {
        const imgWidth = image.offsetWidth;
        const imgHeight = image.offsetHeight;
        
        markers.forEach((marker) => {
            const markerEl = document.createElement('div');
            markerEl.className = 'detection-marker';
            markerEl.style.left = (marker.x * imgWidth / 100) + 'px';
            markerEl.style.top = (marker.y * imgHeight / 100) + 'px';
            markerEl.style.width = (marker.width * imgWidth / 100) + 'px';
            markerEl.style.height = (marker.height * imgHeight / 100) + 'px';
            markerEl.style.borderColor = marker.color;
            
            const label = document.createElement('div');
            label.className = 'marker-label';
            label.textContent = `${marker.ripeness}% - ${marker.level}`;
            markerEl.appendChild(label);
            
            previewDiv.appendChild(markerEl);
        });

        document.getElementById('large-count').textContent = markers.length;
        document.getElementById('large-ripe').textContent = markers.filter(m => m.level === '成熟').length;
        document.getElementById('large-partial').textContent = markers.filter(m => m.level === '半成熟').length;
        document.getElementById('large-unripe').textContent = markers.filter(m => m.level === '未成熟').length;
        
        const avgRipeness = Math.round(markers.reduce((sum, m) => sum + m.ripeness, 0) / markers.length);
        document.getElementById('large-avg').textContent = avgRipeness + '%';
    };
}

function generateFakeMarkers() {
    const count = Math.floor(Math.random() * 5) + 3;
    const markers = [];
    
    for (let i = 0; i < count; i++) {
        const ripeness = Math.floor(Math.random() * 40) + 60;
        let level, color;
        
        if (ripeness >= 85) {
            level = '成熟';
            color = '#10B981';
        } else if (ripeness >= 70) {
            level = '半成熟';
            color = '#F59E0B';
        } else {
            level = '未成熟';
            color = '#EF4444';
        }
        
        markers.push({
            x: 15 + Math.random() * 70,
            y: 15 + Math.random() * 70,
            width: 8 + Math.random() * 5,
            height: 8 + Math.random() * 5,
            ripeness: ripeness,
            level: level,
            color: color
        });
    }
    
    return markers;
}

function resetLarge() {
    const uploadArea = document.getElementById('large-upload-area');
    const resultDiv = document.getElementById('large-result');
    const fileInput = document.getElementById('large-file-input');
    
    uploadArea.style.display = 'block';
    resultDiv.style.display = 'none';
    fileInput.value = '';
}

function initRecords() {
    const timeFilter = document.getElementById('records-time-filter');
    const typeFilter = document.getElementById('records-type-filter');
    const keywordInput = document.getElementById('records-keyword');
    const recordsBody = document.getElementById('records-body');

    if (!recordsBody) return;

    const mockRecords = [
        { id: '#D20240623001', type: 'single', ripeness: 85, level: '成熟', time: '2024-06-23 14:30:25' },
        { id: '#D20240623002', type: 'batch', ripeness: 78, level: '半成熟', time: '2024-06-23 14:25:10' },
        { id: '#D20240623003', type: 'large', ripeness: 92, level: '成熟', time: '2024-06-23 13:45:33' },
        { id: '#D20240622001', type: 'single', ripeness: 65, level: '未成熟', time: '2024-06-22 16:20:15' },
        { id: '#D20240622002', type: 'batch', ripeness: 88, level: '成熟', time: '2024-06-22 15:10:45' },
        { id: '#D20240621001', type: 'single', ripeness: 72, level: '半成熟', time: '2024-06-21 10:30:00' },
    ];

    function renderRecords(filteredRecords) {
        if (filteredRecords.length === 0) {
            recordsBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #9CA3AF; padding: 40px;">暂无检测记录</td></tr>';
            return;
        }

        recordsBody.innerHTML = filteredRecords.map(record => {
            const typeText = record.type === 'single' ? '单图检测' : record.type === 'batch' ? '批量检测' : '大图检测';
            const statusClass = record.level === '成熟' ? 'success' : record.level === '半成熟' ? 'warning' : 'danger';
            
            return `
                <tr>
                    <td>${record.id}</td>
                    <td><img src="https://via.placeholder.com/60/2E5BFF/FFFFFF?text=蓝莓"></td>
                    <td>${typeText}</td>
                    <td>${record.ripeness}%</td>
                    <td><span class="status-badge ${statusClass}">${record.level}</span></td>
                    <td>${record.time}</td>
                    <td><button class="btn-view" onclick="viewRecord('${record.id}')">查看详情</button></td>
                </tr>
            `;
        }).join('');
    }

    function filterRecords() {
        const timeValue = timeFilter?.value || 'all';
        const typeValue = typeFilter?.value || 'all';
        const keyword = (keywordInput?.value || '').toLowerCase();

        let filtered = [...mockRecords];

        if (timeValue !== 'all') {
            const today = new Date().toISOString().split('T')[0];
            filtered = filtered.filter(r => r.time.includes('2024-06-23'));
        }

        if (typeValue !== 'all') {
            filtered = filtered.filter(r => r.type === typeValue);
        }

        if (keyword) {
            filtered = filtered.filter(r => 
                r.id.toLowerCase().includes(keyword) || 
                r.level.includes(keyword)
            );
        }

        renderRecords(filtered);
    }

    timeFilter?.addEventListener('change', filterRecords);
    typeFilter?.addEventListener('change', filterRecords);
    keywordInput?.addEventListener('input', filterRecords);

    renderRecords(mockRecords);
}

function viewRecord(id) {
    alert('查看检测记录详情: ' + id);
}

function saveRecord(type, image, result) {
    const records = JSON.parse(localStorage.getItem('detectionRecords') || '[]');
    records.unshift({
        id: '#D' + Date.now(),
        type: type,
        image: image.substring(0, 100) + '...',
        ripeness: result.ripeness,
        level: result.level,
        time: new Date().toLocaleString('zh-CN')
    });
    localStorage.setItem('detectionRecords', JSON.stringify(records));
}

function startDetection() {
    const resultSection = document.getElementById('result-section');
    if (resultSection) {
        resultSection.classList.add('active');
    }
}

function clearResult() {
    const resultSection = document.getElementById('result-section');
    if (resultSection) {
        resultSection.classList.remove('active');
    }
}

function playVideo() {
    alert('视频播放功能正在开发中...');
}

function initContactForm() {
    const form = document.getElementById('contact-form');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            alert('感谢您的留言！我们会尽快回复您。');
            form.reset();
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initContactForm();
});

window.switchTab = switchTab;
window.resetSingle = resetSingle;
window.resetLarge = resetLarge;
window.viewRecord = viewRecord;
window.removeBatchItem = removeBatchItem;
window.startDetection = startDetection;
window.clearResult = clearResult;
window.playVideo = playVideo;