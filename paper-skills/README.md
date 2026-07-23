# 论文相关 Skills

这个目录集中保存论文阅读、论文写作和成果展示相关的 Codex skills。

`paper-skills/` 只是 GitHub 仓库里的分类目录，本身不包含 `SKILL.md`，因此不会被当成一个 skill。每个子目录仍然是可独立安装、独立触发的完整 skill。

## Skill 选择

| Skill | 主要用途 | 典型输入与交付物 |
| --- | --- | --- |
| [`论文分析`](论文分析/) | 论文精读、逐句翻译、原图复原与逐图讲解 | 输入论文 PDF，输出中文带读手册，以及正文无批注解释、仅图片附图解的逐句中英对照 PDF |
| [`paper-reading-html`](paper-reading-html/) | 构建精读型论文网页 | 输入论文 PDF 或提取文本，输出带原文、图、公式和逐段讲解的 HTML |
| [`20-ml-paper-writing`](20-ml-paper-writing/) | 撰写和投稿完整论文 | 输入研究代码、实验结果或论文草稿，输出会议格式的 LaTeX 论文 |
| [`paper-2-web`](paper-2-web/) | 展示和传播论文成果 | 输入论文或 LaTeX 工程，输出网站、视频或会议海报 |
| [`awesome-ai-research-writing`](awesome-ai-research-writing/) | 路由论文写作任务 | 根据写作阶段和交付格式选择 Prompt 或其他写作 skill |

## 分别调用

需要只使用一个 skill 时，显式点名对应名称。CLI 或 IDE 中推荐使用 `$skill-name`：

```text
使用 $论文分析 分析这篇论文，只生成该 skill 规定的两份 PDF。
```

```text
使用 $paper-reading-html 把这篇论文制作成精读网页。
```

```text
使用 $20-ml-paper-writing 根据这个研究仓库起草一篇 ICML 论文。
```

显式点名一个 skill 不会因为它和其他 skill 位于同一个分类目录而自动调用整组。只有在任务同时匹配其他能力、用户同时点名多个 skill，或者使用路由器时，才需要组合调用。

## 安装原则

- 分别安装具体的子 skill 目录，例如 `paper-skills/论文分析`。
- 安装后让每个 skill 继续保持独立目录和独立 `SKILL.md`。
- 不要将 `paper-skills/` 本身安装成一个 skill。
