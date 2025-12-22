# 不確定節點設計：動態圖與 Fallback 機制

## 🎯 問題陳述

傳統圖的假設：
- ❌ 節點是確定的（知道要調用什麼）
- ❌ 邊是靜態的（知道流向哪裡）
- ❌ 圖形在執行前就完全定義

實際情況：
- ✅ 節點可能是動態的（PDF/DOCX/線上文檔）
- ✅ 可能需要 Fallback（讀取失敗怎麼辦）
- ✅ 圖形可能在執行中「生長」

---

## 🔬 解決方案：三層節點模型

### 核心概念：抽象節點 + 具體實現 + Fallback 鏈

```
┌─────────────────────────────────────────────────────────────────┐
│                     Abstract Node (抽象節點)                     │
│                                                                 │
│  定義「做什麼」而不是「怎麼做」                                   │
│  例如：read_document（讀取文檔）                                 │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Concrete 1   │  │ Concrete 2   │  │ Concrete 3   │          │
│  │ pdf-reader   │  │ docx-reader  │  │ web-reader   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                 │                 │                   │
│         └────────┬────────┴────────┬────────┘                   │
│                  │                 │                            │
│                  ▼                 ▼                            │
│         ┌──────────────┐  ┌──────────────┐                      │
│         │ Fallback 1   │  │ Fallback 2   │                      │
│         │ ask-user     │  │ skip-step    │                      │
│         └──────────────┘  └──────────────┘                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📐 節點類型擴展

### 1. 抽象節點 (Abstract Node)

定義能力的「契約」，不指定具體實現：

```yaml
- id: read_document
  type: abstract
  contract:
    input:
      - name: source
        type: string | file | url
    output:
      - name: content
        type: string
      - name: metadata
        type: object
    capabilities:
      - read_text
      - extract_structure
  
  # 解析策略：如何選擇具體實現
  resolution:
    strategy: auto_detect | user_select | priority_chain
    
    # 自動檢測規則
    auto_detect:
      - condition: "source.endsWith('.pdf')"
        implementation: pdf-reader
      - condition: "source.endsWith('.docx')"
        implementation: docx-reader
      - condition: "source.startsWith('http')"
        implementation: web-reader
      - condition: "default"
        implementation: text-reader
```

### 2. 多態節點 (Polymorphic Node)

一個節點可以有多種實現：

```yaml
- id: document_reader
  type: polymorphic
  
  implementations:
    - id: pdf-reader
      priority: 1
      conditions:
        - "input.type == 'application/pdf'"
        - "input.path.endsWith('.pdf')"
      skill: pdf-reader
      
    - id: docx-reader
      priority: 2
      conditions:
        - "input.type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'"
        - "input.path.endsWith('.docx')"
      skill: docx-reader
      
    - id: web-reader
      priority: 3
      conditions:
        - "input.path.startsWith('http')"
        - "input.type == 'text/html'"
      skill: web-reader
      
    - id: generic-text
      priority: 99  # 最低優先級，作為 fallback
      conditions:
        - "default"
      skill: text-reader
```

### 3. Fallback 鏈節點 (Fallback Chain Node)

定義失敗時的處理策略：

```yaml
- id: read_with_fallback
  type: fallback_chain
  
  primary: pdf-reader
  
  fallbacks:
    - trigger: "error.type == 'FileNotFound'"
      action: web-reader
      
    - trigger: "error.type == 'ParseError'"
      action: ocr-reader  # 嘗試 OCR
      
    - trigger: "error.type == 'PermissionDenied'"
      action: ask_user_permission
      
    - trigger: "retries >= 3"
      action: skip_with_warning
      
    - trigger: "default"
      action: manual_input  # 最終 fallback：請用戶手動輸入
  
  # Fallback 配置
  config:
    max_retries: 3
    retry_delay: 1000  # ms
    timeout: 30000     # ms
