# Progress (Updated: 2025-12-24)

## Done

- v0.5.0 Neuro-Symbolic AI 架構 commit
- Agent 外層約束文件化
- Prompt Compiler 定位確立
- Prompt Compiler 實作方案整理到 ROADMAP
- v0.5.3 「音樂學習助手」設計案例加入 ROADMAP
- v0.5.4 **架構升級：Runtime MCP 動態組裝**
  - 從「靜態編譯」升級為「Runtime MCP 動態組裝」
  - 新增 `capability-router` MCP Server 設計
  - 三重保險機制確保 Agent 讀取 prompt
- v0.5.5 **新增 Research Agent**
  - 建立 `.github/agents/research.agent.md`
  - 整合 PubMed、Zotero、MarkItDown 工具
  - 委派工作流至 Skills 系統（literature-search, literature-retrieval 等）

## Doing

- Git commit + push v0.5.5

## Next

- 實作 `capability-router` MCP Server
  - tools: activate(), list_capabilities(), get_capability_status()
- MVP Phase 1: Capability YAML Schema 設計
- MVP Phase 2: YAML → Graph 解析器
