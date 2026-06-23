(function() {
    var alertsContent = document.getElementById('alertsContent');
    var gardenFilter = document.getElementById('gardenFilter');
    var levelChart = null;
    var gardenChart = null;
    var trendChart = null;

    // 时钟显示
    function updateClock() {
        var clockEl = document.getElementById('navClock');
        if (clockEl) {
            var now = new Date();
            var year = now.getFullYear();
            var month = now.getMonth() + 1;
            var day = now.getDate();
            var hours = String(now.getHours()).padStart(2, '0');
            var minutes = String(now.getMinutes()).padStart(2, '0');
            var seconds = String(now.getSeconds()).padStart(2, '0');
            clockEl.textContent = year + '-' + month + '-' + day + ' ' + hours + ':' + minutes + ':' + seconds;
        }
    }
    updateClock();
    setInterval(updateClock, 1000);

    // 加载果园列表（用于筛选）
    function loadGardenOptions() {
        fetch('/api/gardens')
            .then(function(resp) { return resp.json(); })
            .then(function(data) {
                if (data.success && data.gardens.length > 0) {
                    data.gardens.forEach(function(g) {
                        var option = document.createElement('option');
                        option.value = g.id;
                        option.textContent = g.name;
                        gardenFilter.appendChild(option);
                    });
                }
            })
            .catch(function() {});
    }

    // 加载统计数据
    function loadStats(gardenId) {
        var url = '/api/alerts/stats';
        if (gardenId) {
            url += '?garden_id=' + gardenId;
        }
        fetch(url)
            .then(function(resp) { return resp.json(); })
            .then(function(data) {
                if (data.success) {
                    renderStats(data.stats);
                }
            })
            .catch(function() {});
    }

    // 渲染统计图表
    function renderStats(stats) {
        // 更新统计卡片
        document.getElementById('statTotal').textContent = stats.total || 0;
        var warningCount = 0;
        var infoCount = 0;
        if (stats.by_level) {
            stats.by_level.forEach(function(item) {
                if (item.level === 'warning') warningCount = item.count;
                if (item.level === 'info') infoCount = item.count;
            });
        }
        document.getElementById('statWarning').textContent = warningCount;
        document.getElementById('statInfo').textContent = infoCount;

        // 预警级别分布图
        var levelCtx = document.getElementById('levelChart');
        if (levelChart) levelChart.destroy();
        if (stats.by_level && stats.by_level.length > 0) {
            levelChart = new Chart(levelCtx, {
                type: 'doughnut',
                data: {
                    labels: stats.by_level.map(function(item) {
                        return item.level === 'warning' ? '高级预警' : '提示信息';
                    }),
                    datasets: [{
                        data: stats.by_level.map(function(item) { return item.count; }),
                        backgroundColor: ['#E74C3C', '#3498DB'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { padding: 15, font: { size: 12 } } }
                    }
                }
            });
        }

        // 果园预警排名图
        var gardenCtx = document.getElementById('gardenChart');
        if (gardenChart) gardenChart.destroy();
        if (stats.by_garden && stats.by_garden.length > 0) {
            gardenChart = new Chart(gardenCtx, {
                type: 'bar',
                data: {
                    labels: stats.by_garden.map(function(item) { return item.garden_name; }),
                    datasets: [{
                        label: '预警次数',
                        data: stats.by_garden.map(function(item) { return item.count; }),
                        backgroundColor: '#6C5CE7',
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { beginAtZero: true, ticks: { stepSize: 1 } },
                        y: { grid: { display: false } }
                    }
                }
            });
        }

        // 近30天预警趋势图
        var trendCtx = document.getElementById('trendChart');
        if (trendChart) trendChart.destroy();
        if (stats.by_date && stats.by_date.length > 0) {
            trendChart = new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: stats.by_date.map(function(item) { return item.date; }),
                    datasets: [{
                        label: '预警次数',
                        data: stats.by_date.map(function(item) { return item.count; }),
                        borderColor: '#6C5CE7',
                        backgroundColor: 'rgba(108, 92, 231, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointBackgroundColor: '#6C5CE7'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { grid: { display: false }, ticks: { maxRotation: 45 } },
                        y: { beginAtZero: true, ticks: { stepSize: 1 } }
                    }
                }
            });
        }
    }

    // 加载预警记录
    function loadAlerts(gardenId) {
        alertsContent.innerHTML = '<div class="loading">加载中...</div>';
        var url = '/api/alerts';
        if (gardenId) {
            url += '?garden_id=' + gardenId;
        }
        fetch(url)
            .then(function(resp) { return resp.json(); })
            .then(function(data) {
                if (!data.success) {
                    alertsContent.innerHTML = '<div class="empty-state"><p>加载失败</p></div>';
                    return;
                }
                renderAlerts(data.alerts);
            })
            .catch(function() {
                alertsContent.innerHTML = '<div class="empty-state"><p>网络错误</p></div>';
            });
    }

    function renderAlerts(alerts) {
        if (!alerts || alerts.length === 0) {
            alertsContent.innerHTML = '<div class="empty-state">' +
                '<i class="fas fa-check-circle"></i>' +
                '<p>暂无预警记录</p>' +
            '</div>';
            return;
        }

        var html = '<div class="alert-list">';
        alerts.forEach(function(a) {
            var levelClass = a.level === 'warning' ? 'level-warning' : 'level-info';
            var icon = a.level === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle';
            var iconColor = a.level === 'warning' ? '#E74C3C' : '#3498DB';

            html += '<div class="alert-card ' + levelClass + '">';
            html += '<div class="alert-card-header">';
            html += '<div class="alert-card-title"><i class="fas ' + icon + '" style="color:' + iconColor + ';margin-right:6px;"></i>' + escapeHtml(a.title) + '</div>';
            html += '<span class="alert-card-garden">' + escapeHtml(a.garden_name) + '</span>';
            html += '</div>';
            html += '<div class="alert-card-content">' + escapeHtml(a.content) + '</div>';
            html += '<div class="alert-card-meta">';
            if (a.start_time) {
                html += '<span><i class="fas fa-calendar"></i> 开始: ' + escapeHtml(a.start_time) + '</span>';
            }
            if (a.end_time) {
                html += '<span><i class="fas fa-calendar-check"></i> 结束: ' + escapeHtml(a.end_time) + '</span>';
            }
            html += '<span><i class="fas fa-clock"></i> 记录: ' + escapeHtml(a.created_at) + '</span>';
            html += '</div>';
            html += '</div>';
        });
        html += '</div>';

        alertsContent.innerHTML = html;
    }

    function escapeHtml(text) {
        if (!text) return '';
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // 阈值设置弹窗
    var thresholdModal = document.getElementById('thresholdModal');
    var btnThreshold = document.getElementById('btnThreshold');
    var closeThreshold = document.getElementById('closeThreshold');
    var cancelThreshold = document.getElementById('cancelThreshold');
    var saveThreshold = document.getElementById('saveThreshold');

    function openThresholdModal() {
        // 加载当前阈值
        fetch('/api/user/thresholds')
            .then(function(resp) { return resp.json(); })
            .then(function(data) {
                if (data.success) {
                    var t = data.thresholds;
                    document.getElementById('thTempHigh').value = t.temp_high;
                    document.getElementById('thTempLow').value = t.temp_low;
                    document.getElementById('thHumidityHigh').value = t.humidity_high;
                    document.getElementById('thHumidityLow').value = t.humidity_low;
                    document.getElementById('thWindHigh').value = t.wind_speed_high;
                    document.getElementById('thPrecipHigh').value = t.precipitation_high;
                }
            })
            .catch(function() {});
        thresholdModal.style.display = 'flex';
    }

    function closeThresholdModal() {
        thresholdModal.style.display = 'none';
    }

    btnThreshold.addEventListener('click', openThresholdModal);
    closeThreshold.addEventListener('click', closeThresholdModal);
    cancelThreshold.addEventListener('click', closeThresholdModal);
    thresholdModal.addEventListener('click', function(e) {
        if (e.target === thresholdModal) closeThresholdModal();
    });

    saveThreshold.addEventListener('click', function() {
        var data = {
            temp_high: parseFloat(document.getElementById('thTempHigh').value),
            temp_low: parseFloat(document.getElementById('thTempLow').value),
            humidity_high: parseFloat(document.getElementById('thHumidityHigh').value),
            humidity_low: parseFloat(document.getElementById('thHumidityLow').value),
            wind_speed_high: parseFloat(document.getElementById('thWindHigh').value),
            precipitation_high: parseFloat(document.getElementById('thPrecipHigh').value)
        };

        fetch('/api/user/thresholds', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(function(resp) { return resp.json(); })
        .then(function(result) {
            if (result.success) {
                alert('阈值设置已保存');
                closeThresholdModal();
            } else {
                alert('保存失败: ' + result.message);
            }
        })
        .catch(function() {
            alert('网络错误，请稍后重试');
        });
    });

    // 筛选事件
    gardenFilter.addEventListener('change', function() {
        var val = gardenFilter.value;
        loadAlerts(val ? parseInt(val) : null);
        loadStats(val ? parseInt(val) : null);
    });

    // 初始化
    loadGardenOptions();
    loadAlerts(null);
    loadStats(null);
})();
