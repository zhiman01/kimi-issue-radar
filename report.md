# Kimi 社区 Issue 洞察报告

生成时间：2026-07-31T08:32:34.264050

## 1. 总体概况

| 指标 | 数值 |
|---|---|
| 仓库数 | 2 |
| Issue 总量 | 432 |
| Open 数 | 384 |
| Closed 数 | 48 |
| Open/Closed 比例 | 384:48 |
| 时间跨度 | 2026-01-27 ~ 2026-07-30 |
| 分析模型 | kimi-k2.7-code-highspeed |

## 2. 类目分布

| 排名 | 类目 | 数量 | 占比 | 归属方 |
|---|---:|---:|---:|---|
| 1 | `feature_request` | 132 | 30.6% | 产品 |
| 2 | `agent_runtime` | 108 | 25.0% | 产品 |
| 3 | `ide_integration` | 70 | 16.2% | 产品 |
| 4 | `other` | 60 | 13.9% | 兜底 |
| 5 | `install_env` | 23 | 5.3% | 文档 |
| 6 | `auth_billing` | 23 | 5.3% | 文档 |
| 7 | `docs_gap` | 9 | 2.1% | 文档 |
| 8 | `model_behavior` | 7 | 1.6% | 模型 |

## 3. Blocker 级问题清单

- **#2427** [Edit 失败后陷入死循环：反复"Edit 失败 → 重读 → 再失败"，并逐步删空了被编辑文件的多个章节](https://github.com/MoonshotAI/kimi-code/issues/2427)
  - 类目：`agent_runtime` | 证据：一次 Edit 调用失败（old_string 找不到 / 文件内容已变化）后，agent 没有先诊断、再一次性重读受影响区域，而是连续 十余次 重复"Edit 失败 → 重读一小段 → 再次 Edit 失败"的循环。…
- **#2389** [Swarm + goal mode: quota 403 kills all subagents silently — session idles for hours with no surfaced error, failed subagents never resumed](https://github.com/MoonshotAI/kimi-code/issues/2389)
  - 类目：`agent_runtime` | 证据：when the Kimi **subscription quota** is exhausted mid-run, the API returns `403 permission_error` to subagent and main-a…
- **#2388** [[Windows] browser-use agent's Playwright headless Chrome leaks handles/threads into explorer.exe & dwm.exe, freezing the desktop shell](https://github.com/MoonshotAI/kimi-code/issues/2388)
  - 类目：`agent_runtime` | 证据：When the `browser-use` agent (Playwright-based) runs for an extended session, `explorer.exe` and `dwm.exe` accumulate ha…
- **#2381** [v2 engine (headless -p): deferred MCP tools announced but select_tools never registered — top-level agent cannot call any MCP tool](https://github.com/MoonshotAI/kimi-code/issues/2381)
  - 类目：`agent_runtime` | 证据：But `select_tools` is never registered in the top-level agent's function schema, and neither are the `mcp__*` tools them…
- **#2378** [API 网关对 PDF document 块一律返回无具体原因的 400，且污染会话导致后续所有请求失败](https://github.com/MoonshotAI/kimi-code/issues/2378)
  - 类目：`other` | 证据：通过 https://api.kimi.com/coding/v1/messages 使用 Claude Code 时，只要请求中包含 Anthropic 标准格式的 PDF document 内容块，网关即返回： {"error":{"t…
- **#2364** [crashes every time, which is why tokens are wasted](https://github.com/MoonshotAI/kimi-code/issues/2364)
  - 类目：`other` | 证据：Every time I run a query, Kimi starts thinking for a long time. After 30 minutes, it stops. The tokens are gone. The tas…
- **#2358** [kimi -p (non-interactive) hangs and produces zero output, while the interactive TUI works with the same credentials](https://github.com/MoonshotAI/kimi-code/issues/2358)
  - 类目：`agent_runtime` | 证据：`kimi -p "<prompt>"` hangs indefinitely and writes **zero bytes** to both stdout and
stderr. The interactive TUI works n…
- **#2330** [Can't install from IRAN](https://github.com/MoonshotAI/kimi-code/issues/2330)
  - 类目：`install_env` | 证据：how can install kimi-code from location of iran?…
