"""
Adaptive Graph Engine - 自適應圖執行引擎
支援抽象節點、動態解析、Fallback 機制
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable, Protocol
import asyncio
import time
from datetime import datetime

from .graph import (
    CapabilityGraph, GraphNode, GraphEdge, 
    NodeType, EdgeType, ExecutionStatus
)
from .resolver import AbstractNodeResolver, ResolutionContext
from .fallback import FallbackChain, FallbackResult, ExecutionError, create_standard_fallback_chain


# ═══════════════════════════════════════════════════════════════════
# 執行記錄
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ExecutionStep:
    """執行步驟記錄"""
    node_id: str
    node_type: NodeType
    skill_id: str | None
    status: ExecutionStatus
    started_at: datetime
    finished_at: datetime | None = None
    result: Any = None
    error: ExecutionError | None = None
    fallback_used: bool = False
    retry_count: int = 0
    
    @property
    def duration(self) -> float | None:
        """執行時長（秒）"""
        if self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None


@dataclass
class ExecutionTrace:
    """執行軌跡"""
    graph_id: str
    started_at: datetime
    finished_at: datetime | None = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    steps: list[ExecutionStep] = field(default_factory=list)
    path: list[str] = field(default_factory=list)
    variables: dict[str, Any] = field(default_factory=dict)
    
    # 統計
    total_nodes: int = 0
    executed_nodes: int = 0
    failed_nodes: int = 0
    skipped_nodes: int = 0
    total_retries: int = 0
    
    @property
    def success(self) -> bool:
        return self.status == ExecutionStatus.COMPLETED
    
    @property
    def duration(self) -> float | None:
        if self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None


# ═══════════════════════════════════════════════════════════════════
# Skill 執行器協議
# ═══════════════════════════════════════════════════════════════════

class SkillExecutor(Protocol):
    """Skill 執行器協議"""
    
    async def execute(
        self, 
        skill_id: str, 
        inputs: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """執行 Skill 並返回輸出"""
        ...
    
    def is_available(self, skill_id: str) -> bool:
        """檢查 Skill 是否可用"""
        ...


class InteractionHandler(Protocol):
    """互動處理器協議"""
    
    async def confirm(self, prompt: str) -> bool:
        """確認對話"""
        ...
    
    async def select(self, prompt: str, options: list[str]) -> str:
        """選擇對話"""
        ...
    
    async def input(self, prompt: str) -> str:
        """輸入對話"""
        ...


# ═══════════════════════════════════════════════════════════════════
# 自適應圖執行引擎
# ═══════════════════════════════════════════════════════════════════

class AdaptiveGraphEngine:
    """
    自適應圖執行引擎
    
    特性：
    1. 抽象節點動態解析
    2. 自動 Fallback 處理
    3. 執行軌跡追蹤
    4. 用戶互動支援
    """
    
    def __init__(
        self,
        graph: CapabilityGraph,
        skill_executor: SkillExecutor,
        interaction_handler: InteractionHandler | None = None,
        fallback_chain: FallbackChain | None = None,
    ):
        self.graph = graph
        self.skill_executor = skill_executor
        self.interaction_handler = interaction_handler
        self.fallback_chain = fallback_chain or create_standard_fallback_chain()
        self.resolver = AbstractNodeResolver()
        
        # 執行狀態
        self._trace: ExecutionTrace | None = None
        self._variables: dict[str, Any] = {}
        self._running = False
        
        # 回調
        self._on_node_start: Callable[[str, NodeType], None] | None = None
        self._on_node_complete: Callable[[str, ExecutionStatus], None] | None = None
        self._on_variable_set: Callable[[str, Any], None] | None = None
    
    # ─────────────────────────────────────────────────────────────
    # 回調設定
    # ─────────────────────────────────────────────────────────────
    
    def on_node_start(self, callback: Callable[[str, NodeType], None]):
        """設定節點開始回調"""
        self._on_node_start = callback
    
    def on_node_complete(self, callback: Callable[[str, ExecutionStatus], None]):
        """設定節點完成回調"""
        self._on_node_complete = callback
    
    def on_variable_set(self, callback: Callable[[str, Any], None]):
        """設定變數設定回調"""
        self._on_variable_set = callback
    
    # ─────────────────────────────────────────────────────────────
    # 主執行方法
    # ─────────────────────────────────────────────────────────────
    
    async def execute(
        self,
        initial_variables: dict[str, Any] | None = None,
    ) -> ExecutionTrace:
        """
        執行能力圖
        
        Args:
            initial_variables: 初始變數
        
        Returns:
            ExecutionTrace: 執行軌跡
        """
        # 驗證圖
        valid, errors = self.graph.validate()
        if not valid:
            raise ValueError(f"Invalid graph: {errors}")
        
        # 初始化
        self._running = True
        self._variables = initial_variables or {}
        self._trace = ExecutionTrace(
            graph_id=self.graph.id,
            started_at=datetime.now(),
            total_nodes=len(self.graph.nodes),
        )
        
        # 找到起始節點
        start_node = self.graph.get_start_node()
        if not start_node:
            raise ValueError("Graph must have a start node")
        
        try:
            # 開始執行
            await self._execute_node(start_node.id)
            
            # 標記完成
            self._trace.status = ExecutionStatus.COMPLETED
            self._trace.variables = self._variables.copy()
            
        except Exception as e:
            self._trace.status = ExecutionStatus.FAILED
            raise
        
        finally:
            self._trace.finished_at = datetime.now()
            self._running = False
        
        return self._trace
    
    async def _execute_node(self, node_id: str) -> Any:
        """執行單一節點"""
        node = self.graph.get_node(node_id)
        if not node:
            raise ValueError(f"Node not found: {node_id}")
        
        # 記錄路徑
        self._trace.path.append(node_id)
        
        # 建立步驟記錄
        step = ExecutionStep(
            node_id=node_id,
            node_type=node.type,
            skill_id=node.skill_id,
            status=ExecutionStatus.RUNNING,
            started_at=datetime.now(),
        )
        self._trace.steps.append(step)
        
        # 回調
        if self._on_node_start:
            self._on_node_start(node_id, node.type)
        
        try:
            result = await self._execute_node_by_type(node, step)
            step.status = ExecutionStatus.COMPLETED
            step.result = result
            self._trace.executed_nodes += 1
            
        except Exception as e:
            step.status = ExecutionStatus.FAILED
            step.error = ExecutionError.from_exception(e, node_id, node.skill_id)
            self._trace.failed_nodes += 1
            raise
        
        finally:
            step.finished_at = datetime.now()
            
            if self._on_node_complete:
                self._on_node_complete(node_id, step.status)
        
        return result
    
    async def _execute_node_by_type(self, node: GraphNode, step: ExecutionStep) -> Any:
        """根據節點類型執行"""
        
        if node.type == NodeType.START:
            return await self._handle_start(node)
        
        elif node.type == NodeType.END:
            return await self._handle_end(node)
        
        elif node.type == NodeType.SKILL:
            return await self._handle_skill(node, step)
        
        elif node.type == NodeType.ABSTRACT:
            return await self._handle_abstract(node, step)
        
        elif node.type == NodeType.BRANCH:
            return await self._handle_branch(node)
        
        elif node.type == NodeType.MERGE:
            return await self._handle_merge(node)
        
        elif node.type == NodeType.LOOP_START:
            return await self._handle_loop_start(node)
        
        elif node.type == NodeType.LOOP_END:
            return await self._handle_loop_end(node)
        
        elif node.type in (NodeType.CONFIRM, NodeType.SELECT, NodeType.INPUT):
            return await self._handle_interaction(node)
        
        else:
            raise ValueError(f"Unknown node type: {node.type}")
    
    # ─────────────────────────────────────────────────────────────
    # 各類型節點處理
    # ─────────────────────────────────────────────────────────────
    
    async def _handle_start(self, node: GraphNode) -> Any:
        """處理開始節點"""
        successors = self.graph.get_successors(node.id)
        if successors:
            return await self._execute_node(successors[0])
        return None
    
    async def _handle_end(self, node: GraphNode) -> Any:
        """處理結束節點"""
        return self._variables.copy()
    
    async def _handle_skill(self, node: GraphNode, step: ExecutionStep) -> Any:
        """處理 Skill 節點"""
        if not node.skill_id:
            raise ValueError(f"Skill node {node.id} has no skill_id")
        
        # 準備輸入
        inputs = {k: self._variables.get(k) for k in self._variables}
        
        # 使用 Fallback 執行
        async def execute_skill():
            return await self.skill_executor.execute(
                node.skill_id,
                inputs,
                {"node_id": node.id},
            )
        
        result = await self.fallback_chain.execute_with_fallback(
            execute_skill,
            node_id=node.id,
            skill_id=node.skill_id,
        )
        
        step.fallback_used = result.strategy_used.value != "retry" or result.retries > 0
        step.retry_count = result.retries
        self._trace.total_retries += result.retries
        
        if not result.success:
            raise Exception(f"Skill execution failed: {result.error}")
        
        # 設定輸出變數
        if node.outputs and isinstance(result, dict):
            for output_name in node.outputs:
                if output_name in result:
                    self._set_variable(output_name, result[output_name])
        
        # 繼續執行
        successors = self.graph.get_successors(node.id)
        if successors:
            return await self._execute_node(successors[0])
        
        return result
    
    async def _handle_abstract(self, node: GraphNode, step: ExecutionStep) -> Any:
        """處理抽象節點（動態解析）"""
        
        # 建立解析上下文
        context = ResolutionContext(
            input_path=self._variables.get("input_path"),
            input_type=self._variables.get("input_type"),
            available_skills=[
                impl.skill_id for impl in node.implementations
                if self.skill_executor.is_available(impl.skill_id)
            ],
            variables=self._variables,
        )
        
        # 解析抽象節點
        implementation = self.resolver.resolve(node, context)
        
        if not implementation:
            # 需要用戶選擇
            if self.interaction_handler and node.resolution_strategy == "user_select":
                options = [impl.skill_id for impl in node.implementations]
                selected = await self.interaction_handler.select(
                    f"請選擇用於 {node.id} 的實現：",
                    options,
                )
                implementation = next(
                    (impl for impl in node.implementations if impl.skill_id == selected),
                    None,
                )
            
            if not implementation:
                raise ValueError(f"Cannot resolve abstract node: {node.id}")
        
        # 使用 Fallback 執行選定的實現
        step.skill_id = implementation.skill_id
        inputs = {k: self._variables.get(k) for k in self._variables}
        
        available_impls = [impl.skill_id for impl in node.implementations]
        
        async def execute_implementation():
            return await self.skill_executor.execute(
                implementation.skill_id,
                inputs,
                {"node_id": node.id, "abstract": True},
            )
        
        result = await self.fallback_chain.execute_with_fallback(
            execute_implementation,
            node_id=node.id,
            skill_id=implementation.skill_id,
            available_implementations=available_impls,
        )
        
        step.fallback_used = True
        step.retry_count = result.retries
        self._trace.total_retries += result.retries
        
        if not result.success:
            raise Exception(f"Abstract node execution failed: {result.error}")
        
        # 設定輸出變數
        if node.outputs:
            for output_name in node.outputs:
                self._set_variable(output_name, result)
        
        # 繼續執行
        successors = self.graph.get_successors(node.id)
        if successors:
            return await self._execute_node(successors[0])
        
        return result
    
    async def _handle_branch(self, node: GraphNode) -> Any:
        """處理分支節點"""
        if not node.conditions:
            raise ValueError(f"Branch node {node.id} has no conditions")
        
        # 評估條件
        for condition in node.conditions:
            if self._evaluate_condition(condition.expression):
                return await self._execute_node(condition.target)
        
        # 預設：第一個分支
        return await self._execute_node(node.conditions[0].target)
    
    async def _handle_merge(self, node: GraphNode) -> Any:
        """處理合併節點"""
        successors = self.graph.get_successors(node.id)
        if successors:
            return await self._execute_node(successors[0])
        return None
    
    async def _handle_loop_start(self, node: GraphNode) -> Any:
        """處理迴圈開始節點"""
        max_iterations = node.max_iterations
        
        for i in range(max_iterations):
            self._set_variable("_iteration", i)
            self._set_variable("_iteration_count", i + 1)
            
            # 執行迴圈體
            successors = self.graph.get_successors(node.id)
            if successors:
                await self._execute_node(successors[0])
            
            # 檢查是否應該退出（由 loop_end 設定）
            if self._variables.get("_loop_exit"):
                self._variables.pop("_loop_exit", None)
                break
        
        # 清理迴圈變數
        self._variables.pop("_iteration", None)
        self._variables.pop("_iteration_count", None)
        
        return None
    
    async def _handle_loop_end(self, node: GraphNode) -> Any:
        """處理迴圈結束節點"""
        # loop_end 通常不需要特殊處理，由 loop_start 控制流程
        return None
    
    async def _handle_interaction(self, node: GraphNode) -> Any:
        """處理互動節點"""
        if not self.interaction_handler:
            raise ValueError("Interaction handler not set")
        
        prompt = node.prompt or f"請回應 {node.id}"
        
        if node.type == NodeType.CONFIRM:
            result = await self.interaction_handler.confirm(prompt)
        elif node.type == NodeType.SELECT:
            result = await self.interaction_handler.select(prompt, node.options)
        elif node.type == NodeType.INPUT:
            result = await self.interaction_handler.input(prompt)
        else:
            raise ValueError(f"Unknown interaction type: {node.type}")
        
        # 儲存結果
        output_name = node.outputs[0] if node.outputs else f"{node.id}_result"
        self._set_variable(output_name, result)
        
        # 繼續執行
        successors = self.graph.get_successors(node.id)
        if successors:
            return await self._execute_node(successors[0])
        
        return result
    
    # ─────────────────────────────────────────────────────────────
    # 輔助方法
    # ─────────────────────────────────────────────────────────────
    
    def _set_variable(self, name: str, value: Any):
        """設定變數"""
        self._variables[name] = value
        if self._on_variable_set:
            self._on_variable_set(name, value)
    
    def _evaluate_condition(self, expression: str) -> bool:
        """評估條件表達式"""
        try:
            # 建立安全的評估環境
            safe_vars = self._variables.copy()
            
            # 簡化實作：直接 eval
            # 生產環境應使用 ast 或專用表達式引擎
            return eval(expression, {"__builtins__": {}}, safe_vars)
        except Exception:
            return False
    
    def get_current_state(self) -> dict[str, Any]:
        """取得當前執行狀態"""
        return {
            "running": self._running,
            "variables": self._variables.copy(),
            "path": self._trace.path if self._trace else [],
            "executed_nodes": self._trace.executed_nodes if self._trace else 0,
        }
    
    def stop(self):
        """停止執行"""
        self._running = False


# ═══════════════════════════════════════════════════════════════════
# 工廠函數
# ═══════════════════════════════════════════════════════════════════

def create_engine(
    graph: CapabilityGraph,
    skill_executor: SkillExecutor,
    interaction_handler: InteractionHandler | None = None,
    fallback_mode: str = "standard",
) -> AdaptiveGraphEngine:
    """
    建立自適應圖執行引擎
    
    Args:
        graph: 能力圖
        skill_executor: Skill 執行器
        interaction_handler: 互動處理器
        fallback_mode: Fallback 模式 (standard, aggressive, conservative)
    
    Returns:
        AdaptiveGraphEngine: 執行引擎
    """
    from .fallback import (
        create_standard_fallback_chain,
        create_aggressive_fallback_chain,
        create_conservative_fallback_chain,
    )
    
    if fallback_mode == "aggressive":
        fallback_chain = create_aggressive_fallback_chain()
    elif fallback_mode == "conservative":
        fallback_chain = create_conservative_fallback_chain()
    else:
        fallback_chain = create_standard_fallback_chain()
    
    return AdaptiveGraphEngine(
        graph=graph,
        skill_executor=skill_executor,
        interaction_handler=interaction_handler,
        fallback_chain=fallback_chain,
    )
