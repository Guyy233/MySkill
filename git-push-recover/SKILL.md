---
name: git-push-recover
description: 用于在 git push 上传失败后，快速诊断并修复命令行网络连通与代理配置问题，再重试上传到 GitHub。适用于出现 Could not connect to server、Recv failure、Connection was reset、port 443 超时等错误的场景，尤其是浏览器能访问 GitHub 但终端 git/curl 失败时。
---

# Git Push 故障修复

在 `git push` 失败后，执行一套稳定的网络排障与重试流程，帮助用户尽快完成远程备份。

## 默认目标

- 先确认本地提交是否已经完成
- 判断失败是仓库问题还是网络问题
- 修复终端代理与 Git 网络设置
- 重试 `git push` 直到成功或定位到明确阻塞点

## 标准流程

1. 先确认仓库状态：
   - `git status -sb`
   - `git log --oneline -1`
2. 若出现网络相关报错（443 超时、连接重置等），先做连通性检查：
   - `curl https://github.com`
   - `nslookup github.com`
3. 如果浏览器可用但终端不可用，优先判断为“终端未走代理”。
4. 针对 Clash 等代理环境，执行：
   - 检查系统代理状态：`netsh winhttp show proxy`
   - 检查本机监听端口：`netstat -ano | findstr LISTENING | findstr 127.0.0.1`
   - 给 Git 配置代理（按实际端口替换）：
     - `git config --global http.proxy http://127.0.0.1:7890`
     - `git config --global https.proxy http://127.0.0.1:7890`
5. 给仓库补兼容设置：
   - `git config http.version HTTP/1.1`
   - `git config http.sslBackend schannel`
6. 重试推送：
   - `git push`
   - 失败时读取新报错并迭代修复
7. 成功后确认：
   - `git status -sb` 不再显示 ahead

## 诊断原则

- 浏览器能打开 GitHub，但 `curl/git` 不通：优先定位“命令行代理未生效”。
- `nslookup` 正常但 443 超时：优先检查代理端口与规则模式。
- 本地已提交但推送失败：先保护“本地提交已完成”的事实，再处理网络。

## 输出要求

- 明确告诉用户当前属于哪类问题（仓库问题 / 网络问题 / 认证问题）
- 明确给出下一条可执行命令
- 如果还未推送成功，必须说明“本地提交是否已安全保存”

## 常用修复命令集合

```bash
git config http.version HTTP/1.1
git config http.sslBackend schannel
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
curl https://github.com
git push
```