"""
DDD Architecture Test
測試 DDD 架構的完整性
"""

import asyncio
import sys
from pathlib import Path

# 確保可以找到模組
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def test_domain_layer():
    """測試 Domain 層"""
    print("=" * 60)
    print("測試 Domain 層")
    print("=" * 60)
    
    from src.capability_engine.domain import (
        NodeType, EdgeType, ExecutionStatus,
        ComplexityMetrics, ComplexityLevel,
        NodeContract, Implementation, BranchCondition,
        GraphNode, GraphEdge, CapabilityGraph,
    )
    
    # 測試 Value Objects
    print("\n1. Value Objects:")
    
    # NodeType
    assert NodeType.SKILL.value == "skill"
    assert NodeType.ABSTRACT.is_abstract()
    assert NodeType.BRANCH.is_control()
    print("   ✅ NodeType")
    
    # NodeContract (不可變)
    contract = NodeContract.create(
        inputs=["pdf", "docx"],
        outputs=["text"],
        capabilities=["read-document"]
    )
    assert "pdf" in contract.inputs
    print("   ✅ NodeContract (immutable)")
    
    # Implementation
    impl = Implementation.create(
        id="pdf-reader-impl",
        skill_id="pdf-reader",
        priority=1,
        conditions=["file_type == 'pdf'"]
    )
    assert impl.skill_id == "pdf-reader"
    print("   ✅ Implementation")
    
    # ComplexityMetrics
    metrics = ComplexityMetrics(
        node_count=10,
        edge_count=12,
        cyclomatic_complexity=4,
        max_depth=4,
        branch_factor=1.2,
        max_iterations=10,
        interaction_count=1,
        parallel_branches=0,
        abstract_nodes=2
    )
    assert metrics.complexity_level in ComplexityLevel
    print("   ✅ ComplexityMetrics")
    
    # 測試 Entities
    print("\n2. Entities:")
    
    # GraphNode
    node = GraphNode(
        id="read-doc",
        type=NodeType.ABSTRACT,
        contract=contract,
        implementations=[impl]
    )
    assert node.is_abstract()
    assert len(node.get_available_implementations()) == 1
    print("   ✅ GraphNode")
    
    # GraphEdge
    edge = GraphEdge(
        source="start",
        target="read-doc",
        type=EdgeType.SEQUENCE
    )
    assert edge.source == "start"
    print("   ✅ GraphEdge")
    
    # CapabilityGraph (聚合根)
    graph = CapabilityGraph(
        id="test-capability",
        name="Test Capability",
        description="A test capability"
    )
    
    # 添加節點
    start = GraphNode(id="start", type=NodeType.START)
    end = GraphNode(id="end", type=NodeType.END)
    
    graph.add_node(start)
    graph.add_node(node)
    graph.add_node(end)
    
    # 添加邊
    graph.add_edge(GraphEdge(source="start", target="read-doc"))
    graph.add_edge(GraphEdge(source="read-doc", target="end"))
    
    assert graph.node_count == 3
    assert graph.edge_count == 2
    
    # 拓撲操作
    start_nodes = graph.find_start_nodes()
    assert len(start_nodes) == 1
    assert start_nodes[0].id == "start"
    
    successors = graph.get_successors("start")
    assert len(successors) == 1
    assert successors[0].id == "read-doc"
    
    print("   ✅ CapabilityGraph (Aggregate Root)")
    
    # 複雜度計算
    complexity = graph.calculate_complexity()
    print(f"   ✅ Complexity: {complexity.complexity_level.value} (score={complexity.complexity_score})")
    
    # Mermaid 輸出
    mermaid = graph.to_mermaid()
    assert "graph TD" in mermaid
    print("   ✅ Mermaid output")
    
    # 序列化
    data = graph.to_dict()
    restored = CapabilityGraph.from_dict(data)
    assert restored.id == graph.id
    assert restored.node_count == graph.node_count
    print("   ✅ Serialization/Deserialization")
    
    print("\n✅ Domain 層測試通過！")


