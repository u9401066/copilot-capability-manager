/**
 * Graph-based Capability Execution Engine
 * 基於圖論的能力執行引擎
 */

// ═══════════════════════════════════════════════════════════════════
// 類型定義
// ═══════════════════════════════════════════════════════════════════

/** 節點類型 */
export type NodeType = 
  | 'skill'
  | 'control.start'
  | 'control.end'
  | 'control.branch'
  | 'control.merge'
  | 'control.loop_start'
  | 'control.loop_end'
  | 'control.parallel_split'
  | 'control.parallel_join'
  | 'interaction.confirm'
  | 'interaction.select'
  | 'interaction.input';

/** 執行模式 */
export type ExecutionMode = 'single' | 'iterative' | 'parallel';

/** 邊類型 */
export type EdgeType = 'sequence' | 'conditional' | 'iteration' | 'parallel';

/** 圖節點 */
export interface GraphNode {
  id: string;
  type: NodeType;
  skillId?: string;           // 對應的 skill ID（skill 類型專用）
  executionMode?: ExecutionMode;
  maxIterations?: number;
  timeout?: number;
  conditions?: BranchCondition[];  // branch 節點專用
  prompt?: string;            // interaction 節點專用
  optionsFrom?: string;       // select 節點專用
  outputs?: string[];         // 輸出變數名稱
}

/** 分支條件 */
export interface BranchCondition {
  name: string;
  expression: string;
  target: string;
}

/** 圖的邊 */
export interface GraphEdge {
  from: string;
  to: string;
  type: EdgeType;
  weight?: number;
  condition?: string;
  maxCount?: number;          // iteration 邊專用
  exitCondition?: string;     // iteration 邊專用
}

/** 能力圖 */
export interface CapabilityGraph {
  id: string;
  version: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata?: GraphMetadata;
}

/** 圖的元數據 */
export interface GraphMetadata {
  estimatedComplexity: 'trivial' | 'simple' | 'moderate' | 'complex' | 'very_complex';
  typicalIterations?: number;
  humanInteractions?: number;
  parallelBranches?: number;
}

// ═══════════════════════════════════════════════════════════════════
// 複雜度指標
// ═══════════════════════════════════════════════════════════════════

/** 圖的複雜度指標 */
export interface GraphMetrics {
  nodeCount: number;
  edgeCount: number;
  cyclomaticComplexity: number;
  maxDepth: number;
  branchFactor: number;
  maxIterations: number;
  interactionCount: number;
  parallelBranches: number;
  complexityScore: number;
  complexityLevel: 'trivial' | 'simple' | 'moderate' | 'complex' | 'very_complex';
}

/** 計算圖的複雜度指標 */
export function calculateGraphMetrics(graph: CapabilityGraph): GraphMetrics {
  const N = graph.nodes.length;
  const E = graph.edges.length;
  const P = 1; // 假設單一連通分量
  
  // McCabe 環路複雜度
  const cyclomaticComplexity = E - N + 2 * P;
  
  // 計算最大迭代次數
  const loopNodes = graph.nodes.filter(n => n.type === 'control.loop_start');
  const maxIterations = loopNodes.length > 0 
    ? Math.max(...loopNodes.map(n => n.maxIterations || 1))
    : 0;
  
  // 計算互動次數
  const interactionCount = graph.nodes.filter(n => 
    n.type.startsWith('interaction.')
  ).length;
  
  // 計算並行分支數
  const parallelBranches = graph.nodes.filter(n => 
    n.type === 'control.parallel_split'
  ).length;
  
  // 計算分支因子
  const branchNodes = graph.nodes.filter(n => n.type === 'control.branch');
  const branchFactor = branchNodes.length > 0
    ? branchNodes.reduce((sum, n) => sum + (n.conditions?.length || 0), 0) / branchNodes.length
    : 0;
  
  // 計算最大深度 (BFS)
  const maxDepth = calculateMaxDepth(graph);
  
  // 綜合複雜度評分
  const complexityScore = 
    cyclomaticComplexity * 10 +
    maxIterations * 15 +
    interactionCount * 20 +
    parallelBranches * 5 +
    maxDepth * 3;
  
  // 複雜度等級
  const complexityLevel = getComplexityLevel(complexityScore);
  
  return {
    nodeCount: N,
    edgeCount: E,
    cyclomaticComplexity,
    maxDepth,
    branchFactor,
    maxIterations,
    interactionCount,
    parallelBranches,
    complexityScore,
    complexityLevel
  };
}

