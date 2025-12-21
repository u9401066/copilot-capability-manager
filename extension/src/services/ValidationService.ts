/**
 * ValidationService - 驗證 Capability 合併規則
 */

import { Capability, CapabilityStep, MergeValidation, MergeConflict } from '../types/capability';
import { Skill, SkillIOType } from '../types/skill';
import { SkillService } from './SkillService';

export class ValidationService {
    constructor(private skillService: SkillService) {}

    /**
     * 驗證兩個 Capability 是否可以合併
     */
    async validateMerge(cap1: Capability, cap2: Capability): Promise<MergeValidation> {
        const conflicts: MergeConflict[] = [];
        const warnings: string[] = [];

        // 1. 檢查循環依賴
        const circularCheck = await this.checkCircularDependency(cap1, cap2);
        if (circularCheck) {
            conflicts.push(circularCheck);
        }

        // 2. 檢查輸入輸出相容性
        const ioCheck = await this.checkIOCompatibility(cap1, cap2);
        if (ioCheck) {
            conflicts.push(ioCheck);
        }

        // 3. 檢查資源衝突
        const resourceCheck = await this.checkResourceConflicts(cap1, cap2);
        if (resourceCheck) {
            conflicts.push(resourceCheck);
        }

        // 4. 檢查警告
        const stepOverlap = this.checkStepOverlap(cap1, cap2);
        if (stepOverlap) {
            warnings.push(stepOverlap);
        }

        return {
            canMerge: conflicts.length === 0,
            reason: conflicts.length > 0 ? conflicts[0].description : undefined,
            warnings: warnings.length > 0 ? warnings : undefined,
            conflicts: conflicts.length > 0 ? conflicts : undefined
        };
    }

    /**
     * 檢查步驟連接是否有效
     */
    async validateStepConnection(
        fromStep: CapabilityStep,
        toStep: CapabilityStep
    ): Promise<{ valid: boolean; reason?: string }> {
        const fromSkill = await this.skillService.getSkill(fromStep.skillId);
        const toSkill = await this.skillService.getSkill(toStep.skillId);

        if (!fromSkill || !toSkill) {
            return { valid: false, reason: '找不到對應的 Skill' };
        }

        // 檢查輸出/輸入類型相容性
        if (fromSkill.outputType && toSkill.inputType) {
            if (!this.isIOCompatible(fromSkill.outputType, toSkill.inputType)) {
                return {
                    valid: false,
                    reason: `輸出類型 "${fromSkill.outputType}" 與輸入類型 "${toSkill.inputType}" 不相容`
                };
            }
        }

        return { valid: true };
    }

    /**
     * 驗證迴圈設定
     */
    validateLoop(step: CapabilityStep): { valid: boolean; warnings: string[] } {
        const warnings: string[] = [];

        if (!step.loop) {
            return { valid: true, warnings: [] };
        }

        // 檢查是否有終止條件
        if (step.loop.type === 'while' && !step.loop.condition) {
            return { 
                valid: false, 
                warnings: ['While 迴圈必須有條件表達式'] 
            };
        }

        // 檢查最大迴圈次數
        if (!step.loop.maxIterations) {
            warnings.push('建議設定 maxIterations 以防止無限迴圈');
        } else if (step.loop.maxIterations > 100) {
            warnings.push('maxIterations 超過 100 可能導致執行時間過長');
        }

        return { valid: true, warnings };
    }

    /**
     * 檢查循環依賴
     */
    private async checkCircularDependency(
        cap1: Capability,
        cap2: Capability
    ): Promise<MergeConflict | null> {
        // 取得所有步驟的 Skill ID
        const cap1Skills = new Set(cap1.steps.map(s => s.skillId));
        const cap2Skills = new Set(cap2.steps.map(s => s.skillId));

        // 如果 cap1 包含的 Skill 依賴 cap2，且 cap2 也依賴 cap1 的 Skill
        // 這裡簡化為：如果兩個 capability 共用同一個 skill，且順序相反
        const sharedSkills = [...cap1Skills].filter(s => cap2Skills.has(s));
        
        if (sharedSkills.length > 0) {
            // 檢查順序是否會造成循環
            for (const skillId of sharedSkills) {
                const cap1Order = cap1.steps.find(s => s.skillId === skillId)?.order || 0;
                const cap2Order = cap2.steps.find(s => s.skillId === skillId)?.order || 0;
                
                // 如果相同 Skill 在兩個 capability 中順序不同，可能造成問題
                if (cap1Order !== cap2Order) {
                    return {
                        type: 'circular',
                        description: `Skill "${skillId}" 在兩個能力中順序不一致，可能造成循環依賴`,
                        steps: [skillId]
                    };
                }
            }
        }

        return null;
    }

