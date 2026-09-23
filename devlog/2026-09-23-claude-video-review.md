# Claude 视频播放复核

复核模型：Claude Opus 5。范围：实际部署代码及提供的验收记录；Claude 未自行浏览或实播。

## 第一轮（初次混合播放版本，后续已由全部本站播放替代）

## 结论

**基于代码与你提供的验收记录复核（我没有亲自打开浏览器，也没有实播任何视频）。**

没有发现阻塞上线的问题。源默认值与平台核验一一吻合（3、4 号 `douyin`，其余 7 条 `local`），原位切换、重复点击不重置、原生控件不重建播放器这三条在代码上成立且与记录一致。下面是可证的具体缺陷，全部为非阻塞项。

## 发现

**1. 多张卡片可同时播放，音频叠加（建议修复）**
`static/js/landing.js` → `playInline` / `renderVideos`：切换只作用于当前 `frame`，没有任何地方暂停其他卡片。9 张卡片，用户点开第二张时第一张仍在出声（本站 `<video>` 与抖音 iframe 之间也会叠加）。
最小修复：`playInline` 开头遍历 `document.querySelectorAll('.video-frame')`，对不是当前 `frame` 的、且 `dataset.source === 'local'` 的调用 `querySelector('video')?.pause()`；抖音 iframe 跨域无法暂停，可只在本站源之间互斥并接受该限制。

**2. 键盘激活后焦点丢失（可访问性，建议修复）**
`renderVideos` 的 `keydown` → `activate` → `playInline` 中 `frame.removeAttribute('tabindex')`：被移除 tabindex 的正是当前获得焦点的元素，焦点回落到 `body`，键盘用户丢失位置，需从头 Tab 才能摸到播放控件。
最小修复：`playInline` 末尾，若激活前 `document.activeElement === frame`，则对新建的 `video`（`controls` 默认可聚焦）或 `iframe` 调用 `.focus()`。

**3. 切源时旧 `<video>` 未显式停止，且旧 error 回调可能写脏新状态（可选）**
`playInline` 直接 `frame.innerHTML = ...` 覆盖旧元素；同时 `video.addEventListener('error', ...)` 的回调在触发时才 `card.querySelector('.video-status')`，写的是**当时**的状态行。本站→抖音快速切换时，旧元素的迟到错误会把状态改成「视频加载失败，请刷新页面重试」，与正在播放的抖音源矛盾。
最小修复：覆盖前 `const old = frame.querySelector('video'); if (old) { old.pause(); old.removeAttribute('src'); old.load(); }`；error 回调内加 `if (frame.dataset.source !== 'local') return;`。

**4. `referrerpolicy="unsafe-url"` 向第三方发送完整 URL（可选，且有回归风险）**
`playInline` 的 iframe 模板。首页当前无敏感参数，实际影响很低；但该播放器若日后被复用到带 token/查询串的页面就会外泄。可改 `origin`（仍满足抖音的域名白名单校验），**但必须对 3、4 号——目前仅有的两条实播成功项——重新实测**，不重测就不要动。

**5. 卡 1 与卡 5 共用同一封面 `n1.webp`（内容辨识度）**
两条是不同作品，封面与 `poster` 完全相同，视觉上像重复投放。建议为卡 5 单独出封面。

**6. 需人工确认的可能错配（我无法从材料判定）**
卡 3「小程序使用」→ `miniapp-overview.mp4`，卡 7「辰心 · 实训日常」→ `miniapp-walkthrough.mp4`。卡 7 的标题与文件名语义不吻合（`walkthrough` 更像小程序演示），建议核对卡 3/卡 7 的 `src` 是否对调。vid 你已核对过，此处只涉及本站 MP4。

**7. 陈旧注释与死样式（清理项）**
`static/css/landing.css`：`/* 抖音封面卡（点击新标签打开，抖音禁止 iframe 内嵌） */` 与现在的原位播放行为直接矛盾；`.pending-tag`、`.video-meta span` 已无对应 DOM。

**8. 非漏洞但需记一笔**
`renderVideos` / `playInline` 用模板字符串把 `title` 注入 `innerHTML`、`title=`、`aria-label=`。当前 `PROJECT_VIDEOS` 是硬编码常量，不构成 XSS；若以后改为后端或接口下发，必须先转义。

**9. 测试覆盖边界**
`tests/test_landing_videos.js` 只读 `static/` 与 `pa_demo/static/`，不校验线上副本；由于线上 `initSearch` 刻意不同，本地测试无法发现线上视频代码的漂移。同时未覆盖 `renderVideos`、键盘路径与切源竞态（即上面 1–3 条都在测试盲区）。

## 验证限制

- 我只做了代码与你给的验收记录复核，未做浏览器实播、未访问线上站点、未校验文件哈希或时长。
- 「内容对应」我只能证明：9 个 vid 唯一、9 个 src 唯一、9 条 `source` 默认值与你的平台核验结论一致。标题↔实际画面的对应关系代码无法证明，第 6 条需你人工确认。
- 抖音 iframe 的跨域拒播无法被父页读取、因而只能手动备用，以及不承诺播放计入抖音统计——按你已接受的取舍处理，本次未重新讨论。


## 第二轮：全部本站播放

第一轮之后，用户反馈第 3、4 条抖音内嵌也先后失效。当前修正版将全部 9 条默认设为本站播放，去掉页面中的抖音内嵌入口，保留教师账号原作品外链。以下为同一实际 Claude Code 环境的第二轮复核结果。

## 复核结论

已通读最终 JS 与验证脚本（纯阅读，未运行、未浏览）。未发现阻塞问题，修正本身也没有引入新缺陷。

