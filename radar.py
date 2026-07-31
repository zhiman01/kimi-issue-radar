#!/usr/bin/env python3
"""
Kimi 社区 Issue 洞察雷达
自动抓取 MoonshotAI 开源仓库 GitHub Issues，用 Kimi API 聚类归因，生成 DevRel 报告。
"""

import argparse
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

# ---------- 配置 ----------
DEFAULT_REPOS = [
    "MoonshotAI/kimi-code",
    "MoonshotAI/kimi-agent-sdk",
]
GITHUB_API = "https://api.github.com/repos/{owner}/{repo}/issues"
KIMI_API = "https://api.moonshot.cn/v1/chat/completions"
DEFAULT_MODEL = "kimi-k2.7-code-highspeed"  # K3 对大批量推理较慢，这里降级到高速版
BODY_TRUNCATE = 1500
BATCH_SIZE = 14  # 实测 18 条在 8k max_tokens 下易截断，14 条更稳
REQUEST_TIMEOUT = 180  # 大 batch 推理可能耗时较久
MAX_RETRIES = 3
BACKOFF_BASE = 2  # 秒

REQUIRED_FIELDS = ["number", "title", "body", "state", "labels", "created_at", "closed_at", "comments", "html_url"]

CATEGORY_DEFS = {
    "install_env": "安装、依赖、Node 版本、系统环境 — 文档",
    "ide_integration": "VSCode / JetBrains / Zed 插件、ACP 协议接入 — 产品",
    "auth_billing": "API key、鉴权、额度、计费 — 文档",
    "model_behavior": "模型输出质量、幻觉、不 follow 指令 — 模型",
    "agent_runtime": "Agent 执行、工具调用、任务中断 — 产品",
    "docs_gap": "文档缺失、示例不可用、说明不清 — 文档",
    "feature_request": "功能诉求 — 产品",
    "other": "兜底",
}

PROMPT_TEMPLATE = """你是开发者反馈分析员。对下列 GitHub issue 做受限分类。

铁律：
1. category 只能从给定枚举中选，不得自造新类目。
2. 每条必须给出 evidence，且 evidence 必须是 issue 原文的连续片段，不得改写、不得概括。
3. 若信息不足以判断类目，category 填 "other"，不要猜测。
4. 只输出 JSON 数组，不要任何前言、后语、markdown 围栏。

可用 category 枚举（含义与归属方）：
{category_defs}

severity 定义：
- blocker：完全用不了
- friction：能用但卡手
- nice_to_have：增强诉求

每条记录必须包含字段：number, category, severity, one_line, evidence。

待分析 issues：
{issues}
"""

REPORT_TEMPLATE = """# Kimi 社区 Issue 洞察报告

生成时间：{generated_at}

## 1. 总体概况

| 指标 | 数值 |
|---|---|
| 仓库数 | {repo_count} |
| Issue 总量 | {total} |
| Open 数 | {open_count} |
| Closed 数 | {closed_count} |
| Open/Closed 比例 | {open_closed_ratio} |
| 时间跨度 | {time_span} |
| 分析模型 | {model} |

## 2. 类目分布

| 排名 | 类目 | 数量 | 占比 | 归属方 |
|---|---:|---:|---:|---|
{category_rows}

## 3. Blocker 级问题清单

{blocker_list}

## 4. Top 3 洞察

{top_insights}

---
*本报告由 Kimi 社区 Issue 洞察雷达自动生成。*
"""


# ---------- 工具函数 ----------
def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def truncate(text: str | None, max_len: int = BODY_TRUNCATE) -> str:
    if not text:
        return ""
    return text[:max_len] + ("…[truncated]" if len(text) > max_len else "")


def retry_request(func, max_retries: int = MAX_RETRIES, backoff_base: int = BACKOFF_BASE):
    """指数退避重试包装。"""
    last_exc = None
    for attempt in range(max_retries):
        try:
            return func()
        except requests.RequestException as e:
            last_exc = e
            wait = backoff_base * (2 ** attempt)
            log(f"请求失败（{attempt + 1}/{max_retries}）：{e}，{wait}s 后重试…")
            time.sleep(wait)
    raise last_exc


