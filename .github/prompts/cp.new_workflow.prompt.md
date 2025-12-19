---
description: "🔗 新增工作流程 - 建立新的 Workflow Prompt"
---

# 新增 Workflow 工作流程

## 📝 請提供以下資訊

1. **Workflow ID**: (例如: `review_code`)
2. **Workflow 名稱**: (例如: `程式碼審查`)
3. **說明**: (這個 workflow 做什麼？)
4. **包含的 Skills**: (依序列出要串聯的 skills)

---

## 🔧 執行步驟

### Step 1: 確認 Skills 存在

檢查所有要使用的 skills 是否存在於 `.claude/skills/`

### Step 2: 建立 Prompt File

建立 `.github/prompts/cp.{workflow-id}.prompt.md`：

```markdown
---
description: "{emoji} {名稱} - {說明}"
---

# {Workflow 名稱}

請依序執行以下步驟：

## Step 1: {步驟名} `{skill-id}`

📖 技能參考: `.claude/skills/{skill-id}/SKILL.md`

**任務：**
- {任務描述}

**輸出：** {輸出描述}

---

## Step 2: {步驟名} `{skill-id}`

📖 技能參考: `.claude/skills/{skill-id}/SKILL.md`

**任務：**
- {任務描述}

---

## 📋 完成檢查

- [ ] Step 1: {描述}
- [ ] Step 2: {描述}
```

### Step 3: 更新說明

更新 `cp.help.prompt.md` 加入新的 workflow

### Step 4: 更新 Memory Bank

記錄新 workflow 到 `progress.md`

---

## 📋 完成檢查

- [ ] Skills 確認存在
- [ ] Prompt file 已建立
- [ ] Help 已更新
- [ ] Memory Bank 已更新

---

## 💡 Workflow 設計原則

1. **單一職責**: 每個 workflow 專注一個目標
2. **可組合**: 使用現有 skills 組合
3. **有檢查點**: 每個 step 有明確的輸出
4. **Memory 同步**: 最後一步通常是 `memory-updater`
