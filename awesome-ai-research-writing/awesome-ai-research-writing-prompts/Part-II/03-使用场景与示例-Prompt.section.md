## 使用场景与示例 Prompt

| 使用场景 | 推荐 Skill | 前置输入 | 示例 Prompt | 产出 |
|----------|------------|----------|-------------|----------|
| 从零写一篇论文 | 20-ml-paper-writing | 研究 repo 路径或关键文件（README、results、笔记）+ 目标会议 | 「用这个 repo 帮我写一篇投 NeurIPS 的论文」「根据 results/ 里的实验，起草一篇 ICML 的稿子」 | 一句式贡献确认后，按 Abstract→Introduction→Methods→Experiments→Related Work→Limitations 的完整初稿 |
| 用会议模板开新稿 | 20-ml-paper-writing | 目标会议 + 论文目录存放路径 | 「帮我用 ICLR 2026 模板新建一篇论文」「用 NeurIPS 2025 模板，项目放在当前目录」 | 拷贝完整模板目录并写好标题、作者占位、章节骨架 |
| 加引用 / 写 Related Work | 20-ml-paper-writing | 要引用的主题或关键词（如「RLHF 对齐」），或希望被引用的表述 | 「帮我找并引用 2023 年后 RLHF 的几篇代表作」「Related Work 里需要 cite Vaswani 的 attention，帮我查准并给 BibTeX」 | 经检索/API 核实的 BibTeX；无法核实的标为 [CITATION NEEDED] 或 placeholder，需用户自行核对 |
| 换会议 / 改投别家 | 20-ml-paper-writing | 当前稿子会议格式、目标会议、.tex 或项目路径 | 「这篇稿子要从 NeurIPS 改成 ICML，帮我做格式迁移」「把 main.tex 迁到 ICLR 2026 模板里，页数限制 9 页」 | 新会议模板下的稿子（仅迁移正文与图表）+ 页数、Broader Impact / Limitations 等提醒 |
| 投稿前清单核对 | 20-ml-paper-writing | 无 | 「帮我对一下 NeurIPS 的 paper checklist」「交稿前帮我看一遍 ICML 的要求」 | 按该会议要求的逐项核对（匿名、页数、图表、引用、伦理等），并标出缺失或需修改项 |
| 写 / 改 LaTeX 表格 | 20-ml-paper-writing | 方法名、指标名、数值（或简单列表/CSV） | 「帮我把下面结果做成论文里的表格：Method A 准确率 85.2，Method B 92.1…」「用 booktabs 风格，加 ↑↓ 标注指标方向」 | 可直接粘贴进 .tex 的 `\begin{table}...\end{table}` 代码（含 \toprule/\midrule/\bottomrule、最佳值加粗、数值右对齐等） |
| 图与 caption 规范 | 20-ml-paper-writing | 图或图的描述 | 「帮我写 Figure 1 的 caption，要求包含 xxx」「这张图要符合顶会要求，检查图内标题、色盲友好」 | 符合规范的 caption 文案 + 矢量图/线型等修改建议 |
| 结构化流程写某一节 | doc-coauthoring | 无（进入流程后按提示提供上下文） | 「用 doc coauthoring 流程，我们先写 Introduction」「我想用协作流程写这篇论文的 Methods」 | 三阶段说明（收集上下文→分节起草→读者测试），同意后进入 Stage 1 |
| Stage 1：提供上下文 | doc-coauthoring | 文档类型、读者、目标效果、模板等；repo、主要结论、不确定点、笔记、目标会议（可零散提供） | 「投 ICLR，读者是审稿人」「主要贡献是 X，但 Related Work 还没想好怎么划界」「实验在 results/，README 里有总结」 | 5～10 个澄清问题（如贡献侧重、必放结果），回答后进入 Stage 2 |
| Stage 2：按节起草与修改 | doc-coauthoring | 选定一节；对要点勾选保留/合并/删，对正文用简短指令改 | 「保留 1、4、7，删 3」「这段太长了，压缩成三句」「加一句和 Figure 1 的对应」 | 该节更新版，循环至满意后换下一节 |
| Stage 3：读者测试 | doc-coauthoring | 稿子基本定稿 | 「做一下读者测试」「用新会话试几个读者问题」 | 读者视角下的不清/易误解处 + 修改建议；可按需改稿 |
| 论文概念图 / 示意图 / 框架图 | canvas-design | 图的用途与大致元素（如三阶段 pipeline、方法对比） | 「帮我画一个我们方法的整体框架图，三块：数据、训练、推理」「做一张方法对比的示意图，左边传统方法，右边我们的」 | design philosophy (.md) + 可下载的 .pdf 或 .png，可插入 LaTeX 并配合 20-ml-paper-writing 写 caption |
| 改图的风格或细节 | canvas-design | 对已有图的修改意见 | 「背景改成浅灰」「左边块加大一点」「不要那么多字，只保留标签」 | 按意见调整后的新版图说明，再导出 .pdf/.png 供替换进论文 |
| 去 AI 味 / 润色后终稿检查 | humanizer | 待检查的段落或全文（LaTeX 片段、Word 正文、Markdown 等） | 「这段读起来像 AI 写的，帮我 humanize」「投稿前帮我把 Abstract 和 Introduction 去一下 AI 味」 | 重写后的自然文本 + 可选修改说明；保留原意与语气，减少显著性堆砌、破折号滥用、三点式、AI 高频词等 |
| 用 Word 模板写投稿稿 | docx | 期刊/会议提供的 .docx 投稿模板；你的标题、作者、摘要、各节正文 | 「这是某期刊的 Word 模板，帮我把我的标题、摘要和正文填进去」「在模板里替换作者信息和 Section 1–4 的内容」 | 符合模板格式的 .docx 稿（可先解包再脚本替换占位内容，或按 OOXML 编辑后重新打包） |
| 对 Word 稿做修订建议 | docx | 已写好的 .docx 论文或审稿意见 | 「按 redlining 流程，帮我在文档里标出需要改的几处」「把这段改成 tracked changes：原文删除、新文插入」 | 带修订痕迹的 .docx（仅标记改动处，便于作者接受/拒绝） |

[![Star History Chart](https://api.star-history.com/svg?repos=Leey21/awesome-ai-research-writing&type=Date)](https://star-history.com/#Leey21/awesome-ai-research-writing&Date)
