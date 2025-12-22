"""
Domain - Entities - Graph Edge
領域層 - 實體 - 圖邊
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from ..value_objects import EdgeType


@dataclass
class GraphEdge:
    """
    圖邊（實體）
    
    連接兩個節點的邊
    """
    source: str
    target: str
    type: EdgeType = EdgeType.SEQUENCE
    label: str | None = None
    weight: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def is_conditional(self) -> bool:
        return self.type == EdgeType.CONDITIONAL
    
    def is_optional(self) -> bool:
        return self.type == EdgeType.OPTIONAL
    
    def to_dict(self) -> dict[str, Any]:
        """轉換為字典"""
        d: dict[str, Any] = {
            "source": self.source,
            "target": self.target,
            "type": self.type.value,
        }
        if self.label:
            d["label"] = self.label
        if self.weight != 1:
            d["weight"] = self.weight
        return d
    
    @classmethod
    def from_dict(cls, data: dict) -> "GraphEdge":
        """從字典建立"""
        return cls(
            source=data["source"],
            target=data["target"],
            type=EdgeType(data.get("type", "sequence")),
            label=data.get("label"),
            weight=data.get("weight", 1),
        )
