## Skills 的配置

下文的演示基于 **OpenSkills** 生态：它提供一套**通用的 Skills 加载/管理方式**，让 Cursor 等 AI coding agent 可以读取并使用以 `SKILL.md` 为核心的技能包。参考链接： [Cursor Agent Skills](https://cursor.com/docs/context/skills)、[openskills](https://github.com/numman-ali/openskills)

### 1) 前置依赖

OpenSkills 通过 npm 分发，并会从 GitHub 拉取 skills 仓库，因此建议准备：
- Node.js 20.6+（含 npm）
- Git

### 2) 安装/运行 OpenSkills

OpenSkills 支持直接用 `npx` 运行：

```bash
npx openskills --version
```

如需多项目复用，也可全局安装：

```bash
npm i -g openskills
openskills --version
```

### 3) 一键安装 Skills

OpenSkills 支持直接从 GitHub 仓库安装 Skills，并自动放入默认目录（一般为项目内 `./.claude/skills/`），Cursor 会自动从 `.claude/skills/`（以及 `.cursor/skills/`）发现 skills 并加载

下面以两个上游仓库为例展示 Skills 的安装方式：

```bash
# research 相关：zechenzhangAGI/AI-research-SKILLs
npx openskills install zechenzhangAGI/AI-research-SKILLs

# Anthropic 官方 skills
npx openskills install anthropics/skills
```

执行后 OpenSkills 会弹出交互式选择（勾选需要的 Skill 即可，默认全部安装）

### 4) 在 Cursor 中查看与使用 Skills

Skills 安装到 `.claude/skills/` 后，Cursor 启动时会自动发现并提供给 Agent 使用。建议按以下方式验证：

- **确认 skills 已安装**：`npx openskills list` 能看到目标 skills
- **在 Cursor Settings 中查看**：打开 Cursor Settings，进入 **Rules, Skills, Subagents**，在 **Skills** 区域可看到已发现的 skills
- **在对话中手动调用**：在 Agent Chat 输入 `/`，搜索 skill 名称并手动插入
- **在对话中自然触发**：直接提出明显对应 skill 的需求（例如“用会议模板开新稿”“写一个 booktabs 表格”），若行为与 Skill 文档一致，则配置生效
 
配置完成后，无需记忆复杂 prompt，在对话中直接说明「要做什么」和「已有信息」即可。例如：提供研究 repo 路径与目标会议，说明「用 ICLR 2026 模板新建一篇论文、项目放在当前目录」。

![Skills 配置与触发示意](images/example.png)

