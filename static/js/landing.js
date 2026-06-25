// 门户脚本：抖音视频墙（真实封面 + 点击内嵌播放）+ 搜索 + 锚点滚动。

// 真实封面已下载到本地；可内嵌的点击后载入抖音官方播放器，
// 个别抖音不允许内嵌的（noEmbed）点击直接跳抖音。
const DOUYIN_VIDEOS = [
    { vid: '7655130673144925474', url: 'https://v.douyin.com/8MfeBapZNgY/', title: '智慧农业 · 期末实训',         cover: '/static/img/covers/n1.webp' },     // 木Lin
    { vid: '7654875270570944755', url: 'https://v.douyin.com/mvp9tZaFMes/', title: '智慧农业 · 编程日常实训',   cover: '/static/img/covers/n2.webp' },     // 木Lin
    { vid: '7654863401873726821', url: 'https://v.douyin.com/CmHi4VCIOOs/', title: '小程序使用',                 cover: '/static/img/covers/cover6.webp' },  // 辰心
    { vid: '7654880126593177521', url: 'https://v.douyin.com/NZqqb0Fr-1k/', title: '使用LabelMe标注蓝莓标准流程', cover: '/static/img/covers/n3.webp' },     // 南柳
    { vid: '7654874947399762907', url: 'https://v.douyin.com/EUYkR6A3ofo/', title: '蓝莓种植 · 智慧农业实训',   cover: '/static/img/covers/n1.webp' },     // 木Lin
    { vid: '7655202866122001690', url: 'https://v.douyin.com/DJQ2U-ti8I8/', title: '蓝莓成熟度检测 · 综合实训', cover: '/static/img/covers/blueberry_detect.webp' }, // 木Lin（重发，已开放内嵌）
];

function playInline(frame, v) {
    if (v.noEmbed) {
        window.open(v.url, '_blank', 'noopener');
        return;
    }
    frame.classList.remove('cover');
    frame.style.backgroundImage = '';
    frame.innerHTML = `<iframe src="https://open.douyin.com/player/video?vid=${v.vid}&autoplay=1"
        referrerpolicy="unsafe-url" allow="autoplay; encrypted-media; fullscreen"
        allowfullscreen frameborder="0" scrolling="no"></iframe>`;
}

function renderVideos() {
    const grid = document.getElementById('video-grid');
    if (!grid) return;
    grid.innerHTML = DOUYIN_VIDEOS.map((v, i) => `
        <div class="video-card">
            <div class="video-frame cover" data-i="${i}" role="button" tabindex="0"
                 style="background-image:url('${v.cover}')">
                <span class="play-badge">▶</span>
            </div>
            <div class="video-meta">
                <h4>${v.title}</h4>
                <a href="${v.url}" target="_blank" rel="noopener">在抖音打开 ↗</a>
            </div>
        </div>`).join('');

    grid.querySelectorAll('.video-frame.cover').forEach((f) => {
        f.addEventListener('click', () => playInline(f, DOUYIN_VIDEOS[+f.dataset.i]));
    });
}

// 站内功能搜索：关键词命中即跳转对应页面。
const SEARCH_TARGETS = [
    { url: '/',        keys: ['主页', '首页', 'home', '门户'] },
    { url: '/about',   keys: ['了解我们', '关于', '我们', 'about', '团队', '简介'] },
    { url: '/tech',    keys: ['技术介绍', '技术', 'tech', '模型', 'yolo', 'onnx', '算法'] },
    { url: '/labelme', keys: ['标注教程', '标注', 'labelme', '教程', '数据集'] },
    { url: '/index',   keys: ['蓝莓检测', '检测', '识别', '成熟度', '单图', '批量', '大图', 'detect'] },
    { url: '/weather', keys: ['天气预警', '天气', '预警', '气象', 'weather', '告警'] },
    { url: '/more',    keys: ['更多', 'more'] },
];

function initSearch() {
    const input = document.getElementById('search-input');
    const btn = document.getElementById('search-btn');
    if (!input || !btn) return;
    const go = () => {
        const q = input.value.trim().toLowerCase();
        if (!q) return;
        const hit = SEARCH_TARGETS.find((t) =>
            t.keys.some((k) => { const kl = k.toLowerCase(); return q.includes(kl) || kl.includes(q); }));
        if (hit) {
            window.location.href = hit.url;
        } else {
            input.setCustomValidity('未找到相关功能，试试：检测 / 天气 / 技术 / 标注');
            input.reportValidity();
        }
    };
    btn.addEventListener('click', go);
    input.addEventListener('keypress', (e) => { if (e.key === 'Enter') go(); });
    input.addEventListener('input', () => input.setCustomValidity(''));
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
