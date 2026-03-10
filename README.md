# MySkill

这是我的 Codex Skills 仓库，用来集中保存自己常用或已经创建好的 skill。

## 仓库说明

本仓库按“每个 skill 一个文件夹”的方式整理，便于在 GitHub 上浏览、备份和后续维护。

每个 skill 文件夹通常包含：
- `SKILL.md`：skill 的原始说明文件
- `README.md`：面向 GitHub 浏览的简要介绍
- `agents/`：skill 的界面与元数据配置
- `scripts/`：skill 依赖的脚本
- `references/`：可按需读取的参考资料
- `assets/`：图标、模板或其他附加资源

## 当前收录的 Skills

### 1. `doc`
用于处理 `.docx` 文档，包括创建、编辑、调整格式和检查内容。

适合场景：
- 修改 Word 文档内容
- 保留格式进行编辑
- 检查或导出 docx 文档内容

### 2. `gh-fix-ci`
用于排查和修复 GitHub Actions 中失败的 CI 检查。

适合场景：
- PR 检查失败
- 需要查看 GitHub Actions 日志
- 需要定位 CI 报错并拟定修复方案

### 3. `matlab-run-analyze-fix`
用于运行 MATLAB 批处理任务，分析结果，并协助定位和修复 MATLAB 相关问题。

适合场景：
- 运行 MATLAB 脚本或批处理
- 检查 MATLAB 输出日志和图像结果
- 复现实验并修复 MATLAB 代码问题

### 4. `student-progress-log`
用于维护学生项目的中文进展日志。

适合场景：
- 整理当天进展
- 补写历史阶段总结
- 生成周报素材
- 生成 logbook 风格记录
- 更新 `progress.md`
- 在记录后顺手做 Git 提交与 GitHub 备份

## 使用建议

如果以后新增 skill，建议继续保持：
- 一个 skill 一个文件夹
- 保留原始 `SKILL.md`
- 额外补一个便于阅读的 `README.md`
- 有脚本或参考资料时，放在对应子目录中