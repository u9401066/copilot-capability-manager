/**
 * Capability Engine Bridge - TypeScript 橋接層
 * 
 * 架構：
 * - Python 核心：圖執行、抽象節點解析、Fallback 處理
 * - TypeScript 橋接：VS Code Extension UI 呼叫 Python 引擎
 * 
 * 通訊方式：
 * 1. 直接 spawn Python process
 * 2. 透過 MCP Server（未來）
 */

import * as vscode from 'vscode';
import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';

// ═══════════════════════════════════════════════════════════════════
// 類型定義（與 Python 對應）
// ═══════════════════════════════════════════════════════════════════

export type NodeType = 
  | 'skill'
  | 'abstract'
  | 'control.start'
  | 'control.end'
  | 'control.branch'
  | 'control.merge'
  | 'control.loop_start'
  | 'control.loop_end'
  | 'interaction.confirm'
  | 'interaction.select'
  | 'interaction.input';

export type EdgeType = 'sequence' | 'conditional' | 'iteration' | 'parallel' | 'fallback';

export type ExecutionStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped' | 'waiting';

export type ComplexityLevel = 'trivial' | 'simple' | 'moderate' | 'complex' | 'very_complex';

export interface GraphNode {
  id: string;
  type: NodeType;
  skill_id?: string;
  contract?: {
    inputs: string[];
    outputs: string[];
    capabilities: string[];
  };
  implementations?: Array<{
    id: string;
    skill_id: string;
    priority: number;
    conditions: string[];
    fallbacks: string[];
  }>;
  conditions?: Array<{
    name: string;
    expression: string;
    target: string;
  }>;
  prompt?: string;
  options?: string[];
  outputs?: string[];
  max_iterations?: number;
}

export interface GraphEdge {
  from: string;
  to: string;
  type: EdgeType;
  condition?: string;
  trigger?: string;
}

export interface CapabilityGraph {
  id: string;
  version: string;
  name: string;
  description: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  fallback_strategy?: string;
  max_retries?: number;
}

export interface GraphMetrics {
  node_count: number;
  edge_count: number;
  cyclomatic_complexity: number;
  max_depth: number;
  branch_factor: number;
  max_iterations: number;
  interaction_count: number;
  parallel_branches: number;
  abstract_nodes: number;
  complexity_score: number;
  complexity_level: ComplexityLevel;
}

export interface ExecutionStep {
  node_id: string;
  node_type: NodeType;
  skill_id?: string;
  status: ExecutionStatus;
  started_at: string;
  finished_at?: string;
  result?: any;
  error?: {
    type: string;
    message: string;
  };
  fallback_used: boolean;
  retry_count: number;
}

export interface ExecutionTrace {
  graph_id: string;
  started_at: string;
  finished_at?: string;
  status: ExecutionStatus;
  steps: ExecutionStep[];
  path: string[];
  variables: Record<string, any>;
  total_nodes: number;
  executed_nodes: number;
  failed_nodes: number;
  skipped_nodes: number;
  total_retries: number;
}

// ═══════════════════════════════════════════════════════════════════
// Python 引擎橋接
// ═══════════════════════════════════════════════════════════════════

export interface EngineCommand {
  command: 'execute' | 'validate' | 'metrics' | 'mermaid' | 'stop';
  graph?: CapabilityGraph;
  variables?: Record<string, any>;
}

export interface EngineResponse {
  success: boolean;
  data?: any;
  error?: string;
}

export class CapabilityEngineBridge {
  private pythonPath: string;
  private enginePath: string;
  private process: ChildProcess | null = null;
  private outputChannel: vscode.OutputChannel;

  constructor(extensionPath: string) {
    this.pythonPath = 'python'; // 可從設定讀取
    this.enginePath = path.join(extensionPath, '..', 'src', 'capability_engine');
    this.outputChannel = vscode.window.createOutputChannel('Capability Engine');
  }

  /**
   * 驗證圖結構
   */
  async validateGraph(graph: CapabilityGraph): Promise<{ valid: boolean; errors: string[] }> {
    const result = await this.runCommand({
      command: 'validate',
      graph,
    });

    if (result.success) {
      return result.data;
    } else {
      return { valid: false, errors: [result.error || 'Unknown error'] };
    }
  }

  /**
   * 計算複雜度指標
   */
  async calculateMetrics(graph: CapabilityGraph): Promise<GraphMetrics | null> {
    const result = await this.runCommand({
      command: 'metrics',
      graph,
    });

    return result.success ? result.data : null;
  }

