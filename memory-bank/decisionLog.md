# Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-23 | **Neuro-Symbolic AI 架構** | 結合符號推理的可解釋性與神經網路的靈活性 |
| 2025-12-23 | **Python DDD + TypeScript UI** | Python 處理圖結構，TypeScript 處理 UI |
| 2025-12-23 | **MCP Server 作為主要整合方式** | Copilot 原生支援，完整雙向通信 |
| 2025-12-22 | 圖論基礎的能力組合 | DAG 自然表達迴圈、分支、並行 |
| 2025-12-22 | 抽象節點 + Fallback 鏈 | 處理輸入不確定性，優雅降級 |
| 2025-12-21 | **Skill vs Capability 概念區分** | Skill=原子多工具操作, Capability=動態狀態機 |
| 2025-12-21 | **長任務狀態追蹤機制** | 使用 Checkpoint 檔案實現跨對話狀態持久化 |
| 2025-12-20 | 重構為 Copilot Capability Manager | 專注於 /cp.xxx 斜線指令系統 |
| 2025-12-20 | 不使用 agent: 欄位 | 保持 Agent Mode 完整工具權限 |
| 2025-12-15 | 採用憲法-子法層級架構 | 類似 speckit 的規則層級，可擴展且清晰 |
| 2025-12-15 | DDD + DAL 獨立架構 | 業務邏輯與資料存取分離，提高可測試性 |

---

## [2025-12-23] Neuro-Symbolic AI 架構決策

### 背景
Gemini 指出我們正在朝向嚴謹的 Neuro-Symbolic AI 發展方向。

### 分析
我們的架構確實符合 Neuro-Symbolic 模式：

```
┌─────────────────────────────────────────────────────────────┐
│  🔷 SYMBOLIC LAYER (符號層)                                 │
│  - Capability Graph: 結構化的能力定義                        │
│  - Node Contracts: 可驗證的輸入/輸出契約                     │
│  - Branch Logic: 確定性的條件邏輯                            │
├─────────────────────────────────────────────────────────────┤
│  🔶 SKILL BRIDGE (技能橋接層)                                │
│  - LLM Agent: 神經網路的靈活決策                             │
│  - Abstract Node Resolver: 動態綁定具體實現                  │
│  - Skill Executor: 執行技能（連接 Neural 和 Symbolic）       │
├─────────────────────────────────────────────────────────────┤
│  🔻 TOOL LAYER (工具層)                                     │
│  - MCP Tools: 結構化 API 調用                                │
│  - File System: 檔案操作                                     │
│  - External APIs: 第三方服務                                 │
└─────────────────────────────────────────────────────────────┘
```

### 決定
正式採納 Neuro-Symbolic AI 作為專案核心架構理念：

1. **符號層**負責結構和約束
2. **神經層**（LLM）負責決策和靈活性
3. **工具層**負責實際執行

### 理由

| 特性 | 純 Neural | 純 Symbolic | Neuro-Symbolic |
|------|----------|-------------|----------------|
| 靈活性 | ✅ 高 | ❌ 低 | ✅ 高 |
| 可解釋性 | ❌ 黑箱 | ✅ 透明 | ✅ 透明 |
| 可靠性 | ⚠️ 不穩定 | ✅ 穩定 | ✅ 穩定 |
| 適應性 | ✅ 強 | ❌ 弱 | ✅ 強 |

### 影響
- 更新 ARCHITECTURE.md 加入 Neuro-Symbolic 說明
- 更新 README.md 強調三層架構
- DDD 架構與三層概念對應：
  - Domain = Symbolic
  - Application = Bridge
  - Infrastructure = Tools

---

## [2025-12-23] Python DDD + TypeScript UI 架構決策

### 背景
用戶問：「得要用 typescript? 不能構 python 基底 + 最後 typescript 呈現?」

### 決定
採用混合架構：

```
Python Core (capability_engine/)
├── domain/           # 符號層核心
├── application/      # 業務邏輯
└── infrastructure/   # MCP Server, Prompt Generator

TypeScript Presentation (extension/)
├── providers/        # VS Code UI
├── services/         # Bridge to Python
└── webview/          # GUI
```

### 理由
1. **Python 優勢**：
   - networkx, graphviz 圖處理
   - asyncio 非同步執行
   - dataclasses 簡潔的資料模型

2. **TypeScript 優勢**：
   - VS Code Extension API
   - Webview UI
   - 與 Copilot 原生整合

3. **整合方式**：
   - MCP Server (stdio/JSON-RPC)
   - child_process.spawn

---

## [2025-12-21] Skill vs Capability 核心概念區分

### 背景
原本將 Capability 設計為線性的 Skill 串聯（類似 Workflow），但實際使用場景更複雜。

### 問題場景：文獻評讀
- 輸入：一個資料夾（包含多個 PDF）
- 需要：
  - `search` skill × N（找多篇文獻）
  - 對每個 PDF：
    - `read-pdf` skill × M（長 PDF 可能要讀多次）
    - `write-note` skill × M（每次讀完寫筆記）
  - 最後 `synthesis` skill（綜合整理）

