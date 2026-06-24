// 门户脚本：抖音视频墙 + 搜索框 + 锚点平滑滚动。导航走真实后端路由。

// ===== 主页三个视频：抖音分享链接 =====
// 抖音禁止 iframe 内嵌，故采用封面卡 + 新标签打开。
const DOUYIN_VIDEOS = [
    { url: 'https://v.douyin.com/Q-Aw8biyr5s/', title: '智慧农业实训 · 蓝莓成熟度检测', cover: '/static/BlueBerrytree.jpg' },
    { url: 'https://v.douyin.com/a0mpTG_lr7I/', title: '电脑实训 · 智能制造系',         cover: '/static/RipeBlueBerry.jpg' },
    { url: 'https://v.douyin.com/cRlVCaZnVXI/', title: '电脑实训',                       cover: '/static/Semi-RipeBlueBerry.jpg' },
    { url: 'https://v.douyin.com/N8tBJU9qpa4/', title: '项目实训',                       cover: '/static/UnripeBlueBerry.jpg' },
    { url: 'https://v.douyin.com/F9yVPrtY1Tk/', title: '实训演示',                       cover: '/static/img/detect1.jpg' },
    { url: 'https://v.douyin.com/CmHi4VCIOOs/', title: '小程序使用',                     cover: '/static/img/detect2.jpg' },
];

function renderVideos() {
    const grid = document.getElementById('video-grid');
    if (!grid) return;
    grid.innerHTML = DOUYIN_VIDEOS.map((v) => {
        const pending = !v.url || v.url === '#';
        const attrs = pending ? '' : ' target="_blank" rel="noopener"';
        const href = pending ? 'javascript:void(0)' : v.url;
        const tag = pending ? '<span class="pending-tag">待填链接</span>' : '';
        const hint = pending ? '抖音 · 待替换' : '抖音 · 点击播放';
        return `
            <a class="video-card" href="${href}"${attrs}>
                <div class="video-frame cover" style="background-image:url('${v.cover}')">
                    <span class="play-badge">▶</span>
                    ${tag}
                </div>
                <div class="video-meta"><h4>${v.title}</h4><span>${hint}</span></div>
            </a>`;
    }).join('');
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