  /**
   * 執行能力圖
   */
  async execute(
    graph: CapabilityGraph,
    variables?: Record<string, any>,
    options?: {
      onNodeStart?: (nodeId: string, nodeType: NodeType) => void;
      onNodeComplete?: (nodeId: string, status: ExecutionStatus) => void;
      onInteraction?: (type: string, prompt: string, options?: string[]) => Promise<any>;
    }
  ): Promise<ExecutionTrace | null> {
    // 設定互動回調
    if (options?.onInteraction) {
      this.setupInteractionHandler(options.onInteraction);
    }

    const result = await this.runCommand({
      command: 'execute',
      graph,
      variables,
    });

    return result.success ? result.data : null;
  }

  /**
   * 轉換為 Mermaid 格式
   */
  async toMermaid(graph: CapabilityGraph): Promise<string> {
    const result = await this.runCommand({
      command: 'mermaid',
      graph,
    });

    return result.success ? result.data : '';
  }

  /**
   * 停止執行
   */
  stop(): void {
    if (this.process) {
      this.process.kill();
      this.process = null;
    }
  }

  /**
   * 執行 Python 命令
   */
  private async runCommand(cmd: EngineCommand): Promise<EngineResponse> {
    return new Promise((resolve) => {
      const pythonCode = `
import sys
import json
sys.path.insert(0, '${this.enginePath.replace(/\\/g, '\\\\')}')
sys.path.insert(0, '${path.dirname(this.enginePath).replace(/\\/g, '\\\\')}')

from capability_engine.graph import CapabilityGraph
from capability_engine.adaptive import AdaptiveGraphEngine
import asyncio

cmd = json.loads('''${JSON.stringify(cmd)}''')

def main():
    if cmd['command'] == 'validate':
        graph = CapabilityGraph.from_dict(cmd['graph'])
        valid, errors = graph.validate()
        return {'success': True, 'data': {'valid': valid, 'errors': errors}}
    
    elif cmd['command'] == 'metrics':
        graph = CapabilityGraph.from_dict(cmd['graph'])
        metrics = graph.calculate_metrics()
        return {'success': True, 'data': {
            'node_count': metrics.node_count,
            'edge_count': metrics.edge_count,
            'cyclomatic_complexity': metrics.cyclomatic_complexity,
            'max_depth': metrics.max_depth,
            'branch_factor': metrics.branch_factor,
            'max_iterations': metrics.max_iterations,
            'interaction_count': metrics.interaction_count,
            'parallel_branches': metrics.parallel_branches,
            'abstract_nodes': metrics.abstract_nodes,
            'complexity_score': metrics.complexity_score,
            'complexity_level': metrics.complexity_level.value,
        }}
    
    elif cmd['command'] == 'mermaid':
        graph = CapabilityGraph.from_dict(cmd['graph'])
        return {'success': True, 'data': graph.to_mermaid()}
    
    else:
        return {'success': False, 'error': f"Unknown command: {cmd['command']}"}

try:
    result = main()
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({'success': False, 'error': str(e)}))
`;

      const process = spawn(this.pythonPath, ['-c', pythonCode]);
      let stdout = '';
      let stderr = '';

      process.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      process.stderr.on('data', (data) => {
        stderr += data.toString();
        this.outputChannel.appendLine(`[stderr] ${data.toString()}`);
      });

      process.on('close', (code) => {
        if (code === 0 && stdout) {
          try {
            const result = JSON.parse(stdout.trim());
            resolve(result);
          } catch (e) {
            resolve({ success: false, error: `Failed to parse output: ${stdout}` });
          }
        } else {
          resolve({ success: false, error: stderr || `Process exited with code ${code}` });
        }
      });

      process.on('error', (err) => {
        resolve({ success: false, error: err.message });
      });
    });
  }

  /**
   * 設定互動處理器
   */
  private setupInteractionHandler(
    handler: (type: string, prompt: string, options?: string[]) => Promise<any>
  ): void {
    // TODO: 實作透過 IPC 與 Python process 通訊的互動處理
    // 目前先用同步執行，未來可改為 MCP Server
  }

  dispose(): void {
    this.stop();
    this.outputChannel.dispose();
  }
}

// ═══════════════════════════════════════════════════════════════════
// VS Code 整合
// ═══════════════════════════════════════════════════════════════════

