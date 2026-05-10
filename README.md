# api-lab-gemini-minimal

> 最小化体验：调用 Google Gemini 原生 API 一次。

> 想"通过实操验证理解"而不是"只把代码跑通"？请先翻 [`LEARNING.md`](./LEARNING.md)：
> 里面有 **学习目标 / 实操验证清单 / 自检题 / 跟其它仓库的连接**。本 README 主要负责"具体怎么跑"。

## 它在做什么 / 为什么单独一仓

Google 提供了两套入口：

1. 原生：`https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`
2. OpenAI-compatible 镜像入口（也存在）

本仓库**故意用原生**，让你看到 Gemini 的请求/响应结构和 OpenAI 那一套完全不一样：

- key 不放 header，放 URL query：`?key=...`
- body 用 `contents -> parts -> text`，而不是 `messages -> role/content`
- 响应里取文本走 `candidates[0].content.parts[0].text`
- 触发 safety filter 时会返回空 candidates

理解这点之后，你以后看任何"另一家自己定义协议"的模型 API 都会很快上手。

## 运行步骤

```bash
cd api-lab-gemini-minimal
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# 编辑 .env：
#   GEMINI_API_KEY=AIza...
#   GEMINI_MODEL=（去 Google AI Studio 看你账户可用的模型名）

python3 main.py
cat output/result.json
```

## 常见报错

| 终端打印 | 可能原因 | 怎么处理 |
| --- | --- | --- |
| `未在 .env 中检测到 GEMINI_API_KEY` | 没填 key | `cp .env.example .env` 后填 |
| `HTTP 400` | 请求体格式错 | 检查 `contents/parts` 结构 |
| `HTTP 401` / `HTTP 403` | key 错或当前地区不可用 | 检查 key；Gemini 在部分地区不开放，403 多半是地区限制 |
| `HTTP 404` model not found | 模型名错或在你账户不可用 | 去 AI Studio 拿一个能用的填上 |
| `no candidates returned` | 触发了安全过滤 | 换个无害 prompt 再试，不要硬刚 safety filter |
| `请求超时` | 网络问题 | 不要反复重试 |

## 关于多模态

本仓库**只**测了"文本输入 → 文本输出"。Gemini 真正的卖点是图片/音频/视频也能塞进 `parts`，
等你跑通这一份再玩多模态：

```python
# 伪代码思路（本仓库不实现）
"contents": [
    {"parts": [
        {"text": "请描述这张图"},
        {"inline_data": {"mime_type": "image/png", "data": "<base64>"}}
    ]}
]
```

## .env.example

```
GEMINI_API_KEY=填入你的Gemini API Key
GEMINI_MODEL=填入你账户可用的Gemini模型名
```

## 不会做的事

- 不会自动重试
- 不会打印 API Key
- 不会硬编码最新模型名
- 不会自动绕过 safety filter
