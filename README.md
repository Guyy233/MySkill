# MySkill

这是我的 Codex Skills 仓库，用来集中保存常用的可复用技能。

## 仓库说明

本仓库按“每个 skill 一个文件夹”的方式整理，便于浏览、备份与维护。

每个 skill 文件夹通常包含：
- `SKILL.md`：skill 主体说明
- `README.md`：面向 GitHub 的简介
- `agents/`：可选，skill 元数据
- `scripts/`：可选，运行脚本
- `references/`：可选，参考资料
- `assets/`：可选，附加资源

## 当前收录的 Skills

### 1. `doc`
用于处理 `.docx` 文档，包括创建、编辑、调整格式和检查内容。

### 2. `gh-fix-ci`
用于排查和修复 GitHub Actions 中失败的 CI 检查。

### 3. `matlab-run-analyze-fix`
用于运行 MATLAB 批处理任务，分析结果并协助定位 MATLAB 问题。

### 4. `student-progress-log`
用于维护学生项目的中文进展日志。

### 5. `publish-skill-to-myskill`
用于将本地 skill 整理并上传到 `MySkill` 仓库。

### 6. `git-push-recover`
用于在 `git push` 失败后诊断网络与代理问题并重试上传。

### 7. `awesome-ai-research-writing`
论文写作编排 skill。内置本地 Prompt 全集，并联动外部写作相关 skills。

### 8. `20-ml-paper-writing`
面向 NeurIPS / ICML / ICLR / ACL / AAAI / COLM 的完整论文写作与投稿流程。

### 9. `humanizer`
识别并去除 AI 写作痕迹，使文本更自然、更像人写。

### 10. `docx`
用于 `.docx` 文档创建、编辑、解析与修订痕迹处理。

### 11. `doc-coauthoring`
分阶段文档协作流程：上下文收集、分节起草、读者测试。

### 12. `canvas-design`
用于生成设计导向的单页视觉产物（`.png` / `.pdf`）。

### 13. `paper-2-web`
用于把学术论文整理成交互式网页，也覆盖论文海报和论文视频这类展示材料的生成流程。

## 使用建议

新增 skill 时建议继续保持：
- 一个 skill 一个文件夹
- 保留原始 `SKILL.md`
- 提供可读的 `README.md`
- 有脚本或参考资料时放在对应子目录
