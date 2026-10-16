# 湖泊顶刊精读标准工作流

## A. 每日精读

### Step 0 — 发现当前状态
1. 检查 `index.html`、`pages/`、`summary/`、`学习记忆.html` 是否存在。
2. 找出最近每日页，记录已读论文，避免重复。
3. 如已有 about/template 文件，优先以项目内模板为准。

### Step 1 — 检索
限定期刊：
Nature / Nature Water / Nature Ecology & Evolution / Nature Communications / Nature Climate Change / Nature Sustainability / Nature Geoscience / Science / PNAS。

限定时间：近 3 个月上线。

限定主题：生态学 + 湖泊生态学 + 生态模型学。

优先形成 5–7 篇组合，尽量同时覆盖：
- 操纵实验；
- 野外调查；
- 建模/机器学习/遥感/贝叶斯。

### Step 2 — 证据核验
每篇建立最小证据记录：
- title
- journal
- volume/issue（如有）
- online date
- authors
- corresponding author（若公开）
- DOI
- publisher article page
- OA status
- full-text page（OA 时）
- code/data repository（OA 且公开时）
- abstract source

证据等级：
A = 出版商正文或正式元数据；
B = DOI/期刊页面之外的可信公开数据库；
C = 搜索结果摘要或二手信息，仅用于发现，不能作为关键事实唯一依据。

关键事实必须尽量回到 A 级来源。

### Step 3 — 文章筛选
不是按“期刊名气”机械选择。优先：
1. 与湖泊/生态模型直接相关；
2. 方法具有迁移价值；
3. 研究设计清晰；
4. 理论升格明确；
5. 图表具有可复刻价值；
6. 能帮助用户提升本科论文/后续硕士研究能力。

### Step 4 — 每篇精读结构
固定四部分：
1. 基本信息表；
2. 摘要中英对照；
3. IMRaD 章节写作拆解；
4. 作图风格拆解。

IMRaD 要回答：
- Introduction：漏斗如何收窄，缺口在哪里，为什么必须现在研究？
- Methods：如何证明设计可靠、样本可比、因果或关联边界在哪里？
- Results：结果如何递进，而不是把图表逐张复述？
- Discussion：机制解释 → 与文献对话 → 例外/局限 → 管理启示/理论意义。

### Step 5 — 写作句型
按：
A 开场与缺口
B 设计与方法辩护
C 结果表达
D 讨论与理论升格

每条：
英文句型｜中文解释｜来源（DayN 篇X）。

重复句型不重复收录；如果新版本明显更强，可并列记录。

### Step 6 — 作图
每图说明：
- 图型；
- 变量关系；
- 面板逻辑；
- 为什么这样画；
- 如何用 matplotlib 复现。

默认规范：
- panel a/b/c 标签；
- sharex/sharey；
- diverging 色标需要 center=0；
- 禁 jet；
- 显著性优先符号/字母，不依赖颜色；
- 回归线必须有 95% CI；
- 箱线图可叠加 jitter 原始点；
- ROC 必须有 diagonal；
- 无衬线字体 7–8 pt；
- dpi=300 或矢量导出；
- Nature 单栏约 (3.5, 2.6)，双栏约 (7.2, 4.0) inch。

### Step 7 — 生成每日 HTML
先建立内容，再套用既有页面样式。不要因为追求视觉而牺牲学术信息密度。

### Step 8 — 更新首页
- Today 统计；
- 当日文章卡片；
- “点开原文”；
- 历史归档。

### Step 9 — 更新学习记忆
遵循 `MEMORY_RULES.md`。

### Step 10 — Quality Gate
完成前运行 `QUALITY_GATE.md` 中所有检查。

---

## B. 三日总结

1. 找到最近三个已完成每日页。
2. 只读取这三个页面中的数据。
3. 先建立数据表，再写文字。
4. 严格按照模板 B 六部分。
5. 统计期刊、研究类型、中国作者/中国湖泊、OA 等。
6. 做 discourse move 频次。
7. 汇总句型和作图规范。
8. 对照用户课题给具体迁移动作。
9. 给出 3 条下期选题建议。
10. 写入 `summary/YYYY-MM-DD_三日总结.html`。
11. 更新首页归档。
12. 更新学习记忆中的“三日复盘”。
