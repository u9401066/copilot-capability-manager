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
    /** 工作流程步驟（可為節點圖結構）*/
    steps: CapabilityStep[];
    /** 節點連接（用於非線性流程）*/
    edges?: CapabilityEdge[];
    /** 檔案路徑 */
    filePath?: string;
    /** 建立時間 */
    createdAt?: Date;
    /** 更新時間 */
    updatedAt?: Date;
}

/**
 * 步驟類型
 */
export type StepType = 'skill' | 'branch' | 'loop' | 'parallel' | 'merge';

export interface CapabilityStep {
    /** 步驟 ID（用於節點連接）*/
    id?: string;
    /** 步驟順序（線性流程用）*/
    order: number;
    /** 步驟類型 */
    type?: StepType;
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
    /** 執行條件（用於分支）*/
    condition?: string;
    /** 迴圈設定 */
    loop?: LoopConfig;
    /** 並行步驟（用於 parallel 類型）*/
    parallelSteps?: string[];
}

/**
 * 迴圈設定
 */
export interface LoopConfig {
    /** 迴圈類型 */
    type: 'while' | 'foreach' | 'times';
    /** 條件表達式（while 用）*/
    condition?: string;
    /** 迭代來源（foreach 用）*/
    source?: string;
    /** 次數（times 用）*/
    count?: number;
    /** 最大迴圈次數（防止無限迴圈）*/
    maxIterations?: number;
}

/**
 * 節點連接（用於圖形化流程）
 */
export interface CapabilityEdge {
    /** 來源節點 ID */
    from: string;
    /** 目標節點 ID */
    to: string;
    /** 連接標籤（如：true/false 分支）*/
    label?: string;
    /** 條件表達式 */
    condition?: string;
}

/**
 * 合併驗證結果
 */
export interface MergeValidation {
    /** 是否可合併 */
    canMerge: boolean;
    /** 原因 */
    reason?: string;
    /** 警告（可合併但有潛在問題）*/
    warnings?: string[];
    /** 衝突點 */
    conflicts?: MergeConflict[];
}

export interface MergeConflict {
    /** 衝突類型 */
    type: 'circular' | 'incompatible' | 'resource';
    /** 衝突描述 */
    description: string;
    /** 相關步驟 */
    steps: string[];
}

/**
 * Prompt File 的 Frontmatter 結構
 */
export interface PromptFrontmatter {
    description: string;
}
