# 強制執行機制分析

> 如何確保 Skill/Capability 概念被正確執行？不只依賴 Agent 自願遵守。

## 📊 注入點分析

| 注入點 | 可靠度 | Hard Code 程度 | 說明 |
|--------|--------|----------------|------|
| `.github/copilot-instructions.md` | ⭐⭐⭐⭐⭐ | 中 | **Copilot 必讀**，但仍是文字指令 |
| VS Code Extension | ⭐⭐⭐⭐⭐ | 高 | **程式碼強制**，UI 流程控制 |
| JSON Schema 驗證 | ⭐⭐⭐⭐ | 高 | **格式強制**，但不檢查邏輯 |
| MCP Server | ⭐⭐⭐⭐⭐ | 最高 | **程式碼執行**，完全控制 |
| Git Pre-commit Hook | ⭐⭐⭐ | 高 | 提交時檢查，但不即時 |
| AGENTS.md | ⭐⭐ | 低 | Agent 可能忽略 |
| SKILL.md | ⭐⭐ | 低 | 依賴 Agent 主動讀取 |

---

## 🔧 方案 1: VS Code Extension（已有基礎）

### 可強制的部分

```typescript
// extension/src/services/CapabilityService.ts

async createCapability(capability: Capability): Promise<void> {
    // ✅ 強制檢查：必須有 checkpoint 邏輯
    if (capability.requiresCheckpoint && !capability.checkpointConfig) {
        throw new Error('長任務 Capability 必須設定 Checkpoint');
    }
    
    // ✅ 強制檢查：至少包含一個 Skill
    if (capability.skills.length === 0) {
        throw new Error('Capability 必須包含至少一個 Skill');
    }
    
    // ✅ 強制檢查：迴圈 Skill 必須有終止條件
    for (const skill of capability.skills) {
        if (skill.loop && !skill.loopCondition) {
            throw new Error(`Skill "${skill.id}" 設為迴圈但缺少終止條件`);
        }
    }
}
```

### UI 強制欄位

```typescript
// Capability Builder Webview
interface CapabilityFormFields {
    id: string;           // 必填
    name: string;         // 必填
    skills: SkillRef[];   // 必填，至少一個
    
    // 長任務設定
    isLongRunning: boolean;
    checkpointConfig?: {
        saveFrequency: 'per-item' | 'per-phase';
        resumeStrategy: 'continue' | 'restart';
    };
}
```

---

## 🔧 方案 2: JSON Schema 驗證

### Skill Schema

```yaml
# .vscode/schemas/skill.schema.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["name", "description"],
  "properties": {
    "name": { "type": "string", "minLength": 1 },
    "description": { 
      "type": "string",
      "pattern": ".*LOAD THIS SKILL WHEN.*"  # 強制包含觸發條件
    },
    "category": {
      "enum": ["research", "documentation", "git", "maintenance", "architecture", "quality", "other"]
    }
  }
}
```

### VS Code 設定（自動驗證）

```json
// .vscode/settings.json
{
  "yaml.schemas": {
    ".vscode/schemas/skill.schema.json": ".claude/skills/*/SKILL.md"
  }
}
```

---

## 🔧 方案 3: 自定義 MCP Server（最強）

### 架構

```
┌─────────────────────────────────────────────────────┐
│  Copilot Agent                                      │
│    ↓ 調用 MCP Tool                                  │
├─────────────────────────────────────────────────────┤
│  capability-manager MCP Server                      │
│    ├─ mcp_ccm_create_capability()                   │
│    ├─ mcp_ccm_start_capability()                    │
│    ├─ mcp_ccm_checkpoint_save()                     │
│    ├─ mcp_ccm_checkpoint_load()                     │
│    └─ mcp_ccm_list_skills()                         │
├─────────────────────────────────────────────────────┤
│  程式碼強制邏輯                                      │
│    - 驗證格式                                        │
│    - 檢查依賴                                        │
│    - 管理 Checkpoint                                │
│    - 追蹤執行狀態                                    │
└─────────────────────────────────────────────────────┘
```

