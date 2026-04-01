# VL-RAG-System 后端 API 设计文档

## 1. 系统基础 (System) — `api/routers/system.py`

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| GET | /api/status | 服务器及 ROS 节点健康检查 |
| GET | /api/health | 详细的服务依赖状态报告 |
| POST | /api/system/reset | 重置所有缓存及本地调度状态 |

---

## 2. 交互与对话 (Interaction) — `api/routers/chat.py`

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| POST | /api/chat/multimodal | 提交图文混合请求。Body: {image: file, question: str} |
| GET | /api/chat/stream | 流式获取机器人实时回复内容 |
| POST | /api/chat/interrupt | 强制打断当前机器人的语音输出与推理 |

---

## 3. 检索系统 (Retrieval) — `api/routers/rag.py`

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| POST | /api/rag/search | 多阶段RAG检索（向量检索 + 混合检索 + 重排序） |
| POST | /api/rag/rerank | 对候选结果进行重排序 |
| POST | /api/rag/ingest | 向知识库注入结构化数据（支持chunk） |
| GET | /api/rag/stats | 获取知识库统计信息 |

---

## 4. 记忆系统 (Memory) — `api/routers/memory.py`

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| GET | /api/memory/history | 获取当前会话的对话历史列表 |
| DELETE | /api/memory/clear | 清除当前用户的短时记忆缓存 |
| POST | /api/memory/summary | 触发生成当前长对话的阶段性摘要 |

---

## 5. 共鸣与 Agent (Resonance & Agent) — `api/routers/agent.py`

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| GET | /api/agent/state | 获取机器人当前任务规划及情感共鸣状态 |
| POST | /api/agent/vibe/set | 手动设定机器人的共鸣阈值。Body: {resonance: float} |
| GET | /api/agent/plan | 获取当前任务的 Step-by-Step 逻辑链 |