function calculateMaxDepth(graph: CapabilityGraph): number {
  const startNode = graph.nodes.find(n => n.type === 'control.start');
  if (!startNode) return 0;
  
  const adjacency = buildAdjacencyList(graph);
  const visited = new Set<string>();
  let maxDepth = 0;
  
  function dfs(nodeId: string, depth: number) {
    if (visited.has(nodeId)) return;
    visited.add(nodeId);
    maxDepth = Math.max(maxDepth, depth);
    
    const neighbors = adjacency.get(nodeId) || [];
    for (const neighbor of neighbors) {
      dfs(neighbor, depth + 1);
    }
    visited.delete(nodeId); // 允許多條路徑
  }
  
  dfs(startNode.id, 0);
  return maxDepth;
}

function buildAdjacencyList(graph: CapabilityGraph): Map<string, string[]> {
  const adjacency = new Map<string, string[]>();
  
  for (const node of graph.nodes) {
    adjacency.set(node.id, []);
  }
  
  for (const edge of graph.edges) {
    const neighbors = adjacency.get(edge.from) || [];
    neighbors.push(edge.to);
    adjacency.set(edge.from, neighbors);
  }
  
  return adjacency;
}

function getComplexityLevel(score: number): GraphMetrics['complexityLevel'] {
  if (score <= 20) return 'trivial';
  if (score <= 40) return 'simple';
  if (score <= 60) return 'moderate';
  if (score <= 80) return 'complex';
  return 'very_complex';
}

// ═══════════════════════════════════════════════════════════════════
// 執行引擎
// ═══════════════════════════════════════════════════════════════════

/** 執行上下文 */
export interface ExecutionContext {
  userIntent: string;
  availableTime?: number;
  preferredDepth: 'quick' | 'balanced' | 'thorough';
  variables: Map<string, any>;
  history: ExecutionStep[];
}

/** 執行步驟記錄 */
export interface ExecutionStep {
  nodeId: string;
  timestamp: Date;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  result?: any;
  error?: string;
  duration?: number;
}

/** 執行結果 */
export interface ExecutionResult {
  success: boolean;
  path: string[];
  steps: ExecutionStep[];
  outputs: Map<string, any>;
  metrics: {
    totalDuration: number;
    nodesExecuted: number;
    iterationsPerformed: number;
  };
}

/** 圖執行引擎 */
export class GraphExecutionEngine {
  private graph: CapabilityGraph;
  private context: ExecutionContext;
  private adjacency: Map<string, string[]>;
  private nodeMap: Map<string, GraphNode>;
  
  constructor(graph: CapabilityGraph) {
    this.graph = graph;
    this.adjacency = buildAdjacencyList(graph);
    this.nodeMap = new Map(graph.nodes.map(n => [n.id, n]));
    this.context = {
      userIntent: '',
      preferredDepth: 'balanced',
      variables: new Map(),
      history: []
    };
  }
  
  /** 設定執行上下文 */
  setContext(context: Partial<ExecutionContext>): void {
    this.context = { ...this.context, ...context };
  }
  
  /** 執行能力圖 */
  async execute(): Promise<ExecutionResult> {
    const startNode = this.graph.nodes.find(n => n.type === 'control.start');
    if (!startNode) {
      throw new Error('Graph must have a start node');
    }
    
    const result: ExecutionResult = {
      success: false,
      path: [],
      steps: [],
      outputs: new Map(),
      metrics: {
        totalDuration: 0,
        nodesExecuted: 0,
        iterationsPerformed: 0
      }
    };
    
    const startTime = Date.now();
    
    try {
      await this.executeNode(startNode.id, result);
      result.success = true;
    } catch (error) {
      result.success = false;
      console.error('Execution failed:', error);
    }
    
    result.metrics.totalDuration = Date.now() - startTime;
    result.outputs = this.context.variables;
    
    return result;
  }
  
  /** 執行單一節點 */
  private async executeNode(nodeId: string, result: ExecutionResult): Promise<void> {
    const node = this.nodeMap.get(nodeId);
    if (!node) {
      throw new Error(`Node not found: ${nodeId}`);
    }
    
    result.path.push(nodeId);
    
    const step: ExecutionStep = {
      nodeId,
      timestamp: new Date(),
      status: 'running'
    };
    result.steps.push(step);
    
    const stepStartTime = Date.now();
    
    try {
      switch (node.type) {
        case 'control.start':
          // 開始節點，直接進入下一個
          break;
          
        case 'control.end':
          // 結束節點，終止執行
          step.status = 'completed';
          return;
          
        case 'control.branch':
          await this.handleBranch(node, result);
          return; // handleBranch 會處理後續
          
        case 'control.merge':
          // 合併節點，直接進入下一個
          break;
          
        case 'control.loop_start':
          await this.handleLoopStart(node, result);
          return; // handleLoopStart 會處理迴圈
          
        case 'control.loop_end':
          // 迴圈結束節點，由 handleLoopStart 處理
          break;
          
        case 'skill':
          await this.executeSkill(node, result);
          break;
          
        case 'interaction.confirm':
        case 'interaction.select':
        case 'interaction.input':
          await this.handleInteraction(node, result);
          break;
          
        default:
          console.warn(`Unknown node type: ${node.type}`);
      }
      
      step.status = 'completed';
      step.duration = Date.now() - stepStartTime;
      result.metrics.nodesExecuted++;
      
      // 進入下一個節點
      const nextNodes = this.adjacency.get(nodeId) || [];
      if (nextNodes.length === 1) {
        await this.executeNode(nextNodes[0], result);
      } else if (nextNodes.length > 1) {
        // 多個後繼節點，應該是分支，但這裡不應該發生
        console.warn(`Multiple successors without branch: ${nodeId}`);
        await this.executeNode(nextNodes[0], result);
      }
      
    } catch (error) {
      step.status = 'failed';
      step.error = error instanceof Error ? error.message : String(error);
      step.duration = Date.now() - stepStartTime;
      throw error;
    }
  }
  
