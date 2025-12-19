# VS Code Extension 設計文檔

Copilot Capability Manager 擴充套件詳細設計。

## 概述

本擴充套件目標是提供 GUI 介面，讓使用者可以：

1. **視覺化管理 Skills**：透過表單新增、編輯、刪除 Skills
2. **整合 MCP Tools**：在 Skills 中選擇和設定 MCP Tools
3. **組合 Capabilities**：拖拉 Skills 形成自動化工作流程
4. **生成 Prompt Files**：自動匯出 `.prompt.md` 供 Copilot Chat 使用

---

## 擴充套件結構

```
copilot-capability-manager/
├── package.json                 # 擴充套件設定檔
├── src/
│   ├── extension.ts             # 進入點
│   ├── services/
│   │   ├── SkillService.ts      # Skill CRUD 操作
│   │   ├── CapabilityService.ts # Capability 管理
│   │   └── McpService.ts        # MCP Tool 整合
│   ├── providers/
│   │   ├── SkillTreeProvider.ts # Skill 列表 TreeView
│   │   ├── SkillWebviewProvider.ts
│   │   └── CapabilityWebviewProvider.ts
│   ├── commands/
│   │   ├── skillCommands.ts     # Skill 相關指令
│   │   └── capabilityCommands.ts
│   └── types/
│       ├── skill.ts             # Skill 型別定義
│       └── capability.ts        # Capability 型別定義
├── webview-ui/                  # Webview React 應用
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── SkillManager/
│   │   │   │   ├── SkillList.tsx
│   │   │   │   ├── SkillForm.tsx
│   │   │   │   └── McpToolSelector.tsx
│   │   │   └── CapabilityBuilder/
│   │   │       ├── SkillPalette.tsx
│   │   │       ├── WorkflowCanvas.tsx
│   │   │       └── StepConfigPanel.tsx
│   │   └── hooks/
│   │       └── useVscodeApi.ts
│   └── package.json
└── resources/
    └── icons/
```

---

## package.json 設定

```json
{
  "name": "copilot-capability-manager",
  "displayName": "Copilot Capability Manager",
  "description": "視覺化管理 AI Skills 並組合成自動化工作流程",
  "version": "0.2.0",
  "engines": {
    "vscode": "^1.99.0"
  },
  "categories": ["Other"],
  "activationEvents": [
    "onStartupFinished"
  ],
  "main": "./dist/extension.js",
  "contributes": {
    "viewsContainers": {
      "activitybar": [
        {
          "id": "capability-manager",
          "title": "Capability Manager",
          "icon": "resources/icons/logo.svg"
        }
      ]
    },
    "views": {
      "capability-manager": [
        {
          "id": "skillExplorer",
          "name": "Skills",
          "type": "tree"
        },
        {
          "id": "skillManager",
          "name": "Skill Manager",
          "type": "webview"
        },
        {
          "id": "capabilityBuilder",
          "name": "Capability Builder",
          "type": "webview"
        }
      ]
    },
    "commands": [
      {
        "command": "ccm.skill.create",
        "title": "Create Skill",
        "category": "Capability Manager"
      },
      {
        "command": "ccm.skill.edit",
        "title": "Edit Skill",
        "category": "Capability Manager"
      },
      {
        "command": "ccm.skill.delete",
        "title": "Delete Skill",
        "category": "Capability Manager"
      },
      {
        "command": "ccm.capability.create",
        "title": "Create Capability",
        "category": "Capability Manager"
      },
      {
        "command": "ccm.capability.export",
        "title": "Export to Prompt File",
        "category": "Capability Manager"
      }
    ]
  }
}
```

---

## Skill Manager 設計

### 功能需求

1. **Skills 列表**
   - TreeView 顯示所有 Skills
   - 按 Category 分組
   - 支援搜尋過濾
   - 右鍵選單（編輯、刪除）

2. **新增/編輯 Skill**
   - 表單輸入：名稱、描述、類別
   - 觸發詞設定
   - Prompt 編輯器（Markdown）
   - MCP Tool 選擇器

3. **MCP Tool 選擇器**
   - 列出已安裝的 MCP Servers
   - 每個 Server 下列出可用 Tools
   - Tool 詳情（描述、參數）
   - 參數設定表單

### 資料模型

```typescript
// src/types/skill.ts

export interface Skill {
  id: string;
  name: string;
  description: string;
  category: SkillCategory;
  triggers: string[];
  prompt: string;
  mcpTools?: McpToolConfig[];
  createdAt: Date;
  updatedAt: Date;
}

export type SkillCategory = 
  | 'research'
  | 'documentation'
  | 'git'
  | 'maintenance'
  | 'architecture';

export interface McpToolConfig {
  server: string;        // e.g., 'pubmed-search'
  tool: string;          // e.g., 'search_literature'
  description?: string;
  parameters: Record<string, {
    type: string;
    default?: any;
    description?: string;
  }>;
}
```

