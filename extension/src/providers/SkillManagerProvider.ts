/**
 * SkillManagerProvider - Skill 編輯器 Webview
 */

import * as vscode from 'vscode';
import { SkillService } from '../services/SkillService';
import { Skill, SkillCategory, CATEGORY_LABELS } from '../types';

export class SkillManagerProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'ccm.skillManager';
    
    private _view?: vscode.WebviewView;
    private currentSkill?: Skill;

    constructor(
        private readonly extensionUri: vscode.Uri,
        private readonly skillService: SkillService
    ) {}

    resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ): void {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this.extensionUri]
        };

        webviewView.webview.html = this.getHtmlContent(webviewView.webview);

        // 處理來自 Webview 的訊息
        webviewView.webview.onDidReceiveMessage(async (message) => {
            switch (message.command) {
                case 'saveSkill':
                    await this.saveSkill(message.skill);
                    break;
                case 'createSkill':
                    await this.createSkill(message.skill);
                    break;
                case 'deleteSkill':
                    await this.deleteSkill(message.skillId);
                    break;
                case 'requestSkill':
                    this.sendSkillToWebview();
                    break;
            }
        });
    }

    /**
     * 顯示特定 Skill
     */
    async showSkill(skillId: string): Promise<void> {
        const skill = await this.skillService.getSkill(skillId);
        if (skill) {
            this.currentSkill = skill;
        }
        this.sendSkillToWebview();
    }

    /**
     * 顯示新建 Skill 表單
     */
    showNewSkillForm(): void {
        this.currentSkill = undefined;
        if (this._view) {
            this._view.webview.postMessage({
                command: 'showNewSkillForm',
                categories: Object.entries(CATEGORY_LABELS).map(([value, label]) => ({ value, label }))
            });
        }
    }

    private sendSkillToWebview(): void {
        if (this._view && this.currentSkill) {
            this._view.webview.postMessage({
                command: 'loadSkill',
                skill: this.currentSkill,
                categories: Object.entries(CATEGORY_LABELS).map(([value, label]) => ({ value, label }))
            });
        }
    }

    private async saveSkill(skill: Skill): Promise<void> {
        try {
            await this.skillService.updateSkill(skill.id, skill);
            vscode.window.showInformationMessage(`Skill "${skill.name}" 已儲存`);
            vscode.commands.executeCommand('ccm.skill.refresh');
        } catch (error) {
            vscode.window.showErrorMessage(`儲存失敗: ${error}`);
        }
    }

    private async createSkill(skill: Skill): Promise<void> {
        try {
            await this.skillService.createSkill(skill);
            vscode.window.showInformationMessage(`Skill "${skill.name}" 已建立`);
            vscode.commands.executeCommand('ccm.skill.refresh');
        } catch (error) {
            vscode.window.showErrorMessage(`建立失敗: ${error}`);
        }
    }

    private async deleteSkill(skillId: string): Promise<void> {
        const confirm = await vscode.window.showWarningMessage(
            `確定要刪除 Skill "${skillId}" 嗎？`,
            { modal: true },
            '刪除'
        );
        
        if (confirm === '刪除') {
            try {
                await this.skillService.deleteSkill(skillId);
                vscode.window.showInformationMessage(`Skill "${skillId}" 已刪除`);
                vscode.commands.executeCommand('ccm.skill.refresh');
                this.currentSkill = undefined;
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
    <title>Skill Manager</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            padding: 10px;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
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
        }
        
        textarea {
            min-height: 100px;
            resize: vertical;
        }
        
        .triggers-input {
            min-height: 60px;
        }
        
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
        
        .btn-primary:hover {
            background: var(--vscode-button-hoverBackground);
        }
        
        .btn-danger {
            background: var(--vscode-errorForeground);
            color: white;
        }
        
        .btn-secondary {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }
        
        .button-group {
            display: flex;
            gap: 8px;
            margin-top: 20px;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: var(--vscode-descriptionForeground);
        }
        
        .section-title {
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 10px;
            color: var(--vscode-foreground);
        }
        
        .hint {
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
            margin-top: 4px;
        }
    </style>
</head>
<body>
    <div id="app">
        <div id="empty-state" class="empty-state">
            <p>選擇一個 Skill 以編輯<br>或點擊「新增」建立新的 Skill</p>
            <button class="btn-primary" onclick="showNewForm()">+ 新增 Skill</button>
        </div>
        
        <div id="skill-form" style="display: none;">
            <div class="section-title" id="form-title">編輯 Skill</div>
            
            <div class="form-group">
                <label for="skill-id">ID *</label>
                <input type="text" id="skill-id" placeholder="skill-id (小寫、連字號)">
                <div class="hint">唯一識別碼，例如：web-search、report-generator</div>
            </div>
            
            <div class="form-group">
                <label for="skill-name">名稱 *</label>
                <input type="text" id="skill-name" placeholder="Skill 顯示名稱">
            </div>
            
            <div class="form-group">
                <label for="skill-category">分類</label>
                <select id="skill-category"></select>
            </div>
            
            <div class="form-group">
                <label for="skill-description">描述 *</label>
                <textarea id="skill-description" placeholder="描述這個 Skill 的功能和用途"></textarea>
                <div class="hint">建議格式：功能摘要 | LOAD THIS SKILL WHEN: 觸發時機 | CAPABILITIES: 能力列表</div>
            </div>
            
            <div class="form-group">
                <label for="skill-triggers">觸發詞</label>
                <textarea id="skill-triggers" class="triggers-input" placeholder="每行一個觸發詞"></textarea>
                <div class="hint">當 Agent 偵測到這些詞彙時會載入此 Skill</div>
            </div>
            
            <div class="button-group">
                <button class="btn-primary" onclick="saveSkill()">儲存</button>
                <button class="btn-secondary" onclick="cancel()">取消</button>
                <button class="btn-danger" id="btn-delete" onclick="deleteSkill()" style="display: none;">刪除</button>
            </div>
        </div>
    </div>
    
    <script nonce="${nonce}">
        const vscode = acquireVsCodeApi();
        let isNewSkill = false;
        let originalSkillId = null;
        
        // 接收來自擴充套件的訊息
        window.addEventListener('message', event => {
            const message = event.data;
            switch (message.command) {
                case 'loadSkill':
                    loadSkillData(message.skill, message.categories);
                    break;
                case 'showNewSkillForm':
                    showNewSkillForm(message.categories);
                    break;
            }
        });
        
        function loadSkillData(skill, categories) {
            isNewSkill = false;
            originalSkillId = skill.id;
            
            document.getElementById('empty-state').style.display = 'none';
            document.getElementById('skill-form').style.display = 'block';
            document.getElementById('form-title').textContent = '編輯 Skill';
            document.getElementById('btn-delete').style.display = 'inline-block';
            
            document.getElementById('skill-id').value = skill.id;
            document.getElementById('skill-id').disabled = true; // ID 不可修改
            document.getElementById('skill-name').value = skill.name || '';
            document.getElementById('skill-description').value = skill.description || '';
            document.getElementById('skill-triggers').value = (skill.triggers || []).join('\\n');
            
            // 填充分類選項
            populateCategories(categories, skill.category);
        }
        
        function showNewSkillForm(categories) {
            isNewSkill = true;
            originalSkillId = null;
            
            document.getElementById('empty-state').style.display = 'none';
            document.getElementById('skill-form').style.display = 'block';
            document.getElementById('form-title').textContent = '新增 Skill';
            document.getElementById('btn-delete').style.display = 'none';
            
            document.getElementById('skill-id').value = '';
            document.getElementById('skill-id').disabled = false;
            document.getElementById('skill-name').value = '';
            document.getElementById('skill-description').value = '';
            document.getElementById('skill-triggers').value = '';
            
            populateCategories(categories);
        }
        
        function showNewForm() {
            vscode.postMessage({ command: 'requestNewForm' });
        }
        
        function populateCategories(categories, selected = 'other') {
            const select = document.getElementById('skill-category');
            select.innerHTML = categories.map(c => 
                '<option value="' + c.value + '"' + (c.value === selected ? ' selected' : '') + '>' + c.label + '</option>'
            ).join('');
        }
        
        function saveSkill() {
            const skill = {
                id: document.getElementById('skill-id').value.trim(),
                name: document.getElementById('skill-name').value.trim(),
                category: document.getElementById('skill-category').value,
                description: document.getElementById('skill-description').value.trim(),
                triggers: document.getElementById('skill-triggers').value.split('\\n').filter(t => t.trim())
            };
            
            if (!skill.id || !skill.name || !skill.description) {
                alert('請填寫必填欄位（ID、名稱、描述）');
                return;
            }
            
            if (isNewSkill) {
                vscode.postMessage({ command: 'createSkill', skill });
            } else {
                vscode.postMessage({ command: 'saveSkill', skill });
            }
        }
        
        function deleteSkill() {
            if (originalSkillId) {
                vscode.postMessage({ command: 'deleteSkill', skillId: originalSkillId });
            }
        }
        
        function cancel() {
            document.getElementById('empty-state').style.display = 'block';
            document.getElementById('skill-form').style.display = 'none';
        }
        
        // 請求當前 Skill 資料（如果有）
        vscode.postMessage({ command: 'requestSkill' });
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
