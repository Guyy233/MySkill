---
name: awesome-ai-research-writing
description: 基于 Leey21/awesome-ai-research-writing 的研究论文写作技能，面向机器学习论文的选题、结构化写作、学术表达和审稿反馈迭代。
---

# AI 研究写作 Skill

这个 skill 用来把“研究想法”推进成“可投稿的论文文本”。

## 适用任务

当用户要做以下任务时启用：
- 从研究想法生成论文结构
- 撰写或改写机器学习论文段落
- 强化实验叙事与贡献表达
- 根据审稿意见修改论文并准备 rebuttal

## 输入要求

启动时先收集这些信息：
- 研究问题与核心假设
- 方法要点与关键创新
- 实验设置、主要结果、对比基线
- 目标会议或期刊（如果已确定）
- 当前阶段（大纲、初稿、润色、返修）

如果信息不全，先列缺口，再给最小可执行版本。

## 执行流程

1. 问题与贡献定位：给出一句话问题定义、三句话贡献摘要。
2. 论文骨架搭建：输出标题候选、摘要草稿、章节树。
3. 段落级写作：按“主张 -> 证据 -> 结论”生成可直接粘贴的段落。
4. 学术表达修整：去口语化，压缩冗余，统一术语与符号。
5. 审稿视角复检：从 novelty、soundness、clarity、reproducibility 四维给出风险清单和修订动作。

## 输出规范

默认给出以下结构化结果：
- `Summary`: 本轮改写目标与完成情况
- `Paper Text`: 可直接使用的正文内容
- `Reviewer Risks`: 可能被质疑的点
- `Next Edits`: 下一轮 3-5 个具体动作

## 质量约束

- 不编造实验结果、数据集或引用。
- 结论必须和证据对齐，不能超出实验支持范围。
- 术语第一次出现时给出定义，后续保持一致。
- 公式、图表、表格在文中必须有明确指代。

## 来源说明

本 skill 由以下公开仓库思路整理而成：
- https://github.com/Leey21/awesome-ai-research-writing
- https://github.com/Orchestra-Research/AI-Research-SKILLs/tree/main/20-ml-paper-writing
