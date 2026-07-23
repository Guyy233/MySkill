# MySkill

这是我的 Codex Skills 仓库，用来集中保存常用的可复用技能。

## 仓库结构

每个 skill 始终保留自己的独立目录和 `SKILL.md`。为了便于浏览，相关 skill 可以放进分类目录，但分类目录本身不作为 skill：

- `paper-skills/`：论文阅读、写作和成果展示相关 skills
- 根目录下的其他 skill：通用文档、实验、项目记录和 GitHub 运维能力

每个独立 skill 通常包含：

- `SKILL.md`：skill 主体说明
- `README.md`：面向 GitHub 的简介
- `agents/`：可选，skill 元数据
- `scripts/`：可选，运行脚本
- `references/`：可选，参考资料
- `assets/`：可选，附加资源

## 论文相关 Skills

论文类 skill 统一收录在 [`paper-skills/`](paper-skills/) 中，仍然可以分别安装和调用。

1. [`awesome-ai-research-writing`](paper-skills/awesome-ai-research-writing/)：论文写作总路由器，根据任务选择段落 Prompt 或其他写作 skill。
2. [`20-ml-paper-writing`](paper-skills/20-ml-paper-writing/)：面向 NeurIPS、ICML、ICLR、ACL、AAAI、COLM 和系统会议的完整论文写作与投稿流程。
3. [`论文分析`](paper-skills/论文分析/)：生成逐段、逐式、逐图讲解的中文带读手册，以及正文逐句忠实对应、仅图片附带图解的中英对照译文。
4. [`paper-reading-html`](paper-skills/paper-reading-html/)：把论文整理成保留原文、图和公式的精读型 HTML 页面。
5. [`paper-2-web`](paper-skills/paper-2-web/)：把论文转成项目网站、展示视频或会议海报。

## 文档与内容 Skills

6. [`humanizer`](humanizer/)：识别并去除 AI 写作痕迹，使文本更自然。
7. [`docx`](docx/)：完整处理 `.docx` 创建、编辑、解析、批注和修订痕迹。
8. [`doc`](doc/)：创建或编辑 `.docx`，重点进行渲染和版式质量检查。
9. [`doc-coauthoring`](doc-coauthoring/)：分阶段协作撰写提案、技术规范和结构化文档。
10. [`canvas-design`](canvas-design/)：生成设计导向的静态单页视觉作品（PNG 或 PDF）。

## 实验与项目 Skills

11. [`matlab-run-analyze-fix`](matlab-run-analyze-fix/)：运行 MATLAB、分析结果、检查图像并迭代修复代码。
12. [`student-progress-log`](student-progress-log/)：维护学生项目的中文进展日志和阶段总结。

## GitHub 运维 Skills

13. [`gh-fix-ci`](gh-fix-ci/)：排查和修复 GitHub Actions 中失败的 CI 检查。
14. [`git-push-recover`](git-push-recover/)：在 `git push` 失败后诊断网络与代理问题并重试。
15. [`publish-skill-to-myskill`](publish-skill-to-myskill/)：将本地 skill 整理并上传到本仓库。

## 调用建议

- 需要单独使用某个 skill 时，显式点名它，例如：`使用 $论文分析 分析这篇论文`。
- 需要组合工作流时，可以同时点名多个 skill，或者使用 `awesome-ai-research-writing` 进行论文写作路由。
- 安装时以具体 skill 子目录为单位，不要把 `paper-skills/` 分类目录整体当成一个 skill。

## 维护约定

- 一个 skill 一个独立目录，并保留独立的 `SKILL.md`
- 分类目录只做仓库整理，不放 `SKILL.md`
- 新增或移动 skill 时同步更新根目录和分类目录的 README
- 有脚本、参考资料或模板时放入对应的 `scripts/`、`references/` 或 `assets/`
