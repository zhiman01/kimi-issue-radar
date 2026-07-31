# 常见问题排查

本文档汇总运行雷达过程中可能遇到的问题，以及对应解决方法。

---

## 问题 1：运行时报 `KIMI_API_KEY not set`，自动降级为 mock

### 现象

```
未设置 KIMI_API_KEY，切换为 mock 分析结果
```

### 原因

环境变量里没有 `KIMI_API_KEY`。

### 解决

```bash
export KIMI_API_KEY=sk-xxx
```

或者在项目根目录创建 `.env` 文件（参考 `.env.example`）：

```
KIMI_API_KEY=sk-xxx
GITHUB_TOKEN=ghp_xxx
```

> ⚠️ **不要把 `.env` 提交到 GitHub**。项目 `.gitignore` 已默认忽略 `.env`。

---

## 问题 2：GitHub 抓取很慢或触发 403 rate limit

### 现象

```
获取 MoonshotAI/kimi-code page X 失败：403 Client Error
```

### 原因

未配置 `GITHUB_TOKEN` 时，GitHub API 限流为 60 次/小时。抓取大仓库容易触顶。

### 解决

配置 Personal Access Token：

```bash
export GITHUB_TOKEN=ghp_xxx
```

Token 只需 `public_repo` 权限即可读取公开仓库 issue。

---

## 问题 3：Kimi API 返回 `invalid temperature`

### 现象

```json
{"error": {"message": "invalid temperature: only 1 is allowed for this model"}}
```

### 原因

Moonshot API 当前对所有可用模型锁定 `temperature=1`，不支持 `0.2` 等常见值。

### 解决

无需解决，代码已固定 `temperature=1.0`。如需换模型，用 `--model` 参数即可。

---

## 问题 4：大 batch 超时或返回空内容

### 现象

```
批次 X 分析失败：Read timed out.
```

或：

```
模型返回内容解析失败（…）：Expecting value: line 1 column 1
```

### 原因

- batch size 太大 + body 太长，超过模型处理速度
- `max_tokens` 不足，导致输出被截断或为空

### 解决

减小 batch size 或 body 长度：

```bash
python3 radar.py --batch-size 10 --body-limit 800 --timeout 180
```

当前默认配置（batch=14, body=800, max_tokens=12000）已经过实测稳定。

---

## 问题 5：JSON 解析失败

### 现象

```
parse err Unterminated string starting at...
```

### 原因

模型返回的内容被截断，或带了 markdown 围栏。

### 解决

代码里已经做了 markdown 围栏剥离和重试兜底：

```python
text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
text = re.sub(r"^```\s*", "", text)
text = re.sub(r"\s*```$", "", text)
```

如果仍失败，该 batch 会被标记为 `other`，不会污染整体结果。

---

## 问题 6：报告里的类目分布和我不一样

### 原因

- 抓取的是近期 issue，GitHub 数据每天都在变
- 模型对同一条 issue 的分类可能有轻微差异
- 默认是采样（`max_pages=10`），不是全量

### 解决

如需固定结果，可以：

1. 保存一份 `issues_raw.json`
2. 用 `--skip-fetch --raw-path issues_raw.json` 重新分析

这样只跑分析层，结果可复现。

---

## 更多问题

如果以上没有覆盖你的问题，欢迎在 issue 里描述：

- 运行命令
- 完整报错信息
- 是否使用了自定义参数
