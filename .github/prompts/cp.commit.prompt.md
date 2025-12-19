---
description: "📦 Git Commit - 提交前完整檢查流程"
---

# Git Commit 工作流程

請依序執行以下步驟：

## Step 1: Memory Bank 同步 `memory-updater` [必要]

📖 技能參考: `.claude/skills/memory-updater/SKILL.md`

**任務：**
- 更新 `memory-bank/progress.md`：
  - 將完成項目移到 Done
  - 更新 Doing 和 Next
- 更新 `memory-bank/activeContext.md`

---

## Step 2: README 更新 `readme-updater` [可選]

📖 技能參考: `.claude/skills/readme-updater/SKILL.md`

**檢查：**
- 功能說明是否需要更新？
- 使用方式是否有變更？

如需更新，執行更新。如無變更，跳過。

---

## Step 3: CHANGELOG 更新 `changelog-updater` [可選]

📖 技能參考: `.claude/skills/changelog-updater/SKILL.md`

**檢查：**
- 是否有新功能/修復/變更需要記錄？
- 版本號是否需要更新？

格式：
```markdown
## [Unreleased]
### Added
- 新功能描述

### Changed
- 變更描述

### Fixed
- 修復描述
```

---

## Step 4: ROADMAP 更新 `roadmap-updater` [可選]

📖 技能參考: `.claude/skills/roadmap-updater/SKILL.md`

**檢查：**
- 是否有 roadmap 項目已完成？
- 更新狀態標記

---

## Step 5: 準備提交 `git-precommit`

📖 技能參考: `.claude/skills/git-precommit/SKILL.md`

**任務：**
1. 查看變更：
   ```bash
   git status
   git diff --staged
   ```

2. Stage 檔案：
   ```bash
   git add .
   ```

3. 生成 Commit Message（遵循 Conventional Commits）：
   - `feat:` 新功能
   - `fix:` 修復
   - `docs:` 文檔
   - `refactor:` 重構
   - `chore:` 雜項

4. 執行提交：
   ```bash
   git commit -m "type(scope): description"
   ```

---

## 📋 完成檢查

- [ ] Step 1: Memory Bank 已同步 ✅ 必要
- [ ] Step 2: README 已檢查/更新
- [ ] Step 3: CHANGELOG 已檢查/更新
- [ ] Step 4: ROADMAP 已檢查/更新
- [ ] Step 5: Git 已提交

---

## ⚡ 快速模式

如果只需要快速提交（跳過文檔更新）：

```
只執行 Step 1 (Memory Bank) + Step 5 (Git Commit)
```
