/**
 * Copilot Capability Manager - VS Code Extension
 * 
 * 管理 Agent Skills 和 Capabilities 的視覺化工具
 */

import * as vscode from 'vscode';
import { SkillService, CapabilityService } from './services';
import { SkillTreeProvider, SkillManagerProvider, CapabilityBuilderProvider } from './providers';
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
    const skillManagerProvider = new SkillManagerProvider(context.extensionUri, skillService);
    const capabilityBuilderProvider = new CapabilityBuilderProvider(
        context.extensionUri,
        capabilityService,
        skillService
    );

    // 註冊 TreeView
    context.subscriptions.push(
        vscode.window.registerTreeDataProvider('ccm.skillExplorer', skillTreeProvider)
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
        skillManagerProvider,
        capabilityBuilderProvider
    );

    // 監視檔案變更，自動重新整理
    const config = vscode.workspace.getConfiguration('ccm');
    if (config.get<boolean>('autoRefresh', true)) {
        const skillsPath = config.get<string>('skillsPath', '.claude/skills');
        const watcher = vscode.workspace.createFileSystemWatcher(
            new vscode.RelativePattern(workspaceFolder, `${skillsPath}/**/SKILL.md`)
        );

        watcher.onDidCreate(() => skillTreeProvider.refresh());
        watcher.onDidDelete(() => skillTreeProvider.refresh());
        watcher.onDidChange(() => skillTreeProvider.refresh());

        context.subscriptions.push(watcher);
    }

    vscode.window.showInformationMessage('Copilot Capability Manager 已啟動');
}

export function deactivate(): void {
    console.log('Copilot Capability Manager is now deactivated');
}
