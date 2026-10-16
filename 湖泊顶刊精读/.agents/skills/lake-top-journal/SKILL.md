---
name: lake-top-journal
description: Run the repeatable 湖泊顶刊精读 workflow: select and verify 5–7 recent papers from specified ecology/lake/model journals, produce a mobile HTML daily deep-read page, update the index and learning memory, and build a three-day synthesis using only the last three daily pages.
---

# 湖泊顶刊精读 Skill

## When to use
Use this skill for requests to update today's lake top-journal reading, find recent ecology/lake/ecological-model papers for the reading site, create a three-day synthesis, or synchronize the learning memory.

## Operating sequence
1. Read the project-level `AGENTS.md`.
2. Read only the needed references under `docs/lake-top-journal/`:
   - `WORKFLOW.md` for end-to-end execution;
   - `RESEARCH_RULES.md` for search/evidence;
   - `WRITING_RULES.md` for IMRaD and sentence extraction;
   - `FIGURE_RULES.md` for figure analysis;
   - `USER_RESEARCH.md` for research transfer;
   - `MEMORY_RULES.md` when updating memory;
   - `QUALITY_GATE.md` before finalizing.
3. Inspect existing pages and templates before creating a new page.
4. Keep the publisher/article page as the source of truth for DOI, date, authors, and abstract whenever available.
5. Never invent missing facts. Use explicit uncertainty markers.
6. Generate HTML, not a Markdown deliverable.
7. Update `index.html` and `学习记忆.html` as required.
8. Run the quality gate mentally or mechanically before reporting completion.

## Daily mode
- Select 5–7 articles from the whitelist and three-month window.
- Prefer a mix of manipulation, field observation, and modelling/ML/remote sensing/Bayesian work.
- Each article gets: metadata, abstract bilingual section, IMRaD breakdown, reusable English sentences, figure-by-figure design analysis, matplotlib reproduction notes.
- End with “今日可抄句型” and “今日作图要点清单”.

## Three-day mode
- Locate exactly the three most recent completed daily pages.
- Treat those pages as the sole numerical source.
- Do not backfill their counts from memory or a new literature search.
- Follow the six sections of “模板 B · 三日总结”.
- Keep an original-article button for every article.
- After writing the summary, update the learning memory and index.

## User research transfer
Always test whether the day's methods can become concrete actions for:
CK/PE/PLA/PBAT/PLPB/PBS/PHA, 7×5, 14 indicators, ANOVA + homogeneous-subset analysis, SPSS-style charts.
Pay special attention to:
- standardized/stratified experimental description;
- compact multi-indicator reporting;
- threshold/nonlinear/tipping interpretations only when evidence supports them;
- boxplot + jitter for 5 replicates;
- matplotlib recreation of publication-quality SPSS-like figures.

## Important anti-hallucination rule
A missing abstract is not permission to synthesize a plausible abstract. A DOI pattern is not evidence of a DOI. A search result is not evidence of a publisher page. A chart style inference must be labeled as an inference.

## Final response
Report what was created/updated, validation performed, and any evidence gaps. Do not claim a file was published or displayed unless the environment/tool actually confirms it.
