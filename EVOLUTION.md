# 技术路径与修改链路

本文件记录从第一版脚本到可跑通真实 Kimi API 的完整迭代过程，供复盘使用。

---

## 1. 第一版：MVP 骨架

目标：先让 `--mock` 跑通，不依赖任何外部 key。

- 创建 `radar.py`：单文件集成抓取、分析、报告。
- 抓取层：`fetch_repo_issues` 分页拉取，按 `pull_request` 字段过滤 PR，只保留 9 个字段，body 截断 1500。
- 分析层：Prompt 硬约束（枚举、原文 evidence、仅 JSON）。
- 报告层：总量、open/closed、类目分布、blocker 清单、Top 3 洞察。
- Mock 兜底：无 `KIMI_API_KEY` 或 `--mock` 时，用规则启发式分类。
- 验证：`python3 radar.py --mock` 成功生成 `report.md`。

## 2. 修复 Mock 启发式分类顺序

问题：issue "文档里没有多 agent 协作示例" 被错分为 `agent_runtime`，因为规则里 `agent` 关键字匹配优先于 `文档`。

修改：
- 把 `docs_gap` 判断提前到 `agent_runtime` 之前。
- `one_line` 从 24 字改为 15 字，符合 Spec。

## 3. 接入真实 Kimi API

### 3.1 模型名与 temperature

第一次真实调用返回 400：

```
invalid temperature: only 1 is allowed for this model
```

结论：当前 Moonshot API 对所有可用模型（kimi-k3、kimi-k2.7-code-highspeed、kimi-k2.6 等）均只支持 `temperature=1.0`。

修改：把 `temperature` 从 0.2 改为 1.0。

### 3.2 K3 大 batch 超时

第一次用 `kimi-k3`、batch=18、body=1500 跑真实分析：
- 18 条 issue prompt 约 32k 字符。
- 连续在 120s/180s 超时。

实验：
- 3 条 issue：K3 正常返回。
- 10/18 条 issue：K3 超时。

结论：K3 对大批量长文本推理太慢，不满足 MVP 45 分钟要求，需要降级。

### 3.3 模型选型实验

对 batch=18、body=1500 测试三个模型：

| 模型 | 结果 | 耗时 | 备注 |
|---|---|---|---|
| kimi-k3 | 超时 | — | 推理慢 |
| kimi-k2.6 | 超时 | — | 同样慢 |
| kimi-k2.7-code | 200，解析成功 | 114s | 可用但偏慢 |
| kimi-k2.7-code-highspeed | 200，解析成功 | 23.9s | 选中 |

修改：默认模型改为 `kimi-k2.7-code-highspeed`。

### 3.4 max_tokens 不足导致空返回/截断

切换到 highspeed 后，脚本里 `max_tokens=4000`，批次出现两种失败：

1. **空 content**：`Expecting value: line 1 column 1 (char 0)`。
2. **JSON 截断**：`Unterminated string starting at...`。

实验：
- max_tokens=6000：10 条仍截断。
- max_tokens=8000：有时返回空，有时 18 条完整。
- max_tokens=12000：10/12/14 条均完整解析。

结论：14 条 + 12000 max_tokens 是稳定配置。

修改：
- `max_tokens` 从 4000 → 12000。
- `BATCH_SIZE` 从 18 → 14（18 条在 12k 下仍有截断风险）。

### 3.5 超时与可观测性

- 请求 timeout 从 120s → 180s。
- HTTP 400/500 时打印服务端返回体，方便定位 temperature/max_tokens 问题。
- JSON 解析失败时打印模型返回前 500 字符预览。

### 3.6 CLI 参数化

为后续调参不硬编码，新增：
- `--batch-size`
- `--body-limit`
- `--timeout`
- `--model`（已存在，保留）

抓取层 `fetch_repo_issues` / `fetch_all`、分析层 `analyze_batch` / `analyze_issues` 均改为接收参数而非读全局变量。

---

## 4. 当前稳定配置

```python
DEFAULT_MODEL = "kimi-k2.7-code-highspeed"
BODY_TRUNCATE = 1500
BATCH_SIZE = 14
REQUEST_TIMEOUT = 180
max_tokens = 12000
temperature = 1.0
```

---

## 5. 仍未解决 / 可优化项

