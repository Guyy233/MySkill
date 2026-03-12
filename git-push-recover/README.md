# git-push-recover

这是一个用于在 `git push` 失败后排查网络并重试上传的 skill。

## 用途

当出现 `Could not connect to server`、`Recv failure`、`Connection was reset` 等错误时，快速完成诊断、代理修复和重试上传。

## 适用场景

- `git push` 连续失败
- 浏览器可以打开 GitHub，但终端 `git/curl` 不通
- 需要配合 Clash 代理修复命令行网络
- 需要确认“本地已提交但远程未同步”的状态

## 主要文件

- `SKILL.md`
- `agents/openai.yaml`
- `references/troubleshooting.md`