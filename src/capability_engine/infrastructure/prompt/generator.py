"""
Infrastructure - Prompt Generator
基礎設施層 - Prompt 動態生成器

這是另一種讓 Copilot 能使用能力引擎的方式：
動態生成 .prompt.md 檔案，讓 Copilot 的 /xxx 指令能觸發能力。
"""

from pathlib import Path
from typing import Any
from dataclasses import dataclass


@dataclass
class PromptTemplate:
    """Prompt 模板"""
    id: str
    title: str
    description: str
    mode: str  # ask, edit, agent
    tools: list[str]
    steps: list[str]


class PromptGenerator:
    """
    Prompt 生成器
    
    根據能力圖動態生成 .prompt.md 檔案
    """
    
    def __init__(self, prompts_dir: str = ".github/prompts"):
        self.prompts_dir = Path(prompts_dir)
    
    def generate_from_capability(self, capability_id: str, graph_data: dict[str, Any]) -> str:
        """
        從能力圖生成 Prompt 檔案內容
        
        Args:
            capability_id: 能力 ID
            graph_data: 能力圖資料
        
        Returns:
            Prompt 檔案內容
        """
        name = graph_data.get("name", capability_id)
        description = graph_data.get("description", "")
        nodes = graph_data.get("nodes", [])
        
        # 收集所有 skill 節點
        skills = [n for n in nodes if n.get("type") == "skill"]
        
        # 收集所有互動節點
        interactions = [n for n in nodes if n.get("type", "").startswith("interaction.")]
        
        # 生成步驟
        steps = self._generate_steps(nodes, graph_data.get("edges", []))
        
        # 組裝 Prompt
        lines = [
            f"---",
            f"mode: agent",
            f"description: {description}",
            f"tools:",
        ]
        
        # 添加需要的工具
        tools = self._determine_tools(skills)
        for tool in tools:
            lines.append(f"  - {tool}")
        
        lines.extend([
            f"---",
            f"",
            f"# {name}",
            f"",
            f"{description}",
            f"",
            f"## 執行步驟",
            f"",
        ])
        
        for i, step in enumerate(steps, 1):
            lines.append(f"{i}. {step}")
        
        # 如果有互動節點，添加確認點
        if interactions:
            lines.extend([
                f"",
                f"## 確認點",
                f"",
            ])
            for interaction in interactions:
                prompt = interaction.get("prompt", "請確認")
                lines.append(f"- {prompt}")
        
        # 添加能力引用
        lines.extend([
            f"",
            f"## 技能參考",
            f"",
            f"請參考以下技能文件執行：",
            f"",
        ])
        
        for skill in skills:
            skill_id = skill.get("skill_id", skill.get("id"))
            lines.append(f"- `.claude/skills/{skill_id}/SKILL.md`")
        
        return "\n".join(lines)
    
    def _generate_steps(self, nodes: list[dict], edges: list[dict]) -> list[str]:
        """從節點和邊生成執行步驟"""
        steps = []
        
        # 建立鄰接表
        adj: dict[str, list[str]] = {}
        for edge in edges:
            source = edge["source"]
            target = edge["target"]
            if source not in adj:
                adj[source] = []
            adj[source].append(target)
        
        # 找起點
        targets = {e["target"] for e in edges}
        start_nodes = [n["id"] for n in nodes if n["id"] not in targets or n.get("type") == "control.start"]
        
        if not start_nodes:
            return ["執行能力"]
        
        # BFS 遍歷生成步驟
        visited = set()
        queue = list(start_nodes)
        
        while queue:
            node_id = queue.pop(0)
            if node_id in visited:
                continue
            visited.add(node_id)
            
            # 找節點資料
            node = next((n for n in nodes if n["id"] == node_id), None)
            if not node:
                continue
            
            # 根據類型生成步驟
            node_type = node.get("type", "")
            
            if node_type == "skill":
                skill_id = node.get("skill_id", node_id)
                steps.append(f"執行技能 `{skill_id}`")
            elif node_type == "abstract":
                contract = node.get("contract", {})
                caps = contract.get("capabilities", [])
                if caps:
                    steps.append(f"解析並執行：{', '.join(caps)}")
            elif node_type == "control.branch":
                conditions = node.get("conditions", [])
                if conditions:
                    steps.append(f"根據條件分支處理")
            elif node_type.startswith("interaction."):
                prompt = node.get("prompt", "等待用戶輸入")
                steps.append(f"確認：{prompt}")
            
            # 加入後繼
            for next_id in adj.get(node_id, []):
                if next_id not in visited:
                    queue.append(next_id)
        
        return steps if steps else ["執行能力"]
    
    def _determine_tools(self, skills: list[dict]) -> list[str]:
        """根據技能判斷需要的工具"""
        tools = set()
        
        for skill in skills:
            skill_id = skill.get("skill_id", "")
            
            # 根據技能類型推斷工具
            if "literature" in skill_id or "search" in skill_id:
                tools.add("mcp_pubmed_search_search_literature")
            if "zotero" in skill_id:
                tools.add("mcp_zotero_keeper_search_items")
            if "pdf" in skill_id or "read" in skill_id:
                tools.add("read_file")
            if "write" in skill_id or "note" in skill_id:
                tools.add("create_file")
            if "git" in skill_id:
                tools.add("run_in_terminal")
            if "memory" in skill_id:
                tools.add("memory")
        
        # 基本工具
        tools.add("read_file")
        tools.add("semantic_search")
        
        return sorted(list(tools))
    
    def save_prompt(self, capability_id: str, content: str) -> Path:
        """儲存 Prompt 檔案"""
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = self.prompts_dir / f"cp.{capability_id}.prompt.md"
        file_path.write_text(content, encoding="utf-8")
        
        return file_path
    
    def generate_and_save(self, capability_id: str, graph_data: dict[str, Any]) -> Path:
        """生成並儲存 Prompt"""
        content = self.generate_from_capability(capability_id, graph_data)
        return self.save_prompt(capability_id, content)


