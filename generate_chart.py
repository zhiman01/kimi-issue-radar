#!/usr/bin/env python3
"""从 issues_analyzed.json 生成可视化图表。"""

import json
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt


def set_chinese_font():
    plt.rcParams["font.sans-serif"] = ["Hiragino Sans GB", "SimHei", "Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False


def load_issues() -> list[dict]:
    data_path = Path("issues_analyzed.json")
    if not data_path.exists():
        raise FileNotFoundError("找不到 issues_analyzed.json，请先运行分析")
    return json.loads(data_path.read_text(encoding="utf-8"))


def plot_category_distribution(issues: list[dict]) -> None:
    categories = Counter(i.get("category", "other") for i in issues)
    categories = dict(categories.most_common())

    labels = list(categories.keys())
    values = list(categories.values())
    total = sum(values)

    label_map = {
        "feature_request": "功能诉求",
        "agent_runtime": "Agent 运行时",
        "ide_integration": "IDE 集成",
        "other": "其他",
        "install_env": "安装环境",
        "auth_billing": "鉴权计费",
        "docs_gap": "文档缺失",
        "model_behavior": "模型行为",
    }
    labels_cn = [label_map.get(l, l) for l in labels]

    colors = [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
        "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F",
    ]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(labels_cn[::-1], values[::-1], color=colors[::-1], edgecolor="white", height=0.6)

    for bar, val in zip(bars, values[::-1]):
        width = bar.get_width()
        ax.text(
            width + 2,
            bar.get_y() + bar.get_height() / 2,
            f"{val}  ({val / total * 100:.1f}%)",
            va="center",
            ha="left",
            fontsize=10,
            fontweight="bold",
        )

    ax.set_xlabel("Issue 数量", fontsize=12)
    ax.set_title(f"Kimi 社区 Issue 类目分布（n={total}）", fontsize=15, fontweight="bold", pad=15)
    ax.set_xlim(0, max(values) * 1.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.3, linestyle="--")

    plt.tight_layout()
    plt.savefig("category_distribution.png", dpi=150, bbox_inches="tight", facecolor="white")
    print("已生成 category_distribution.png")


def plot_severity_distribution(issues: list[dict]) -> None:
    severities = Counter(i.get("severity", "unknown") for i in issues)
    order = ["blocker", "friction", "nice_to_have"]
    labels = [s for s in order if s in severities]
    values = [severities[s] for s in labels]
    total = sum(values)

    label_map = {
        "blocker": "blocker：完全无法使用",
        "friction": "friction：能用但卡手",
        "nice_to_have": "nice_to_have：增强诉求",
    }
    labels_cn = [label_map.get(l, l) for l in labels]
    colors = ["#FF6B6B", "#FFA502", "#2ED573"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels_cn, values, color=colors, edgecolor="white", width=0.6)

    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 3,
            f"{val}\n({val / total * 100:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    ax.set_ylabel("Issue 数量", fontsize=12)
    ax.set_title(f"Severity 分布（n={total}）", fontsize=15, fontweight="bold", pad=15)
    ax.set_ylim(0, max(values) * 1.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3, linestyle="--")

    plt.tight_layout()
    plt.savefig("severity_distribution.png", dpi=150, bbox_inches="tight", facecolor="white")
    print("已生成 severity_distribution.png")


def plot_repo_comparison(issues: list[dict]) -> None:
    repos = Counter(i.get("repo", "unknown") for i in issues)
    repo_names = {
        "MoonshotAI/kimi-code": "kimi-code",
        "MoonshotAI/kimi-agent-sdk": "kimi-agent-sdk",
    }
    labels = [repo_names.get(r, r) for r in repos.keys()]
    values = list(repos.values())
    colors = ["#45B7D1", "#96CEB4"]

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.barh(labels, values, color=colors, edgecolor="white", height=0.5)

    for bar, val in zip(bars, values):
        width = bar.get_width()
        ax.text(
            width + 5,
            bar.get_y() + bar.get_height() / 2,
            str(val),
            va="center",
            ha="left",
            fontsize=12,
            fontweight="bold",
        )

    ax.set_xlabel("Issue 数量", fontsize=12)
    ax.set_title("两个仓库 Issue 数量对比", fontsize=15, fontweight="bold", pad=15)
    ax.set_xlim(0, max(values) * 1.15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.3, linestyle="--")

    plt.tight_layout()
    plt.savefig("repo_comparison.png", dpi=150, bbox_inches="tight", facecolor="white")
    print("已生成 repo_comparison.png")


def main() -> None:
    set_chinese_font()
    issues = load_issues()
    plot_category_distribution(issues)
    plot_severity_distribution(issues)
    plot_repo_comparison(issues)


if __name__ == "__main__":
    main()