### 決定
重新定義概念層級：

```
┌─────────────────────────────────────────────────────┐
│  Tool (工具)                                        │
│  - 最小單位，單一 API 調用                           │
│  - 例：fetch_webpage, read_file, run_in_terminal   │
├─────────────────────────────────────────────────────┤
│  Skill (技能)                                       │
│  - 多個 Tools 的編排                                │
│  - 完成一個明確的小任務                              │
│  - 例：search-literature (搜尋+篩選+摘要)           │
├─────────────────────────────────────────────────────┤
│  Capability (能力)                                  │
│  - 動態的 Skill 狀態機                              │
│  - 可迴圈、條件分支、根據狀況決定下一步              │
│  - 需要狀態追蹤（長任務可能跨對話）                   │
│  - 例：literature-review (多輪搜尋+多篇閱讀+綜合)   │
└─────────────────────────────────────────────────────┘
```

### 理由
- Workflow 暗示線性執行，不適合描述動態流程
- Capability 強調「能力」，包含判斷和迴圈
- 符合實際使用場景（批次處理、長任務）

---

## [2025-12-21] 長任務狀態追蹤機制

### 背景
Copilot 有 context window 限制，長任務（如處理 20 篇 PDF）無法在單次對話完成。

### 挑戰
1. Context 會被截斷，Agent 忘記之前做了什麼
2. 需要知道「處理到哪裡了」
3. 中途中斷後要能繼續

### 決定
引入 **Checkpoint 機制**：

```
memory-bank/
├── checkpoints/
│   └── {capability-id}-{timestamp}.json
│       {
│         "capability": "literature-review",
│         "status": "in-progress",
│         "currentPhase": "reading",
│         "progress": {
│           "total": 20,
│           "completed": 8,
│           "current": "paper-09.pdf"
│         },
│         "completedItems": ["paper-01.pdf", ...],
│         "notes": [...],
│         "lastUpdated": "2025-12-21T10:30:00Z"
│       }
```

### 執行流程
1. **啟動**：建立 checkpoint 檔案
2. **執行中**：每完成一個 item 更新 checkpoint
3. **中斷**：checkpoint 保留狀態
4. **繼續**：讀取 checkpoint，從斷點繼續
5. **完成**：標記 checkpoint 為 completed

### Copilot 支援度
- ✅ 可透過 Memory Bank 實現（檔案系統）
- ✅ Agent 可讀寫 checkpoint 檔案
- ⚠️ 需要明確指示「繼續上次任務」
- ⚠️ 跨對話需用戶主動觸發

### 影響
- 新增 `memory-bank/checkpoints/` 目錄
- Capability 模板需包含 checkpoint 邏輯
- 需要 `checkpoint-manager` skill

---

## [2025-12-20] 重構為 Copilot Capability Manager

### 背景
原本是 AI 輔助開發的專案模板，需要更明確的定位和功能。

### 選項
1. 保持模板定位 - 用戶克隆後使用
2. 重構為獨立工具 - 專注 /cp.xxx 指令系統
3. 同時兼顧兩者

### 決定
採用選項 2：重構為獨立工具

### 理由
- 更明確的定位：Copilot 能力管理器
- 專注於 Prompt Files 機制
- 提供可擴展的 Skill 和 Workflow 系統

---

## [2025-12-20] 不使用 agent: 欄位

### 背景
研究 SpecKit 時發現它使用 `agent:` 欄位切換到自定義 agent。

### 選項
1. 使用 `agent:` - 像 SpecKit 一樣
2. 不使用 `agent:` - 保持在標準 Agent Mode

### 決定
採用選項 2：不使用 `agent:` 欄位

### 理由
- 使用 `agent:` 會切換到自定義 agent，失去：
  - MCP 工具（如 PubMed 搜尋）
  - 終端機命令執行
  - 完整的工具訪問權限
- 保持 Agent Mode 可以使用所有工具

### 影響
- Prompt Files 直接包含完整步驟
- 不需要 `.github/agents/` 目錄
- AGENTS.md 簡化為靜態專案上下文

---

## [2025-12-15] 採用憲法-子法層級架構

### 背景
需要一個清晰的規則層級系統，類似 speckit 但可擴展。

### 選項
1. 單一 copilot-instructions.md - 簡單但不夠靈活
2. 憲法 + 子法層級 - 清晰層級，可擴展
3. 全部放在 Skills 內 - 分散，難以管理

### 決定
採用選項 2：憲法-子法層級

### 理由
- 最高原則集中在 CONSTITUTION.md
- 細則可在 bylaws/ 擴展
- Skills 專注於操作程序
- 符合現實法律體系，易理解

### 影響
- 新增 CONSTITUTION.md
- 新增 .github/bylaws/ 目錄
- Skills 需引用相關法規
| 2025-12-22 | Prompt Compiler 定位：我們不是在執行能力，而是在編譯能力成 Prompt | Agent 外層約束：唯一通道是 AGENTS.md / .prompt.md (純文字)。具象化是為了「管理」和「編譯」，不是為了「執行」。我們需要的是 Prompt Compiler，不是 Workflow Engine。 |
