"""
Application - Use Cases - Execute Capability
應用層 - 用例 - 執行能力
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Protocol
from datetime import datetime
import uuid

from ...domain.entities import CapabilityGraph, GraphNode
from ...domain.value_objects import NodeType, ExecutionStatus


class SkillExecutor(Protocol):
    """技能執行器協議"""
    async def execute(self, skill_id: str, inputs: dict[str, Any]) -> dict[str, Any]:
        ...


class InteractionHandler(Protocol):
    """互動處理器協議"""
    async def confirm(self, prompt: str) -> bool:
        ...
    
    async def select(self, prompt: str, options: list[str]) -> str:
        ...
    
    async def input(self, prompt: str) -> str:
        ...


@dataclass
class ExecutionStep:
    """執行步驟"""
    node_id: str
    node_type: str
    status: ExecutionStatus
    start_time: datetime
    end_time: datetime | None = None
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    resolved_skill: str | None = None


@dataclass
class ExecutionTrace:
    """執行追蹤"""
    execution_id: str
    capability_id: str
    status: ExecutionStatus
    steps: list[ExecutionStep] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    
    def add_step(self, step: ExecutionStep) -> None:
        self.steps.append(step)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "capability_id": self.capability_id,
            "status": self.status.value,
            "steps": [
                {
                    "node_id": s.node_id,
                    "node_type": s.node_type,
                    "status": s.status.value,
                    "start_time": s.start_time.isoformat(),
                    "end_time": s.end_time.isoformat() if s.end_time else None,
                    "error": s.error,
                    "resolved_skill": s.resolved_skill,
                }
                for s in self.steps
            ],
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }


class ExecuteCapabilityUseCase:
    """
    執行能力用例
    
    核心業務邏輯：
    1. 遍歷能力圖
    2. 解析抽象節點
    3. 執行技能
    4. 處理分支和迴圈
    5. 追蹤執行狀態
    """
    
    def __init__(
        self,
        skill_executor: SkillExecutor | None = None,
        interaction_handler: InteractionHandler | None = None,
    ):
        self.skill_executor = skill_executor
        self.interaction_handler = interaction_handler
    
    async def execute(
        self,
        graph: CapabilityGraph,
        inputs: dict[str, Any],
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        執行能力圖
        
        Args:
            graph: 能力圖
            inputs: 執行輸入
            options: 執行選項
                - auto_resolve: 是否自動解析抽象節點
                - skip_confirmation: 是否跳過確認
        
        Returns:
            執行結果
        """
        options = options or {}
        auto_resolve = options.get("auto_resolve", True)
        skip_confirmation = options.get("skip_confirmation", False)
        
        # 建立執行追蹤
        trace = ExecutionTrace(
            execution_id=str(uuid.uuid4()),
            capability_id=graph.id,
            status=ExecutionStatus.RUNNING,
        )
        
        # 執行上下文
        context: dict[str, Any] = {
            "inputs": inputs,
            "outputs": {},
            "variables": {},
        }
        
        try:
            # 找到起始節點
            start_nodes = graph.find_start_nodes()
            if not start_nodes:
                raise ValueError("No start node found in graph")
            
            # 從起始節點開始執行
            for start_node in start_nodes:
                await self._execute_node(
                    graph, start_node, context, trace,
                    auto_resolve, skip_confirmation
                )
            
            trace.status = ExecutionStatus.COMPLETED
            trace.end_time = datetime.now()
            
            return {
                "success": True,
                "execution_id": trace.execution_id,
                "outputs": context["outputs"],
                "trace": trace.to_dict(),
            }
            
        except Exception as e:
            trace.status = ExecutionStatus.FAILED
            trace.end_time = datetime.now()
            
            return {
                "success": False,
                "execution_id": trace.execution_id,
                "error": str(e),
                "trace": trace.to_dict(),
            }
    
    async def _execute_node(
        self,
        graph: CapabilityGraph,
        node: GraphNode,
        context: dict[str, Any],
        trace: ExecutionTrace,
        auto_resolve: bool,
        skip_confirmation: bool,
    ) -> None:
        """執行單個節點"""
        step = ExecutionStep(
            node_id=node.id,
            node_type=node.type.value,
            status=ExecutionStatus.RUNNING,
            start_time=datetime.now(),
            inputs=context.get("outputs", {}),
        )
        trace.add_step(step)
        
        try:
            # 根據節點類型執行
            if node.type == NodeType.START:
                # 起始節點，直接繼續
                pass
            
            elif node.type == NodeType.END:
                # 結束節點，收集輸出
                step.status = ExecutionStatus.COMPLETED
                step.end_time = datetime.now()
                return  # 不繼續執行後繼
            
            elif node.type == NodeType.SKILL:
                # 執行技能
                if self.skill_executor and node.skill_id:
                    result = await self.skill_executor.execute(
                        node.skill_id,
                        context.get("outputs", {})
                    )
                    context["outputs"].update(result)
                    step.outputs = result
            
            elif node.type == NodeType.ABSTRACT:
                # 抽象節點 - 需要解析
                if auto_resolve and node.implementations:
                    # 自動選擇第一個實現
                    impl = node.get_available_implementations()[0]
                    step.resolved_skill = impl.skill_id
                    
                    if self.skill_executor:
                        result = await self.skill_executor.execute(
                            impl.skill_id,
                            context.get("outputs", {})
                        )
                        context["outputs"].update(result)
                        step.outputs = result
            
            elif node.type == NodeType.BRANCH:
                # 分支節點 - 評估條件
                selected_target = await self._evaluate_branch(
                    node, context
                )
                step.outputs = {"selected": selected_target}
                
                # 只執行選中的分支
                if selected_target:
                    target_node = graph.get_node(selected_target)
                    if target_node:
                        step.status = ExecutionStatus.COMPLETED
                        step.end_time = datetime.now()
                        await self._execute_node(
                            graph, target_node, context, trace,
                            auto_resolve, skip_confirmation
                        )
                        return
            
            elif node.type == NodeType.CONFIRM:
                # 確認節點
                if not skip_confirmation and self.interaction_handler:
                    confirmed = await self.interaction_handler.confirm(
                        node.prompt or "Continue?"
                    )
                    if not confirmed:
                        step.status = ExecutionStatus.SKIPPED
                        step.end_time = datetime.now()
                        return
            
            elif node.type == NodeType.SELECT:
                # 選擇節點
                if self.interaction_handler:
                    selected = await self.interaction_handler.select(
                        node.prompt or "Select an option:",
                        node.options
                    )
                    context["variables"]["selected"] = selected
                    step.outputs = {"selected": selected}
            
            elif node.type == NodeType.LOOP:
                # 迴圈節點
                await self._execute_loop(
                    graph, node, context, trace,
                    auto_resolve, skip_confirmation
                )
            
            step.status = ExecutionStatus.COMPLETED
            step.end_time = datetime.now()
            
            # 執行後繼節點
            successors = graph.get_successors(node.id)
            for successor in successors:
                await self._execute_node(
                    graph, successor, context, trace,
                    auto_resolve, skip_confirmation
                )
                
        except Exception as e:
            step.status = ExecutionStatus.FAILED
            step.error = str(e)
            step.end_time = datetime.now()
            raise
    
    async def _evaluate_branch(
        self,
        node: GraphNode,
        context: dict[str, Any],
    ) -> str | None:
        """評估分支條件"""
        for condition in node.conditions:
            # 簡單的條件評估
            expr = condition.expression
            
            # 支援基本的條件語法
            # file_type == 'pdf'
            # count > 10
            # has_error == true
            
            try:
                # 準備評估環境
                eval_context = {
                    **context.get("inputs", {}),
                    **context.get("outputs", {}),
                    **context.get("variables", {}),
                }
                
                # 安全評估（生產環境應使用更安全的方式）
                result = eval(expr, {"__builtins__": {}}, eval_context)
                
                if result:
                    return condition.target
            except Exception:
                continue
        
        # 沒有匹配的條件，返回第一個條件的目標（default）
        if node.conditions:
            return node.conditions[-1].target
        
        return None
    
    async def _execute_loop(
        self,
        graph: CapabilityGraph,
        node: GraphNode,
        context: dict[str, Any],
        trace: ExecutionTrace,
        auto_resolve: bool,
        skip_confirmation: bool,
    ) -> None:
        """執行迴圈"""
        iteration = 0
        max_iterations = node.max_iterations
        
        while iteration < max_iterations:
            iteration += 1
            context["variables"]["loop_iteration"] = iteration
            
            # 執行迴圈體（後繼節點）
            successors = graph.get_successors(node.id)
            
            for successor in successors:
                await self._execute_node(
                    graph, successor, context, trace,
                    auto_resolve, skip_confirmation
                )
            
            # 檢查終止條件
            if context.get("variables", {}).get("loop_break", False):
                break