1. **全量 432 条耗时**：body=1500 时约 18-20 分钟；为在合理时间内跑完真实分析，本次实际运行采用 body=800（仍满足"截断长日志"的设计目标）。
2. **证据链长度**：当前 evidence 是模型自由截取的原文片段，未限制最大长度，报告里做了 120 字截断展示。
3. **模型稳定性**：highspeed 偶尔返回空 content，当前靠重试 3 次兜底；若仍失败则整批标为 `other`。
4. **扩展项未做**：时间趋势、首次响应时长、自动生成文档条目清单。

---

## 6. 学到的关键经验

- **不要假设 OpenAI 兼容接口的 temperature 可任意设置**：Moonshot 当前对 K3/K2 系列均锁定 temperature=1。
- **max_tokens 不是越大越快**：12000 比 8000 反而更稳；8000 时出现空返回可能与内部分配策略有关。
- **大 batch + 长 body 对推理型模型是灾难**：K3 更适合小批量精排，highspeed 更适合批量归类。
- **真实数据远比 mock 复杂**：mock 规则无法覆盖的边界（如长日志、中英混合、PR 混入）必须在真实运行中暴露。

---

## 7. 基于 Kimi 文档站观察的扩展方向

> 本节来自对 Kimi 文档站（platform.kimi.com/docs）的观察与本项目 issue 数据的交叉分析。

Kimi 文档站已经是 AI-native 架构：按用户旅程分层、组件化页面、支持 llms.txt/llms-full.txt 给 AI 读取。但从社区 issue 数据看，内容的"实战深度"和"失败模式覆盖"仍有明显缺口。以下三个方向值得作为后续项目或实习工作推进：

### 7.1 做一组「从 X 迁移到 Kimi」实战指南

issue 里大量反馈来自 Claude Code / Anthropic-compatible provider / Cursor 等第三方工具用户：

- #2378：API 网关对 PDF document 块返回 400（Claude Code 格式兼容）
- #2328：Anthropic provider 下 MCP tools 的 schema 问题
- #2062：Anthropic-compatible provider 的 max_tokens 限制
- #1796：HTTP 429 被静默吞掉

文档站目前对这些工具集成着墨较少。可产出一套《从 Claude Code / Cursor / OpenAI 迁移到 Kimi》系列，每篇按「错误现象 → 根因 → 解决代码」三段式写作，直接复用 issue 里的真实踩坑案例。

### 7.2 建一个「静默失败」专项排障中心

本次分析发现 88 个 blocker 中大量属于"静默挂起"——系统不报错、直接卡死：

| 现象 | 对应 issue | 建议文档条目 |
|---|---|---|
| `kimi -p` 零输出挂起 | #2358 | 非交互模式排障 |
| Windows 每次 prompt 永久卡死 | #2219 | Windows 环境检查清单 |
| 流式响应中途静默 | #1798 | SSE 流式连接问题排查 |
| 429 被吞，无 Retry-After 提示 | #1796 | 限流与重试机制说明 |
| K3 max effort 下挂起 10 分钟 | #1911 | 思考模型超时与 token 预算 |

可在文档站开设「Kimi 没反应时怎么办」troubleshooting hub，把静默失败变成可排查、可恢复。

### 7.3 把额度/计费体验写成「产品使用指南」

付费用户对额度耗尽的处理方式极度不满：

- #2389：额度耗尽静默杀掉所有 subagent
- #1482：5 小时 deep research token 全丢
- #158：刚充月订阅，用 4 次被限流

商业层和技术层虽然在文档站物理分开，但用户体验是连续的。建议新增《Kimi 额度与任务保存指南》，覆盖额度耗尽场景、token 预算设置、长任务分段保存、429/403 恢复流程。

### 7.4 把 radar 升级为「文档反馈闭环」原型

Kimi 已有 llms.txt/llms-full.txt 让 AI 读文档；本 radar 可反向工作——让 AI 读社区反馈，自动发现文档缺口并建议更新条目。理想闭环：

```
社区反馈 ──雷达──▶ 结构化洞察 ──▶ 建议更新 llms-full.txt 的哪些章节
         │                                    │
         └────── 文档改进后观察反馈是否减少 ─────┘
```

下一步可在 `radar.py` 中增加一个扩展模块：输入 `issues_analyzed.json`，输出建议新增/更新的文档条目清单（含对应 issue 链接和证据），让 demo 从一次性报告升级为可复用的 DevRel 工具。

