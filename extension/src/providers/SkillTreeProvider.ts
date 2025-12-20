/**
 * SkillTreeProvider - 側邊欄 Skill 列表 TreeView
 */

import * as vscode from 'vscode';
import { SkillService } from '../services/SkillService';
import { Skill, SkillCategory, CATEGORY_LABELS, CATEGORY_ICONS } from '../types';

type TreeItemType = SkillCategoryItem | SkillItem;

export class SkillTreeProvider implements vscode.TreeDataProvider<TreeItemType> {
    private _onDidChangeTreeData = new vscode.EventEmitter<TreeItemType | undefined | null | void>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    private skillService: SkillService;
    private skills: Skill[] = [];

    constructor(skillService: SkillService) {
        this.skillService = skillService;
        this.loadSkills();
    }

    /**
     * 重新載入 Skills
     */
    async refresh(): Promise<void> {
        await this.loadSkills();
        this._onDidChangeTreeData.fire();
    }

    private async loadSkills(): Promise<void> {
        this.skills = await this.skillService.listSkills();
    }

    getTreeItem(element: TreeItemType): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: TreeItemType): Promise<TreeItemType[]> {
        if (!element) {
            // 根層級：顯示分類
            return this.getCategories();
        }
        
        if (element instanceof SkillCategoryItem) {
            // 分類層級：顯示該分類下的 Skills
            return this.getSkillsByCategory(element.category);
        }
        
        return [];
    }

    /**
     * 取得所有分類
     */
    private getCategories(): SkillCategoryItem[] {
        const categoryMap = new Map<SkillCategory, number>();
        
        // 統計每個分類的 Skill 數量
        for (const skill of this.skills) {
            const category = skill.category || 'other';
            categoryMap.set(category, (categoryMap.get(category) || 0) + 1);
        }
        
        // 建立分類項目（只顯示有 Skills 的分類）
        const categories: SkillCategoryItem[] = [];
        for (const [category, count] of categoryMap) {
            categories.push(new SkillCategoryItem(category, count));
        }
        
        // 按分類名稱排序
        return categories.sort((a, b) => 
            CATEGORY_LABELS[a.category].localeCompare(CATEGORY_LABELS[b.category])
        );
    }

    /**
     * 取得特定分類下的 Skills
     */
    private getSkillsByCategory(category: SkillCategory): SkillItem[] {
        return this.skills
            .filter(skill => (skill.category || 'other') === category)
            .map(skill => new SkillItem(skill));
    }

    /**
     * 取得 Skill（供外部使用）
     */
    getSkill(id: string): Skill | undefined {
        return this.skills.find(s => s.id === id);
    }
}

/**
 * 分類 TreeItem
 */
class SkillCategoryItem extends vscode.TreeItem {
    constructor(
        public readonly category: SkillCategory,
        public readonly count: number
    ) {
        super(
            `${CATEGORY_LABELS[category]} (${count})`,
            vscode.TreeItemCollapsibleState.Expanded
        );
        
        this.iconPath = new vscode.ThemeIcon(CATEGORY_ICONS[category]);
        this.contextValue = 'category';
    }
}

/**
 * Skill TreeItem
 */
class SkillItem extends vscode.TreeItem {
    constructor(public readonly skill: Skill) {
        super(skill.name || skill.id, vscode.TreeItemCollapsibleState.None);
        
        // 設定圖示
        this.iconPath = new vscode.ThemeIcon('symbol-method');
        
        // 設定描述（截取 description 的第一行）
        const firstLine = skill.description.split('\n')[0].trim();
        this.description = firstLine.length > 50 
            ? firstLine.substring(0, 50) + '...' 
            : firstLine;
        
        // 設定 tooltip
        this.tooltip = new vscode.MarkdownString();
        this.tooltip.appendMarkdown(`**${skill.name}**\n\n`);
        this.tooltip.appendMarkdown(skill.description.substring(0, 200));
        if (skill.triggers && skill.triggers.length > 0) {
            this.tooltip.appendMarkdown(`\n\n**觸發詞:** ${skill.triggers.join(', ')}`);
        }
        
        // 設定點擊行為
        this.command = {
            command: 'ccm.skill.openFile',
            title: '開啟 SKILL.md',
            arguments: [skill.id]
        };
        
        // 設定 context value（供 menu 判斷使用）
        this.contextValue = 'skill';
        
        // 儲存 ID 供命令使用
        this.id = skill.id;
    }
}