def test_application_layer():
    """測試 Application 層"""
    print("\n" + "=" * 60)
    print("測試 Application 層")
    print("=" * 60)
    
    from src.capability_engine.application import (
        ExecuteCapabilityUseCase,
        NodeResolverService,
        GraphValidatorService,
    )
    
    # 測試 NodeResolverService
    print("\n1. NodeResolverService:")
    
    resolver = NodeResolverService()
    
    async def test_resolver():
        # 測試檔案類型偵測
        result = await resolver.resolve(
            contract={"capabilities": ["read-document"]},
            context={"input_file": "document.pdf"}
        )
        assert result["skill_id"] == "pdf-reader"
        print(f"   ✅ PDF detection: {result['skill_id']}")
        
        result = await resolver.resolve(
            contract={"capabilities": ["read-document"]},
            context={"input_file": "document.docx"}
        )
        assert result["skill_id"] == "docx-reader"
        print(f"   ✅ DOCX detection: {result['skill_id']}")
        
        result = await resolver.resolve(
            contract={"capabilities": ["read-document"]},
            context={"input_url": "https://example.com"}
        )
        assert result["skill_id"] == "web-reader"
        print(f"   ✅ URL detection: {result['skill_id']}")
    
    asyncio.run(test_resolver())
    
    # 測試 GraphValidatorService
    print("\n2. GraphValidatorService:")
    
    from src.capability_engine.domain import (
        CapabilityGraph, GraphNode, GraphEdge, NodeType
    )
    
    validator = GraphValidatorService()
    
    # 建立有效的圖
    graph = CapabilityGraph(id="valid", name="Valid Graph")
    graph.add_node(GraphNode(id="start", type=NodeType.START))
    graph.add_node(GraphNode(id="skill1", type=NodeType.SKILL, skill_id="test-skill"))
    graph.add_node(GraphNode(id="end", type=NodeType.END))
    graph.add_edge(GraphEdge(source="start", target="skill1"))
    graph.add_edge(GraphEdge(source="skill1", target="end"))
    
    result = validator.validate(graph)
    assert result["valid"]
    print(f"   ✅ Valid graph validation: {result}")
    
    # 建立無效的圖（有孤立節點）
    invalid_graph = CapabilityGraph(id="invalid", name="Invalid Graph")
    invalid_graph.add_node(GraphNode(id="orphan", type=NodeType.SKILL))
    
    result = validator.validate(invalid_graph)
    assert not result["valid"]
    print(f"   ✅ Invalid graph detection: {result['errors']}")
    
    print("\n✅ Application 層測試通過！")


def test_infrastructure_layer():
    """測試 Infrastructure 層"""
    print("\n" + "=" * 60)
    print("測試 Infrastructure 層")
    print("=" * 60)
    
    from src.capability_engine.infrastructure import (
        CapabilityMCPServer,
        PromptGenerator,
        PromptInjector,
    )
    
    # 測試 MCP Server
    print("\n1. MCP Server:")
    
    server = CapabilityMCPServer()
    
    tools = server.get_tools()
    assert len(tools) >= 5
    print(f"   ✅ MCP Tools: {[t.name for t in tools]}")
    
    resources = server.get_resources()
    assert len(resources) >= 1
    print(f"   ✅ MCP Resources: {[r.uri for r in resources]}")
    
    # 測試 Prompt Generator
    print("\n2. Prompt Generator:")
    
    generator = PromptGenerator()
    
    graph_data = {
        "name": "Write Report",
        "description": "撰寫報告的能力",
        "nodes": [
            {"id": "start", "type": "control.start"},
            {"id": "search", "type": "skill", "skill_id": "literature-search"},
            {"id": "read", "type": "abstract", "contract": {"capabilities": ["read-document"]}},
            {"id": "write", "type": "skill", "skill_id": "note-writer"},
            {"id": "end", "type": "control.end"},
        ],
        "edges": [
            {"source": "start", "target": "search"},
            {"source": "search", "target": "read"},
            {"source": "read", "target": "write"},
            {"source": "write", "target": "end"},
        ]
    }
    
    prompt_content = generator.generate_from_capability("write-report", graph_data)
    assert "Write Report" in prompt_content
    assert "literature-search" in prompt_content
    print("   ✅ Prompt generation")
    print("\n   Generated prompt preview:")
    print("   " + "-" * 50)
    for line in prompt_content.split("\n")[:15]:
        print(f"   {line}")
    print("   ...")
    
    # 測試 Prompt Injector
    print("\n3. Prompt Injector:")
    
    injector = PromptInjector()
    context = injector.inject_capability_context("write-report", graph_data)
    assert "write-report" in context
    assert "mermaid" in context.lower() or "graph" in context.lower()
    print("   ✅ Context injection")
    
    print("\n✅ Infrastructure 層測試通過！")


