---
description: "🔍 專案檢查 - 檢查專案狀態與文件完整性"
---

# 專案檢查工作流程

請依序執行以下步驟：

## Step 1: 專案狀態檢查 `project-checker`

📖 技能參考: `.claude/skills/project-checker/SKILL.md`

**任務：**
- 檢查必要文件是否存在：
  - [ ] README.md
  - [ ] CHANGELOG.md
  - [ ] CONSTITUTION.md
  - [ ] AGENTS.md
  - [ ] .gitignore
- 檢查 Memory Bank 狀態
- 檢查 Git 狀態（未提交變更）

**輸出：** 專案狀態報告

---

## Step 2: 文件更新 `doc-updater`

📖 技能參考: `.claude/skills/doc-updater/SKILL.md`

**任務：**
- 根據檢查結果更新過時文件
- 同步程式碼與文檔

---

## Step 3: Memory Bank 同步 `memory-updater`

📖 技能參考: `.claude/skills/memory-updater/SKILL.md`

**任務：**
- 更新 `progress.md`
- 確保 `activeContext.md` 反映當前狀態

---

## Step 4: 驗證

**任務：**
- 重新執行 Step 1 確認問題已解決
- 輸出最終狀態報告

---

## 📋 完成檢查

- [ ] Step 1: 專案狀態已檢查
- [ ] Step 2: 文件已更新
- [ ] Step 3: Memory Bank 已同步
- [ ] Step 4: 驗證通過
