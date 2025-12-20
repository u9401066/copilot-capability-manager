/**
 * SkillService - Skill 的 CRUD 操作
 * 
 * 負責讀寫 .claude/skills/ 目錄下的 SKILL.md 檔案
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs/promises';
import * as yaml from 'yaml';
import { Skill, SkillFrontmatter, SkillCategory } from '../types';

export class SkillService {
    private skillsDir: string;
    private workspaceRoot: string;

    constructor(workspaceRoot: string) {
        this.workspaceRoot = workspaceRoot;
        // 從設定讀取路徑，或使用預設值
        const config = vscode.workspace.getConfiguration('ccm');
        const skillsPath = config.get<string>('skillsPath') || '.claude/skills';
        this.skillsDir = path.join(workspaceRoot, skillsPath);
    }

    /**
     * 列出所有 Skills
     */
    async listSkills(): Promise<Skill[]> {
        const skills: Skill[] = [];
        
        try {
            // 確保目錄存在
            await this.ensureDirectory(this.skillsDir);
            
            const dirs = await fs.readdir(this.skillsDir, { withFileTypes: true });
            
            for (const dir of dirs) {
                if (dir.isDirectory()) {
                    const skillPath = path.join(this.skillsDir, dir.name, 'SKILL.md');
                    if (await this.fileExists(skillPath)) {
                        try {
                            const skill = await this.loadSkill(skillPath, dir.name);
                            skills.push(skill);
                        } catch (err) {
                            console.warn(`Failed to load skill ${dir.name}:`, err);
                        }
                    }
                }
            }
        } catch (err) {
            console.error('Failed to list skills:', err);
        }
        
        return skills.sort((a, b) => a.name.localeCompare(b.name));
    }

    /**
     * 取得單一 Skill
     */
    async getSkill(id: string): Promise<Skill | null> {
        const skillPath = path.join(this.skillsDir, id, 'SKILL.md');
        if (await this.fileExists(skillPath)) {
            return this.loadSkill(skillPath, id);
        }
        return null;
    }

    /**
     * 建立新 Skill
     */
    async createSkill(skill: Skill): Promise<void> {
        const skillDir = path.join(this.skillsDir, skill.id);
        
        // 檢查是否已存在
        if (await this.fileExists(skillDir)) {
            throw new Error(`Skill "${skill.id}" 已存在`);
        }
        
        // 建立目錄
        await fs.mkdir(skillDir, { recursive: true });
        
        // 寫入 SKILL.md
        const content = this.serializeSkill(skill);
        await fs.writeFile(path.join(skillDir, 'SKILL.md'), content, 'utf-8');
    }

    /**
     * 更新 Skill
     */
    async updateSkill(id: string, skill: Skill): Promise<void> {
        const skillPath = path.join(this.skillsDir, id, 'SKILL.md');
        
        if (!await this.fileExists(skillPath)) {
            throw new Error(`Skill "${id}" 不存在`);
        }
        
        const content = this.serializeSkill(skill);
        await fs.writeFile(skillPath, content, 'utf-8');
    }

    /**
     * 刪除 Skill
     */
    async deleteSkill(id: string): Promise<void> {
        const skillDir = path.join(this.skillsDir, id);
        
        if (!await this.fileExists(skillDir)) {
            throw new Error(`Skill "${id}" 不存在`);
        }
        
        await fs.rm(skillDir, { recursive: true });
    }

    /**
     * 取得 Skill 檔案路徑
     */
    getSkillPath(id: string): string {
        return path.join(this.skillsDir, id, 'SKILL.md');
    }

    /**
     * 載入 SKILL.md 並解析
     */
    private async loadSkill(filePath: string, id: string): Promise<Skill> {
        const content = await fs.readFile(filePath, 'utf-8');
        const { frontmatter, body } = this.parseFrontmatter(content);
        
        return {
            id,
            name: frontmatter.name || id,
            description: frontmatter.description || '',
            category: frontmatter.category || this.inferCategory(id),
            triggers: frontmatter.triggers || [],
            mcpTools: frontmatter.mcpTools,
            prompt: body.trim(),
            filePath
        };
    }

    /**
     * 序列化 Skill 為 SKILL.md 格式
     */
    private serializeSkill(skill: Skill): string {
        const frontmatter: SkillFrontmatter = {
            name: skill.id,
            description: skill.description
        };
        
        if (skill.category) {
            frontmatter.category = skill.category;
        }
        if (skill.triggers && skill.triggers.length > 0) {
            frontmatter.triggers = skill.triggers;
        }
        if (skill.mcpTools && skill.mcpTools.length > 0) {
            frontmatter.mcpTools = skill.mcpTools;
        }

        const yamlContent = yaml.stringify(frontmatter, {
            lineWidth: 0,
            defaultStringType: 'QUOTE_DOUBLE'
        });

        return `---
${yamlContent}---

${skill.prompt}`;
    }

    /**
     * 解析 YAML Frontmatter
     */
    private parseFrontmatter(content: string): { frontmatter: SkillFrontmatter; body: string } {
        const fmRegex = /^---\n([\s\S]*?)\n---\n?([\s\S]*)$/;
        const match = content.match(fmRegex);
        
        if (match) {
            try {
                const frontmatter = yaml.parse(match[1]) as SkillFrontmatter;
                return {
                    frontmatter,
                    body: match[2]
                };
            } catch (err) {
                console.warn('Failed to parse frontmatter:', err);
            }
        }
        
        return {
            frontmatter: { name: '', description: '' },
            body: content
        };
    }

    /**
     * 根據 ID 推斷分類
     */
    private inferCategory(id: string): SkillCategory {
        const lowerID = id.toLowerCase();
        if (lowerID.includes('git') || lowerID.includes('commit') || lowerID.includes('push')) {
            return 'git';
        }
        if (lowerID.includes('readme') || lowerID.includes('changelog') || lowerID.includes('doc') || lowerID.includes('report')) {
            return 'documentation';
        }
        if (lowerID.includes('search') || lowerID.includes('web') || lowerID.includes('research')) {
            return 'research';
        }
        if (lowerID.includes('test') || lowerID.includes('review') || lowerID.includes('check')) {
            return 'quality';
        }
        if (lowerID.includes('refactor') || lowerID.includes('clean') || lowerID.includes('memory')) {
            return 'maintenance';
        }
        if (lowerID.includes('arch') || lowerID.includes('ddd') || lowerID.includes('init')) {
            return 'architecture';
        }
        return 'other';
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
