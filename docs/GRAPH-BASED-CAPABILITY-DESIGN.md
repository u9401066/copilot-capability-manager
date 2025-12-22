# 基於圖論的能力組合系統設計

## 🎯 問題分析

### 核心挑戰

不同 Capability 的複雜度差異巨大：

| Capability | 複雜度 | 特徵 |
|------------|--------|------|
| 文獻檢索 | 高 | 多次迭代搜尋、條件分支、人機互動 |
| 成績單調閱 | 低 | 線性流程、單次執行 |
| 報告撰寫 | 中-高 | 多輸入來源、狀態分支 |
| 專案清理 | 低 | 簡單線性 |

### 傳統方法的問題

```
❌ 固定步驟數：無法適應動態需求
❌ 線性流程：無法表達迴圈和分支
❌ 靜態組合：無法根據上下文調整
```

---

## 🔬 解決方案：圖論建模

### 核心概念：有向加權圖 (Directed Weighted Graph)

```
G = (V, E, W)

V = 節點集合 (Skills + 控制節點)
E = 邊集合 (執行流向)
W = 權重函數 (成本、優先級、條件)
```

### 節點類型 (Node Types)

```yaml
node_types:
  # 1. 技能節點 - 執行實際工作
  skill:
    properties:
      - id: string
      - execution_mode: single | iterative | parallel
      - max_iterations: number (optional)
      - timeout: number (optional)
    
  # 2. 控制節點 - 流程控制
  control:
    subtypes:
      - start: 入口點
      - end: 終止點
      - branch: 條件分支
      - merge: 合併點
      - loop_start: 迴圈開始
      - loop_end: 迴圈結束
      - parallel_split: 並行分叉
      - parallel_join: 並行匯合
    
  # 3. 互動節點 - 需要人機互動
  interaction:
    subtypes:
      - confirm: 確認繼續
      - select: 選擇選項
      - input: 用戶輸入
```

### 邊類型 (Edge Types)

```yaml
edge_types:
  # 1. 順序邊 - 無條件執行
  sequence:
    weight: execution_cost
    
  # 2. 條件邊 - 根據條件決定
  conditional:
    condition: expression
    weight: probability * cost
    
  # 3. 迭代邊 - 迴圈控制
  iteration:
    max_count: number
    exit_condition: expression
    
  # 4. 並行邊 - 同時執行
  parallel:
    sync_required: boolean
```

---

## 📊 圖形表示範例

### 範例 1：簡單能力（成績單調閱）

```
[START] ──► [query-grades] ──► [format-output] ──► [END]

節點數: 4
邊數: 3
複雜度: O(n) 線性
```

### 範例 2：中等能力（Git 提交）

```
                    ┌──► [update-readme] ──┐
[START] ──► [BRANCH] ├──► [update-changelog] ├──► [MERGE] ──► [git-commit] ──► [END]
                    └──► [update-memory] ──┘

節點數: 8
邊數: 8
複雜度: O(n) 但有並行
```

### 範例 3：複雜能力（文獻檢索）

```
[START]
    │
    ▼
[identify-input] ──────────────────────────────────┐
    │                                              │
    ├──► Mode A: PDF ──► [read-pdf] ───────────────┤
    │                                              │
    ├──► Mode B: PMID ──► [fetch-details] ─────────┤
    │                                              │
    └──► Mode C: Search                            │
              │                                    │
              ▼                                    │
         [LOOP_START] ◄────────────────┐           │
              │                        │           │
              ▼                        │           │
         [generate-query]              │           │
              │                        │           │
              ▼                        │           │
         [search-literature]           │           │
              │                        │           │
              ▼                        │           │
         [BRANCH: enough?]             │           │
              │         │              │           │
         YES  │         │ NO           │           │
              │         └──► [expand-query] ──┘    │
              │                                    │
              ▼                                    │
         [LOOP_END]                                │
              │                                    │
              ▼                                    │
         [INTERACT: confirm-selection]             │
              │                                    │
              ▼                                    │
         [filter-results] ◄────────────────────────┘
              │
              ▼
         [write-report]
              │
              ▼
         [END]

節點數: 15+
邊數: 18+
複雜度: O(n*k) 其中 k 是迭代次數
```

---

## 🏗️ 資料結構設計

### Graph Schema (YAML)