### SkillService 實作

```typescript
// src/services/SkillService.ts

import * as vscode from 'vscode';
import * as fs from 'fs/promises';
import * as path from 'path';
import * as yaml from 'yaml';
import { Skill } from '../types/skill';

export class SkillService {
  private skillsDir: string;

  constructor(workspaceRoot: string) {
    this.skillsDir = path.join(workspaceRoot, '.claude', 'skills');
  }

  async listSkills(): Promise<Skill[]> {
    const skills: Skill[] = [];
    const dirs = await fs.readdir(this.skillsDir);
    
    for (const dir of dirs) {
      const skillPath = path.join(this.skillsDir, dir, 'SKILL.md');
      if (await this.fileExists(skillPath)) {
        const skill = await this.loadSkill(skillPath);
        skills.push(skill);
      }
    }
    
    return skills;
  }

  async createSkill(skill: Skill): Promise<void> {
    const skillDir = path.join(this.skillsDir, skill.id);
    await fs.mkdir(skillDir, { recursive: true });
    
    const content = this.serializeSkill(skill);
    await fs.writeFile(
      path.join(skillDir, 'SKILL.md'),
      content,
      'utf-8'
    );
  }

  async updateSkill(id: string, skill: Skill): Promise<void> {
    const skillPath = path.join(this.skillsDir, id, 'SKILL.md');
    const content = this.serializeSkill(skill);
    await fs.writeFile(skillPath, content, 'utf-8');
  }

  async deleteSkill(id: string): Promise<void> {
    const skillDir = path.join(this.skillsDir, id);
    await fs.rm(skillDir, { recursive: true });
  }

  private serializeSkill(skill: Skill): string {
    const frontmatter = {
      name: skill.name,
      description: skill.description,
      category: skill.category,
      triggers: skill.triggers,
      mcpTools: skill.mcpTools
    };

    return `---
${yaml.stringify(frontmatter)}---

${skill.prompt}`;
  }

  private async loadSkill(path: string): Promise<Skill> {
    // 解析 YAML frontmatter 和 Markdown content
    // ...實作省略
  }

  private async fileExists(path: string): Promise<boolean> {
    try {
      await fs.access(path);
      return true;
    } catch {
      return false;
    }
  }
}
```

---

## Capability Builder 設計

### 功能需求

1. **Skills 側邊欄**
   - 顯示所有可用 Skills
   - 可拖動到工作流程

2. **工作流程畫布**
   - 拖拉排序 Skills
   - 視覺化流程連線
   - 點選步驟查看/編輯

3. **步驟設定面板**
   - 覆寫 Skill 預設參數
   - 條件設定（可選）

4. **匯出功能**
   - 預覽生成的 Prompt
   - 儲存到 `.github/prompts/`

### 資料模型

```typescript
// src/types/capability.ts

export interface Capability {
  id: string;
  name: string;
  description: string;
  steps: CapabilityStep[];
  createdAt: Date;
  updatedAt: Date;
}

export interface CapabilityStep {
  order: number;
  skillId: string;
  skillName?: string;  // 顯示用
  overrides?: {
    parameters?: Record<string, any>;
    condition?: string;
  };
}
```

### Prompt 生成邏輯

```typescript
// src/services/CapabilityService.ts

export class CapabilityService {
  private skillService: SkillService;

  async generatePromptFile(capability: Capability): Promise<string> {
    let content = `---
description: "🔗 ${capability.description}"
---

# ${capability.name}

`;

    for (const step of capability.steps) {
      const skill = await this.skillService.getSkill(step.skillId);
      
      content += `## Step ${step.order}: ${skill.name}

📖 **技能參考**: \`.claude/skills/${skill.id}/SKILL.md\`

${skill.prompt}

`;

      if (step.overrides?.parameters) {
        content += `**參數覆寫**:
\`\`\`json
${JSON.stringify(step.overrides.parameters, null, 2)}
\`\`\`

`;
      }
    }

    return content;
  }

  async exportToPromptFile(capability: Capability): Promise<void> {
    const content = await this.generatePromptFile(capability);
    const promptPath = path.join(
      this.workspaceRoot,
      '.github',
      'prompts',
      `cp.${capability.id}.prompt.md`
    );
    
    await fs.writeFile(promptPath, content, 'utf-8');
  }
}
```

---

## MCP 整合設計

### McpService

```typescript
// src/services/McpService.ts

