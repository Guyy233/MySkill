# 快速排障卡片

## 常见症状

- `Failed to connect to github.com port 443`
- `Recv failure: Connection was reset`
- 浏览器可以访问 GitHub，但终端 `curl` 或 `git push` 失败

## 快速步骤

1. `curl https://github.com`
2. `nslookup github.com`
3. `netsh winhttp show proxy`
4. `netstat -ano | findstr LISTENING | findstr 127.0.0.1`
5. 设置 Git 代理并重试 push

## Clash 建议

- 打开 `System Proxy`
- 可选打开 `TUN Mode`
- 模式可先切 `Global` 验证连通，再回 `Rule`