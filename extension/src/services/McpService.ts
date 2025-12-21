/**
 * McpService - MCP Tools 發現與管理
 * 
 * 從 VS Code 設定中讀取已設定的 MCP servers
 * 並提供可用 Tools 列表供 Skill 選用
 */

import * as vscode from 'vscode';

export interface McpTool {
    name: string;           // e.g., "mcp_pubmed_search_search_literature"
    server: string;         // e.g., "pubmed-search"
    description?: string;   // Tool 的描述
    category?: string;      // 分類
    parameters?: McpParameter[];
}

export interface McpParameter {
    name: string;
    type: string;
    required: boolean;
    description?: string;
    default?: any;
}

export interface McpServer {
    name: string;
    command?: string;
    args?: string[];
    enabled: boolean;
}

/**
 * 預定義的 MCP Tools 清單
 * 這些是根據系統中常見的 MCP servers 整理
 */
const KNOWN_MCP_TOOLS: McpTool[] = [
    // PubMed Search Tools
    {
        name: 'mcp_pubmed_search_search_literature',
        server: 'pubmed-search',
        category: '文獻搜尋',
        description: '在 PubMed 搜尋醫學文獻',
        parameters: [
            { name: 'query', type: 'string', required: true, description: '搜尋查詢' },
            { name: 'limit', type: 'number', required: false, default: 5 },
            { name: 'min_year', type: 'number', required: false },
            { name: 'article_type', type: 'string', required: false }
        ]
    },
    {
        name: 'mcp_pubmed_search_fetch_article_details',
        server: 'pubmed-search',
        category: '文獻搜尋',
        description: '取得文章詳細資訊',
        parameters: [
            { name: 'pmids', type: 'string', required: true, description: 'PMID 列表，逗號分隔' }
        ]
    },
    {
        name: 'mcp_pubmed_search_generate_search_queries',
        server: 'pubmed-search',
        category: '文獻搜尋',
        description: '產生 MeSH 擴展搜尋策略',
        parameters: [
            { name: 'topic', type: 'string', required: true },
            { name: 'strategy', type: 'string', required: false, default: 'comprehensive' }
        ]
    },
    {
        name: 'mcp_pubmed_search_find_related_articles',
        server: 'pubmed-search',
        category: '文獻探索',
        description: '找尋相關文章',
        parameters: [
            { name: 'pmid', type: 'string', required: true },
            { name: 'limit', type: 'number', required: false, default: 5 }
        ]
    },
    {
        name: 'mcp_pubmed_search_get_citation_metrics',
        server: 'pubmed-search',
        category: '文獻分析',
        description: '取得引用指標 (RCR/Percentile)',
        parameters: [
            { name: 'pmids', type: 'string', required: true },
            { name: 'sort_by', type: 'string', required: false, default: 'citation_count' }
        ]
    },
    {
        name: 'mcp_pubmed_search_merge_search_results',
        server: 'pubmed-search',
        category: '文獻搜尋',
        description: '合併多個搜尋結果',
        parameters: [
            { name: 'results_json', type: 'string', required: true }
        ]
    },
    // Zotero Tools
    {
        name: 'mcp_zotero_keeper_search_items',
        server: 'zotero-keeper',
        category: 'Zotero',
        description: '搜尋 Zotero 書目資料',
        parameters: [
            { name: 'query', type: 'string', required: true },
            { name: 'limit', type: 'number', required: false, default: 25 }
        ]
    },
    {
        name: 'mcp_zotero_keeper_batch_import_from_pubmed',
        server: 'zotero-keeper',
        category: 'Zotero',
        description: '批次從 PubMed 匯入文獻到 Zotero',
        parameters: [
            { name: 'pmids', type: 'string', required: true },
            { name: 'collection_name', type: 'string', required: false },
            { name: 'tags', type: 'array', required: false }
        ]
    },
    {
        name: 'mcp_zotero_keeper_check_articles_owned',
        server: 'zotero-keeper',
        category: 'Zotero',
        description: '檢查哪些文章已在 Zotero 中',
        parameters: [
            { name: 'pmids', type: 'array', required: true }
        ]
    },
    // Pylance Tools
    {
        name: 'mcp_pylance_mcp_s_pylanceDocuments',
        server: 'pylance',
        category: 'Python',
        description: '搜尋 Pylance 文件',
        parameters: [
            { name: 'search', type: 'string', required: true }
        ]
    },
    {
        name: 'mcp_pylance_mcp_s_pylanceInvokeRefactoring',
        server: 'pylance',
        category: 'Python',
        description: '執行 Python 重構',
        parameters: [
            { name: 'fileUri', type: 'string', required: true },
            { name: 'name', type: 'string', required: true },
            { name: 'mode', type: 'string', required: false }
        ]
    }
];

