"""
Capability Engine - DDD Architecture
能力引擎 - 領域驅動設計架構

目錄結構：
├── domain/              # 領域層
│   ├── value_objects/   # 值物件（不可變）
│   ├── entities/        # 實體（有生命週期）
│   └── services/        # 領域服務
├── application/         # 應用層
│   ├── use_cases/       # 用例
│   └── services/        # 應用服務
├── infrastructure/      # 基礎設施層
│   ├── mcp/             # MCP Server
│   └── prompt/          # Prompt 生成器
└── presentation/        # 呈現層（TypeScript Extension）

與 VS Code Copilot 的整合方式：

1. MCP Server (推薦)
   - Copilot 原生支援 MCP 協議
   - 透過 tools/call 調用能力引擎
   - 完整的雙向通信

2. Prompt Injection
   - 動態生成 .prompt.md 檔案
   - 透過 /cp.xxx 指令觸發
   - 適合簡單的能力

3. Chat Participant (進階)
   - 註冊 @capability 參與者
   - 完整的對話控制
   - 需要 Extension 支援
"""

# === 舊版相容匯出 (Legacy) ===
from .graph import CapabilityGraph as LegacyCapabilityGraph
from .graph import GraphNode as LegacyGraphNode
from .graph import GraphEdge as LegacyGraphEdge
from .adaptive import AdaptiveGraphEngine
from .resolver import NodeResolver, AbstractNodeResolver
from .fallback import FallbackChain, FallbackStrategy

# === DDD 架構匯出 ===

# Domain Layer
from .domain import (
    # Value Objects
    NodeType,
    EdgeType,
    ExecutionStatus,
    ComplexityMetrics,
    ComplexityLevel,
    NodeContract,
    Implementation,
    BranchCondition,
    # Entities
    GraphNode,
    GraphEdge,
    CapabilityGraph,
)

# Application Layer
from .application import (
    # Use Cases
    ExecuteCapabilityUseCase,
    ExecutionTrace,
    ExecutionStep,
    SkillExecutor,
    InteractionHandler,
    # Services
    NodeResolverService,
    GraphValidatorService,
    SkillRegistry,
)

# Infrastructure Layer
from .infrastructure import (
    # MCP
    CapabilityMCPServer,
    run_mcp_server,
    # Prompt
    PromptGenerator,
    PromptInjector,
    PromptTemplate,
)

__all__ = [
    # Legacy (for backward compatibility)
    "LegacyCapabilityGraph",
    "LegacyGraphNode",
    "LegacyGraphEdge",
    "AdaptiveGraphEngine",
    "NodeResolver",
    "AbstractNodeResolver",
    "FallbackChain",
    "FallbackStrategy",
    # Domain - Value Objects
    "NodeType",
    "EdgeType",
    "ExecutionStatus",
    "ComplexityMetrics",
    "ComplexityLevel",
    "NodeContract",
    "Implementation",
    "BranchCondition",
    # Domain - Entities
    "GraphNode",
    "GraphEdge",
    "CapabilityGraph",
    # Application - Use Cases
    "ExecuteCapabilityUseCase",
    "ExecutionTrace",
    "ExecutionStep",
    "SkillExecutor",
    "InteractionHandler",
    # Application - Services
    "NodeResolverService",
    "GraphValidatorService",
    "SkillRegistry",
    # Infrastructure - MCP
    "CapabilityMCPServer",
    "run_mcp_server",
    # Infrastructure - Prompt
    "PromptGenerator",
    "PromptInjector",
    "PromptTemplate",
]

__version__ = "1.0.0"
