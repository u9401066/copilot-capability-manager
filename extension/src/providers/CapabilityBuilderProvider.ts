/**
 * CapabilityBuilderProvider - Workflow 建立器 Webview
 */

import * as vscode from 'vscode';
import { CapabilityService } from '../services/CapabilityService';
import { SkillService } from '../services/SkillService';
import { Capability, CapabilityStep, Skill } from '../types';

export class CapabilityBuilderProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'ccm.capabilityBuilder';
    
    private _view?: vscode.WebviewView;
    private currentCapability?: Capability;
    private availableSkills: Skill[] = [];

    constructor(
        private readonly extensionUri: vscode.Uri,
        private readonly capabilityService: CapabilityService,
        private readonly skillService: SkillService
    ) {}

    async resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ): Promise<void> {
        this._view = webviewView;

        // 載入可用的 Skills
        this.availableSkills = await this.skillService.listSkills();

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this.extensionUri]
        };

        webviewView.webview.html = this.getHtmlContent(webviewView.webview);

        // 處理來自 Webview 的訊息
        webviewView.webview.onDidReceiveMessage(async (message: any) => {
            switch (message.command) {
                case 'saveCapability':
                    await this.saveCapability(message.capability);
                    break;
                case 'createCapability':
                    await this.createCapability(message.capability);
                    break;
                case 'deleteCapability':
                    await this.deleteCapability(message.capabilityId);
                    break;
                case 'requestCapability':
                    this.sendCapabilityToWebview();
                    break;
                case 'requestSkills':
                    this.sendSkillsToWebview();
                    break;
            }
        });
    }

    /**
     * 顯示特定 Capability
     */
    async showCapability(capabilityId: string): Promise<void> {
        const capability = await this.capabilityService.getCapability(capabilityId);
        if (capability) {
            this.currentCapability = capability;
        }
        this.sendCapabilityToWebview();
    }

    /**
     * 顯示新建 Capability 表單
     */
    showNewCapabilityForm(): void {
        this.currentCapability = undefined;
        if (this._view) {
            this._view.webview.postMessage({
                command: 'showNewCapabilityForm',
                skills: this.availableSkills.map(s => ({
                    id: s.id,
                    name: s.name || s.id,
                    description: s.description.split('\n')[0]
                }))
            });
        }
    }

    private sendCapabilityToWebview(): void {
        if (this._view && this.currentCapability) {
            this._view.webview.postMessage({
                command: 'loadCapability',
                capability: this.currentCapability,
                skills: this.availableSkills.map(s => ({
                    id: s.id,
                    name: s.name || s.id,
                    description: s.description.split('\n')[0]
                }))
            });
        }
    }

    private sendSkillsToWebview(): void {
        if (this._view) {
            this._view.webview.postMessage({
                command: 'skillsList',
                skills: this.availableSkills.map(s => ({
                    id: s.id,
                    name: s.name || s.id,
                    description: s.description.split('\n')[0]
                }))
            });
        }
    }

    private async saveCapability(capability: Capability): Promise<void> {
        try {
            await this.capabilityService.updateCapability(capability.id, capability);
            vscode.window.showInformationMessage(`Workflow "${capability.name}" 已儲存`);
            vscode.commands.executeCommand('ccm.capability.refresh');
        } catch (error) {
            vscode.window.showErrorMessage(`儲存失敗: ${error}`);
        }
    }

    private async createCapability(capability: Capability): Promise<void> {
        try {
            await this.capabilityService.createCapability(capability);
            vscode.window.showInformationMessage(`Workflow "${capability.name}" 已建立`);
            vscode.commands.executeCommand('ccm.capability.refresh');
        } catch (error) {
            vscode.window.showErrorMessage(`建立失敗: ${error}`);
        }
    }

    private async deleteCapability(capabilityId: string): Promise<void> {
        const confirm = await vscode.window.showWarningMessage(
            `確定要刪除 Workflow "${capabilityId}" 嗎？`,
            { modal: true },
            '刪除'
        );
        
        if (confirm === '刪除') {
            try {
                await this.capabilityService.deleteCapability(capabilityId);
                vscode.window.showInformationMessage(`Workflow "${capabilityId}" 已刪除`);
                vscode.commands.executeCommand('ccm.capability.refresh');
                this.currentCapability = undefined;
            } catch (error) {
                vscode.window.showErrorMessage(`刪除失敗: ${error}`);
            }
        }
    }

    private getHtmlContent(webview: vscode.Webview): string {
        const nonce = getNonce();

        return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Capability Builder</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            padding: 10px;
        }
        
        .form-group { margin-bottom: 15px; }
        
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        input, select, textarea {
            width: 100%;
            padding: 6px 8px;
            border: 1px solid var(--vscode-input-border);
            background: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border-radius: 2px;
            box-sizing: border-box;
        }
        
        textarea { min-height: 80px; resize: vertical; }
        
        button {
            padding: 8px 16px;
            margin-right: 8px;
            border: none;
            border-radius: 2px;
            cursor: pointer;
        }
        
        .btn-primary {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
        }
        
        .btn-primary:hover { background: var(--vscode-button-hoverBackground); }
        .btn-danger { background: var(--vscode-errorForeground); color: white; }
        
        .btn-secondary {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }
        
        .btn-small {
            padding: 4px 8px;
            font-size: 12px;
        }
        
        .button-group { display: flex; gap: 8px; margin-top: 20px; }
        
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: var(--vscode-descriptionForeground);
        }
        
        .section-title {
            font-size: 14px;
            font-weight: bold;
            margin: 15px 0 10px;
            color: var(--vscode-foreground);
        }
        
        .hint {
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
            margin-top: 4px;
        }
        
        .step-item {
            background: var(--vscode-editor-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 4px;
            padding: 10px;
            margin-bottom: 10px;
        }
        
        .step-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .step-number {
            font-weight: bold;
            color: var(--vscode-textLink-foreground);
        }
        
        .step-actions { display: flex; gap: 4px; }
        
        .step-content { margin-top: 8px; }
        
        .step-content input,
        .step-content select {
            margin-bottom: 8px;
        }
        
        #steps-container { margin-top: 10px; }
        
        .add-step-btn {
            width: 100%;
            margin-top: 10px;
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }
    </style>
</head>
<body>
    <div id="app">
        <div id="empty-state" class="empty-state">
            <p>選擇一個 Workflow 以編輯<br>或點擊「新增」建立新的 Workflow</p>
            <button class="btn-primary" onclick="showNewForm()">+ 新增 Workflow</button>
        </div>
        
        <div id="capability-form" style="display: none;">
            <div class="section-title" id="form-title">編輯 Workflow</div>
            
            <div class="form-group">
                <label for="cap-id">ID *</label>
                <input type="text" id="cap-id" placeholder="workflow-id (會產生 cp.{id} 指令)">
                <div class="hint">例如：write_report → 產生 /cp.write_report 指令</div>
            </div>
            
            <div class="form-group">
                <label for="cap-name">名稱 *</label>
                <input type="text" id="cap-name" placeholder="Workflow 顯示名稱">
            </div>
            
            <div class="form-group">
                <label for="cap-description">描述</label>
                <textarea id="cap-description" placeholder="描述這個 Workflow 的用途"></textarea>
            </div>
            
            <div class="section-title">執行步驟</div>
            <div id="steps-container"></div>
            <button class="add-step-btn" onclick="addStep()">+ 新增步驟</button>
            
            <div class="button-group">
                <button class="btn-primary" onclick="saveCapability()">儲存</button>
                <button class="btn-secondary" onclick="cancel()">取消</button>
                <button class="btn-danger" id="btn-delete" onclick="deleteCapability()" style="display: none;">刪除</button>
            </div>
        </div>
    </div>
    
    <script nonce="${nonce}">
        const vscode = acquireVsCodeApi();
        let isNewCapability = false;
        let originalCapabilityId = null;
        let steps = [];
        let availableSkills = [];
        
        window.addEventListener('message', event => {
            const message = event.data;
            switch (message.command) {
                case 'loadCapability':
                    loadCapabilityData(message.capability, message.skills);
                    break;
                case 'showNewCapabilityForm':
                    showNewCapabilityForm(message.skills);
                    break;
                case 'skillsList':
                    availableSkills = message.skills;
                    break;
            }
        });
        
        function loadCapabilityData(capability, skills) {
            isNewCapability = false;
            originalCapabilityId = capability.id;
            availableSkills = skills;
            
            document.getElementById('empty-state').style.display = 'none';
            document.getElementById('capability-form').style.display = 'block';
            document.getElementById('form-title').textContent = '編輯 Workflow';
            document.getElementById('btn-delete').style.display = 'inline-block';
            
            document.getElementById('cap-id').value = capability.id;
            document.getElementById('cap-id').disabled = true;
            document.getElementById('cap-name').value = capability.name || '';
            document.getElementById('cap-description').value = capability.description || '';
            
            steps = capability.steps || [];
            renderSteps();
        }
        
        function showNewCapabilityForm(skills) {
            isNewCapability = true;
            originalCapabilityId = null;
            availableSkills = skills;
            
            document.getElementById('empty-state').style.display = 'none';
            document.getElementById('capability-form').style.display = 'block';
            document.getElementById('form-title').textContent = '新增 Workflow';
            document.getElementById('btn-delete').style.display = 'none';
            
            document.getElementById('cap-id').value = '';
            document.getElementById('cap-id').disabled = false;
            document.getElementById('cap-name').value = '';
            document.getElementById('cap-description').value = '';
            
            steps = [];
            renderSteps();
        }
        
        function showNewForm() {
            vscode.postMessage({ command: 'requestSkills' });
            setTimeout(() => {
                showNewCapabilityForm(availableSkills);
            }, 100);
        }
        
        function renderSteps() {
            const container = document.getElementById('steps-container');
            container.innerHTML = steps.map((step, index) => \`
                <div class="step-item">
                    <div class="step-header">
                        <span class="step-number">步驟 \${index + 1}</span>
                        <div class="step-actions">
                            <button class="btn-small btn-secondary" onclick="moveStep(\${index}, -1)" \${index === 0 ? 'disabled' : ''}>↑</button>
                            <button class="btn-small btn-secondary" onclick="moveStep(\${index}, 1)" \${index === steps.length - 1 ? 'disabled' : ''}>↓</button>
                            <button class="btn-small btn-danger" onclick="removeStep(\${index})">✕</button>
                        </div>
                    </div>
                    <div class="step-content">
                        <input type="text" value="\${step.name || ''}" placeholder="步驟名稱" onchange="updateStep(\${index}, 'name', this.value)">
                        <select onchange="updateStep(\${index}, 'skillId', this.value)">
                            <option value="">-- 選擇 Skill --</option>
                            \${availableSkills.map(s => \`<option value="\${s.id}" \${step.skillId === s.id ? 'selected' : ''}>\${s.name}</option>\`).join('')}
                        </select>
                        <input type="text" value="\${step.description || ''}" placeholder="步驟說明（選填）" onchange="updateStep(\${index}, 'description', this.value)">
                    </div>
                </div>
            \`).join('');
        }
        
        function addStep() {
            steps.push({ name: '', skillId: '', description: '' });
            renderSteps();
        }
        
        function removeStep(index) {
            steps.splice(index, 1);
            renderSteps();
        }
        
        function moveStep(index, direction) {
            const newIndex = index + direction;
            if (newIndex >= 0 && newIndex < steps.length) {
                [steps[index], steps[newIndex]] = [steps[newIndex], steps[index]];
                renderSteps();
            }
        }
        
        function updateStep(index, field, value) {
            steps[index][field] = value;
        }
        
        function saveCapability() {
            const capability = {
                id: document.getElementById('cap-id').value.trim(),
                name: document.getElementById('cap-name').value.trim(),
                description: document.getElementById('cap-description').value.trim(),
                steps: steps.filter(s => s.skillId) // 只保留有選擇 Skill 的步驟
            };
            
            if (!capability.id || !capability.name) {
                alert('請填寫必填欄位（ID、名稱）');
                return;
            }
            
            if (capability.steps.length === 0) {
                alert('請至少新增一個步驟');
                return;
            }
            
            if (isNewCapability) {
                vscode.postMessage({ command: 'createCapability', capability });
            } else {
                vscode.postMessage({ command: 'saveCapability', capability });
            }
        }
        
        function deleteCapability() {
            if (originalCapabilityId) {
                vscode.postMessage({ command: 'deleteCapability', capabilityId: originalCapabilityId });
            }
        }
        
        function cancel() {
            document.getElementById('empty-state').style.display = 'block';
            document.getElementById('capability-form').style.display = 'none';
        }
        
        // 初始請求
        vscode.postMessage({ command: 'requestSkills' });
    </script>
</body>
</html>`;
    }
}

function getNonce(): string {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}