export class McpService {
    private tools: McpTool[] = [];
    private servers: McpServer[] = [];

    constructor() {
        this.loadKnownTools();
        this.discoverServers();
    }

    /**
     * 載入預定義的 Tools
     */
    private loadKnownTools(): void {
        this.tools = [...KNOWN_MCP_TOOLS];
    }

    /**
     * 從 VS Code 設定發現 MCP servers
     */
    private discoverServers(): void {
        const config = vscode.workspace.getConfiguration('github.copilot');
        const mcpConfig = config.get<Record<string, any>>('chat.mcpServers');
        
        if (mcpConfig) {
            this.servers = Object.entries(mcpConfig).map(([name, settings]) => ({
                name,
                command: settings.command,
                args: settings.args,
                enabled: true
            }));
        }
    }

    /**
     * 取得所有可用的 MCP Tools
     */
    getAllTools(): McpTool[] {
        return this.tools;
    }

    /**
     * 依分類取得 Tools
     */
    getToolsByCategory(): Map<string, McpTool[]> {
        const byCategory = new Map<string, McpTool[]>();
        
        for (const tool of this.tools) {
            const category = tool.category || 'Other';
            if (!byCategory.has(category)) {
                byCategory.set(category, []);
            }
            byCategory.get(category)!.push(tool);
        }
        
        return byCategory;
    }

    /**
     * 依 server 取得 Tools
     */
    getToolsByServer(serverName: string): McpTool[] {
        return this.tools.filter(t => t.server === serverName);
    }

    /**
     * 搜尋 Tools
     */
    searchTools(query: string): McpTool[] {
        const lowerQuery = query.toLowerCase();
        return this.tools.filter(t => 
            t.name.toLowerCase().includes(lowerQuery) ||
            t.description?.toLowerCase().includes(lowerQuery) ||
            t.category?.toLowerCase().includes(lowerQuery)
        );
    }

    /**
     * 取得 Tool 詳細資訊
     */
    getTool(name: string): McpTool | undefined {
        return this.tools.find(t => t.name === name);
    }

    /**
     * 取得已設定的 MCP Servers
     */
    getServers(): McpServer[] {
        return this.servers;
    }

    /**
     * 產生 Tool 的使用範例 markdown
     */
    generateToolUsageExample(tool: McpTool): string {
        const params = tool.parameters?.filter(p => p.required)
            .map(p => `${p.name}="${p.type === 'string' ? 'value' : '...'}"`)
            .join(', ') || '';
        
        return `使用 ${tool.name}(${params})`;
    }

    /**
     * 為 Skill 推薦相關的 MCP Tools
     */
    recommendToolsForSkill(skillName: string, description: string): McpTool[] {
        const text = `${skillName} ${description}`.toLowerCase();
        
        const keywords: Record<string, string[]> = {
            '文獻搜尋': ['pubmed', 'literature', 'search', 'article', '文獻', '搜尋', '論文'],
            '文獻探索': ['related', 'citing', 'reference', '相關', '引用'],
            '文獻分析': ['citation', 'metrics', 'impact', '引用', '指標', 'IF'],
            'Zotero': ['zotero', 'reference', 'bibliography', '書目', '管理'],
            'Python': ['python', 'refactor', 'lint', 'pylance']
        };

        const matchedCategories = new Set<string>();
        
        for (const [category, categoryKeywords] of Object.entries(keywords)) {
            if (categoryKeywords.some(kw => text.includes(kw))) {
                matchedCategories.add(category);
            }
        }

        if (matchedCategories.size === 0) {
            return [];
        }

        return this.tools.filter(t => 
            t.category && matchedCategories.has(t.category)
        );
    }

    /**
     * 重新整理 - 重新載入設定
     */
    refresh(): void {
        this.loadKnownTools();
        this.discoverServers();
    }
}
