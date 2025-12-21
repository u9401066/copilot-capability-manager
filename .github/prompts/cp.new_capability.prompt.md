---
description: "🔗 新增 Capability - 互動式建立新的能力組合"
---

# 🔗 新增 Capability（能力組合）

我會引導你建立一個新的 Capability。請回答以下問題：

---

## 📝 Step 1: 基本資訊

請提供：

1. **Capability ID**（用於指令名稱，小寫+底線）
   - 例如：`code_review`、`daily_standup`、`release_notes`

2. **顯示名稱**（中文或英文皆可）
   - 例如：`程式碼審查`、`每日站會`、`發布說明`

3. **簡短描述**（一句話說明用途）
   - 例如：`審查程式碼品質並提供改進建議`

4. **Emoji 圖示**
   - 例如：🔍、📊、🚀

---

## 📝 Step 2: 選擇 Skills

從以下可用 Skills 中選擇要組合的：

### 🔬 研究類
- `web-search` - 網路/文獻檢索

### 📝 文件類
- `report-generator` - 報告產出
- `report-formatter` - 報告格式化
- `readme-updater` - README 更新
- `changelog-updater` - CHANGELOG 更新
- `roadmap-updater` - ROADMAP 更新

### 📦 Git 類
- `git-precommit` - 提交前檢查
- `git-pusher` - Git 推送

### 🔧 維護類
- `memory-updater` - Memory Bank 同步
- `memory-checkpoint` - 記憶檢查點
- `temp-cleaner` - 清理暫存
- `file-restructurer` - 檔案重構
- `code-refactor` - 程式碼重構

### ✅ 品質類
- `project-checker` - 專案狀態檢查
- `code-reviewer` - 程式碼審查
- `test-generator` - 測試生成

### 🏗️ 架構類
- `ddd-architect` - DDD 架構輔助
- `project-init` - 專案初始化

**請按執行順序列出要使用的 Skills**（例如：`code-reviewer → test-generator → memory-updater`）

---

## 🔧 Step 3: 我會幫你建立

收到你的回答後，我會：

1. **建立 Prompt File**
   ```
   .github/prompts/cp.{capability-id}.prompt.md
   ```

2. **生成內容**（包含每個 Step 的任務描述）

3. **更新 Help**
   - 將新 Capability 加入 `cp.help.prompt.md`

4. **更新 AGENTS.md**
   - 將新 Capability 加入指令表

5. **同步 Memory Bank**
   - 記錄到 `progress.md`

---

## 💡 範例對話

**你**：
> ID: `code_review`
> 名稱: 程式碼審查
> 描述: 審查程式碼品質並產出報告
> Emoji: 🔍
> Skills: code-reviewer → report-generator → memory-updater

**我**：建立 `cp.code_review.prompt.md`，包含 3 個 Steps...

---

## ⏳ 請開始回答 Step 1 的問題！

