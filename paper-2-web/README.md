# paper-2-web

这个 skill 用来把学术论文整理成 **交互式论文网页**，也支持扩展到 **海报** 和 **视频** 场景。它来自上游仓库 `Sologa/codex-pipeline` 中的 `paper-2-web` 目录，我这里保留了原始 `SKILL.md` 和 `references/` 文档，再补了一份适合 GitHub 浏览的中文说明。

## 用途

- 把 LaTeX 论文或 PDF 论文转成网页
- 为论文生成展示页面、会议海报、视频讲解材料
- 给预印本、实验室主页、项目主页补一个可读性更强的网页入口

## 适用场景

- 论文投稿后，想做一个配套展示页
- 需要把论文内容整理成会议材料
- 想把 PDF 论文转成更容易传播的网页形式
- 需要把一篇或多篇论文批量整理成线上展示内容

## 主要文件

- `SKILL.md`：原始 skill 主说明
- `references/installation.md`：安装与环境配置
- `references/paper2web.md`：论文网页生成说明
- `references/paper2video.md`：论文视频生成说明
- `references/paper2poster.md`：论文海报生成说明
- `references/usage_examples.md`：完整使用示例

## 使用方式

这个 skill 本身主要提供工作流说明。实际生成网页、海报、视频时，核心依赖是 **Paper2All**。

典型流程如下：

1. 先安装 `Paper2All`
2. 准备论文输入目录，放入 `main.tex` 或 `paper.pdf`
3. 按 `SKILL.md` 或 `references/` 里的命令运行 `pipeline_all.py` 或 `pipeline_light.py`
4. 在输出目录中查看生成结果，例如 `website/index.html`

常见命令示例：

```bash
python pipeline_all.py \
  --input-dir "path/to/paper" \
  --output-dir "path/to/output" \
  --model-choice 1 \
  --generate-website
```

## 呈现结果

网页部分通常会输出到：

```text
output/paper_name/website/
```

其中常见文件包括：

- `index.html`
- `styles.css`
- `script.js`
- `assets/`

## 上游来源

- 上游 skill 仓库：[Sologa/codex-pipeline](https://github.com/Sologa/codex-pipeline)
- 底层项目：[YuhangChen1/Paper2All](https://github.com/YuhangChen1/Paper2All)