    /**
     * 檢查輸入輸出相容性
     */
    private async checkIOCompatibility(
        cap1: Capability,
        cap2: Capability
    ): Promise<MergeConflict | null> {
        // 取得 cap1 最後一個步驟的輸出
        const lastStep1 = cap1.steps[cap1.steps.length - 1];
        const lastSkill1 = await this.skillService.getSkill(lastStep1.skillId);

        // 取得 cap2 第一個步驟的輸入
        const firstStep2 = cap2.steps[0];
        const firstSkill2 = await this.skillService.getSkill(firstStep2.skillId);

        if (lastSkill1?.outputType && firstSkill2?.inputType) {
            if (!this.isIOCompatible(lastSkill1.outputType, firstSkill2.inputType)) {
                return {
                    type: 'incompatible',
                    description: `能力 1 的輸出 "${lastSkill1.outputType}" 與能力 2 的輸入 "${firstSkill2.inputType}" 不相容`,
                    steps: [lastStep1.skillId, firstStep2.skillId]
                };
            }
        }

        return null;
    }

    /**
     * 檢查資源衝突
     */
    private async checkResourceConflicts(
        cap1: Capability,
        cap2: Capability
    ): Promise<MergeConflict | null> {
        const cap1Resources = new Set<string>();
        const cap2Resources = new Set<string>();

        // 收集 cap1 使用的資源
        for (const step of cap1.steps) {
            const skill = await this.skillService.getSkill(step.skillId);
            skill?.resources?.forEach(r => cap1Resources.add(r));
        }

        // 收集 cap2 使用的資源
        for (const step of cap2.steps) {
            const skill = await this.skillService.getSkill(step.skillId);
            skill?.resources?.forEach(r => cap2Resources.add(r));
        }

        // 檢查互斥資源
        const mutuallyExclusiveResources = ['git-lock', 'file-write-lock'];
        const conflictingResources = mutuallyExclusiveResources.filter(
            r => cap1Resources.has(r) && cap2Resources.has(r)
        );

        if (conflictingResources.length > 0) {
            return {
                type: 'resource',
                description: `資源衝突: ${conflictingResources.join(', ')}`,
                steps: []
            };
        }

        return null;
    }

    /**
     * 檢查步驟重疊
     */
    private checkStepOverlap(cap1: Capability, cap2: Capability): string | null {
        const cap1Skills = new Set(cap1.steps.map(s => s.skillId));
        const cap2Skills = new Set(cap2.steps.map(s => s.skillId));
        const overlap = [...cap1Skills].filter(s => cap2Skills.has(s));

        if (overlap.length > 0) {
            return `警告: 兩個能力共用 ${overlap.length} 個 Skill: ${overlap.join(', ')}`;
        }

        return null;
    }

    /**
     * 檢查輸入輸出類型是否相容
     */
    private isIOCompatible(output: SkillIOType, input: SkillIOType): boolean {
        // any 類型與任何類型相容
        if (output === 'any' || input === 'any') {
            return true;
        }

        // 相同類型相容
        if (output === input) {
            return true;
        }

        // 相容矩陣
        const compatibilityMatrix: Record<SkillIOType, SkillIOType[]> = {
            'text': ['markdown', 'any'],
            'markdown': ['text', 'any'],
            'json': ['any'],
            'pmids': ['text', 'json', 'any'],
            'files': ['any'],
            'pdf': ['files', 'any'],
            'code': ['text', 'any'],
            'any': ['text', 'markdown', 'json', 'pmids', 'files', 'pdf', 'code', 'any']
        };

        return compatibilityMatrix[output]?.includes(input) || false;
    }
}
