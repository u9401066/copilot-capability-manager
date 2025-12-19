```markdown
---
name: doc-updater
description: |
  Update project documentation and sync docs with code changes.
  LOAD THIS SKILL WHEN: Code changes require doc updates | User says "更新文件", "同步文檔", "update docs" | after feature implementation | before releases.
  CAPABILITIES: Update README, CHANGELOG, API docs, ARCHITECTURE, sync with code changes.
---

# 文件更新技能

## 描述
更新專案文件，確保文檔與程式碼同步。

## 觸發條件
- 「更新文件」
- 「同步文檔」
- 專案檢查後發現需要更新
- Workflow 中的文件更新步驟

## 更新範圍

### 自動更新文件
| 文件 | 更新內容 |
|------|----------|
| README.md | 功能說明、安裝指引、使用範例 |
| CHANGELOG.md | 版本變更記錄 |
| API.md | API 文檔（從程式碼提取） |
| ARCHITECTURE.md | 架構說明 |

### Memory Bank 同步
| 文件 | 更新內容 |
|------|----------|
| activeContext.md | 當前工作焦點 |
| progress.md | 進度追蹤 |
| decisionLog.md | 決策記錄 |
| productContext.md | 產品上下文 |

## 執行流程
```
1. 掃描程式碼變更
2. 識別需要更新的文件
3. 生成更新內容
4. 驗證更新正確性
5. 應用變更
6. 生成更新報告
```

## 輸出格式
```
📝 文件更新報告

更新的文件：
  ✅ README.md - 新增安裝說明
  ✅ CHANGELOG.md - 添加 v0.2.0
  ✅ progress.md - 更新完成項目
  ⏭️ API.md - 無變更需要

變更摘要：
  - 修改 3 個文件
  - 新增 45 行
  - 刪除 12 行

所有文件已同步！
```

## 使用範例
```
「更新專案文件」
「同步 Memory Bank」
「更新 README」
```

```
