---
description: "❓ 顯示所有可用的 /cp.xxx 指令"
---

# Copilot Capability Manager 指令說明

## 📋 可用指令

| 指令 | 說明 | 步驟流程 |
|------|------|----------|
| `/cp.write_report` | 📝 撰寫報告 | 網路檢索 → 產出報告 → 格式化 → Memory 同步 |
| `/cp.project_check` | 🔍 專案檢查 | 檢查專案 → 文件更新 → Memory 同步 → 驗證 |
| `/cp.deploy` | 🚀 部署專案 | 測試 → 檢查 → Memory → Git → Push → 清理 |
| `/cp.cleanup` | 🧹 清理專案 | 清理暫存 → 重構（可選）→ Memory 同步 |
| `/cp.commit` | 📦 Git 提交 | Memory → README → CHANGELOG → ROADMAP → Commit |
| `/cp.new_skill` | 🧩 新增技能 | 建立新的 Skill 模組 |
| `/cp.new_workflow` | 🔗 新增工作流程 | 建立新的 Workflow Prompt |
| `/cp.help` | ❓ 顯示說明 | 顯示此說明 |

## 🧩 擴展能力

### 新增 Skill（原子能力）

使用 `/cp.new_skill` 或手動建立：

```
.claude/skills/my-skill/
└── SKILL.md
```

### 新增 Workflow（組合能力）

使用 `/cp.new_workflow` 或手動建立：

```
.github/prompts/cp.my-workflow.prompt.md
```

## 📁 相關檔案

| 檔案 | 說明 |
|------|------|
| `.github/prompts/*.prompt.md` | Workflow 定義（觸發 `/cp.xxx`） |
| `.claude/skills/*/SKILL.md` | Skill 定義 |
| `AGENTS.md` | 專案上下文指引 |
| `memory-bank/` | 專案記憶系統 |

## 📖 更多資訊

- [README.md](../../README.md) - 專案說明
- [AGENTS.md](../../AGENTS.md) - Agent 指引
- [docs/PROMPT-FILES-MECHANISM.md](../../docs/PROMPT-FILES-MECHANISM.md) - 機制說明
