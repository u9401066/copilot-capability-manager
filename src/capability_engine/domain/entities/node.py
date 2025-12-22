"""
Domain - Entities - Graph Node
領域層 - 實體 - 圖節點
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from ..value_objects import NodeType, NodeContract, Implementation, BranchCondition


@dataclass
class GraphNode:
    """
    圖節點（實體）
    
    實體特性：
    - 有唯一識別（id）
    - 可變狀態
    - 生命週期追蹤
    """
    id: str
    type: NodeType
    
    # Skill 節點專用
    skill_id: str | None = None
    
    # 抽象節點專用
    contract: NodeContract | None = None
    implementations: list[Implementation] = field(default_factory=list)
    resolution_strategy: str = "auto_detect"
    
    # 控制節點專用
    conditions: list[BranchCondition] = field(default_factory=list)
    max_iterations: int = 10
    
    # 互動節點專用
    prompt: str | None = None
    options: list[str] = field(default_factory=list)
    
    # 通用
    timeout: int | None = None
    outputs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def is_abstract(self) -> bool:
        return self.type == NodeType.ABSTRACT
    
    def is_control(self) -> bool:
        return self.type.is_control()
    
    def is_interaction(self) -> bool:
        return self.type.is_interaction()
    
    def is_executable(self) -> bool:
        """是否可執行（skill 或 abstract）"""
        return self.type in (NodeType.SKILL, NodeType.ABSTRACT)
    
    def get_available_implementations(self) -> list[Implementation]:
        """取得可用的實現（按優先級排序）"""
        return sorted(self.implementations, key=lambda x: x.priority)
    
    def to_dict(self) -> dict[str, Any]:
        """轉換為字典"""
        d: dict[str, Any] = {
            "id": self.id,
            "type": self.type.value,
        }
        if self.skill_id:
            d["skill_id"] = self.skill_id
        if self.contract:
            d["contract"] = {
                "inputs": list(self.contract.inputs),
                "outputs": list(self.contract.outputs),
                "capabilities": list(self.contract.capabilities),
            }
        if self.implementations:
            d["implementations"] = [
                {
                    "id": impl.id,
                    "skill_id": impl.skill_id,
                    "priority": impl.priority,
                    "conditions": list(impl.conditions),
                    "fallbacks": list(impl.fallbacks),
                }
                for impl in self.implementations
            ]
        if self.conditions:
            d["conditions"] = [
                {"name": c.name, "expression": c.expression, "target": c.target}
                for c in self.conditions
            ]
        if self.prompt:
            d["prompt"] = self.prompt
        if self.outputs:
            d["outputs"] = self.outputs
        return d
    
    @classmethod
    def from_dict(cls, data: dict) -> "GraphNode":
        """從字典建立"""
        contract = None
        if "contract" in data:
            contract = NodeContract.create(
                inputs=data["contract"].get("inputs", []),
                outputs=data["contract"].get("outputs", []),
                capabilities=data["contract"].get("capabilities", []),
            )
        
        implementations = [
            Implementation.create(
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
        
        return cls(
            id=data["id"],
            type=NodeType(data["type"]),
            skill_id=data.get("skill_id"),
            contract=contract,
            implementations=implementations,
            conditions=conditions,
            prompt=data.get("prompt"),
            outputs=data.get("outputs", []),
        )