### 修正点验证（逐条对代码）
- **并发出声**：`playInline` 开头 `document.querySelectorAll('.video-frame video').forEach(pause)` + 每个 video 的原生 `play` 监听互斥暂停，覆盖了「用原生控件手动播放第二个」的路径。成立。
- **旧 video 卸载**：`pause → removeAttribute('src') → load()` 再整体替换 `innerHTML`，能中断在途网络请求。用 `removeAttribute` 而非 `src=''` 是对的，后者在部分浏览器会额外抛 error。
- **迟到 error**：`if (frame.querySelector('video') !== video) return;` 在异步 error 触发时 frame 已换内容，守卫生效，不会覆盖新状态；`{ once: true }` 也不影响该守卫（监听只需消费一次）。
- **焦点承接**：`moveFocus` 在替换前取值，替换后 focus 到 `video, iframe`，且模板必有其一，不会 null 崩。
- **重复选择不重建**：`frame.dataset.source === source` 早退；首渲染时 `dataset.source` 为 undefined，不会误早退。

### 当前 source 全为 local 的产品行为
- 9 张卡只渲染「本站播放」按钮 + 「抖音原视频 ↗」外链，页内无任何抖音播放入口，符合你描述的策略；`source === 'douyin'` 的按钮与状态文案分支保留但当前不可达，逻辑上仍自洽，将来改 source 即可启用。
- `card.querySelectorAll('[data-source]')` 会把已被写入 `data-source` 的 **frame 本身**选中；靠 `button.tagName === 'BUTTON'` 过滤掉。当前正确，但这个判断是承重的，别在后续重构里当成冗余删掉。

### 值得知道的两点（非阻塞）
1. **验证脚本的覆盖范围比描述窄**：`grid.querySelectorAll` 返回 `[]`，`renderVideos` 里的 click/keydown/按钮绑定循环整段未执行；`frame.closest()` 的 `querySelectorAll` 也返回 `[]`，所以 `aria-pressed` 同步未被断言。脚本实测到的是「渲染出的 HTML 字符串」+「直接调用 playInline 的行为」，事件接线与 aria-pressed 仍依赖部署后浏览器复测。这不是 bug，只是结论措辞上别把它算进已验证项。
2. **`<video controls autoplay playsinline>` 未加 muted**：点击是用户手势，但 autoplay 属性的起播是异步的，是否被策略拦截取决于浏览器（尤其 iOS Safari），我没有实测。若被拦，表现是停在 poster、controls 可用，而状态文案已经写成「正在本站播放」——可用性不受影响，只是文案略提前。若浏览器复测发现有拦截，最小改法是起播后 `video.play().catch(() => {})` 或按 `playing` 事件再更新文案，现在不必改。

封面/标题沿用、卡3/7不调换、不做样式清理、不恢复抖音内嵌与统计——均未在代码里发现与之矛盾的残留。

**APPROVED**


## 执行与正式站点验收

- 根据第一轮意见修复原生视频互斥播放、键盘焦点承接、替换前媒体释放、旧错误事件隔离，纠正旧 CSS 注释；封面、标题与已核对的内容对应关系保持原样。
- 当前 `20260923-videos2` 正式版全部 9 条使用本站视频，保留教师账号作品外链；本页无抖音 iframe 播放入口。
- 第二轮 APPROVED 后发布并重载，服务器 9 份 MP4 校验通过；公开 JS/CSS 返回内容与经过复核的部署文件一致。
- 本地检查通过：`node tests/test_landing_videos.js`、`node --check /tmp/landing.js`、所改代码差异格式检查。Node 脚本不替代真实浏览器事件验证。
- 由主执行者在未登录抖音的正式首页逐条点击/键盘激活 9 条视频，每条均显示画面并有实际播放进度，无媒体错误；取样进度（秒）：19.76、17.93、21.63、8.35、11.43、4.71、8.68、17.09、4.04。LabelMe 截图显示教程实际画面。
- 浏览器验证包含 Enter/空格封面启动、焦点转移至 VIDEO、本站按钮激活和 aria-pressed 更新、重复选择不重置进度、启动下一条暂停上一条、使用原生控件恢复已暂停视频时暂停其他视频。
- 全部 9 个外链仍为已核对的教师账号作品，9 次主页内启动后 URL 始终为正式首页，视频 iframe 数量为 0。
- 未完整看完所有长视频，未实测 iOS/Safari 或所有外部网络，也不承诺本站播放计入抖音统计。Claude 的结论属于代码/所提供证据复核，实际播放验证由主执行者完成。


## 后续重复封面修正复核

APPROVED — the change is a single `cover` field swap with src/vid/title/source and playback untouched, the new JPEG is verified as the item-1 3s frame, item 5 correctly keeps n1.webp, and image-before-JS-before-template ordering means the worst transient state is a stale-but-valid old cover for cached clients. One thing to actually confirm before flipping the JS: `training-final.jpg` must be present and served (correct MIME, not 404) under *each* of the three static roots — root `static`, `pa_demo/static`, and the live deployment copy — since only the deployed copy's path matters for the online search behavior you're preserving. Also worth a grep that no other markup (preload hint, OG/meta image, or inline fallback) pins item 1 to `n1.webp` outside landing.js, since the template bump only busts the JS.

执行核验：第 1、5 条内容与时长不同，先前错误共用 n1.webp。新 training-final.jpg 来自第 1 条第 3 秒画面；公开图片文件与本地字节一致，正式页面已载入 videos3 并引用 9 个不同封面。HTML/CSS 无第 1 条旧图的其他引用。
