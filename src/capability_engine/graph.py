"""
Graph Data Structures - 圖資料結構
基於圖論的能力定義
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Optional
import json


# ═══════════════════════════════════════════════════════════════════
# 枚舉類型
# ═══════════════════════════════════════════════════════════════════

class NodeType(Enum):
    """節點類型"""
    # Skill 節點
    SKILL = "skill"
    ABSTRACT = "abstract"  # 抽象節點 - 延遲綁定
    
    # 控制節點
    START = "control.start"
    END = "control.end"
    BRANCH = "control.branch"
    MERGE = "control.merge"
    LOOP_START = "control.loop_start"
    LOOP_END = "control.loop_end"
    PARALLEL_SPLIT = "control.parallel_split"
    PARALLEL_JOIN = "control.parallel_join"
    
    # 互動節點
    CONFIRM = "interaction.confirm"
    SELECT = "interaction.select"
    INPUT = "interaction.input"


class EdgeType(Enum):
    """邊類型"""
    SEQUENCE = "sequence"       # 順序執行
    CONDITIONAL = "conditional" # 條件分支
    ITERATION = "iteration"     # 迴圈
    PARALLEL = "parallel"       # 並行
    FALLBACK = "fallback"       # 失敗回退


class ExecutionStatus(Enum):
    """執行狀態"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WAITING = "waiting"  # 等待用戶輸入


class ComplexityLevel(Enum):
    """複雜度等級"""
    TRIVIAL = "trivial"
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


# ═══════════════════════════════════════════════════════════════════
# 節點定義
# ═══════════════════════════════════════════════════════════════════

@dataclass
class NodeContract:
    """節點的輸入輸出契約（用於抽象節點）"""
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)  # 需要的能力


@dataclass
class BranchCondition:
    """分支條件"""
    name: str
    expression: str
    target: str  # 目標節點 ID


@dataclass 
class Implementation:
    """抽象節點的具體實現"""
    id: str
    skill_id: str
    priority: int = 1
    conditions: list[str] = field(default_factory=list)  # 適用條件
    fallbacks: list[str] = field(default_factory=list)   # 失敗時的備選


@dataclass
class GraphNode:
    """圖節點"""
    id: str
    type: NodeType
    
    # Skill 節點專用
    skill_id: str | None = None
    
    # 抽象節點專用
    contract: NodeContract | None = None
    implementations: list[Implementation] = field(default_factory=list)
    resolution_strategy: str = "auto_detect"  # auto_detect | user_select | priority
    
    # 控制節點專用
    conditions: list[BranchCondition] = field(default_factory=list)
    max_iterations: int = 10
    
    # 互動節點專用
    prompt: str | None = None
    options: list[str] = field(default_factory=list)
    
    # 通用
    timeout: int | None = None  # 秒
    outputs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def is_abstract(self) -> bool:
        """是否為抽象節點"""
        return self.type == NodeType.ABSTRACT
    
    def is_control(self) -> bool:
        """是否為控制節點"""
        return self.type.value.startswith("control.")
    
    def is_interaction(self) -> bool:
        """是否為互動節點"""
        return self.type.value.startswith("interaction.")


# ═══════════════════════════════════════════════════════════════════
# 邊定義
# ═══════════════════════════════════════════════════════════════════

@dataclass
class GraphEdge:
    """圖的邊"""
    from_node: str
    to_node: str
    type: EdgeType = EdgeType.SEQUENCE
    
    # 條件邊專用
    condition: str | None = None
    
    # 迴圈邊專用
    max_count: int | None = None
    exit_condition: str | None = None
    
    # Fallback 邊專用
    trigger: str | None = None  # 觸發條件，如 "error.type == 'ParseError'"
    
    # 權重（用於路徑選擇）
    weight: float = 1.0


# ═══════════════════════════════════════════════════════════════════
# 圖定義
# ═══════════════════════════════════════════════════════════════════