- **#2328** [Anthropic provider: 400 on MCP tools with top-level oneOf/anyOf/allOf in input_schema (and [tools].disabled doesn't filter MCP tools from the wire)](https://github.com/MoonshotAI/kimi-code/issues/2328)
  - 类目：`agent_runtime` | 证据：When using an `anthropic`-type provider (Claude models), any MCP server that exposes a tool whose `inputSchema` has a to…
- **#2327** [[CRITICAL] Unauthorized deletion of template files by AI agent](https://github.com/MoonshotAI/kimi-code/issues/2327)
  - 类目：`agent_runtime` | 证据：Kimi Code autonomously executed destructive `rm` / `rm -rf` commands to delete the `template/pc` and `template/mobile` d…
- **#2325** [[openai_responses] Continuous compaction loop on startup](https://github.com/MoonshotAI/kimi-code/issues/2325)
  - 类目：`agent_runtime` | 证据：In Kimi 0.29.2 (Linux x64), when using the `openai_responses` API type with a self-hosted model, Kimi continuously trigg…
- **#2311** [Kimi Code 0.29.x ReadMediaFile 读取视频失败](https://github.com/MoonshotAI/kimi-code/issues/2311)
  - 类目：`agent_runtime` | 证据：[Regression] ReadMediaFile 0.29.2 无法读取 mp4 — 工具 Schema 强制要求 `region` 和 `full_resolution`，后端对视频调用拒绝该参数…
- **#2265** [Can't Stop in VS Code](https://github.com/MoonshotAI/kimi-code/issues/2265)
  - 类目：`ide_integration` | 证据：Can't Stop in VS Code

### What issue are you seeing?

There's no way for me to stop / interrupt Kimi in VS Code once sh…
- **#2225** [[Windows] kimi.exe blocked by Smart App Control — please Authenticode-sign the CLI binaries](https://github.com/MoonshotAI/kimi-code/issues/2225)
  - 类目：`install_env` | 证据：The Windows CLI binary `kimi.exe` (installed at `%USERPROFILE%\.kimi-code\bin\kimi.exe`) is **not Authenticode-signed**.…
- **#2219** [Windows x64: Kimi Code CLI v0.29.1 hangs forever on every prompt.](https://github.com/MoonshotAI/kimi-code/issues/2219)
  - 类目：`agent_runtime` | 证据：Kimi Code hangs indefinitely on every prompt and prints no response.…
- **#2198** [`[Bug] Kimi Work desktop: Swarm mode selection no longer reaches the runtime — no swarm_mode.enter / enter-reminder injection since app 3.1.4, while sessions still run as k3-agent-swarm`](https://github.com/MoonshotAI/kimi-code/issues/2198)
  - 类目：`agent_runtime` | 证据：Selecting Swarm mode in Kimi Work desktop no longer reaches the runtime — no swarm_mode.enter / enter-reminder injection…
- **#2166** [Error with models not supporting prompt cache](https://github.com/MoonshotAI/kimi-code/issues/2166)
  - 类目：`other` | 证据：This was working fine until the latest update today. I believe Nvidia NIM doesn't support this but I have been using the…
- **#2152** [Reason: Rate limit exceeded  {"message":"The engine is currently overloaded, please try again later","type":"engine_overloaded_error"}:使用vscode调用api的时候，频繁出错，周流量和频率限制都没有超过的情况下，还是频繁出错，基本不可使用。](https://github.com/MoonshotAI/kimi-code/issues/2152)
  - 类目：`ide_integration` | 证据：使用vscode调用api的时候，频繁出错，周流量和频率限制都没有超过的情况下，还是频繁出错，基本不可使用。…
