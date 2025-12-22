"""
Node Resolver - 節點解析器
處理抽象節點的動態解析與實現選擇
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol
import re
import fnmatch

from .graph import GraphNode, NodeType, Implementation


# ═══════════════════════════════════════════════════════════════════
# 解析上下文
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ResolutionContext:
    """解析上下文 - 用於決定使用哪個具體實現"""
    
    # 輸入資訊
    input_type: str | None = None      # MIME type 或檔案類型
    input_path: str | None = None      # 檔案路徑或 URL
    input_content: bytes | None = None # 原始內容（用於檢測）
    
    # 用戶偏好
    user_preference: str | None = None
    
    # 環境資訊
    available_skills: list[str] = field(default_factory=list)
    
    # 執行歷史
    previous_attempts: list[str] = field(default_factory=list)
    last_error: str | None = None
    
    # 變數
    variables: dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════
# 條件匹配器
# ═══════════════════════════════════════════════════════════════════

class ConditionMatcher:
    """條件匹配器 - 評估實現的條件"""
    
    @staticmethod
    def match(condition: str, context: ResolutionContext) -> bool:
        """
        評估條件是否匹配
        
        支援的條件格式：
        - "*.pdf" - glob 模式匹配路徑
        - "input.type == 'application/pdf'" - 表達式
        - "http*" - URL 模式
        - "default" - 總是匹配
        """
        condition = condition.strip()
        
        # 特殊條件
        if condition == "default":
            return True
        
        # Glob 模式 (檔案擴展名)
        if condition.startswith("*.") and context.input_path:
            return fnmatch.fnmatch(context.input_path.lower(), condition.lower())
        
        # URL 模式
        if condition.startswith("http") and context.input_path:
            return context.input_path.startswith(condition.rstrip("*"))
        
        # 表達式求值
        if "==" in condition or "!=" in condition:
            return ConditionMatcher._evaluate_expression(condition, context)
        
        # MIME type 匹配
        if "/" in condition and context.input_type:
            return fnmatch.fnmatch(context.input_type, condition)
        
        return False
    
    @staticmethod
    def _evaluate_expression(expression: str, context: ResolutionContext) -> bool:
        """評估簡單表達式"""
        # 建立安全的評估環境
        safe_vars = {
            "input_type": context.input_type,
            "input_path": context.input_path,
            "user_preference": context.user_preference,
            "last_error": context.last_error,
            **context.variables,
        }
        
        # 替換變數
        result_expr = expression
        for key, value in safe_vars.items():
            pattern = rf'\b{key}\b'
            if value is None:
                replacement = "None"
            elif isinstance(value, str):
                replacement = f"'{value}'"
            else:
                replacement = str(value)
            result_expr = re.sub(pattern, replacement, result_expr)
        
        # 安全評估
        try:
            # 只允許比較操作
            allowed_ops = {"==", "!=", "in", "not", "and", "or", "True", "False", "None"}
            tokens = re.findall(r"[a-zA-Z_]+|'[^']*'|\"[^\"]*\"", result_expr)
            
            # 簡化版本：直接 eval（生產環境應使用 ast.literal_eval 或自定義解析器）
            return eval(result_expr)
        except Exception:
            return False


# ═══════════════════════════════════════════════════════════════════
# 節點解析器
# ═══════════════════════════════════════════════════════════════════

class NodeResolver(ABC):
    """節點解析器基類"""
    
    @abstractmethod
    def resolve(self, node: GraphNode, context: ResolutionContext) -> Implementation | None:
        """解析抽象節點，返回具體實現"""
        pass
    
    @abstractmethod
    def can_resolve(self, node: GraphNode) -> bool:
        """是否能解析此節點"""
        pass


class AbstractNodeResolver(NodeResolver):
    """
    抽象節點解析器
    根據上下文選擇最佳實現
    """
    
    def __init__(self):
        self.matcher = ConditionMatcher()
        self._type_detectors: dict[str, Callable[[bytes], bool]] = {}
        self._register_default_detectors()
    
    def _register_default_detectors(self):
        """註冊預設的類型檢測器"""
        # PDF 魔數
        self._type_detectors["application/pdf"] = lambda b: b[:4] == b"%PDF"
        
        # DOCX (ZIP-based)
        self._type_detectors["application/vnd.openxmlformats-officedocument.wordprocessingml.document"] = (
            lambda b: b[:4] == b"PK\x03\x04"
        )
        
        # HTML
        self._type_detectors["text/html"] = (
            lambda b: b"<html" in b[:1024].lower() or b"<!doctype html" in b[:1024].lower()
        )
    
    def register_type_detector(self, mime_type: str, detector: Callable[[bytes], bool]):
        """註冊類型檢測器"""
        self._type_detectors[mime_type] = detector
    
    def can_resolve(self, node: GraphNode) -> bool:
        """是否能解析此節點"""
        return node.type == NodeType.ABSTRACT and len(node.implementations) > 0
    
    def resolve(self, node: GraphNode, context: ResolutionContext) -> Implementation | None:
        """
        解析抽象節點
        
        策略：
        1. auto_detect: 自動根據條件選擇
        2. user_select: 讓用戶選擇
        3. priority: 按優先級選擇
        """
        if not self.can_resolve(node):
            return None
        
        # 自動檢測輸入類型
        if context.input_content and not context.input_type:
            context.input_type = self._detect_type(context.input_content)
        
        strategy = node.resolution_strategy
        
        if strategy == "priority":
            return self._resolve_by_priority(node, context)
        elif strategy == "user_select":
            return self._resolve_by_user(node, context)
        else:  # auto_detect
            return self._resolve_by_condition(node, context)
    
    def _detect_type(self, content: bytes) -> str | None:
        """檢測內容類型"""
        for mime_type, detector in self._type_detectors.items():
            try:
                if detector(content):
                    return mime_type
            except Exception:
                continue
        return None
    
    def _resolve_by_condition(
        self, node: GraphNode, context: ResolutionContext
    ) -> Implementation | None:
        """根據條件自動選擇"""
        # 排除已嘗試過的實現
        candidates = [
            impl for impl in node.implementations
            if impl.skill_id not in context.previous_attempts
        ]
        
        # 按優先級排序
        candidates.sort(key=lambda x: x.priority)
        
        # 找第一個匹配的
        for impl in candidates:
            if self._match_implementation(impl, context):
                return impl
        
        # 沒有匹配的，返回優先級最高的
        return candidates[0] if candidates else None
    
    def _resolve_by_priority(
        self, node: GraphNode, context: ResolutionContext
    ) -> Implementation | None:
        """按優先級選擇"""
        candidates = [
            impl for impl in node.implementations
            if impl.skill_id not in context.previous_attempts
        ]
        
        if not candidates:
            return None
        
        candidates.sort(key=lambda x: x.priority)
        return candidates[0]
    
    def _resolve_by_user(
        self, node: GraphNode, context: ResolutionContext
    ) -> Implementation | None:
        """讓用戶選擇（返回 None 表示需要互動）"""
        # 如果用戶已經指定偏好
        if context.user_preference:
            for impl in node.implementations:
                if impl.id == context.user_preference:
                    return impl
        
        # 需要用戶選擇
        return None
    
    def _match_implementation(
        self, impl: Implementation, context: ResolutionContext
    ) -> bool:
        """檢查實現是否匹配上下文"""
        if not impl.conditions:
            return True  # 沒有條件，總是匹配
        
        # 任一條件匹配即可
        return any(
            self.matcher.match(cond, context)
            for cond in impl.conditions
        )
    
    def get_available_implementations(
        self, node: GraphNode, context: ResolutionContext
    ) -> list[Implementation]:
        """取得所有可用的實現（用於用戶選擇）"""
        if not self.can_resolve(node):
            return []
        
        return [
            impl for impl in node.implementations
            if impl.skill_id in context.available_skills or not context.available_skills
        ]


# ═══════════════════════════════════════════════════════════════════
# 類型檢測工具
# ═══════════════════════════════════════════════════════════════════

class TypeDetector:
    """輸入類型檢測器"""
    
    # 副檔名對應 MIME type
    EXTENSION_MAP = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".doc": "application/msword",
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".html": "text/html",
        ".htm": "text/html",
        ".json": "application/json",
        ".xml": "application/xml",
        ".csv": "text/csv",
    }
    
    @classmethod
    def from_path(cls, path: str) -> str | None:
        """從路徑推斷類型"""
        if not path:
            return None
        
        # URL
        if path.startswith("http://") or path.startswith("https://"):
            return "text/html"  # 預設網頁
        
        # 檔案擴展名
        path_lower = path.lower()
        for ext, mime_type in cls.EXTENSION_MAP.items():
            if path_lower.endswith(ext):
                return mime_type
        
        return None
    
    @classmethod
    def from_content(cls, content: bytes) -> str | None:
        """從內容魔數推斷類型"""
        if not content:
            return None
        
        # PDF
        if content[:4] == b"%PDF":
            return "application/pdf"
        
        # ZIP-based (DOCX, XLSX, PPTX)
        if content[:4] == b"PK\x03\x04":
            return "application/zip"  # 需要進一步檢查
        
        # HTML
        lower_start = content[:1024].lower()
        if b"<html" in lower_start or b"<!doctype html" in lower_start:
            return "text/html"
        
        # XML
        if content[:5] == b"<?xml":
            return "application/xml"
        
        # JSON
        stripped = content.lstrip()
        if stripped and stripped[0:1] in (b"{", b"["):
            return "application/json"
        
        return None
