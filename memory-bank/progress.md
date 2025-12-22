# Progress (Updated: 2025-12-23)

## Done

### v0.5.0 - Neuro-Symbolic AI 架構
- 🧠 **Neuro-Symbolic AI 三層架構**
  - Symbolic Layer: Capability Graph, Contracts, Branch Logic
  - Skill Bridge: LLM Agent + Abstract Node Resolver
  - Tool Layer: MCP Tools, File System, APIs
- 📦 **DDD Python 核心引擎**
  - Domain 層: value_objects (NodeType, Complexity, Contract), entities (Node, Edge, Graph)
  - Application 層: use_cases (ExecuteCapability), services (Resolver, Validator)
  - Infrastructure 層: MCP Server (6 tools), Prompt Generator/Injector
- 🔌 **VS Code Copilot 整合**
  - MCP Server: execute_capability, resolve_abstract_node, validate_graph, get_complexity_metrics, list_capabilities, get_capability_status
  - Prompt Injection: 動態生成 .prompt.md
  - mcp.json 設定檔
- 🧪 **完整測試套件**
  - test_ddd.py 全部通過 ✅
- 📝 **文件更新**
  - ARCHITECTURE.md - Neuro-Symbolic 架構說明
  - README.md - 三層架構 + 整合方式
  - CHANGELOG.md - v0.5.0

### v0.4.0 - 能力架構
- 能力自動觸發系統
- 圖論基礎的能力組合設計
- 自適應圖與不確定性處理

### v0.3.0 - Extension 功能
- 非線性流程支援
- MCP Tools 整合
- 驗證服務
- Capability TreeView

### v0.2.0 - Extension 實作
- VS Code Extension 基礎架構
- Skill Manager GUI
- Capability Builder GUI

## Doing

- 準備 Git commit 和 push

## Next

- 實作 Chat Participant API (@capability)
- Webview UI 改進
- Skill 市集功能
