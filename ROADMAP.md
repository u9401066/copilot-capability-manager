# Roadmap

> 🔬 **研究導向路線圖** - 這是一個探索性專案，版本迭代以概念驗證為主

---

## 🎯 核心問題：何謂「能力」(Capability)？

### 開放問題 (Open Questions)

```
Q1: 能力 ≠ 工作流？差異是什麼？
Q2: 能力可以被「測量」嗎？如何衡量？
Q3: 能力可以被「組合」嗎？組合邏輯是什麼？
Q4: 能力可以被「抽象」嗎？抽象層次有幾層？
Q5: 能力可以被「驗證」嗎？正確性如何定義？
```

### 工作假設 (Working Hypothesis)

```
Capability = Graph + Contracts + Semantics + Execution Policy

其中：
• Graph       = 結構（節點、邊、拓撲）
• Contracts   = 約束（前置、後置、不變式）
• Semantics   = 語義（意圖、領域、上下文）
• Policy      = 策略（重試、超時、回退）
```

---

## 🏗️ 架構探索：我們在建什麼？

```
┌─────────────────────────────────────────────────────────────────────┐
│                    傳統 Agent 框架位置                               │
│                                                                      │
│    User ──► [LangGraph/AutoGen] ──► LLM ──► Tools                   │
│                     ↑                                                │
│              狀態機在這裡                                             │
│              (Agent 內部)                                            │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    我們的架構位置                                     │
│                                                                      │
│    User ──► [Capability Layer] ──► Agent (Copilot) ──► Tools        │
│                     ↑                                                │
│              結構在這裡                                               │
│              (Agent 外部)                                            │
│              Agent 是黑盒執行者                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### 關鍵洞察

> 我們不是在做 Agent 編排，而是在做 **「給 Agent 的指令結構化」**

---

## � 核心約束：Agent 外層作業

```text
┌─────────────────────────────────────────────────────────────────────┐
│                        實際系統約束                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌───────────────────┐                    ┌───────────────────┐    │
│   │  Our Software     │    唯一通道        │    Copilot        │    │
│   │  (具象化能力)      │ ═══════════════► │    (黑盒 Agent)    │    │
│   │                   │   AGENTS.md        │                   │    │
│   │  • Graph          │   .prompt.md       │   讀取文字        │    │
│   │  • Contract       │   (純文字!)        │   做出行動        │    │
│   │  • Policy         │                    │                   │    │
│   └───────────────────┘                    └───────────────────┘    │
│                                                                      │
│   具象化 ────────────────────────────────► 抽象化                   │
│   (結構、圖、契約)                          (Markdown 文字)          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 核心矛盾與解決

```text
我們想要：結構化、可驗證、可視化的「能力」表示
Agent 能讀：純文字 Markdown

解決方案：結構 ──編譯──► 文字 ──通道──► Agent
```

### 💡 重新定義：Capability = Prompt 的元表示

```text
┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│   我們不是在「執行」能力，而是在「編譯」能力成 Prompt                 │
│                                                                      │
│   ┌─────────────┐      ┌─────────────┐      ┌─────────────┐        │
│   │ Capability  │ ───► │   Prompt    │ ───► │  Markdown   │        │
│   │   Graph     │      │  Compiler   │      │   Output    │        │
│   │ (元表示)    │      │  (編譯器)   │      │ (給 Agent)  │        │
│   └─────────────┘      └─────────────┘      └─────────────┘        │
│                                                                      │
│   類比：                                                             │
│   TypeScript ──► tsc ──► JavaScript                                 │
│   Capability ──► compiler ──► Prompt Markdown                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 「軟體具象化」的真正目的

| 目的 | 說明 | 最終輸出 |
|------|------|----------|
| **設計時驗證** | 檢查流程邏輯、契約一致性 | 無（內部用） |
| **視覺化編輯** | GUI 拖拉、連線 | 無（內部用） |
| **版本管理** | 追蹤能力演進 | 無（內部用） |
| **Prompt 編譯** | 把結構轉成文字 | ✅ `.prompt.md` |

> **結論：具象化是為了「管理」和「編譯」，不是為了「執行」！**

---

## �📊 現有系統可融入分析

| 系統 | 特性 | 可借鑒 | 融入可能性 |
|------|------|--------|-----------|
| **Petri Net** | 並發、同步、資源 | Token-based 執行語義 | ⭐⭐⭐ 高 |
| **Statecharts** | 層次狀態、歷史 | 嵌套狀態機 | ⭐⭐ 中 |
| **BPMN** | 業務流程標準 | Gateway, Event | ⭐⭐ 中 |
| **Activity Diagram** | UML 標準 | Fork/Join/Decision | ⭐⭐ 中 |
| **Dataflow** | 數據驅動 | 管線式處理 | ⭐⭐⭐ 高 |
| **Knowledge Graph** | 語義網路 | 實體關係 | ⭐⭐⭐ 高 |
| **Process Algebra** | 形式化驗證 | CSP/CCS 語義 | ⭐ 低 (學術) |

### 融入策略

```yaml
Phase 1: Capability Graph (基礎 DAG)
  └─ 借鑒: Activity Diagram (控制流)

