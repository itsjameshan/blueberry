(function() {
    var gardenList = document.getElementById('gardenList');
    var weatherContent = document.getElementById('weatherContent');
    var alertBanner = document.getElementById('alertBanner');
    var alertText = document.getElementById('alertText');
    var closeAlert = document.getElementById('closeAlert');

    var selectedGardenId = null;

    var stageNames = {
        'dormant': '休眠期',
        'sprouting': '萌芽期',
        'flowering': '花期',
        'fruiting': '果期'
    };

    function loadGardens() {
        fetch('/api/gardens')
            .then(function(resp) { return resp.json(); })
            .then(function(data) {
                if (!data.success || data.gardens.length === 0) {
                    gardenList.innerHTML = '<div class="loading">暂无果园</div>';
                    return;
                }
                renderGardenList(data.gardens);
                // 自动选择第一个果园
                if (data.gardens.length > 0 && !selectedGardenId) {
                    selectGarden(data.gardens[0].id);
                }
                // 检查所有果园的预警并发送邮件
                checkAllGardensAlerts();
            })
            .catch(function() {
                gardenList.innerHTML = '<div class="loading">加载失败</div>';
            });
    }

    function checkAllGardensAlerts() {
        fetch('/api/weather/check-all')
            .then(function(resp) { return resp.json(); })
            .then(function(data) {
                if (data.success && data.sent > 0) {
                    console.log('[预警检查] 已发送 ' + data.sent + ' 封预警邮件');
                }
            })
            .catch(function(err) {
                console.error('[预警检查] 失败:', err);
            });
    }

    function renderGardenList(gardens) {
        gardenList.innerHTML = gardens.map(function(g) {
            return '<div class="garden-item' + (g.id === selectedGardenId ? ' active' : '') + '" data-id="' + g.id + '">' +
                '<div class="garden-item-name">' + escapeHtml(g.name) + '</div>' +
                '<div class="garden-item-location"><i class="fas fa-map-marker-alt"></i> ' + escapeHtml(g.location) + '</div>' +
            '</div>';
        }).join('');

        document.querySelectorAll('.garden-item').forEach(function(item) {
            item.addEventListener('click', function() {
                selectGarden(parseInt(item.dataset.id));
            });
        });
    }

    function selectGarden(gardenId) {
        selectedGardenId = gardenId;
        document.querySelectorAll('.garden-item').forEach(function(item) {
            item.classList.toggle('active', parseInt(item.dataset.id) === gardenId);
        });
        loadWeather(gardenId);
    }

    function loadWeather(gardenId) {
        weatherContent.innerHTML = '<div class="loading">加载气象数据...</div>';
        fetch('/api/weather/' + gardenId)
            .then(function(resp) { return resp.json(); })
            .then(function(data) {
                if (!data.success) {
                    weatherContent.innerHTML = '<div class="empty-state"><p>加载失败</p></div>';
                    return;
                }
                renderWeather(data);
            })
            .catch(function() {
                weatherContent.innerHTML = '<div class="empty-state"><p>网络错误</p></div>';
            });
    }

    function renderWeather(data) {
        var garden = data.garden;
        var weather = data.weather;
        var alerts = data.alerts;

        // 显示预警
        if (alerts && alerts.length > 0) {
            alertText.textContent = alerts[0].title + ': ' + alerts[0].content;
            alertBanner.style.display = 'flex';
        } else {
            alertBanner.style.display = 'none';
        }

        if (!weather) {
            weatherContent.innerHTML = '<div class="empty-state">' +
                '<i class="fas fa-cloud-sun"></i>' +
                '<p>暂无气象数据</p>' +
            '</div>';
            return;
        }

        var html = '<div class="weather-header">' +
            '<h2>' + escapeHtml(garden.name) + '</h2>' +
            '<div class="location"><i class="fas fa-map-marker-alt"></i> ' + escapeHtml(garden.location) + ' · ' + stageNames[garden.growth_stage] + '</div>' +
        '</div>';

        // 数据更新时间
        var fetchedAt = weather.fetched_at || '';
        if (fetchedAt) {
            html += '<div class="fetch-time"><i class="fas fa-clock"></i> 数据更新: ' + escapeHtml(fetchedAt) + '</div>';
        }

        // 实时天气数据
        var realtime = weather.realtime || {};
        
        // 实时天气卡片
        html += '<div class="realtime-weather">';
        html += '<div class="current-temp">' + (realtime.temp || '--') + '°C</div>';
        html += '<div class="current-text">' + escapeHtml(realtime.text || '未知') + '</div>';
        html += '<div class="current-details">';
        html += '<span>体感 ' + (realtime.feelsLike || '--') + '°C</span>';
        html += '<span>湿度 ' + (realtime.humidity || '--') + '%</span>';
        html += '<span>' + escapeHtml(realtime.windDir || '') + ' ' + (realtime.windSpeed || '--') + 'km/h</span>';
        html += '</div>';
        html += '</div>';

        // 气象数据卡片
        html += '<div class="weather-grid">';
        if (realtime.temp !== undefined) {
            html += '<div class="weather-card">' +
                '<div class="weather-card-icon"><i class="fas fa-temperature-half" style="color:#E74C3C;"></i></div>' +
                '<div class="weather-card-value">' + realtime.temp + '°C</div>' +
                '<div class="weather-card-label">温度</div>' +
            '</div>';
        }
        if (realtime.humidity !== undefined) {
            html += '<div class="weather-card">' +
                '<div class="weather-card-icon"><i class="fas fa-droplet" style="color:#3498DB;"></i></div>' +
                '<div class="weather-card-value">' + realtime.humidity + '%</div>' +
                '<div class="weather-card-label">湿度</div>' +
            '</div>';
        }
        if (realtime.windSpeed !== undefined) {
            html += '<div class="weather-card">' +
                '<div class="weather-card-icon"><i class="fas fa-wind" style="color:#95A5A6;"></i></div>' +
                '<div class="weather-card-value">' + realtime.windSpeed + ' km/h</div>' +
                '<div class="weather-card-label">风速</div>' +
            '</div>';
        }
        if (realtime.precipitation !== undefined) {
            html += '<div class="weather-card">' +
                '<div class="weather-card-icon"><i class="fas fa-cloud-rain" style="color:#3498DB;"></i></div>' +
                '<div class="weather-card-value">' + realtime.precipitation + ' mm</div>' +
                '<div class="weather-card-label">降水量</div>' +
            '</div>';
        }
        if (realtime.pressure !== undefined) {
            html += '<div class="weather-card">' +
                '<div class="weather-card-icon"><i class="fas fa-gauge" style="color:#9B59B6;"></i></div>' +
                '<div class="weather-card-value">' + realtime.pressure + ' hPa</div>' +
                '<div class="weather-card-label">气压</div>' +
            '</div>';
        }
        if (realtime.visibility !== undefined) {
            html += '<div class="weather-card">' +
                '<div class="weather-card-icon"><i class="fas fa-eye" style="color:#1ABC9C;"></i></div>' +
                '<div class="weather-card-value">' + realtime.visibility + ' km</div>' +
                '<div class="weather-card-label">能见度</div>' +
            '</div>';
        }
        html += '</div>';

        // 3天预报（跳过今天，显示未来3天：明天、后天、大后天）
        var forecast = weather.forecast || [];
        if (forecast.length > 1) {
            var futureForecast = forecast.slice(1, 4);
            html += '<div class="weather-section">';
            html += '<h3><i class="fas fa-calendar-week"></i> 3天预报</h3>';
            html += '<div class="forecast-list">';
            futureForecast.forEach(function(day) {
                var date = new Date(day.date);
                var month = date.getMonth() + 1;
                var dayNum = date.getDate();
                var dateStr = month + '月' + dayNum + '日';
                html += '<div class="forecast-item">';
                html += '<div class="forecast-date">' + dateStr + '</div>';
                html += '<div class="forecast-text">' + escapeHtml(day.textDay || '') + '</div>';
                html += '<div class="forecast-temp">' + (day.tempMin || '--') + '° / ' + (day.tempMax || '--') + '°</div>';
                html += '</div>';
            });
            html += '</div>';
            html += '</div>';
        }

        // 农业建议
        var advice = data.advice || [];
        html += '<div class="weather-section">' +
            '<h3><i class="fas fa-seedling"></i> 农业建议</h3>';
        if (advice.length > 0) {
            html += '<div class="advice-list">';
            advice.forEach(function(item) {
                var levelClass = 'advice-' + (item.level || 'info');
                var icon = item.level === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle';
                var iconColor = item.level === 'warning' ? '#E74C3C' : '#3498DB';
                html += '<div class="advice-item ' + levelClass + '">' +
                    '<div class="advice-header">' +
                        '<i class="fas ' + icon + '" style="color:' + iconColor + '"></i>' +
                        '<span class="advice-title">' + escapeHtml(item.title) + '</span>' +
                    '</div>' +
                    '<p class="advice-content">' + escapeHtml(item.content) + '</p>' +
                '</div>';
            });
            html += '</div>';
        } else {
            html += '<div class="empty-state" style="min-height:100px;">' +
                '<p>当前气象条件下暂无特别建议</p>' +
            '</div>';
        }
        html += '</div>';

        weatherContent.innerHTML = html;
    }

    function escapeHtml(text) {
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

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

    // 每30分钟自动刷新天气数据
    setInterval(function() {
        if (selectedGardenId) {
            loadWeather(selectedGardenId);
        }
    }, 30 * 60 * 1000);

    // 邮箱设置弹窗
    var emailModal = document.getElementById('emailModal');
    var btnSetEmail = document.getElementById('btnSetEmail');
    var closeEmailModal = document.getElementById('closeEmailModal');
    var cancelEmail = document.getElementById('cancelEmail');
    var saveEmail = document.getElementById('saveEmail');
    var inputEmail = document.getElementById('inputEmail');
    var emailMsg = document.getElementById('emailMsg');

    // 加载当前邮箱
    function loadUserEmail() {
        fetch('/api/user/info')
            .then(function(resp) { return resp.json(); })
            .then(function(data) {
                if (data.success && data.user.email) {
                    inputEmail.value = data.user.email;
                }
            })
            .catch(function() {});
    }

    function openEmailModal() {
        emailMsg.textContent = '';
        emailMsg.className = 'form-msg';
        loadUserEmail();
        emailModal.style.display = 'flex';
    }

    function closeEmailModalFn() {
        emailModal.style.display = 'none';
    }

    function saveEmailFn() {
        var email = inputEmail.value.trim();
        if (!email) {
            emailMsg.textContent = '请输入邮箱地址';
            emailMsg.className = 'form-msg error';
            return;
        }
        fetch('/api/user/email', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email: email})
        })
        .then(function(resp) { return resp.json(); })
        .then(function(data) {
            if (data.success) {
                emailMsg.textContent = '邮箱设置成功';
                emailMsg.className = 'form-msg success';
                setTimeout(closeEmailModalFn, 1500);
            } else {
                emailMsg.textContent = data.message || '设置失败';
                emailMsg.className = 'form-msg error';
            }
        })
        .catch(function() {
            emailMsg.textContent = '网络错误';
            emailMsg.className = 'form-msg error';
        });
    }

    if (btnSetEmail) btnSetEmail.addEventListener('click', openEmailModal);
    if (closeEmailModal) closeEmailModal.addEventListener('click', closeEmailModalFn);
    if (cancelEmail) cancelEmail.addEventListener('click', closeEmailModalFn);
    if (saveEmail) saveEmail.addEventListener('click', saveEmailFn);

    if (closeAlert) {
        closeAlert.addEventListener('click', function() {
            alertBanner.style.display = 'none';
        });
    }

    loadGardens();
})();
