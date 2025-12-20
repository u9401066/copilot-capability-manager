# Active Context

> 📌 此檔案記錄當前工作焦點，每次工作階段開始時檢視，結束時更新。

## 🎯 當前焦點

- 完成 VS Code Extension 實作，準備 Git commit

## 📝 進行中的變更

| 檔案 | 變更內容 |
|------|----------|
| `extension/` | 新增完整 VS Code Extension 實作 |
| `extension/package.json` | 擴充套件配置：commands, views, menus |
| `extension/src/services/` | SkillService, CapabilityService |
| `extension/src/providers/` | TreeView 和 Webview Providers |
| `extension/src/types/` | TypeScript 型別定義 |
| `extension/src/commands/` | 命令註冊 |

## ⚠️ 待解決

- 需要在 extension/ 執行 npm install
- 需要測試 TypeScript 編譯

## 💡 重要決定

- **Extension 獨立目錄**：extension/ 有自己的 package.json 和 tsconfig
- **採用 TreeView + Webview**：Skill 列表用 TreeView，編輯器用 Webview
- **分類管理**：Skills 按 category 分組顯示

## 📁 相關檔案

```
extension/
├── package.json
├── tsconfig.json
└── src/
    ├── extension.ts
    ├── commands/index.ts
    ├── providers/
    │   ├── SkillTreeProvider.ts
    │   ├── SkillManagerProvider.ts
    │   └── CapabilityBuilderProvider.ts
    ├── services/
    │   ├── SkillService.ts
    │   └── CapabilityService.ts
    └── types/
        ├── skill.ts
        └── capability.ts
```

## 🔜 下一步

1. Git commit VS Code Extension
2. npm install && npm run compile
3. 測試 Extension

---
*Last updated: 2025-12-20*