"""
Capability Engine 測試
展示自適應圖執行引擎的使用
"""

import asyncio
from capability_engine.graph import (
    CapabilityGraph, GraphNode, GraphEdge,
    NodeType, EdgeType, NodeContract, Implementation, BranchCondition
)
from capability_engine.adaptive import AdaptiveGraphEngine, SkillExecutor, InteractionHandler
from capability_engine.fallback import create_standard_fallback_chain


# ═══════════════════════════════════════════════════════════════════
# Mock 實現
# ═══════════════════════════════════════════════════════════════════

class MockSkillExecutor:
    """模擬的 Skill 執行器"""
    
    def __init__(self):
        self.available_skills = {
            "pdf-reader", "docx-reader", "web-reader",
            "text-reader", "ocr-reader", "note-writer",
        }
        self.execution_log = []
    
    async def execute(self, skill_id: str, inputs: dict, context: dict) -> dict:
        """執行 Skill"""
        self.execution_log.append({
            "skill_id": skill_id,
            "inputs": inputs,
            "context": context,
        })
        
        print(f"  🔧 執行 Skill: {skill_id}")
        
        # 模擬執行
        await asyncio.sleep(0.1)
        
        # 模擬 PDF 讀取失敗（測試 Fallback）
        if skill_id == "pdf-reader" and inputs.get("input_path", "").endswith(".corrupted.pdf"):
            raise ValueError("PDF 檔案損壞，無法解析")
        
        return {
            "content": f"Content from {skill_id}",
            "metadata": {"skill": skill_id},
        }
    
    def is_available(self, skill_id: str) -> bool:
        return skill_id in self.available_skills


class MockInteractionHandler:
    """模擬的互動處理器"""
    
    def __init__(self, auto_responses: dict = None):
        self.auto_responses = auto_responses or {}
        self.interaction_log = []
    
    async def confirm(self, prompt: str) -> bool:
        self.interaction_log.append(("confirm", prompt))
        print(f"  ❓ 確認: {prompt}")
        return self.auto_responses.get(prompt, True)
    
    async def select(self, prompt: str, options: list) -> str:
        self.interaction_log.append(("select", prompt, options))
        print(f"  📋 選擇: {prompt} -> {options}")
        return self.auto_responses.get(prompt, options[0])
    
    async def input(self, prompt: str) -> str:
        self.interaction_log.append(("input", prompt))
        print(f"  ✏️ 輸入: {prompt}")
        return self.auto_responses.get(prompt, "user_input")


# ═══════════════════════════════════════════════════════════════════
# 測試案例
# ═══════════════════════════════════════════════════════════════════

def create_simple_graph() -> CapabilityGraph:
    """建立簡單的線性圖"""
    return CapabilityGraph(
        id="simple-test",
        version="1.0",
        name="簡單測試",
        nodes=[
            GraphNode(id="start", type=NodeType.START),
            GraphNode(
                id="read", 
                type=NodeType.SKILL, 
                skill_id="pdf-reader",
                outputs=["content"],
            ),
            GraphNode(
                id="write",
                type=NodeType.SKILL,
                skill_id="note-writer",
                outputs=["note"],
            ),
            GraphNode(id="end", type=NodeType.END),
        ],
        edges=[
            GraphEdge(from_node="start", to_node="read"),
            GraphEdge(from_node="read", to_node="write"),
            GraphEdge(from_node="write", to_node="end"),
        ],
    )


def create_abstract_node_graph() -> CapabilityGraph:
    """建立包含抽象節點的圖"""
    return CapabilityGraph(
        id="abstract-test",
        version="1.0",
        name="抽象節點測試",
        nodes=[
            GraphNode(id="start", type=NodeType.START),
            GraphNode(
                id="read_document",
                type=NodeType.ABSTRACT,
                contract=NodeContract(
                    inputs=["input_path"],
                    outputs=["content"],
                    capabilities=["read_text"],
                ),
                implementations=[
                    Implementation(
                        id="pdf",
                        skill_id="pdf-reader",
                        priority=1,
                        conditions=["*.pdf"],
                        fallbacks=["ocr-reader"],
                    ),
                    Implementation(
                        id="docx",
                        skill_id="docx-reader",
                        priority=2,
                        conditions=["*.docx"],
                    ),
                    Implementation(
                        id="web",
                        skill_id="web-reader",
                        priority=3,
                        conditions=["http*"],
                    ),
                    Implementation(
                        id="default",
                        skill_id="text-reader",
                        priority=99,
                        conditions=["default"],
                    ),
                ],
                resolution_strategy="auto_detect",
                outputs=["content"],
            ),
            GraphNode(
                id="write",
                type=NodeType.SKILL,
                skill_id="note-writer",
            ),
            GraphNode(id="end", type=NodeType.END),
        ],
        edges=[
            GraphEdge(from_node="start", to_node="read_document"),
            GraphEdge(from_node="read_document", to_node="write"),
            GraphEdge(from_node="write", to_node="end"),
        ],
    )


