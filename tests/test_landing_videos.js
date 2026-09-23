// Run with: node tests/test_landing_videos.js
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');

for (const directory of ['static', 'pa_demo/static']) {
    const script = fs.readFileSync(path.join(root, directory, 'js/landing.js'), 'utf8');
    const grid = { innerHTML: '', querySelectorAll: () => [] };
    const otherVideo = { paused: false, pause() { this.paused = true; } };
    const document = {
        activeElement: null, addEventListener() {},
        getElementById: () => grid, querySelectorAll: () => [otherVideo]
    };
    const { videos, playInline, renderVideos } = vm.runInNewContext(
        script + '\n({ videos: PROJECT_VIDEOS, playInline, renderVideos });', { document }
    );
    assert.equal(videos.length, 9);
    assert.equal(new Set(videos.map(v => v.vid)).size, 9);
    assert.equal(new Set(videos.map(v => v.src)).size, 9);
    renderVideos();
    assert.equal((grid.innerHTML.match(/<button[^>]*data-source="douyin"/g) || []).length, 0);
    assert.equal((grid.innerHTML.match(/<button[^>]*data-source="local"/g) || []).length, 9);
    assert.equal((grid.innerHTML.match(/https:\/\/www\.douyin\.com\/video\//g) || []).length, 9);
    for (const video of videos) {
        assert.equal(video.source, 'local');
        const asset = path.join(root, directory, video.src.slice('/static/'.length));
        assert.ok(fs.statSync(asset).size > 100000, `Missing or empty video: ${asset}`);
        const status = { textContent: '' };
        let html = '', media;
        const frame = {
            dataset: {}, style: {},
            get innerHTML() { return html; },
            set innerHTML(value) {
                html = value;
                media = {
                    paused: false, src: true, loads: 0, events: {},
                    pause() { this.paused = true; },
                    removeAttribute(name) { if (name === 'src') this.src = false; },
                    load() { this.loads++; },
                    focus() { document.activeElement = this; },
                    addEventListener(name, handler) { this.events[name] = handler; }
                };
            },
            classList: { remove() {} }, removeAttribute() {},
            querySelector(selector) { return selector === 'video' && !html.includes('<video') ? null : media; },
            closest() { return { querySelectorAll: () => [], querySelector: () => status }; }
        };
        document.activeElement = frame;
        playInline(frame, video);
        const firstMedia = media;
        assert.equal(document.activeElement, media);
        otherVideo.paused = false;
        media.events.play();
        assert.equal(otherVideo.paused, true, 'Native control playback must pause other local videos');
        playInline(frame, video, 'douyin');
        assert.equal(firstMedia.paused, true);
        assert.equal(firstMedia.src, false);
        assert.equal(firstMedia.loads, 1);
        assert.ok(frame.innerHTML.includes(`vid=${video.vid}&autoplay=1`));
        assert.ok(frame.innerHTML.includes('<iframe'));
        const douyinStatus = status.textContent;
        firstMedia.events.error();
        assert.equal(status.textContent, douyinStatus, 'Detached video errors must not overwrite the new source status');
        playInline(frame, video, 'local');
        assert.ok(frame.innerHTML.includes(`<video src="${video.src}"`));
        assert.ok(frame.innerHTML.includes('controls autoplay playsinline'));
        assert.ok(!frame.innerHTML.includes('<iframe'));
        const replacement = media;
        firstMedia.events.error();
        assert.equal(status.textContent, '正在本站播放');
        playInline(frame, video, 'local');
        assert.equal(media, replacement);
        media.events.error();
        assert.equal(status.textContent, '视频加载失败，请刷新页面重试。');
    }
}
console.log('Both video walls: 9 local defaults, source links, playback controls, cleanup, focus and error isolation passed.');
