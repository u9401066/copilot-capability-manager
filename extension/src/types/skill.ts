/**
 * Skill 型別定義
 */

export type SkillCategory = 
    | 'research'
    | 'documentation'
    | 'git'
    | 'maintenance'
    | 'architecture'
    | 'quality'
    | 'other';

export interface Skill {
    /** Skill ID（對應目錄名稱）*/
    id: string;
    /** 顯示名稱 */
    name: string;
    /** 詳細描述（支援多行，含 LOAD THIS SKILL WHEN）*/
    description: string;
    /** 分類 */
    category?: SkillCategory;
    /** 觸發詞列表 */
    triggers?: string[];
    /** MCP Tools 設定 */
    mcpTools?: McpToolConfig[];
    /** Prompt 內容（SKILL.md 的 Markdown 部分）*/
    prompt: string;
    /** 檔案路徑 */
    filePath?: string;
    /** 建立時間 */
    createdAt?: Date;
    /** 更新時間 */
    updatedAt?: Date;
}

export interface McpToolConfig {
    /** MCP Server 名稱 */
    server: string;
    /** Tool 名稱 */
    tool: string;
    /** Tool 描述 */
    description?: string;
    /** Tool 參數設定 */
    parameters?: Record<string, {
        type: string;
        default?: unknown;
        description?: string;
    }>;
}

/**
 * SKILL.md 的 Frontmatter 結構
 */
export interface SkillFrontmatter {
    name: string;
    description: string;
    category?: SkillCategory;
    triggers?: string[];
    mcpTools?: McpToolConfig[];
    skill_id?: string;
    priority?: number;
}

/**
 * 分類顯示設定
 */
export const CATEGORY_LABELS: Record<SkillCategory, string> = {
    research: '🔬 研究',
    documentation: '📝 文件',
    git: '📦 Git',
    maintenance: '🔧 維護',
    architecture: '🏗️ 架構',
    quality: '✅ 品質',
    other: '📂 其他'
};

export const CATEGORY_ICONS: Record<SkillCategory, string> = {
    research: 'beaker',
    documentation: 'book',
    git: 'git-commit',
    maintenance: 'tools',
    architecture: 'symbol-structure',
    quality: 'check-all',
    other: 'folder'
};
