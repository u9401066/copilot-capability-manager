# Capability 架構設計：結構化能力文件 + 動態插入

## 🎯 設計目標

1. **AGENTS.md 保持精簡** - 只放核心規則和觸發指引
2. **能力可模組化** - 每個 capability 獨立定義
3. **可重用/組合** - Skill → Composite Skill → Capability 三層架構
4. **動態載入** - 根據用戶意圖自動載入對應能力

---

## 📁 建議的目錄結構

```
.claude/
├── skills/                     # 原子技能 (Atomic Skills)
│   ├── literature-search/
│   │   └── SKILL.md
│   ├── pdf-reader/
│   │   └── SKILL.md
│   └── ...
│
├── capabilities/               # 能力定義 (NEW!)
│   ├── registry.yaml          # 能力註冊表 (觸發條件)
│   ├── write-report/
│   │   ├── CAPABILITY.md      # 能力文件
│   │   └── config.yaml        # 組合設定
│   ├── project-deploy/
│   │   ├── CAPABILITY.md
│   │   └── config.yaml
│   └── ...
│
└── composites/                 # 組合技能 (可選，介於 skill 和 capability 之間)
    ├── literature-retrieval/
    │   └── COMPOSITE.md
    └── ...

AGENTS.md                       # 精簡版，只放觸發規則
```

---

## 🔧 核心設計：Capability Registry

### `registry.yaml` - 能力註冊表

```yaml
# .claude/capabilities/registry.yaml
version: "1.0"

capabilities:
  write-report:
    name: "文獻報告撰寫"
    triggers:
      keywords: ["寫報告", "write report", "文獻回顧", "論文分析"]
      patterns:
        - "幫我.*報告"
        - "分析.*論文"
        - "閱讀.*PDF"
    priority: high
    path: ".claude/capabilities/write-report/CAPABILITY.md"
    
  project-deploy:
    name: "專案部署"
    triggers:
      keywords: ["部署", "deploy", "push", "上線"]
      patterns:
        - "部署.*專案"
        - "推送.*git"
    priority: medium
    path: ".claude/capabilities/project-deploy/CAPABILITY.md"
    
  code-review:
    name: "程式碼審查"
    triggers:
      keywords: ["review", "審查", "檢查程式碼"]
      file_types: [".py", ".ts", ".js"]
      context: "有程式碼修改時"
    priority: low
    path: ".claude/capabilities/code-review/CAPABILITY.md"
```

---

## 📝 CAPABILITY.md 結構

```yaml
# .claude/capabilities/write-report/CAPABILITY.md

---
id: write-report
name: 文獻報告撰寫
version: "1.0"
description: 從 PDF/PMID/搜尋結果產出詳細文獻報告

dependencies:
  skills:
    - pdf-reader
    - literature-search
    - literature-filter
    - note-writer
    - report-formatter
  
  mcp_tools:
    - pubmed-search
    - zotero-keeper

inputs:
  - type: pdf_file
    description: 直接提供 PDF 檔案
  - type: pmid
    description: PubMed ID
  - type: search_query
    description: 搜尋關鍵字

outputs:
  - type: markdown_report
    location: reports/
    
states:
  - identify_input_type
  - gather_content
  - extract_key_points
  - write_report
  - validate_output
---

# 執行流程

## Step 1: 識別輸入類型

根據用戶輸入判斷：
- **Mode A**: PDF 檔案 → 跳至 Step 2a
- **Mode B**: PMID → 跳至 Step 2b  
- **Mode C**: 搜尋需求 → 跳至 Step 2c

## Step 2a: PDF 直接讀取

1. 使用 `pdf-reader` skill 讀取 PDF
2. 參考: `.claude/skills/pdf-reader/SKILL.md`

## Step 2b: PMID 文獻獲取

1. 使用 `mcp_pubmed_search_fetch_article_details` 取得詳情
2. 檢查全文可用性

## Step 2c: 文獻搜尋流程

1. 使用 `literature-search` skill
2. 使用 `literature-filter` skill 過濾
3. 參考: `.claude/skills/literature-retrieval/SKILL.md`

## Step 3: 內容提取與分析

1. 根據用戶需求提取重點
2. 建立結構化筆記

## Step 4: 報告撰寫

1. 使用 `note-writer` skill
2. 使用 `report-formatter` skill 格式化
3. 輸出至 `reports/` 目錄

## Step 5: 驗證與更新

1. 確認報告完整性
2. 更新 Memory Bank
```

---

## 🔄 動態插入機制

### 方案 A: AGENTS.md 觸發指引 (推薦)

