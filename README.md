# Kimi 社区 Issue 洞察雷达

按预定义类目对 MoonshotAI 开源仓库的 GitHub Issues 做聚类与归因，输出 DevRel 洞察报告。

## 用法

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 无 key 时跑 mock 全流程（验证脚本与报告格式）
python3 radar.py --mock

# 3. 生产环境：设置 token 后执行
export GITHUB_TOKEN=ghp_xxx          # 可选，避免 60 次/小时限流
export KIMI_API_KEY=sk-xxx           # 必须，否则自动降级为 mock 分析
python3 radar.py

# 4. 只分析已抓取的 issues_raw.json，不再打 GitHub
python3 radar.py --skip-fetch

# 5. 高级：换模型、调 batch、调 body 长度、调超时
python3 radar.py --model kimi-k3 --batch-size 10 --body-limit 800 --timeout 180
```

## 输出

- `issues_raw.json`：过滤后的原始 issue 数据
- `issues_analyzed.json`：带 category / severity / evidence 的分析结果
- `report.md`：最终洞察报告

## 设计要点

- PR 过滤：通过 `pull_request` 字段存在性剔除混在 issues 里的 PR。
- 分批：默认每批 18 条送入 Kimi API，避免单次上下文过长；可用 `--batch-size` 调整。
- 重试：GitHub / Kimi API 均包 3 次指数退避重试。
- JSON 容错：先 strip ` ```json ` 围栏再解析；解析失败会打印模型返回预览。
- Mock 兜底：无 `KIMI_API_KEY` 或指定 `--mock` 时，用规则启发式跑通全流程。
- 模型默认：`kimi-k2.7-code-highspeed`（K3 对大批量推理易超时，可用 `--model` 切换）。
