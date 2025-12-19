---
description: "🧹 清理專案 - 清理暫存檔案與可選重構"
---

# 清理工作流程

請依序執行以下步驟：

## Step 1: 清理暫存檔案 `temp-cleaner`

📖 技能參考: `.claude/skills/temp-cleaner/SKILL.md`

**任務：**
- 清理常見暫存檔案：
  - `__pycache__/`, `*.pyc`
  - `node_modules/` (如需重建)
  - `.pytest_cache/`
  - `*.log`, `*.tmp`
  - `.DS_Store`
- 清理建置產物（可選）

**執行：**
```bash
# Python
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 或使用 git clean
git clean -fd --dry-run  # 預覽
git clean -fd            # 執行
```

---

## Step 2: 檔案重構 `file-restructurer` (可選)

📖 技能參考: `.claude/skills/file-restructurer/SKILL.md`

**任務（如需要）：**
- 整理檔案結構
- 移動錯置的檔案
- 合併重複檔案

---

## Step 3: Memory Bank 同步 `memory-updater`

📖 技能參考: `.claude/skills/memory-updater/SKILL.md`

**任務：**
- 更新 `progress.md`
- 記錄清理操作

---

## 📋 完成檢查

- [ ] Step 1: 暫存檔案已清理
- [ ] Step 2: 檔案結構已整理（如需要）
- [ ] Step 3: Memory Bank 已同步
