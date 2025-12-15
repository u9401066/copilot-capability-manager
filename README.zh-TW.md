# template-is-all-you-need

> 🏗️ AI 輔助開發專案模板 - 整合 Claude Skills、Memory Bank 與憲法-子法架構

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

🌐 [English](README.md)

## ✨ 特色

- 🏛️ **憲法-子法架構** - 類似 speckit 的層級規則系統
- 🤖 **Claude Skills** - 12+ 個模組化 AI 技能，自動化開發流程
- 📝 **Memory Bank** - 跨對話專案記憶系統
- 🏗️ **DDD 架構** - 領域驅動設計 + DAL 獨立
- 🔄 **Git 自動化** - 提交前自動更新文檔
- 🐍 **Python 環境** - uv 優先的套件管理

## 📁 專案結構

```
template-is-all-you-need/
├── CONSTITUTION.md          # 📜 專案憲法（最高原則）
├── .github/
│   ├── bylaws/              # 📋 子法
│   │   ├── ddd-architecture.md
│   │   ├── git-workflow.md
│   │   ├── memory-bank.md
│   │   └── python-environment.md
│   ├── workflows/           # ⚙️ CI/CD
│   ├── ISSUE_TEMPLATE/      # 📝 Issue 模板
│   └── copilot-instructions.md
├── .claude/skills/          # 🤖 Claude Skills
│   ├── git-precommit/       # Git 提交編排器
│   ├── ddd-architect/       # DDD 架構輔助
│   ├── code-refactor/       # 程式碼重構
│   ├── memory-updater/      # Memory Bank 同步
│   ├── memory-checkpoint/   # 預摘要記憶檢查點
│   ├── readme-updater/      # README 更新
│   ├── readme-i18n/         # README 國際化
│   ├── changelog-updater/   # CHANGELOG 更新
│   ├── roadmap-updater/     # ROADMAP 更新
│   ├── code-reviewer/       # 程式碼審查
│   ├── test-generator/      # 測試生成
│   └── project-init/        # 專案初始化
├── memory-bank/             # 🧠 專案記憶
├── README.md                # 主 README（英文）
├── README.zh-TW.md          # 本檔案（中文）
├── CHANGELOG.md
├── ROADMAP.md
├── ARCHITECTURE.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
└── LICENSE
```

## 🚀 快速開始

### 作為模板使用

```bash
# 方式 1：GitHub CLI
gh repo create my-project --template u9401066/template-is-all-you-need

# 方式 2：手動 clone
git clone https://github.com/u9401066/template-is-all-you-need.git my-project
cd my-project
rm -rf .git && git init
```

### VS Code 設定

確保已安裝 GitHub Copilot，專案會自動啟用：
- Claude Skills 支援
- 自定義指令
- Agent 模式

## 🤖 Skills 使用

| 指令 | 功能 |
|------|------|
| 「準備 commit」 | 執行完整 Git 提交流程 |
| 「快速 commit」 | 只同步 Memory Bank |
| 「建立功能 X」 | 生成 DDD 結構 |
| 「review 程式碼」 | 程式碼審查 |
| 「生成測試」 | 自動生成測試 |
| 「checkpoint」 | 在上下文丟失前保存記憶 |

## 🏛️ 架構原則

本專案遵循：

1. **DDD (Domain-Driven Design)** - 領域驅動設計
2. **DAL 獨立** - 資料存取層分離
3. **文檔優先** - 程式碼是文檔的編譯產物
4. **Memory Bank 綁定** - 操作即時同步記憶

詳見 [CONSTITUTION.md](CONSTITUTION.md)

## 📋 文檔

- [憲法](CONSTITUTION.md) - 最高原則
- [架構說明](ARCHITECTURE.md) - 系統架構
- [變更日誌](CHANGELOG.md) - 版本歷史
- [路線圖](ROADMAP.md) - 功能規劃
- [貢獻指南](CONTRIBUTING.md) - 如何貢獻
- [CLAUDE.md](CLAUDE.md) - Claude Code 專用指引
- [AGENTS.md](AGENTS.md) - VS Code Copilot Agent 指引

## 🧪 測試支援

模板包含完整的測試配置：

- **靜態分析**：ruff、mypy、bandit
- **單元測試**：pytest，80% 覆蓋率要求
- **整合測試**：pytest-asyncio
- **E2E 測試**：Playwright
- **CI/CD**：GitHub Actions，6 個 jobs

## 📄 授權

[Apache License 2.0](LICENSE)