@dataclass
class GraphMetrics:
    """圖的複雜度指標"""
    node_count: int = 0
    edge_count: int = 0
    cyclomatic_complexity: int = 0
    max_depth: int = 0
    branch_factor: float = 0.0
    max_iterations: int = 0
    interaction_count: int = 0
    parallel_branches: int = 0
    abstract_nodes: int = 0
    complexity_score: float = 0.0
    complexity_level: ComplexityLevel = ComplexityLevel.TRIVIAL


@dataclass
class CapabilityGraph:
    """能力圖"""
    id: str
    version: str = "1.0"
    name: str = ""
    description: str = ""
    
    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)
    
    # 全局配置
    fallback_strategy: str = "retry_then_ask"  # retry_then_ask | skip | abort
    max_retries: int = 3
    retry_delay: float = 1.0  # 秒
    
    # 快取
    _adjacency: dict[str, list[str]] = field(default_factory=dict, repr=False)
    _node_map: dict[str, GraphNode] = field(default_factory=dict, repr=False)
    _metrics: GraphMetrics | None = field(default=None, repr=False)
    
    def __post_init__(self):
        self._build_cache()
    
    def _build_cache(self):
        """建立快取"""
        self._node_map = {n.id: n for n in self.nodes}
        self._adjacency = {n.id: [] for n in self.nodes}
        for edge in self.edges:
            if edge.from_node in self._adjacency:
                self._adjacency[edge.from_node].append(edge.to_node)
    
    def get_node(self, node_id: str) -> GraphNode | None:
        """取得節點"""
        return self._node_map.get(node_id)
    
    def get_successors(self, node_id: str) -> list[str]:
        """取得後繼節點"""
        return self._adjacency.get(node_id, [])
    
    def get_predecessors(self, node_id: str) -> list[str]:
        """取得前驅節點"""
        return [e.from_node for e in self.edges if e.to_node == node_id]
    
    def get_edge(self, from_node: str, to_node: str) -> GraphEdge | None:
        """取得邊"""
        for edge in self.edges:
            if edge.from_node == from_node and edge.to_node == to_node:
                return edge
        return None
    
    def get_start_node(self) -> GraphNode | None:
        """取得起始節點"""
        for node in self.nodes:
            if node.type == NodeType.START:
                return node
        return None
    
    def get_end_nodes(self) -> list[GraphNode]:
        """取得結束節點"""
        return [n for n in self.nodes if n.type == NodeType.END]
    
    def get_abstract_nodes(self) -> list[GraphNode]:
        """取得所有抽象節點"""
        return [n for n in self.nodes if n.type == NodeType.ABSTRACT]
    
    def add_node(self, node: GraphNode):
        """新增節點"""
        self.nodes.append(node)
        self._node_map[node.id] = node
        self._adjacency[node.id] = []
        self._metrics = None  # 清除快取
    
    def add_edge(self, edge: GraphEdge):
        """新增邊"""
        self.edges.append(edge)
        if edge.from_node in self._adjacency:
            self._adjacency[edge.from_node].append(edge.to_node)
        self._metrics = None  # 清除快取
    
    def calculate_metrics(self) -> GraphMetrics:
        """計算複雜度指標"""
        if self._metrics is not None:
            return self._metrics
        
        N = len(self.nodes)
        E = len(self.edges)
        P = 1  # 假設單一連通分量
        
        # McCabe 環路複雜度
        cyclomatic = E - N + 2 * P
        
        # 計算各種指標
        loop_nodes = [n for n in self.nodes if n.type == NodeType.LOOP_START]
        max_iterations = max((n.max_iterations for n in loop_nodes), default=0)
        
        interaction_count = sum(1 for n in self.nodes if n.is_interaction())
        parallel_branches = sum(1 for n in self.nodes if n.type == NodeType.PARALLEL_SPLIT)
        abstract_nodes = sum(1 for n in self.nodes if n.is_abstract())
        
        # 分支因子
        branch_nodes = [n for n in self.nodes if n.type == NodeType.BRANCH]
        branch_factor = (
            sum(len(n.conditions) for n in branch_nodes) / len(branch_nodes)
            if branch_nodes else 0
        )
        
        # 最大深度
        max_depth = self._calculate_max_depth()
        
        # 綜合複雜度評分
        score = (
            cyclomatic * 10 +
            max_iterations * 15 +
            interaction_count * 20 +
            parallel_branches * 5 +
            abstract_nodes * 25 +  # 抽象節點增加不確定性
            max_depth * 3
        )
        
        # 複雜度等級
        if score <= 20:
            level = ComplexityLevel.TRIVIAL
        elif score <= 40:
            level = ComplexityLevel.SIMPLE
        elif score <= 60:
            level = ComplexityLevel.MODERATE
        elif score <= 80:
            level = ComplexityLevel.COMPLEX
        else:
            level = ComplexityLevel.VERY_COMPLEX
        
        self._metrics = GraphMetrics(
            node_count=N,
            edge_count=E,
            cyclomatic_complexity=cyclomatic,
            max_depth=max_depth,
            branch_factor=branch_factor,
            max_iterations=max_iterations,
            interaction_count=interaction_count,
            parallel_branches=parallel_branches,
            abstract_nodes=abstract_nodes,
            complexity_score=score,
            complexity_level=level,
        )
        
        return self._metrics
    
    def _calculate_max_depth(self) -> int:
        """計算最大深度（BFS）"""
        start = self.get_start_node()
        if not start:
            return 0
        
        visited = set()
        max_depth = 0
        
        def dfs(node_id: str, depth: int):
            nonlocal max_depth
            if node_id in visited:
                return
            visited.add(node_id)
            max_depth = max(max_depth, depth)
            
            for successor in self.get_successors(node_id):
                dfs(successor, depth + 1)
            
            visited.remove(node_id)
        
        dfs(start.id, 0)
        return max_depth
    
    def validate(self) -> tuple[bool, list[str]]:
        """驗證圖的結構"""
        errors = []
        
        # 檢查 start 節點
        start_nodes = [n for n in self.nodes if n.type == NodeType.START]
        if len(start_nodes) == 0:
            errors.append("Graph must have a start node")
        elif len(start_nodes) > 1:
            errors.append("Graph must have exactly one start node")
        
        # 檢查 end 節點
        end_nodes = [n for n in self.nodes if n.type == NodeType.END]
        if len(end_nodes) == 0:
            errors.append("Graph must have at least one end node")
        
        # 檢查邊的節點是否存在
        node_ids = set(n.id for n in self.nodes)
        for edge in self.edges:
            if edge.from_node not in node_ids:
                errors.append(f"Edge references non-existent node: {edge.from_node}")
            if edge.to_node not in node_ids:
                errors.append(f"Edge references non-existent node: {edge.to_node}")
        
        # 檢查 branch 節點是否有條件
        for node in self.nodes:
            if node.type == NodeType.BRANCH and not node.conditions:
                errors.append(f"Branch node {node.id} must have conditions")
        
        # 檢查 skill 節點是否有 skill_id
        for node in self.nodes:
            if node.type == NodeType.SKILL and not node.skill_id:
                errors.append(f"Skill node {node.id} must have skill_id")
        
        # 檢查抽象節點是否有 implementations
        for node in self.nodes:
            if node.type == NodeType.ABSTRACT and not node.implementations:
                errors.append(f"Abstract node {node.id} must have implementations")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            "id": self.id,
            "version": self.version,
            "name": self.name,
            "description": self.description,
            "nodes": [self._node_to_dict(n) for n in self.nodes],
            "edges": [self._edge_to_dict(e) for e in self.edges],
            "fallback_strategy": self.fallback_strategy,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
        }
    
    def _node_to_dict(self, node: GraphNode) -> dict:
        """節點轉字典"""
        d = {
            "id": node.id,
            "type": node.type.value,
        }
        if node.skill_id:
            d["skill_id"] = node.skill_id
        if node.contract:
            d["contract"] = {
                "inputs": node.contract.inputs,
                "outputs": node.contract.outputs,
                "capabilities": node.contract.capabilities,
            }
        if node.implementations:
            d["implementations"] = [
                {
                    "id": impl.id,
                    "skill_id": impl.skill_id,
                    "priority": impl.priority,
                    "conditions": impl.conditions,
                    "fallbacks": impl.fallbacks,
                }
                for impl in node.implementations
            ]
        if node.conditions:
            d["conditions"] = [
                {"name": c.name, "expression": c.expression, "target": c.target}
                for c in node.conditions
            ]
        if node.prompt:
            d["prompt"] = node.prompt
        if node.outputs:
            d["outputs"] = node.outputs
        return d
    
    def _edge_to_dict(self, edge: GraphEdge) -> dict:
        """邊轉字典"""
        d = {
            "from": edge.from_node,
            "to": edge.to_node,
            "type": edge.type.value,
        }
        if edge.condition:
            d["condition"] = edge.condition
        if edge.trigger:
            d["trigger"] = edge.trigger
        return d
    
    @classmethod
    def from_dict(cls, data: dict) -> "CapabilityGraph":
        """從字典建立"""
        nodes = [cls._node_from_dict(n) for n in data.get("nodes", [])]
        edges = [cls._edge_from_dict(e) for e in data.get("edges", [])]
        
        return cls(
            id=data["id"],
            version=data.get("version", "1.0"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            nodes=nodes,
            edges=edges,
            fallback_strategy=data.get("fallback_strategy", "retry_then_ask"),
            max_retries=data.get("max_retries", 3),
            retry_delay=data.get("retry_delay", 1.0),
        )
    
    @classmethod
    def _node_from_dict(cls, data: dict) -> GraphNode:
        """從字典建立節點"""
        contract = None
        if "contract" in data:
            contract = NodeContract(
                inputs=data["contract"].get("inputs", []),
                outputs=data["contract"].get("outputs", []),
                capabilities=data["contract"].get("capabilities", []),
            )
        
        implementations = [
            Implementation(
                id=impl["id"],
                skill_id=impl["skill_id"],
                priority=impl.get("priority", 1),
                conditions=impl.get("conditions", []),
                fallbacks=impl.get("fallbacks", []),
            )
            for impl in data.get("implementations", [])
        ]
        
        conditions = [
            BranchCondition(
                name=c["name"],
                expression=c["expression"],
                target=c["target"],
            )
            for c in data.get("conditions", [])
        ]
        
        return GraphNode(
            id=data["id"],
            type=NodeType(data["type"]),
            skill_id=data.get("skill_id"),
            contract=contract,
            implementations=implementations,
            conditions=conditions,
            prompt=data.get("prompt"),
            outputs=data.get("outputs", []),
        )
    
    @classmethod
    def _edge_from_dict(cls, data: dict) -> GraphEdge:
        """從字典建立邊"""
        return GraphEdge(
            from_node=data["from"],
            to_node=data["to"],
            type=EdgeType(data.get("type", "sequence")),
            condition=data.get("condition"),
            trigger=data.get("trigger"),
        )
    
    def to_mermaid(self) -> str:
        """轉換為 Mermaid 格式"""
        lines = ["graph TD"]
        
        # 節點樣式
        shape_map = {
            NodeType.START: ("((", "))"),
            NodeType.END: ("((", "))"),
            NodeType.BRANCH: ("{", "}"),
            NodeType.MERGE: ("[[", "]]"),
            NodeType.ABSTRACT: ("{{", "}}"),  # 六角形
            NodeType.CONFIRM: ("[/", "/]"),
            NodeType.SELECT: ("[/", "/]"),
            NodeType.INPUT: ("[/", "/]"),
        }
        default_shape = ("[", "]")
        
        for node in self.nodes:
            shape = shape_map.get(node.type, default_shape)
            label = node.skill_id or node.id
            lines.append(f"    {node.id}{shape[0]}{label}{shape[1]}")
        
        # 邊樣式
        arrow_map = {
            EdgeType.SEQUENCE: "-->",
            EdgeType.CONDITIONAL: "-.->",
            EdgeType.ITERATION: "==>",
            EdgeType.PARALLEL: "-->",
            EdgeType.FALLBACK: "-. fallback .->",
        }
        
        for edge in self.edges:
            arrow = arrow_map.get(edge.type, "-->")
            label = f"|{edge.condition}|" if edge.condition else ""
            lines.append(f"    {edge.from_node} {arrow}{label} {edge.to_node}")
        
        return "\n".join(lines)
