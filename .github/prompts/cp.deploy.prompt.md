---
description: "🚀 部署專案 - 完整的測試、Git 提交與部署流程"
---

# 部署工作流程

請依序執行以下步驟：

## Step 1: 專案測試 `project-tester`

📖 技能參考: `.claude/skills/project-tester/SKILL.md`

**任務：**
- 執行測試（如有）：
  ```bash
  pytest  # Python
  npm test  # Node.js
  ```
- 確認測試通過

**輸出：** 測試結果

---

## Step 2: 專案檢查 `project-checker`

📖 技能參考: `.claude/skills/project-checker/SKILL.md`

**任務：**
- 檢查必要文件完整性
- 確認無遺漏的變更

---

## Step 3: Memory Bank 同步 `memory-updater`

📖 技能參考: `.claude/skills/memory-updater/SKILL.md`

**任務：**
- 更新 `progress.md`（Done 區塊）
- 更新 `activeContext.md`

---

## Step 4: Git 提交 `git-precommit`

📖 技能參考: `.claude/skills/git-precommit/SKILL.md`

**任務：**
- 確認 staged files
- 生成 commit message（遵循 Conventional Commits）
- 執行 commit：
  ```bash
  git add .
  git commit -m "type: description"
  ```

---

## Step 5: Git 推送 `git-pusher`

📖 技能參考: `.claude/skills/git-pusher/SKILL.md`

**任務：**
- 推送到遠端：
  ```bash
  git push origin main
  ```
- 確認 CI 狀態（如有）

---

## Step 6: 清理 `temp-cleaner`

📖 技能參考: `.claude/skills/temp-cleaner/SKILL.md`

**任務：**
- 清理暫存檔案
- 清理建置產物（如需要）

---

## 📋 完成檢查

- [ ] Step 1: 測試通過
- [ ] Step 2: 專案檢查通過
- [ ] Step 3: Memory Bank 已同步
- [ ] Step 4: Git 已提交
- [ ] Step 5: 已推送到遠端
- [ ] Step 6: 清理完成
