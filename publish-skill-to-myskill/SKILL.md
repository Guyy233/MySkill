---
name: publish-skill-to-myskill
description: 用于在一个 skill 创建或更新完成后，将其整理并上传到 GitHub 仓库 MySkill。适用于需要把本地 Codex skill 复制到 MySkill 仓库、为 skill 补充 README.md、检查仓库结构、提交并推送到远程仓库的场景。
---

# 上传 Skill 到 MySkill

把已经完成的本地 skill 整理后上传到 GitHub 仓库 `MySkill`。

## 默认目标

- 本地 skill 源目录：`C:\Users\15376\.codex\skills`
- 本地整理仓库：用户当前工作区中的 `MySkill_repo`
- 远程仓库：`https://github.com/Guyy233/MySkill`

如果用户明确指定了其他路径或仓库，以用户要求为准。

## 标准流程

1. 确认目标 skill 已经完成，至少包含：
   - `SKILL.md`
   - 如有需要的 `agents/`、`scripts/`、`references/`、`assets/`
2. 检查 `MySkill_repo` 是否存在；如果不存在，则初始化一个临时本地仓库并连接到 `MySkill` 远程仓库。
3. 将目标 skill 从本地 skills 目录复制到 `MySkill_repo` 中。
4. 在该 skill 文件夹中补一个适合 GitHub 浏览的 `README.md`：
   - 用中文说明 skill 用途
   - 说明适用场景
   - 列出主要文件
5. 如有需要，更新 `MySkill_repo` 根目录 `README.md`，把新 skill 收录进去。
6. 在 `MySkill_repo` 中执行：
   - `git status`
   - `git add`
   - `git commit`
   - `git push`
7. 向用户简要说明：
   - 上传了哪些 skill
   - 最新提交哈希
   - GitHub 仓库地址

## README.md 写法要求

为每个 skill 生成的 `README.md` 应尽量简洁，优先包含：
- skill 名称
- 用途
- 适用场景
- 主要文件

默认使用中文，除非用户明确要求英文。

## 根目录 README 更新要求

如果把新 skill 上传到 `MySkill_repo`，优先同步更新仓库首页：
- 新增该 skill 的简介
- 保持“每个 skill 一个文件夹”的说明
- 让 GitHub 首页可以快速看懂仓库内容

## 使用原则

- 只上传非系统 skill，除非用户明确要求上传 `.system` 下的内容。
- 不要擅自覆盖用户未要求替换的其他 skill。
- 如果目标 skill 尚未完成，应先提示或协助完成 skill 再上传。
- 如果上传过程中遇到网络或权限问题，应优先保留本地整理结果，并向用户说明下一步。

## 常用提交信息

优先使用清晰的英文或中文提交信息，例如：
- `Add new skill: publish-skill-to-myskill`
- `Update skill collection with new publishing workflow`
- `添加新的 skill 上传流程`
- `更新 MySkill 仓库中的 skill 说明`