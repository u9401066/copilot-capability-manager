# AGENTS.md - VS Code Copilot Agent 指引

此文件為 VS Code GitHub Copilot 的 Agent Mode 提供專案上下文。

---

## 🎯 /cp.xxx 指令系統

本專案使用 **Prompt Files** 實現自定義斜線指令。

### 可用指令

| 指令 | 說明 | 用途 |
|------|------|------|
| `/cp.write_report` | 📝 撰寫報告 | 文獻搜尋 → 報告產出 → 格式化 |
| `/cp.project_check` | 🔍 專案檢查 | 檢查專案狀態與文件完整性 |
| `/cp.deploy` | 🚀 部署專案 | 測試 → Git → Push |
| `/cp.cleanup` | 🧹 清理專案 | 清理暫存檔案 |
| `/cp.commit` | 📦 Git 提交 | Memory 同步 → 文件更新 → Commit |
| `/cp.new_skill` | 🧩 新增技能 | 建立新的 Skill 模組 |
| `/cp.new_workflow` | 🔗 新增工作流程 | 建立新的 Workflow |
| `/cp.help` | ❓ 顯示說明 | 列出所有指令 |

### 運作原理

```
用戶輸入 /cp.xxx
    ↓
VS Code 載入 .github/prompts/cp.xxx.prompt.md
    ↓
Prompt 內容注入到 Agent Mode
    ↓
Agent 依照步驟執行（保留完整工具權限）
```

---

## 📦 Skill 系統

Skills 是可重用的原子能力，位於 `.claude/skills/`。

### 可用 Skills

| 類別 | Skill ID | 說明 |
|------|----------|------|
| **研究** | `web-search` | 網路/文獻檢索 |
| **文件** | `report-generator` | 報告產出 |
| | `report-formatter` | 報告格式化 |
| | `doc-updater` | 文件更新 |
| | `readme-updater` | README 更新 |
| | `changelog-updater` | CHANGELOG 更新 |
| | `roadmap-updater` | ROADMAP 更新 |
| **專案** | `project-checker` | 專案狀態檢查 |
| | `memory-updater` | Memory Bank 同步 |
| | `memory-checkpoint` | 記憶檢查點 |
| **品質** | `project-tester` | 專案測試 |
| | `code-reviewer` | 程式碼審查 |
| | `test-generator` | 測試生成 |
| **Git** | `git-precommit` | 提交前檢查 |
| | `git-pusher` | Git 推送 |
| **維護** | `temp-cleaner` | 清理暫存 |
| | `file-restructurer` | 檔案重構 |
| | `code-refactor` | 程式碼重構 |
| **架構** | `ddd-architect` | DDD 架構輔助 |
| | `project-init` | 專案初始化 |

### 使用 Skill

執行 Skill 時，參考對應的 SKILL.md：

```
.claude/skills/{skill-id}/SKILL.md
```

---

## 📋 專案規則

### 法規層級

1. **憲法**：`CONSTITUTION.md` - 最高原則
2. **子法**：`.github/bylaws/*.md` - 細則規範
3. **技能**：`.claude/skills/*/SKILL.md` - 操作程序

### Memory Bank 同步

每次重要操作必須更新 Memory Bank：

| 操作 | 更新文件 |
|------|----------|
| 完成任務 | `memory-bank/progress.md` (Done) |
| 開始任務 | `memory-bank/progress.md` (Doing) |
| 重大決策 | `memory-bank/decisionLog.md` |
| 架構變更 | `memory-bank/architect.md` |

### Git 工作流

提交前檢查清單：
- ✅ Memory Bank 同步（必要）
- 📖 README 更新（如需要）
- 📋 CHANGELOG 更新（如需要）
- 🗺️ ROADMAP 更新（如需要）

---

## 🔧 擴展能力

### 新增 Skill

1. 建立目錄：`.claude/skills/{skill-id}/`
2. 建立 `SKILL.md` 定義技能
3. 在 Workflow 中引用

### 新增 Workflow

1. 建立 `.github/prompts/cp.{id}.prompt.md`
2. 定義執行步驟，引用 Skills
3. 更新 `cp.help.prompt.md`

詳見：`/cp.new_skill` 和 `/cp.new_workflow`

---

## 📁 專案結構

```
copilot-capability-manager/
├── .github/
│   ├── prompts/           # Prompt Files (觸發 /cp.xxx)
│   └── bylaws/            # 子法規
├── .claude/
│   └── skills/            # Skill 模組
├── memory-bank/           # 專案記憶
├── AGENTS.md              # 本文件
├── CONSTITUTION.md        # 憲法
└── README.md              # 專案說明
```

---

## 回應風格

- 使用**繁體中文**
- 提供清晰的步驟說明
- 執行操作後更新 Memory Bank
