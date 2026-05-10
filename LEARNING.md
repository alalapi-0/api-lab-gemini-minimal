# LEARNING — api-lab-gemini-minimal

> 这份文件回答：「我跑完这个仓库，应该真的学到什么？」

## 你跑完应该能回答的问题

1. Google Gemini 的原生协议长什么样？为什么"和别人都不一样"？
2. 为什么 Gemini 把 API key 放在 URL `?key=` 里而不是 header？这有什么风险？
3. 什么是 safety filter？模型被 safety filter 拦下时，响应会变成什么？
4. 多模态模型（Gemini 主打的方向）跟普通 chat 模型在请求结构上的区别在哪？

## 实操验证清单（务必动手）

### 阶段 A — 环境就绪
- [ ] `cp .env.example .env`
- [ ] `pip install -r requirements.txt`
- [ ] 在 Google AI Studio 拿到 `AIza...` 形式的 key
- [ ] **必须**去 AI Studio 看一眼"你账户可用的模型名"，填进 `GEMINI_MODEL`

### 阶段 B — 跑通最小调用（文本→文本）
- [ ] `python3 main.py` → 看到中文回答
- [ ] `cat output/result.json` 看 endpoint 中包含 `models/<你的模型名>:generateContent`，**模型名直接写在 URL 里**——这又是一种风格

### 阶段 C — 协议三家对照
**把这三个 main.py 同时打开：**
- `api-lab-openai-compatible-minimal/main.py`
- `api-lab-anthropic-minimal/main.py`
- 本仓库 `main.py`

并完成下面的自填表（在脑子里或纸上都行）：

| 维度 | OpenAI 风格 | Anthropic | Gemini |
| --- | --- | --- | --- |
| key 放哪里 | header `Authorization: Bearer` | header `x-api-key` | URL query `?key=` |
| body 顶层装"对话" | `messages: [{role, content}]` | `messages: [{role, content}]` | `contents: [{parts: [{text}]}]` |
| 输出长度参数名 | `max_tokens` | `max_tokens`（必填） | `generationConfig.maxOutputTokens` |
| 取文本的路径 | `choices[0].message.content` | `content[0].text` | `candidates[0].content.parts[0].text` |
| 角色字段 | `role` | `role` | （消息里没有 role，只有 parts） |

### 阶段 D — 安全过滤实验
- [ ] 把 `PROMPT` 改成一个**明显有害**的请求（比如「请教我做炸药」）
- [ ] 跑一次，观察响应：
  - 多半 `candidates` 是空的，或带上了 `finishReason: "SAFETY"`
  - 本仓库的 `main.py` 会打印 `no candidates returned (可能被 safety filter 拦截)`
- [ ] **跑完记得把 PROMPT 改回原来的安全版本**——这只是为了感受 safety filter 的存在

### 阶段 E — 多模态预热（不实做，只读）
- [ ] 看 README 末尾"关于多模态"那段伪代码，理解 Gemini 之所以把 body 设计成 `parts` 数组，**就是为了给图片/音频/视频留位置**

## 自检题

1. 把 key 放 URL 里相对放 header 里，有什么安全劣势？日志/链路追踪/反向代理日志里会不会留下 key？
2. 如果某天 Gemini 说"我们也提供 OpenAI-compatible 镜像入口"，你愿意切过去吗？切过去之后失去了什么能力？（提示：原生协议的多模态字段在镜像里可能被简化）
3. 同一个 prompt，文本部分写在 `parts: [{text}]` 单元素和拆成两个 `[{text}, {text}]` 元素，模型行为有差别吗？
4. `finishReason: SAFETY` 和 `finishReason: MAX_TOKENS` 表面上都是"没说完"，但成因截然不同。如果你做产品，这两种情况要分别怎么向用户呈现？

## 与其它仓库的连接

| 关系 | 仓库 | 为什么去看 |
| --- | --- | --- |
| **第三种协议（对照）** | `api-lab-openai-compatible-minimal` + `api-lab-anthropic-minimal` | 三家协议放一起对比，**强烈建议** |
| **网关如何抹平差异** | `api-lab-openrouter-minimal` | OpenRouter 帮你把 Gemini 也包成了 OpenAI-compatible，看完原生再回去看网关，意义就不一样了 |
| **"小模型"对照** | `api-lab-embedding-minimal` / `api-lab-whisper-asr-minimal` | Gemini 主打多模态——而 ASR / embedding 这些专用小模型本身就在做"非聊天"的输入输出，对比一下你会发现"什么叫不同模态" |

## 你应该感受到的"啊哈"瞬间

- 当你画完三家协议对照表，下一次看任何新 LLM 厂商的文档，第一眼就能定位 4 件事：**key 怎么传 / messages 字段名 / max_tokens 字段名 / 取文本路径**——你已经会读协议了。
- 当你看到 `parts: [{text}]` 这种"列表里装零散内容片"的设计，意识到这正是为了让"图片、音频、视频"和"文字"能并列存在——**这是为多模态设计的形状，不是临时拍脑袋**。