def parse_json_robust(text: str) -> list[dict]:
    """剥离 markdown 围栏并解析 JSON。"""
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # 尝试再剥一层
        m = re.search(r"\[.*\]", text, re.DOTALL)
        if m:
            return json.loads(m.group(0))
        raise e


# ---------- 抓取 ----------
def fetch_repo_issues(repo: str, token: str | None = None, max_pages: int = 10, body_limit: int = BODY_TRUNCATE) -> list[dict]:
    owner, name = repo.split("/")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    issues = []
    for page in range(1, max_pages + 1):
        url = GITHUB_API.format(owner=owner, repo=name)
        params = {"state": "all", "per_page": 100, "page": page}

        def do_request():
            resp = requests.get(url, headers=headers, params=params, timeout=30)
            resp.raise_for_status()
            return resp

        try:
            resp = retry_request(do_request)
        except requests.RequestException as e:
            log(f"获取 {repo} page {page} 失败：{e}")
            break

        data = resp.json()
        if not data:
            break

        for item in data:
            # GitHub /issues 接口会把 PR 混进来
            if item.get("pull_request") is not None:
                continue
            issues.append({
                "repo": repo,
                "number": item["number"],
                "title": item.get("title", ""),
                "body": truncate(item.get("body") or "", body_limit),
                "state": item.get("state", ""),
                "labels": [label.get("name", "") for label in item.get("labels", [])],
                "created_at": item.get("created_at", ""),
                "closed_at": item.get("closed_at", ""),
                "comments": item.get("comments", 0),
                "html_url": item.get("html_url", ""),
            })

        # GitHub 不会返回 total，但一页不满说明到底
        if len(data) < 100:
            break

        # 保守：无 token 时 60 次/小时， sleep 一下
        if not token:
            time.sleep(0.6)

    log(f"{repo} 抓取完成：{len(issues)} 条有效 issue")
    return issues


def fetch_all(repos: list[str], token: str | None = None, body_limit: int = BODY_TRUNCATE) -> list[dict]:
    all_issues = []
    for repo in repos:
        all_issues.extend(fetch_repo_issues(repo, token, body_limit=body_limit))
    return all_issues


# ---------- 分析 ----------
def build_batch_prompt(batch: list[dict]) -> str:
    category_lines = "\n".join([f"- {k}: {v}" for k, v in CATEGORY_DEFS.items()])
    issues_json = json.dumps(batch, ensure_ascii=False, indent=2)
    return PROMPT_TEMPLATE.format(category_defs=category_lines, issues=issues_json)


def analyze_batch(batch: list[dict], api_key: str, model: str, timeout: int = REQUEST_TIMEOUT) -> list[dict]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一名严谨的开发者反馈分析员，只输出严格 JSON。"},
            {"role": "user", "content": build_batch_prompt(batch)},
        ],
        "temperature": 1.0,  # Moonshot 当前模型只支持 temperature=1
        "max_tokens": 12000,  # 保证 14 条 issue 的完整 JSON 输出不被截断
    }

    def do_request():
        resp = requests.post(KIMI_API, headers=headers, json=payload, timeout=timeout)
        if resp.status_code >= 400:
            # 把服务端错误详情抛出来，方便排查模型参数问题
            body = resp.text[:500]
            raise requests.HTTPError(f"{resp.status_code} {resp.reason}: {body}", response=resp)
        resp.raise_for_status()
        return resp

    resp = retry_request(do_request)
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    try:
        return parse_json_robust(content)
    except json.JSONDecodeError as e:
        # 把模型返回内容打印出来，方便排查格式/空内容问题
        preview = content[:500].replace("\n", " ")
        raise json.JSONDecodeError(f"模型返回内容解析失败（{preview}…）：{e}", e.doc, e.pos) from e


