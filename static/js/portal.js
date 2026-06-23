(function() {
    // 检查登录状态
    fetch('/api/check_login').then(function(resp) {
        return resp.json();
    }).then(function(data) {
        if (!data.logged_in) {
            window.location.href = '/login';
        }
    }).catch(function() {
        // 网络错误时不做跳转，让用户看到页面
    });

    // 卡片点击动画
    var cards = document.querySelectorAll('.portal-card');
    cards.forEach(function(card) {
        card.addEventListener('mousedown', function() {
            card.style.transform = 'translateY(-2px) scale(0.98)';
        });
        card.addEventListener('mouseup', function() {
            card.style.transform = '';
        });
        card.addEventListener('mouseleave', function() {
            card.style.transform = '';
        });
    });
})();
