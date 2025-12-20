# Changelog

所有重要變更都會記錄在此檔案中。

格式基於 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)，
專案遵循 [語義化版本](https://semver.org/lang/zh-TW/)。

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
