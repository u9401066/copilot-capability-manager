import * as vscode from 'vscode';
import { SkillService } from './services/SkillService';
import { CapabilityService } from './services/CapabilityService';
import { SkillTreeProvider } from './providers/SkillTreeProvider';
import { SkillManagerProvider } from './providers/SkillManagerProvider';
import { CapabilityBuilderProvider } from './providers/CapabilityBuilderProvider';
import { registerCommands } from './commands';

/**
 * Copilot Capability Manager 擴充套件入口點
 * 
 * 功能：
 * 1. 視覺化管理 Skills（.claude/skills/）
 * 2. 組合 Capabilities（.github/prompts/）
 * 3. 整合 MCP Tools
 */
export function activate(context: vscode.ExtensionContext) {
    console.log('Copilot Capability Manager is now active!');

    // 取得工作區路徑
    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspaceRoot) {
        vscode.window.showWarningMessage('請先開啟一個工作區資料夾');
        return;
    }

    // 初始化核心服務
    const skillService = new SkillService(workspaceRoot);
    const capabilityService = new CapabilityService(workspaceRoot, skillService);

    // 註冊 TreeView Provider（側邊欄 Skill 列表）
    const skillTreeProvider = new SkillTreeProvider(skillService);
    context.subscriptions.push(
        vscode.window.registerTreeDataProvider('skillExplorer', skillTreeProvider)
    );

    // 註冊 Webview Provider（Skill Manager）
    const skillManagerProvider = new SkillManagerProvider(context.extensionUri, skillService);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('skillManager', skillManagerProvider)
    );

    // 註冊 Webview Provider（Capability Builder）
    const capabilityBuilderProvider = new CapabilityBuilderProvider(
        context.extensionUri, 
        skillService, 
        capabilityService
    );
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('capabilityBuilder', capabilityBuilderProvider)
    );

    // 註冊命令
    registerCommands(context, skillService, capabilityService, skillTreeProvider);

    // 監聽檔案變更，自動重新整理
    const skillWatcher = vscode.workspace.createFileSystemWatcher('**/.claude/skills/**/SKILL.md');
    skillWatcher.onDidChange(() => skillTreeProvider.refresh());
    skillWatcher.onDidCreate(() => skillTreeProvider.refresh());
    skillWatcher.onDidDelete(() => skillTreeProvider.refresh());
    context.subscriptions.push(skillWatcher);
}

export function deactivate() {
    console.log('Copilot Capability Manager deactivated');
}