export interface McpServer {
  name: string;
  description?: string;
}

export interface McpTool {
  name: string;
  description: string;
  inputSchema: JsonSchema;
}

export class McpService {
  /**
   * 從 VS Code 設定中取得已設定的 MCP Servers
   */
  async discoverServers(): Promise<McpServer[]> {
    const config = vscode.workspace.getConfiguration('mcp');
    const servers = config.get<Record<string, any>>('servers') || {};
    
    return Object.keys(servers).map(name => ({
      name,
      description: servers[name].description
    }));
  }

  /**
   * 取得 MCP Server 的 Tool 列表
   * 
   * 注意：這需要解析 MCP Server 的 schema
   * 或者從 VS Code MCP 擴充套件 API 取得
   */
  async listTools(serverName: string): Promise<McpTool[]> {
    // TODO: 實作 MCP Tool 列舉
    // 可能需要：
    // 1. 讀取 MCP Server 的 manifest
    // 2. 或使用 VS Code MCP API
    return [];
  }

  /**
   * 取得特定 Tool 的參數 Schema
   */
  async getToolSchema(
    serverName: string, 
    toolName: string
  ): Promise<JsonSchema> {
    // TODO: 實作
    return {};
  }
}
```

### MCP Tool 選擇器 UI

```tsx
// webview-ui/src/components/SkillManager/McpToolSelector.tsx

import React, { useState, useEffect } from 'react';
import { vscode } from '../../hooks/useVscodeApi';

interface McpToolSelectorProps {
  selectedTools: McpToolConfig[];
  onChange: (tools: McpToolConfig[]) => void;
}

export const McpToolSelector: React.FC<McpToolSelectorProps> = ({
  selectedTools,
  onChange
}) => {
  const [servers, setServers] = useState<McpServer[]>([]);
  const [tools, setTools] = useState<Record<string, McpTool[]>>({});
  const [expandedServer, setExpandedServer] = useState<string | null>(null);

  useEffect(() => {
    // 載入 MCP Servers
    vscode.postMessage({ type: 'getMcpServers' });
  }, []);

  const handleToolSelect = (server: string, tool: McpTool) => {
    const newConfig: McpToolConfig = {
      server,
      tool: tool.name,
      description: tool.description,
      parameters: extractDefaultParams(tool.inputSchema)
    };
    
    onChange([...selectedTools, newConfig]);
  };

  return (
    <div className="mcp-tool-selector">
      <h4>🔧 MCP Tools</h4>
      
      {servers.map(server => (
        <div key={server.name} className="server-group">
          <div 
            className="server-header"
            onClick={() => setExpandedServer(
              expandedServer === server.name ? null : server.name
            )}
          >
            <span>{expandedServer === server.name ? '▼' : '▶'}</span>
            <span>{server.name}</span>
          </div>
          
          {expandedServer === server.name && (
            <div className="tool-list">
              {tools[server.name]?.map(tool => (
                <div 
                  key={tool.name} 
                  className="tool-item"
                  onClick={() => handleToolSelect(server.name, tool)}
                >
                  <span className="tool-name">{tool.name}</span>
                  <span className="tool-desc">{tool.description}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
      
      <div className="selected-tools">
        <h5>已選擇:</h5>
        {selectedTools.map((config, idx) => (
          <div key={idx} className="selected-tool">
            <span>{config.server}.{config.tool}</span>
            <button onClick={() => {
              const newTools = selectedTools.filter((_, i) => i !== idx);
              onChange(newTools);
            }}>✕</button>
          </div>
        ))}
      </div>
    </div>
  );
};
```

---

## 開發步驟

### Phase 2.1: 擴充套件基礎 (1 週)

1. 使用 `yo code` 生成擴充套件專案
2. 設定 TypeScript + Webpack + ESLint
3. 註冊 Activity Bar View Container
4. 建立空的 Webview Provider

### Phase 2.2: Skill Manager (2 週)

1. 實作 `SkillService`
2. 實作 `SkillTreeProvider`
3. 建立 Webview React 應用
4. 實作 Skill 表單

### Phase 2.3: MCP 整合 (1 週)

1. 實作 `McpService`
2. 建立 MCP Tool 選擇器 UI
3. 整合到 Skill 表單

### Phase 3: Capability Builder (3 週)

1. 實作拖拉介面
2. 實作流程視覺化
3. 實作 Prompt 生成
4. 測試和優化

---

## 相關資源

- [VS Code Extension API](https://code.visualstudio.com/api)
- [Webview UI Toolkit](https://github.com/microsoft/vscode-webview-ui-toolkit)
- [Model Context Protocol](https://modelcontextprotocol.io/)
