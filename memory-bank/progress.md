# Progress (Updated: 2025-12-21)

## Done

- 撰寫 Sevoflurane 麻醉意識調控機制讀書報告
- 分析 Skill 觸發機制問題並建立改進報告
- 更新 copilot-instructions.md 添加 Skill 自動觸發指引表
- ✅ **完成全部 22 個 Skills 的 description 強化**
- ✅ **實作 VS Code Extension 完整框架**
  - extension/ 目錄：package.json, tsconfig.json
  - services/：SkillService, CapabilityService
  - providers/：SkillTreeProvider, SkillManagerProvider, CapabilityBuilderProvider
  - types/：skill.ts, capability.ts
  - commands/：index.ts 註冊所有命令
- ✅ **統一術語：Workflow → Capability**
  - 建立 Tool → Skill → Capability 概念層級
  - 建立 Checkpoint 機制支援長任務狀態追蹤
  - 分析 Enforcement 機制限制
- ✅ **專案文件一致性整理**
  - 更新 CLAUDE.md：反映正確專案描述
  - 更新 docs/CAPABILITY-GUIDE.md：Tool→Skill→Capability 概念
  - 更新 docs/PROMPT-FILES-MECHANISM.md：統一術語
  - 更新 docs/EXTENSION-DESIGN.md：Capability Builder 功能
  - 更新 ROADMAP.md：Phase 3 描述
  - 更新 AGENTS.md：移除舊 workflow 參考

## Doing

- Git commit 文件一致性更新

## Next

- 在 extension/ 目錄執行 npm install
- 測試 Extension 編譯與執行
- 發布到 VS Code Marketplace
