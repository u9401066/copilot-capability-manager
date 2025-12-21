/**
 * CapabilityTreeProvider - 側邊欄 Capability/Workflow 列表 TreeView
 */

import * as vscode from 'vscode';
import { CapabilityService } from '../services/CapabilityService';
import { Capability } from '../types';

type TreeItemType = CapabilityItem | CapabilityStepItem;

export class CapabilityTreeProvider implements vscode.TreeDataProvider<TreeItemType> {
    private _onDidChangeTreeData = new vscode.EventEmitter<TreeItemType | undefined | null | void>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    private capabilityService: CapabilityService;
    private capabilities: Capability[] = [];

    constructor(capabilityService: CapabilityService) {
        this.capabilityService = capabilityService;
        this.loadCapabilities();
    }

    /**
     * 重新載入 Capabilities
     */
    async refresh(): Promise<void> {
        await this.loadCapabilities();
        this._onDidChangeTreeData.fire();
    }

    private async loadCapabilities(): Promise<void> {
        this.capabilities = await this.capabilityService.listCapabilities();
    }

    getTreeItem(element: TreeItemType): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: TreeItemType): Promise<TreeItemType[]> {
        if (!element) {
            // 根層級：顯示所有 Capabilities
            return this.capabilities.map(cap => new CapabilityItem(cap));
        }
        
        // Capability 層級：顯示步驟
        if (element instanceof CapabilityItem && element.capability.steps && element.capability.steps.length > 0) {
            return element.capability.steps.map((step, index) => 
                new CapabilityStepItem(step, index + 1)
            );
        }
        
        return [];
    }

    /**
     * 取得 Capability（供外部使用）
     */
    getCapability(id: string): Capability | undefined {
        return this.capabilities.find(c => c.id === id);
    }
}

/**
 * Capability TreeItem
 */
class CapabilityItem extends vscode.TreeItem {
    constructor(public readonly capability: Capability) {
        super(
            capability.name || capability.id,
            capability.steps && capability.steps.length > 0
                ? vscode.TreeItemCollapsibleState.Collapsed
                : vscode.TreeItemCollapsibleState.None
        );
        
        // 設定圖示
        this.iconPath = new vscode.ThemeIcon('symbol-event');
        
        // 設定描述
        const stepCount = capability.steps?.length || 0;
        this.description = `${stepCount} 步驟`;
        
        // 設定 tooltip
        const tooltip = new vscode.MarkdownString();
        tooltip.appendMarkdown(`**${capability.name || capability.id}**\n\n`);
        if (capability.description) {
            tooltip.appendMarkdown(capability.description + '\n\n');
        }
        tooltip.appendMarkdown(`**指令:** \`/cp.${capability.id}\`\n\n`);
        if (capability.steps && capability.steps.length > 0) {
            tooltip.appendMarkdown('**步驟:**\n');
            capability.steps.forEach((step, i) => {
                tooltip.appendMarkdown(`${i + 1}. ${step.title || step.skillId}\n`);
            });
        }
        this.tooltip = tooltip;
        
        // 設定點擊行為
        this.command = {
            command: 'ccm.capability.edit',
            title: '編輯 Workflow',
            arguments: [capability.id]
        };
        
        // 設定 context value
        this.contextValue = 'capability';
        
        // 儲存 ID
        this.id = capability.id;
    }
}

/**
 * Capability Step TreeItem
 */
class CapabilityStepItem extends vscode.TreeItem {
    constructor(
        public readonly step: { skillId: string; title?: string; order?: number },
        public readonly stepNumber: number
    ) {
        super(`${stepNumber}. ${step.title || step.skillId}`, vscode.TreeItemCollapsibleState.None);
        
        this.iconPath = new vscode.ThemeIcon('symbol-method');
        this.description = step.skillId;
        
        // 點擊開啟對應 Skill
        this.command = {
            command: 'ccm.skill.openFile',
            title: '開啟 Skill',
            arguments: [step.skillId]
        };
        
        this.contextValue = 'capabilityStep';
    }
}