```yaml
# .claude/capabilities/write-report/graph.yaml

graph:
  id: write-report
  version: "1.0"
  
  # 節點定義
  nodes:
    - id: start
      type: control.start
      
    - id: identify_input
      type: skill
      skill_id: input-classifier
      execution_mode: single
      
    - id: branch_input_type
      type: control.branch
      conditions:
        - name: pdf_mode
          expression: "input.type == 'pdf'"
          target: read_pdf
        - name: pmid_mode
          expression: "input.type == 'pmid'"
          target: fetch_pmid
        - name: search_mode
          expression: "input.type == 'search'"
          target: loop_search_start
          
    - id: read_pdf
      type: skill
      skill_id: pdf-reader
      execution_mode: single
      
    - id: fetch_pmid
      type: skill
      skill_id: pubmed-fetcher
      execution_mode: single
      
    - id: loop_search_start
      type: control.loop_start
      max_iterations: 5
      
    - id: generate_query
      type: skill
      skill_id: query-generator
      execution_mode: single
      
    - id: search_literature
      type: skill
      skill_id: literature-search
      execution_mode: single
      outputs:
        - result_count
        - results
        
    - id: branch_enough
      type: control.branch
      conditions:
        - name: enough
          expression: "result_count >= 10 OR iteration >= 3"
          target: loop_search_end
        - name: not_enough
          expression: "result_count < 10 AND iteration < 3"
          target: expand_query
          
    - id: expand_query
      type: skill
      skill_id: query-expander
      execution_mode: single
      
    - id: loop_search_end
      type: control.loop_end
      loop_start: loop_search_start
      
    - id: confirm_selection
      type: interaction.select
      prompt: "請選擇要分析的文獻"
      options_from: results
      
    - id: merge_content
      type: control.merge
      
    - id: write_report
      type: skill
      skill_id: report-writer
      execution_mode: single
      
    - id: end
      type: control.end
      
  # 邊定義
  edges:
    - from: start
      to: identify_input
      type: sequence
      
    - from: identify_input
      to: branch_input_type
      type: sequence
      
    - from: read_pdf
      to: merge_content
      type: sequence
      
    - from: fetch_pmid
      to: merge_content
      type: sequence
      
    - from: loop_search_start
      to: generate_query
      type: sequence
      
    - from: generate_query
      to: search_literature
      type: sequence
      
    - from: search_literature
      to: branch_enough
      type: sequence
      
    - from: expand_query
      to: loop_search_start
      type: iteration
      
    - from: loop_search_end
      to: confirm_selection
      type: sequence
      
    - from: confirm_selection
      to: merge_content
      type: sequence
      
    - from: merge_content
      to: write_report
      type: sequence
      
    - from: write_report
      to: end
      type: sequence

  # 圖的元數據
  metadata:
    estimated_complexity: high
    typical_iterations: 2-3
    human_interactions: 1
    parallel_branches: 0
```

---

## 🔢 複雜度標準化

### 複雜度指標計算

```typescript
interface GraphMetrics {
  // 基本指標
  nodeCount: number;
  edgeCount: number;
  
  // 結構指標
  cyclomaticComplexity: number;  // 環路複雜度 = E - N + 2P
  maxDepth: number;              // 最深嵌套
  branchFactor: number;          // 平均分支數
  
  // 執行指標
  maxIterations: number;         // 最大迭代次數
  interactionCount: number;      // 人機互動次數
  parallelBranches: number;      // 並行分支數
  
  // 綜合評分
  complexityScore: number;       // 0-100
  estimatedDuration: number;     // 預估執行時間
}

function calculateComplexity(graph: Graph): GraphMetrics {
  const N = graph.nodes.length;
  const E = graph.edges.length;
  const P = 1; // 連通分量數
  
  // McCabe 環路複雜度
  const cyclomaticComplexity = E - N + 2 * P;
  
  // 計算最大迭代
  const loopNodes = graph.nodes.filter(n => n.type === 'control.loop_start');
  const maxIterations = Math.max(...loopNodes.map(n => n.max_iterations || 1));
  
  // 綜合評分 (加權計算)
  const complexityScore = 
    cyclomaticComplexity * 10 +
    maxIterations * 15 +
    interactionCount * 20 +
    parallelBranches * 5;
    
  return {
    nodeCount: N,
    edgeCount: E,
    cyclomaticComplexity,
    maxIterations,
    complexityScore,
    // ...
  };
}
```

### 複雜度分級