def analyze_issues(issues: list[dict], api_key: str, model: str, batch_size: int = BATCH_SIZE, timeout: int = REQUEST_TIMEOUT) -> list[dict]:
    analyzed = []
    total_batches = (len(issues) + batch_size - 1) // batch_size
    for i in range(total_batches):
        batch = issues[i * batch_size : (i + 1) * batch_size]
        log(f"分析批次 {i + 1}/{total_batches}（{len(batch)} 条）…")
        try:
            results = analyze_batch(batch, api_key, model, timeout=timeout)
        except Exception as e:
            log(f"批次 {i + 1} 分析失败：{e}")
            # 失败时全部标记为 other，避免中断
            results = [
                {
                    "number": issue["number"],
                    "category": "other",
                    "severity": "friction",
                    "one_line": "分析失败，待人工复核",
                    "evidence": "",
                }
                for issue in batch
            ]

        # 把分析结果 merge 回原始 issue
        for issue, result in zip(batch, results):
            merged = {**issue, **result}
            merged.setdefault("category", "other")
            merged.setdefault("severity", "friction")
            merged.setdefault("one_line", issue.get("title", "")[:15])
            merged.setdefault("evidence", "")
            analyzed.append(merged)

        # 简单限流，避免触发 TPM/RPM
        if i < total_batches - 1:
            time.sleep(0.5)

    return analyzed


# ---------- 报告 ----------
def format_time_span(issues: list[dict]) -> str:
    dates = [i["created_at"] for i in issues if i.get("created_at")]
    if not dates:
        return "无"
    sorted_dates = sorted(dates)
    return f"{sorted_dates[0][:10]} ~ {sorted_dates[-1][:10]}"


def generate_report(analyzed: list[dict], model: str, repos: list[str]) -> str:
    total = len(analyzed)
    open_count = sum(1 for i in analyzed if i.get("state") == "open")
    closed_count = total - open_count
    ratio = f"{open_count}:{closed_count}" if closed_count else f"{open_count}:0"

    categories = Counter(i.get("category", "other") for i in analyzed)
    category_rows = []
    for rank, (cat, count) in enumerate(categories.most_common(), 1):
        pct = count / total * 100 if total else 0
        owner = CATEGORY_DEFS.get(cat, "其他").split(" — ")[-1]
        category_rows.append(
            f"| {rank} | `{cat}` | {count} | {pct:.1f}% | {owner} |"
        )

    blockers = [i for i in analyzed if i.get("severity") == "blocker"]
    if blockers:
        blocker_lines = []
        for i in blockers:
            blocker_lines.append(
                f"- **#{i['number']}** [{i.get('title', '')}]({i.get('html_url', '')})\n"
                f"  - 类目：`{i.get('category')}` | 证据：{i.get('evidence', '无')[:120]}…"
            )
        blocker_list = "\n".join(blocker_lines)
    else:
        blocker_list = "_未识别到 blocker 级问题。_"

    # Top 3 洞察：基于分布和 blocker 人工生成
    top_cat = categories.most_common(3)
    insights = []
    if top_cat:
        name, count = top_cat[0]
        owner = CATEGORY_DEFS.get(name, "").split(" — ")[-1]
        insights.append(
            f"1. **{CATEGORY_DEFS.get(name, name)}问题最集中**："
            f"共 {count} 条，占 {count/total*100:.1f}%。"
            f"建议 {owner} 团队优先梳理该场景下的高频卡点，补充 FAQ 或排障指南。"
        )
    if len(top_cat) > 1:
        name, count = top_cat[1]
        owner = CATEGORY_DEFS.get(name, "").split(" — ")[-1]
        insights.append(
            f"2. **{CATEGORY_DEFS.get(name, name)}位居第二**："
            f"{count} 条反馈。建议 {owner} 侧 review 相关流程，识别是否因设计不一致导致重复提问。"
        )
    if blockers:
        cat_counter = Counter(i.get("category") for i in blockers)
        top_blocker_cat = cat_counter.most_common(1)[0]
        insights.append(
            f"3. **{len(blockers)} 个 blocker 需立即跟进**："
            f"其中 `{top_blocker_cat[0]}` 类最多（{top_blocker_cat[1]} 条）。"
            f"建议按 repo 建立 blocker 看板，逐条确认修复或文档兜底方案。"
        )
    else:
        insights.append(
            "3. **当前样本中无 blocker 级问题**：社区健康度较好，"
            "可继续监控 friction 类问题是否向 blocker 转化。"
        )

    return REPORT_TEMPLATE.format(
        generated_at=datetime.now().isoformat(),
        repo_count=len(repos),
        total=total,
        open_count=open_count,
        closed_count=closed_count,
        open_closed_ratio=ratio,
        time_span=format_time_span(analyzed),
        model=model,
        category_rows="\n".join(category_rows),
        blocker_list=blocker_list,
        top_insights="\n\n".join(insights),
    )


