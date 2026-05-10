"""api-lab-gemini-minimal

调用 Google Gemini 官方 API 一次。
注意：Gemini 官方接口不是 OpenAI-compatible（虽然 Google 也提供了一个兼容入口，本仓库故意用原生协议）。

Endpoint:
  POST https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}
Body:
  {
    "contents": [{"parts": [{"text": "..."}]}],
    "generationConfig": {"maxOutputTokens": 100}
  }
Response:
  candidates[0].content.parts[0].text
"""

import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

PROMPT = "请用初学者能懂的方式解释什么是多模态模型。"
ENDPOINT_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
TIMEOUT_SECONDS = 30
MAX_OUTPUT_TOKENS = 120


def main() -> int:
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "").strip()

    if not api_key:
        print("[错误] 未在 .env 中检测到 GEMINI_API_KEY。")
        print("       请运行: cp .env.example .env，然后填入真实 key。")
        return 2
    if not model:
        print("[错误] 未在 .env 中检测到 GEMINI_MODEL。")
        print("       请填入你账户可用的 Gemini 模型名（去 Google AI Studio 查）。")
        return 2

    url = ENDPOINT_TEMPLATE.format(model=model)
    # Gemini 把 key 放在 query 参数里；header 里也可以用 x-goog-api-key，本仓库用 query 形式更直观
    params = {"key": api_key}
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": PROMPT}]}],
        "generationConfig": {"maxOutputTokens": MAX_OUTPUT_TOKENS},
    }

    print(f"[信息] endpoint = {url}")
    print(f"[信息] model    = {model}")
    print(f"[信息] prompt   = {PROMPT}")

    started = time.time()
    try:
        resp = requests.post(
            url, headers=headers, params=params, json=payload, timeout=TIMEOUT_SECONDS
        )
    except requests.exceptions.Timeout:
        print(f"[失败] 请求超时（{TIMEOUT_SECONDS}s）。")
        return 1
    except requests.exceptions.RequestException as exc:
        print(f"[失败] 网络请求异常: {exc}")
        return 1
    elapsed = time.time() - started

    if resp.status_code != 200:
        print(f"[失败] HTTP {resp.status_code}")
        print(f"        响应片段: {resp.text[:300]}")
        print("        常见原因: API Key 无效 / 模型名错 / 当前地区不可用。")
        print("        提示：Gemini 在部分地区不开放，403 多半是地区限制。")
        return 1

    try:
        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            # 可能因为 safety filter 被拦截
            raise ValueError("no candidates returned (可能被 safety filter 拦截)")
        parts = candidates[0].get("content", {}).get("parts", [])
        text_pieces = [p.get("text", "") for p in parts if isinstance(p, dict)]
        content = "".join(text_pieces).strip()
        if not content:
            raise ValueError("no text parts")
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        print(f"[失败] 响应结构与预期不符: {exc}")
        print(f"        原始响应片段: {resp.text[:300]}")
        return 1

    print()
    print("[成功] 模型返回内容：")
    print(content)
    print()
    print(f"[信息] 耗时 {elapsed:.2f}s")

    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)
    result = {
        "provider": "gemini",
        "endpoint": url,
        "model": model,
        "prompt": PROMPT,
        "elapsed_seconds": round(elapsed, 3),
        "content": content,
    }
    out_file = out_dir / "result.json"
    out_file.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[信息] 已写入 {out_file}（不会被 git 提交）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