- **#2143** [Bash tool fails to spawn (ENOENT) when session workspace is a WSL UNC path](https://github.com/MoonshotAI/kimi-code/issues/2143)
  - 类目：`agent_runtime` | 证据：On Windows, when a Kimi Work session workspace points to a WSL directory via its UNC path (`\\wsl.localhost\<distro>\...…
- **#2118** [`Read` tool rejects an integer `line_offset` with "must be integer" validation error](https://github.com/MoonshotAI/kimi-code/issues/2118)
  - 类目：`agent_runtime` | 证据：The `Read` tool rejects a valid integer `line_offset` argument. The agent called `Read` with `{"path": "main.go", "line_…
- **#2109** [MCP stdio server 意外死亡后无自动重连，调用挂起至 toolTimeoutMs 而非快速失败](https://github.com/MoonshotAI/kimi-code/issues/2109)
  - 类目：`agent_runtime` | 证据：当 stdio MCP server 进程意外死亡（崩溃、OOM、Windows 上 `taskkill /F`）时，kimi-code 能正确检测并把 server 标记为 `failed`——但**从不尝试重连**，且发往已死 serv…
- **#2080** [Session permanently bricked after one 400 "high risk" rejection — no recovery path, likely false positive](https://github.com/MoonshotAI/kimi-code/issues/2080)
  - 类目：`other` | 证据：After ~5 hours of normal operation, every LLM request in the session started failing with `400 The request was rejected …
- **#2062** [FALLBACK_MAX_TOKENS=128000 rejected by Anthropic-compatible providers with lower output limits](https://github.com/MoonshotAI/kimi-code/issues/2062)
  - 类目：`agent_runtime` | 证据：When using an Anthropic-compatible provider (e.g., Volcano Engine) with a non-Claude model like `k2.7`, these providers …
- **#2045** [Terminal execution abnormal termination](https://github.com/MoonshotAI/kimi-code/issues/2045)
  - 类目：`agent_runtime` | 证据：as i excute a task . a commond timeout or exception will interrupt the thread, dialog will exit and layout organization.…
- **#2037** [ACP: session/prompt never returns after terminal LLM failure on resumed session](https://github.com/MoonshotAI/kimi-code/issues/2037)
  - 类目：`ide_integration` | 证据：When a `session/prompt` request fails with a terminal LLM error on a resumed session, the ACP server never answers the r…
- **#2024** [Security: prompt injection via always-sent system prompt baseline](https://github.com/MoonshotAI/kimi-code/issues/2024)
  - 类目：`other` | 证据：Kimi Code appears to include large, attacker-controllable payloads as part of the **always-sent system prompt baseline**…
- **#1985** [400 The message at position 307 with role 'assistant' must not be empty](https://github.com/MoonshotAI/kimi-code/issues/1985)
  - 类目：`agent_runtime` | 证据：400 The message at position 307 with role 'assistant' must not be empty…
- **#1955** [20k tokens to say "hi"](https://github.com/MoonshotAI/kimi-code/issues/1955)
  - 类目：`model_behavior` | 证据：The previous version 0.27.0 consumed around 13,000 tokens, but after upgrading to 0.28.0, it now uses over 20,000 tokens…
- **#1952** [反复误报“Provider safety policy blocked”](https://github.com/MoonshotAI/kimi-code/issues/1952)
  - 类目：`model_behavior` | 证据：反复报安全错误，我让AI把可能触发报错的地方都改了还是不行，完全没法用了…
- **#1949** [TUI 流式输出被逐词折行（CJK 文本几乎无法阅读）](https://github.com/MoonshotAI/kimi-code/issues/1949)
  - 类目：`agent_runtime` | 证据：流式渲染时，助手输出的中文/英文文本被切成"几乎每个词单独成行"，一段正常的话变成竖排的词列，完全无法阅读。…
- **#1943** [[Bug] 0.27.0 web server process repeatedly dies with SIGSEGV in V8 GC marking — 6 crashes in ~26 h](https://github.com/MoonshotAI/kimi-code/issues/1943)
  - 类目：`install_env` | 证据：The kimi web server process dies abruptly with **SIGSEGV** — 6 crashes in ~26 hours, all with the same signature: the fa…
- **#1942** [Undici HTTP/2 下，独立 SSE 流占用调度槽位导致 Streamable HTTP MCP 启动超时](https://github.com/MoonshotAI/kimi-code/issues/1942)
  - 类目：`agent_runtime` | 证据：当 Kimi Code 连接一个满足以下条件的 Streamable HTTP MCP 服务器时，MCP 初始化必然超时…
- **#1932** [Kimi Code CLI 在 VS 2022 的嵌入Powershell终端中某些时候调整窗口大小会导致VS窗口闪烁或消失](https://github.com/MoonshotAI/kimi-code/issues/1932)
  - 类目：`other` | 证据：2.使用kimi要求修改一些内容，我这里使用了SuperPower插件。当kimi code cli 开始使用子代理编码时。调整终端窗口。

3.Bug触发窗口开始闪烁，最小化VS 后，窗口消失，无法再次唤起。…
- **#1931** [stdio MCP child env injects bracketed [::1] into NO_PROXY, crashing Python httpx-based MCP servers](https://github.com/MoonshotAI/kimi-code/issues/1931)
  - 类目：`agent_runtime` | 证据：With an HTTP proxy configured (`HTTP_PROXY`/`HTTPS_PROXY`/`ALL_PROXY` set), any stdio MCP server implemented in Python o…
- **#1925** [[Bug] session_index.jsonl loses newline between entries, causing session.not_found on resume](https://github.com/MoonshotAI/kimi-code/issues/1925)
  - 类目：`agent_runtime` | 证据：`session_index.jsonl` can end up with two JSON objects concatenated on the same line (missing newline separator), which …
- **#1924** [Background tasks marked "lost" without liveness check; resume spawns duplicate concurrent workers](https://github.com/MoonshotAI/kimi-code/issues/1924)
  - 类目：`agent_runtime` | 证据：When a kimi-code process with live background tasks is still running and a second process resumes the same session, `mar…
- **#1917** [[Bug] APIConnectionError becomes permanent until process restart — HTTP client wedges, no sockets opened during retries (0.27.0)](https://github.com/MoonshotAI/kimi-code/issues/1917)
  - 类目：`other` | 证据：Several times per day, mid-session, every LLM request starts failing with
`Error: [provider.connection_error] Connection…
- **#1911** [[Bug] Interactive TUI and non-interactive -p mode both hang indefinitely on kimi-k3 (max effort); Ctrl+C/Esc unresponsive for 10+ min; agent also exceeds instructed scope](https://github.com/MoonshotAI/kimi-code/issues/1911)
  - 类目：`agent_runtime` | 证据：Kimi Code CLI hangs with no visible output for 10+ minutes in both interactive mode and non-interactive `-p` mode, even …
- **#1909** [[Bug] wind-allskill 插件完全不可用：agent_gw Python SDK 未预装导致 NETWORK_ERROR](https://github.com/MoonshotAI/kimi-code/issues/1909)
  - 类目：`install_env` | 证据：`wind-allskill` 插件（Wind 万得数据）在 Kimi 桌面版中返回 `NETWORK_ERROR`，经排查根因为 **`agent_gw` Python SDK 未预装** 在 managed Python runtime…
- **#1892** [[TUI] iTerm2 中审批弹窗出现时整个 TUI 卡死（高速闪烁、键鼠无响应、无法滚动），Terminal.app 正常](https://github.com/MoonshotAI/kimi-code/issues/1892)
  - 类目：`agent_runtime` | 证据：iTerm2 中运行 kimi，工具审批弹窗出现时整个 TUI 高速闪烁/跳动并完全卡死：键盘（方向键+回车）无响应、终端无法滚动，只能中断会话。…
- **#1883** [Issue: macOS 上 kimi-code CLI 因 clipboard.darwin-universal.node 死锁而无限卡住](https://github.com/MoonshotAI/kimi-code/issues/1883)
  - 类目：`install_env` | 证据：- **操作系统**: macOS 26.5.2 (25F84) — Darwin ARM64
- **Node.js**: v22.23.1（也测试过 v18.20.8，问题相同）
- **kimi-code 测试版本**: 0.26.0…
- **#1850** [install.ps1解析架构异常](https://github.com/MoonshotAI/kimi-code/issues/1850)
  - 类目：`install_env` | 证据：脚本解析时出现下面的错误:

```
    ==> Detected target: win32-arm64 arm64
    ==> Resolving latest version from https://code.kimi.co…
- **#1798** [Silent infinite hang when a streaming completion stalls mid-body (0.26.0)](https://github.com/MoonshotAI/kimi-code/issues/1798)
  - 类目：`agent_runtime` | 证据：An SSE completion stream that goes silent **mid-body** blocks the whole turn forever. Symptom is identical to #1796 (sil…
- **#1796** [Silent infinite hang on HTTP 429: rate-limit error and Retry-After are discarded (0.26.0)](https://github.com/MoonshotAI/kimi-code/issues/1796)
  - 类目：`auth_billing` | 证据：When the API returns **HTTP 429 (rate limit)**, kimi-code discards the error and hangs forever. No error message, no ret…
- **#1792** [Windows TUI prints raw ANSI escape sequences instead of rendering (Windows Terminal, PowerShell, cmd)](https://github.com/MoonshotAI/kimi-code/issues/1792)
  - 类目：`other` | 证据：Running `kimi` dumps the whole TUI as literal escape text. Colors, box drawing, cursor control, etc. never render. The U…
- **#1725** [VSCODE 插件式没人管了么](https://github.com/MoonshotAI/kimi-code/issues/1725)
  - 类目：`ide_integration` | 证据：新版kimi code 没法兼容vscode 插件…
- **#1610** [400 error: "tools.function.parameters is not a valid moonshot flavored json schema" when using custom API endpoint with MCP tools](https://github.com/MoonshotAI/kimi-code/issues/1610)
  - 类目：`agent_runtime` | 证据：When using a custom API endpoint with multiple MCP servers configured,the LLM request fails with:
APIStatusError: 400 to…
- **#1579** [Windows bash detection fails when git comes from a native MSYS2 environment (ucrt64/clang64/clangarm64)](https://github.com/MoonshotAI/kimi-code/issues/1579)
  - 类目：`install_env` | 证据：### What issue are you seeing?

On Windows, starting kimi-code fails with:

Git Bash was not found on this Windows host.…
- **#1495** [Windows 下结构化工具结果在 UI 可见但模型无法读取](https://github.com/MoonshotAI/kimi-code/issues/1495)
  - 类目：`agent_runtime` | 证据：在 Windows 环境下，Kimi Code CLI 的结构化工具结果会显示在 UI 中，但模型无法读取这些工具返回的实际内容。…
- **#1485** [kimi acp completes prompt with end_turn but emits zero agent_message_chunk updates (no visible response in generic ACP clients)](https://github.com/MoonshotAI/kimi-code/issues/1485)
  - 类目：`ide_integration` | 证据：kimi acp completes prompt with end_turn but emits zero agent_message_chunk updates (no visible response in generic ACP c…
- **#1482** [正在做着deep research , 触发了限额，所有的都丢了，5h额度的token白白浪费。至少有两次实在有点忍耐不了了](https://github.com/MoonshotAI/kimi-code/issues/1482)
  - 类目：`auth_billing` | 证据：正在做着deep research , 触发了限额，所有的都丢了，5h额度的token白白浪费。至少有两次实在有点忍耐不了了…
- **#1473** [Ubuntu Kimi Code Cli Not response](https://github.com/MoonshotAI/kimi-code/issues/1473)
  - 类目：`other` | 证据：从2026/7/7 下午大概5:00左右，Kimi Cli 开始不返回任何信息，一直在处理，使用OAuth / API Key 都不行。…
- **#1455** [openai_responses should treat final function-call arguments as authoritative](https://github.com/MoonshotAI/kimi-code/issues/1455)
  - 类目：`agent_runtime` | 证据：Kimi Code frequently aborts tool-calling turns when using the `openai_responses` provider.…
- **#1449** [服务挂了？](https://github.com/MoonshotAI/kimi-code/issues/1449)
  - 类目：`other` | 证据：服务挂了？…
- **#222** [vscode 插件提示未登录](https://github.com/MoonshotAI/kimi-agent-sdk/issues/222)
  - 类目：`ide_integration` | 证据：kimi code 升级到0.24.1 后，vscode 插件一直提示Authentication failed. Your login session may have expired. Please run "/login" to si…
- **#213** [持续执行过程中无法停止](https://github.com/MoonshotAI/kimi-agent-sdk/issues/213)
  - 类目：`agent_runtime` | 证据：上下文比较长的时候，点击了停止按钮一直没反应，强制发送消息也没反应。不得不退出重启…
- **#210** [[Bug] Kimi Code VS Code extension fails on macOS 14.6.1 (Intel): bundled CLI hangs during startup](https://github.com/MoonshotAI/kimi-agent-sdk/issues/210)
  - 类目：`install_env` | 证据：CLI Not Found
The bundled CLI is unavailable. Please install manually.
Bridge checkCLI timed out…
- **#201** [VS Code中kimi code插件无法登录](https://github.com/MoonshotAI/kimi-agent-sdk/issues/201)
  - 类目：`auth_billing` | 证据：Authentication failed. Your login session may have expired. Please run "/login" to sign in again.
{"jsonrpc":"2.0","id":…
- **#199** [[Regression] Kimi Code panel completely missing in Remote-SSH on VS Code 1.123.0](https://github.com/MoonshotAI/kimi-agent-sdk/issues/199)
  - 类目：`ide_integration` | 证据：After upgrading VS Code from 1.122.1 to 1.123.0, the Kimi Code panel entry 
completely disappears in remote (SSH) worksp…
- **#185** [更新0.58后CLI一直报错无法使用](https://github.com/MoonshotAI/kimi-agent-sdk/issues/185)
  - 类目：`install_env` | 证据：The bundled CLI is unavailable. Please install manually.   试了很多方法都报错，上午还能正常使用，下午更新后就无法使用了！！！！…
- **#183** [VSCode插件无法登录](https://github.com/MoonshotAI/kimi-agent-sdk/issues/183)
  - 类目：`auth_billing` | 证据：我想登录Kimi Code的VSCode插件，但是点“Sign in with Kimi Account”后报错：
```json
{"type": "error", "message": "Login failed: Cannot con…
- **#178** [SDK deadlocks with kimi CLI v1.40.0 due to unknown MCPLoadingBegin/MCPLoadingEnd events](https://github.com/MoonshotAI/kimi-agent-sdk/issues/178)
  - 类目：`agent_runtime` | 证据：SDK deadlocks with kimi CLI v1.40.0 due to unknown MCPLoadingBegin/MCPLoadingEnd events…
- **#174** [Connection Error: The bundled CLI is unavailable. Please install manually. (It is installed...)](https://github.com/MoonshotAI/kimi-agent-sdk/issues/174)
  - 类目：`install_env` | 证据：I installed kimi-cli (verified with kimi --version)

I installed the Antigravity Kimi Code Extension (VSCode) > logged i…
- **#170** [MCP Server Connection Always Fails on Windows Due to Unicode Encoding Bug in kimi.exe (PyInstaller Python 3.14)](https://github.com/MoonshotAI/kimi-agent-sdk/issues/170)
  - 类目：`agent_runtime` | 证据：The mcp test command and MCP server connection always fail on Windows with UnicodeEncodeError: 'charmap' codec can't enc…
- **#169** [开启思考模式后调用工具会出现Error code: 400  thinking is enabled but reasoning_content is missing in assistant tool call message at](https://github.com/MoonshotAI/kimi-agent-sdk/issues/169)
  - 类目：`model_behavior` | 证据：开启思考模式后调用工具会出现Error code: 400  thinking is enabled but reasoning_content is missing in assistant tool call message at…
- **#168** [Can't get anything to show when installed](https://github.com/MoonshotAI/kimi-agent-sdk/issues/168)
  - 类目：`ide_integration` | 证据：The Kimi Code VSCode extension just doesn't work at all. No kimi. commands are working, nothing, this has been prevalent…
- **#158** [我发一张样本图片和文档要求，服务就不可用了](https://github.com/MoonshotAI/kimi-agent-sdk/issues/158)
  - 类目：`auth_billing` | 证据：我发一张样本图片和文档要求，服务就不可用了
我在VS code 编程任务框里发了一张样本图片，然后传上我的工作要求，它在运行的时候就来一个服务暂时不可用。我是晚上7点钟才充的月订阅，才用了4次，就让我要等下一个周期刷新？他这个刷新什么意思啊…
- **#146** [vs code插件一直Loading...](https://github.com/MoonshotAI/kimi-agent-sdk/issues/146)
  - 类目：`ide_integration` | 证据：vs code插件一直Loading...…
- **#145** [Positron里面的Kimi coding使用问题](https://github.com/MoonshotAI/kimi-agent-sdk/issues/145)
  - 类目：`auth_billing` | 证据：Mac M2笔记本电脑，非虚拟机在Positron里使用Kimi code插件，今天突然出现问题显示无法连接：
Service temporarily unavailable.
{"jsonrpc":"2.0","id":"2_177570…
- **#144** [插件一直Processing](https://github.com/MoonshotAI/kimi-agent-sdk/issues/144)
  - 类目：`ide_integration` | 证据：插件一直Processing
无论输入什么，一直Processing…
- **#138** [[MCP Bug] v0.4.5 MCP 多重问题：GitHub 工具不加载 + Playwright/Context7 添加卡死](https://github.com/MoonshotAI/kimi-agent-sdk/issues/138)
  - 类目：`agent_runtime` | 证据：[MCP Bug] v0.4.5 MCP 多重问题：GitHub 工具不加载 + Playwright/Context7 添加卡死

## 问题 1：GitHub MCP 配置正确但工具未加载

### 配置详情
- **Name**: g…
- **#133** [CRITICAL SERVICE OUTAGE - Error 401 Kimi Code VS Code and Antigravity Extension | Issue #132 Confirmed | Annual Subscription Unusable](https://github.com/MoonshotAI/kimi-agent-sdk/issues/133)
  - 类目：`auth_billing` | 证据：Persistent 401 authentication error on every request. Cannot use the paid service.…
- **#130** [VS Code中的kimi插件无法找到kimi-cli](https://github.com/MoonshotAI/kimi-agent-sdk/issues/130)
  - 类目：`ide_integration` | 证据：如果使用内置则报错The bundled CLI is unavailable, 如果指定另外安装的则报错The configured CLI path is invalid or the CLI version is incompatib…
- **#128** [Linux下vscode的kimi code无法登陆](https://github.com/MoonshotAI/kimi-agent-sdk/issues/128)
  - 类目：`ide_integration` | 证据：打开网页，登陆成功回到vscode后：
报错：/bin/sh: symbol lookup error: /bin/sh: undefined symbol: rl_trim_arg_from_keyseq…
- **#121** [[Bug] Stuck in 401 Invalid Authentication loop - No way to log out or reset token (macOS)](https://github.com/MoonshotAI/kimi-agent-sdk/issues/121)
  - 类目：`auth_billing` | 证据：Stuck in 401 Invalid Authentication loop - No way to log out or reset token (macOS)…
- **#118** [虚拟机Code上一直处于服务不可用的状态](https://github.com/MoonshotAI/kimi-agent-sdk/issues/118)
  - 类目：`ide_integration` | 证据：每当发送内容的时候就会出现错误：
`Service temporarily unavailable.
{"jsonrpc":"2.0","id":"4_1772629726544","error":{"code":-32003,"messa…
- **#116** [kimi vscode插件一直load](https://github.com/MoonshotAI/kimi-agent-sdk/issues/116)
  - 类目：`ide_integration` | 证据：kimi vscode插件一直load…
- **#115** [kimi code插件一直loading](https://github.com/MoonshotAI/kimi-agent-sdk/issues/115)
  - 类目：`ide_integration` | 证据：打不开这个插件了。之前还行。…
- **#87** [VSCode Extension is again nonusable](https://github.com/MoonshotAI/kimi-agent-sdk/issues/87)
  - 类目：`ide_integration` | 证据：VSCode Extension is again nonusable

I stop auto extension update now, actually i stop using this extension.…
- **#81** [Vscode extension stop working](https://github.com/MoonshotAI/kimi-agent-sdk/issues/81)
  - 类目：`ide_integration` | 证据：Vscode extension stop working

I type i sent but nothing happen it dont work…
- **#78** [我刚订阅最高付费等级的订阅，第二天在vscode经常出现服务不可用 Service temporarily unavailable.](https://github.com/MoonshotAI/kimi-agent-sdk/issues/78)
  - 类目：`ide_integration` | 证据：我刚订阅最高付费等级的订阅，第二天在vscode经常出现服务不可用 Service temporarily unavailable.

 问题根因

  VS Code 扩展 moonshot-ai.kimi-code-0.3.1 的调试日…
- **#74** [在vscode经常出现服务不可用](https://github.com/MoonshotAI/kimi-agent-sdk/issues/74)
  - 类目：`ide_integration` | 证据：在vscode经常出现服务不可用

1. 最近一两天容易经常性的出现“Service temporarily unavailable.
{"jsonrpc":"2.0","id":"29_1770111798225","error":{"c…
- **#73** [kimi code keep processing](https://github.com/MoonshotAI/kimi-agent-sdk/issues/73)
  - 类目：`agent_runtime` | 证据：kimi code keep processing

Today in kimi code, not respond many times and keep practicing.…
- **#66** [使用报错](https://github.com/MoonshotAI/kimi-agent-sdk/issues/66)
  - 类目：`install_env` | 证据：使用报错

安装之后报错，Window系统，vscode版本1.85.2，还原视图时出错: kimi.webview…
- **#65** [The Agent freezes if I press the Stop button when it asks for permission to execute a shell command.](https://github.com/MoonshotAI/kimi-agent-sdk/issues/65)
  - 类目：`agent_runtime` | 证据：The Agent freezes if I press the Stop button when it asks for permission to execute a shell command.

The page keeps spi…
- **#56** [in linux need remove  libreadline.so](https://github.com/MoonshotAI/kimi-agent-sdk/issues/56)
  - 类目：`install_env` | 证据：in linux need remove
mv ~/.config/Code/User/globalStorage/moonshot-ai.kimi-code/bin/kimi/_internal/libreadline.so.8{,.ba…
- **#54** [VS Code Extension 0.2.6: "Service temporarily unavailable" after auto-update (0.2.5 works fine)](https://github.com/MoonshotAI/kimi-agent-sdk/issues/54)
  - 类目：`ide_integration` | 证据：After the automatic update to version 0.2.6 of the Kimi Code VS Code extension, the service shows "Service temporarily u…
- **#43** [no respond keep processing](https://github.com/MoonshotAI/kimi-agent-sdk/issues/43)
  - 类目：`ide_integration` | 证据：No more respond and keep processing.…

## 4. 核心洞察

> 说明：本节结论由人工判断得出，而非按类目数量自动排序。"数量最多"不等于"最重要"，以下三条基于问题的性质与业务影响，而非计数。

### 洞察 1：模型能力不是瓶颈，接入与运行时才是

`model_behavior` 仅 7 条（1.6%），是全部类目中最少的一类。与之相对，`agent_runtime`（108 条）与 `ide_integration`（70 条）合计 178 条，占全部反馈的 41%。

**结论**：开发者几乎不抱怨 K3 的智能水平，抱怨集中在"装不上、连不上、跑到一半挂了"。对一家刚开源全球最大参数模型的公司，这是积极信号——模型能力已不是短板，真正的护城河在最后一公里的工程与接入体验。这也正是文档、教程与 onboarding 内容能直接发力的地方。

### 洞察 2：一整类"静默挂起"问题正在侵蚀新用户信任

多条 blocker 指向同一根因——出错时不报错，直接静默卡死，用户无从判断发生了什么：

- #2358：`kimi -p` 非交互模式挂起，零输出
- #2219：Windows 每次 prompt 永久卡死
- #1798：流式响应中途静默，整轮阻塞
- #1796：遇到 HTTP 429 直接吞掉错误与 Retry-After，永久挂起
- #1911：K3 max effort 下挂起 10 分钟以上，Ctrl+C 无响应

**结论**：这不是零散 bug，而是同一种失败模式。报错尚可排查，静默卡死只会导致卸载。建议优先建立"任何失败都必须向用户显性反馈"的兜底机制，这是留存新用户的关键一环。

### 洞察 3：付费用户的额度体验正在制造流失

以下反馈来自已付费用户，愤怒点高度一致——付了钱、任务跑到一半、额度耗尽、成果全丢、且无明确提示：

- #2389：额度耗尽时静默杀掉所有 subagent，会话空转数小时
- #1482：触发限额，5 小时 deep research 的 token 全部作废
- #158：刚充月订阅，用 4 次即被限流
- #133：年订阅遭遇持续 401，服务完全不可用

**结论**：对一家 API First、依赖付费转化的公司，这类问题直接影响营收留存。核心不在额度本身，而在"耗尽时的处理方式"——无预警、无优雅降级、无成果保全。

### 附：一个被高频踩中的坑（亲测复现）

#1955（"20k tokens to say hi"）与 #2364（思考 30 分钟耗尽 token、任务未完成）指向同一问题：K3 强制思考且思考 token 计入输出配额，在简单任务上造成显著浪费。这与我首次调用 K3 API 时的实测一致——请求仅回复两字，却因思考未结束撞上 token 上限而返回空结果。建议在「快速开始」文档中明确提示 K3 的思考特性与 token 预算，可为新用户规避大量困惑。

---
*本报告由 Kimi 社区 Issue 洞察雷达自动生成。*
