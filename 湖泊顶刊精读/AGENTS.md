# 湖泊顶刊精读：Codex 项目级执行规则

## 1. 项目目标
本目录是“湖泊顶刊精读”长期知识库。Codex 在本目录内工作时，默认目标不是简单找论文，而是把近期顶刊湖泊生态/生态学/生态模型研究转化为：
1. 可核验的每日精读 HTML；
2. 可追踪的三日横向总结；
3. 可累积的句型库、作图规范和研究迁移经验；
4. 可供用户直接阅读的手机网页。

本项目服务于用户的科研训练，尤其关注湖泊生态、沉水植物、生态模型、生态系统服务，同时持续迁移到用户的“可降解地膜 × 烤烟生理生态”实验。

## 2. 文件与职责
- `pages/YYYY-MM-DD.html`：当日 5–7 篇精读。
- `summary/YYYY-MM-DD_三日总结.html`：最近三个每日页的横向复盘，日期取周期最后一天。
- `index.html`：首页、Today 统计、当日文章卡片、历史归档。
- `学习记忆.html`：跨日累计的句型库、作图规范、三日复盘和日志。
- `docs/lake-top-journal/`：稳定规则、模板和用户课题背景。
- `.agents/skills/lake-top-journal/SKILL.md`：可复用的 Codex 工作流。

详细规则按需读取，不要每次无差别加载全部文档；本项目任务发生时至少读取与当前任务直接相关的规则。

## 3. 触发词
以下请求默认进入本项目工作流：
- “更新今天的湖泊顶刊精读”
- “做今天的精读”
- “做三日总结”
- “更新学习记忆”
- “找近期 Nature/Nature Water/Science/PNAS 湖泊论文”
- “把这篇顶刊学会/拆解/迁移到我的课题”

## 4. 每日精读硬约束
检索范围默认：
Nature、Nature Water、Nature Ecology & Evolution、Nature Communications、Nature Climate Change、Nature Sustainability、Nature Geoscience、Science、PNAS；近 3 个月上线；主题为生态学、湖泊生态学、生态模型学。优先覆盖：
- 操纵实验；
- 野外调查；
- 建模，包括机器学习、遥感、贝叶斯。

选 5–7 篇，优先研究问题清晰、方法可迁移、理论升格明显、作图规范成熟的文章。

每篇必须核实：
期刊、卷期、上线日期、作者与通讯作者、DOI、原文链接、OA 状态；OA 时尽可能提供全文及代码/数据仓库。任何无法核实的信息必须明确标记，绝不能猜测。

摘要规则：
- 能公开取得原文时，先逐段英文原文，再逐句中文翻译。
- 公开渠道确实拿不到摘要原文时，只写已核实的结构化概览，并明确标注“⚠️概览”。
- 严禁把模型自己生成的摘要当作原摘要。
- 严禁虚构 DOI、作者、数据、结果、显著性和链接。

每篇还必须完成：
1. IMRaD 写作拆解；
2. 可复用英文句型 + 中文说明；
3. 逐图作图风格拆解；
4. matplotlib 复现要点。

页面顶部必须注明：若章节骨架或写作推断不是原文直接表述，应写“建议点开原文对照”。

## 5. 三日总结硬约束
三日总结的数据来源唯一限定为最近三个已生成的每日精读 HTML。

禁止：
- 重新检索后替代每日页数据；
- 凭记忆补数字；
- 推算不存在的统计量；
- 虚构三日趋势。

必须严格使用“模板 B · 三日总结”的六部分：
一、本期数据面板
二、本期文章一览表
三、写作范式横向归纳
四、作图风格横向归纳
五、可迁移到用户研究的点
六、下期选题建议

文章一览表的每篇文章保留“点开原文”按钮。

## 6. HTML 与视觉规范
所有交付页面均为 HTML，不生成 Markdown 作为最终产物。

移动端最低要求：
- `<meta name="viewport" content="width=device-width, initial-scale=1">`
- 表格、代码块可横向滚动；
- 按钮触摸目标至少 44px；
- 移动端媒体查询字号至少 15px；
- 返回首页使用 sticky 吸顶栏；
- 页面视觉与既有每日页、首页保持一致。

如果已有页面提供了成熟样式，优先复用，不另造一套视觉系统。

## 7. 用户课题迁移
固定背景见 `docs/lake-top-journal/USER_RESEARCH.md`。任何“可迁移到我的研究”部分都要具体落到：
CK / PE / PLA / PBAT / PLPB / PBS / PHA，共 7 组 × 5 重复；
SOD、MDA、CAT、POD、脯氨酸、叶绿素、光合参数、可溶性糖、土壤养分等 14 项指标；
ANOVA + 齐性子集分析；
SPSS 风格学术图表；
同时考虑广东工业大学环境科学与工程学硕（湖泊/水环境方向）备考中的湖泊与水环境方法训练。

## 8. 学习记忆同步
更新 `学习记忆.html` 时：
- 先读取现有文件及其中“五、给执行者的更新规则”；
- 只允许追加与置顶调整；
- 不删除任何已有条目；
- 今天新句型按 A/B/C/D 分类追加；
- 今天新作图要点按 A/B/C/D 分组追加；
- 最新日志插入 `<!-- NEW-LOG-ANCHOR -->` 正下方；
- 跨三期以上、明显最高频的句型可置顶，但不得删除旧条目；
- 同步累计数字和最近更新日期；
- 三日复盘必须包含数据摘要、最高频 3 个 discourse moves、最值得留下的 5 条句型、下一步练习清单。

## 9. 验收原则
完成任何一次任务前，必须检查：
- 所有事实和数字都有来源；
- DOI/链接可核验；
- 摘要没有虚构；
- 每日页和三日总结之间数据一致；
- index 历史归档已更新；
- 学习记忆只追加/置顶；
- HTML 手机端可读；
- 图表规范没有违反禁用项；
- 用户课题迁移是具体行动项而非泛泛建议。

不要为了“看起来完成”而填补缺失证据。宁可标记缺失，也不能杜撰。


## Weekly single-paper journal club
For weekly lake ecology/model papers, follow `docs/lake-top-journal/WEEKLY_JOURNAL_CLUB.md`. In addition to the four-part science presentation, each paper must yield a writing-method analysis, figure-by-figure design analysis, transferable lessons, and a Codex case-study note. Only promote reusable, evidence-backed lessons into stable rules. Do not modify `master`; sync to `lake-top-journal` and verify the commit.