/**
 * 在 VS Code 中顯示圖的預覽
 */
export async function showGraphPreview(
  bridge: CapabilityEngineBridge,
  graph: CapabilityGraph
): Promise<void> {
  const mermaid = await bridge.toMermaid(graph);
  const metrics = await bridge.calculateMetrics(graph);

  const panel = vscode.window.createWebviewPanel(
    'capabilityGraphPreview',
    `Graph: ${graph.name || graph.id}`,
    vscode.ViewColumn.Beside,
    { enableScripts: true }
  );

  panel.webview.html = `
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
  <style>
    body { font-family: var(--vscode-font-family); padding: 20px; }
    .metrics { margin-bottom: 20px; padding: 10px; background: var(--vscode-editor-background); border-radius: 4px; }
    .metrics h3 { margin-top: 0; }
    .metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
    .metric { text-align: center; }
    .metric-value { font-size: 24px; font-weight: bold; color: var(--vscode-textLink-foreground); }
    .metric-label { font-size: 12px; color: var(--vscode-descriptionForeground); }
    .complexity-${metrics?.complexity_level} { color: ${getComplexityColor(metrics?.complexity_level)}; }
    .mermaid { margin-top: 20px; }
  </style>
</head>
<body>
  <div class="metrics">
    <h3>📊 複雜度指標</h3>
    <div class="metrics-grid">
      <div class="metric">
        <div class="metric-value">${metrics?.node_count ?? '-'}</div>
        <div class="metric-label">節點數</div>
      </div>
      <div class="metric">
        <div class="metric-value">${metrics?.cyclomatic_complexity ?? '-'}</div>
        <div class="metric-label">環路複雜度</div>
      </div>
      <div class="metric">
        <div class="metric-value">${metrics?.abstract_nodes ?? '-'}</div>
        <div class="metric-label">抽象節點</div>
      </div>
      <div class="metric">
        <div class="metric-value">${metrics?.max_depth ?? '-'}</div>
        <div class="metric-label">最大深度</div>
      </div>
      <div class="metric">
        <div class="metric-value complexity-${metrics?.complexity_level}">${metrics?.complexity_score?.toFixed(0) ?? '-'}</div>
        <div class="metric-label">複雜度分數</div>
      </div>
      <div class="metric">
        <div class="metric-value complexity-${metrics?.complexity_level}">${metrics?.complexity_level ?? '-'}</div>
        <div class="metric-label">等級</div>
      </div>
    </div>
  </div>
  
  <h3>🔗 圖結構</h3>
  <div class="mermaid">
${mermaid}
  </div>
  
  <script>
    mermaid.initialize({ startOnLoad: true, theme: 'dark' });
  </script>
</body>
</html>
`;
}

function getComplexityColor(level?: string): string {
  switch (level) {
    case 'trivial': return '#4CAF50';
    case 'simple': return '#8BC34A';
    case 'moderate': return '#FFC107';
    case 'complex': return '#FF9800';
    case 'very_complex': return '#F44336';
    default: return 'inherit';
  }
}

/**
 * 執行能力圖並顯示進度
 */
export async function executeWithProgress(
  bridge: CapabilityEngineBridge,
  graph: CapabilityGraph,
  variables?: Record<string, any>
): Promise<ExecutionTrace | null> {
  return vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: `執行: ${graph.name || graph.id}`,
      cancellable: true,
    },
    async (progress, token) => {
      token.onCancellationRequested(() => {
        bridge.stop();
      });

      const trace = await bridge.execute(graph, variables, {
        onNodeStart: (nodeId, nodeType) => {
          progress.report({ message: `執行 ${nodeId}...` });
        },
        onNodeComplete: (nodeId, status) => {
          const icon = status === 'completed' ? '✅' : status === 'failed' ? '❌' : '⏭️';
          progress.report({ message: `${icon} ${nodeId}` });
        },
      });

      if (trace?.status === 'completed') {
        vscode.window.showInformationMessage(
          `✅ 執行完成！共 ${trace.executed_nodes} 個節點，耗時 ${trace.steps.reduce((sum, s) => sum + (s.retry_count || 0), 0)} 次重試`
        );
      } else if (trace?.status === 'failed') {
        vscode.window.showErrorMessage(
          `❌ 執行失敗：${trace.steps.find(s => s.status === 'failed')?.error?.message || 'Unknown error'}`
        );
      }

      return trace;
    }
  );
}
