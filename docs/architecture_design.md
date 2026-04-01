# VL-RAG-System 架构设计文档

本文档定义了“技心”多模态交互机器人的核心模块规范与交互逻辑。

## 1. 系统总控 (System Orchestrator)
**文件**: `local_model_processor.py`  
**职责**: 全局状态机，协调感知输入、智能决策与执行层调度，充当整个机器人的“中枢神经”。

**持有的子系统**:
- `llm_system`: LanguageSystem — 语言/逻辑系统
- `retrieval_system`: RetrievalSystem — 知识检索系统
- `memory_system`: MemorySystem — 记忆/历史系统
- `resonance_system`: ResonanceEngine — 共鸣/情感驱动
- `vision_system`: VisionSystem — 视觉感知系统
- `hearing_system`: HearingSystem — 听觉解析系统
- `voice_out_system`: TTSSystem — 语音输出系统

**持有的 Agent**:
- `scene_analyzer`: SceneAnalyzerAgent — 环境与展品视觉分析
- `dialogue_orchestrator`: DialogueAgent — 对话策略与人设维护
- `action_planner`: ActionAgent — 机器人动作与播放规划

**全局状态**:
- `interaction_state`: InteractionPhase — 当前交互阶段 (监听/思考/播报)
- `session_context`: SessionContext — 当前会话的全局上下文 (包含用户特征)
- `active_memory`: List[ChatTurn] — 活跃的对话短期记忆

**核心接口**:
- `start_orchestration()` — 启动全链路交互流程
- `process_input(voice_text, image_data)` — 处理多模态输入并生成决策
- `sync_resonance_state()` — 同步情感共鸣引擎状态
- `get_robot_state()` — 获取机器人当前的全局物理与逻辑状态
- `reset_session()` — 清除会话并重置到初始监听状态

---

## 2. 认知引擎模块 (Cognitive Engines)

### 2.1 检索系统 (Retrieval System)
**文件**: `rag/retriever.py`  
**职责**: 基于结构化知识库执行多阶段RAG检索流程，从知识库中召回与当前问题最相关的展品信息，并通过混合检索与重排序机制提升检索结果的准确性与相关性。

**核心接口**:
- `retrieve(query, top_k)` — 执行完整检索流程（向量检索 + 可选BM25 + 重排序），返回相关知识片段  
- `rerank(query, candidates)` — 对候选结果进行语义重排序  
- `get_stats()` — 获取知识库统计信息

### 2.2 记忆系统 (Memory System)
**文件**: `services/memory_service.py`  
**职责**: 管理短期对话流与长期用户知识沉淀。

**全局状态**:
- `short_term_buffer`: List[Message] — 滑动窗口式的短时对话缓冲

**核心接口**:
- `fetch_history(user_id)` — 获取指定用户的对话历史
- `commit_turn(user_id, turn_data)` — 将一轮对话存入持久化记忆

### 2.3 共鸣引擎 (Resonance Engine)
**文件**: `services/resonance_engine.py`  
**职责**: 实现“技心”人设的人格化算法，调节回应的情感质感与美学比重。

**核心接口**:
- `calculate_vibe(text_input)` — 评估交互内容的情感共鸣分值
- `apply_persona_filter(raw_response)` — 将生成的原始文本通过人设协议进行滤镜化处理

---

## 3. 感知与执行模块 (Perception & Execution)

### 3.1 视觉系统 (Vision System)
**文件**: `services/vision_service.py`  
**职责**: 负责实时摄像头流的捕捉、快照分析及展品特征提取。

**核心接口**:
- `capture_snapshot()` — 触发一次高清画面捕捉
- `get_latest_frame()` — 获取缓存中的最新一帧数据

### 3.2 听觉系统 (Hearing System)
**文件**: `services/asr_service.py`  
**职责**: 负责音频降噪、语义断句及文字转化 (ASR)。

**核心接口**:
- `start_listening()` — 开启麦克风监听流
- `stop_listening()` — 停止监听并返回最终文本

### 3.3 语言系统 (Language System)
**文件**: `services/llm_service.py`  
**职责**: 负责大模型的底层调用、流式输出管理及提示词注入。

**核心接口**:
- `generate_stream(prompts, history)` — 发起流式模型预测
- `generate_sync(prompts)` — 发起同步模型预测
