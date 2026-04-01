---
name: awesome-ai-research-writing
description: 基于本地 Prompt 库与 5 个外部写作技能的论文写作编排器。用于在中文/英文学术写作、润色、审稿视角检查、图表标题生成与投稿前检查之间做自动路由。
---

# Awesome AI Research Writing Orchestrator

这个 skill 不是单一 prompt，而是一个本地路由层。它把 `awesome-ai-research-writing-prompts` 里的 Prompt 原文和外部 skills 串起来，让同一次对话可以按场景自动切换。

## 本地资源

- Prompt 总库：`awesome-ai-research-writing-prompts/`
- Part I Prompt 原文：`awesome-ai-research-writing-prompts/Part-I/*.prompt.md`
- Part II 技能说明：`awesome-ai-research-writing-prompts/Part-II/*.md`
- 索引：`awesome-ai-research-writing-prompts/目录索引.md`

## 调用总原则

1. 先识别用户意图，再路由到对应 `.prompt.md`。
2. 一旦选中 prompt，优先保留其约束和输出结构，不随意改写格式。
3. 如果任务超出单条 prompt 范围，切换到对应外部 skill 处理。
4. 涉及完整论文工程时，优先调用 `20-ml-paper-writing`，再按需叠加其他 skill。

## Prompt 路由

- 中转英：`Part-I/01-中转英.prompt.md`
- 英转中：`Part-I/02-英转中.prompt.md`
- 中转中：`Part-I/03-中转中.prompt.md`
- 缩写：`Part-I/04-缩写.prompt.md`
- 扩写：`Part-I/05-扩写.prompt.md`
- 表达润色（英文论文）：`Part-I/06-表达润色（英文论文）.prompt.md`
- 表达润色（中文论文）：`Part-I/07-表达润色（中文论文）.prompt.md`
- 逻辑检查：`Part-I/08-逻辑检查.prompt.md`
- 去 AI 味（LaTeX 英文）：`Part-I/09-去-AI-味（LaTeX-英文）.prompt.md`
- 去 AI 味（Word 中文）：`Part-I/10-去-AI-味（Word-中文）.prompt.md`
- 论文架构图：`Part-I/11-论文架构图.prompt.md`
- 实验绘图推荐：`Part-I/12-实验绘图推荐.prompt.md`
- 生成图的标题：`Part-I/13-生成图的标题.prompt.md`
- 生成表的标题：`Part-I/14-生成表的标题.prompt.md`
- 实验分析：`Part-I/15-实验分析.prompt.md`
- Reviewer 视角整稿审视：`Part-I/16-论文整体以-Reviewer-视角进行审视.prompt.md`
- 模型选择参考：`Part-I/17-模型选择.section.md`

## 外部 Skill 联动

- `20-ml-paper-writing`：整篇论文起稿、模板切换、引用核验、投稿 checklist。
- `humanizer`：去 AI 味和语言自然化，适合终稿前通读。
- `docx`：Word 模板填充、`.docx` 编辑、批注与修订痕迹。
- `doc-coauthoring`：按阶段协作写作，先上下文再分节迭代。
- `canvas-design`：概念图、框架图、示意图的视觉设计产出。

## 推荐调用顺序

1. 单段文字任务：直接走 Part I 对应 prompt。
2. 单章节或多轮改写：先用 Part I 草稿，再切 `doc-coauthoring` 打磨。
3. 整篇论文：先 `20-ml-paper-writing`，再用 Part I 做局部增强。
4. 投稿前终检：`逻辑检查` + `humanizer` + `Reviewer 视角整稿审视`。
5. Word 交付：在 `docx` 里做最终模板替换与导出。

## 输出要求

- 明确说明本轮实际调用了哪个 prompt 或 skill。
- 保留原文中的技术名词、实验事实和数值，不编造引用。
- 如果引用无法核验，必须显式标记为待核验，不得伪造。
