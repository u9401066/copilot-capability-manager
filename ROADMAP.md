# Roadmap

Copilot Capability Manager 開發路線圖。

## 願景

**成為 VS Code 擴充套件**，提供 GUI 介面管理 AI Skills 並組合成 **經驗證的能力路徑 (Validated Skill Pathway)**。

> 🛤️ **Capability = Validated Skill Pathway**
> 不只是 workflow，而是經過驗證的「能力路徑」

---

## 核心創新

| 特性 | 一般 Workflow | Skill Pathway (我們) |
|------|--------------|---------------------|
| 結構 | 線性步驟 | **有向圖 + 權重** |
| 驗證 | 無 | **自動驗證 + 認證** |
| 視覺化 | 流程圖 | **拓撲圖 + 熱力圖** |
| 統計 | 無 | **使用頻率、成功率** |

---

## Phase 1: 核心機制 ✅ (已完成)

**目標**：驗證 Prompt Files 機制可行性

- [x] VS Code Prompt Files 機制實作
- [x] `/cp.xxx` 斜線指令系統
- [x] Skill 模組架構 (`.claude/skills/`)
- [x] Memory Bank 整合
- [x] 基礎工作流程 (write_report, commit, deploy 等)

**產出**：
- 8 個 Prompt Files
- 22 個 Skills
- 機制說明文檔

---

## Phase 2: VS Code Extension 基礎 🚧 (進行中)

**目標**：建立 VS Code 擴充套件框架

### 2.1 擴充套件架構

- [ ] 初始化 VS Code Extension 專案
- [ ] 設定 TypeScript + Webpack
- [ ] 註冊 Commands 和 Views
- [ ] 建立 Webview 框架

### 2.2 Skill Manager GUI

- [ ] Skill 列表 (TreeView)
- [ ] Skill 詳情面板
- [ ] 新增 Skill 表單
- [ ] 編輯 Skill 表單
- [ ] 刪除 Skill 確認

### 2.3 資料層

- [ ] Skill YAML 讀寫
- [ ] Prompt MD 生成
- [ ] 設定儲存 (VS Code Settings)

**預計時程**：2-3 週

---

## Phase 3: Capability Builder 📋

**目標**：視覺化組合 Skills 成工作流程

### 3.1 拖拉介面

- [ ] Skills 側邊欄
- [ ] 工作流程畫布
- [ ] 拖拉排序
- [ ] 步驟連接線

### 3.2 工作流程設定

- [ ] 步驟參數設定
- [ ] 條件分支（進階）
- [ ] 錯誤處理
- [ ] 預覽模式

### 3.3 匯出功能

- [ ] 生成 `.prompt.md`
- [ ] 生成 YAML workflow
- [ ] 即時預覽

**預計時程**：3-4 週

---

## Phase 4: MCP Tool 整合 📋

**目標**：在 Skills 中整合 MCP Tools

### 4.1 MCP Tool 選擇器

- [ ] 列出可用 MCP Tools
- [ ] Tool 搜尋過濾
- [ ] Tool 詳情展示
- [ ] 一鍵加入 Skill

### 4.2 Tool 參數設定

- [ ] 參數表單生成
- [ ] 參數驗證
- [ ] 預設值設定
- [ ] 參數模板

### 4.3 動態載入

- [ ] 偵測已安裝 MCP Servers
- [ ] Tool Schema 解析
- [ ] 執行時 Tool 呼叫

**預計時程**：2-3 週

---

## Phase 5: 進階功能 📋

**目標**：擴展生態系統

### 5.1 Skill Pathway 視覺化 ⭐ 創新功能

- [ ] 有向圖顯示 (React Flow)
- [ ] 節點大小 = 使用頻率
- [ ] 邊粗細 = 轉換頻率
- [ ] 熱力圖模式
- [ ] 時間軸視圖

### 5.2 能力驗證機制 ⭐ 創新功能

- [ ] 驗證等級系統 (Draft → Certified)
- [ ] 自動驗證規則 (成功率、執行次數)
- [ ] 人工審核流程
- [ ] 驗證報告生成
- [ ] 徽章系統 (⚪🔵🟢⭐🏆)

### 5.3 統計儀表板

- [ ] 使用趨勢圖表
- [ ] Skill 排行榜
- [ ] Pathway 效能分析
- [ ] 成功率趨勢

### 5.4 Skill 市集

- [ ] 匯出 Skill 為可分享格式
- [ ] 匯入他人 Skills
- [ ] 線上 Skill Gallery（未來）

### 5.5 團隊協作

- [ ] Skill 版本控制
- [ ] 團隊共享設定
- [ ] 權限管理

### 5.6 雲端同步

- [ ] 設定同步
- [ ] Skills 備份
- [ ] 跨裝置

**預計時程**：持續迭代

---

## 技術里程碑

| 里程碑 | 描述 | 狀態 |
|--------|------|------|
| M1 | Prompt Files POC | ✅ 完成 |
| M2 | Extension 可安裝 | 🚧 開發中 |
| M3 | Skill Manager 可用 | 📋 計劃 |
| M4 | Capability Builder 可用 | 📋 計劃 |
| M5 | MCP 整合完成 | 📋 計劃 |
| M6 | **Skill Pathway 視覺化** | 📋 計劃 |
| M7 | **能力驗證系統** | 📋 計劃 |
| M8 | 發布到 Marketplace | 📋 計劃 |

---

## 版本規劃

| 版本 | 內容 | 預計日期 |
|------|------|----------|
| v0.1.0 | 核心機制 (Prompt Files) | ✅ 2025-12-20 |
| v0.2.0 | Extension 基礎 + Skill Manager | 2025-01 |
| v0.3.0 | Capability Builder | 2025-02 |
| v0.4.0 | MCP 整合 | 2025-03 |
| v0.5.0 | **Skill Pathway + 驗證** | 2025-04 |
| v1.0.0 | 正式發布 | 2025-Q2 |
