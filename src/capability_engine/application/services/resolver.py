"""
Application - Services - Node Resolver
應用層 - 服務 - 節點解析器
"""

from __future__ import annotations
from typing import Any, Protocol, Optional, List, Dict


class SkillRegistry(Protocol):
    """技能註冊表協議"""
    def get_skill(self, skill_id: str) -> Optional[Dict[str, Any]]:
        ...
    
    def find_skills_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        ...


class NodeResolverService:
    """
    節點解析服務
    
    將抽象節點解析為具體的技能實現
    """
    
    def __init__(self, skill_registry: Optional[SkillRegistry] = None):
        self.skill_registry = skill_registry
        
        # 內建的類型偵測規則
        self._type_detectors = {
            ".pdf": "pdf-reader",
            ".docx": "docx-reader",
            ".md": "markdown-reader",
            ".txt": "text-reader",
            ".html": "web-reader",
            "http://": "web-reader",
            "https://": "web-reader",
        }
    
    async def resolve(
        self,
        contract: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        解析抽象節點
        
        Args:
            contract: 節點契約
                - inputs: 輸入類型
                - outputs: 輸出類型
                - capabilities: 需要的能力
            context: 執行上下文
        
        Returns:
            解析結果
                - skill_id: 選中的技能
                - confidence: 信心度
                - reason: 選擇原因
        """
        capabilities = contract.get("capabilities", [])
        inputs = contract.get("inputs", [])
        
        # 1. 嘗試從上下文推斷
        if "input_file" in context:
            file_path = context["input_file"]
            skill_id = self._detect_by_file_type(file_path)
            if skill_id:
                return {
                    "skill_id": skill_id,
                    "confidence": 0.9,
                    "reason": f"Auto-detected from file type: {file_path}",
                }
        
        if "input_url" in context:
            return {
                "skill_id": "web-reader",
                "confidence": 0.95,
                "reason": "URL input detected",
            }
        
        # 2. 從能力要求找匹配的技能
        if capabilities and self.skill_registry:
            for cap in capabilities:
                skills = self.skill_registry.find_skills_by_capability(cap)
                if skills:
                    # 選擇第一個匹配的
                    return {
                        "skill_id": skills[0]["id"],
                        "confidence": 0.8,
                        "reason": f"Matched capability: {cap}",
                    }
        
        # 3. 使用預設
        if "read" in inputs or any("read" in cap for cap in capabilities):
            return {
                "skill_id": "pdf-reader",
                "confidence": 0.5,
                "reason": "Default reader selected",
            }
        
        return {
            "skill_id": None,
            "confidence": 0,
            "reason": "No matching skill found",
        }
    
    def _detect_by_file_type(self, file_path: str) -> Optional[str]:
        """根據檔案類型偵測技能"""
        file_path_lower = file_path.lower()
        
        for pattern, skill_id in self._type_detectors.items():
            if pattern.startswith("."):
                if file_path_lower.endswith(pattern):
                    return skill_id
            else:
                if file_path_lower.startswith(pattern):
                    return skill_id
        
        return None


class GraphValidatorService:
    """
    圖驗證服務
    
    驗證能力圖的結構正確性
    """
    
    def validate(self, graph) -> Dict[str, Any]:
        """
        驗證圖結構
        
        Returns:
            驗證結果
                - valid: 是否有效
                - errors: 錯誤列表
                - warnings: 警告列表
        """
        errors: List[str] = []
        warnings: List[str] = []
        
        # 1. 檢查是否有起始節點
        start_nodes = graph.find_start_nodes()
        if not start_nodes:
            errors.append("Graph has no start node")
        elif len(start_nodes) > 1:
            warnings.append(f"Graph has multiple start nodes: {len(start_nodes)}")
        
        # 2. 檢查是否有結束節點
        end_nodes = graph.find_end_nodes()
        if not end_nodes:
            warnings.append("Graph has no explicit end node")
        
        # 3. 檢查是否有環（排除迴圈節點）
        if graph.has_cycle():
            warnings.append("Graph contains cycles (may be intentional for loops)")
        
        # 4. 檢查孤立節點
        all_nodes = set(n.id for n in graph.nodes())
        connected = set()
        
        for edge in graph.edges():
            connected.add(edge.source)
            connected.add(edge.target)
        
        orphans = all_nodes - connected
        if orphans:
            errors.append(f"Graph has orphan nodes: {orphans}")
        
        # 5. 檢查抽象節點是否有實現
        for node in graph.nodes():
            if node.is_abstract() and not node.implementations:
                warnings.append(f"Abstract node '{node.id}' has no implementations")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }
