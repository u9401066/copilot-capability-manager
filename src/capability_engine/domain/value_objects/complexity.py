"""
Domain - Value Objects - Complexity Metrics
領域層 - 值物件 - 複雜度指標
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class ComplexityLevel(Enum):
    """複雜度等級"""
    TRIVIAL = "trivial"
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"
    
    @classmethod
    def from_score(cls, score: float) -> "ComplexityLevel":
        """根據分數判定等級"""
        if score <= 20:
            return cls.TRIVIAL
        elif score <= 40:
            return cls.SIMPLE
        elif score <= 60:
            return cls.MODERATE
        elif score <= 80:
            return cls.COMPLEX
        else:
            return cls.VERY_COMPLEX


@dataclass(frozen=True)
class ComplexityMetrics:
    """
    複雜度指標（值物件 - 不可變）
    
    計算公式：
    score = cyclomatic * 10 + iterations * 15 + interactions * 20 
            + parallel * 5 + abstract * 25 + depth * 3
    """
    node_count: int
    edge_count: int
    cyclomatic_complexity: int
    max_depth: int
    branch_factor: float
    max_iterations: int
    interaction_count: int
    parallel_branches: int
    abstract_nodes: int
    
    @property
    def complexity_score(self) -> float:
        """計算複雜度分數"""
        return (
            self.cyclomatic_complexity * 10 +
            self.max_iterations * 15 +
            self.interaction_count * 20 +
            self.parallel_branches * 5 +
            self.abstract_nodes * 25 +
            self.max_depth * 3
        )
    
    @property
    def complexity_level(self) -> ComplexityLevel:
        """取得複雜度等級"""
        return ComplexityLevel.from_score(self.complexity_score)
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "cyclomatic_complexity": self.cyclomatic_complexity,
            "max_depth": self.max_depth,
            "branch_factor": self.branch_factor,
            "max_iterations": self.max_iterations,
            "interaction_count": self.interaction_count,
            "parallel_branches": self.parallel_branches,
            "abstract_nodes": self.abstract_nodes,
            "complexity_score": self.complexity_score,
            "complexity_level": self.complexity_level.value,
        }
