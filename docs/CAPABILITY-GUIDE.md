# 🧩 能力系統使用指南

> **能力 (Capability) = Skill + Workflow**
>
> Skill 是原子化的技能模組，Workflow 是串聯多個 Skill 的工作流程。

---

## 📖 目錄

- [概念說明](#概念說明)
- [新增 Skill](#新增-skill)
- [組合 Workflow](#組合-workflow)
- [最佳實踐](#最佳實踐)
- [範例](#範例)

---

## 概念說明

### 架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                    使用者輸入                                │
│                  「/cp.write_report」                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Workflow (cp.write_report)                      │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ .github/prompts/cp.write_report.prompt.md               ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Skill #1     │   │  Skill #2     │   │  Skill #3     │
│  web-search   │──▶│report-generator│──▶│memory-updater │
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  SKILL.md     │   │  SKILL.md     │   │  SKILL.md     │
└───────────────┘   └───────────────┘   └───────────────┘
```

### 名詞定義

| 名詞 | 說明 | 位置 |
|------|------|------|
| **Skill** | 單一、可重用的技能模組 | `.claude/skills/{skill-id}/SKILL.md` |
| **Workflow** | 串聯多個 Skill 的工作流程 | `.github/prompts/cp.{id}.prompt.md` |
| **Capability** | Skill + Workflow 的總稱 | — |

---

## 新增 Skill

### Step 1: 建立目錄結構

```
.claude/skills/{skill-id}/
└── SKILL.md
```

**命名規則：**
- 使用小寫英文 + 連字號（如 `code-reviewer`）
- 簡潔明確，描述技能用途
- 長度 1-64 字元

### Step 2: 撰寫 SKILL.md

使用以下模板：

```markdown
---
name: {skill-id}
description: |
  [一行英文摘要 - 說明這個技能做什麼]
  LOAD THIS SKILL WHEN: [觸發條件，包含中英文關鍵詞]
  CAPABILITIES: [具體功能列表]
---

# {技能名稱}

## 描述

{詳細說明這個技能的用途和適用場景}

## 觸發條件

- 「{觸發詞1}」
- 「{觸發詞2}」
- {情境描述}

## 執行流程

1. **{步驟1名稱}**
   - {具體動作}
   - {預期結果}

2. **{步驟2名稱}**
   - {具體動作}

3. **{步驟3名稱}**
   - {具體動作}

## 輸入參數

| 參數 | 說明 | 必要 | 預設值 |
|------|------|------|--------|
| {param1} | {說明} | ✅ | — |
| {param2} | {說明} | ❌ | {值} |

## 輸出格式

```
{輸出範例}
```

## 使用範例

**範例 1：{場景}**
```
用戶：「{輸入}」
結果：{輸出}
```

## 相關技能

- `{related-skill-1}` - {說明}
- `{related-skill-2}` - {說明}
```

### Step 3: 驗證 Skill

確認以下項目：

- [ ] `name` 與目錄名稱一致
- [ ] `description` 包含 `LOAD THIS SKILL WHEN:` 觸發條件
- [ ] 執行流程清晰可操作
- [ ] 有具體的輸入/輸出範例

---

## 組合 Workflow

### Step 1: 確認所需 Skills

列出工作流程需要的 Skills：

```
Workflow: 文獻回顧
├── Step 1: web-search      (搜尋文獻)
├── Step 2: report-generator (產出報告)
├── Step 3: report-formatter (格式化)
└── Step 4: memory-updater   (更新記憶)
```

### Step 2: 建立 Prompt File

位置：`.github/prompts/cp.{workflow-id}.prompt.md`

```markdown
---
description: "{emoji} {名稱} - {簡短說明}"
---

# {Workflow 名稱}

請依序執行以下步驟，完成後打勾 ✅：

## Step 1: {步驟名} `{skill-id}`

📖 技能參考: `.claude/skills/{skill-id}/SKILL.md`

**任務：**
- {任務描述 1}
- {任務描述 2}

**輸出：** {預期輸出}

---

## Step 2: {步驟名} `{skill-id}`

📖 技能參考: `.claude/skills/{skill-id}/SKILL.md`

**任務：**
- {任務描述}

**輸出：** {預期輸出}

---

## Step 3: {步驟名} `{skill-id}`

📖 技能參考: `.claude/skills/{skill-id}/SKILL.md`

**任務：**
- {任務描述}

---

## 📋 完成檢查

- [ ] Step 1: {完成條件描述}
- [ ] Step 2: {完成條件描述}
- [ ] Step 3: {完成條件描述}
```

### Step 3: 更新 Help 文件

編輯 `.github/prompts/cp.help.prompt.md`，加入新的 Workflow：

```markdown
| `/cp.{workflow-id}` | {emoji} {名稱} | {說明} |
```

### Step 4: 測試 Workflow

執行 `/cp.{workflow-id}` 確認流程正常運作。

---

## 最佳實踐

### Skill 設計原則

| 原則 | 說明 | ✅ 好的範例 | ❌ 不好的範例 |
|------|------|-------------|---------------|
| **單一職責** | 一個 Skill 只做一件事 | `code-reviewer` | `code-reviewer-and-fixer` |
| **可組合** | 可與其他 Skill 串聯 | `report-formatter` | `complete-report-system` |
| **明確觸發** | 清楚的觸發條件 | `LOAD WHEN: "commit"` | `description: 程式碼工具` |
| **有輸出** | 定義明確的輸出格式 | 輸出 Markdown 報告 | 無明確輸出 |

### Workflow 設計原則

1. **線性流程**：Step 1 → Step 2 → Step 3（避免分支）
2. **檢查點**：每個 Step 有明確的完成條件
3. **最後更新 Memory**：通常以 `memory-updater` 結尾
4. **錯誤處理**：說明失敗時的處理方式

### Description 格式（重要！）

為了讓 Agent 自動觸發 Skill，`description` 必須包含三個部分：

```yaml
description: |
  [英文摘要] - Agent 快速理解用途
  LOAD THIS SKILL WHEN: [觸發條件] - Agent 判斷是否載入
  CAPABILITIES: [功能列表] - Agent 確認是否符合需求
```

**範例：**

```yaml
description: |
  Generate comprehensive test suites following the test pyramid.
  LOAD THIS SKILL WHEN: User says "寫測試", "test", "coverage", "pytest" | needs test generation | code review requires tests.
  CAPABILITIES: pytest configuration, static analysis, unit/integration/E2E tests, coverage reports.
```

---

## 範例

### 範例 1: 建立「程式碼分析」Skill

**1. 建立檔案**

```
.claude/skills/code-analyzer/SKILL.md
```

**2. 撰寫內容**

```markdown
---
name: code-analyzer
description: |
  Analyze code structure, complexity, and potential issues.
  LOAD THIS SKILL WHEN: User says "分析程式碼", "analyze code", "程式碼品質", "complexity" | reviewing large codebase | architecture discussion.
  CAPABILITIES: Cyclomatic complexity, dependency analysis, code smell detection, architecture visualization.
---

# 程式碼分析技能

## 描述

分析程式碼結構、複雜度、依賴關係，找出潛在問題。

## 觸發條件

- 「分析這段程式碼」
- 「檢查程式碼品質」
- 「這個專案的架構如何？」

## 執行流程

1. **掃描程式碼結構**
   - 識別檔案、類別、函式
   - 建立依賴關係圖

2. **計算複雜度指標**
   - Cyclomatic Complexity
   - Lines of Code (LOC)
   - Coupling/Cohesion

3. **產出分析報告**
   - 問題清單
   - 改進建議
   - 視覺化圖表

## 輸出格式

```markdown
## 程式碼分析報告

### 📊 指標摘要
| 指標 | 值 | 狀態 |
|------|-----|------|
| 總行數 | 1,234 | ✅ |
| 平均複雜度 | 5.2 | ✅ |
| 高複雜度函式 | 3 | ⚠️ |

### ⚠️ 發現的問題
1. `utils.py:45` - 函式過長 (120 行)
2. `api.py:89` - 循環依賴

### 💡 改進建議
- 拆分 `process_data()` 為多個小函式
- 使用依賴注入解決循環依賴
```

## 使用範例

**範例：分析 Python 專案**
```
用戶：「分析 src/ 目錄的程式碼品質」
結果：產出程式碼分析報告，包含複雜度指標和改進建議
```
```

### 範例 2: 建立「程式碼審查」Workflow

**1. 建立檔案**

```
.github/prompts/cp.code_review.prompt.md
```

**2. 撰寫內容**

```markdown
---
description: "🔍 程式碼審查 - 完整的程式碼品質檢查流程"
---

# 程式碼審查工作流程

請依序執行以下步驟：

## Step 1: 分析程式碼 `code-analyzer`

📖 技能參考: `.claude/skills/code-analyzer/SKILL.md`

**任務：**
- 掃描指定的程式碼範圍
- 計算複雜度指標
- 識別潛在問題

**輸出：** 程式碼分析報告

---

## Step 2: 審查程式碼 `code-reviewer`

📖 技能參考: `.claude/skills/code-reviewer/SKILL.md`

**任務：**
- 根據分析結果進行深入審查
- 檢查程式碼風格
- 提出具體改進建議

**輸出：** 審查意見清單

---

## Step 3: 生成測試建議 `test-generator`

📖 技能參考: `.claude/skills/test-generator/SKILL.md`

**任務：**
- 針對高風險程式碼建議測試案例
- 評估現有測試覆蓋率

**輸出：** 測試建議清單

---

## Step 4: 更新記憶 `memory-updater`

📖 技能參考: `.claude/skills/memory-updater/SKILL.md`

**任務：**
- 記錄審查結果到 `progress.md`
- 重大發現記錄到 `decisionLog.md`

---

## 📋 完成檢查

- [ ] Step 1: 程式碼分析完成
- [ ] Step 2: 審查意見已產出
- [ ] Step 3: 測試建議已產出
- [ ] Step 4: Memory Bank 已更新
```

---

## 快速指令

| 指令 | 說明 |
|------|------|
| `/cp.new_skill` | 🧩 引導式建立新 Skill |
| `/cp.new_workflow` | 🔗 引導式建立新 Workflow |
| `/cp.help` | ❓ 查看所有可用指令 |

---

## 常見問題

### Q: Skill 沒有被自動觸發？

**A:** 檢查 `description` 是否包含 `LOAD THIS SKILL WHEN:` 格式，並確認觸發詞涵蓋中英文。

### Q: Workflow 執行到一半失敗了？

**A:** 檢查每個 Step 的 Skill 是否存在，並確認 SKILL.md 的執行流程描述清楚。

### Q: 如何讓多個 Skill 共享資料？

**A:** 使用 Memory Bank 作為中介：
1. 前一個 Skill 將結果寫入 `activeContext.md`
2. 後一個 Skill 從 `activeContext.md` 讀取

---

## 相關文件

- [Skill 機制改進分析](./SKILL-IMPROVEMENT-ANALYSIS.md)
- [Prompt Files 機制](./PROMPT-FILES-MECHANISM.md)
- [專案架構](../ARCHITECTURE.md)
