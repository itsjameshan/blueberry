(function() {
    var gardenList = document.getElementById('gardenList');
    var addGardenBtn = document.getElementById('addGardenBtn');
    var gardenModal = document.getElementById('gardenModal');
    var closeModal = document.getElementById('closeModal');
    var saveGardenBtn = document.getElementById('saveGardenBtn');
    var modalTitle = document.getElementById('modalTitle');
    var modalError = document.getElementById('modalError');

    var editingId = null;

    var stageNames = {
        'dormant': '休眠期',
        'sprouting': '萌芽期',
        'flowering': '花期',
        'fruiting': '果期'
    };

    function loadGardens() {
        gardenList.innerHTML = '<div class="loading">加载中...</div>';
        fetch('/api/gardens')
            .then(function(resp) { return resp.json(); })
            .then(function(data) {
                if (!data.success) {
                    gardenList.innerHTML = '<div class="empty">加载失败</div>';
                    return;
                }
                if (data.gardens.length === 0) {
                    gardenList.innerHTML = '<div class="empty">暂无果园，点击右上角添加</div>';
                    return;
                }
                renderGardens(data.gardens);
            })
            .catch(function() {
                gardenList.innerHTML = '<div class="empty">网络错误</div>';
            });
    }

    function renderGardens(gardens) {
        gardenList.innerHTML = gardens.map(function(g) {
            return '<div class="garden-card" data-id="' + g.id + '">' +
                '<div class="garden-header">' +
                    '<div>' +
                        '<div class="garden-name">' + escapeHtml(g.name) + '</div>' +
                        '<div class="garden-location"><i class="fas fa-map-marker-alt"></i> ' + escapeHtml(g.location) + '</div>' +
                    '</div>' +
                    '<span class="garden-stage stage-' + g.growth_stage + '">' + stageNames[g.growth_stage] + '</span>' +
                '</div>' +
                '<div class="garden-info">' +
                    '<div class="info-row"><span class="info-label">种植日期</span><span class="info-value">' + (g.plant_date || '未设置') + '</span></div>' +
                    '<div class="info-row"><span class="info-label">创建时间</span><span class="info-value">' + g.created_at + '</span></div>' +
                '</div>' +
                '<div class="garden-actions">' +
                    '<button class="btn-sm btn-edit" data-id="' + g.id + '"><i class="fas fa-edit"></i> 编辑</button>' +
                    '<button class="btn-sm btn-delete" data-id="' + g.id + '"><i class="fas fa-trash"></i> 删除</button>' +
                '</div>' +
            '</div>';
        }).join('');

        document.querySelectorAll('.btn-edit').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var id = parseInt(btn.dataset.id);
                var garden = gardens.find(function(g) { return g.id === id; });
                if (garden) openEditModal(garden);
            });
        });

        document.querySelectorAll('.btn-delete').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var id = parseInt(btn.dataset.id);
                if (confirm('确定要删除该果园吗？')) {
                    deleteGarden(id);
                }
            });
        });
    }

    function openAddModal() {
        editingId = null;
        modalTitle.textContent = '添加果园';
        document.getElementById('gardenName').value = '';
        document.getElementById('gardenLocation').value = '';
        document.getElementById('gardenPlantDate').value = '';
        document.getElementById('gardenStage').value = 'dormant';
        modalError.textContent = '';
        gardenModal.style.display = 'flex';
    }

    function openEditModal(garden) {
        editingId = garden.id;
        modalTitle.textContent = '编辑果园';
        document.getElementById('gardenName').value = garden.name;
        document.getElementById('gardenLocation').value = garden.location;
        document.getElementById('gardenPlantDate').value = garden.plant_date || '';
        document.getElementById('gardenStage').value = garden.growth_stage;
        modalError.textContent = '';
        gardenModal.style.display = 'flex';
    }

    function saveGarden() {
        var name = document.getElementById('gardenName').value.trim();
        var location = document.getElementById('gardenLocation').value.trim();
        var plantDate = document.getElementById('gardenPlantDate').value;
        var stage = document.getElementById('gardenStage').value;

        if (!name || !location) {
            modalError.textContent = '果园名称和地点不能为空';
            return;
        }

        var data = {
            name: name,
            location: location,
            plant_date: plantDate,
            growth_stage: stage
        };

        var url = editingId ? '/api/gardens/' + editingId : '/api/gardens';
        var method = editingId ? 'PUT' : 'POST';

        saveGardenBtn.disabled = true;
        saveGardenBtn.textContent = '保存中...';

        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(function(resp) { return resp.json(); })
        .then(function(result) {
            if (result.success) {
                gardenModal.style.display = 'none';
                loadGardens();
            } else {
                modalError.textContent = result.message;
            }
        })
        .catch(function() {
            modalError.textContent = '网络错误';
        })
        .finally(function() {
            saveGardenBtn.disabled = false;
            saveGardenBtn.textContent = '保存';
        });
    }

    function deleteGarden(id) {
        fetch('/api/gardens/' + id, { method: 'DELETE' })
            .then(function(resp) { return resp.json(); })
            .then(function(result) {
                if (result.success) {
                    loadGardens();
                } else {
                    alert(result.message);
                }
            })
            .catch(function() {
                alert('网络错误');
            });
    }

    function escapeHtml(text) {
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    if (addGardenBtn) {
        addGardenBtn.addEventListener('click', openAddModal);
    }

    if (closeModal) {
        closeModal.addEventListener('click', function() {
            gardenModal.style.display = 'none';
        });
    }

    gardenModal.addEventListener('click', function(e) {
        if (e.target === gardenModal) {
            gardenModal.style.display = 'none';
        }
    });

    if (saveGardenBtn) {
        saveGardenBtn.addEventListener('click', saveGarden);
    }

    loadGardens();
})();
