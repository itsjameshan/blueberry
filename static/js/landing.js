// 门户脚本：抖音视频墙（真实封面 + 点击内嵌播放）+ 搜索 + 锚点滚动。

// 真实封面已下载到本地；可内嵌的点击后载入抖音官方播放器，
// 个别抖音不允许内嵌的（noEmbed）点击直接跳抖音。
const DOUYIN_VIDEOS = [
    { vid: '7655130673144925474', url: 'https://v.douyin.com/8MfeBapZNgY/', title: '智慧农业 · 期末实训',         cover: '/static/img/covers/n1.webp' },     // 木Lin
    { vid: '7654875270570944755', url: 'https://v.douyin.com/mvp9tZaFMes/', title: '智慧农业 · 编程日常实训',   cover: '/static/img/covers/n2.webp' },     // 木Lin
    { vid: '7654863401873726821', url: 'https://v.douyin.com/CmHi4VCIOOs/', title: '小程序使用',                 cover: '/static/img/covers/cover6.webp' },  // 辰心
    { vid: '7654880126593177521', url: 'https://v.douyin.com/NZqqb0Fr-1k/', title: '使用LabelMe标注蓝莓标准流程', cover: '/static/img/covers/n3.webp' },     // 南柳
    { vid: '7654874947399762907', url: 'https://v.douyin.com/EUYkR6A3ofo/', title: '蓝莓种植 · 智慧农业实训',   cover: '/static/img/covers/n1.webp' },     // 木Lin
    { vid: '7654835275138436367', url: 'https://v.douyin.com/Q-Aw8biyr5s/', noEmbed: true, title: '蓝莓成熟度检测 · 综合实训', cover: '/static/img/covers/blueberry_detect.webp' }, // 木Lin（未开放内嵌，点击跳抖音）
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
