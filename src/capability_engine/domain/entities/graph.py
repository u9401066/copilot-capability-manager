"""
Domain - Entities - Capability Graph
領域層 - 實體 - 能力圖（聚合根）
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Iterator

from .node import GraphNode
from .edge import GraphEdge
from ..value_objects import NodeType, ComplexityMetrics, ComplexityLevel


@dataclass
class CapabilityGraph:
    """
    能力圖（聚合根）
    
    聚合根特性：
    - 統一訪問入口
    - 保護內部一致性
    - 定義聚合邊界
    """
    id: str
    name: str
    description: str = ""
    version: str = "1.0.0"
    
    _nodes: dict[str, GraphNode] = field(default_factory=dict)
    _edges: list[GraphEdge] = field(default_factory=list)
    
    # === 節點操作 ===
    
    def add_node(self, node: GraphNode) -> None:
        """添加節點"""
        if node.id in self._nodes:
            raise ValueError(f"Node {node.id} already exists")
        self._nodes[node.id] = node
    
    def get_node(self, node_id: str) -> GraphNode | None:
        """取得節點"""
        return self._nodes.get(node_id)
    
    def remove_node(self, node_id: str) -> None:
        """移除節點（同時移除相關邊）"""
        if node_id not in self._nodes:
            return
        del self._nodes[node_id]
        self._edges = [e for e in self._edges if e.source != node_id and e.target != node_id]
    
    def nodes(self) -> Iterator[GraphNode]:
        """迭代所有節點"""
        return iter(self._nodes.values())
    
    @property
    def node_count(self) -> int:
        return len(self._nodes)
    
    # === 邊操作 ===
    
    def add_edge(self, edge: GraphEdge) -> None:
        """添加邊"""
        if edge.source not in self._nodes:
            raise ValueError(f"Source node {edge.source} not found")
        if edge.target not in self._nodes:
            raise ValueError(f"Target node {edge.target} not found")
        self._edges.append(edge)
    
    def get_edges_from(self, node_id: str) -> list[GraphEdge]:
        """取得從節點出發的所有邊"""
        return [e for e in self._edges if e.source == node_id]
    
    def get_edges_to(self, node_id: str) -> list[GraphEdge]:
        """取得指向節點的所有邊"""
        return [e for e in self._edges if e.target == node_id]
    
    def edges(self) -> Iterator[GraphEdge]:
        """迭代所有邊"""
        return iter(self._edges)
    
    @property
    def edge_count(self) -> int:
        return len(self._edges)
    
    # === 拓撲操作 ===
    
    def find_start_nodes(self) -> list[GraphNode]:
        """找到起始節點（入度為 0 或類型為 START）"""
        targets = {e.target for e in self._edges}
        return [
            node for node in self._nodes.values()
            if node.type == NodeType.START or node.id not in targets
        ]
    
    def find_end_nodes(self) -> list[GraphNode]:
        """找到結束節點（出度為 0 或類型為 END）"""
        sources = {e.source for e in self._edges}
        return [
            node for node in self._nodes.values()
            if node.type == NodeType.END or node.id not in sources
        ]
    
    def get_successors(self, node_id: str) -> list[GraphNode]:
        """取得後繼節點"""
        edges = self.get_edges_from(node_id)
        return [self._nodes[e.target] for e in edges if e.target in self._nodes]
    
    def get_predecessors(self, node_id: str) -> list[GraphNode]:
        """取得前驅節點"""
        edges = self.get_edges_to(node_id)
        return [self._nodes[e.source] for e in edges if e.source in self._nodes]
    
    def has_cycle(self) -> bool:
        """檢測是否有環"""
        visited: set[str] = set()
        rec_stack: set[str] = set()
        
        def dfs(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            
            for edge in self.get_edges_from(node_id):
                if edge.target not in visited:
                    if dfs(edge.target):
                        return True
                elif edge.target in rec_stack:
                    return True
            
            rec_stack.remove(node_id)
            return False
        
        # 允許迴圈節點有環
        for node in self._nodes.values():
            if node.type == NodeType.LOOP:
                continue
            if node.id not in visited:
                if dfs(node.id):
                    return True
        return False
    
    # === 複雜度計算 ===
    
    def calculate_complexity(self) -> ComplexityMetrics:
        """計算圖的複雜度"""
        node_count = len(self._nodes)
        edge_count = len(self._edges)
        
        skill_count = sum(1 for n in self._nodes.values() if n.type == NodeType.SKILL)
        abstract_count = sum(1 for n in self._nodes.values() if n.is_abstract())
        branch_count = sum(1 for n in self._nodes.values() if n.type == NodeType.BRANCH)
        loop_count = sum(1 for n in self._nodes.values() if n.type == NodeType.LOOP)
        interaction_count = sum(1 for n in self._nodes.values() if n.is_interaction())
        parallel_count = sum(1 for n in self._nodes.values() if n.type == NodeType.PARALLEL_SPLIT)
        
        # 計算最大深度
        max_depth = self._calculate_max_depth()
        
        # 計算分支因子
        branch_factor = edge_count / max(node_count, 1)
        
        # 計算 cyclomatic complexity
        cyclomatic = edge_count - node_count + 2
        
        # 計算最大迴圈迭代
        max_iterations = max(
            (n.max_iterations for n in self._nodes.values() if n.type == NodeType.LOOP),
            default=0
        )
        
        return ComplexityMetrics(
            node_count=node_count,
            edge_count=edge_count,
            cyclomatic_complexity=cyclomatic,
            max_depth=max_depth,
            branch_factor=branch_factor,
            max_iterations=max_iterations,
            interaction_count=interaction_count,
            parallel_branches=parallel_count,
            abstract_nodes=abstract_count,
        )
    
    def _calculate_max_depth(self) -> int:
        """計算最大深度"""
        start_nodes = self.find_start_nodes()
        if not start_nodes:
            return 0
        
        max_depth = 0
        visited: dict[str, int] = {}
        
        def dfs(node_id: str, depth: int) -> int:
            if node_id in visited:
                return visited[node_id]
            
            visited[node_id] = depth
            local_max = depth
            
            for edge in self.get_edges_from(node_id):
                local_max = max(local_max, dfs(edge.target, depth + 1))
            
            return local_max
        
        for start in start_nodes:
            max_depth = max(max_depth, dfs(start.id, 1))
        
        return max_depth
    
    # === 序列化 ===
    
    def to_dict(self) -> dict[str, Any]:
        """轉換為字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "nodes": [node.to_dict() for node in self._nodes.values()],
            "edges": [edge.to_dict() for edge in self._edges],
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CapabilityGraph":
        """從字典建立"""
        graph = cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
        )
        
        for node_data in data.get("nodes", []):
            graph.add_node(GraphNode.from_dict(node_data))
        
        for edge_data in data.get("edges", []):
            graph.add_edge(GraphEdge.from_dict(edge_data))
        
        return graph
    
    # === Mermaid 輸出 ===
    
    def to_mermaid(self) -> str:
        """輸出 Mermaid 圖"""
        lines = ["graph TD"]
        
        # 節點樣式
        style_map = {
            NodeType.START: "([{label}])",
            NodeType.END: "([{label}])",
            NodeType.SKILL: "[{label}]",
            NodeType.ABSTRACT: "[/{label}/]",
            NodeType.BRANCH: "{{{label}}}",
            NodeType.LOOP: "(({label}))",
            NodeType.CONFIRM: ">{label}]",
            NodeType.SELECT: ">{label}]",
            NodeType.INPUT: ">{label}]",
        }
        
        for node in self._nodes.values():
            label = node.skill_id or node.id
            style = style_map.get(node.type, "[{label}]")
            lines.append(f"    {node.id}{style.format(label=label)}")
        
        for edge in self._edges:
            if edge.label:
                lines.append(f"    {edge.source} -->|{edge.label}| {edge.target}")
            else:
                lines.append(f"    {edge.source} --> {edge.target}")
        
        return "\n".join(lines)