Phase 2: + 數據流
  └─ 借鑒: Dataflow (數據管線)

Phase 3: + 並發模型
  └─ 借鑒: Petri Net (Token 語義)

Phase 4: + 語義層
  └─ 借鑒: Knowledge Graph (意圖路由)
```

---

## 🔣 符號統一問題

### 目前符號系統 (v0.5.x)

```python
# 節點類型
class NodeType(Enum):
    SKILL = "skill"              # 技能節點
    TOOL = "tool"                # 工具調用
    DECISION = "control.decision" # 分支
    LOOP = "control.loop"        # 循環
    ABSTRACT = "abstract"        # 抽象節點

# 邊類型
class EdgeType(Enum):
    SEQUENCE = "sequence"        # 順序
    CONDITIONAL = "conditional"  # 條件
    OPTIONAL = "optional"        # 可選
```

### 符號統一方向

```
┌─────────────────────────────────────────────────────────────────────┐
│                         符號統一框架 (提案)                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. 節點符號 (Node Symbols)                                          │
│     ○ = 普通節點 (Skill/Tool)                                        │
│     ◇ = 決策節點 (Decision)                                          │
│     □ = 抽象節點 (Abstract) - 執行時綁定                              │
│     ◎ = 複合節點 (Composite) - 嵌套子圖                              │
│     ● = 終端節點 (Terminal)                                          │
│                                                                      │
│  2. 邊符號 (Edge Symbols)                                            │
│     ─→ = 控制流 (Control Flow)                                       │
│     ═> = 數據流 (Data Flow)                                          │
│     ╌→ = 條件邊 (Conditional)                                        │
│     ⋯> = 可選邊 (Optional)                                           │
│                                                                      │
│  3. 契約符號 (Contract Symbols)                                       │
│     ⊢ = 前置條件 (Precondition)                                      │
│     ⊣ = 後置條件 (Postcondition)                                     │
│     ⊨ = 不變式 (Invariant)                                           │
│                                                                      │
│  4. 執行符號 (Execution Symbols)                                      │
│     ⊕ = 並行分支 (Fork)                                              │
│     ⊗ = 並行合併 (Join)                                              │
│     ↻ = 循環 (Loop)                                                  │
│     ⟲ = 重試 (Retry)                                                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔷 抽象層設計

### 目前三層架構

```
Layer 3: Capability (能力)
Layer 2: Skill (技能)
Layer 1: Tool (工具)
```

### 擴展提案：五層架構

```
┌─────────────────────────────────────────────────────────────────────┐
│                         五層抽象架構 (提案)                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Layer 5: INTENT (意圖層) 🆕                                         │
│  ├─ "寫一篇報告" / "部署應用" / "代碼審查"                           │
│  ├─ 最高層抽象，接近自然語言                                         │
│  └─ 一個意圖可對應多個能力                                           │
│                                                                      │
│  Layer 4: CAPABILITY (能力層)                                        │
│  ├─ 結構化的執行圖                                                   │
│  ├─ 包含契約、策略、語義                                             │
│  └─ 一個能力 = 多個技能的編排                                        │
│                                                                      │
│  Layer 3: SKILL (技能層)                                             │
│  ├─ 可重用的操作單元                                                 │
│  ├─ 有清晰的輸入/輸出契約                                            │
│  └─ 一個技能可使用多個工具                                           │
│                                                                      │
│  Layer 2: TOOL (工具層)                                              │
│  ├─ MCP Tools / VS Code APIs                                         │
│  ├─ 確定性的 API 調用                                                │
│  └─ 最低層抽象                                                       │
│                                                                      │
│  Layer 1: RUNTIME (執行時層) 🆕                                      │
│  ├─ 實際的執行環境                                                   │
│  ├─ 文件系統、網路、記憶體                                           │
│  └─ 資源管理、狀態追蹤                                               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 層間關係

```
Intent ──1:N──► Capability ──1:N──► Skill ──1:N──► Tool
                                                      │
                                                      ▼
                                                   Runtime
```

---

## 📅 研究路線圖 (Research Roadmap)

### v0.5.x - 基礎驗證 (現在)

```yaml
狀態: 🚧 進行中
目標: 驗證 Neuro-Symbolic 架構可行性

完成:
  - [x] DDD 三層架構 (Domain/Application/Infrastructure)
  - [x] Capability Graph 基礎實現
  - [x] 抽象節點 (Abstract Node) 概念
  - [x] MCP Server 原型

進行中:
  - [ ] 契約系統原型 (Contract System)
  - [ ] 符號統一初版

開放問題:
  - 契約語言用什麼？(YAML? DSL? 形式化?)
  - 抽象節點解析策略？(規則? 學習?)
```

### v0.6.x - 符號系統 (Q1 2025)

```yaml
狀態: 📋 計劃
目標: 建立統一的符號表示系統

研究問題:
  - R1: 節點類型的完整分類
  - R2: 邊語義的形式化定義
  - R3: 契約語言設計
  - R4: 執行語義定義

