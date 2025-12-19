#!/usr/bin/env python3
"""
Capability Manager CLI - 能力管理器命令列工具

用法:
    python cp.py write_report "AI 在醫療的應用"
    python cp.py project_check
    python cp.py deploy
    python cp.py cleanup
    python cp.py clear  # 清除當前工作流程
    python cp.py list   # 列出所有可用工作流程
"""

import sys
import os
import yaml
from pathlib import Path
from datetime import datetime

# 專案根目錄
PROJECT_ROOT = Path(__file__).parent.parent.parent
AGENTS_MD = PROJECT_ROOT / "AGENTS.md"
WORKFLOWS_DIR = Path(__file__).parent.parent / "workflows"

# 工作流程區塊標記
WORKFLOW_START = "<!-- ACTIVE_WORKFLOW_START -->"
WORKFLOW_END = "<!-- ACTIVE_WORKFLOW_END -->"


def load_workflow(workflow_name: str) -> dict:
    """載入工作流程定義"""
    workflow_file = WORKFLOWS_DIR / f"{workflow_name}.yaml"
    if not workflow_file.exists():
        raise FileNotFoundError(f"找不到工作流程: {workflow_file}")
    
    with open(workflow_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def generate_workflow_content(workflow: dict, topic: str = "") -> str:
    """生成工作流程內容"""
    wf = workflow.get('workflow', workflow)
    
    content = f"""**狀態**: 🔄 執行中 - {wf['id']}

**工作流程**: {wf['name']}
**說明**: {wf['description']}
**啟動時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    if topic:
        content += f"**主題/參數**: {topic}\n"
    
    content += """
### 📋 執行步驟

請依序執行以下步驟，完成後將 `[ ]` 改為 `[x]`：

"""
    
    for step in wf['steps']:
        skill_path = f".claude/skills/{step['skill']}/SKILL.md"
        content += f"""- [ ] **Step {step['step']}: {step['name']}** (`{step['skill']}`)
  - 📖 技能文件: `{skill_path}`
  - 📝 說明: {step['description']}
  
"""
    
    content += """### 🎯 當前進度

請開始執行 **Step 1**，完成後更新上方的 checkbox。

### 📌 完成後

所有步驟完成後，請執行: `python .claude/capability-manager/cp.py clear`
"""
    
    return content


def generate_idle_content() -> str:
    """生成待命狀態內容"""
    return """**狀態**: ⏸️ 待命中 (無啟用的工作流程)

### 可用指令

在終端機執行以下指令來啟動工作流程：

```bash
# 撰寫報告
python .claude/capability-manager/cp.py write_report "報告主題"

# 檢查專案
python .claude/capability-manager/cp.py project_check

# 部署專案
python .claude/capability-manager/cp.py deploy

# 清理專案
python .claude/capability-manager/cp.py cleanup

# 列出所有工作流程
python .claude/capability-manager/cp.py list
```

啟動後，請依照下方顯示的步驟依序執行各個 Skill。"""


def update_agents_md(new_content: str) -> None:
    """更新 AGENTS.md 中的工作流程區塊"""
    with open(AGENTS_MD, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到標記位置
    start_idx = content.find(WORKFLOW_START)
    end_idx = content.find(WORKFLOW_END)
    
    if start_idx == -1 or end_idx == -1:
        print("❌ 錯誤: 找不到工作流程區塊標記")
        print(f"   請確認 AGENTS.md 中有 {WORKFLOW_START} 和 {WORKFLOW_END}")
        sys.exit(1)
    
    # 替換內容
    new_agents = (
        content[:start_idx + len(WORKFLOW_START)] +
        "\n" + new_content + "\n" +
        content[end_idx:]
    )
    
    with open(AGENTS_MD, 'w', encoding='utf-8') as f:
        f.write(new_agents)


def cmd_activate(workflow_name: str, topic: str = "") -> None:
    """啟動工作流程"""
    try:
        workflow = load_workflow(workflow_name)
        content = generate_workflow_content(workflow, topic)
        update_agents_md(content)
        
        wf = workflow.get('workflow', workflow)
        print(f"✅ 已啟動工作流程: {wf['name']}")
        print(f"📁 AGENTS.md 已更新")
        print(f"\n請開啟 Copilot Chat，它會讀取 AGENTS.md 並依序執行步驟。")
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)


def cmd_clear() -> None:
    """清除工作流程"""
    content = generate_idle_content()
    update_agents_md(content)
    print("✅ 已清除工作流程，狀態回到待命中")


def cmd_list() -> None:
    """列出所有可用工作流程"""
    print("📋 可用的工作流程:\n")
    
    for yaml_file in WORKFLOWS_DIR.glob("*.yaml"):
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                wf = yaml.safe_load(f)
                wf = wf.get('workflow', wf)
                
            steps = " → ".join([s['name'] for s in wf['steps']])
            print(f"  {wf['id']}")
            print(f"    名稱: {wf['name']}")
            print(f"    說明: {wf['description']}")
            print(f"    步驟: {steps}")
            print()
        except Exception as e:
            print(f"  {yaml_file.stem} (讀取錯誤: {e})")


def cmd_help() -> None:
    """顯示幫助"""
    print(__doc__)
    print("\n可用指令:")
    print("  write_report [主題]  - 啟動撰寫報告工作流程")
    print("  project_check        - 啟動專案檢查工作流程")
    print("  deploy               - 啟動部署工作流程")
    print("  cleanup              - 啟動清理工作流程")
    print("  clear                - 清除當前工作流程")
    print("  list                 - 列出所有可用工作流程")
    print("  help                 - 顯示此幫助訊息")


def main():
    if len(sys.argv) < 2:
        cmd_help()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == "help" or command == "-h" or command == "--help":
        cmd_help()
    elif command == "clear":
        cmd_clear()
    elif command == "list":
        cmd_list()
    elif command in ["write_report", "project_check", "deploy", "cleanup"]:
        topic = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        cmd_activate(command, topic)
    else:
        print(f"❌ 未知指令: {command}")
        print("   使用 'python cp.py help' 查看可用指令")
        sys.exit(1)


if __name__ == "__main__":
    main()
