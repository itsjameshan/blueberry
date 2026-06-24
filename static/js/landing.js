// 门户脚本：抖音视频墙（官方播放器内嵌）+ 搜索 + 锚点滚动。

// ===== 主页视频：抖音官方播放器内嵌 =====
// vid 由短链解析得到；url 保留作“在抖音打开”兜底。
const DOUYIN_VIDEOS = [
    { vid: '7654835275138436367', url: 'https://v.douyin.com/Q-Aw8biyr5s/', title: '智慧农业实训 · 蓝莓成熟度检测' },
    { vid: '7654793042503275955', url: 'https://v.douyin.com/a0mpTG_lr7I/', title: '电脑实训 · 智能制造系' },
    { vid: '7654793661703632730', url: 'https://v.douyin.com/cRlVCaZnVXI/', title: '电脑实训' },
    { vid: '7654795546972915930', url: 'https://v.douyin.com/N8tBJU9qpa4/', title: '项目实训' },
    { vid: '7654797018267844250', url: 'https://v.douyin.com/F9yVPrtY1Tk/', title: '实训演示' },
    { vid: '7654863401873726821', url: 'https://v.douyin.com/CmHi4VCIOOs/', title: '小程序使用' },
];

function renderVideos() {
    const grid = document.getElementById('video-grid');
    if (!grid) return;
    grid.innerHTML = DOUYIN_VIDEOS.map((v) => `
        <div class="video-card">
            <div class="video-frame">
                <iframe src="https://open.douyin.com/player/video?vid=${v.vid}&autoplay=0"
                        referrerpolicy="unsafe-url"
                        allow="encrypted-media; fullscreen"
                        allowfullscreen frameborder="0" scrolling="no"></iframe>
            </div>
            <div class="video-meta">
                <h4>${v.title}</h4>
                <a href="${v.url}" target="_blank" rel="noopener">在抖音打开 ↗</a>
            </div>
        </div>`).join('');
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
