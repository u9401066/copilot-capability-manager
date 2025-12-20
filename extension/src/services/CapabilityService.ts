/**
 * CapabilityService - Capability（工作流程）管理
 * 
 * 負責讀寫 .github/prompts/ 目錄下的 Prompt Files
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs/promises';
import { Capability, CapabilityStep, PromptFrontmatter } from '../types';
import { SkillService } from './SkillService';

export class CapabilityService {
    private promptsDir: string;
    private workspaceRoot: string;
    private skillService: SkillService;

    constructor(workspaceRoot: string, skillService: SkillService) {
        this.workspaceRoot = workspaceRoot;
        this.skillService = skillService;
        
        // 從設定讀取路徑
        const config = vscode.workspace.getConfiguration('ccm');
        const promptsPath = config.get<string>('promptsPath') || '.github/prompts';
        this.promptsDir = path.join(workspaceRoot, promptsPath);
    }

    /**
     * 列出所有 Capabilities（cp.*.prompt.md 檔案）
     */
    async listCapabilities(): Promise<Capability[]> {
        const capabilities: Capability[] = [];
        
        try {
            await this.ensureDirectory(this.promptsDir);
            const files = await fs.readdir(this.promptsDir);
            
            for (const file of files) {
                // 只處理 cp.*.prompt.md 格式
                if (file.startsWith('cp.') && file.endsWith('.prompt.md')) {
                    const filePath = path.join(this.promptsDir, file);
                    try {
                        const capability = await this.loadCapability(filePath);
                        if (capability) {
                            capabilities.push(capability);
                        }
                    } catch (err) {
                        console.warn(`Failed to load capability ${file}:`, err);
                    }
                }
            }
        } catch (err) {
            console.error('Failed to list capabilities:', err);
        }
        
        return capabilities;
    }

    /**
     * 取得單一 Capability
     */
    async getCapability(id: string): Promise<Capability | null> {
        const filePath = path.join(this.promptsDir, `cp.${id}.prompt.md`);
        if (await this.fileExists(filePath)) {
            return this.loadCapability(filePath);
        }
        return null;
    }

    /**
     * 建立新 Capability
     */
    async createCapability(capability: Capability): Promise<void> {
        await this.ensureDirectory(this.promptsDir);
        const content = await this.generatePromptContent(capability);
        const filePath = path.join(this.promptsDir, `cp.${capability.id}.prompt.md`);
        await fs.writeFile(filePath, content, 'utf-8');
    }

    /**
     * 更新 Capability
     */
    async updateCapability(id: string, capability: Capability): Promise<void> {
        const content = await this.generatePromptContent(capability);
        const filePath = path.join(this.promptsDir, `cp.${id}.prompt.md`);
        await fs.writeFile(filePath, content, 'utf-8');
    }

    /**
     * 刪除 Capability
     */
    async deleteCapability(id: string): Promise<void> {
        const filePath = path.join(this.promptsDir, `cp.${id}.prompt.md`);
        if (await this.fileExists(filePath)) {
            await fs.unlink(filePath);
        }
    }

    /**
     * 生成 Prompt File 內容
     */
    async generatePromptContent(capability: Capability): Promise<string> {
        const emoji = capability.emoji || '🔗';
        let content = `---
description: "${emoji} ${capability.name} - ${capability.description}"
---

# ${capability.name}

請依序執行以下步驟，完成後打勾 ✅：

`;

        for (const step of capability.steps) {
            const skill = await this.skillService.getSkill(step.skillId);
            const stepTitle = step.title || skill?.name || step.skillId;
            
            content += `## Step ${step.order}: ${stepTitle} \`${step.skillId}\`

📖 技能參考: \`.claude/skills/${step.skillId}/SKILL.md\`

`;
            
            if (step.tasks && step.tasks.length > 0) {
                content += `**任務：**\n`;
                for (const task of step.tasks) {
                    content += `- ${task}\n`;
                }
                content += '\n';
            }
            
            if (step.output) {
                content += `**輸出：** ${step.output}\n\n`;
            }
            
            content += `---\n\n`;
        }

        // 添加完成檢查清單
        content += `## 📋 完成檢查\n\n`;
        for (const step of capability.steps) {
            const stepTitle = step.title || step.skillId;
            content += `- [ ] Step ${step.order}: ${stepTitle} 完成\n`;
        }

        return content;
    }

    /**
     * 載入 Capability 從 Prompt File
     * 注意：這是反向解析，可能無法完全還原所有資訊
     */
    private async loadCapability(filePath: string): Promise<Capability | null> {
        const content = await fs.readFile(filePath, 'utf-8');
        const fileName = path.basename(filePath);
        
        // 解析 ID：cp.{id}.prompt.md
        const idMatch = fileName.match(/^cp\.(.+)\.prompt\.md$/);
        if (!idMatch) {
            return null;
        }
        const id = idMatch[1];
        
        // 解析 frontmatter
        const fmRegex = /^---\n([\s\S]*?)\n---\n?([\s\S]*)$/;
        const match = content.match(fmRegex);
        
        let description = '';
        let name = id;
        let emoji = '🔗';
        
        if (match) {
            try {
                const frontmatter = match[1];
                const descMatch = frontmatter.match(/description:\s*"(.+)"/);
                if (descMatch) {
                    const fullDesc = descMatch[1];
                    // 解析 "emoji 名稱 - 描述" 格式
                    const parts = fullDesc.match(/^(.+?)\s+(.+?)\s+-\s+(.+)$/);
                    if (parts) {
                        emoji = parts[1];
                        name = parts[2];
                        description = parts[3];
                    } else {
                        description = fullDesc;
                    }
                }
            } catch (err) {
                // 忽略解析錯誤
            }
        }
        
        // 解析步驟（簡化版，只提取基本資訊）
        const steps: CapabilityStep[] = [];
        const stepRegex = /## Step (\d+): (.+?) `(.+?)`/g;
        let stepMatch;
        
        while ((stepMatch = stepRegex.exec(content)) !== null) {
            steps.push({
                order: parseInt(stepMatch[1], 10),
                skillId: stepMatch[3],
                title: stepMatch[2]
            });
        }
        
        return {
            id,
            name,
            description,
            emoji,
            steps,
            filePath
        };
    }

    /**
     * 確保目錄存在
     */
    private async ensureDirectory(dirPath: string): Promise<void> {
        try {
            await fs.access(dirPath);
        } catch {
            await fs.mkdir(dirPath, { recursive: true });
        }
    }

    /**
     * 檢查檔案是否存在
     */
    private async fileExists(filePath: string): Promise<boolean> {
        try {
            await fs.access(filePath);
            return true;
        } catch {
            return false;
        }
    }
}
