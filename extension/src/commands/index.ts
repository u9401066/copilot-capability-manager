/**
 * 註冊所有命令
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { SkillService } from '../services/SkillService';
import { CapabilityService } from '../services/CapabilityService';
import { SkillTreeProvider } from '../providers/SkillTreeProvider';
import { SkillManagerProvider } from '../providers/SkillManagerProvider';
import { CapabilityBuilderProvider } from '../providers/CapabilityBuilderProvider';

export function registerCommands(
    context: vscode.ExtensionContext,
    skillService: SkillService,
    capabilityService: CapabilityService,
    skillTreeProvider: SkillTreeProvider,
    skillManagerProvider: SkillManagerProvider,
    capabilityBuilderProvider: CapabilityBuilderProvider
): void {
    // 重新整理 Skill 列表
    context.subscriptions.push(
        vscode.commands.registerCommand('ccm.skill.refresh', () => {
            skillTreeProvider.refresh();
        })
    );

    // 新增 Skill
    context.subscriptions.push(
        vscode.commands.registerCommand('ccm.skill.create', () => {
            skillManagerProvider.showNewSkillForm();
            // 聚焦到 Skill Manager 面板
            vscode.commands.executeCommand('ccm.skillManager.focus');
        })
    );

    // 編輯 Skill
    context.subscriptions.push(
        vscode.commands.registerCommand('ccm.skill.edit', async (skillId: string) => {
            await skillManagerProvider.showSkill(skillId);
            vscode.commands.executeCommand('ccm.skillManager.focus');
        })
    );

    // 刪除 Skill
    context.subscriptions.push(
        vscode.commands.registerCommand('ccm.skill.delete', async (skillId: string) => {
            const confirm = await vscode.window.showWarningMessage(
                `確定要刪除 Skill "${skillId}" 嗎？`,
                { modal: true },
                '刪除'
            );
            
            if (confirm === '刪除') {
                try {
                    await skillService.deleteSkill(skillId);
                    vscode.window.showInformationMessage(`Skill "${skillId}" 已刪除`);
                    skillTreeProvider.refresh();
                } catch (error) {
                    vscode.window.showErrorMessage(`刪除失敗: ${error}`);
                }
            }
        })
    );

    // 開啟 SKILL.md 檔案
    context.subscriptions.push(
        vscode.commands.registerCommand('ccm.skill.openFile', async (skillId: string) => {
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                return;
            }

            const config = vscode.workspace.getConfiguration('ccm');
            const skillsPath = config.get<string>('skillsPath', '.claude/skills');
            const skillFilePath = path.join(
                workspaceFolder.uri.fsPath,
                skillsPath,
                skillId,
                'SKILL.md'
            );

            try {
                const doc = await vscode.workspace.openTextDocument(skillFilePath);
                await vscode.window.showTextDocument(doc);
            } catch (error) {
                vscode.window.showErrorMessage(`無法開啟檔案: ${error}`);
            }
        })
    );

    // 新增 Capability/Workflow
    context.subscriptions.push(
        vscode.commands.registerCommand('ccm.capability.create', () => {
            capabilityBuilderProvider.showNewCapabilityForm();
            vscode.commands.executeCommand('ccm.capabilityBuilder.focus');
        })
    );

    // 編輯 Capability/Workflow
    context.subscriptions.push(
        vscode.commands.registerCommand('ccm.capability.edit', async (capabilityId: string) => {
            await capabilityBuilderProvider.showCapability(capabilityId);
            vscode.commands.executeCommand('ccm.capabilityBuilder.focus');
        })
    );

    // 重新整理 Capability 列表
    context.subscriptions.push(
        vscode.commands.registerCommand('ccm.capability.refresh', () => {
            // 目前 Capability 沒有 TreeView，這個命令保留給未來使用
            vscode.window.showInformationMessage('Workflow 列表已重新整理');
        })
    );

    // 匯出 Skills 為 copilot-instructions.md
    context.subscriptions.push(
        vscode.commands.registerCommand('ccm.skill.export', async () => {
            try {
                const skills = await skillService.listSkills();
                const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
                if (!workspaceFolder) {
                    throw new Error('請先開啟工作區');
                }

                // 產生 skills 區塊
                const skillsXml = skills.map(skill => `<skill>
<name>${skill.id}</name>
<description>${skill.description.split('\n')[0]}</description>
<file>${path.join(workspaceFolder.uri.fsPath, '.claude/skills', skill.id, 'SKILL.md')}</file>
</skill>`).join('\n');

                const content = `<skills>
Here is a list of skills that contain domain specific knowledge on a variety of topics.
Each skill comes with a description of the topic and a file path that contains the detailed instructions.
When a user asks you to perform a task that falls within the domain of a skill, use the 'read_file' tool to acquire the full instructions from the file URI.
${skillsXml}
</skills>`;

                // 顯示在新文件中
                const doc = await vscode.workspace.openTextDocument({
                    content,
                    language: 'xml'
                });
                await vscode.window.showTextDocument(doc);

                vscode.window.showInformationMessage(
                    `已匯出 ${skills.length} 個 Skills。複製此內容到 .github/copilot-instructions.md`
                );
            } catch (error) {
                vscode.window.showErrorMessage(`匯出失敗: ${error}`);
            }
        })
    );
}