### MCP Server 實作

```python
# mcp-capability-manager/server.py

from mcp.server import Server
from mcp.types import Tool

server = Server("capability-manager")

@server.tool("ccm_start_capability")
async def start_capability(capability_id: str, params: dict) -> dict:
    """啟動 Capability，強制建立 Checkpoint"""
    
    # ✅ 強制檢查：Capability 存在
    cap = load_capability(capability_id)
    if not cap:
        raise ValueError(f"Capability '{capability_id}' 不存在")
    
    # ✅ 強制建立 Checkpoint
    checkpoint = {
        "capability": capability_id,
        "status": "in-progress",
        "startedAt": datetime.now().isoformat(),
        "progress": {"total": 0, "completed": 0},
        "params": params
    }
    save_checkpoint(capability_id, checkpoint)
    
    return {
        "message": f"已啟動 {capability_id}",
        "checkpoint_id": checkpoint["id"],
        "next_skill": cap["skills"][0]
    }

@server.tool("ccm_complete_item")
async def complete_item(checkpoint_id: str, item_id: str, result: dict) -> dict:
    """完成一個項目，強制更新 Checkpoint"""
    
    checkpoint = load_checkpoint(checkpoint_id)
    checkpoint["completedItems"].append(item_id)
    checkpoint["progress"]["completed"] += 1
    checkpoint["lastUpdated"] = datetime.now().isoformat()
    
    save_checkpoint(checkpoint_id, checkpoint)
    
    # 計算下一步
    if checkpoint["progress"]["completed"] >= checkpoint["progress"]["total"]:
        return {"status": "completed", "next": "synthesis"}
    else:
        return {"status": "continue", "next_item": get_next_item(checkpoint)}
```

---

## 🔧 方案 4: copilot-instructions.md 強化

目前最實際的方案 - 在 Copilot 必讀的檔案中加入強制檢查指令：

```markdown
## ⚠️ 強制執行規則

### Capability 執行規則（必須遵守）

1. **啟動 Capability 時**：
   - 必須建立 `memory-bank/checkpoints/{id}-{timestamp}.json`
   - 必須記錄初始狀態

2. **每完成一個項目時**：
   - 必須更新 checkpoint 的 `completedItems`
   - 必須更新 `progress.completed`

3. **迴圈執行時**：
   - 每次迴圈必須檢查 checkpoint
   - 必須有明確的終止條件

4. **錯誤處理**：
   - 必須記錄錯誤到 checkpoint 的 `errors` 陣列
   - 不可靜默失敗

### 自我檢查清單

執行 Capability 前，回答以下問題：
- [ ] 這是長任務嗎？（需要 checkpoint）
- [ ] 有多個項目要處理嗎？（需要迴圈邏輯）
- [ ] checkpoint 檔案存在嗎？（繼續或新建）
```

---

## 📋 建議實施順序

1. **立即可做**：強化 `copilot-instructions.md`
2. **短期**：完善 VS Code Extension 驗證邏輯
3. **中期**：加入 JSON Schema 驗證
4. **長期**：開發專用 MCP Server

---

## 🤔 Copilot 限制

即使有這些機制，仍有限制：

| 限制 | 影響 | 緩解方案 |
|------|------|----------|
| 無後台執行 | 長任務需分段 | Checkpoint + 用戶觸發繼續 |
| Context 截斷 | 忘記之前做了什麼 | Checkpoint 記錄狀態 |
| 無強制讀取 | Agent 可能跳過文件 | MCP Server 程式控制 |
| 無狀態 API | 每次對話重新開始 | 檔案系統持久化 |

---

*最終結論：MCP Server 是最可靠的 hard code 方案，但開發成本較高。短期內先強化 copilot-instructions.md + VS Code Extension。*