def create_branch_graph() -> CapabilityGraph:
    """建立包含分支的圖"""
    return CapabilityGraph(
        id="branch-test",
        version="1.0",
        name="分支測試",
        nodes=[
            GraphNode(id="start", type=NodeType.START),
            GraphNode(
                id="check_type",
                type=NodeType.BRANCH,
                conditions=[
                    BranchCondition(name="is_pdf", expression="file_type == 'pdf'", target="read_pdf"),
                    BranchCondition(name="is_web", expression="file_type == 'web'", target="read_web"),
                    BranchCondition(name="default", expression="True", target="read_text"),
                ],
            ),
            GraphNode(id="read_pdf", type=NodeType.SKILL, skill_id="pdf-reader"),
            GraphNode(id="read_web", type=NodeType.SKILL, skill_id="web-reader"),
            GraphNode(id="read_text", type=NodeType.SKILL, skill_id="text-reader"),
            GraphNode(id="merge", type=NodeType.MERGE),
            GraphNode(id="write", type=NodeType.SKILL, skill_id="note-writer"),
            GraphNode(id="end", type=NodeType.END),
        ],
        edges=[
            GraphEdge(from_node="start", to_node="check_type"),
            GraphEdge(from_node="read_pdf", to_node="merge"),
            GraphEdge(from_node="read_web", to_node="merge"),
            GraphEdge(from_node="read_text", to_node="merge"),
            GraphEdge(from_node="merge", to_node="write"),
            GraphEdge(from_node="write", to_node="end"),
        ],
    )


# ═══════════════════════════════════════════════════════════════════
# 測試執行
# ═══════════════════════════════════════════════════════════════════

async def test_simple_graph():
    """測試簡單圖"""
    print("\n" + "=" * 60)
    print("測試 1: 簡單線性圖")
    print("=" * 60)
    
    graph = create_simple_graph()
    executor = MockSkillExecutor()
    
    engine = AdaptiveGraphEngine(graph, executor)
    
    trace = await engine.execute({"input_path": "test.pdf"})
    
    print(f"\n✅ 執行完成!")
    print(f"   路徑: {' -> '.join(trace.path)}")
    print(f"   執行節點數: {trace.executed_nodes}")
    print(f"   耗時: {trace.duration:.2f}s")


async def test_abstract_node_graph():
    """測試抽象節點圖"""
    print("\n" + "=" * 60)
    print("測試 2: 抽象節點圖 (PDF)")
    print("=" * 60)
    
    graph = create_abstract_node_graph()
    executor = MockSkillExecutor()
    
    engine = AdaptiveGraphEngine(graph, executor)
    
    # 測試 PDF
    trace = await engine.execute({"input_path": "document.pdf"})
    
    print(f"\n✅ 執行完成!")
    print(f"   路徑: {' -> '.join(trace.path)}")
    print(f"   選擇的 Skill: {[s.skill_id for s in trace.steps if s.skill_id]}")
    
    # 測試 DOCX
    print("\n" + "-" * 40)
    print("測試 2b: 抽象節點圖 (DOCX)")
    print("-" * 40)
    
    engine2 = AdaptiveGraphEngine(graph, MockSkillExecutor())
    trace2 = await engine2.execute({"input_path": "document.docx"})
    
    print(f"\n✅ 執行完成!")
    print(f"   選擇的 Skill: {[s.skill_id for s in trace2.steps if s.skill_id]}")
    
    # 測試 URL
    print("\n" + "-" * 40)
    print("測試 2c: 抽象節點圖 (URL)")
    print("-" * 40)
    
    engine3 = AdaptiveGraphEngine(graph, MockSkillExecutor())
    trace3 = await engine3.execute({"input_path": "https://example.com/article"})
    
    print(f"\n✅ 執行完成!")
    print(f"   選擇的 Skill: {[s.skill_id for s in trace3.steps if s.skill_id]}")


async def test_branch_graph():
    """測試分支圖"""
    print("\n" + "=" * 60)
    print("測試 3: 分支圖")
    print("=" * 60)
    
    graph = create_branch_graph()
    executor = MockSkillExecutor()
    
    engine = AdaptiveGraphEngine(graph, executor)
    
    # 測試 PDF 分支
    trace = await engine.execute({"file_type": "pdf"})
    
    print(f"\n✅ 執行完成!")
    print(f"   路徑: {' -> '.join(trace.path)}")
    
    # 測試 Web 分支
    print("\n" + "-" * 40)
    print("測試 3b: Web 分支")
    print("-" * 40)
    
    engine2 = AdaptiveGraphEngine(graph, MockSkillExecutor())
    trace2 = await engine2.execute({"file_type": "web"})
    
    print(f"\n✅ 執行完成!")
    print(f"   路徑: {' -> '.join(trace2.path)}")


async def test_metrics():
    """測試複雜度指標"""
    print("\n" + "=" * 60)
    print("測試 4: 複雜度指標")
    print("=" * 60)
    
    graphs = [
        ("簡單圖", create_simple_graph()),
        ("抽象節點圖", create_abstract_node_graph()),
        ("分支圖", create_branch_graph()),
    ]
    
    for name, graph in graphs:
        metrics = graph.calculate_metrics()
        print(f"\n📊 {name}:")
        print(f"   節點數: {metrics.node_count}")
        print(f"   邊數: {metrics.edge_count}")
        print(f"   環路複雜度: {metrics.cyclomatic_complexity}")
        print(f"   抽象節點: {metrics.abstract_nodes}")
        print(f"   複雜度分數: {metrics.complexity_score}")
        print(f"   複雜度等級: {metrics.complexity_level.value}")


async def test_mermaid():
    """測試 Mermaid 輸出"""
    print("\n" + "=" * 60)
    print("測試 5: Mermaid 輸出")
    print("=" * 60)
    
    graph = create_abstract_node_graph()
    mermaid = graph.to_mermaid()
    
    print("\n```mermaid")
    print(mermaid)
    print("```")


# ═══════════════════════════════════════════════════════════════════
# 主程式
# ═══════════════════════════════════════════════════════════════════

async def main():
    """執行所有測試"""
    print("🚀 Capability Engine 測試")
    print("=" * 60)
    
    await test_simple_graph()
    await test_abstract_node_graph()
    await test_branch_graph()
    await test_metrics()
    await test_mermaid()
    
    print("\n" + "=" * 60)
    print("✅ 所有測試完成!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