  /** 處理分支節點 */
  private async handleBranch(node: GraphNode, result: ExecutionResult): Promise<void> {
    if (!node.conditions || node.conditions.length === 0) {
      throw new Error(`Branch node ${node.id} has no conditions`);
    }
    
    // 評估條件，找到第一個為真的
    for (const condition of node.conditions) {
      const isTrue = this.evaluateCondition(condition.expression);
      if (isTrue) {
        await this.executeNode(condition.target, result);
        return;
      }
    }
    
    // 如果沒有條件為真，使用第一個作為默認
    await this.executeNode(node.conditions[0].target, result);
  }
  
  /** 處理迴圈開始節點 */
  private async handleLoopStart(node: GraphNode, result: ExecutionResult): Promise<void> {
    const maxIterations = node.maxIterations || 10;
    let iteration = 0;
    
    // 找到對應的 loop_end 節點
    const loopEndNode = this.graph.nodes.find(n => 
      n.type === 'control.loop_end' && 
      this.findLoopEnd(node.id) === n.id
    );
    
    while (iteration < maxIterations) {
      this.context.variables.set('iteration', iteration);
      result.metrics.iterationsPerformed++;
      
      // 執行迴圈體
      const nextNodes = this.adjacency.get(node.id) || [];
      if (nextNodes.length > 0) {
        await this.executeNode(nextNodes[0], result);
      }
      
      // 檢查是否應該退出迴圈
      // 這需要檢查最後執行的節點是否到達了 loop_end
      const lastStep = result.steps[result.steps.length - 1];
      if (loopEndNode && lastStep.nodeId === loopEndNode.id) {
        break;
      }
      
      iteration++;
    }
    
    // 迴圈結束後，繼續執行 loop_end 之後的節點
    if (loopEndNode) {
      const nextAfterLoop = this.adjacency.get(loopEndNode.id) || [];
      if (nextAfterLoop.length > 0) {
        await this.executeNode(nextAfterLoop[0], result);
      }
    }
  }
  
  /** 找到迴圈結束節點 */
  private findLoopEnd(loopStartId: string): string | undefined {
    // 簡單實作：假設 loop_end 節點的 ID 包含對應的 loop_start
    for (const node of this.graph.nodes) {
      if (node.type === 'control.loop_end') {
        // 檢查是否有迭代邊指向 loopStartId
        const hasIterationEdge = this.graph.edges.some(e => 
          e.from === node.id && 
          e.to === loopStartId && 
          e.type === 'iteration'
        );
        if (hasIterationEdge) {
          return node.id;
        }
      }
    }
    return undefined;
  }
  
  /** 執行 Skill 節點 */
  private async executeSkill(node: GraphNode, result: ExecutionResult): Promise<void> {
    if (!node.skillId) {
      throw new Error(`Skill node ${node.id} has no skillId`);
    }
    
    console.log(`Executing skill: ${node.skillId}`);
    
    // TODO: 實際執行 skill
    // 這裡應該調用 SkillService 來執行對應的 skill
    
    // 模擬執行
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // 設定輸出變數
    if (node.outputs) {
      for (const output of node.outputs) {
        this.context.variables.set(output, `result_of_${node.skillId}`);
      }
    }
  }
  
  /** 處理互動節點 */
  private async handleInteraction(node: GraphNode, result: ExecutionResult): Promise<void> {
    console.log(`Interaction required: ${node.type} - ${node.prompt || node.id}`);
    
    // TODO: 實際與用戶互動
    // 這裡應該透過 VS Code API 顯示對話框或選擇器
    
    // 模擬用戶確認
    this.context.variables.set(`${node.id}_result`, 'user_confirmed');
  }
  