def test_integration():
    """測試整合"""
    print("\n" + "=" * 60)
    print("測試整合（端到端）")
    print("=" * 60)
    
    from src.capability_engine import (
        # Domain
        CapabilityGraph, GraphNode, GraphEdge, NodeType, NodeContract, Implementation,
        # Application
        ExecuteCapabilityUseCase, GraphValidatorService,
        # Infrastructure
        PromptGenerator,
    )
    
    # 1. 建立完整的能力圖
    print("\n1. 建立能力圖:")
    
    graph = CapabilityGraph(
        id="literature-review",
        name="Literature Review",
        description="執行文獻回顧的完整流程"
    )
    
    # 添加節點
    graph.add_node(GraphNode(id="start", type=NodeType.START))
    
    # 抽象節點 - 文獻搜尋
    search_contract = NodeContract.create(
        inputs=["query"],
        outputs=["pmids"],
        capabilities=["search-literature"]
    )
    graph.add_node(GraphNode(
        id="search",
        type=NodeType.ABSTRACT,
        contract=search_contract,
        implementations=[
            Implementation.create(
                id="pubmed-search",
                skill_id="literature-search",
                priority=1
            ),
            Implementation.create(
                id="semantic-search",
                skill_id="semantic-search",
                priority=2
            )
        ]
    ))
    
    # 抽象節點 - 文獻閱讀
    read_contract = NodeContract.create(
        inputs=["document"],
        outputs=["text", "summary"],
        capabilities=["read-document"]
    )
    graph.add_node(GraphNode(
        id="read",
        type=NodeType.ABSTRACT,
        contract=read_contract,
        implementations=[
            Implementation.create(
                id="pdf-impl",
                skill_id="pdf-reader",
                priority=1,
                conditions=["file_type == 'pdf'"]
            ),
            Implementation.create(
                id="web-impl",
                skill_id="web-reader",
                priority=1,
                conditions=["input_type == 'url'"]
            )
        ]
    ))
    
    graph.add_node(GraphNode(
        id="write",
        type=NodeType.SKILL,
        skill_id="note-writer"
    ))
    
    graph.add_node(GraphNode(id="end", type=NodeType.END))
    
    # 添加邊
    graph.add_edge(GraphEdge(source="start", target="search"))
    graph.add_edge(GraphEdge(source="search", target="read"))
    graph.add_edge(GraphEdge(source="read", target="write"))
    graph.add_edge(GraphEdge(source="write", target="end"))
    
    print(f"   ✅ Graph created: {graph.node_count} nodes, {graph.edge_count} edges")
    
    # 2. 驗證圖
    print("\n2. 驗證圖結構:")
    
    validator = GraphValidatorService()
    validation = validator.validate(graph)
    print(f"   Valid: {validation['valid']}")
    print(f"   Errors: {validation['errors']}")
    print(f"   Warnings: {validation['warnings']}")
    
    # 3. 計算複雜度
    print("\n3. 計算複雜度:")
    
    complexity = graph.calculate_complexity()
    print(f"   Level: {complexity.complexity_level.value}")
    print(f"   Nodes: {complexity.node_count}")
    print(f"   Abstract: {complexity.abstract_nodes}")
    print(f"   Depth: {complexity.max_depth}")
    print(f"   Score: {complexity.complexity_score}")
    
    # 4. 生成 Mermaid
    print("\n4. Mermaid 輸出:")
    
    mermaid = graph.to_mermaid()
    print(mermaid)
    
    # 5. 生成 Prompt
    print("\n5. 生成 Prompt:")
    
    generator = PromptGenerator()
    prompt = generator.generate_from_capability("literature-review", graph.to_dict())
    print("   " + "-" * 50)
    for line in prompt.split("\n")[:20]:
        print(f"   {line}")
    print("   ...")
    
    print("\n✅ 整合測試通過！")


def main():
    """主程式"""
    print("\n" + "=" * 60)
    print(" DDD Architecture Test Suite")
    print("=" * 60)
    
    try:
        test_domain_layer()
        test_application_layer()
        test_infrastructure_layer()
        test_integration()
        
        print("\n" + "=" * 60)
        print(" 🎉 所有測試通過！DDD 架構運作正常")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