實驗:
  - [ ] 符號 DSL 設計與實現
  - [ ] 圖序列化格式 (JSON? YAML? 自定義?)
  - [ ] 符號可視化原型

產出:
  - 符號系統設計文檔
  - DSL 參考實現
  - 測試案例集
```

### v0.7.x - 數據流擴展 (Q1 2025)

```yaml
狀態: 📋 計劃
目標: 從純控制流擴展到數據流

研究問題:
  - R5: 控制流 vs 數據流的統一表示
  - R6: 數據依賴如何表達？
  - R7: 類型系統需要嗎？

實驗:
  - [ ] 數據流邊類型
  - [ ] 數據轉換節點
  - [ ] 管線式執行模型

借鑒:
  - Apache Beam (Dataflow)
  - TensorFlow Graph
  - Unix Pipes
```

### v0.8.x - 並發模型 (Q2 2025)

```yaml
狀態: 📋 計劃
目標: 引入並發執行能力

研究問題:
  - R8: 並發語義如何定義？
  - R9: 同步點如何表達？
  - R10: 資源競爭如何處理？

實驗:
  - [ ] Fork/Join 節點
  - [ ] 同步屏障 (Barrier)
  - [ ] 並發執行器原型

借鑒:
  - Petri Net (Token 語義)
  - Go Channels
  - Actor Model
```

### v0.9.x - 語義層 (Q2 2025)

```yaml
狀態: 📋 計劃
目標: 加入語義理解能力

研究問題:
  - R11: 意圖如何表示？
  - R12: 領域知識如何編碼？
  - R13: 語義路由如何實現？

實驗:
  - [ ] 意圖分類器
  - [ ] 領域本體 (Ontology)
  - [ ] 語義匹配引擎

借鑒:
  - Knowledge Graph
  - OWL/RDF
  - Intent Classification (NLU)
```

### v1.0.x - 整合與驗證 (Q3 2025)

```yaml
狀態: 📋 遠期
目標: 整合所有組件，完整驗證

驗證目標:
  - V1: 能力定義的完整性
  - V2: 符號系統的一致性
  - V3: 執行模型的正確性
  - V4: 實用性評估

產出:
  - 完整的理論框架
  - 參考實現
  - 評估報告
  - 論文草稿 (?)
```

---

## 🧪 實驗追蹤

| ID | 實驗名稱 | 狀態 | 結論 |
|----|----------|------|------|
| E01 | Prompt Files 機制 | ✅ | 可行，但有限制 |
| E02 | DDD + Python Engine | ✅ | 結構清晰 |
| E03 | MCP Server 整合 | ✅ | 可用 |
| E04 | 抽象節點原型 | 🚧 | 待驗證 |
| E05 | 契約語言設計 | 📋 | - |
| E06 | 數據流擴展 | 📋 | - |
| E07 | 並發模型 | 📋 | - |
| E08 | 語義路由 | 📋 | - |

---

## 📖 參考資源

### 理論基礎

- [Petri Nets](https://en.wikipedia.org/wiki/Petri_net) - 並發系統建模
- [Statecharts](https://statecharts.dev/) - 層次狀態機
- [Design by Contract](https://en.wikipedia.org/wiki/Design_by_contract) - 契約式設計
- [Neuro-Symbolic AI](https://arxiv.org/abs/2012.05876) - 神經符號 AI

### 相關專案

- [IBM LNN](https://github.com/IBM/LNN) - Logical Neural Networks
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent 狀態圖
- [Temporal](https://temporal.io/) - 工作流引擎
- [Prefect](https://www.prefect.io/) - 數據管線

### 標準規範

- [BPMN 2.0](https://www.omg.org/spec/BPMN/2.0/) - 業務流程建模
- [UML Activity Diagram](https://www.uml-diagrams.org/activity-diagrams.html)
- [MCP Protocol](https://modelcontextprotocol.io/) - 模型上下文協議

---

## ⚠️ 風險與挑戰

| 風險 | 影響 | 緩解策略 |
|------|------|----------|
| 過度抽象 | 實用性下降 | 每階段保持可執行原型 |
| 符號爆炸 | 複雜度失控 | 最小可行符號集 |
| 學術化傾向 | 脫離實際需求 | 持續與實際場景對接 |
| 範圍蔓延 | 無法完成 | 嚴格的階段目標 |

---

## 📝 決策記錄

| 日期 | 決策 | 原因 |
|------|------|------|
| 2024-12-20 | 採用 Prompt Files 機制 | VS Code 原生支援 |
| 2024-12-22 | Python DDD 架構 | 類型安全 + 測試友好 |
| 2024-12-23 | Neuro-Symbolic 定位 | 區別於 LangGraph 等 |
| 2024-12-23 | 研究導向路線圖 | 探索性專案 |
| 2024-12-23 | **Prompt Compiler 定位** | Agent 外層約束，唯一通道是純文字 |
| 2024-12-23 | 具象化為編譯非執行 | 我們不執行能力，而是編譯成 Prompt |