在 `AGENTS.md` 中加入精簡的觸發規則：

```markdown
## 🎯 能力自動觸發指引

當偵測到以下情境時，**必須先讀取對應的 CAPABILITY.md**：

| 觸發條件 | 載入能力 | 路徑 |
|----------|----------|------|
| 用戶提到「報告」「PDF」「文獻」 | write-report | `.claude/capabilities/write-report/CAPABILITY.md` |
| 用戶提到「部署」「push」「上線」 | project-deploy | `.claude/capabilities/project-deploy/CAPABILITY.md` |
| 用戶提到「審查」「review」 | code-review | `.claude/capabilities/code-review/CAPABILITY.md` |

> 💡 完整能力清單見 `.claude/capabilities/registry.yaml`
```

### 方案 B: 透過 Skills 機制 (VS Code 原生)

VS Code Copilot 的 `skills` 機制可以用來定義 capabilities：

```json
// .vscode/settings.json 或透過 extension
{
  "github.copilot.chat.skills": [
    {
      "name": "write-report",
      "description": "文獻報告撰寫能力",
      "file": ".claude/capabilities/write-report/CAPABILITY.md"
    }
  ]
}
```

### 方案 C: Prompt File 作為入口 (現有方案增強)

保留 `/cp.xxx` 但讓它們更輕量，只作為「載入器」：

```markdown
<!-- .github/prompts/cp.write_report.prompt.md -->

# Capability: write-report

請立即讀取並遵循以下能力文件：
`.claude/capabilities/write-report/CAPABILITY.md`

然後根據用戶的輸入執行對應流程。
```

---

## 🏗️ 三層架構圖

```
┌─────────────────────────────────────────────────────────────────┐
│                        AGENTS.md                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ • 核心規則 (憲法引用)                                      │  │
│  │ • 觸發指引表 (精簡)                                        │  │
│  │ • 指向 registry.yaml                                       │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Capability Layer                               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ write-report │ │project-deploy│ │ code-review  │ ...        │
│  │              │ │              │ │              │            │
│  │ CAPABILITY.md│ │ CAPABILITY.md│ │ CAPABILITY.md│            │
│  │ config.yaml  │ │ config.yaml  │ │ config.yaml  │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│         │                │                │                     │
│         └────────────────┼────────────────┘                     │
│                          ▼                                      │
│                  registry.yaml                                  │
│              (觸發條件、優先級)                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Skill Layer                                  │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │ pdf-reader │ │lit-search  │ │note-writer │ │report-fmt  │   │
│  │ SKILL.md   │ │ SKILL.md   │ │ SKILL.md   │ │ SKILL.md   │   │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Tool Layer                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ MCP Tools: pubmed-search, zotero-keeper, pylance, ...      │ │
│  │ VS Code: read_file, create_file, run_in_terminal, ...      │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔑 實作建議

### 階段 1: 建立結構
1. 建立 `.claude/capabilities/` 目錄
2. 將現有 prompt files 內容遷移到 `CAPABILITY.md`
3. 建立 `registry.yaml`

### 階段 2: 精簡 AGENTS.md
1. 移除詳細的 capability 說明
2. 只保留觸發指引表
3. 引用 registry.yaml

### 階段 3: 動態載入測試
1. 測試 Copilot 是否能正確識別觸發條件
2. 測試 CAPABILITY.md 的載入和執行
3. 調整觸發條件的關鍵字

### 階段 4 (可選): Extension 整合
1. 在 VS Code Extension 中讀取 registry.yaml
2. 提供 UI 讓用戶選擇 capability
3. 自動注入 capability context

---

## ⚖️ 方案比較

| 特性 | 現有 Prompt Files | 動態 CAPABILITY.md |
|------|-------------------|---------------------|
| 觸發方式 | 手動 `/cp.xxx` | 自動識別 + 手動 |
| AGENTS.md 大小 | 中等 | 精簡 |
| 模組化程度 | 中 | 高 |
| 重用性 | 低（複製貼上） | 高（引用組合） |
| 維護成本 | 高（分散）| 低（集中） |
| 學習曲線 | 低 | 中 |

---

## 📌 結論

Gemini 的建議是**完全可行的**！建議採用：

1. **`registry.yaml`** 作為能力註冊表
2. **`CAPABILITY.md`** 作為每個能力的完整定義
3. **精簡的 `AGENTS.md`** 只放觸發規則
4. **保留 `/cp.xxx`** 作為明確觸發的方式

這樣既能保持 AGENTS.md 精簡，又能實現能力的模組化和動態載入！
