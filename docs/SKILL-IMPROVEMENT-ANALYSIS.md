# Skill 機制改進分析報告

> 📅 分析日期：2024-12-20

---

## 📊 問題診斷

### 1. 為什麼 Skill 沒有被觸發？

**根本原因**：目前專案使用的 `.claude/skills/` 結構**並非 VS Code 原生機制**，而是依賴 `copilot-instructions.md` 中的 `<skills>` 標籤讓 Agent 「知道」有這些技能。

```
當前機制流程：
┌─────────────────────────────────────────────────┐
│  copilot-instructions.md                        │
│  ├── <skills> 標籤列出所有技能                  │
│  │   └── 包含 name, description, file path      │
│  └── Agent 看到後「可能」會讀取 SKILL.md        │
└─────────────────────────────────────────────────┘
          ↓ (問題點)
    Agent 不一定會自動讀取 SKILL.md！
    只有當用戶明確提到觸發詞，Agent 才「可能」聯想到
```

### 2. 官方 Agent Skills 機制（VS Code Insiders）

根據 [agentskills.io](https://agentskills.io) 和 VS Code 文檔：

```
官方機制流程：
┌─────────────────────────────────────────────────┐
│  Progressive Disclosure（漸進式載入）           │
│                                                 │
│  Level 1: Discovery（啟動時）                   │
│  └── 載入所有 skill 的 name + description       │
│                                                 │
│  Level 2: Activation（匹配時）                  │
│  └── 當任務匹配 description，載入完整 SKILL.md  │
│                                                 │
│  Level 3: Resources（需要時）                   │
│  └── 按需載入 scripts/, references/, assets/    │
└─────────────────────────────────────────────────┘
```

**關鍵差異**：
- 官方機制：**自動**基於 description 匹配載入
- 當前機制：依賴 Agent **主動**讀取 `<skills>` 標籤後決定

---

## 🔧 改進方案

### 方案 A：遷移到官方 `.github/skills/` 格式

**優點**：
- ✅ 標準格式，跨工具相容（VS Code, CLI, GitHub Copilot）
- ✅ 自動載入機制（Progressive Disclosure）
- ✅ 未來相容性佳

**缺點**：
- ⚠️ 需要 VS Code Insiders
- ⚠️ 需要啟用 `chat.useAgentSkills` 設定
- ⚠️ 功能仍在 Preview

**遷移步驟**：
```
1. 建立 .github/skills/ 目錄
2. 將 .claude/skills/* 遷移過去
3. 修正 SKILL.md 格式符合官方規格
4. 啟用 VS Code 設定
```

### 方案 B：強化當前機制（短期方案）

**改進 description 讓 Agent 更容易匹配**：

```yaml
# 不佳的 description（當前）
description: Comprehensive code review checking quality...

# 改進的 description（廣設觸發詞 + 明確場景）
description: |
  Code review and quality analysis. Automatically activate when:
  - User asks to review, check, or audit code
  - User mentions 'PR', 'pull request', 'code quality', 'bug', 'security'
  - User says '審查', '檢查', '看一下程式碼', '幫我看看'
  - Before git commit or push operations
  - When discussing code improvements or refactoring
```

### 方案 C：混合策略（推薦）

```
短期：強化 description + 在 copilot-instructions.md 添加觸發指引
長期：準備遷移到 .github/skills/ 官方格式
```

---

## 📝 官方 SKILL.md 格式規格

### 必要欄位

```yaml
---
name: skill-name          # 必填：1-64 字元，小寫+連字號
description: |            # 必填：1-1024 字元
  詳細描述 skill 做什麼、何時使用。
  應包含具體關鍵字幫助 Agent 識別相關任務。
---

# Skill 標題

## When to use this skill
[明確描述使用場景]

## How to [主要任務]
1. 步驟一...
2. 步驟二...

## Examples
[輸入輸出範例]
```

### 選填欄位

```yaml
---
name: pdf-processing
description: ...
license: Apache-2.0                    # 授權
compatibility: Requires python 3.10+   # 環境需求
metadata:                              # 額外資訊
  author: your-name
  version: "1.0"
allowed-tools: Bash(git:*) Read        # 預先授權的工具（實驗性）
---
```

### 目錄結構

```
skill-name/
├── SKILL.md              # 必要：主要指令
├── scripts/              # 選填：可執行腳本
│   ├── run-tests.py
│   └── validate.sh
├── references/           # 選填：參考文檔
│   ├── REFERENCE.md
│   └── API.md
└── assets/               # 選填：靜態資源
    ├── templates/
    └── examples/
```

---

## 🚀 具體改進行動

### 階段一：立即改進（今天可做）

1. **強化所有 SKILL.md 的 description**
   - 加入更多觸發詞（中英文）
   - 明確描述使用場景
   - 添加「自動觸發條件」

2. **更新 copilot-instructions.md**
   - 添加「當偵測到 X 情境時，讀取 Y skill」的指引
   - 建立 skill 與場景的對應表

### 階段二：短期優化（本週）

3. **測試 skill 載入**
   - 建立測試案例驗證 skill 是否被正確讀取
   - 記錄哪些觸發詞有效

4. **重構 SKILL.md 結構**
   - 符合官方規格
   - 添加 scripts/ 目錄放置可執行腳本

### 階段三：長期遷移（評估後）

5. **評估遷移到 `.github/skills/`**
   - 需要 VS Code Insiders
   - 測試 Progressive Disclosure 機制
   - 確認跨工具相容性

---

## 📋 立即可執行的改進

### 改進範例：`code-reviewer` Skill

**Before（當前）**：
```yaml
description: Comprehensive code review checking quality, security, and best practices. Triggers: CR, review, 審查, 檢查, check, 看一下, PR, code review, 品質.
```

**After（改進後）**：
```yaml
description: |
  Automated code review for quality, security, and best practices.
  
  AUTOMATICALLY LOAD THIS SKILL WHEN:
  - User asks to "review", "check", "audit", or "look at" code
  - User mentions "PR", "pull request", "merge request"
  - User discusses "code quality", "bugs", "security issues"
  - User says "幫我看", "檢查", "審查", "review 一下"
  - Before creating git commits or pull requests
  - When refactoring or improving existing code
  
  CAPABILITIES:
  - Quality: naming, DRY, complexity, function length
  - Security: SQL injection, XSS, sensitive data exposure
  - Performance: N+1 queries, memory leaks, loops
  - Maintainability: comments, error handling, test coverage
```

### 改進範例：`git-precommit` Skill

**After（改進後）**：
```yaml
description: |
  Pre-commit workflow orchestrator for Git operations.
  
  AUTOMATICALLY LOAD THIS SKILL WHEN:
  - User wants to "commit", "push", or "submit" code
  - User says "準備提交", "要 commit 了", "git push"
  - User asks about "pre-commit", "commit message"
  - Before any git commit or push operation
  - When preparing code for review or merge
  
  ORCHESTRATES THESE STEPS:
  1. Memory Bank sync (required)
  2. README update (if needed)
  3. CHANGELOG update (if needed)
  4. ROADMAP update (if needed)
  5. Architecture doc check
  6. Commit message generation
```

---

## ✅ 結論

1. **Skill 沒觸發的主因**：description 不夠明確 + 缺乏自動載入機制
2. **短期解法**：強化 description，添加明確的觸發場景
3. **長期解法**：遷移到官方 `.github/skills/` 格式
4. **測試建議**：實際測試各種觸發詞，記錄效果

---

## 📚 參考資源

- [Agent Skills 官方規格](https://agentskills.io/specification)
- [VS Code Agent Skills 文檔](https://code.visualstudio.com/docs/copilot/customization/agent-skills)
- [Anthropic Skills 範例庫](https://github.com/anthropics/skills)
- [GitHub Awesome Copilot](https://github.com/github/awesome-copilot)
