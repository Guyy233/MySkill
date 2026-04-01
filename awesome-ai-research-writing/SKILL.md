---
name: awesome-ai-research-writing
description: 论文写作总路由器。根据用户输入自动选择 Part-I Prompt 或 20-ml-paper-writing/humanizer/docx/doc-coauthoring/canvas-design，并支持多技能串联执行。
---

# Awesome AI Research Writing Router

这个 skill 是一个路由器，不直接替代其他 skill。它的职责是先判断任务类型，再选择最合适的 prompt 或 skill，并给出稳定的执行顺序。

## 1) 路由输入

接收用户自然语言需求后，先抽取四类信号：

- 写作阶段：起稿、改写、润色、终稿、投稿
- 载体格式：LaTeX、Word、图表、整篇论文
- 目标动作：翻译、缩写、扩写、逻辑检查、审稿视角
- 交付形式：文本片段、整稿、`.docx`、图像文件

如果信号冲突，优先级是：交付形式 > 写作阶段 > 目标动作。

## 2) 单路由规则（必须命中一条主路由）

### A. Prompt 直连（Part-I）

当任务是“单段或单节文本处理”，直接调用对应 prompt 文件：

- 中转英 -> `awesome-ai-research-writing-prompts/Part-I/01-中转英.prompt.md`
- 英转中 -> `awesome-ai-research-writing-prompts/Part-I/02-英转中.prompt.md`
- 中转中 -> `.../03-中转中.prompt.md`
- 缩写 -> `.../04-缩写.prompt.md`
- 扩写 -> `.../05-扩写.prompt.md`
- 表达润色（英文论文） -> `.../06-表达润色（英文论文）.prompt.md`
- 表达润色（中文论文） -> `.../07-表达润色（中文论文）.prompt.md`
- 逻辑检查 -> `.../08-逻辑检查.prompt.md`
- 去 AI 味（LaTeX 英文） -> `.../09-去-AI-味（LaTeX-英文）.prompt.md`
- 去 AI 味（Word 中文） -> `.../10-去-AI-味（Word-中文）.prompt.md`
- 论文架构图 -> `.../11-论文架构图.prompt.md`
- 实验绘图推荐 -> `.../12-实验绘图推荐.prompt.md`
- 生成图标题 -> `.../13-生成图的标题.prompt.md`
- 生成表标题 -> `.../14-生成表的标题.prompt.md`
- 实验分析 -> `.../15-实验分析.prompt.md`
- Reviewer 视角整稿审视 -> `.../16-论文整体以-Reviewer-视角进行审视.prompt.md`

### B. 整篇论文工程

命中条件：用户要“从 repo 起稿/改投会议/引用核验/投稿 checklist/整篇结构化交付”。

主调用：`20-ml-paper-writing`

### C. 去 AI 味与风格人写化

命中条件：用户明确要求“去 AI 味、人写感、自然口吻终稿”。

主调用：`humanizer`

### D. Word 文档交付

命中条件：用户要 `.docx` 模板填充、带修订、批注、格式化成 Word 稿。

主调用：`docx`

### E. 协作式分节写作

命中条件：用户要“分阶段协作、按节迭代、读者测试”。

主调用：`doc-coauthoring`

### F. 视觉图与概念图

命中条件：用户要“框架图、示意图、设计化视觉单页”。

主调用：`canvas-design`

## 3) 多路由串联规则（同一请求含多个目标）

当请求涉及多个动作时，固定按下面顺序串联，避免乱序：

1. `20-ml-paper-writing`（整稿骨架与证据）
2. Part-I 对应 prompt（段落级改写/翻译/分析）
3. `humanizer`（终稿去 AI 味）
4. `docx`（Word 模板与修订痕迹）
5. `canvas-design`（图与视觉资产）

如果用户明确指定先后顺序，以用户顺序为准。

## 4) 冲突处理

- 用户说“我要 Word 终稿 + 去 AI 味”：先 `humanizer`，后 `docx`。
- 用户说“整篇论文 + 图表建议”：先 `20-ml-paper-writing`，后 Part-I `实验绘图推荐/图表标题`。
- 用户只给一句模糊需求：优先走 Part-I 最近义 prompt，不空转。

## 5) 调用输出协议

每次执行后都要显式输出以下三行，保证可追踪：

- `主路由: <prompt文件或skill名>`
- `子路由: <若有则列出串联步骤；无则写 none>`
- `调用依据: <命中的关键词或任务信号>`

## 6) 质量与安全约束

- 不伪造引用；无法核验就标记待核验。
- 不篡改实验结论；所有数值必须可追溯到输入。
- 使用 prompt 文件时保持其输出结构，不私自改成别的格式。
- 如果用户指定会议，整稿流程默认交由 `20-ml-paper-writing` 接管。

## 7) 本地索引

- Prompt 索引：`awesome-ai-research-writing-prompts/目录索引.md`
- 来源备份：`awesome-ai-research-writing-prompts/README_source.md`
- Part II 说明：`awesome-ai-research-writing-prompts/Part-II/*.md`
