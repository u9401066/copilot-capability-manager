"""
Domain - Value Objects - Contract
領域層 - 值物件 - 節點契約
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class NodeContract:
    """
    節點契約（值物件 - 不可變）
    定義抽象節點的輸入輸出規格
    """
    inputs: tuple[str, ...] = field(default_factory=tuple)
    outputs: tuple[str, ...] = field(default_factory=tuple)
    capabilities: tuple[str, ...] = field(default_factory=tuple)
    
    @classmethod
    def create(
        cls,
        inputs: list[str] | None = None,
        outputs: list[str] | None = None,
        capabilities: list[str] | None = None,
    ) -> "NodeContract":
        return cls(
            inputs=tuple(inputs or []),
            outputs=tuple(outputs or []),
            capabilities=tuple(capabilities or []),
        )


@dataclass(frozen=True)
class Implementation:
    """
    具體實現（值物件 - 不可變）
    定義抽象節點的一個具體實現
    """
    id: str
    skill_id: str
    priority: int = 1
    conditions: tuple[str, ...] = field(default_factory=tuple)
    fallbacks: tuple[str, ...] = field(default_factory=tuple)
    
    @classmethod
    def create(
        cls,
        id: str,
        skill_id: str,
        priority: int = 1,
        conditions: list[str] | None = None,
        fallbacks: list[str] | None = None,
    ) -> "Implementation":
        return cls(
            id=id,
            skill_id=skill_id,
            priority=priority,
            conditions=tuple(conditions or []),
            fallbacks=tuple(fallbacks or []),
        )


@dataclass(frozen=True)
class BranchCondition:
    """
    分支條件（值物件 - 不可變）
    """
    name: str
    expression: str
    target: str