# ---------- CLI ----------
def load_mock_issues() -> list[dict]:
    mock_path = Path(__file__).with_name("mock_issues.json")
    if not mock_path.exists():
        log("未找到 mock_issues.json，使用内置样例")
        return _built_in_mock()
    with open(mock_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _built_in_mock() -> list[dict]:
    return [
        {
            "repo": "MoonshotAI/kimi-code",
            "number": 101,
            "title": "npm install 后执行 kimi 报 command not found",
            "body": "环境：macOS 14，Node 18。按 README 执行 `npm install -g kimi-code` 后，终端输入 `kimi` 提示 command not found。",
            "state": "open",
            "labels": ["bug"],
            "created_at": "2026-07-20T10:00:00Z",
            "closed_at": "",
            "comments": 3,
            "html_url": "https://github.com/MoonshotAI/kimi-code/issues/101",
        },
        {
            "repo": "MoonshotAI/kimi-code",
            "number": 102,
            "title": "VSCode 插件无法识别已登录状态",
            "body": "在 VSCode 里已经用 CLI 登录过，但插件侧边栏仍提示请登录。重启编辑器无效。",
            "state": "open",
            "labels": ["bug", "vscode"],
            "created_at": "2026-07-21T12:00:00Z",
            "closed_at": "",
            "comments": 5,
            "html_url": "https://github.com/MoonshotAI/kimi-code/issues/102",
        },
        {
            "repo": "MoonshotAI/kimi-code",
            "number": 103,
            "title": "希望支持 JetBrains 系列 IDE",
            "body": "目前只有 VSCode 插件，团队主要用 PyCharm/WebStorm，希望能提供 JetBrains 插件或兼容 ACP 协议。",
            "state": "open",
            "labels": ["feature-request"],
            "created_at": "2026-07-22T09:00:00Z",
            "closed_at": "",
            "comments": 12,
            "html_url": "https://github.com/MoonshotAI/kimi-code/issues/103",
        },
        {
            "repo": "MoonshotAI/kimi-code",
            "number": 104,
            "title": "API key 已创建但调用提示 401",
            "body": "在平台创建了 key，复制到 .env 后调用接口返回 401 Unauthorized。文档里没写 key 格式要不要带 Bearer。",
            "state": "closed",
            "labels": ["docs"],
            "created_at": "2026-07-15T08:00:00Z",
            "closed_at": "2026-07-16T10:00:00Z",
            "comments": 2,
            "html_url": "https://github.com/MoonshotAI/kimi-code/issues/104",
        },
        {
            "repo": "MoonshotAI/kimi-code",
            "number": 105,
            "title": "Agent 模式执行到一半任务中断",
            "body": "让 agent 帮我重构一个文件，执行到第 5 步时报错退出，没有保存中间结果。",
            "state": "open",
            "labels": ["bug", "agent"],
            "created_at": "2026-07-23T14:00:00Z",
            "closed_at": "",
            "comments": 8,
            "html_url": "https://github.com/MoonshotAI/kimi-code/issues/105",
        },
        {
            "repo": "MoonshotAI/kimi-agent-sdk",
            "number": 201,
            "title": "模型不 follow 系统指令，输出格式错乱",
            "body": "系统 prompt 要求输出 JSON，但模型经常带 markdown 代码围栏，导致 json.loads 失败。",
            "state": "open",
            "labels": ["bug"],
            "created_at": "2026-07-18T11:00:00Z",
            "closed_at": "",
            "comments": 6,
            "html_url": "https://github.com/MoonshotAI/kimi-agent-sdk/issues/201",
        },
        {
            "repo": "MoonshotAI/kimi-agent-sdk",
            "number": 202,
            "title": "工具调用返回后没有继续执行",
            "body": "自定义 tool 返回结果后，agent 直接结束对话，没有基于 tool 结果继续回答用户问题。",
            "state": "open",
            "labels": ["bug"],
            "created_at": "2026-07-19T13:00:00Z",
            "closed_at": "",
            "comments": 4,
            "html_url": "https://github.com/MoonshotAI/kimi-agent-sdk/issues/202",
        },
        {
            "repo": "MoonshotAI/kimi-agent-sdk",
            "number": 203,
            "title": "pip install 报错依赖冲突",
            "body": "Python 3.12 下 `pip install kimi-agent-sdk` 提示 openai 1.x 与现有环境冲突。",
            "state": "closed",
            "labels": ["bug"],
            "created_at": "2026-07-10T07:00:00Z",
            "closed_at": "2026-07-12T09:00:00Z",
            "comments": 3,
            "html_url": "https://github.com/MoonshotAI/kimi-agent-sdk/issues/203",
        },
        {
            "repo": "MoonshotAI/kimi-agent-sdk",
            "number": 204,
            "title": "文档里没有多 agent 协作示例",
            "body": "想找多个 agent 互相调用的例子，官方文档只有单 agent 的 hello world。",
            "state": "open",
            "labels": ["docs"],
            "created_at": "2026-07-24T10:00:00Z",
            "closed_at": "",
            "comments": 1,
            "html_url": "https://github.com/MoonshotAI/kimi-agent-sdk/issues/204",
        },
        {
            "repo": "MoonshotAI/kimi-agent-sdk",
            "number": 205,
            "title": "计费页没有显示 token 消耗明细",
            "body": "调用 API 后账单只显示总金额，希望像 OpenAI 一样展示 input/output token 数。",
            "state": "open",
            "labels": ["feature-request"],
            "created_at": "2026-07-25T16:00:00Z",
            "closed_at": "",
            "comments": 7,
            "html_url": "https://github.com/MoonshotAI/kimi-agent-sdk/issues/205",
        },
        {
            "repo": "MoonshotAI/kimi-code",
            "number": 106,
            "title": "Windows 下路径解析错误",
            "body": "在 Windows PowerShell 里执行，文件路径里的反斜杠被当成转义符，导致读取失败。",
            "state": "open",
            "labels": ["bug"],
            "created_at": "2026-07-26T08:00:00Z",
            "closed_at": "",
            "comments": 2,
            "html_url": "https://github.com/MoonshotAI/kimi-code/issues/106",
        },
        {
            "repo": "MoonshotAI/kimi-code",
            "number": 107,
            "title": "建议支持深色主题",
            "body": "终端主题只有浅色，晚上使用刺眼，希望能跟随系统主题。",
            "state": "open",
            "labels": ["feature-request"],
            "created_at": "2026-07-27T09:00:00Z",
            "closed_at": "",
            "comments": 0,
            "html_url": "https://github.com/MoonshotAI/kimi-code/issues/107",
        },
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Kimi 社区 Issue 洞察雷达")
    parser.add_argument("--repos", nargs="+", default=DEFAULT_REPOS, help="目标仓库，默认 MoonshotAI/kimi-code MoonshotAI/kimi-agent-sdk")
    parser.add_argument("--mock", action="store_true", help="使用内置/本地 mock 数据跑通全流程")
    parser.add_argument("--skip-fetch", action="store_true", help="不抓 GitHub，直接分析现有 issues_raw.json")
    parser.add_argument("--raw-path", default="issues_raw.json", help="原始 issue 文件路径（配合 --skip-fetch）")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Kimi 模型名")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help="每批送入模型的 issue 数")
    parser.add_argument("--body-limit", type=int, default=BODY_TRUNCATE, help="抓取时 issue body 截断长度")
    parser.add_argument("--timeout", type=int, default=REQUEST_TIMEOUT, help="Kimi API 请求超时秒数")
    parser.add_argument("--output", default="report.md", help="报告输出路径")
    args = parser.parse_args()

    raw_path = Path(args.raw_path)
    analyzed_path = Path("issues_analyzed.json")

    # 1. 获取数据
    if args.mock:
        log("进入 mock 模式，读取样例数据")
        issues = load_mock_issues()
        raw_path.write_text(json.dumps(issues, ensure_ascii=False, indent=2), encoding="utf-8")
    elif args.skip_fetch:
        if not raw_path.exists():
            log(f"找不到 {raw_path}，无法跳过抓取")
            return 1
        log(f"跳过抓取，读取 {raw_path}")
        issues = json.loads(raw_path.read_text(encoding="utf-8"))
    else:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            log("警告：未设置 GITHUB_TOKEN，将使用无 token 模式（限流 60 次/小时）")
            log("建议 export GITHUB_TOKEN=your_pat 以避免被限流")
        log(f"开始抓取仓库：{args.repos}，body 截断={args.body_limit}")
        issues = fetch_all(args.repos, token, body_limit=args.body_limit)
        raw_path.write_text(json.dumps(issues, ensure_ascii=False, indent=2), encoding="utf-8")
        log(f"原始数据已保存：{raw_path}（{len(issues)} 条）")

    if not issues:
        log("没有可用 issue，结束")
        return 0

    # 2. 分析
    api_key = os.environ.get("KIMI_API_KEY")
    if args.mock or not api_key:
        if not args.mock:
            log("未设置 KIMI_API_KEY，切换为 mock 分析结果")
        # mock 模式下用简单规则模拟模型输出，保证流程跑通
        analyzed = []
        for issue in issues:
            title = issue.get("title", "")
            body = issue.get("body", "")
            text = (title + " " + body).lower()
            if "install" in text or "npm" in text or "pip" in text or "依赖" in text or "command not found" in text:
                cat = "install_env"
            elif "vscode" in text or "jetbrains" in text or "ide" in text or "插件" in text:
                cat = "ide_integration"
            elif "api key" in text or "401" in text or "计费" in text or "额度" in text:
                cat = "auth_billing"
            elif "文档" in text or "示例" in text or "readme" in text:
                cat = "docs_gap"
            elif "模型" in text or "幻觉" in text or "不 follow" in text:
                cat = "model_behavior"
            elif "agent" in text or "工具调用" in text or "任务中断" in text:
                cat = "agent_runtime"
            elif "希望" in text or "建议" in text or "feature" in text:
                cat = "feature_request"
            else:
                cat = "other"

            if "完全用不了" in text or "blocker" in text or "command not found" in text or "401" in text:
                severity = "blocker"
            elif "希望" in text or "建议" in text or "feature" in text or "深色主题" in text:
                severity = "nice_to_have"
            else:
                severity = "friction"

            analyzed.append({
                **issue,
                "category": cat,
                "severity": severity,
                "one_line": title[:15],
                "evidence": body[:150] or title,
            })
    else:
        log(f"开始用模型 {args.model} 分析 {len(issues)} 条 issue，batch={args.batch_size}，timeout={args.timeout}s…")
        analyzed = analyze_issues(issues, api_key, args.model, batch_size=args.batch_size, timeout=args.timeout)

    analyzed_path.write_text(json.dumps(analyzed, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"分析结果已保存：{analyzed_path}")

    # 3. 生成报告
    report = generate_report(analyzed, args.model, args.repos)
    Path(args.output).write_text(report, encoding="utf-8")
    log(f"报告已生成：{args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