```

---

## 🎮 動態圖擴展

### 概念：Lazy Expansion（延遲展開）

圖不是一開始就完全定義，而是在執行時「生長」：

```
┌─────────────────────────────────────────────────────────────────┐
│                     初始圖 (骨架)                                │
│                                                                 │
│  [START] ──► [abstract: process_input] ──► [write] ──► [END]   │
│                        │                                        │
│                        │ (執行時展開)                            │
│                        ▼                                        │
│              ┌─────────────────────┐                            │
│              │ Runtime Expansion   │                            │
│              │                     │                            │
│              │ 檢測到 PDF 檔案     │                            │
│              │         ↓           │                            │
│              │ [pdf-reader]        │                            │
│              │     ↓ (失敗)        │                            │
│              │ [ocr-reader]        │                            │
│              │     ↓ (成功)        │                            │
│              │ 繼續執行            │                            │
│              └─────────────────────┘                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 實現：Expansion Rules（展開規則）

```yaml
expansion_rules:
  # 規則 1：根據輸入類型展開
  - trigger: "node.type == 'abstract' && node.contract.input.source"
    expand_to:
      - detect_input_type
      - select_implementation
      - execute_with_fallback
      
  # 規則 2：根據上下文展開
  - trigger: "context.user_preference == 'thorough'"
    expand_to:
      - add_validation_step
      - add_confirmation_step
      
  # 規則 3：根據錯誤展開
  - trigger: "last_step.status == 'failed'"
    expand_to:
      - analyze_error
      - select_fallback
      - retry_or_skip
```

---

## 🔄 自適應圖模型

### 核心：圖 + 狀態機 + 規則引擎

```typescript
interface AdaptiveGraph {
  // 靜態部分：圖的骨架
  skeleton: {
    nodes: AbstractNode[];
    edges: AbstractEdge[];
  };
  
  // 動態部分：運行時擴展
  runtime: {
    expandedNodes: Map<string, ConcreteNode[]>;
    executionPath: string[];
    currentState: ExecutionState;
  };
  
  // 規則引擎：決定如何擴展
  rules: {
    expansionRules: ExpansionRule[];
    fallbackRules: FallbackRule[];
    adaptationRules: AdaptationRule[];
  };
}
```

### 執行流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    自適應執行流程                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 載入骨架圖                                                  │
│         ↓                                                       │
│  2. 遇到抽象節點                                                │
│         ↓                                                       │
│  3. 查詢規則引擎 ──────────────────────┐                        │
│         │                              │                        │
│         ▼                              ▼                        │
│  4a. 自動解析              4b. 請求用戶輸入                     │
│      (條件匹配)                 (無法判斷)                      │
│         │                              │                        │
│         └──────────┬───────────────────┘                        │
│                    ↓                                            │
│  5. 展開為具體節點                                              │
│         ↓                                                       │
│  6. 執行具體節點                                                │
│         │                                                       │
│    ┌────┴────┐                                                  │
│    ↓         ↓                                                  │
│ 成功      失敗                                                  │
│    │         │                                                  │
│    │         ▼                                                  │
│    │    7. 查詢 Fallback 規則                                   │
│    │         │                                                  │
│    │    ┌────┴────┐                                             │
│    │    ↓         ↓                                             │
│    │  有 FB    無 FB                                            │
│    │    │         │                                             │
│    │    ▼         ▼                                             │
│    │  展開 FB   標記失敗                                        │
│    │    │         │                                             │
│    └────┴────┬────┘                                             │
│              ↓                                                  │
│  8. 繼續執行下一節點                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 不確定性的量化

### 節點不確定性指標

```typescript
interface NodeUncertainty {
  // 實現不確定性：有多少種可能的實現
  implementationVariance: number;  // 0 = 確定, 1+ = 不確定
  
  // 成功不確定性：執行成功的概率
  successProbability: number;  // 0-1
  
  // 路徑不確定性：可能的後續路徑數
  pathVariance: number;
  
  // 時間不確定性：執行時間的變異係數
  durationVariance: number;
}

// 計算整個圖的不確定性
function calculateGraphUncertainty(graph: AdaptiveGraph): number {
  const nodeUncertainties = graph.skeleton.nodes.map(n => 
    calculateNodeUncertainty(n)
  );
  
  // 使用蒙特卡羅模擬估計整體不確定性
  return monteCarloSimulation(graph, 1000);
}
```

### 不確定性等級

| 等級 | 描述 | 處理策略 |
|------|------|----------|
| **Deterministic** | 完全確定 | 直接執行 |
| **Low Uncertainty** | 少量變化 | 自動選擇 + 日誌 |
| **Medium Uncertainty** | 多種可能 | 自動嘗試 + Fallback |
| **High Uncertainty** | 高度不確定 | 請求用戶確認 |
| **Unknown** | 無法預測 | 互動式探索 |

