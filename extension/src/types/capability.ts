/**
 * Capability（工作流程）型別定義
 */

export interface Capability {
    /** Capability ID（對應 prompt file 名稱）*/
    id: string;
    /** 顯示名稱 */
    name: string;
    /** 描述 */
    description: string;
    /** Emoji 圖示 */
    emoji?: string;
    /** 工作流程步驟 */
    steps: CapabilityStep[];
    /** 檔案路徑 */
    filePath?: string;
    /** 建立時間 */
    createdAt?: Date;
    /** 更新時間 */
    updatedAt?: Date;
}

export interface CapabilityStep {
    /** 步驟順序 */
    order: number;
    /** 對應的 Skill ID */
    skillId: string;
    /** Skill 名稱（顯示用）*/
    skillName?: string;
    /** 步驟標題（可選，預設用 Skill 名稱）*/
    title?: string;
    /** 任務描述 */
    tasks?: string[];
    /** 預期輸出 */
    output?: string;
    /** 參數覆寫 */
    parameterOverrides?: Record<string, unknown>;
    /** 執行條件 */
    condition?: string;
}

/**
 * Prompt File 的 Frontmatter 結構
 */
export interface PromptFrontmatter {
    description: string;
}
