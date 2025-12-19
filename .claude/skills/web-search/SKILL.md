---
name: web-search
description: |
  Web research and literature search capabilities for external resources.
  LOAD THIS SKILL WHEN: User says "搜尋", "search", "找資料", "查詢", "檢索", "web search", "網路搜尋" | needs external documentation | research task | API reference lookup | technology comparison | wants latest information.
  CAPABILITIES: Technical docs (MDN, GitHub, Stack Overflow), academic papers (PubMed integration), API documentation, real-time web data via fetch_webpage, structured search results.
skill_id: web-search
category: research
priority: 10
---

# 網路檢索技能

## 描述
透過網路搜尋相關資源、文獻、技術文檔等資料。

## 觸發條件
- 「搜尋 XXX」
- 「找一下 XXX 的資料」
- 「查找相關文獻」
- 需要外部資料時

## 能力範圍

### 可搜尋資源
- 技術文檔 (MDN, Stack Overflow, GitHub)
- 學術文獻 (PubMed, Google Scholar)
- API 參考文檔
- 最新技術資訊

### 輸出格式
```
🔍 搜尋結果：[關鍵字]

📚 找到 N 筆相關資料：

1. [標題]
   來源：[URL]
   摘要：[簡短摘要]
   相關度：⭐⭐⭐⭐⭐

2. [標題]
   ...
```

## 使用範例
```
「搜尋 Python async 最佳實踐」
「找一下 React 18 新功能」
「查找 Docker Compose 設定範例」
```

## 配合工具
- `fetch_webpage` - 抓取網頁內容
- `mcp_pubmed_search_*` - PubMed 文獻搜尋

```
