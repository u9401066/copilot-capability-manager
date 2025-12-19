# Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-15 | 採用憲法-子法層級架構 | 類似 speckit 的規則層級，可擴展且清晰 |
| 2025-12-15 | DDD + DAL 獨立架構 | 業務邏輯與資料存取分離，提高可測試性 |
| 2025-12-15 | Skills 模組化拆分 | 單一職責，可組合使用，易於維護 |
| 2025-12-15 | Memory Bank 與操作綁定 | 確保專案記憶即時更新，不遺漏 |
| 2025-12-20 | 重構為 Copilot Capability Manager | 專注於 /cp.xxx 斜線指令系統 |
| 2025-12-20 | 不使用 agent: 欄位 | 保持 Agent Mode 完整工具權限 |
| 2025-12-20 | Prompt Files 直接包含完整步驟 | 簡化架構，不需動態更新 AGENTS.md |

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
