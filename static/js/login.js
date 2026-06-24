(function() {
    var tabBtns = document.querySelectorAll('.tab-btn');
    var loginForm = document.getElementById('loginForm');
    var registerForm = document.getElementById('registerForm');
    var loginError = document.getElementById('loginError');
    var regError = document.getElementById('regError');
    var loginBtn = document.querySelector('#loginForm .btn-primary');
    var regBtn = document.querySelector('#registerForm .btn-primary');

    if (!loginForm || !registerForm) return;

    var loginBtnText = loginBtn ? loginBtn.textContent : '登 录';
    var regBtnText = regBtn ? regBtn.textContent : '注 册';

    tabBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            tabBtns.forEach(function(b) { b.classList.remove('active'); });
            btn.classList.add('active');
            var tab = btn.dataset.tab;
            if (tab === 'login') {
                loginForm.classList.add('active');
                registerForm.classList.remove('active');
            } else {
                registerForm.classList.add('active');
                loginForm.classList.remove('active');
            }
            clearError(loginError);
            clearError(regError);
        });
    });

    function showError(el, msg) {
        el.textContent = msg;
        el.classList.add('show');
    }

    function clearError(el) {
        el.textContent = '';
        el.classList.remove('show');
        el.style.color = '';
    }

    function setBtnLoading(btn, loading) {
        if (!btn) return;
        btn.disabled = loading;
        btn.textContent = loading ? '处理中...' : (btn === loginBtn ? loginBtnText : regBtnText);
    }

    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        var username = document.getElementById('loginUsername').value.trim();
        var password = document.getElementById('loginPassword').value;

        if (!username || !password) {
            showError(loginError, '请输入用户名和密码');
            return;
        }

        clearError(loginError);
        setBtnLoading(loginBtn, true);
        fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username, password: password })
        }).then(function(resp) {
            return resp.json();
        }).then(function(data) {
            if (data.success) {
                var params = new URLSearchParams(window.location.search);
                var next = params.get('next') || '/portal';
                // 仅允许站内相对路径，防止开放重定向
                if (next.charAt(0) !== '/' || next.charAt(1) === '/') next = '/portal';
                window.location.href = next;
            } else {
                showError(loginError, data.message);
                setBtnLoading(loginBtn, false);
            }
        }).catch(function() {
            showError(loginError, '网络错误，请稍后重试');
            setBtnLoading(loginBtn, false);
        });
    });

    registerForm.addEventListener('submit', function(e) {
        e.preventDefault();
        var username = document.getElementById('regUsername').value.trim();
        var password = document.getElementById('regPassword').value;
        var confirm = document.getElementById('regConfirm').value;

        if (!username || !password) {
            showError(regError, '请填写所有字段');
            return;
        }
        if (username.length < 3) {
            showError(regError, '用户名至少3个字符');
            return;
        }
        if (password.length < 6) {
            showError(regError, '密码至少6个字符');
            return;
        }
        if (password !== confirm) {
            showError(regError, '两次密码不一致');
            return;
        }

        clearError(regError);
        setBtnLoading(regBtn, true);
        fetch('/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username, password: password })
        }).then(function(resp) {
            return resp.json();
        }).then(function(data) {
            if (data.success) {
                regError.style.color = '#10B981';
                showError(regError, '注册成功！请切换到登录页面');
                document.getElementById('regUsername').value = '';
                document.getElementById('regPassword').value = '';
                document.getElementById('regConfirm').value = '';
                setBtnLoading(regBtn, false);
            } else {
                showError(regError, data.message);
                setBtnLoading(regBtn, false);
            }
        }).catch(function() {
            showError(regError, '网络错误，请稍后重试');
            setBtnLoading(regBtn, false);
        });
    });
})();