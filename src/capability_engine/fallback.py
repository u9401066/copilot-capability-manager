"""
Fallback Chain - 失敗回退機制
處理執行失敗時的自動重試與替代方案
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Awaitable
import asyncio
import time


# ═══════════════════════════════════════════════════════════════════
# 錯誤類型
# ═══════════════════════════════════════════════════════════════════

class ErrorType(Enum):
    """錯誤類型"""
    FILE_NOT_FOUND = "FileNotFound"
    PARSE_ERROR = "ParseError"
    PERMISSION_DENIED = "PermissionDenied"
    TIMEOUT = "Timeout"
    NETWORK_ERROR = "NetworkError"
    VALIDATION_ERROR = "ValidationError"
    SKILL_NOT_FOUND = "SkillNotFound"
    UNKNOWN = "Unknown"


@dataclass
class ExecutionError:
    """執行錯誤"""
    type: ErrorType
    message: str
    node_id: str
    skill_id: str | None = None
    original_exception: Exception | None = None
    timestamp: float = field(default_factory=time.time)
    
    @classmethod
    def from_exception(
        cls, 
        e: Exception, 
        node_id: str, 
        skill_id: str | None = None
    ) -> "ExecutionError":
        """從異常建立錯誤"""
        error_type = cls._classify_exception(e)
        return cls(
            type=error_type,
            message=str(e),
            node_id=node_id,
            skill_id=skill_id,
            original_exception=e,
        )
    
    @staticmethod
    def _classify_exception(e: Exception) -> ErrorType:
        """分類異常"""
        name = type(e).__name__.lower()
        msg = str(e).lower()
        
        if "not found" in msg or "no such file" in msg:
            return ErrorType.FILE_NOT_FOUND
        if "parse" in name or "decode" in name or "json" in name:
            return ErrorType.PARSE_ERROR
        if "permission" in msg or "access denied" in msg:
            return ErrorType.PERMISSION_DENIED
        if "timeout" in name or "timeout" in msg:
            return ErrorType.TIMEOUT
        if "connection" in msg or "network" in msg:
            return ErrorType.NETWORK_ERROR
        if "validation" in name or "invalid" in msg:
            return ErrorType.VALIDATION_ERROR
        
        return ErrorType.UNKNOWN


# ═══════════════════════════════════════════════════════════════════
# Fallback 策略
# ═══════════════════════════════════════════════════════════════════

class FallbackStrategy(Enum):
    """Fallback 策略"""
    RETRY = "retry"              # 重試當前
    NEXT_IMPLEMENTATION = "next" # 嘗試下一個實現
    ASK_USER = "ask_user"        # 請求用戶協助
    SKIP = "skip"                # 跳過此步驟
    ABORT = "abort"              # 終止執行


@dataclass
class FallbackRule:
    """Fallback 規則"""
    trigger: str  # 觸發條件，如 "error.type == 'ParseError'"
    strategy: FallbackStrategy
    max_retries: int = 3
    retry_delay: float = 1.0  # 秒
    next_skill: str | None = None  # NEXT_IMPLEMENTATION 策略專用
    message: str | None = None     # ASK_USER 策略專用
    
    def matches(self, error: ExecutionError, retry_count: int) -> bool:
        """檢查是否匹配此規則"""
        trigger = self.trigger.lower()
        
        # 特殊觸發條件
        if trigger == "default":
            return True
        if trigger == "any":
            return True
        if trigger.startswith("retries >="):
            threshold = int(trigger.split(">=")[1].strip())
            return retry_count >= threshold
        
        # 錯誤類型匹配
        if f"'{error.type.value.lower()}'" in trigger.lower():
            return True
        if error.type.value.lower() in trigger.lower():
            return True
        
        return False


# ═══════════════════════════════════════════════════════════════════
# Fallback 鏈
# ═══════════════════════════════════════════════════════════════════

@dataclass
class FallbackResult:
    """Fallback 執行結果"""
    success: bool
    strategy_used: FallbackStrategy
    retries: int = 0
    final_skill: str | None = None
    user_response: Any = None
    error: ExecutionError | None = None


class FallbackChain:
    """
    Fallback 鏈 - 管理失敗回退邏輯
    
    執行順序：
    1. 嘗試執行
    2. 失敗 → 匹配 FallbackRule
    3. 根據策略處理
    4. 重複直到成功或無法恢復
    """
    
    def __init__(
        self,
        rules: list[FallbackRule] | None = None,
        max_total_retries: int = 10,
        global_timeout: float = 300.0,  # 5 分鐘
    ):
        self.rules = rules or self._default_rules()
        self.max_total_retries = max_total_retries
        self.global_timeout = global_timeout
        
        # 回調
        self._on_retry: Callable[[ExecutionError, int], None] | None = None
        self._on_fallback: Callable[[FallbackStrategy, str], None] | None = None
        self._ask_user: Callable[[str], Awaitable[Any]] | None = None
    
    def _default_rules(self) -> list[FallbackRule]:
        """預設的 Fallback 規則"""
        return [
            # 網路錯誤：重試
            FallbackRule(
                trigger="error.type == 'NetworkError'",
                strategy=FallbackStrategy.RETRY,
                max_retries=3,
                retry_delay=2.0,
            ),
            # 超時：重試一次
            FallbackRule(
                trigger="error.type == 'Timeout'",
                strategy=FallbackStrategy.RETRY,
                max_retries=1,
                retry_delay=0,
            ),
            # 解析錯誤：嘗試下一個實現
            FallbackRule(
                trigger="error.type == 'ParseError'",
                strategy=FallbackStrategy.NEXT_IMPLEMENTATION,
            ),
            # 找不到檔案：詢問用戶
            FallbackRule(
                trigger="error.type == 'FileNotFound'",
                strategy=FallbackStrategy.ASK_USER,
                message="找不到檔案，請提供正確的路徑",
            ),
            # 重試過多：詢問用戶
            FallbackRule(
                trigger="retries >= 3",
                strategy=FallbackStrategy.ASK_USER,
                message="多次嘗試失敗，需要您的協助",
            ),
            # 預設：終止
            FallbackRule(
                trigger="default",
                strategy=FallbackStrategy.ABORT,
            ),
        ]
    
    def on_retry(self, callback: Callable[[ExecutionError, int], None]):
        """設定重試回調"""
        self._on_retry = callback
    
    def on_fallback(self, callback: Callable[[FallbackStrategy, str], None]):
        """設定 Fallback 回調"""
        self._on_fallback = callback
    
    def set_ask_user(self, callback: Callable[[str], Awaitable[Any]]):
        """設定用戶詢問回調"""
        self._ask_user = callback
    
    async def execute_with_fallback(
        self,
        func: Callable[..., Awaitable[Any]],
        *args,
        node_id: str = "unknown",
        skill_id: str | None = None,
        available_implementations: list[str] | None = None,
        **kwargs,
    ) -> FallbackResult:
        """
        帶 Fallback 的執行
        
        Args:
            func: 要執行的異步函數
            *args: 函數參數
            node_id: 節點 ID（用於錯誤報告）
            skill_id: 當前 skill ID
            available_implementations: 可用的替代實現
            **kwargs: 函數關鍵字參數
        
        Returns:
            FallbackResult: 執行結果
        """
        start_time = time.time()
        total_retries = 0
        current_skill = skill_id
        impl_index = 0
        implementations = available_implementations or []
        
        while True:
            # 檢查全局超時
            if time.time() - start_time > self.global_timeout:
                return FallbackResult(
                    success=False,
                    strategy_used=FallbackStrategy.ABORT,
                    retries=total_retries,
                    error=ExecutionError(
                        type=ErrorType.TIMEOUT,
                        message="Global timeout exceeded",
                        node_id=node_id,
                        skill_id=current_skill,
                    ),
                )
            
            # 檢查重試上限
            if total_retries >= self.max_total_retries:
                return FallbackResult(
                    success=False,
                    strategy_used=FallbackStrategy.ABORT,
                    retries=total_retries,
                    error=ExecutionError(
                        type=ErrorType.UNKNOWN,
                        message="Max retries exceeded",
                        node_id=node_id,
                        skill_id=current_skill,
                    ),
                )
            
            # 嘗試執行
            try:
                result = await func(*args, **kwargs)
                return FallbackResult(
                    success=True,
                    strategy_used=FallbackStrategy.RETRY if total_retries > 0 else FallbackStrategy.SKIP,
                    retries=total_retries,
                    final_skill=current_skill,
                )
            except Exception as e:
                error = ExecutionError.from_exception(e, node_id, current_skill)
                total_retries += 1
                
                # 找匹配的規則
                rule = self._find_matching_rule(error, total_retries)
                
                if self._on_fallback:
                    self._on_fallback(rule.strategy, f"{error.type.value}: {error.message}")
                
                # 執行策略
                if rule.strategy == FallbackStrategy.RETRY:
                    if self._on_retry:
                        self._on_retry(error, total_retries)
                    
                    if total_retries <= rule.max_retries:
                        await asyncio.sleep(rule.retry_delay)
                        continue
                    else:
                        # 重試次數超過，找下一個規則
                        continue
                
                elif rule.strategy == FallbackStrategy.NEXT_IMPLEMENTATION:
                    impl_index += 1
                    if impl_index < len(implementations):
                        current_skill = implementations[impl_index]
                        # TODO: 更新 func 使用新的 skill
                        continue
                    else:
                        # 沒有更多實現，嘗試下一個規則
                        continue
                
                elif rule.strategy == FallbackStrategy.ASK_USER:
                    if self._ask_user:
                        message = rule.message or f"執行失敗：{error.message}"
                        user_response = await self._ask_user(message)
                        return FallbackResult(
                            success=True,  # 用戶處理了
                            strategy_used=FallbackStrategy.ASK_USER,
                            retries=total_retries,
                            user_response=user_response,
                        )
                    else:
                        # 沒有用戶回調，終止
                        return FallbackResult(
                            success=False,
                            strategy_used=FallbackStrategy.ABORT,
                            retries=total_retries,
                            error=error,
                        )
                
                elif rule.strategy == FallbackStrategy.SKIP:
                    return FallbackResult(
                        success=True,  # 跳過視為成功
                        strategy_used=FallbackStrategy.SKIP,
                        retries=total_retries,
                    )
                
                else:  # ABORT
                    return FallbackResult(
                        success=False,
                        strategy_used=FallbackStrategy.ABORT,
                        retries=total_retries,
                        error=error,
                    )
    
    def _find_matching_rule(self, error: ExecutionError, retry_count: int) -> FallbackRule:
        """找到匹配的規則"""
        for rule in self.rules:
            if rule.matches(error, retry_count):
                return rule
        
        # 返回預設規則（終止）
        return FallbackRule(trigger="default", strategy=FallbackStrategy.ABORT)


# ═══════════════════════════════════════════════════════════════════
# 預設 Fallback 鏈
# ═══════════════════════════════════════════════════════════════════

def create_standard_fallback_chain() -> FallbackChain:
    """建立標準的 Fallback 鏈"""
    return FallbackChain(
        rules=[
            # 網路問題：指數退避重試
            FallbackRule(
                trigger="error.type == 'NetworkError'",
                strategy=FallbackStrategy.RETRY,
                max_retries=5,
                retry_delay=2.0,
            ),
            # 超時：立即重試一次
            FallbackRule(
                trigger="error.type == 'Timeout'",
                strategy=FallbackStrategy.RETRY,
                max_retries=2,
                retry_delay=0.5,
            ),
            # 解析錯誤：嘗試替代實現
            FallbackRule(
                trigger="error.type == 'ParseError'",
                strategy=FallbackStrategy.NEXT_IMPLEMENTATION,
            ),
            # 找不到檔案：問用戶
            FallbackRule(
                trigger="error.type == 'FileNotFound'",
                strategy=FallbackStrategy.ASK_USER,
                message="找不到指定的檔案，請確認路徑是否正確",
            ),
            # 權限問題：問用戶
            FallbackRule(
                trigger="error.type == 'PermissionDenied'",
                strategy=FallbackStrategy.ASK_USER,
                message="沒有權限存取此資源，請確認權限設定",
            ),
            # 重試太多次：問用戶
            FallbackRule(
                trigger="retries >= 3",
                strategy=FallbackStrategy.ASK_USER,
                message="多次嘗試失敗，請檢查問題或提供其他選項",
            ),
            # 預設：終止
            FallbackRule(
                trigger="default",
                strategy=FallbackStrategy.ABORT,
            ),
        ],
        max_total_retries=10,
        global_timeout=300.0,
    )


def create_aggressive_fallback_chain() -> FallbackChain:
    """建立積極的 Fallback 鏈（儘量自動處理）"""
    return FallbackChain(
        rules=[
            # 任何錯誤：先重試
            FallbackRule(
                trigger="any",
                strategy=FallbackStrategy.RETRY,
                max_retries=2,
                retry_delay=1.0,
            ),
            # 重試失敗：嘗試替代
            FallbackRule(
                trigger="retries >= 2",
                strategy=FallbackStrategy.NEXT_IMPLEMENTATION,
            ),
            # 沒有替代：跳過
            FallbackRule(
                trigger="retries >= 5",
                strategy=FallbackStrategy.SKIP,
            ),
            # 預設：問用戶
            FallbackRule(
                trigger="default",
                strategy=FallbackStrategy.ASK_USER,
                message="需要您的協助來處理這個問題",
            ),
        ],
        max_total_retries=15,
        global_timeout=600.0,
    )


def create_conservative_fallback_chain() -> FallbackChain:
    """建立保守的 Fallback 鏈（謹慎處理）"""
    return FallbackChain(
        rules=[
            # 只有網路錯誤才重試
            FallbackRule(
                trigger="error.type == 'NetworkError'",
                strategy=FallbackStrategy.RETRY,
                max_retries=3,
                retry_delay=2.0,
            ),
            # 其他錯誤都問用戶
            FallbackRule(
                trigger="default",
                strategy=FallbackStrategy.ASK_USER,
                message="執行過程中發生問題，需要您的確認",
            ),
        ],
        max_total_retries=5,
        global_timeout=180.0,
    )