| 等級 | 分數範圍 | 特徵 | 範例 |
|------|----------|------|------|
| **Trivial** | 0-20 | 線性、無迴圈、無互動 | 專案清理 |
| **Simple** | 21-40 | 少量分支、無迴圈 | 成績單調閱 |
| **Moderate** | 41-60 | 有分支和並行 | Git 提交 |
| **Complex** | 61-80 | 有迴圈、多互動 | 報告撰寫 |
| **Very Complex** | 81-100 | 多重迴圈、動態組合 | 文獻檢索 |

---

## 🎮 動態組合演算法

### 問題：如何根據上下文選擇最優路徑？

```typescript
interface ExecutionContext {
  userIntent: string;
  availableTime: number;
  preferredDepth: 'quick' | 'thorough';
  previousResults: any[];
}

// 使用 Dijkstra 變體找最優路徑
function findOptimalPath(
  graph: Graph,
  context: ExecutionContext
): ExecutionPath {
  
  // 根據上下文調整邊的權重
  const adjustedGraph = adjustWeights(graph, context);
  
  // 找到從 START 到 END 的最優路徑
  // 考慮：成本、時間、品質
  const path = dijkstraWithConstraints(
    adjustedGraph,
    'start',
    'end',
    {
      maxCost: context.availableTime,
      qualityThreshold: context.preferredDepth === 'thorough' ? 0.8 : 0.5
    }
  );
  
  return path;
}

// 權重調整函數
function adjustWeights(graph: Graph, context: ExecutionContext): Graph {
  const adjusted = cloneGraph(graph);
  
  for (const edge of adjusted.edges) {
    // 如果用戶趕時間，增加迭代邊的權重（懲罰）
    if (context.preferredDepth === 'quick' && edge.type === 'iteration') {
      edge.weight *= 2;
    }
    
    // 如果用戶要求詳細，降低互動邊的權重（鼓勵）
    if (context.preferredDepth === 'thorough' && 
        edge.to.type === 'interaction') {
      edge.weight *= 0.5;
    }
  }
  
  return adjusted;
}
```

---

## 📐 解決「數量差異」的關鍵設計

### 核心洞察

> **不是用「skill 數量」來衡量能力，而是用「圖的拓撲結構」來定義能力**

### 設計原則

```
┌─────────────────────────────────────────────────────────────┐
│                    統一抽象層                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 節點標準化                                              │
│     - 每個 skill 都是一個標準節點                           │
│     - 控制邏輯用控制節點表達                                │
│     - 複雜度差異 = 圖的結構差異                             │
│                                                             │
│  2. 邊的語義化                                              │
│     - 迭代不是「多個節點」，是「迭代邊」                    │
│     - 分支不是「複製流程」，是「條件邊」                    │
│                                                             │
│  3. 執行模式分離                                            │
│     - 圖定義「可能的路徑」                                  │
│     - 執行時根據上下文「選擇路徑」                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 具體比較

| 能力 | 傳統表示 | 圖論表示 |
|------|----------|----------|
| 成績單調閱 | 2 個 skill | 4 節點, 3 邊, 線性 |
| 文獻檢索 | 10+ 個 skill | 15 節點, 18 邊, 有迴圈 |
| **結構化程度** | ❌ 無法比較 | ✅ 可量化比較 |

### 為什麼這樣可以結構化？

```
圖論的優勢：

1. 拓撲不變性
   - 不管執行幾次迭代，圖的結構是固定的
   - 複雜度在設計時就確定

2. 可組合性
   - 子圖可以嵌入到更大的圖中
   - 能力可以組合成更複雜的能力

3. 可分析性
   - 可以用標準演算法分析（最短路徑、環路檢測等）
   - 可以預估執行成本

4. 可視化
   - 圖天然適合可視化
   - 用戶可以理解複雜流程
```

---

## 🛠️ 實作建議

### Phase 1: 基礎結構

1. 定義節點和邊的 TypeScript 類型
2. 實作 YAML 解析器
3. 建立基本的圖遍歷引擎

### Phase 2: 執行引擎

1. 實作狀態機執行器
2. 處理迴圈和分支
3. 加入人機互動支援

### Phase 3: 智慧組合

1. 實作路徑優化演算法
2. 加入上下文感知
3. 動態調整執行策略

### Phase 4: 視覺化

1. 在 VS Code Extension 中顯示能力圖
2. 支援互動式編輯
3. 即時顯示執行進度

---

## 📚 參考

- **Petri Nets**: 適合建模並行和同步
- **BPMN**: 業務流程建模標準
- **State Machines**: 狀態管理
- **DAG (有向無環圖)**: 依賴管理

---

*設計日期: 2024-12-22*