---

## 🛠️ 實現範例：文檔讀取能力

### graph.yaml

```yaml
graph:
  id: adaptive-document-reader
  version: "1.0"
  type: adaptive  # 標記為自適應圖
  
  nodes:
    - id: start
      type: control.start
      
    - id: detect_source
      type: skill
      skill_id: source-detector
      outputs: [source_type, source_path]
      
    - id: read_document
      type: abstract  # 抽象節點！
      contract:
        input: [source_path, source_type]
        output: [content, metadata]
      resolution:
        strategy: auto_detect
        implementations:
          - condition: "source_type == 'pdf'"
            skill: pdf-reader
            fallback: [ocr-reader, ask-user]
          - condition: "source_type == 'docx'"
            skill: docx-reader
            fallback: [text-extractor, ask-user]
          - condition: "source_type == 'url'"
            skill: web-reader
            fallback: [wget-reader, ask-user]
          - condition: "source_type == 'google_doc'"
            skill: gdoc-reader
            fallback: [export-pdf, ask-user]
          - condition: "default"
            skill: generic-reader
            fallback: [ask-user]
      
    - id: validate_content
      type: skill
      skill_id: content-validator
      optional: true  # 可選步驟
      
    - id: end
      type: control.end
      
  edges:
    - from: start
      to: detect_source
      type: sequence
      
    - from: detect_source
      to: read_document
      type: sequence
      
    - from: read_document
      to: validate_content
      type: sequence
      
    - from: validate_content
      to: end
      type: sequence
      
  # 全局 Fallback 策略
  fallback_strategy:
    max_retries: 3
    retry_delay: 1000
    on_all_failed:
      - log_error
      - notify_user
      - skip_or_abort  # 由用戶決定
```

---

## 💡 關鍵洞察

### 「不確定」不是問題，是特性

```
傳統思維：
  「圖必須在執行前完全定義」 ❌

新思維：
  「圖是執行的藍圖，具體路徑在執行時確定」 ✅
```

### 設計原則

1. **契約優先**
   - 定義「做什麼」而不是「怎麼做」
   - 抽象節點描述輸入/輸出契約

2. **延遲綁定**
   - 具體實現在執行時決定
   - 根據上下文選擇最佳實現

3. **優雅降級**
   - 每個節點都有 Fallback 鏈
   - 失敗是預期的一部分

4. **可觀察性**
   - 記錄所有擴展和 Fallback
   - 便於調試和優化

---

## 🔮 進階：自學習圖

### 概念：執行歷史 → 優化圖

```typescript
interface LearningGraph extends AdaptiveGraph {
  // 執行歷史
  history: ExecutionHistory[];
  
  // 學習到的優化
  optimizations: {
    // 某個抽象節點的最佳實現統計
    bestImplementations: Map<string, ImplementationStats>;
    
    // 成功的 Fallback 鏈
    successfulFallbacks: FallbackChain[];
    
    // 常見錯誤和解決方案
    errorSolutions: Map<ErrorPattern, Solution>;
  };
}

// 根據歷史優化圖
function optimizeGraph(graph: LearningGraph): void {
  // 1. 調整實現優先級
  for (const [nodeId, stats] of graph.optimizations.bestImplementations) {
    reorderImplementations(graph, nodeId, stats);
  }
  
  // 2. 添加常見的 Fallback 路徑
  for (const chain of graph.optimizations.successfulFallbacks) {
    addFallbackIfMissing(graph, chain);
  }
  
  // 3. 預先處理常見錯誤
  for (const [pattern, solution] of graph.optimizations.errorSolutions) {
    addPreemptiveHandling(graph, pattern, solution);
  }
}
```

---

## 📚 總結

| 問題 | 解決方案 |
|------|----------|
| 節點不確定 | 抽象節點 + 多態實現 |
| 執行失敗 | Fallback 鏈 |
| 圖形不確定 | 延遲展開 + 規則引擎 |
| 自由度高 | 契約約束 + 可觀察性 |

**核心思想**：圖定義的是「可能的路徑空間」，而不是「確定的執行路徑」。

---

*設計日期: 2024-12-22*
