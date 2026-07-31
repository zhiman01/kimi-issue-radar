# Kimi 社区 Issue 洞察雷达

> 自动抓取 MoonshotAI 开源仓库 GitHub Issues，用 Kimi API 做聚类与归因，输出一份可行动的 DevRel 洞察报告。

这个项目是我为 **Developer Relations (Content) Intern** 岗位准备的作品：它从开发者社区的一线反馈出发，用 AI Agent 和自动化工具把散落的 issue 收敛成产品、文档、运营都能看懂的可行动结论。

---

## 为什么做这个项目

DevRel 内容不是“写教程”，而是回答一个问题：**开发者现在最卡在哪里？**

MoonshotAI 有两个核心开源仓库：`kimi-code` 和 `kimi-agent-sdk`。它们的 GitHub Issues 里沉淀了大量真实反馈，但零散阅读很难看出模式。这个雷达尝试把“读 issue”自动化、结构化，让文档补什么、产品修什么变得有据可依。

---

## 核心结果

对 2026-01-27 至 2026-07-30 期间的 **432 条有效 issue** 进行分析后，得到以下关键发现：

| 维度 | 结果 |
|---|---|
| Open / Closed | 384 / 48 |
| 最集中类目 | `feature_request`（132 条，30.6%） |
| 最致命类目 | `agent_runtime`（108 条 blocker 占比最高） |
| 静默挂起类 blocker | 约 20+ 条指向同一失败模式 |
| 付费用户额度投诉 | 多条年订阅 / 月订阅用户反馈 |
| 模型质量反馈 | `model_behavior` 仅 7 条（1.6%） |

完整洞察见 [`report.md`](./report.md)。

---

## 项目架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  GitHub API │────▶│  数据清洗   │────▶│ issues_raw  │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                                │
                                                ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Kimi API   │◀────│  分批分析   │◀────│  issue batch│
└──────┬──────┘     └─────────────┘     └─────────────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│ 分类/severity│────▶│ issues_analyzed│
│  evidence   │     └──────┬──────┘
└─────────────┘            │
                           ▼
                    ┌─────────────┐
                    │  report.md  │
                    └─────────────┘
```

### 三层职责

1. **抓取层**：分页拉取 GitHub Issues，用 `pull_request` 字段过滤 PR，只保留分析必需字段，body 截断避免日志噪音。
2. **分析层**：每批 14 条送入 Kimi API，做**受限分类**（8 个类目），输出 category / severity / one_line / evidence。
3. **报告层**：生成总量、分布、blocker 清单与 Top 3 洞察。

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 无 key 验证流程

```bash
python3 radar.py --mock
```

会自动生成 `issues_raw.json`、`issues_analyzed.json`、`report.md`。

### 3. 生产环境运行

```bash
export GITHUB_TOKEN=ghp_xxx          # 可选，避免 60 次/小时限流
export KIMI_API_KEY=sk-xxx           # 必须，否则自动降级为 mock 分析
python3 radar.py
```

### 4. 只分析已有数据

```bash
python3 radar.py --skip-fetch
```

### 5. 高级参数

```bash
python3 radar.py \
  --model kimi-k3 \
  --batch-size 14 \
  --body-limit 800 \
  --timeout 180 \
  --raw-path issues_raw_800.json
```

---

## 文件说明

| 文件 | 说明 |
|---|---|
| `radar.py` | 主脚本：抓取 + 分析 + 报告 |
| `requirements.txt` | Python 依赖 |
| `report.md` | 最终洞察报告 |
| `EVOLUTION.md` | 技术迭代链路：从 mock 到真实 API 的踩坑记录 |
| `INTERVIEW_SCRIPT.md` | 基于本项目整理的 DevRel 面试演讲稿 |
| `issues_raw.json` | 432 条原始 issue（body 截断 1500） |
| `issues_raw_800.json` | 432 条原始 issue（body 截断 800，用于快速分析） |
| `issues_analyzed.json` | 带 category / severity / evidence 的分析结果 |

---

## 设计亮点

### 受限分类体系

不让模型自由发挥，而是固定 8 个类目，每个对应归属方：

| 类目 | 归属方 | 含义 |
|---|---|---|
| `install_env` | 文档 | 安装、依赖、Node 版本、系统环境 |
| `ide_integration` | 产品 | VSCode / JetBrains / Zed 插件、ACP 协议接入 |
| `auth_billing` | 文档 | API key、鉴权、额度、计费 |
| `model_behavior` | 模型 | 模型输出质量、幻觉、不 follow 指令 |
| `agent_runtime` | 产品 | Agent 执行、工具调用、任务中断 |
| `docs_gap` | 文档 | 文档缺失、示例不可用、说明不清 |
| `feature_request` | 产品 | 功能诉求 |
| `other` | 兜底 | 其他 |

### 强制 evidence

每条分类必须附带 issue 原文片段，保证结论可追溯、可验证，而不是模型拍脑袋。

### 工程兜底

- 3 次指数退避重试
- JSON markdown 围栏自动剥离
- API 异常时打印模型返回预览
- 解析失败整批标记 `other`，不污染结论

---

## 踩坑记录

真实 API 调用中遇到的典型问题都记录在 [`EVOLUTION.md`](./EVOLUTION.md)，主要包括：

- Kimi API 当前所有模型只支持 `temperature=1`
- `kimi-k3` 对大批量长文本推理易超时，最终降级到 `kimi-k2.7-code-highspeed`
- `max_tokens` 不足会导致空返回或 JSON 截断，最终稳定在 12000
- batch size 从 18 降到 14 后，432 条 issue 全部分析成功

---

## 与 DevRel 岗位的关联

这个作品直接对应 Developer Relations (Content) Intern 的核心职责：

- **深入开发者社区**：抓取并分析 432 条真实 GitHub issue
- **从开发者视角体验产品**：自己调 Kimi API，踩过 temperature、max_tokens、超时等真实开发者会踩的坑
- **自动化反馈整理**：用 Python + Kimi API 把手动读帖变成结构化洞察
- **开发者文档优化**：报告中的洞察直接指向“文档该写什么”，如 K3 思考机制、静默挂起排查、额度预警
- **AI Coding 生态关注**：issue 覆盖 VSCode 插件、MCP、Agent 运行时等前沿工具链

---

## 后续可扩展方向

- [ ] 时间趋势分析：哪些类目在上升 / 下降
- [ ] 首次响应时长统计：社区运营健康度
- [ ] 自动生成“建议补充的文档条目”清单
- [ ] 接入 Discord / Reddit 等更多开发者社区数据源
- [ ] cron 化：每日/每周自动生成增量报告

---

## 作者

- GitHub: [@zhiman01](https://github.com/zhiman01)
- 本项目为 DevRel Content Intern 面试准备的作品