class PromptInjector:
    """
    Prompt 注入器
    
    在 Copilot 會話中動態注入能力上下文
    """
    
    def __init__(self):
        self.context_stack: list[dict[str, Any]] = []
    
    def inject_capability_context(self, capability_id: str, graph_data: dict[str, Any]) -> str:
        """
        生成要注入到 Copilot 的上下文文字
        
        這段文字會透過 system prompt 或 copilot-instructions.md 注入
        """
        name = graph_data.get("name", capability_id)
        description = graph_data.get("description", "")
        
        context = f"""
## 當前執行能力：{name}

{description}

### 執行流程

```mermaid
{self._generate_mermaid(graph_data)}
```

### 當前狀態

- 能力 ID: {capability_id}
- 狀態: 執行中
- 下一步: 請按照上述流程執行

### 注意事項

1. 每完成一個步驟，更新 Memory Bank
2. 遇到分支時，根據條件選擇正確路徑
3. 遇到確認點時，等待用戶輸入
"""
        return context.strip()
    
    def _generate_mermaid(self, graph_data: dict[str, Any]) -> str:
        """生成 Mermaid 圖"""
        lines = ["graph TD"]
        
        for node in graph_data.get("nodes", []):
            node_id = node["id"]
            label = node.get("skill_id", node_id)
            node_type = node.get("type", "")
            
            if node_type == "control.start":
                lines.append(f"    {node_id}(([{label}]))")
            elif node_type == "control.end":
                lines.append(f"    {node_id}(([{label}]))")
            elif node_type == "skill":
                lines.append(f"    {node_id}[{label}]")
            elif node_type == "abstract":
                lines.append(f"    {node_id}[/{label}/]")
            elif node_type == "control.branch":
                lines.append(f"    {node_id}{{{{{label}}}}}")
            else:
                lines.append(f"    {node_id}[{label}]")
        
        for edge in graph_data.get("edges", []):
            source = edge["source"]
            target = edge["target"]
            label = edge.get("label", "")
            
            if label:
                lines.append(f"    {source} -->|{label}| {target}")
            else:
                lines.append(f"    {source} --> {target}")
        
        return "\n".join(lines)
