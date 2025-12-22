"""
Domain - Value Objects - Node Types
領域層 - 值物件 - 節點類型
"""

from enum import Enum


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
    LOOP = "control.loop"  # 迴圈節點
    LOOP_START = "control.loop_start"
    LOOP_END = "control.loop_end"
    PARALLEL_SPLIT = "control.parallel_split"
    PARALLEL_JOIN = "control.parallel_join"
    
    # 互動節點
    CONFIRM = "interaction.confirm"
    SELECT = "interaction.select"
    INPUT = "interaction.input"
    
    def is_control(self) -> bool:
        return self.value.startswith("control.")
    
    def is_interaction(self) -> bool:
        return self.value.startswith("interaction.")
    
    def is_abstract(self) -> bool:
        return self == NodeType.ABSTRACT


class EdgeType(Enum):
    """邊類型"""
    SEQUENCE = "sequence"       # 順序執行
    CONDITIONAL = "conditional" # 條件分支
    ITERATION = "iteration"     # 迴圈
    PARALLEL = "parallel"       # 並行
    FALLBACK = "fallback"       # 失敗回退
    OPTIONAL = "optional"       # 可選路徑


class ExecutionStatus(Enum):
    """執行狀態"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WAITING = "waiting"  # 等待用戶輸入
