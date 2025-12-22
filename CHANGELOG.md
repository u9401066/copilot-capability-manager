# Changelog

所有重要變更都會記錄在此檔案中。

格式基於 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)，
專案遵循 [語義化版本](https://semver.org/lang/zh-TW/)。

## [0.5.0] - 2025-12-23

### Added
- **🧠 Neuro-Symbolic AI 架構**
  - 實現三層架構：Symbolic Layer → Skill Bridge → Tool Layer
  - 符號層處理結構化能力定義與邏輯
  - 神經網路層處理 LLM 決策
  - 工具層執行結構化 API

- **📦 DDD (Domain-Driven Design) Python 核心引擎**
  - `domain/value_objects/` - 不可變值物件
    - `node_type.py` - NodeType, EdgeType, ExecutionStatus
    - `complexity.py` - ComplexityMetrics, ComplexityLevel
    - `contract.py` - NodeContract, Implementation, BranchCondition
  - `domain/entities/` - 實體（聚合根）
    - `node.py` - GraphNode
    - `edge.py` - GraphEdge
    - `graph.py` - CapabilityGraph (Aggregate Root)
  - `application/use_cases/` - 用例
    - `execute_capability.py` - ExecuteCapabilityUseCase
  - `application/services/` - 應用服務
    - `resolver.py` - NodeResolverService, GraphValidatorService
  - `infrastructure/mcp/` - MCP Server 整合
    - `server.py` - CapabilityMCPServer (6 tools)
  - `infrastructure/prompt/` - Prompt 生成
    - `generator.py` - PromptGenerator, PromptInjector

- **🔌 VS Code Copilot 整合**
  - MCP Server 提供 6 個 tools：
    - `execute_capability` - 執行能力圖
    - `resolve_abstract_node` - 解析抽象節點
    - `validate_graph` - 驗證圖結構
    - `get_complexity_metrics` - 計算複雜度
    - `list_capabilities` - 列出所有能力
    - `get_capability_status` - 取得執行狀態
  - Prompt Injection 動態生成 `.prompt.md`
  - Prompt Injector 注入能力上下文

- **🧪 完整測試套件**
  - `test_ddd.py` - DDD 架構測試
  - Domain 層測試 ✅
  - Application 層測試 ✅
  - Infrastructure 層測試 ✅
  - 端到端整合測試 ✅

### Changed
- 更新 `ARCHITECTURE.md` - 加入 Neuro-Symbolic AI 架構說明
- 更新 `README.md` - 加入三層架構圖與整合方式
- 舊版 Python 模組標記為 Legacy，保持向後相容

---

## [0.4.0] - 2025-12-22

### Added
- **能力自動觸發系統**
  - 新增 `.claude/capabilities/registry.yaml` 能力註冊表
  - 新增 `.claude/capabilities/write-report/CAPABILITY.md` 範例能力
  - AGENTS.md 加入自動觸發規則表

- **圖論基礎的能力組合設計**
  - 新增 `docs/GRAPH-BASED-CAPABILITY-DESIGN.md` 設計文件
  - 新增 `extension/src/services/GraphExecutionEngine.ts` 執行引擎
  - 支援 McCabe 環路複雜度計算
  - 支援節點類型：skill, control.*, interaction.*
  - 支援邊類型：sequence, conditional, iteration, parallel

- **自適應圖與不確定性處理**
  - 新增 `docs/ADAPTIVE-GRAPH-DESIGN.md` 設計文件
  - 抽象節點（Abstract Node）+ 多態實現
  - Fallback 鏈機制
  - 延遲展開（Lazy Expansion）
  - 不確定性量化指標

- **文檔更新**
  - 新增 `docs/CAPABILITY-ARCHITECTURE.md` 架構文件
  - README.md 新增「設計理念」區塊

---

## [0.3.0] - 2025-12-22

### Added
- **非線性流程支援**
  - 新增 `StepType`: skill, branch, loop, parallel, merge
  - 新增 `LoopConfig`: 固定次數、條件迴圈、遍歷
  - 新增 `CapabilityEdge`: 節點連接圖結構
  - CapabilityBuilderProvider 更新：步驟類型選擇 UI

- **MCP Tools 整合**
  - 新增 `McpService`: MCP 工具發現與推薦
  - 支援 PubMed, Zotero, Pylance 等工具
  - SkillManagerProvider 新增「顯示推薦的 MCP Tools」

- **驗證服務**
  - 新增 `ValidationService`: Capability 合併驗證
  - 檢查循環依賴、I/O 相容性、資源衝突
  - 迴圈設定驗證（防止無限迴圈）

- **Capability TreeView**
  - 新增 `CapabilityTreeProvider`: 側邊欄 Capability 列表
  - 顯示步驟數量、點擊編輯、展開檢視步驟

- **Skill 複製功能**
  - 新增 `ccm.skill.duplicate` 命令
  - 右鍵選單快速複製現有 Skill

### Changed
- 更新 `types/skill.ts`: 新增 `inputType`, `outputType`, `resources`
- 更新 `types/capability.ts`: 新增 `edges`, 重新設計 `CapabilityStep`
- 更新 `extension.ts`: 註冊 CapabilityTreeProvider 和檔案監視
- 更新 `commands/index.ts`: 新增 duplicate 和 refresh 命令

---

## [0.2.0] - 2025-12-20

### Added
- **VS Code Extension 實作**
  - `extension/package.json` - 擴充套件配置
  - `extension/tsconfig.json` - TypeScript 配置
  - `extension/src/extension.ts` - 主入口
  - `extension/src/services/` - 核心服務層
    - `SkillService.ts` - Skill CRUD 操作
    - `CapabilityService.ts` - Workflow 管理
  - `extension/src/providers/` - UI Providers
    - `SkillTreeProvider.ts` - 側邊欄 Skill 列表
    - `SkillManagerProvider.ts` - Skill 編輯器 Webview
    - `CapabilityBuilderProvider.ts` - Workflow 建立器
  - `extension/src/types/` - TypeScript 型別定義
    - `skill.ts` - Skill 相關型別
    - `capability.ts` - Capability 相關型別
  - `extension/src/commands/index.ts` - 命令註冊

### Features
- 視覺化 Skill 管理：TreeView 按分類顯示
- Skill 編輯器：Webview 表單編輯 SKILL.md
- Workflow 建立器：拖放組合 Skills 產生 Prompt File
- 自動監視：檔案變更時自動重新整理

## [0.1.0] - 2025-12-15

### Added
- 初始化專案結構
- 新增 Claude Skills 支援
  - `git-doc-updater` - Git 提交前自動更新文檔技能
- 新增 Memory Bank 系統
  - `activeContext.md` - 當前工作焦點
  - `productContext.md` - 專案上下文
  - `progress.md` - 進度追蹤
  - `decisionLog.md` - 決策記錄
  - `projectBrief.md` - 專案簡介
  - `systemPatterns.md` - 系統模式
  - `architect.md` - 架構文檔
- 新增 VS Code 設定
  - 啟用 Claude Skills
  - 啟用 Agent 模式
  - 啟用自定義指令檔案
