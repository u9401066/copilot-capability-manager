# Copilot 自定義指令

## 🏗️ 核心概念（必須理解）

```
Tool (工具)     → 單一 API 調用
Skill (技能)    → 多 Tools 編排，完成小任務
Capability (能力) → 動態 Skill 狀態機，可迴圈、分支、跨對話
```

**重要**：Capability ≠ Workflow。Capability 支援迴圈執行和狀態追蹤。

---

## ⚠️ 強制執行規則（必須遵守）

### Capability 執行規則

1. **啟動 Capability 時**：
   ```
   必須建立 memory-bank/checkpoints/{id}-{timestamp}.json
   ```

2. **每完成一個項目時**：
   ```
   必須更新 checkpoint 的 completedItems 和 progress
   ```

3. **迴圈執行時**：
   - 每次迴圈必須檢查 checkpoint
   - 必須有明確的終止條件
   - 不可無限迴圈

4. **錯誤處理**：
   - 必須記錄錯誤到 checkpoint
   - 不可靜默失敗

### Checkpoint 格式

```json
{
  "capability": "capability-id",
  "status": "in-progress",
  "progress": { "total": N, "completed": M },
  "currentItem": "item-id",
  "completedItems": [],
  "errors": []
}
```

---

## ⚡ /cp.* 指令處理 (最高優先級)

**當用戶輸入以 `/cp.` 開頭的訊息時，你必須：**

### Step 1: 執行終端機指令更新 AGENTS.md
```powershell
python .claude/capability-manager/cp.py {workflow_name} "{參數}"
```

### Step 2: 讀取更新後的 AGENTS.md
讀取專案根目錄的 `AGENTS.md` 檔案

### Step 3: 按照 AGENTS.md 中的工作流程執行
依序執行「當前執行的工作流程」區塊中的每個步驟

### Step 4: 讀取對應的 SKILL.md
每個步驟執行前，先讀取 `.claude/skills/{skill_id}/SKILL.md`

**範例**：
- `/cp.write_report AI醫療` → 執行 `python .claude/capability-manager/cp.py write_report "AI醫療"`
- `/cp.project_check` → 執行 `python .claude/capability-manager/cp.py project_check`
- `/cp.clear` → 執行 `python .claude/capability-manager/cp.py clear`

---

## 開發哲學 💡
> **「想要寫文件的時候，就更新 Memory Bank 吧！」**
> 
> **「想要零散測試的時候，就寫測試檔案進 tests/ 資料夾吧！」**

## 法規遵循
你必須遵守以下法規層級：
1. **憲法**：`CONSTITUTION.md` - 最高原則
2. **子法**：`.github/bylaws/*.md` - 細則規範
3. **技能**：`.claude/skills/*/SKILL.md` - 操作程序
4. **動態指引**：`AGENTS.md` - 當前工作流程狀態（每次對話開始時請讀取）

## 架構原則
- 採用 DDD (Domain-Driven Design)
- DAL (Data Access Layer) 必須獨立
- 參見子法：`.github/bylaws/ddd-architecture.md`

## Python 環境（uv 優先）
- 新專案必須使用 uv 管理套件
- 必須建立虛擬環境（禁止全域安裝）
- 參見子法：`.github/bylaws/python-environment.md`

## Memory Bank 同步
每次重要操作必須更新 Memory Bank：
- 參見子法：`.github/bylaws/memory-bank.md`
- 目錄：`memory-bank/`

## Git 工作流
提交前必須執行檢查清單：
- 參見子法：`.github/bylaws/git-workflow.md`
- 觸發 Skill：`git-precommit`

---

## 🎯 Skill 自動觸發指引

**重要**：當偵測到以下情境時，你必須主動讀取對應的 SKILL.md 檔案！

| 情境 | 讀取 Skill | 路徑 |
|------|------------|------|
| 用戶要 commit/push/提交 | `git-precommit` | `.claude/skills/git-precommit/SKILL.md` |
| 完成任務/對話結束 | `memory-updater` | `.claude/skills/memory-updater/SKILL.md` |
| 審查/檢查程式碼 | `code-reviewer` | `.claude/skills/code-reviewer/SKILL.md` |
| 重構/拆分/模組化 | `code-refactor` | `.claude/skills/code-refactor/SKILL.md` |
| 寫測試/測試覆蓋 | `test-generator` | `.claude/skills/test-generator/SKILL.md` |
| 更新 README | `readme-updater` | `.claude/skills/readme-updater/SKILL.md` |
| 更新 CHANGELOG | `changelog-updater` | `.claude/skills/changelog-updater/SKILL.md` |
| 新功能/新模組 | `ddd-architect` | `.claude/skills/ddd-architect/SKILL.md` |

**執行方式**：讀取 SKILL.md → 依照指令執行 → 更新 Memory Bank

---

## 回應風格
- 使用繁體中文
- 提供清晰的步驟說明
- 引用相關法規條文
