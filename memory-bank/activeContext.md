# Active Context

> 📌 此檔案記錄當前工作焦點，每次工作階段開始時檢視，結束時更新。

## 🎯 當前焦點

- 完成 Copilot Capability Manager 重構，準備 Git commit

## 📝 進行中的變更

| 檔案 | 變更內容 |
|------|----------|
| `.github/prompts/*.prompt.md` | 重寫所有 Prompt Files，直接包含完整步驟 |
| `AGENTS.md` | 簡化為靜態專案上下文 |
| `README.md` | 更新為 Copilot Capability Manager 說明 |
| `docs/PROMPT-FILES-MECHANISM.md` | 新增機制說明文檔 |

## ⚠️ 待解決

- (無)

## 💡 重要決定

- **不使用 `agent:` 欄位**：保持 Agent Mode 的完整工具權限
- **Prompt Files 直接包含步驟**：不需要動態更新 AGENTS.md
- **Skills 保留在 `.claude/skills/`**：這是讓技能生效的必要位置

## 📁 相關檔案

```
.github/prompts/
  cp.write_report.prompt.md
  cp.project_check.prompt.md
  cp.deploy.prompt.md
  cp.cleanup.prompt.md
  cp.commit.prompt.md
  cp.new_skill.prompt.md
  cp.new_workflow.prompt.md
  cp.help.prompt.md
AGENTS.md
README.md
docs/PROMPT-FILES-MECHANISM.md
```

## 🔜 下一步

1. Git commit 並 push
2. 測試 /cp.xxx 指令

---
*Last updated: 2025-12-20*