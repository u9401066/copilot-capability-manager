"""
Infrastructure - MCP Server
基礎設施層 - MCP 伺服器

這是讓 VS Code Copilot 能調用能力引擎的關鍵整合點。
MCP (Model Context Protocol) 是 Copilot 支援的標準協議。
"""

import asyncio
import json
import sys
from typing import Any
from dataclasses import dataclass

# MCP Server 的核心協議實現
# 參考: https://modelcontextprotocol.io/


@dataclass
class MCPTool:
    """MCP 工具定義"""
    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass
class MCPResource:
    """MCP 資源定義"""
    uri: str
    name: str
    mime_type: str


class CapabilityMCPServer:
    """
    能力引擎 MCP 伺服器
    
    提供以下 MCP Tools 給 Copilot：
    
    1. execute_capability - 執行能力圖
    2. resolve_abstract_node - 解析抽象節點
    3. validate_graph - 驗證圖結構
    4. get_complexity_metrics - 取得複雜度
    5. list_capabilities - 列出所有能力
    6. get_capability_status - 取得執行狀態
    """
    
    def __init__(self, capabilities_dir: str = ".claude/capabilities"):
        self.capabilities_dir = capabilities_dir
        self._running_capabilities: dict[str, Any] = {}
        
    def get_tools(self) -> list[MCPTool]:
        """回傳可用的 MCP Tools"""
        return [
            MCPTool(
                name="execute_capability",
                description="執行指定的能力圖，會自動解析抽象節點、處理分支和回退",
                input_schema={
                    "type": "object",
                    "properties": {
                        "capability_id": {
                            "type": "string",
                            "description": "能力 ID (例如: write-report, git-commit)"
                        },
                        "inputs": {
                            "type": "object",
                            "description": "執行輸入參數"
                        },
                        "options": {
                            "type": "object",
                            "properties": {
                                "auto_resolve": {"type": "boolean", "default": True},
                                "skip_confirmation": {"type": "boolean", "default": False},
                            }
                        }
                    },
                    "required": ["capability_id"]
                }
            ),
            MCPTool(
                name="resolve_abstract_node",
                description="解析抽象節點到具體實現",
                input_schema={
                    "type": "object",
                    "properties": {
                        "contract": {
                            "type": "object",
                            "properties": {
                                "inputs": {"type": "array", "items": {"type": "string"}},
                                "outputs": {"type": "array", "items": {"type": "string"}},
                                "capabilities": {"type": "array", "items": {"type": "string"}},
                            },
                            "description": "節點的契約要求"
                        },
                        "context": {
                            "type": "object",
                            "description": "當前上下文（用於條件判斷）"
                        }
                    },
                    "required": ["contract"]
                }
            ),
            MCPTool(
                name="validate_graph",
                description="驗證能力圖的結構正確性",
                input_schema={
                    "type": "object",
                    "properties": {
                        "graph": {
                            "type": "object",
                            "description": "能力圖 JSON 定義"
                        }
                    },
                    "required": ["graph"]
                }
            ),
            MCPTool(
                name="get_complexity_metrics",
                description="計算能力圖的複雜度指標",
                input_schema={
                    "type": "object",
                    "properties": {
                        "capability_id": {
                            "type": "string",
                            "description": "能力 ID"
                        }
                    },
                    "required": ["capability_id"]
                }
            ),
            MCPTool(
                name="list_capabilities",
                description="列出所有可用的能力",
                input_schema={
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "過濾類別 (例如: report, git, code)"
                        }
                    }
                }
            ),
            MCPTool(
                name="get_capability_status",
                description="取得能力執行狀態（用於長時間執行的能力）",
                input_schema={
                    "type": "object",
                    "properties": {
                        "execution_id": {
                            "type": "string",
                            "description": "執行 ID"
                        }
                    },
                    "required": ["execution_id"]
                }
            ),
        ]
    
    def get_resources(self) -> list[MCPResource]:
        """回傳可用的 MCP Resources"""
        return [
            MCPResource(
                uri="capability://registry",
                name="Capability Registry",
                mime_type="application/json"
            ),
            MCPResource(
                uri="capability://skills",
                name="Available Skills",
                mime_type="application/json"
            ),
        ]
    
    async def handle_tool_call(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """處理 MCP Tool 調用"""
        handlers = {
            "execute_capability": self._execute_capability,
            "resolve_abstract_node": self._resolve_abstract_node,
            "validate_graph": self._validate_graph,
            "get_complexity_metrics": self._get_complexity_metrics,
            "list_capabilities": self._list_capabilities,
            "get_capability_status": self._get_capability_status,
        }
        
        handler = handlers.get(tool_name)
        if not handler:
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            return await handler(arguments)
        except Exception as e:
            return {"error": str(e)}
    
    async def _execute_capability(self, args: dict[str, Any]) -> dict[str, Any]:
        """執行能力"""
        from ..domain.entities import CapabilityGraph
        from ..application.use_cases import ExecuteCapabilityUseCase
        
        capability_id = args["capability_id"]
        inputs = args.get("inputs", {})
        options = args.get("options", {})
        
        # 載入能力圖
        graph = await self._load_capability_graph(capability_id)
        if not graph:
            return {"error": f"Capability not found: {capability_id}"}
        
        # 建立用例並執行
        use_case = ExecuteCapabilityUseCase()
        result = await use_case.execute(graph, inputs, options)
        
        return result
    
    async def _resolve_abstract_node(self, args: dict[str, Any]) -> dict[str, Any]:
        """解析抽象節點"""
        from ..application.services import NodeResolverService
        
        contract = args["contract"]
        context = args.get("context", {})
        
        resolver = NodeResolverService()
        implementation = await resolver.resolve(contract, context)
        
        return {
            "resolved": True,
            "implementation": implementation,
        }
    
    async def _validate_graph(self, args: dict[str, Any]) -> dict[str, Any]:
        """驗證圖結構"""
        from ..domain.entities import CapabilityGraph
        from ..application.services import GraphValidatorService
        
        graph_data = args["graph"]
        graph = CapabilityGraph.from_dict(graph_data)
        
        validator = GraphValidatorService()
        result = validator.validate(graph)
        
        return result
    
    async def _get_complexity_metrics(self, args: dict[str, Any]) -> dict[str, Any]:
        """取得複雜度"""
        capability_id = args["capability_id"]
        
        graph = await self._load_capability_graph(capability_id)
        if not graph:
            return {"error": f"Capability not found: {capability_id}"}
        
        metrics = graph.calculate_complexity()
        
        return {
            "skill_count": metrics.skill_count,
            "abstract_count": metrics.abstract_count,
            "branch_count": metrics.branch_count,
            "loop_count": metrics.loop_count,
            "interaction_count": metrics.interaction_count,
            "max_depth": metrics.max_depth,
            "total": metrics.total,
            "level": metrics.level.value,
        }
    
    async def _list_capabilities(self, args: dict[str, Any]) -> dict[str, Any]:
        """列出所有能力"""
        from pathlib import Path
        import yaml
        
        registry_path = Path(self.capabilities_dir) / "registry.yaml"
        
        if not registry_path.exists():
            return {"capabilities": [], "count": 0}
        
        with open(registry_path) as f:
            registry = yaml.safe_load(f)
        
        capabilities = registry.get("capabilities", [])
        category = args.get("category")
        
        if category:
            capabilities = [c for c in capabilities if c.get("category") == category]
        
        return {
            "capabilities": capabilities,
            "count": len(capabilities),
        }
    
    async def _get_capability_status(self, args: dict[str, Any]) -> dict[str, Any]:
        """取得執行狀態"""
        execution_id = args["execution_id"]
        
        if execution_id not in self._running_capabilities:
            return {"error": f"Execution not found: {execution_id}"}
        
        status = self._running_capabilities[execution_id]
        return status
    
    async def _load_capability_graph(self, capability_id: str):
        """載入能力圖"""
        from pathlib import Path
        import yaml
        from ..domain.entities import CapabilityGraph
        
        graph_path = Path(self.capabilities_dir) / capability_id / "graph.yaml"
        
        if not graph_path.exists():
            return None
        
        with open(graph_path) as f:
            data = yaml.safe_load(f)
        
        return CapabilityGraph.from_dict(data)


# === MCP Server 主程式 ===

async def run_mcp_server():
    """運行 MCP Server (stdio 模式)"""
    server = CapabilityMCPServer()
    
    while True:
        try:
            # 從 stdin 讀取 JSON-RPC 請求
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            # 處理請求
            if method == "tools/list":
                result = {
                    "tools": [
                        {
                            "name": t.name,
                            "description": t.description,
                            "inputSchema": t.input_schema,
                        }
                        for t in server.get_tools()
                    ]
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                result = await server.handle_tool_call(tool_name, arguments)
            elif method == "resources/list":
                result = {
                    "resources": [
                        {
                            "uri": r.uri,
                            "name": r.name,
                            "mimeType": r.mime_type,
                        }
                        for r in server.get_resources()
                    ]
                }
            else:
                result = {"error": f"Unknown method: {method}"}
            
            # 發送回應
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result,
            }
            print(json.dumps(response), flush=True)
            
        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)},
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    asyncio.run(run_mcp_server())