  /** 評估條件表達式 */
  private evaluateCondition(expression: string): boolean {
    // 簡單實作：使用變數替換後 eval
    // 實際應該使用更安全的表達式解析器
    try {
      let evalExpression = expression;
      for (const [key, value] of this.context.variables) {
        evalExpression = evalExpression.replace(
          new RegExp(`\\b${key}\\b`, 'g'),
          JSON.stringify(value)
        );
      }
      // eslint-disable-next-line no-eval
      return eval(evalExpression);
    } catch {
      console.warn(`Failed to evaluate condition: ${expression}`);
      return false;
    }
  }
}

// ═══════════════════════════════════════════════════════════════════
// 圖的工具函數
// ═══════════════════════════════════════════════════════════════════

/** 驗證圖的結構 */
export function validateGraph(graph: CapabilityGraph): { valid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  // 檢查是否有 start 節點
  const startNodes = graph.nodes.filter(n => n.type === 'control.start');
  if (startNodes.length === 0) {
    errors.push('Graph must have a start node');
  } else if (startNodes.length > 1) {
    errors.push('Graph must have exactly one start node');
  }
  
  // 檢查是否有 end 節點
  const endNodes = graph.nodes.filter(n => n.type === 'control.end');
  if (endNodes.length === 0) {
    errors.push('Graph must have at least one end node');
  }
  
  // 檢查所有邊的節點是否存在
  const nodeIds = new Set(graph.nodes.map(n => n.id));
  for (const edge of graph.edges) {
    if (!nodeIds.has(edge.from)) {
      errors.push(`Edge references non-existent node: ${edge.from}`);
    }
    if (!nodeIds.has(edge.to)) {
      errors.push(`Edge references non-existent node: ${edge.to}`);
    }
  }
  
  // 檢查 branch 節點是否有條件
  for (const node of graph.nodes) {
    if (node.type === 'control.branch') {
      if (!node.conditions || node.conditions.length === 0) {
        errors.push(`Branch node ${node.id} must have conditions`);
      }
    }
  }
  
  // 檢查 skill 節點是否有 skillId
  for (const node of graph.nodes) {
    if (node.type === 'skill' && !node.skillId) {
      errors.push(`Skill node ${node.id} must have skillId`);
    }
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
}

/** 找到圖中的所有路徑 */
export function findAllPaths(graph: CapabilityGraph): string[][] {
  const adjacency = buildAdjacencyList(graph);
  const startNode = graph.nodes.find(n => n.type === 'control.start');
  const endNodes = new Set(graph.nodes.filter(n => n.type === 'control.end').map(n => n.id));
  
  if (!startNode) return [];
  
  const allPaths: string[][] = [];
  const currentPath: string[] = [];
  const visited = new Set<string>();
  
  function dfs(nodeId: string) {
    if (visited.has(nodeId)) return;
    
    currentPath.push(nodeId);
    visited.add(nodeId);
    
    if (endNodes.has(nodeId)) {
      allPaths.push([...currentPath]);
    } else {
      const neighbors = adjacency.get(nodeId) || [];
      for (const neighbor of neighbors) {
        dfs(neighbor);
      }
    }
    
    currentPath.pop();
    visited.delete(nodeId);
  }
  
  dfs(startNode.id);
  return allPaths;
}

/** 將圖轉換為 Mermaid 格式 */
export function toMermaid(graph: CapabilityGraph): string {
  const lines: string[] = ['graph TD'];
  
  // 節點定義
  for (const node of graph.nodes) {
    const shape = getNodeShape(node.type);
    const label = node.skillId || node.id;
    lines.push(`    ${node.id}${shape[0]}${label}${shape[1]}`);
  }
  
  // 邊定義
  for (const edge of graph.edges) {
    const arrow = getEdgeArrow(edge.type);
    const label = edge.condition ? `|${edge.condition}|` : '';
    lines.push(`    ${edge.from} ${arrow}${label} ${edge.to}`);
  }
  
  return lines.join('\n');
}

function getNodeShape(type: NodeType): [string, string] {
  switch (type) {
    case 'control.start':
    case 'control.end':
      return ['((', '))'];  // 圓形
    case 'control.branch':
      return ['{', '}'];     // 菱形
    case 'control.merge':
    case 'control.parallel_join':
      return ['[[', ']]'];   // 方形框
    case 'interaction.confirm':
    case 'interaction.select':
    case 'interaction.input':
      return ['[/', '/]'];   // 平行四邊形
    default:
      return ['[', ']'];     // 矩形
  }
}

function getEdgeArrow(type: EdgeType): string {
  switch (type) {
    case 'conditional':
      return '-..->';
    case 'iteration':
      return '==>';
    case 'parallel':
      return '-->';
    default:
      return '-->';
  }
}
