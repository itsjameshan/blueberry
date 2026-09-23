// 门户视频：抖音播放与本站备用，均在原卡片内切换。
const PROJECT_VIDEOS = [
    { vid: '7688613759690359930', src: '/static/videos/training-final.mp4', title: '智慧农业 · 期末实训', cover: '/static/img/covers/training-final.jpg', source: 'local' },
    { vid: '7688625790132977649', src: '/static/videos/coding-practice.mp4', title: '智慧农业 · 编程日常实训', cover: '/static/img/covers/n2.webp', source: 'local' },
    { vid: '7688627184253026033', src: '/static/videos/miniapp-overview.mp4', title: '小程序使用', cover: '/static/img/covers/cover6.webp', source: 'local' },
    { vid: '7688627587128764529', src: '/static/videos/labelme-tutorial.mp4', title: '使用LabelMe标注蓝莓标准流程', cover: '/static/img/covers/n3.webp', source: 'local' },
    { vid: '7688628453709991089', src: '/static/videos/training-daily.mp4', title: '蓝莓种植 · 智慧农业实训', cover: '/static/img/covers/n1.webp', source: 'local' },
    { vid: '7688629053854802801', src: '/static/videos/blueberry-detection.mp4', title: '蓝莓成熟度检测 · 综合实训', cover: '/static/img/covers/blueberry_detect.webp', source: 'local' },
    { vid: '7688634618685829553', src: '/static/videos/miniapp-walkthrough.mp4', title: '辰心 · 实训日常', cover: '/static/img/covers/chenxin.webp', source: 'local' },
    { vid: '7688636612057537445', src: '/static/videos/codex-presentation.mp4', title: 'Codex 讲解 · 智慧农业实训', cover: '/static/img/covers/codex.webp', source: 'local' },
    { vid: '7688634963625137393', src: '/static/videos/project-summary.mp4', title: '蓝莓成熟度检测 · 总结汇报', cover: '/static/img/covers/summary.webp', source: 'local' },
];

function playInline(frame, v, source = v.source) {
    if (frame.dataset.source === source) return;
    const moveFocus = document.activeElement === frame;
    document.querySelectorAll('.video-frame video').forEach((other) => other.pause());
    const previous = frame.querySelector('video');
    if (previous) {
        previous.pause();
        previous.removeAttribute('src');
        previous.load();
    }
    frame.dataset.source = source;
    frame.classList.remove('cover');
    frame.style.backgroundImage = '';
    frame.removeAttribute('role');
    frame.removeAttribute('tabindex');
    if (source === 'douyin') {
        frame.innerHTML = `<iframe src="https://open.douyin.com/player/video?vid=${v.vid}&autoplay=1"
            title="${v.title}" referrerpolicy="unsafe-url" allow="autoplay; encrypted-media; fullscreen"
            allowfullscreen frameborder="0" scrolling="no"></iframe>`;
    } else {
        frame.innerHTML = `<video src="${v.src}" poster="${v.cover}" aria-label="${v.title}"
            controls autoplay playsinline preload="metadata">浏览器暂不支持视频播放。</video>`;
    }
    const card = frame.closest('.video-card');
    card.querySelectorAll('[data-source]').forEach((button) => {
        if (button.tagName === 'BUTTON') button.setAttribute('aria-pressed', String(button.dataset.source === source));
    });
    card.querySelector('.video-status').textContent = source === 'douyin'
        ? '正在使用抖音播放器；若无法播放，可点击“本站备用”。' : '正在本站播放';
    const video = frame.querySelector('video');
    if (video) {
        video.addEventListener('play', () => {
            document.querySelectorAll('.video-frame video').forEach((other) => {
                if (other !== video) other.pause();
            });
        });
        video.addEventListener('error', () => {
            if (frame.querySelector('video') !== video) return;
            card.querySelector('.video-status').textContent = '视频加载失败，请刷新页面重试。';
        }, { once: true });
    }
    if (moveFocus) frame.querySelector('video, iframe').focus();
}

function renderVideos() {
    const grid = document.getElementById('video-grid');
    if (!grid) return;
    grid.innerHTML = PROJECT_VIDEOS.map((v, i) => `
        <div class="video-card">
            <div class="video-frame cover" data-i="${i}" role="button" tabindex="0" aria-label="播放：${v.title}"
                 style="background-image:url('${v.cover}')">
                <span class="play-badge">▶</span>
            </div>
            <div class="video-meta">
                <h4>${v.title}</h4>
                <div class="video-actions">
                    ${v.source === 'douyin' ? '<button type="button" data-source="douyin" aria-pressed="false">抖音播放</button>' : ''}
                    <button type="button" data-source="local" aria-pressed="false">${v.source === 'douyin' ? '本站备用' : '本站播放'}</button>
                    <a href="https://www.douyin.com/video/${v.vid}" target="_blank" rel="noopener">抖音原视频 ↗</a>
                </div>
                <p class="video-status" aria-live="polite">点击封面播放</p>
            </div>
        </div>`).join('');

    grid.querySelectorAll('.video-card').forEach((card, i) => {
        const frame = card.querySelector('.video-frame');
        const activate = () => {
            if (frame.classList.contains('cover')) playInline(frame, PROJECT_VIDEOS[i]);
        };
        frame.addEventListener('click', activate);
        frame.addEventListener('keydown', (event) => {
            if (frame.classList.contains('cover') && (event.key === 'Enter' || event.key === ' ')) {
                event.preventDefault();
                activate();
            }
        });
        card.querySelectorAll('button[data-source]').forEach((button) => {
            button.addEventListener('click', () => playInline(frame, PROJECT_VIDEOS[i], button.dataset.source));
        });
    });
}

function initSearch() {
    const input = document.getElementById('search-input');
    const btn = document.getElementById('search-btn');
    if (!input || !btn) return;
    const go = () => { if (input.value.trim()) window.location.href = '/index'; };
    btn.addEventListener('click', go);
    input.addEventListener('keypress', (e) => { if (e.key === 'Enter') go(); });
}

function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach((a) => {
        a.addEventListener('click', (e) => {
            const target = document.querySelector(a.getAttribute('href'));
            if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    renderVideos();
    initSearch();
    initSmoothScroll();
});
