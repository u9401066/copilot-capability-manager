# Copilot Capability Manager

> 🤖 VS Code 擴充套件 - 透過 GUI 管理 AI Skills 並組合成自動化工作流程

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Status](https://img.shields.io/badge/Status-🚧_Under_Construction-yellow.svg)]()

> ⚠️ **注意：此專案正在積極開發中，API 和功能可能會有重大變更。**

🌐 [繁體中文](README.zh-TW.md) | 📖 [架構設計](ARCHITECTURE.md) | 🗺️ [Roadmap](ROADMAP.md)

## 🎯 願景

將 AI 能力模組化、視覺化，讓使用者可以：

1. **管理 Skills** - 透過 GUI 新增、編輯、設定 AI 技能（包含 MCP Tools）
2. **組合 Capabilities** - 拖拉排序 Skills 形成工作流程
3. **一鍵執行** - 透過 `/cp.xxx` 斜線指令觸發

## ✨ 功能特色

### 🧩 Skill Manager（技能管理器）

- 📋 **Skill 列表** - 瀏覽所有可用技能
- ➕ **新增 Skill** - GUI 表單建立新技能
- ⚙️ **MCP Tool 整合** - 選擇並設定 MCP 工具
- 📝 **Prompt 編輯器** - 編輯技能的執行指令
- 🏷️ **標籤分類** - 研究、文件、Git、維護等

### 🔗 Capability Builder（能力組合器）

- 🎨 **拖拉介面** - 拖動 Skills 排列順序
- 🔄 **重複使用** - 同一 Skill 可多次使用
- 📊 **流程預覽** - 視覺化工作流程
- 💾 **匯出 Prompt** - 自動生成 `.prompt.md` 檔案

### ⚡ 執行引擎

- `/cp.xxx` 斜線指令觸發
- 保持 Agent Mode 完整工具權限
- 依序執行 Skills
- 自動同步 Memory Bank

## 📁 專案結構

```
copilot-capability-manager/
├── src/                          # 🔧 VS Code 擴充套件原始碼
│   ├── extension.ts              # 擴充套件入口
│   ├── views/                    # Webview UI
│   │   ├── SkillManager.ts       # Skill 管理頁面
│   │   └── CapabilityBuilder.ts  # Capability 組合頁面
│   ├── providers/                # 資料提供者
│   │   ├── SkillProvider.ts
│   │   └── CapabilityProvider.ts
│   └── services/                 # 核心服務
│       ├── SkillService.ts
│       ├── McpService.ts
│       └── PromptGenerator.ts
├── webview-ui/                   # 🎨 前端 UI (React/Vue)
├── .github/prompts/              # 📝 生成的 Prompt Files
├── .claude/skills/               # 🧩 Skill 定義
├── memory-bank/                  # 🧠 專案記憶
└── package.json                  # 擴充套件配置
```

## 🚀 開發階段

### Phase 1: 核心機制 ✅
- [x] Prompt Files 機制
- [x] Skill 模組架構
- [x] `/cp.xxx` 斜線指令

### Phase 2: VS Code Extension 🚧
- [ ] 擴充套件基礎架構
- [ ] Skill Manager GUI
- [ ] Capability Builder GUI

### Phase 3: MCP 整合
- [ ] MCP Tool 選擇器
- [ ] Tool 參數設定
- [ ] 動態工具載入

### Phase 4: 進階功能
- [ ] Skill 市集（匯入/匯出）
- [ ] 雲端同步
- [ ] 團隊共享

## 🛠️ 技術棧

| 層級 | 技術 |
|------|------|
| **擴充套件** | TypeScript, VS Code Extension API |
| **UI 框架** | React / Vue (Webview) |
| **資料格式** | YAML (Skills), Markdown (Prompts) |
| **MCP 整合** | Model Context Protocol SDK |
| **儲存** | 本地檔案 + VS Code Settings |

## 📖 文檔

- [架構設計](ARCHITECTURE.md) - 系統架構與組件設計
- [**能力系統指南**](docs/CAPABILITY-GUIDE.md) - 📚 如何新增 Skill 與 Workflow
- [擴充套件設計](docs/EXTENSION-DESIGN.md) - VS Code Extension 詳細設計
- [Prompt Files 機制](docs/PROMPT-FILES-MECHANISM.md) - 當前運作原理
- [Skill 改進分析](docs/SKILL-IMPROVEMENT-ANALYSIS.md) - Skill 觸發機制改進
- [AGENTS.md](AGENTS.md) - Agent 指引
- [Roadmap](ROADMAP.md) - 開發路線圖

## 🤝 貢獻

歡迎貢獻！請參閱 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 📄 License

[Apache License 2.0](LICENSE)
