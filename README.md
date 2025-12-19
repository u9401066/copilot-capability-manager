# Copilot Capability Manager

> 🤖 VS Code Copilot Agent Mode 的能力管理系統 - 透過 `/cp.xxx` 指令觸發自動化工作流程

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

🌐 [繁體中文](README.zh-TW.md) | 📖 [機制說明](docs/PROMPT-FILES-MECHANISM.md)

## ✨ 特色

- 🎯 **`/cp.xxx` 斜線指令** - 在 Copilot Chat 輸入 `/cp.write_report` 即可觸發工作流程
- 🔄 **Workflow 引擎** - 將多個 Skills 串聯成自動化流程
- 🤖 **保持 Agent Mode** - 不切換到自定義 agent，保留完整工具訪問權限
- 📝 **Memory Bank** - 跨對話的專案記憶系統
- 🏛️ **Constitution-Bylaw** - 階層式規則架構

## 🚀 快速開始

### 1. 專案結構

確保 `.github/prompts/` 在 **workspace root**：

```
your-workspace/           # ← VS Code 開啟這個資料夾
├── .github/
│   └── prompts/          # ← Prompt Files 必須在這裡
│       ├── cp.write_report.prompt.md
│       ├── cp.project_check.prompt.md
│       └── ...
├── .claude/
│   ├── capability-manager/
│   │   └── cp.py         # 工作流程管理器
│   ├── workflows/        # 工作流程定義 (YAML)
│   └── skills/           # 技能模組
└── AGENTS.md             # Agent 指引文件
```

### 2. 使用方式

在 Copilot Chat 輸入：

```
/cp.write_report 我想搜尋 TIVA 相關文獻
```

系統會：
1. 注入 Prompt File 指令
2. **保持在 Agent Mode**（有完整工具權限）
3. 執行 `cp.py` 更新 AGENTS.md
4. 依序執行 workflow 中定義的 steps

## 📋 可用指令

| 指令 | 說明 | 步驟流程 |
|------|------|----------|
| `/cp.write_report [主題]` | 📝 撰寫報告 | 網路檢索 → 產出報告 → 格式化 → Memory 同步 |
| `/cp.project_check` | 🔍 專案檢查 | 檢查專案 → 文件更新 → Memory 同步 → 驗證 |
| `/cp.deploy` | 🚀 部署專案 | 測試 → Git → CI → 清理 |
| `/cp.cleanup` | 🧹 清理專案 | 清理暫存 → 重構（可選）→ Memory 同步 |
| `/cp.help` | ❓ 顯示說明 | - |

## 🔧 核心機制

### VS Code Prompt Files

本專案使用 **VS Code 1.99+ 的 Prompt Files 功能**：

```
.github/prompts/cp.write_report.prompt.md
```

```yaml
---
description: "📝 撰寫報告 - 執行完整的文獻搜尋與報告產出流程"
---

# 撰寫報告工作流程
請執行以下步驟...
```

**關鍵：不使用 `agent:` 欄位**，這樣會保持在標準 Agent Mode，擁有完整的工具訪問權限。

### Workflow 定義

`.claude/workflows/write_report.yaml`:

```yaml
workflow:
  id: write_report
  name: 撰寫報告
  steps:
    - step: 1
      skill: web-search
      name: 網路檢索
    - step: 2
      skill: report-generator
      name: 產出報告
    # ...
```

### cp.py 管理器

執行指令會更新 `AGENTS.md` 中的工作流程區塊：

```bash
python .claude/capability-manager/cp.py write_report "TIVA 文獻"
```

## 📁 完整專案結構

```
copilot-capability-manager/
├── .github/
│   ├── prompts/              # 🎯 Prompt Files (觸發 /cp.xxx)
│   │   ├── cp.write_report.prompt.md
│   │   ├── cp.project_check.prompt.md
│   │   ├── cp.deploy.prompt.md
│   │   ├── cp.cleanup.prompt.md
│   │   └── cp.help.prompt.md
│   └── bylaws/               # 📋 子法規
├── .claude/
│   ├── capability-manager/   # 🔧 能力管理器
│   │   └── cp.py
│   ├── workflows/            # 🔄 工作流程定義
│   │   ├── write_report.yaml
│   │   ├── project_check.yaml
│   │   ├── deploy.yaml
│   │   └── cleanup.yaml
│   └── skills/               # 🤖 技能模組
│       ├── web-search/
│       ├── report-generator/
│       ├── memory-updater/
│       └── ...
├── memory-bank/              # 🧠 專案記憶
├── AGENTS.md                 # 📖 Agent 指引
├── CONSTITUTION.md           # 📜 憲法（最高原則）
└── docs/
    └── PROMPT-FILES-MECHANISM.md  # 機制說明
```

## 🆚 與 SpecKit 的差異

| 項目 | SpecKit | Copilot Capability Manager |
|------|---------|---------------------------|
| 指令格式 | `/speckit.xxx` | `/cp.xxx` |
| 使用 agent | ✅ 切換到自定義 agent | ❌ 保持 Agent Mode |
| 工具權限 | 受限於 agent 定義 | 完整權限（MCP、終端機等） |
| 工作流程 | 單一 prompt | YAML 定義多步驟 workflow |

## 📖 文檔

- [機制說明](docs/PROMPT-FILES-MECHANISM.md) - Prompt Files 運作原理
- [AGENTS.md](AGENTS.md) - VS Code Copilot Agent 指引
- [CONSTITUTION.md](CONSTITUTION.md) - 專案憲法

## 🙏 致謝

- 靈感來自 [SpecKit](https://github.com/github/spec-kit) 的 Prompt Files 架構
- 基於 [template-is-all-you-need](https://github.com/u9401066/template-is-all-you-need) 模板

## 📄 License

[Apache License 2.0](LICENSE)
