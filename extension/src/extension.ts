/**
 * Copilot Capability Manager - VS Code Extension
 * 
 * 管理 Agent Skills 和 Capabilities 的視覺化工具
 */

import * as vscode from 'vscode';
import { SkillService, CapabilityService } from './services';
import { SkillTreeProvider, SkillManagerProvider, CapabilityBuilderProvider, CapabilityTreeProvider } from './providers';
import { registerCommands } from './commands';

export function activate(context: vscode.ExtensionContext): void {
    console.log('Copilot Capability Manager is now active');

    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showWarningMessage('請開啟一個工作區以使用 Copilot Capability Manager');
        return;
    }

    // 初始化服務
    const skillService = new SkillService(workspaceFolder.uri.fsPath);
    const capabilityService = new CapabilityService(workspaceFolder.uri.fsPath, skillService);

    // 初始化 Providers
    const skillTreeProvider = new SkillTreeProvider(skillService);
    const capabilityTreeProvider = new CapabilityTreeProvider(capabilityService);
    const skillManagerProvider = new SkillManagerProvider(context.extensionUri, skillService);
    const capabilityBuilderProvider = new CapabilityBuilderProvider(
        context.extensionUri,
        capabilityService,
        skillService
    );

    // 註冊 TreeViews
    context.subscriptions.push(
        vscode.window.registerTreeDataProvider('ccm.skillExplorer', skillTreeProvider)
    );
    
    context.subscriptions.push(
        vscode.window.registerTreeDataProvider('ccm.capabilityExplorer', capabilityTreeProvider)
    );

    // 註冊 WebviewViewProviders
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(
            SkillManagerProvider.viewType,
            skillManagerProvider
        )
    );

    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(
            CapabilityBuilderProvider.viewType,
            capabilityBuilderProvider
        )
    );

    // 註冊命令
    registerCommands(
        context,
        skillService,
        capabilityService,
        skillTreeProvider,
        capabilityTreeProvider,
        skillManagerProvider,
        capabilityBuilderProvider
    );

    // 監視檔案變更，自動重新整理
    const config = vscode.workspace.getConfiguration('ccm');
    if (config.get<boolean>('autoRefresh', true)) {
        const skillsPath = config.get<string>('skillsPath', '.claude/skills');
        const promptsPath = config.get<string>('promptsPath', '.github/prompts');
        
        // Skills 監視
        const skillWatcher = vscode.workspace.createFileSystemWatcher(
            new vscode.RelativePattern(workspaceFolder, `${skillsPath}/**/SKILL.md`)
        );
        skillWatcher.onDidCreate(() => skillTreeProvider.refresh());
        skillWatcher.onDidDelete(() => skillTreeProvider.refresh());
        skillWatcher.onDidChange(() => skillTreeProvider.refresh());
        context.subscriptions.push(skillWatcher);
        
        // Capabilities 監視
        const capWatcher = vscode.workspace.createFileSystemWatcher(
            new vscode.RelativePattern(workspaceFolder, `${promptsPath}/cp.*.prompt.md`)
        );
        capWatcher.onDidCreate(() => capabilityTreeProvider.refresh());
        capWatcher.onDidDelete(() => capabilityTreeProvider.refresh());
        capWatcher.onDidChange(() => capabilityTreeProvider.refresh());
        context.subscriptions.push(capWatcher);
    }

    vscode.window.showInformationMessage('Copilot Capability Manager 已啟動');
}

export function deactivate(): void {
    console.log('Copilot Capability Manager is now deactivated');
}
