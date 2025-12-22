# Capability: write-report

---
id: write-report
name: 文獻報告撰寫
version: "1.0"
description: 從 PDF/PMID/搜尋結果產出詳細文獻報告

author: Copilot Capability Manager
created: 2024-12-22
updated: 2024-12-22

dependencies:
  skills:
    required:
      - pdf-reader
      - note-writer
      - report-formatter
    optional:
      - literature-search
      - literature-filter
      - content-validator
  
  mcp_tools:
    - mcp_pubmed_search_*
    - mcp_zotero_keeper_*
    - mcp_pylance_*

inputs:
  - name: pdf_file
    type: file
    extensions: [".pdf"]
    description: 直接提供 PDF 檔案
    
  - name: pmid
    type: string
    pattern: "^\\d+$"
    description: PubMed ID
    
  - name: search_query
    type: string
    description: 搜尋關鍵字或 PICO 問題

outputs:
  - name: report
    type: markdown
    location: reports/
    naming: "{topic}-report-{date}.md"

states:
  - id: identify_input
    name: 識別輸入類型
    next: [read_pdf, fetch_pmid, search_literature]
    
  - id: read_pdf
    name: 讀取 PDF
    skill: pdf-reader
    next: [extract_content]
    
  - id: fetch_pmid
    name: 獲取 PMID 詳情
    tool: mcp_pubmed_search_fetch_article_details
    next: [extract_content]
    
  - id: search_literature
    name: 文獻搜尋
    skill: literature-search
    next: [filter_results]
    
  - id: filter_results
    name: 過濾結果
    skill: literature-filter
    next: [extract_content]
    
  - id: extract_content
    name: 提取內容
    next: [write_report]
    
  - id: write_report
    name: 撰寫報告
    skill: note-writer
    next: [format_report]
    
  - id: format_report
    name: 格式化報告
    skill: report-formatter
    next: [validate, update_memory]
    
  - id: validate
    name: 驗證報告
    skill: content-validator
    optional: true
    next: [update_memory]
    
  - id: update_memory
    name: 更新 Memory Bank
    skill: memory-updater
    next: [complete]
    
  - id: complete
    name: 完成
    terminal: true
---

# 📝 文獻報告撰寫能力

## 概述

此能力用於從各種輸入來源（PDF、PMID、搜尋查詢）產出詳細的文獻報告。

## 執行流程

```
┌─────────────────────────────────────────────────────────────┐
│                    輸入識別                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   用戶輸入                                                  │
│       │                                                     │
│       ├──► PDF 檔案? ──► Mode A: 直接讀取                  │
│       │                                                     │
│       ├──► PMID?     ──► Mode B: 獲取詳情                  │
│       │                                                     │
│       └──► 搜尋需求? ──► Mode C: 文獻檢索                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Mode A: PDF 直接讀取

### Step 1: 讀取 PDF

**使用 Skill**: `pdf-reader`

```
讀取 .claude/skills/pdf-reader/SKILL.md 並執行
```

**工具**: PyMuPDF 或 `convert_to_markdown` MCP tool

### Step 2: 內容提取

根據用戶需求：
- 全文提取
- 特定段落（如 "Results 之後"）
- 表格和圖表說明

### Step 3: 撰寫報告

**使用 Skill**: `note-writer`

報告結構：
1. 文獻基本資訊
2. 研究方法摘要
3. 主要結果詳解
4. 討論與臨床意義
5. 研究限制
6. 結論

---

## Mode B: PMID 獲取

### Step 1: 獲取文章詳情

```python
mcp_pubmed_search_fetch_article_details(pmids="12345678")
```

### Step 2: 檢查全文可用性

```python
mcp_pubmed_search_get_article_fulltext_links(pmid="12345678")
```

### Step 3: 如有 PMC 全文，可進一步分析

### Step 4: 撰寫報告（同 Mode A Step 3）

---

## Mode C: 文獻檢索

### Step 1: 文獻搜尋

**使用 Skill**: `literature-search`

```
讀取 .claude/skills/literature-search/SKILL.md 並執行
```

搜尋策略選擇：
- 快速搜尋：`search_literature(query, limit=10)`
- PICO 搜尋：`parse_pico()` → `generate_search_queries()` → `search_literature()`

### Step 2: 過濾結果

**使用 Skill**: `literature-filter`

與用戶確認要分析的文獻

### Step 3: 批量獲取詳情

```python
mcp_pubmed_search_fetch_article_details(pmids="comma,separated,pmids")
```

### Step 4: 撰寫報告

---

## 報告格式要求

### 基本結構

```markdown
# {標題}

## 📚 文獻基本資訊
| 項目 | 內容 |
|------|------|
| 期刊 | ... |
| 年份 | ... |

## 🎯 研究結果詳細解析
### 1. 主要發現
### 2. 次要發現

## 🔍 討論重點

## 📋 研究限制

## 🔑 結論

## 📚 參考文獻
```

### 增強元素

- 使用 emoji 增加可讀性
- 提供表格整理數據
- 使用 ASCII 流程圖
- 加入 "💡 解讀" 和 "⚠️ 注意" 提示框
- 提供臨床實務建議

---

## Checkpoint 管理

執行此能力時，必須建立 checkpoint：

```json
{
  "capability": "write-report",
  "status": "in-progress",
  "input_type": "pdf|pmid|search",
  "input_value": "...",
  "progress": {
    "total": 5,
    "completed": 0
  },
  "currentState": "identify_input",
  "completedStates": [],
  "output_path": null,
  "errors": []
}
```

---

## 錯誤處理

| 錯誤情境 | 處理方式 |
|----------|----------|
| PDF 無法讀取 | 嘗試其他讀取方式，或請用戶提供文字版本 |
| PMID 不存在 | 提示用戶確認 PMID |
| 搜尋無結果 | 建議擴展搜尋策略 |
| 全文不可用 | 僅根據摘要撰寫，並註明限制 |

---

## 相關 Skills

- [pdf-reader](../../skills/pdf-reader/SKILL.md)
- [literature-search](../../skills/literature-search/SKILL.md)
- [literature-filter](../../skills/literature-filter/SKILL.md)
- [note-writer](../../skills/note-writer/SKILL.md)
- [report-formatter](../../skills/report-formatter/SKILL.md)
- [content-validator](../../skills/content-validator/SKILL.md)
